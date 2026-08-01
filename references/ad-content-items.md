# AD 内容项：ISO/IEC/IEEE 42010 逐条要求

本文是产出清单的权威依据。写作或评审 AD 时按此核对。

## 一手依据与其边界

| 来源 | 用途 | 可靠性 |
|---|---|---|
| ISO/IEC/IEEE 42010:2022 官方免费预览（前 15 页） | 第 4 章一致性条款、第 3 章全部术语定义、第 6 章条款目录、Scope、Foreword 的变更说明 | 一手，原文 |
| 42010 官方配套站点的 AD 模板（Rich Hilliard，"bare bones" 版，2014 rev 2.2） | 各条款的 must/should 逐条落地 | 一手性质，但**对应 2011 版** |
| 42010 官方站点 Conceptual Model 页（WG42 维护） | 2022 版概念变更与新概念的作用 | 一手性质 |

**需要注意的版本落差**：官方模板是 2011 版的。2022 版的条款编号与部分术语已变（见下「2022 版变更」）。本文已按 2022 版重排条款号，但标注 must/should 时依据的是 2011 版模板——凡 2022 版可能改变了强制性的地方，均已显式标注不确定。

## 第 4 章：一致性（决定了「必需」的范围）

原文要点：

- "The requirements in this document are contained in Clauses 6, 7 and 8."
- 对一份 AD 声明一致性时："the claim shall demonstrate that the specification of the architecture description meets the requirements listed in **Clause 6**"。
- 五种可声明一致性的对象：AD（第 6 章）、ADF（7.1）、ADL（7.2）、architecture viewpoint（8.1）、model kind（8.2）。
- "This document is designed such that 'tailoring' is neither required nor permitted for its use when claims of conformance are made."

**推论**：声明「按 42010 组织」就必须覆盖第 6 章全部十项。可以声明某项「不适用」并说明理由，但不能默默省略。

## 第 6 章：AD 的规范性内容项

### 6.1 AD 标识与概述

官方模板的 must 项：

- 识别所描述的架构（给出架构名称或以其他适当方式）。
- 识别本 AD 所描述的 **entity of interest**（2011 版称 system of interest）。
- 提供由项目/组织确定的补充信息（版本、日期、作者、状态等）。

模板的 should 项：概述（optional）、**架构评估记录**（1.3.2）、关键决策的理由（1.3.3）。

**逆向场景补充**：必须记录依据的 commit / tag / 版本号，以及分析日期。行号会随时间漂移，没有 commit 锚点的 `file:line` 半年后无法复核。

### 6.2 识别利益相关者

must：识别并描述该架构的利益相关者。

must：**下列类别在适用于该 EoI 时必须被识别**——users、operators、acquirers、owners、suppliers、developers、builders、maintainers。（名称不必照用，应按项目实际命名。）

**逆向场景**：全部为【推断】。代码里只能看到角色痕迹。开源项目的常见落位：

| 类别 | 开源项目里通常是 |
|---|---|
| users | API/CLI/UI 的使用者，从端点与命令定义反推 |
| operators | 运维端点、配置项、监控指标的消费者 |
| acquirers / owners | 上游维护者组织、基金会、赞助方（从 LICENSE、GOVERNANCE、CODEOWNERS 反推） |
| suppliers | 依赖清单里的上游库与外部服务 |
| developers / builders | 贡献者（git shortlog）、CI 构建流程 |
| maintainers | CODEOWNERS、review 集中的人 |

不要因为「代码里看不到」就跳过 acquirers/owners——治理约束（许可证兼容性、CLA、发布节奏）是真实的架构约束，常常解释了某些设计选择。

### 6.3 识别干系人视角（stakeholder perspectives）

2022 版新增的条款。定义（3.18）："way of thinking about an entity of interest, especially as it relates to concerns"。

官方概念模型页说明其作用：**"introduces Stakeholder Perspectives as a means to group Concerns and therefore to organize Viewpoints framing those Concerns"** —— 即给 concern 分组，从而组织视角。

标准举例：Zachman 框架中 owner / designer / builder 三行即 perspectives；UAF 与 NAF 网格的行也是。

**逆向场景的实用做法**：不要生造哲学术语。按读者分组即可，例如「运维者视角」「集成者视角」「贡献者视角」，然后把 concerns 挂到这些组下，用来解释你为什么选了这几个视角。

