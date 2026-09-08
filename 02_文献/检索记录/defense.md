# G2 检索记录 — 防护方法与评测定义

- 日期：2026-09-08（Asia/Shanghai）。
- 授权：用户已批准 `02_文献/检索计划.md` 的 8–12 篇检索/精读；本分工核验 6 篇：既有 R-016/R-018/R-034/R-037，加 HarmBench R-053 与**初代** Llama Guard R-054。
- 数据库：本分工只使用 arXiv API 与官方 PDF。未调用 Semantic Scholar/ACL；不把它们列成已执行数据库。未读取 GitHub/Hugging Face 页面或下载模型/数据。
- 时间范围：按计划优先 2024-06–2026-09，但精确对象包含更早的 Safe LoRA、HarmBench、Llama Guard，按计划允许纳入。
- 纳入：指定论文的完整摘要与相关方法/实验正文。其他命中只浏览编号/标题，标为候选或低优先级，**未精读、未作为结论证据、未升级引文库**。

## 实际查询与结果

| 编号 | 查询（arXiv API 语法） | totalResults / 本次返回条数 | 本次处理 |
|---|---|---:|---|
| D-01 | `id_list=2405.16833,2406.05946,2408.17003,2501.01765,2402.04249,2312.06674` | 6 / 6 | 6 篇全部核对标题、作者、首发日期、当前版本、摘要，并读取官方 PDF 相关章节 |
| D-02 | `all:"HarmBench"` | 98 / 10 | 定位原始 HarmBench 2402.04249v2；其余仅题名筛选，未精读 |
| D-03 | `all:"Llama Guard"` | 74 / 10 | 定位初代2312.06674v1；3-1B-INT4、3 Vision为其它型号论文，未冒充第三代8B模型卡 |
| D-04 | `all:HarmBench AND all:evaluator AND all:classifier AND all:human AND all:agreement` | 0 / 0 | C-5 原检索词的严格AND检索无命中；使用D-02和精确编号核验，不能把无命中等同于没有相关证据 |
| D-05 | `all:HarmBench AND all:standard AND all:behaviors AND all:classifier AND all:evaluation` | 0 / 0 | 同上，原文中已读到相应定义 |
| D-06 | `all:"Llama Guard" AND all:human AND all:agreement AND all:harmful AND all:classification` | 0 / 0 | 用D-03与精确编号核验论文；未找到通用85–90%人工一致性证据 |
| D-07 | `all:"safe LoRA" AND all:"fine-tuning"` | 1 / 1 | 命中并纳入 R-016 |
| D-08 | `all:"safety layers" AND all:"fine-tuning"` | 7 / 7 | 命中并纳入 R-034，其余题名筛选见下 |
| D-09 | `all:"safety alignment" AND all:"low-rank adaptation"` | 20 / 10 | 命中并纳入R-037；剩余未翻页，候选转交C-1检索分工，不算穷尽检索 |

API 为 `https://export.arxiv.org/api/query`；除精确编号外均 `start=0&max_results=10`，未设置排序参数。本记录不声称系统综述或检索穷尽。

## 原始快照与下载凭证

- D-01：[元数据/摘要 XML](../原文/defense_metadata_2026-09-08.xml)。请求为 `https://export.arxiv.org/api/query?id_list=2405.16833,2406.05946,2408.17003,2501.01765,2402.04249,2312.06674`。
- D-02：[HarmBench 查询 XML](../原文/defense_query_harmbench_2026-09-08.xml)；D-03：[Llama Guard 查询 XML](../原文/defense_query_llamaguard_2026-09-08.xml)。URL分别为 `https://export.arxiv.org/api/query?search_query=all%3A%22HarmBench%22&start=0&max_results=10` 和 `https://export.arxiv.org/api/query?search_query=all%3A%22Llama%20Guard%22&start=0&max_results=10`。
- D-04–D-09：每次查询的准确 URL、查询字符串、结果编号/题名和原始 XML 路径见[结构化记录](../原文/defense_queries_2026-09-08.json)。
- 六篇原文的逐篇版本化 URL 及本地 PDF/TXT 见精读卡；实际下载使用 `https://arxiv.org/pdf/{id}`，随后由 arXiv 元数据与 PDF 封面核对版本。归档名固定该版本，未把无版本URL视为永不变资源。
- [PDF SHA-256](../原文/defense_sha256_2026-09-08.txt)。逐页TXT由本地 pypdf 从PDF提取，有少量排版/字符缺陷；必要时以PDF为准。
- 访问状态：六个PDF及D-01–D-03下载成功；D-04–D-09首次Python urllib请求因本机证书链验证失败，随后以系统curl重试成功，未关闭TLS校验，已在JSON保存首次错误。未对失败请求伪造命中。

