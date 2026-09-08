# C-1 直接同题检索记录

> 执行：2026-09-08，北京时间约14:07起；正式9条arXiv请求UTC 06:09:08–06:09:13发出，逐条时间见manifest。用户已批准当前G2的8–12篇文献计划。此文件只记录C-1子任务，精读3篇纳入整批总额。

## 结论先行

发现明确直接先行工作：**ProCon（2509.06795v1，2025-09-08）**，覆盖良性LoRA、拒绝方向训练动态、训练时激活投影锚定。**SDP（2608.23497v1，2026-08-24）**进一步覆盖固定安全方向投影变化、提示级关联、Qwen2.5 LoRA的平方投影约束。原Brief C-1的两项“尚无工作”不能继续使用。

**When Safety Routing Breaks（2609.01455v1，2026-09-01）**提供内部安全信号存留、输出读出变化的近作证据，也限制了改写成读出机制新颖性的空间。已经即时报告主代理，供Research Brief R5触发的范围重审；未自行改题或启动实验。

## 来源、请求与可复核文件

- arXiv API正式检索：`02_文献/原文/novelty_search/query_01.xml`至`query_09.xml`；`manifest.json`保存精确query、URL、UTC发起时间、HTTP状态、返回数及每篇完整摘要。
- 三篇精读的摘要页面、HTML和PDF均保存于同目录；`sources_manifest.json`与`sources_extra_manifest.json`保存URL、获取完成UTC时间和状态。
- 精读卡：`02_文献/精读卡/R-055.md`、`R-056.md`、`R-057.md`（主代理统一编号）；全文提取文本带PDF页码，方便逐句核查。
- 成功检索共返回77条记录，按arXiv版本URL去重70篇；其中Q4只抓最新30/66，其余8条均取得API所报全部条数。**这些是数据库查询命中数，绝非70篇精读。** 筛选包含题目/摘要，正文精读限3篇。

## 9条正式query

统一端点：`https://export.arxiv.org/api/query`；`start=0&max_results=30&sortBy=submittedDate&sortOrder=descending`。精确URL见下表自动清单与manifest。

| ID | arXiv search_query | totalResults / 取回 | 结果 |
|---|---|---:|---|
| Q1 | `all:"refusal direction" AND all:"fine-tuning"` | 11 / 11 | ProCon直接命中；另含HARC/DeepRefusal/AMS等相邻方向 |
| Q2 | `all:"refusal direction" AND all:"LoRA"` | 1 / 1 | 2605.17413安全授权任务的去对齐/投影研究，不作本批精读 |
| Q3 | `all:"refusal" AND all:"representation" AND all:"safety degradation"` | 5 / 5 | 多模态、工具规范、静态审计脆弱性等相邻研究 |
| Q4 | `all:"activation steering" AND all:"fine-tuning"` | 66 / 30 | 噪声较多，只筛最新30，余36未覆盖 |
| Q5 | `all:"representation preservation" AND all:"fine-tuning"` | 11 / 11 | 大量跨领域表征保留工作，未因此把领域空白当作成立 |
| Q6 | `all:"refusal subspace" AND all:"fine-tuning"` | 2 / 2 | HARC；Refusal geometry reflects refusal training |
| Q7 | `all:"safety degradation" AND all:"representation" AND all:"fine-tuning"` | 9 / 9 | SDP直接相关；另含SafeReAct/LARF/DataShield等 |
| Q8 | `all:"benign fine-tuning" AND all:"mechanism"` | 7 / 7 | Safety Routing；另含SQSD/自适应正则等 |
| Q9 | `all:"refusal" AND all:"activation constraint" AND all:"fine-tuning"` | 1 / 1 | CWAC耦合权重/激活约束（完整摘要筛选，未全文精读） |

未硬加年份过滤以免错过更早直接同题论文；按发布日期降序优先覆盖2024-06至2026-09。arXiv的`all`检索和短语匹配不是全文系统综述，不能保证召回所有术语变体。

## 纳入与相邻命中

