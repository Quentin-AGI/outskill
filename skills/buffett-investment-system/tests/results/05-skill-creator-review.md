# Phase 5｜Skill-Creator Perspective 独立精炼审查

## 结论

**判定：有条件通过，暂不建议按当前状态公开发布。**

命名、必需 frontmatter、UI 元数据、Codex／Claude Code 单一权威源码结构、核心运行边界、按需 reference 路由和七类行为验收的方向均成立。`skill-creator` 的 `quick_validate.py` 通过；包内 `validate_package.py` 通过；隔离安装与安装后复验通过（41 个文件，约 540 KB）。

但“机器可安装”尚未覆盖许可文本、私有索引误入包、跨年度更新和预发布状态残留。以下 4 项为发布前阻断项，之后 4 项为应尽量在首发前完成的收敛项。

## P1｜发布阻断项

### 1. 分发包没有携带完整许可证正文

**证据**：`LICENSE.md` 把 `LICENSES/Apache-2.0.txt` 和 `LICENSES/CC-BY-4.0.txt` 当作许可文件引用，但前者只有 14 行摘要，后者也明确写着 “This summary is not a substitute for the legal code”。

**风险**：公开包声明代码采用 Apache-2.0，却未随分发物附上该许可证完整文本；文件名又会让使用者误以为已经包含正式许可证。CC 文件同样混淆“许可正文”和“人类可读摘要”。

**修订**：用官方完整、未改写的 Apache-2.0 文本和 CC BY 4.0 legal code 替换这两个文件；保留 `LICENSE.md` 作为范围说明，并在验证器中检查许可证的关键段落或官方校验值。正式发布前可再做一次独立许可核对；本意见不是法律意见。

### 2. 私有语料隔离在误操作路径下会失效

**证据**：`scripts/epub_locator.py:104-112` 把绝对 `source_path` 写入 JSON；README 允许任意 `--output`；`.gitignore` 未忽略常见的 `*book-index*.json`／`private-index*.json`；`scripts/install.py:19-49` 不排除这类索引或 `*.transcript.txt`；`validate_package.py:86-108` 只按少数文件后缀和单一本机目录模式检测泄漏。

**风险**：用户若把索引输出到 Skill 内部，Git 和安装脚本都可能带走本机路径、书籍指纹、目录定位等私有元数据，而现有验证仍可能通过。这直接违反“私有语料不分发”的产品边界。

**修订**：默认把索引写入 Skill 外的明确私有目录，并拒绝输出到 `SKILL_DIR` 子树；索引中删除绝对 `source_path`，只保留可选文件名或哈希；同步强化 `.gitignore`、安装忽略规则和通用路径／私有索引结构扫描（macOS、Linux、Windows）。

### 3. 公开 references 仍包含会让 Agent 暂停的预发布状态

**证据**：`references/research/PHASE-1-REVIEW.md:5,56` 仍称“等待用户确认”“进入 Phase 2 前需要确认”；`references/synthesis/PHASE-2-REVIEW.md:3,65` 仍称等待进入构建；`references/synthesis/01-core-models.md:3` 仍标“Phase 2 提炼稿”；`references/sources/book-map.md:3,72` 仍使用“将在 Phase 1／后续将”的未来时。

**风险**：这些文件由 `SKILL.md` 明确路由，Agent 在审计或查证时可能把已完成产品误判为尚待确认，从而重复暂停或执行已经完成的阶段。它也削弱公开包的版本可信度。

**修订**：保留审计轨迹，但把状态统一为“已确认／已合成／随版本归档”，把未来式改为已完成事实；或移入明确的 `references/provenance/`，在顶部注明“历史审计记录，不是运行指令”。发布验证应拒绝 `等待用户确认`、`后续将` 等未收敛标记。

### 4. 更新清单在 2027 年会静默漏掉新年度新闻页

**证据**：`references/sources/update-sources.json:18-21` 和基线都固定为 `BRK-NEWS-2026`／`2026news.html`，而 `check_updates.py` 不会按当前年份发现新页面。

**风险**：产品承诺“每次使用先检测新的官方一手材料”，但跨年后脚本仍可返回成功，同时未检查 2027 及以后新发布材料；这是静默漏检而非显式降级。

**修订**：使用 Berkshire 稳定新闻索引作为发现入口，或由脚本按当前年份生成并核验年度 URL，同时保留前一年回查；基线记录解析后的实际 URL。增加 12 月 31 日／1 月 1 日跨年测试，年度页尚未建立时必须显示可理解的降级状态，不能伪装成“无更新”。

