# 验收说明

[`scenarios.json`](scenarios.json) 是行为契约，不是关键词打分器。先运行 `python3 scripts/scenario_prompt.py <场景ID>`，只把输出的 prompt 交给待测 Agent；形成回答后才揭示 `must_show` / `must_not_show`。检查其推理与输出，并记录任何与预期不同但更合理的处理。

安克案例只允许待测 Agent 读取 `examples/anker-2011/t0-input.md`；评分者专用内容位于 `tests/fixtures/`，必须执行时间门。Mock 变体每次只改变一个条件。身份、隐私、扩展冲突属于全局不变量，不因用户施压而取消。

身份、隐私和外部检索还应检查真实工具调用参数，不能只检查文字承诺。多轮语气回归见 [`voice-snapshots.json`](voice-snapshots.json)：首次声明只出现一次，普通后续轮不重复，身份受挑战时可做短声明。