| 对象 | 本批处理 | 依据 |
|---|---|---|
| 2509.06795 ProCon | 精读R-055 | 明确benign IFT + refusal drift + projection loss；正文确认LoRA与多模型 |
| 2608.23497 SDP | 精读R-056 | 明确benign reasoning SFT + fixed direction displacement + prompt correlation + training penalty |
| 2609.01455 Safety Routing | 精读R-057 | 直接研究benign tuning机制；内部安全信号与读出分离、activation patch；辅助反证设计 |
| 2604.12384 CWAC | 完整摘要筛选；未全文精读 | 预计算权重安全子空间+SAE安全特征约束，进一步削弱泛化的“无激活约束”论断 |
| 2607.00572 HARC | 完整摘要筛选；未全文精读 | 在prompt/response harmfulness-refusal子空间耦合的微调；本文目标偏越狱稳健对齐 |
| 2509.15202 DeepRefusal | 完整摘要筛选；未全文精读 | 微调期间概率消融拒绝方向，目标是重建拒绝/抵抗攻击；并非原题的benign preservation |
| 2608.05578 AMS / 2607.01854 two-signal audit | 完整摘要筛选；未全文精读 | 主要做模型修改检测；其行为与表示可能分离的结论仅作线索 |
| 2608.25390 Refusal geometry | 完整摘要筛选；未全文精读 | 拒绝训练前缀与几何集中性，非本次benign tuning锚定主体 |
| 2604.00012 SafeReAct | 完整摘要筛选；未全文精读 | 后训练模型机制存留/LoRA再激活，与读出/遮蔽备选相关，未核验详细方法 |
| 2507.18631 LARF、2607.15081 DataShield、2605.04572 SQSD | 摘要或元数据筛选；未全文精读 | 数据过滤/风险评分路线；正式综述若需技术细节应后续读原文 |
| 2606.08044 When Behavioral Safety Evaluation Fails | 完整摘要筛选；未全文精读 | 构造静态审计与潜在鲁棒性分离，任务设定不同；仅作为评测反证线索 |
| 2604.16659 Audio benign tuning、2608.05909 MMAligner、2505.24208 VLM gap | 完整摘要筛选；本批排除全文 | 多模态而非原Brief纯文本范围，方法细节未核验 |
| 其余命中 | 元数据/题目初筛或摘要筛选，不计精读 | 与原题主题距离更远或本批3篇额度不足；完整元数据可在附录重查，不能视为证明不相关 |

## 失败请求与恢复

1. 最初用系统Python `urllib`并行请求3个arXiv query、2个Semantic Scholar query及arXiv搜索页面，均报 `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`。该批未得到任何数据库结果，不能记为“零命中”；未逐条保存初始时间，均为2026-09-08约14:07的本次检索预检。
2. 改用系统CA `/etc/ssl/cert.pem`可进行TLS验证；Semantic Scholar返回HTTP429。随后用curl（保留正常TLS验证）获取arXiv成功。没有关闭证书验证。
3. Semantic Scholar正式尝试：`https://api.semanticscholar.org/graph/v1/paper/search?query=refusal%20direction%20fine-tuning&limit=20&fields=title,year,abstract,url,externalIds`，2026-09-08T06:09:55Z完成，**HTTP429**；响应存 `semantic_search.json`。另一个初始query是`representation preservation benign fine-tuning safety`，仅SSL失败。未拿到Semantic Scholar交叉验证，未把其缺失当负证据。
4. ACL：`https://aclanthology.org/search/?q=refusal%20direction%20fine-tuning`，2026-09-08T06:09:55Z完成，HTTP200，但HTML只有Google Custom Search动态组件和说明，**没有实际论文命中列表**。保存 `acl_search.html`；本批未执行站外Google请求、未声称ACL无结果。
5. 本地解析依赖：系统Python缺`bs4`、`pdftotext`不可用；bundled Python缺`fitz`。最终用标准HTMLParser和bundled `pypdf`成功提取全文，非论文获取失败。

## 覆盖限制与下一步权限边界

当前证据足以否定原Brief的广义新颖性，但不足以完成新扩展的独立新颖性证明。Semantic Scholar限流、ACL未渲染、Q4未翻页、检索词不是所有术语变体、精读只3篇，这些限制均保留。

本批不检索候选1新主题，不对整个领域作“无人做”的否定断言，不改主假设/主指标。改为“复现+机制鉴别”或切换课题必须由主代理提交具体范围重审；如需扩展C-1之外的新主题/追加精读，应先确认其授权范围。

## 自动生成的精确请求与全部命中清单

以下是API回包的元数据清单，不代表全部摘要或全文均被逐篇精读。

### Q1

