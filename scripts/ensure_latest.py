#!/usr/bin/env python3
"""Check GitHub on every invocation and update DeerPhotos before use."""

import argparse
import datetime
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
import zipfile


REPOSITORY = "Roylyl/DeerPhotos"
BRANCH = "main"
GIT_URL = "https://github.com/" + REPOSITORY + ".git"
STATE_FILE = ".deerphotos-update.json"
MAX_DOWNLOAD = 512 * 1024 * 1024
MAX_UNPACKED = 1024 * 1024 * 1024


class UpdateBlocked(Exception):
    pass


def version_tuple(value):
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value):
        raise UpdateBlocked("版本号必须为major.minor.patch，无法确认版本时禁止运行。")
    return tuple(int(part) for part in value.split("."))


def read_version(root):
    try:
        value = (root / "VERSION").read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise UpdateBlocked("本地缺少可读取的VERSION文件。") from exc
    version_tuple(value)
    return value


def request(url):
    headers = {
        "User-Agent": "DeerPhotos-Update-Gate",
        "Accept": "application/vnd.github+json",
        "Cache-Control": "no-cache",
    }
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=headers), timeout=30
    )


def fetch_bytes(url, limit):
    with request(url) as response:
        body = response.read(limit + 1)
    if len(body) > limit:
        raise UpdateBlocked("GitHub响应超过预期大小，停止更新。")
    return body


def latest_snapshot():
    # A Git commit ID identifies the snapshot. No file checksums are calculated.
    url = "https://api.github.com/repos/" + REPOSITORY + "/commits/" + BRANCH
    metadata = json.loads(fetch_bytes(url, 1024 * 1024))
    commit = metadata.get("sha", "")
    if not re.fullmatch(r"[0-9a-f]{40,64}", commit):
        raise UpdateBlocked("GitHub没有返回有效的main提交标识。")
    url = "https://raw.githubusercontent.com/" + REPOSITORY + "/" + commit + "/VERSION"
    try:
        version = fetch_bytes(url, 128).decode("utf-8").strip()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise UpdateBlocked(
                "GitHub的main分支尚无VERSION；无法确认最新版本，禁止运行。"
            ) from exc
        raise
    version_tuple(version)
    return {"commit": commit, "version": version}


def git(root, *arguments):
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=120, check=False,
    )
    if result.returncode:
        raise UpdateBlocked("Git更新失败：" + result.stderr.strip())
    return result.stdout.strip()


def validate_package(root, expected_version):
    for name in (
        "VERSION", "SKILL.md", "scripts/ensure_latest.py",
        "agents/openai.yaml", "references/characters.json",
    ):
        if not (root / name).is_file():
            raise UpdateBlocked("下载包缺少必要文件：" + name)
    if read_version(root) != expected_version:
        raise UpdateBlocked("下载包版本与刚检查的GitHub版本不一致。")
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    if not re.search(r"^name:\s*deerphotos\s*$", skill, re.MULTILINE):
        raise UpdateBlocked("下载包不是deerphotos技能。")
    # Check only referenced resources needed to run the skill, not file hashes.
    roster = json.loads((root / "references/characters.json").read_text(encoding="utf-8"))
    if not roster.get("people"):
        raise UpdateBlocked("下载包缺少人物档案。")
    for person in roster["people"]:
        for reference in person["visual"]["references"]:
            path = Path(reference["path"])
            if path.is_absolute() or ".." in path.parts or not (root / path).is_file():
                raise UpdateBlocked("下载包缺少有效的角色参考：" + str(path))


def download_package(commit, destination):
    url = "https://codeload.github.com/" + REPOSITORY + "/zip/" + commit
    total = 0
    with request(url) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_DOWNLOAD:
                raise UpdateBlocked("更新包超过大小限制。")
            output.write(chunk)


