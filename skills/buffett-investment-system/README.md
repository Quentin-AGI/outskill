# 巴菲特投资认知系统

[English](README.en.md)

一个以《巴菲特致股东的信：投资者和公司高管教程》（原书第 4 版）为最高基准、面向 Codex 与 Claude Code 的通用 Agent Skill。

它不是语录机器人，也不冒充巴菲特本人。它把巴菲特的投资方法转化为可审计、可运行的分析系统：先建立用户的问题模型，再全局扫描企业、管理层、财务、资本配置、估值和风险，最后选择决定性维度深入分析，并把最终判断留给用户。

## 能做什么

- 分析上市公司、非上市企业和管理层；
- 审查投资论证与关键假设；
- 在定性门槛通过后进行区间估值；
- 分析并购、回购、分红、债券、保险浮存金和交易结构；
- 讨论个人资产配置与投资纪律；
- 按概念或原书章节主动教学；
- 对已完成决策进行事后复盘；
- 检查新的官方一手材料，并在人工确认后更新知识库。

## 核心设计

- **原书最高**：坎宁安只作导航，英文原信用于校准，后续官方材料单列扩展与演变。
- **证据分层**：明确区分巴菲特说过的、实际做过的、系统推演、领域事实和芒格补充。
- **七个核心模型**：所有者视角、能力圈、质量复利、所有者收益、价值与资本配置、生存优先、受托治理。
- **两遍式分析**：先完整扫描，再选择性深挖，并披露遗漏、缺口和否决项。
- **允许不知道**：定性门槛不通过时明确停止估值，不输出伪精确目标价。
- **全球校正**：分析不同市场时强制检查治理、会计、税务、监管与少数股东保护。
- **不冒充本人**：可以使用第一人称分析视角，但不虚构巴菲特经历、口吻或原话。

## 安装

仓库目录是唯一权威源码。以下命令均从 `outskill` 仓库根目录执行；安装脚本默认只预览目标，只有加入 `--apply` 才复制文件。若已进入本 Skill 目录，可把脚本路径缩短为 `scripts/install.py`。

### Codex 用户级安装

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform codex
python3 skills/buffett-investment-system/scripts/install.py --platform codex --apply
```

### Claude Code 用户级安装

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform claude
python3 skills/buffett-investment-system/scripts/install.py --platform claude --apply
```

### 项目级安装

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform codex --scope project --project-dir /path/to/project --apply
python3 skills/buffett-investment-system/scripts/install.py --platform claude --scope project --project-dir /path/to/project --apply
```

已有同名安装时脚本会停止。明确使用 `--force` 后，旧版本会先移动到带时间戳的备份目录，不会直接删除。

更具体的平台说明见 [Codex 适配](adapters/codex/README.md)和 [Claude Code 适配](adapters/claude-code/README.md)。

## 使用

示例：

```text
使用 $buffett-investment-system 审查我的投资论证，一次只问一个关键问题。
```

```text
用巴菲特投资认知系统分析这家公司。先核对最新一手材料，再判断是否有资格估值。
```

```text
按原书第 6 章教我理解所有者收益；用案例检验，不要一次讲完。
```

系统支持基础、标准和专业三种本次深度，并会按会计、行业、估值、治理和组合等维度动态调整解释方式。

## 关联自备原书

公开包不包含 EPUB。持有合法副本的用户可在仓库之外生成不可还原的私有索引：

```bash
python3 skills/buffett-investment-system/scripts/epub_locator.py index \
  --epub /absolute/path/to/your-book.epub \
  --output /absolute/private/path/buffett-book-index.json
```

读取特定章节只输出到终端，不写回公开包：

```bash
python3 skills/buffett-investment-system/scripts/epub_locator.py read \
  --epub /absolute/path/to/your-book.epub \
  --item text/part0062.html
```

索引不记录原书路径，脚本也会拒绝把索引写进 Skill 目录。仍不要把原书、完整转写、私有索引或本地路径提交到公开仓库。

## 更新检查

```bash
python3 skills/buffett-investment-system/scripts/check_updates.py
```

哈希变化只代表“可能有新内容”，不证明新内容由巴菲特撰写，也不会自动修改知识库。维护者完成人工归因、日期、完整性和原书关系审查后，才可记录新基线：

```bash
python3 skills/buffett-investment-system/scripts/check_updates.py --write-baseline --confirm-reviewed
```

## 证据与版权边界

公开包只包含原创中文转述、结构化模型、案例分析和英文来源定位，不包含原书 EPUB、长篇原文、完整影音转写或可替代原作的连续内容。研究范围与已知缺口见 [来源注册表](references/sources/source-registry.md)。

## 许可

- `scripts/` 中的原创代码：Apache License 2.0；
- 其余原创文档与结构化内容：Creative Commons Attribution 4.0 International；
- 第三方书籍、演讲、访谈、商标和链接内容不随本项目重新许可；
- 私有语料层不属于发布物。

详情见 [LICENSE.md](LICENSE.md) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 署名

作者与维护者：[一笑而过](https://github.com/Quentin-AGI)
方法支持：[女娲 · Skill 造人术](https://github.com/alchaincyf/nuwa-skill)