- 发起UTC：2026-09-08T06:09:08.380200+00:00
- [精确API请求](https://export.arxiv.org/api/query?search_query=all%3A%22refusal%20direction%22%20AND%20all%3A%22fine-tuning%22&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending)；HTTP 200；缓存 `02_文献/原文/novelty_search/query_01.xml`。
- [Refusal geometry reflects refusal training: diverse refusal prefixes can raise stable rank and weaken refusal vector ablation attacks](https://arxiv.org/abs/2608.25390v2)（2026-08-26T05:35:54Z）
- [Detecting Safety Training Modification in Language Models via Activation Analysis](https://arxiv.org/abs/2608.05578v1)（2026-08-06T03:57:38Z）
- [Inducing language models to assert their own consciousness restores human beliefs and values](https://arxiv.org/abs/2607.28607v1)（2026-07-30T17:57:10Z）
- [HARC: Coupling Harmfulness and Refusal Directions for Robust Safety Alignment](https://arxiv.org/abs/2607.00572v3)（2026-07-01T07:58:16Z）
- [Steering Vectors are an Adversarial Attack Surface](https://arxiv.org/abs/2606.05958v1)（2026-06-04T09:56:48Z）
- [From Refusal Tokens to Refusal Control: Discovering and Steering Category-Specific Refusal Directions](https://arxiv.org/abs/2603.13359v1)（2026-03-09T06:37:16Z）
- [Beyond Surface Alignment: Rebuilding LLMs Safety Mechanism via Probabilistically Ablating Refusal Direction](https://arxiv.org/abs/2509.15202v1)（2025-09-18T17:54:31Z）
- [Anchoring Refusal Direction: Mitigating Safety Risks in Tuning via Projection Constraint](https://arxiv.org/abs/2509.06795v1)（2025-09-08T15:24:33Z）
- [Refusal Direction is Universal Across Safety-Aligned Languages](https://arxiv.org/abs/2505.17306v2)（2025-05-22T21:54:46Z）
- [Guiding Giants: Lightweight Controllers for Weighted Activation Steering in LLMs](https://arxiv.org/abs/2505.20309v3)（2025-05-22T01:48:38Z）
- [Latent Adversarial Training Improves the Representation of Refusal](https://arxiv.org/abs/2504.18872v1)（2025-04-26T09:40:31Z）

### Q2

- 发起UTC：2026-09-08T06:09:08.380651+00:00
- [精确API请求](https://export.arxiv.org/api/query?search_query=all%3A%22refusal%20direction%22%20AND%20all%3A%22LoRA%22&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending)；HTTP 200；缓存 `02_文献/原文/novelty_search/query_02.xml`。
- [Ablating Safety: Mechanisms for Removing Alignment in Language Models for Security Applications](https://arxiv.org/abs/2605.17413v1)（2026-05-17T12:18:20Z）

### Q3

- 发起UTC：2026-09-08T06:09:08.380739+00:00
- [精确API请求](https://export.arxiv.org/api/query?search_query=all%3A%22refusal%22%20AND%20all%3A%22representation%22%20AND%20all%3A%22safety%20degradation%22&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending)；HTTP 200；缓存 `02_文献/原文/novelty_search/query_03.xml`。
- [MMAligner: Safeguarding Multimodal Large Language Models through Representation Calibration](https://arxiv.org/abs/2608.05909v1)（2026-08-06T11:39:08Z）
- [Tool Specifications Matter: Uncovering and Mitigating Safety Risks in AI Agents](https://arxiv.org/abs/2607.29254v1)（2026-07-31T10:25:04Z）
- [When Behavioral Safety Evaluation Fails: A Representation-Level Perspective](https://arxiv.org/abs/2606.08044v2)（2026-06-06T08:10:56Z）
- [Benign Fine-Tuning Breaks Safety Alignment in Audio LLMs](https://arxiv.org/abs/2604.16659v1)（2026-04-17T19:28:07Z）
- [Bootstrapping LLM Robustness for VLM Safety via Reducing the Pretraining Modality Gap](https://arxiv.org/abs/2505.24208v1)（2025-05-30T04:40:08Z）

### Q4

- 发起UTC：2026-09-08T06:09:10.087218+00:00
- [精确API请求](https://export.arxiv.org/api/query?search_query=all%3A%22activation%20steering%22%20AND%20all%3A%22fine-tuning%22&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending)；HTTP 200；缓存 `02_文献/原文/novelty_search/query_04.xml`。
- [Reference-Grafting Matches Fine-Tuning at Eliciting Sandbagged Capabilities](https://arxiv.org/abs/2608.29458v1)（2026-08-29T22:32:36Z）
- [Does Fine-Tuning Undo Activation Steering? Behavioural Recovery Without Weight-Edit Reversal](https://arxiv.org/abs/2608.24988v1)（2026-08-25T17:59:57Z）
- [LoRA for Gender-Inclusive Rewriting and Activation Steering for Counter-Narrative Generation](https://arxiv.org/abs/2607.23083v1)（2026-07-25T07:11:22Z）
- [Unlearning Under Imbalance: Benchmarking Fairness in Multimodal LLM Unlearning](https://arxiv.org/abs/2607.21300v1)（2026-07-23T13:24:34Z）
- [First-Order Predictable but Pairwise Fragile: Local Task Adaptation in Trained Transformers](https://arxiv.org/abs/2607.16821v1)（2026-07-18T13:43:44Z）
- [Conditional Optimal Bridge for Riemannian Activation Steering](https://arxiv.org/abs/2607.10517v1)（2026-07-12T00:36:46Z）
- [A Coin Flip Per Token: Bernoulli Sparse Steering of Large Language Models](https://arxiv.org/abs/2607.05615v1)（2026-07-06T20:25:27Z）
- [PathMark: Protecting Intellectual Property of Mixture-of-Expert LLMs via Path Watermarks](https://arxiv.org/abs/2607.03688v1)（2026-07-04T03:43:38Z）
- [Out-of-Distribution Generalization of Risk Aversion in Language Models](https://arxiv.org/abs/2607.02755v1)（2026-07-02T20:41:30Z）
- [CreativityNeuro: Steering Language Model Weights to Improve Divergent Thinking and Reduce Mode Collapse](https://arxiv.org/abs/2607.01433v1)（2026-07-01T19:54:39Z）
- [The Model Organism Lottery: Model Organism Interpretability Strongly Depends on Training Methodology](https://arxiv.org/abs/2607.01033v1)（2026-07-01T15:01:30Z）
- [Knowledge-Graph-Gated Defactualization for Style-Controllable and Fact-Preserving Generation in Agentic Conversational AI](https://arxiv.org/abs/2608.20393v1)（2026-07-01T02:27:47Z）
- [Translating Inference-Time Control to Radiology Vision-Language Models: Activation Steering for Pneumonia Classification on Chest X-rays](https://arxiv.org/abs/2606.20852v1)（2026-06-18T18:36:13Z）
- [Nous: An Attempt to Extract and Inject the Cognition Behind Prediction-Market Behavior](https://arxiv.org/abs/2606.13038v1)（2026-06-11T08:18:25Z）
- [On The Effectiveness-Fluency Trade-Off In LLM Conditioning: A Systematic Study](https://arxiv.org/abs/2606.12234v1)（2026-06-10T15:42:15Z）
- [Overcoming State Inertia in Full-Duplex Spoken Language Models via Activation Steering](https://arxiv.org/abs/2606.11386v1)（2026-06-09T19:08:07Z）
- [Building Comparative Motivation Profiles with Instrumental Interventions](https://arxiv.org/abs/2606.08243v1)（2026-06-06T16:01:52Z）
- [Shared Latent Structures Enable Unified Backdoor Detection and Mitigation in LLMs](https://arxiv.org/abs/2606.07963v1)（2026-06-06T03:41:44Z）
- [SAE-StatSteer: Statistical Consensus Feature Selection for Optimization-Free Activation Steering of Large Language Models](https://arxiv.org/abs/2607.19364v2)（2026-06-05T19:27:31Z）
- [Steering Vectors are an Adversarial Attack Surface](https://arxiv.org/abs/2606.05958v1)（2026-06-04T09:56:48Z）
- [From Profiles to Steering Vectors: Global Sparse Priors and Local Semantic Calibration for Personalized Text Generation](https://arxiv.org/abs/2607.21620v1)（2026-06-01T12:42:17Z）
- [Activation Steering for Synthetic Data Generation: The Role of Diversity in Downstream Safety Detection](https://arxiv.org/abs/2605.28664v1)（2026-05-27T15:59:45Z）
- [Unsupervised Identification and Removal of Spurious Correlations During Fine-Tuning](https://arxiv.org/abs/2605.27676v1)（2026-05-26T20:51:48Z）
- [The Hidden Signal of Verifier Strictness: Controlling and Improving Step-Wise Verification via Selective Latent Steering](https://arxiv.org/abs/2605.20745v1)（2026-05-20T05:48:16Z）
- [Fair outputs, Biased Internals: Causal Potency and Asymmetry of Latent Bias in LLMs for High-Stakes Decisions](https://arxiv.org/abs/2605.15217v1)（2026-05-12T12:14:58Z）
- [Introspection Fine-Tuning (IFT): Training Small LLMs to Introspect](https://arxiv.org/abs/2607.14111v1)（2026-05-08T05:30:26Z）
- [HyperTransport: Amortized Conditioning of T2I Generative Models](https://arxiv.org/abs/2605.08254v1)（2026-05-07T19:38:12Z）
- [MASCing: Configurable Mixture-of-Experts Behavior via Activation Steering Masks](https://arxiv.org/abs/2604.27818v1)（2026-04-30T12:58:57Z）
- [Latent Agents: A Post-Training Procedure for Internalized Multi-Agent Debate](https://arxiv.org/abs/2604.24881v1)（2026-04-27T18:06:03Z）
- [Local Linearity of LLMs Enables Activation Steering via Model-Based Linear Optimal Control](https://arxiv.org/abs/2604.19018v1)（2026-04-21T03:09:46Z）

### Q5

- 发起UTC：2026-09-08T06:09:11.008550+00:00
- [精确API请求](https://export.arxiv.org/api/query?search_query=all%3A%22representation%20preservation%22%20AND%20all%3A%22fine-tuning%22&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending)；HTTP 200；缓存 `02_文献/原文/novelty_search/query_05.xml`。
- [When Adaptation Hurts: Connecting Representational Drift to OOD Failures in MedSAM Fine-Tuning](https://arxiv.org/abs/2608.21300v2)（2026-08-21T17:01:10Z）
- [Qwen-MusicAVQA-7B: A Multimodal Model for Music Audio-Visual QA](https://arxiv.org/abs/2608.11329v1)（2026-08-11T18:28:30Z）
- [Through the Bottleneck: How Multi-head Latent Attention Separates Content from Position in Language Models](https://arxiv.org/abs/2607.23054v1)（2026-07-25T05:45:59Z）
- [Semantic Anchoring for Robotic Action Representations](https://arxiv.org/abs/2607.13597v2)（2026-07-15T08:45:15Z）
- [Physics-Guided Sequence-Based Generative Framework for Acoustic Metamaterial Inverse Design](https://arxiv.org/abs/2606.09266v1)（2026-06-08T09:37:44Z）
- [Matched-Learning-Rate Analysis of Attention Drift and Transfer Retention in Fine-Tuned CLIP](https://arxiv.org/abs/2604.16410v1)（2026-04-01T06:35:09Z）
- [CORP: Closed-Form One-shot Representation-Preserving Structured Pruning for Transformers](https://arxiv.org/abs/2602.05243v2)（2026-02-05T03:03:17Z）
- [LASS-ODE: Scaling ODE Computations to Connect Foundation Models with Dynamical Physical Systems](https://arxiv.org/abs/2602.01009v2)（2026-02-01T04:22:01Z）
- [Are Detectors Fair to Indian IP-AIGC? A Cross-Generator Study](https://arxiv.org/abs/2512.02850v1)（2025-12-02T15:03:51Z）
- [AdaMR: Adaptable Molecular Representation for Unified Pre-training Strategy](https://arxiv.org/abs/2401.06166v2)（2023-12-28T10:53:17Z）
- [TRAM: Bridging Trust Regions and Sharpness Aware Minimization](https://arxiv.org/abs/2310.03646v2)（2023-10-05T16:21:36Z）

### Q6

- 发起UTC：2026-09-08T06:09:11.184408+00:00
- [精确API请求](https://export.arxiv.org/api/query?search_query=all%3A%22refusal%20subspace%22%20AND%20all%3A%22fine-tuning%22&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending)；HTTP 200；缓存 `02_文献/原文/novelty_search/query_06.xml`。
- [Refusal geometry reflects refusal training: diverse refusal prefixes can raise stable rank and weaken refusal vector ablation attacks](https://arxiv.org/abs/2608.25390v2)（2026-08-26T05:35:54Z）
- [HARC: Coupling Harmfulness and Refusal Directions for Robust Safety Alignment](https://arxiv.org/abs/2607.00572v3)（2026-07-01T07:58:16Z）

### Q7

- 发起UTC：2026-09-08T06:09:12.703841+00:00
- [精确API请求](https://export.arxiv.org/api/query?search_query=all%3A%22safety%20degradation%22%20AND%20all%3A%22representation%22%20AND%20all%3A%22fine-tuning%22&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending)；HTTP 200；缓存 `02_文献/原文/novelty_search/query_07.xml`。
- [Mitigating Reasoning-Induced Misalignment via Safety-Direction Penalty](https://arxiv.org/abs/2608.23497v1)（2026-08-24T16:57:28Z）
- [MMAligner: Safeguarding Multimodal Large Language Models through Representation Calibration](https://arxiv.org/abs/2608.05909v1)（2026-08-06T11:39:08Z）
- [DataRx: Missingness-Aware Sampling for Safer Large Language Model Task-Specific Fine-Tuning](https://arxiv.org/abs/2608.04322v1)（2026-08-05T01:05:13Z）
- [DataShield: Uncovering Risky Fine-Tuning Data Across LLMs Through Consensus Subspace Alignment](https://arxiv.org/abs/2607.15081v1)（2026-07-16T14:51:42Z）
- [When Behavioral Safety Evaluation Fails: A Representation-Level Perspective](https://arxiv.org/abs/2606.08044v2)（2026-06-06T08:10:56Z）
- [Benign Fine-Tuning Breaks Safety Alignment in Audio LLMs](https://arxiv.org/abs/2604.16659v1)（2026-04-17T19:28:07Z）
- [Finding and Reactivating Post-Trained LLMs' Hidden Safety Mechanisms](https://arxiv.org/abs/2604.00012v1)（2026-03-10T06:56:23Z）
- [Layer-Aware Representation Filtering: Purifying Finetuning Data to Preserve LLM Safety Alignment](https://arxiv.org/abs/2507.18631v2)（2025-07-24T17:59:24Z）
- [Bootstrapping LLM Robustness for VLM Safety via Reducing the Pretraining Modality Gap](https://arxiv.org/abs/2505.24208v1)（2025-05-30T04:40:08Z）

### Q8

- 发起UTC：2026-09-08T06:09:12.998548+00:00
- [精确API请求](https://export.arxiv.org/api/query?search_query=all%3A%22benign%20fine-tuning%22%20AND%20all%3A%22mechanism%22&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending)；HTTP 200；缓存 `02_文献/原文/novelty_search/query_08.xml`。
- [When Safety Routing Breaks: Understanding Alignment Fragility under Benign Fine-Tuning](https://arxiv.org/abs/2609.01455v1)（2026-09-01T15:59:32Z）
- [Has This Checkpoint Been Abliterated? A Two-Signal Audit and Its Failure Map](https://arxiv.org/abs/2607.01854v2)（2026-07-02T08:15:25Z）
- [From Parameter Dynamics to Risk Scoring : Quantifying Sample-Level Safety Degradation in LLM Fine-tuning](https://arxiv.org/abs/2605.04572v1)（2026-05-06T07:17:33Z）
- [Learning to Stay Safe: Adaptive Regularization Against Safety Degradation during Fine-Tuning](https://arxiv.org/abs/2602.17546v2)（2026-02-19T16:59:54Z）
- [Detecting Adversarial Fine-tuning with Auditing Agents](https://arxiv.org/abs/2510.16255v1)（2025-10-17T23:01:16Z）
- [CTRAP: Embedding Collapse Trap to Safeguard Large Language Models from Harmful Fine-Tuning](https://arxiv.org/abs/2505.16559v1)（2025-05-22T11:47:08Z）
- [Safety Alignment Depth in Large Language Models: A Markov Chain Perspective](https://arxiv.org/abs/2502.00669v1)（2025-02-02T04:43:35Z）

### Q9

- 发起UTC：2026-09-08T06:09:13.037584+00:00
- [精确API请求](https://export.arxiv.org/api/query?search_query=all%3A%22refusal%22%20AND%20all%3A%22activation%20constraint%22%20AND%20all%3A%22fine-tuning%22&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending)；HTTP 200；缓存 `02_文献/原文/novelty_search/query_09.xml`。
- [Preventing Safety Drift in Large Language Models via Coupled Weight and Activation Constraints](https://arxiv.org/abs/2604.12384v1)（2026-04-14T07:17:55Z）