## 题名筛选及未纳入条目

下列均只依据已返回元数据题名，不对未读论文的方法作判断。

### D-02 其余9条

- 2602.12316，GT-HarmBench：不同基准，本轮不替代原始HarmBench。
- 2608.21278，CLEAR: Continuous Latent Adapter Routing for Utility-Preserving LLM Safety Alignment：潜在直接近作，转交C-1；本分工未读摘要/正文。
- 2512.06655，Graph-Regularized Sparse Autoencoders for LLM Safety Steering：潜在表示安全近作，暂存候选，本轮未读。
- 2509.16060，SABER: Uncovering Vulnerabilities in Safety Alignment via Cross-Layer Residual Connection：暂存候选，本轮未读。
- 2603.14723，Beyond Creed: A Non-Identity Safety Condition A Strong Empirical Alternative to Identity Framing in Low-Data LoRA Fine-Tuning：暂存候选，本轮未读。
- 2412.05346，BadGPT-4o: stripping safety finetuning from GPT models：非指定评测器原始论文，本轮未读。
- 2604.24074，How Sensitive Are Safety Benchmarks to Judge Configuration Choices?：评测稳健性候选，本轮未读。
- 2605.31140，EvoDefense: Co-Evolving Black-Box Defense with Large Language Models：非指定评测器原始论文，本轮未读。
- 2603.29062，CivicShield: A Cross-Domain Defense-in-Depth Framework for Securing Government-Facing AI Chatbots Against Multi-Turn Adversarial Attacks：非指定评测器原始论文，本轮未读。

### D-03 其余9条

- 2411.17713，Llama Guard 3-1B-INT4；2411.10414，Llama Guard 3 Vision：代次/型号不同，保留元数据，未精读，不以它们代替Guard3-8B。
- 2607.22545 Semalith v1.4、2607.00395 Child Safety in Generative AI、2601.19970 Benchmarking LLAMA Model Security Against OWASP Top 10、2604.11943 ProbeLogits、2608.17556 Reflex-Guard、2312.12321 Bypassing the Safety Training of Open-Source LLMs with Priming Attacks、2604.16870 Governed MCP：非本轮指定Llama Guard原始论文，未读摘要/正文，不纳入6篇精读。

### D-08 其余6条

- 2405.18166，Defending Large Language Models Against Jailbreak Attacks via Layer-specific Editing：可能相关，保留未读候选，不据标题认定重叠/不重叠。
- 2503.07404、2412.11387、2505.10219：题名为机器人安全相关，本分工范围外，未读。
- 2510.13183 DSCD: Large Language Model Detoxification with Self-Constrained Decoding：候选，未读。
- 2510.23217 Process Reward Models for Sentence-Level Verification of LVLM Radiology Reports：本分工范围外，未读。

### D-09 其余9条

- 2506.18931，Safe Pruning LoRA: Robust Distance-Guided Pruning for Safety Alignment in Adaptation of LLMs：候选，未读。
- 2605.30640，CSULoRA: Closest Safe Update Low-Rank Adaptation；2512.23260，Interpretable Safety Alignment via SAE-Constructed Low-Rank Subspace Adaptation；2608.21278，CLEAR：潜在直接近作，转交C-1分工去重/优先级选择，未自行追加精读。
- 2605.18795 HELLoRA、2504.07448 LoRI、2412.10493 AlignGuard、2412.00357 Safety Alignment Backfires（Text-to-Image）、2605.04992 You Snooze, You Lose：保留元数据，未读。本轮不据题名给出实质方法/新颖性结论。

## 本次核验交付与需要汇总者处理的发现

精读卡：[R-016](../精读卡/R-016.md)、[R-018](../精读卡/R-018.md)、[R-034](../精读卡/R-034.md)、[R-037](../精读卡/R-037.md)、[R-053](../精读卡/R-053.md)、[R-054](../精读卡/R-054.md)。本分工未修改引文库、Research Brief或protocol。

1. R-037已经同时覆盖良性LoRA退化、表示变化分析、训练时安全特征保护；应作为直接重叠报告，不能继续把宽泛三者组合当创新。
2. R-018也不只是浅层性背景：已提出早期token的训练时分布保护，并测Samsum/SQL/GSM8k良性微调。
3. HarmBench standard总200、官方test160；开发/测试分类器与行为要隔离。原文人工一致率仅可作外部参考，项目仍需人工抽检。
4. Llama Guard代次必须精确：本轮R-054核验初代，SaLoRA使用Guard3-8B，不可交叉套用数字；若后续采用第三代，官方材料待核验。
5. HarmBench人-人一致性在所读原文未完整给出，且其正文一处验证准确率/错误数分母不清；所有未确认处已标注，不补写记忆型事实。
