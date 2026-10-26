<p align="center">
  <img src="assets/icon.jpg" width="128" alt="鹿图DeerPhotos鹿头图标">
</p>

<h1 align="center">鹿图DeerPhotos</h1>

<p align="center">用固定角色演绎真实生活，把聚餐、旅行和日常片段留成AI照片。</p>

<p align="center">
  <a href="VERSION"><img src="https://img.shields.io/badge/version-2.1.0-333333?style=flat-square" alt="版本2.1.0"></a>
  <a href="SKILL.md"><img src="https://img.shields.io/badge/type-Agent_Skill-333333?style=flat-square" alt="类型：Agent Skill"></a>
  <a href="#快速开始"><img src="https://img.shields.io/badge/tool-image__gen-555555?style=flat-square" alt="生图工具：image_gen"></a>
  <a href="#角色参考"><img src="https://img.shields.io/badge/characters-10-555555?style=flat-square" alt="10位固定角色"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-333333?style=flat-square" alt="MIT许可证"></a>
  <a href="https://github.com/Roylyl/DeerPhotos/stargazers"><img src="https://img.shields.io/github/stars/Roylyl/DeerPhotos?style=flat-square&amp;color=555555" alt="GitHub Stars"></a>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> ·
  <a href="#主要功能">主要功能</a> ·
  <a href="#角色参考">角色参考</a> ·
  <a href="#怎么描述场景">场景示例</a> ·
  <a href="#维护人物档案">人物维护</a>
</p>

鹿图是一套面向Codex等Agent环境的生图技能。它把朋友的本名、昵称和专属形象对应起来，让同一批角色出现在不同生活场景中。你可以直接说“毛毛、企鹅和困困去吃宵夜”，再接着说“还是他们，换成海边”，不用每次重新描述人物外观。

内置10位成员、68个别名、10张原始参考图和10张白底全身4视图，并按160cm、175cm、180cm三组参考身高安排多人画面。

## 快速开始

当前版本为[2.1.0](VERSION)。需要能读取本地文件、查看图片并调用生图工具的Agent环境，以及可访问GitHub并下载、解压源码的能力。鹿图默认使用内置`image_gen`，技能本身不包含独立生图程序。

### 安装后调用

1. 获取完整的`DeerPhotos`目录，保留其中的`SKILL.md`、`agents/`、`references/`和`assets/`。
2. 将目录放入`$CODEX_HOME/skills/`；未设置`CODEX_HOME`时使用`~/.codex/skills/`。可将文件夹命名为`deerphotos`，入口为`skills/deerphotos/SKILL.md`。
3. 当前会话识别技能后，使用`$deerphotos`并描述场景：

```text
$deerphotos

毛毛、企鹅和困困凌晨在路边摊吃面，三个人都入镜。
像朋友用手机随手拍的，横向构图，保留各自形象。
```

### 直接指定路径

也可以将本地[SKILL.md](SKILL.md)的路径交给Agent，请它使用鹿图完成同样的请求。整个文件夹需要能被读取；只提供技能正文会缺少人物档案和图片。

生成结果包含图片与简短场景记录。需要指定保存位置时，直接在请求中补充目录。若当前环境没有可用的生图工具，鹿图会说明情况并提供提示词和参考图清单。

### 每次运行前更新