def unpack_package(archive, destination):
    prefix = None
    total = 0
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            parts = PurePosixPath(info.filename).parts
            if (
                not parts or info.filename.startswith("/") or "\\" in info.filename
                or ".." in parts or ".git" in parts or ":" in info.filename
            ):
                raise UpdateBlocked("更新包包含不安全的路径。")
            if prefix is None:
                prefix = parts[0]
            if parts[0] != prefix:
                raise UpdateBlocked("更新包包含多个根目录。")
            kind = stat.S_IFMT(info.external_attr >> 16)
            if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise UpdateBlocked("更新包包含不支持的链接或特殊文件。")
            total += info.file_size
            if total > MAX_UNPACKED:
                raise UpdateBlocked("更新包解压大小超过限制。")
            if len(parts) == 1:
                continue
            target = destination.joinpath(*parts[1:])
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)


def state_matches(root, latest):
    try:
        state = json.loads((root / STATE_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (
        state.get("repository") == REPOSITORY
        and state.get("commit") == latest["commit"]
        and state.get("version") == latest["version"]
        and read_version(root) == latest["version"]
    )


def update_git_checkout(root, latest):
    if git(root, "status", "--porcelain", "--untracked-files=normal"):
        raise UpdateBlocked("Git开发目录存在未提交改动；保留原文件并停止，不自动覆盖。")
    if git(root, "rev-parse", "HEAD") == latest["commit"]:
        validate_package(root, latest["version"])
        return {}
    git(root, "fetch", "--no-tags", GIT_URL, BRANCH)
    if git(root, "rev-parse", "FETCH_HEAD") != latest["commit"]:
        raise UpdateBlocked("检查期间GitHub分支已变化，请重新执行本次更新检查。")
    git(root, "merge", "--ff-only", "--no-overwrite-ignore", "FETCH_HEAD")
    if git(root, "rev-parse", "HEAD") != latest["commit"]:
        raise UpdateBlocked("本地提交与GitHub最新提交不同，可能尚未发布；禁止运行。")
    validate_package(root, latest["version"])
    return {"updated": True}


def update_installation(root, latest):
    if state_matches(root, latest):
        validate_package(root, latest["version"])
        return {}
    backup_parent = root.parent / ("." + root.name + "-backups")
    with tempfile.TemporaryDirectory(prefix="." + root.name + "-update-", dir=root.parent) as tmp:
        tmp = Path(tmp)
        archive = tmp / "package.zip"
        staged = tmp / "skill"
        staged.mkdir()
        download_package(latest["commit"], archive)
        unpack_package(archive, staged)
        validate_package(staged, latest["version"])
        state = {
            "repository": REPOSITORY, "branch": BRANCH,
            "commit": latest["commit"], "version": latest["version"],
        }
        (staged / STATE_FILE).write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        backup_parent.mkdir(exist_ok=True)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = backup_parent / (stamp + "-" + uuid.uuid4().hex[:8])
        root.rename(backup)
        try:
            staged.rename(root)
        except OSError:
            backup.rename(root)
            raise
    return {"updated": True, "backup": str(backup)}


def ensure_latest(root):
    root = root.resolve(strict=True)
    local = read_version(root)
    latest = latest_snapshot()  # Always network; state is never an offline pass.
    if version_tuple(local) > version_tuple(latest["version"]):
        raise UpdateBlocked(
            "本地版本" + local + "高于GitHub版本" + latest["version"]
            + "，可能尚未发布；不降级，也不放行。"
        )
    lock = root.parent / ("." + root.name + "-update.lock")
    try:
        descriptor = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise UpdateBlocked("另一次更新正在进行；若进程已终止，请处理遗留锁文件：" + str(lock)) from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(str(os.getpid()) + "\n")
        git_parent = next(
            (p for p in (root, *root.parents) if (p / ".git").exists()), None
        )
        if git_parent is not None and git_parent != root:
            raise UpdateBlocked("技能位于另一个Git工作树内部；请使用独立的已安装技能目录。")
        if git_parent == root:
            details = update_git_checkout(root, latest)
        else:
            details = update_installation(root, latest)
        return {
            "status": "ready", "updated": details.get("updated", False),
            "repository": REPOSITORY, "branch": BRANCH,
            "version": latest["version"], "commit": latest["commit"],
            "skill_dir": str(root),
            "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            **details,
        }
    finally:
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = ensure_latest(args.skill_dir)
    except (
        UpdateBlocked, OSError, ValueError, KeyError, TypeError,
        urllib.error.URLError, subprocess.SubprocessError, zipfile.BadZipFile,
    ) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, ensure_ascii=False))
        return 20
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
