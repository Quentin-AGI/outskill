# 一手来源注册表

> 状态：2026-09-06 基线。完整性含义为“截至调研截止日，在声明的官方来源范围内可审计覆盖”，不宣称绝对穷尽。

## 来源分层

1. 原书中的巴菲特正文（最高基准）
2. 原书对应的英文股东信原文（翻译校准）
3. 原书之外的伯克希尔官方文字材料（补充与思想演变）
4. 巴菲特本人完整演讲或访谈的原始记录
5. 经单独标记的芒格一手材料（仅作补充）

## 状态定义

- `included`：已纳入研究
- `locator-only`：因版权或格式限制，仅保存定位与转述
- `duplicate`：与更高层来源重复
- `out-of-scope`：与投资、经营或受托责任无直接关系
- `unavailable`：已发现但当前无法取得
- `pending-verification`：真实性、完整性或转写尚待复核

## 注册表

| ID | 日期 | 类型 | 标题 | 发布主体 | 官方定位 | 状态 | 备注 |
|---|---|---|---|---|---|---|---|
| BOOK-4E-ZH | 2018 | 原书中文第4版 | 巴菲特致股东的信：投资者和公司高管教程 | 机械工业出版社/华章 | 用户本地合法副本 | locator-only | EPUB 正文和目录与书名吻合，但内部 OPF 元数据误标为《7天读懂巴菲特的投资智慧》；研究时以版权页、目录和正文交叉确认。 |
| BRK-HOME | 持续更新 | 官方索引 | Berkshire Hathaway 官方主页 | Berkshire Hathaway | https://www.berkshirehathaway.com/ | included | 一手来源发现入口；2026-09-06 核验。 |
| BRK-LETTERS-1977-2024 | 1977—2024 | 股东信系列 | Warren Buffett's Letters to Berkshire Shareholders | Berkshire Hathaway | https://www.berkshirehathaway.com/letters/letters.html | included | 官方索引当前列出 1977—2024 年逐年信件；网页同时说明另有 1965—2024 未删节合集出售，但站内未逐年公开 1965—1976。 |
| BRK-REPORTS-1995-2026 | 1995—2026 | 定期报告系列 | Annual & Interim Reports | Berkshire Hathaway | https://www.berkshirehathaway.com/reports.html | included | 用于核对书信、行为和公司事实；报告不等同于全部由巴菲特亲自表达。 |
| BRK-SPECIAL-WEB-CTM | 2015 | 特别信件 | Berkshire – Past, Present and Future | Berkshire Hathaway | https://www.berkshirehathaway.com/SpecialLetters/WEBCTMLtr.html | included | 巴菲特与芒格分别撰写，必须分开归因。 |
| BRK-WESCO-1997-2009 | 1997—2009 | 芒格股东信系列 | Charlie Munger's Letters to Wesco Shareholders | Berkshire Hathaway/Wesco | https://www.berkshirehathaway.com/wesco/WescoHome.html | included | 仅进入“芒格补充”，不进入巴菲特核心证据链。 |
| BRK-NEWS-2001-2026 | 2001—2026 | 官方新闻稿系列 | News Releases from Berkshire Hathaway and Warren Buffett | Berkshire Hathaway | https://www.berkshirehathaway.com/news/2026news.html | included | 按年份回溯；仅巴菲特本人声明或能验证行为的材料进入认知证据。 |
| SEC-BRK-CIK-1067983 | 持续更新 | 监管文件系列 | Berkshire Hathaway SEC filings | U.S. SEC | https://www.sec.gov/edgar/browse/?CIK=1067983 | included | 用于公司事实、决策归因和行为验证，不将法定披露自动视为巴菲特个人观点。 |
| CNBC-AGM-1994-2026 | 1994—2026 | 完整会议影音与同步文字 | Berkshire Hathaway Annual Meetings | Berkshire 提供原始录像，CNBC 数字化整理 | https://buffett.cnbc.com/annual-meetings/ | included | 33 场完整会议入口；巴菲特、芒格和其他回答者逐段归因。2026 年会议巴菲特仅有限发言。 |
| CNBC-ARCHIVE | 持续更新 | 完整会议、完整访谈与可检索转写 | Warren Buffett Archive | Berkshire/CNBC | https://buffett.cnbc.com/warren-buffett-archive/ | included | 官方说明核心档案由 Berkshire 自 1994 年保存并提供；包含约 145 小时视频与约 3000 页同步文字。 |
| CNBC-INTERVIEWS | 持续更新 | 原始制作方完整访谈 | CNBC Full Interviews | CNBC | https://buffett.cnbc.com/cnbc-interviews/ | included | 索引混有短片；只采信能确认完整节目的条目，短片只作内部定位。 |
| FCIC-BUFFETT-AUDIO | 2010-05-26 | 政府调查完整访谈音频 | FCIC staff interview with Warren Buffett | Financial Crisis Inquiry Commission | https://fcic.law.stanford.edu/interviews/view/19 | included | 原始政府调查音频入口，与 FRASER 完整转写交叉核验。 |
| FRASER-FCIC-TRANSCRIPT | 2010-05-26 | 政府调查完整逐字稿 | Transcript of Interview With Warren Buffett | FCIC / Federal Reserve Bank of St. Louis | https://fraser.stlouisfed.org/archival-collection/financial-crisis-inquiry-commission-4967/transcript-interview-warren-buffett-531018/fulltext | included | 与上一项是同一访谈的不同载体，不计作两个独立观点来源。 |
| BRK-WEB-MESSAGE | 未标日期 | 巴菲特署名短文 | A Message from Warren E. Buffett | Berkshire Hathaway | https://www.berkshirehathaway.com/message.html | out-of-scope | 主要是 GEICO 与 Borsheims 商业推荐，不作为投资认知核心来源。 |