### 6.4 识别关注点（concerns）

must：识别对该 EoI 架构而言基础性的关注点。

must（模板的必须考虑清单）：

- 该 EoI 的目的是什么？
- 架构对达成这些目的的适宜性如何？
- 构建与部署该 EoI 的可行性如何？
- 全生命周期中该 EoI 对其干系人的潜在风险与影响是什么？
- 该 EoI 将如何被维护与演进？

标准（5.2.3）还列举 concern 可涉及的面：需求、架构目标、期望、职责、设计约束、假设、依赖、质量属性、架构决策、风险。并明确**敌对性关注点（adversarial concerns）也应纳入考虑**——安全审计场景尤其相关。

**逆向场景的取证方法**：concern 的强证据是「代码里的显式投入」。

| 代码里的投入 | 指向的 concern |
|---|---|
| 布隆过滤器、索引、缓存 | 查询延迟 / 性能效率 |
| feature gate、条件编译 | 可裁剪性 / 商业版本切分 |
| 重试、熔断、故障转移 | 可用性 / 韧性 |
| 迁移脚本、版本协商 | 可演进性 / 兼容性 |
| 审计日志、权限检查点 | 安全 / 合规 |
| 压测目录、benchmark | 明确的性能目标 |

**否定结论同样有价值**：某方面代码里完全没有投入，说明它不是这个项目的 concern。写出来。

**优先级不可恢复**——不要伪造排序。

质量属性的分类可参照 ISO/IEC 25010:2023 的九特性（performance efficiency、compatibility、interaction capability、reliability、security、maintainability、flexibility、safety、functional suitability）。注意 2023 版相对 2011 版的变化：新增 safety；usability 改为 interaction capability；portability 改为 flexibility。

### 6.5 识别方面（aspects）

2022 版新增。定义（3.9）："part of an entity's character or nature"，举例：功能面、结构面、信息面。与 concern 是**多对多**关系。

官方概念模型页说明其作用：**"Aspects can be used to refine the traceability between Concerns and Views"**。

**逆向场景的实用做法**：当一个 concern 横跨多个视图时，用 aspect 把它切开，让追溯矩阵不至于变成「所有 concern 对所有 view 都打勾」。例如 concern「查询要快」可切成结构面（索引组织）、行为面（执行流水线）、信息面（数据编码），分别落到不同视图。

### 6.6 纳入架构视角（viewpoints）

must：为本 AD 使用的每个视角提供规约。

must：**"Viewpoints must be chosen for the AD such that each identified concern is framed by at least one viewpoint."** —— 可机械核对的完备性约束。

must：为每个所用视角提供**理由**（rationale）。

must：每个视角的规约须符合 42010 关于视角规约的条款（2022 版为 8.1）。视角规约本身的结构（官方 viewpoint 模板）：

1. 视角名称
2. 概述
3. 关注点与干系人（3.1 concerns，3.2 typical stakeholders，3.3 "anti-concerns"（optional））
4. model kinds（每个 model kind：名称、约定、可选的记法/元模型/模板、操作、对应规则）
5. 视图上的操作
6. 对应规则
7. 示例（optional）、注记（optional）
8. 来源（作者、历史、依据）

**逆向场景**：视角选择不是恢复出来的，是设计动作。必须写明为什么选这套目录——见 `viewpoint-catalogs.md`。

### 6.7 纳入架构视图（views）

must（每个视图）：

- 给出视图名称。
- 提供关于该视图的标识与补充信息。
- **指明管辖它的视角**（必须来自 6.6 中已规约的那些）。
- 记录视图与其视角约定之间的任何**偏离**（模板的 "Known Issues with View"）。

视图的定义（3.7）："information part comprising portion of an architecture description"。

注意 2022 版的基数变化：一个视角可以管辖**一个或多个**视图。

### 6.8 纳入视图构件（view components）

**2022 版最需要注意的术语变更。** Foreword 原文：

> "The term 'architecture view component' is introduced as a separable portion of one or more architecture views, **replacing 'architecture model'** in the 2011 edition. This change is to account for the fact that some parts of a view are model-based while others may not be."

> "Model-based view components are governed by model kinds and documented by legends. Non-model-based view components are documented by legends."

