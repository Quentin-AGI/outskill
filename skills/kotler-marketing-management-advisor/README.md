# 科特勒式营销管理顾问

[English](README.en.md)

一个以 Kotler、Keller、Chernev 合著《营销管理》第16版为稳定核心的通用 Agent Skill。它把全书组织为三层式营销管理操作系统：主控顾问、七个深度工作流、企业私有工作区；首批使用情境针对刚开始品牌化或已有稳定销量、正在增长的跨境电商团队，但核心方法不依赖特定平台。

## 它能做什么

- 从具体问题进入，只补齐会改变判断的最小信息；完整企业营销体检是可选入口。
- 用 G-STIC、5C、3V、7T 和六个心智模型保持全局一致。
- 深入处理用户洞察、目标市场、品牌定位、产品组合、定价、渠道与投放、营销团队管理。
- 重大决策生成营销决策板；用户决定后继续形成行动、指标、复盘与知识沉淀。
- 在顾问模式和边做边学模式之间按意图切换。
- 对关键事实标明书中章节、外部来源、企业提供者或推断链。

它不会把平台规则、其他营销流派或最新市场做法伪装成原书方法。启用任何扩展方法前，必须先说明边界并取得用户同意。

## 三层结构

1. **主控层**：[`SKILL.md`](SKILL.md) 负责意图识别、资料闸门、路由、证据纪律和决策闭环。
2. **专业层**：[`modules/`](modules/) 提供七个工作流；[`chapters/`](chapters/) 提供覆盖21章的按需知识层。
3. **私有层**：企业事实、咨询案例、个人学习档案、批准知识、扩展方法和本地原书索引保存在公开 Skill 之外。

公开包只含原创提炼和定位信息，不含 EPUB、连续原文或私有企业数据。详见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

## 开始使用

脚本需要 Python 3.10 或更高版本。

把整个目录放进支持 Agent Skills 的环境，然后直接提出业务问题，例如：

```text
我们准备进入美国市场，但还没确定先服务谁。请用顾问模式帮我做目标市场决策。
```

```text
请切到边做边学模式，带我完成一次品牌定位，并解释每一步对应第16版哪一章。
```

跨境安装脚本默认为预演，不会写文件：

```bash
python3 scripts/install.py --platform codex --scope user
python3 scripts/install.py --platform claude --scope user
```

确认目标后加 `--apply`。项目级安装需传 `--scope project --project-dir <目录>`；也可用 `--target-root <目录>` 明确目标。现有安装不会被覆盖；只有显式加 `--force` 时才先做时间戳备份。

## 初始化企业私有工作区

先预演：

```bash
python3 scripts/init_workspace.py <私有工作区目录>
```

确认后：

```bash
python3 scripts/init_workspace.py <私有工作区目录> --apply
```

POSIX 系统默认用目录 `0700`、文件 `0600` 创建。企业可以通过外部 ACL 显式共享团队案例，但不要递归放宽个人学习档案；每位成员应在自己的操作系统账号或独立私有根中保存个人档案。Windows 等无法由脚本保证 ACL 的环境会显示警告，必须先由管理员配置访问控制。

使用时把工作区路径明确告诉 Agent，或设置 `KOTLER_MARKETING_WORKSPACE`；Skill 不会扫描主目录寻找企业资料。每位成员的个人学习档案默认只对本人可见；企业知识只有经营销负责人批准才能晋级为正式品牌营销知识。

## 可选：绑定本地原书

没有原书也可完整使用公开核心。合法持有 EPUB 的用户可以在私有工作区建立只含元数据、目录定位、大小和摘要哈希的索引：

```bash
python3 scripts/epub_locator.py index --epub <原书.epub> --output <私有工作区>/book/index.json
```

使用索引中的精确项目与锚点做本地短摘录核对；单次输出硬限制为最多 800 个 Unicode 字符，不能输出整份 XHTML：

```bash
python3 scripts/epub_locator.py excerpt --epub <原书.epub> --item <项目路径> --anchor <锚点> --max-chars 500
```

必要短摘录只能在本地增强模式中显示；不得批量调用以重建正文或把索引写回公开包。索引已存在时默认拒绝覆盖，只有显式加 `--force` 才先备份后替换。

## 演示与验收

- [`完整 Mock 品牌教程`](examples/mock-brand/end-to-end-tutorial.md)：从问题澄清到90天复盘，串联七个工作流。
- [`五个关键变体`](examples/mock-brand/five-variants.md)：只改变一个关键条件，检查顾问是否真正更新判断。
- [`安克 2011 冻结案例`](examples/anker-2011/frozen-case.md)：将 T0 输入与评测者密封材料物理分离，防止用后来的成功倒推早期决策。
- [`行为场景`](tests/scenarios.json)：包含正例、边缘例、隐私、证据和身份边界。

运行静态验证：

```bash
python3 scripts/validate_package.py
python3 scripts/smoke_test.py
```

`smoke_test.py` 只在临时目录生成合成 EPUB、安装副本和私有工作区，用于验证 EPUB2/3、短摘录上限、权限、原子安装与递归路径防护。

不同宿主的说明见 [`Codex`](adapters/codex/README.md) 与 [`Claude Code`](adapters/claude-code/README.md)。

## 角色与归属

“科特勒式”是交互风格和营销管理传统，不代表 Philip Kotler 本人或官方代理。第16版由 Philip Kotler、Kevin Lane Keller、Alexander Chernev 合著；书中第2章的 G-STIC、5C、3V、7T 等图式应按包内来源注册表保留准确归属。

## 许可与署名

- `scripts/` 中的原创代码：Apache License 2.0；
- 其他原创文档、模板和结构化知识：CC BY 4.0；
- 原书、译文、案例文本、商标以及用户私有资料不随本项目重新许可。

详情见 [LICENSE.md](LICENSE.md) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

作者与维护者：[一笑而过](https://github.com/Quentin-AGI)
方法支持：[女娲 · Skill 造人术](https://github.com/alchaincyf/nuwa-skill)
