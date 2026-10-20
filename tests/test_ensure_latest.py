import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import zipfile


SPEC = importlib.util.spec_from_file_location(
    "ensure_latest", Path(__file__).resolve().parents[1] / "scripts/ensure_latest.py"
)
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)
LATEST = {"commit": "a" * 40, "version": "2.1.0"}


def package(path, version="2.1.0", missing_skill=False):
    with zipfile.ZipFile(path, "w") as archive:
        contents = {
            "VERSION": version,
            "scripts/ensure_latest.py": "# fixture",
            "agents/openai.yaml": "interface: {}",
            "references/characters.json": json.dumps({
                "people": [{"visual": {"references": [{"path": "assets/ref.jpg"}]}}],
            }),
            "assets/ref.jpg": "fixture-image",
        }
        if not missing_skill:
            contents["SKILL.md"] = "---\nname: deerphotos\n---\n"
        for name, value in contents.items():
            archive.writestr("DeerPhotos-snapshot/" + name, value)


class UpdateGateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "deerphotos"
        self.root.mkdir()
        (self.root / "VERSION").write_text("2.0.0\n")
        (self.root / "my-scene.txt").write_text("keep this user content")

    def test_offline_is_blocked_even_with_previous_state(self):
        (self.root / updater.STATE_FILE).write_text(json.dumps({
            **LATEST, "repository": updater.REPOSITORY,
        }))
        with patch.object(updater, "latest_snapshot", side_effect=urllib.error.URLError("offline")):
            with patch("sys.argv", ["ensure_latest.py", "--skill-dir", str(self.root)]):
                with patch("sys.stdout", new_callable=io.StringIO) as output:
                    self.assertEqual(updater.main(), 20)
                    self.assertEqual(json.loads(output.getvalue())["status"], "blocked")
        self.assertTrue((self.root / "my-scene.txt").exists())

    def test_missing_remote_version_is_blocked(self):
        responses = [
            json.dumps({"sha": LATEST["commit"]}).encode(),
            urllib.error.HTTPError("https://example.invalid/VERSION", 404, "missing", {}, None),
        ]
        with patch.object(updater, "fetch_bytes", side_effect=responses):
            with self.assertRaises(updater.UpdateBlocked):
                updater.latest_snapshot()

    def test_unpublished_local_version_is_not_downgraded(self):
        (self.root / "VERSION").write_text("3.0.0")
        with patch.object(updater, "latest_snapshot", return_value=LATEST):
            with self.assertRaises(updater.UpdateBlocked):
                updater.ensure_latest(self.root)
        self.assertEqual((self.root / "VERSION").read_text(), "3.0.0")

    def test_update_preserves_backup_and_rechecks_network_on_next_run(self):
        with patch.object(updater, "latest_snapshot", return_value=LATEST) as check:
            with patch.object(updater, "download_package", side_effect=lambda _, dest: package(dest)) as download:
                first = updater.ensure_latest(self.root)
                self.assertTrue(first["updated"])
                self.assertEqual((Path(first["backup"]) / "my-scene.txt").read_text(), "keep this user content")
                self.assertEqual((self.root / "VERSION").read_text(), "2.1.0")
                second = updater.ensure_latest(self.root)
                self.assertFalse(second["updated"])
                self.assertEqual(check.call_count, 2)
                self.assertEqual(download.call_count, 1)

    def test_invalid_package_does_not_replace_existing_installation(self):
        with patch.object(updater, "latest_snapshot", return_value=LATEST):
            with patch.object(updater, "download_package", side_effect=lambda _, dest: package(dest, missing_skill=True)):
                with self.assertRaises(updater.UpdateBlocked):
                    updater.ensure_latest(self.root)
        self.assertEqual((self.root / "VERSION").read_text(), "2.0.0\n")
        self.assertTrue((self.root / "my-scene.txt").exists())

    def test_failed_replacement_restores_old_directory(self):
        original_rename = Path.rename

        def fail_install(path, target):
            if path.name == "skill" and Path(target).resolve() == self.root.resolve():
                raise OSError("simulated replacement failure")
            return original_rename(path, target)

        with patch.object(updater, "latest_snapshot", return_value=LATEST):
            with patch.object(updater, "download_package", side_effect=lambda _, dest: package(dest)):
                with patch.object(Path, "rename", fail_install):
                    with self.assertRaises(OSError):
                        updater.ensure_latest(self.root)
        self.assertTrue((self.root / "my-scene.txt").exists())
        self.assertEqual((self.root / "VERSION").read_text(), "2.0.0\n")

    def test_zip_cannot_escape_staging_directory(self):
        archive = Path(self.temporary.name) / "bad.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr("repo/../../escape.txt", "bad")
        with self.assertRaises(updater.UpdateBlocked):
            updater.unpack_package(archive, self.root / "stage")
        self.assertFalse((Path(self.temporary.name) / "escape.txt").exists())

    def test_dirty_git_checkout_is_not_updated(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        with patch.object(updater, "latest_snapshot", return_value=LATEST):
            with self.assertRaises(updater.UpdateBlocked):
                updater.ensure_latest(self.root)
        self.assertTrue((self.root / "my-scene.txt").exists())
        self.assertEqual((self.root / "VERSION").read_text(), "2.0.0\n")

    def test_local_git_ahead_with_same_version_is_blocked(self):
        (self.root / "VERSION").write_text(LATEST["version"])
        (self.root / ".git").mkdir()

        def fake_git(root, *args):
            if args == ("rev-parse", "HEAD"):
                return "b" * 40
            if args == ("rev-parse", "FETCH_HEAD"):
                return LATEST["commit"]
            return ""

        with patch.object(updater, "latest_snapshot", return_value=LATEST):
            with patch.object(updater, "git", side_effect=fake_git):
                with self.assertRaises(updater.UpdateBlocked):
                    updater.ensure_latest(self.root)

    def test_matching_state_does_not_allow_missing_character_image(self):
        with patch.object(updater, "latest_snapshot", return_value=LATEST):
            with patch.object(updater, "download_package", side_effect=lambda _, dest: package(dest)):
                updater.ensure_latest(self.root)
            (self.root / "assets/ref.jpg").unlink()
            with self.assertRaises(updater.UpdateBlocked):
                updater.ensure_latest(self.root)


if __name__ == "__main__":
    unittest.main()