定义（3.19）："separable portion of one or more architecture views that is governed by the applicable model kind or legend"。注 1："a legend is an informal documentation of conventions"。

2011 版模板对 model 的 must 项（现应读作对 view component 的要求）：

- 提供一个或多个符合管辖视角的构件。
- **构件必须覆盖该视角框定的全部 concern，并从该视角覆盖整个系统。**
- 每个构件须包含版本标识。
- 每个构件须指明其管辖的 model kind 并遵守该 model kind 的约定。

**实践含义**：文字、表格、清单与图同为一等构件。不要为了「有图」把该用表格表达的内容硬画成图。一个构件可以出现在多个视图中（避免冗余）。

### 6.9 记录架构对应关系

三个子条款：6.9.1 AD 内一致性、6.9.2 对应关系、6.9.3 对应方法。

must：**记录 AD 中任何已知的不一致**（模板 5.1）。模板说明：「虽然一致的 AD 显然更可取，但出于时间、精力或信息不足，有时无法或不切实际地解决所有不一致」——即允许存在不一致，但不允许隐瞒。

should：AD 应包含对其构件与视图一致性的分析。

must：识别 AD 中每个对应关系及其参与的 AD 元素；识别管辖它的对应规则。

must：识别适用于本 AD 的每条对应规则；**对每条规则，记录该规则是否成立，否则记录全部已知违反**。

对应关系的定义（3.11）："identified or named relationship between two or more architecture description elements"，可表达等价、组合、精化、一致性、追溯、依赖、约束、满足、义务等关系。可用表格、链接或其他关联形式表达。

2022 版新增注记：**一份 AD 可以作为另一份 AD 中的 AD 元素**——这使多份 AD 之间的对应成为可能（例如上游 AD 与你的 fork 的 AD）。

**为什么这是逆向 AD 的重点**：静态分析能精确给出跨视图映射与规则违反，这是人手写不好、也维护不住的部分；而且它是唯一能固化成 CI 门禁的部分。

### 6.10 记录架构决策与理由

两个子条款：6.10.1 决策记录、6.10.2 理由记录。

**「决策」与「理由」的强制性不同，这是最容易搞错的一点。**

2011 版（有一手依据，两处独立佐证）：

- **记录决策本身 = 可选**。官方模板附录 A："It is not required by the Standard to capture architecture decisions. This section describes recommendations ('shoulds') for their recording."
- **关键决策的理由 = 强制**。同一份模板 §1.3.3 标为 must："An architecture description **shall** include rationale for each decision considered to be a key architecture decision（per ISO/IEC/IEEE 42010, **5.8.2**）。"
- 官方 FAQ 独立佐证：它列举 2011 版第 5 章的全部 "shalls"，最后一条即「providing rationale for key decisions made in the AD」。

两处不矛盾——它们约束的是不同对象：**你可以不做结构化的决策清单，但只要存在关键架构决策，就必须给出其理由。**

2022 版（仍无法确证，如实标注）：

- 6.10 拆成 6.10.1 决策记录与 6.10.2 理由记录两个子条款，正文措辞无法从公开材料获取（官方免费预览与 DIS 预览均止于 5.2.3）。
- **注意一个容易犯的推理错误**：不能因为 6.10 位于第 6 章就断定它是强制的。DIS 明文规定了动词约定——"Requirements of this document are marked by the use of the verb 'shall.' Recommendations are marked by the use of the verb 'should.'"，而一致性条款要求的是"meets the **requirements** listed in Clause 6"。**第 6 章同时包含 shall 与 should，只有 shall 项构成一致性要求。** 身处第 6 章是必要条件，不是充分条件。
- 合理推测（非结论）：鉴于 2011 版已把「关键决策的理由」定为 shall，2022 版的 6.10.2 大概率延续，而 6.10.1 可能仍偏 should。

**实践结论**：两版都要求关键决策必须有理由，所以无论如何都记录。引用条款时，2011 版的强制性可以确定表述；2022 版 6.10 的具体措辞须标注为未确证。

关键决策的选取判据（模板给出）：

- 影响关键干系人或众多干系人
- 对项目计划与管理至关重要
- 强制执行或实施代价高
- 对变更高度敏感或改动代价大
- 涉及复杂或非显然的推理
- 关系到架构显著需求（architecturally significant requirements）
- 需要投入大量时间或精力才能做出
- 导致资本支出或间接成本