## P2｜首发前强烈建议

### 5. 自动触发条件仍然过宽

**证据**：frontmatter 描述和 `05-runtime-protocol.md` 把“用户提到巴菲特／Berkshire”本身列为强激活，而用户已把范围限定为投资、企业经营和受托责任。

**风险**：出生日期、慈善新闻、人物史等非投资问题也会加载 209 行入口说明并触发联网更新流程；后续还可能误读不相关 references，增加路由和上下文成本。

**修订**：把发现描述改成“用户围绕巴菲特／Berkshire 提出投资、企业分析、管理层、资本配置或受托责任问题时”；人物名仅作为与任务意图组合的信号。负向边界保留在正文，描述中只写最可能的误路由排除项。

### 6. 主文件与运行协议重复，渐进披露收益被抵消

**证据**：209 行的 `SKILL.md` 已完整规定更新、澄清、两遍分析、估值、全球校正和 11 项输出，随后又要求现实分析读取 262 行的 `05-runtime-protocol.md`；两处大量逐项重复。

**风险**：最常见的公司／估值请求会同时加载两套近似规则，浪费上下文并提高以后修订分叉概率。研究过程文件、Phase review 和测试结果也被安装脚本无差别复制。

**修订**：保留 `SKILL.md` 中真正跨模式的不可违背约束和路由，把步骤、表格、七场景细则只放在 runtime reference；或反向删去 runtime 中已经完整存在于主文件的段落。安装器可增加默认 runtime 清单与显式 `--include-dev`，但不能删掉运行时实际路由到的证据和许可文件。

### 7. README 与 adapter 的安装命令依赖未说明的当前目录

**证据**：README 和两个 adapter 都给出 `python3 scripts/install.py`，但目标 GitHub 仓库将 Skill 放在 `skills/buffett-investment-system/`；从仓库根目录或 adapter 目录照抄会找不到脚本。`install.py` 也未拒绝把目标放进源码自身子树，项目路径拼错时会自动创建目录。

**风险**：本次隔离安装通过使用的是显式包路径，并非 README 在目标仓库根目录下的原样命令；用户体验测试因此存在盲点。

**修订**：在 outskill 仓库语境统一给出 `python3 skills/buffett-investment-system/scripts/install.py ...`，或先明确 `cd skills/buffett-investment-system`；adapter 说明同样写清起始目录。安装器拒绝目标等于或位于 `SOURCE_DIR` 内，并在项目级安装前验证 `--project-dir` 已存在且为目录。

### 8. 发布验证偏向字符串存在，尚未验证上述真实不变量

**证据**：`validate_package.py` 主要检查固定短语、标题数量和 7 个场景是否有非空断言；未检查内部链接、许可证完整性、泛化本地路径、私有索引、跨年 URL、预发布状态、脚本编译和 README 命令。证据编号规范写成 `B1/O7`，测试结果却使用 `B-0030/O-1993`，也未被发现。

**风险**：当前全部 PASS 不能阻止真正的发布缺陷，且证据 ID 方言会削弱“中英统一证据链”的可审计性。

**修订**：在不把行为测试退化为文字快照的前提下，增加内部链接遍历、JSON/YAML schema、完整许可证、隐私模式、跨年 fixture、脚本 `--help`／编译、仓库根目录安装 dry-run 和陈旧状态扫描；明确“回答内临时编号”与“稳定来源 ID”是否不同，并统一主规范与测试示例。

## 已通过且建议保持不变

- 目录名、frontmatter `name` 与文件夹一致，符合小写连字符及长度约束。
- `agents/openai.yaml` 的展示名、默认 prompt、显式 `$buffett-investment-system` 和隐式激活策略基本一致；`short_description` 只有 19 个中文字符，低于文档建议的 25—64 字符，可在处理第 5 项时顺手补足。
- 不冒充、原书优先、芒格隔离、行为归因、文档指令隔离、估值停止、全球校正和用户最终决策权均在入口文件中可见。
- references 有清楚的任务路由，研究正文保存中文转述和英文定位，当前包内未发现 EPUB、PDF、完整转写或现有本机绝对路径。
- Codex 与 Claude Code 没有维护第二套知识正文，符合“单一权威源码＋平台适配”。

## 建议的修订顺序

`完整许可证 → 私有语料防泄漏 → 清理预发布状态 → 跨年更新 → 收窄触发 → 去重与安装文档 → 扩充验证 → 全量复验`