每次使用鹿图，Agent都会先访问GitHub官网检查[GitHub的main分支](https://github.com/Roylyl/DeerPhotos/tree/main)。有更新时尝试下载并替换已安装的技能，保留旧副本作为备份。更新后重新读取新规则，后续改图请求也会重新检查。

检查或更新失败时，继续使用本地可用版本生成，并提示前往[GitHub项目](https://github.com/Roylyl/DeerPhotos)更新最新版Skill。Git开发目录有未提交改动时跳过自动更新，保留本地工作并继续生成。具体检查方式和备份位置见[更新规则](references/updates.md)。

## 主要功能

- 固定人物身份：本名和昵称对应同一角色，延续脸型、物种、发型、体型及标志性配件。
- 多角度参考：每位角色提供正面、朝左侧面、朝右侧面和背面，便于安排全身动作与镜头角度。
- 多人比例：按参考身高与远近透视安排高矮，保留每个人原有的胖瘦和肢体比例。
- 口语指令：理解“全员除了某人”“换成某人”“还是刚才那几个”“其他不变”等表达。
- 连续修改：沿用已确认的人物，调整地点、天气、服装、姿势或摄影风格。
- 场景记录：随图片保留出场名单、参考文件、提示词和版本，方便继续修改。

## 角色参考

每张图是同一个角色的4个角度，从左到右依次为正面、朝画面左的侧面、朝画面右的侧面、背面。点击可查看大图。

<table>
  <tr>
    <td align="center"><a href="assets/characters/li-yanzhen/turnaround-v1.png"><img src="assets/characters/li-yanzhen/turnaround-v1.png" width="440" alt="李彦臻的白底全身4视图"></a><br>李彦臻·175cm</td>
    <td align="center"><a href="assets/characters/luo-yulun/turnaround-v1.png"><img src="assets/characters/luo-yulun/turnaround-v1.png" width="440" alt="罗宇伦的白底全身4视图"></a><br>罗宇伦·175cm</td>
  </tr>
  <tr>
    <td align="center"><a href="assets/characters/peng-peng/turnaround-v1.png"><img src="assets/characters/peng-peng/turnaround-v1.png" width="440" alt="彭鹏的白底全身4视图"></a><br>彭鹏·175cm</td>
    <td align="center"><a href="assets/characters/tang-bofu/turnaround-v1.png"><img src="assets/characters/tang-bofu/turnaround-v1.png" width="440" alt="唐博釜的白底全身4视图"></a><br>唐博釜·175cm</td>
  </tr>
  <tr>
    <td align="center"><a href="assets/characters/tang-yinxin/turnaround-v1.png"><img src="assets/characters/tang-yinxin/turnaround-v1.png" width="440" alt="唐胤鑫的白底全身4视图"></a><br>唐胤鑫·175cm</td>
    <td align="center"><a href="assets/characters/tu-tenghui/turnaround-v1.png"><img src="assets/characters/tu-tenghui/turnaround-v1.png" width="440" alt="涂腾辉的白底全身4视图"></a><br>涂腾辉·160cm</td>
  </tr>
  <tr>
    <td align="center"><a href="assets/characters/wei-ziqi/turnaround-v1.png"><img src="assets/characters/wei-ziqi/turnaround-v1.png" width="440" alt="魏子奇的白底全身4视图"></a><br>魏子奇·180cm</td>
    <td align="center"><a href="assets/characters/xia-weicheng/turnaround-v1.png"><img src="assets/characters/xia-weicheng/turnaround-v1.png" width="440" alt="夏炜城的白底全身4视图"></a><br>夏炜城·180cm</td>
  </tr>
  <tr>
    <td align="center"><a href="assets/characters/zhan-shaoyuan/turnaround-v1.png"><img src="assets/characters/zhan-shaoyuan/turnaround-v1.png" width="440" alt="詹绍源的白底全身4视图"></a><br>詹绍源·175cm</td>
    <td align="center"><a href="assets/characters/li-jianyu/turnaround-v1.png"><img src="assets/characters/li-jianyu/turnaround-v1.png" width="440" alt="黎健毓的白底全身4视图"></a><br>黎健毓·160cm</td>
  </tr>
</table>

### 多人场景身高

| 参考身高 | 角色 |
| --- | --- |
| 180cm | 魏子奇、夏炜城 |
| 175cm | 李彦臻、罗宇伦、彭鹏、唐博釜、唐胤鑫、詹绍源 |
| 160cm | 涂腾辉、黎健毓 |

这些身高用于画面中的相对比例，按脚底至头顶计算，不含鹿角等突出部分。远近透视、坐姿和台阶另行处理，单人参考板上的像素高度不用于比较不同角色。

<details>
<summary>查看本名与常用别名</summary>

| 本名 | 部分别名 |
| --- | --- |
| 李彦臻 | 吉吉毛毛、毛毛、李彦毛、臻哥、蒸鸽、蒸哥 |
| 罗宇伦 | 企鹅、扑克、朴客、撸一撸、录一录 |
| 彭鹏 | 彭鸟、鸟鸟、鸟别 |
| 唐博釜 | 唐伯虎、唐白虎、虎先锋 |
| 唐胤鑫 | 唐狗、tango、帅狗、狗别 |
| 涂腾辉 | 涂涂、鹿、鹿腾辉、兔爷、兔兔、涂爷、涂别 |
| 魏子奇 | 拍别、魏别、维基吧、重庆别、青蛙、蛙别、鹿子奇、五子棋 |
| 夏炜城 | 龟龟、龟炜城、夏别、龟别、龟头 |
| 詹绍源 | 鹿绍源、困困、水豚、困别、战绩吧、詹味、展位、水豚噜噜 |
| 黎健毓 | 寝委书记、书记、记记、记吧、黎书记、哆啦A梦、哆啦B梦、B梦、健叔 |

</details>

原始形象与多角度参考均随包保存。完整图片、生成提示词和补全说明见[多角度参考与身高](references/standardized-views.md)，人物对应关系见[人物档案](references/characters.json)。

## 怎么描述场景

直接说明谁出场、在哪里、做什么，再按需要补充摄影风格即可。

> 黎书记、企鹅和毛毛去露营，傍晚坐在帐篷外聊天，像手机抓拍。

> 全员在民宿吃火锅，兔爷坐中间，狗别这次不出镜，不加名字。

> 沿用上一张，把鸟别也加进来，其他人的外观、位置和光线保持一致。

> 换成雨天的海边，还是刚才那三个人，大家穿便服。

鹿图会结合语境理解称呼：

| 说法 | 对应理解 |
| --- | --- |
| 毛毛、臻哥和企鹅 | 李彦臻、罗宇伦，共两位 |
| 书记、健叔和B梦 | 都是黎健毓，只出现一位 |
| 鹿子奇、鹿绍源和鹿 | 魏子奇、詹绍源、涂腾辉，共三位 |
| 青蛙和企鹅下五子棋 | 两位成员下棋，不把活动当成第三个人 |
| 在展位打扑克，录一录视频 | 根据句意理解地点和活动，不机械匹配昵称 |
| 不是企鹅，是鸟别 | 替换对应人物，保留其余条件 |

更多用法见[指令变体与示例](references/instruction-variants.md)。如果“我”“他们”或某个称呼缺少明确对应关系，会先确认影响出场名单的信息。

## 维护人物档案

[characters.json](references/characters.json)保存人物身份、别名、参考图、外观特征和参考身高。

| 需要调整 | 做法 |
| --- | --- |
| 新增昵称 | 明确说明“以后也叫某人某昵称”，加入该人物的`aliases` |
| 新增人物 | 提供本名、别名和明确对应的形象图，建立独立人物记录 |
| 更新默认形象 | 提供新图并说明是长期默认，更新参考路径和可见特征 |
| 临时换装 | 在场景请求中描述服装，不覆盖长期身份档案 |
| 调整参考身高 | 修改该人物的`reference_height_cm`，用于后续多人构图 |

新参考板用于全身姿态，脸部和配件细节可回查原图。原图没有展示的侧背面属于生成补全；例如涂腾辉的全身西装造型，是在半身参考的基础上补出西裤、皮鞋和手部。

```text
DeerPhotos/
├── VERSION                          # 当前版本
├── SKILL.md                         # 技能入口
├── README.md
├── LICENSE
├── scripts/ensure_latest.py         # 旧版可选更新工具
├── agents/openai.yaml               # 名称、图标与默认调用
├── assets/
│   ├── icon.jpg                     # 项目图标
│   └── characters/                  # 原图、4视图和生成提示词
└── references/
    ├── characters.json              # 人物档案与身高
    ├── instruction-variants.md      # 口语指令示例
    ├── standardized-views.md        # 多角度参考索引
    └── updates.md                   # 更新与失败回退规则
```

生图时，场景描述与所选参考图会交给当前环境的生图工具；服务规则、费用和额度由实际工具及账户决定。所有生成场景均为AI演绎。

## 许可

本项目采用[MIT许可证](LICENSE)，版权所有©2026 Roylyl。
