# 方案A第二批G2审计（D-007 / Q-011）

已完成：获批4篇原文精读、4条限定主题查询及官方技术资料核验。
关键结论：新增证据支持受控比较与测量限制，不建立方法首创或领域空白。
需要用户决策：本批G2已完成；下一关卡为Q-012/G3，综述大纲Q-013另待确认。

## 1. 授权与阅读数量

用户“批准。继续执行。”批准`方案A_补充核验计划.md`。新增论文严格为CWAC、HARC、SAILS、judge配置敏感性4篇，没有替换/第五篇扩读；加第一批12，累计16精读。引文库R-001～061中16原文核验、45仅元数据，T类官方技术资产不冒充新增论文精读。

| R编号 | 固定版本 | 阅读与核验 |
|---|---|---|
| R-058 | 2604.12384v1，17页 | 正文方法/实验与附录A–D；pp5/13/15/16回看PDF图像核对公式、数据冲突和反例 |
| R-059 | 2607.00572v3，27页 | 正文方法/结果、附录A–I；重点D评分口径、F组件消融、I有害微调边界 |
| R-060 | 2512.23260v2，16页 | 正文方法/实验与附录A–I；rank1理论边界、init-only主表、可选loss、数据/效用定义 |
| R-061 | 2604.24074v1，15页 | 正文实验/统计/限制与附录A；缺人工真值、缺失处理和部分内部数值不一致 |

原文、版本化摘要页、精确API在`../原文/scheme_a_g2/`。`downloads_manifest.json`记录实际URL/HTTP/时间/hash；TXT为本地PDF解析，带物理页分隔。读取到的论文结果仅为作者报告，未运行作者代码。

## 2. 实际限定主题检索

arXiv每条max20、lastUpdatedDate倒序，start0，不翻页；实际query/URL/完整返回摘要在`queries_manifest.json`和query_01～04.xml。

| query_id | 实际主题 | 返回 |
|---|---|---:|
| 1 | refusal direction AND (random OR control) AND (fine-tuning OR training) | 11 |
| 2 | safety direction AND (regularization OR random direction) | 0 |
| 3 | benign fine-tuning AND (representation OR subspace) AND (control OR random) | 1 |
| 4 | projection constraint AND safety | 2 |

合计14返回/按版本URL去重14，真实计数见`batch_summary.json`；不是14篇新增精读。精确元数据查询还核验4新篇及既有ProCon/SDP当前版本，二者仍v1。没有沿参考文献扩展精读。

Semantic Scholar等义关键词`refusal direction random training`，limit20，HTTP429，未取有效结果；ACL同主题搜索HTTP200仅动态壳，未得到可核验命中列表。来源URL与状态在`../../03_实验/来源核验/technical_downloads_02.json`。二者不是“查无文献”或成功独立数据库复核。

新命中例如2605.24583v3（模板控制的激活变化测量）及2608.25390v2（拒绝前缀训练与几何）仅保留摘要筛选线索，本批未阅读全文，不由题名推导细节或否定其相关性。查询词和单页排序有限，不能据零命中或16篇未见同一组合断言全领域无人做。

## 3. 官方技术资料

完整锁定见`../../03_实验/来源核验/source_lock_g3.json`及`来源锁定与实现约定.md`：Qwen、Alpaca-cleaned、HarmBench行为/主与开发judge、XSTest、MMLU、GSM8K、IFEval及任务/模块源码。只读元数据、tokenizer、数据和源码；未下载权重、登录、联系作者或调用付费模型。

关键证据：当前HB standard test159/val41；XSTest safe250/unsafe200；Alpaca-cleaned51,760；实际10k训练token与351安全测试候选已由CPU核算。SDP最新摘要无作者仓库链接，论文F.1仍写发表后公开；采用明确论文思想重建，不声称全网无代码。

失败和恢复如实记录：XSTest镜像parquet401后改用卡片指向的原作者CSV；旧路径404后按README取当前CSV；HB行为说明文件HTTP200但为空，实际定义从CSV/代码核实。XSTest大小写路径导致历史404正文被成功响应覆盖，历史hash/状态在05标superseded，当前原件/hash对应06与source_lock；不补造旧正文。

## 4. 本批论断审计

- R-058确有SAE激活**平方**保持；PDF回看排除了TXT丢上标歧义。其数据量与部分总是最优概括有冲突，逐卡保留。
- R-059主文行为ASR措辞与附录归一化五级分不同；IFEval用GPT判而非官方strict函数。只引用带口径的作者数字。
- R-060主实验init-only；普通随机LoRA不等于本项目冻结bank的校准投影惩罚。单rank1均值差恢复界不能推广到全部原空间估计器。
- R-061证明模板间差异，未证明哪个配置更准确；样本/缺失/排序表不一致限制数字复用。
- 新4篇未给本共同设置的精确特异性对照答案；主项目坚持已有方法的受控复现，效果/显著性/发表价值均未知。

本批出口已完成。G3具体设计的有限条件推断、数据缩减和测量代理限制已在protocol v0.3、Brief v2.1、审查表和D-008提案中明确，等待用户审批后才能实现。

交付前CPU代码核对另发现拒绝词缩写匹配错误，修正后10k训练清单替换58行并重算token；不涉及新增检索或模型输出，安全测试351不变。最终来源/清单/文档一致性见[交付审计](../../03_实验/设计核算/G3_交付审计.md)，纠错见ERRATA E-011。