决策的记录字段（模板的 should 清单）：

- 决策的唯一标识
- 决策陈述
- 与所涉 concerns 的对应/链接
- 决策的负责人
- 与受影响 AD 元素的对应/链接
- 与决策关联的理由
- 决策上的作用力与约束
- 影响决策的假设
- **考虑过的备选方案及其潜在后果**

这组字段与 ADR（Nygard 格式 / MADR）高度重合，用 ADR 承载 6.10 是自然的。

**逆向场景**：理由原理上不可恢复（architectural knowledge vaporization）。严格三分：有据（引出处）/ 推测（标置信度与推理链）/ 不可知（照实写「理由未知」）。「考虑过的备选方案」通常属缺口——除非在 PR 讨论里找到争论记录。

## 2022 版相对 2011 版的变更（Foreword 原文要点）

- **system of interest → entity of interest (EoI)**，以兼容 42020/42030 并适用于非系统类架构场景。
- **architecture framework → architecture description framework (ADF)**，以区别于 42030 的架构评估框架等其他架构框架。
- **AD element** 在第 3 章正式定义。
- **aspect 与 stakeholder perspective** 正式定义并描述（2011 版仅提及）。
- **correspondence**：新增注记——一份 AD 可作为另一份 AD 中的 AD 元素。
- **architecture model → architecture view component**。
- model-based 构件由 model kind 管辖并以 legend 记录约定；non-model-based 构件以 legend 记录。
- **model kind 成为新的一致性声明对象**。
- viewpoint 的概念更新为「一个视角管辖一个或多个视图」。
- model kind 的定义扩展为涵盖 UAF 这类 ADF 使用的模型类别。
- 图示从 UML 类图改为非正式 ER 记法。
- 新增 Annex E（架构与 AD 的生命周期）、Annex F（ADF 如何符合本标准的示例）。

## 42010 明确不规定什么（Scope 原文）

- 不规定创建、使用或管理 AD 的**过程、架构方法、模型、记法、技术或工具**。
- 不规定记录 AD 的**任何格式或媒介**。
- 不规定 EoI 本身或其环境的要求。
- Introduction 补充："This document does not explicitly address completeness or correctness regarding the inclusion of particular elements in an AD."

**推论**：视图目录、图的记法、文档格式都必须由你外挂选择，并说明理由。42010 给的是内容清单与一致性约束，不是模板。

## 完整自检清单

### 结构完备性

- [ ] 6.1 标识与概述：架构名、EoI、版本/commit、分析日期、本 AD 的目的
- [ ] 6.2 干系人：八类逐个考虑过，适用者已识别
- [ ] 6.3 干系人视角：concerns 已分组，且该分组解释了视角选择
- [ ] 6.4 关注点：五类必须考虑项逐个覆盖；含否定结论
- [ ] 6.4 concern↔stakeholder 追溯矩阵存在
- [ ] 6.5 方面：横跨多视图的 concern 已用 aspect 切分
- [ ] 6.6 每个视角有规约 + 选择理由
- [ ] 6.6 每个 concern 至少被一个视角框定（机械核对）
- [ ] 6.7 每个视图指明了管辖视角，并记录了偏离
- [ ] 6.8 构件覆盖了该视角框定的全部 concern 且覆盖整个系统
- [ ] 6.9 对应关系表存在，参与元素已识别
- [ ] 6.9 每条对应规则给出「成立」或「全部已知违反」
- [ ] 6.9 已知不一致已记录
- [ ] 6.10 关键决策按判据选取，字段完整

### 逆向场景专项

- [ ] 文档头一次性声明了档位、视角目录选择、6.2/6.3/6.10 的缺口
- [ ] 每条实质断言归入事实/推断/缺口之一
- [ ] 所有【事实】有 `file:line` + 依据 commit
- [ ] 所有【推断】有推理链与置信度
- [ ] 没有任何无出处的动机陈述
- [ ] 每个视图有动机段
- [ ] 每张图 5–20 个元素，删任一元素都会损失大意思
- [ ] as-built vs as-intended 漂移单列成节
- [ ] 契约缺口（实现违背干系人利益处）已显式记录
- [ ] 浅克隆时 git 类结论标注了历史截断日期
- [ ] 未覆盖区域已列出并说明原因