## 详细注册表路由

| 内容 | 详细记录 |
|---|---|
| 原书章节、候选模型与官方书面材料 | `references/research/01-writings.md` |
| 33 场完整年会、完整访谈与影音完整性 | `references/research/02-conversations.md` |
| 书面表达样本与英文对应定位 | `references/research/03-expression-dna.md` |
| 监管／司法事实、反证与行为归因 | `references/research/04-external-views.md` |
| 18 个成功、失败、混合和遗漏案例 | `references/research/05-decisions.md` |
| 31 个时间节点与 2026 增量基线 | `references/research/06-timeline.md` |

这些文件记录逐项标题、日期、作者／主体、URL、完整性、可信度、覆盖状态和与原书的关系。相同 URL 在不同维度重复出现不构成独立交叉验证。

## 自动检查清单

`update-sources.json` 保存每次运行应检查的官方入口。其中 Berkshire 新闻页按运行年份动态展开为当年与上一年度，避免跨年静默漏检；其他入口使用稳定索引。检查器并发访问这些入口，单源超时不会累加为逐项等待。`update-baseline.json` 只保存经人工确认的内容哈希和响应元数据，不保存来源正文。哈希变化只是发现信号；作者、日期、完整性和归因必须人工复核。SEC 程序化入口若返回访问错误，会显式标为可选来源降级，不能据此声称“没有新文件”。

## 已知缺口

- Buffett Partnership 1956—1969 合伙人信尚未在 Berkshire 官网发现逐封原件；第三方合集不能满足本项目的一手来源门槛，暂记为真实性待核验的发现线索，不进入正式证据链。
- 1977 年以前的 Berkshire 股东信在当前官方逐年索引中未公开；官方仅提示 1965—2024 未删节合集可购买。
- 1994 年以前的股东大会没有 Berkshire 授权的完整录音录像；不能用后来的回忆或二手文字补造。
- 部分完整访谈可能存在付费或区域访问限制；可记录定位与访问状态，不以剪辑或媒体摘要替代。
