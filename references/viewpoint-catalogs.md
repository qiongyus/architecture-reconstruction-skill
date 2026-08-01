# 视角目录的选择

42010 刻意不规定视图目录（Scope 明确不规定 models、notations、techniques），必须外挂一套并说明选择理由（这是官方模板的 must 项）。本文给出四套候选与选择指引。

## 默认推荐：Rozanski & Woods 的视角 + 透视

出自 *Software Systems Architecture: Working with Stakeholders Using Viewpoints and Perspectives*（Rozanski & Woods，第 2 版 2012）。这套是公认最贴近 42010 的实例化——书中架构概念直接建立在 42010 之上。

### 7 个视角（viewpoints）

| 视角 | 回答什么 | 从代码取证的主要来源 |
|---|---|---|
| **Context** | 系统边界、外部实体与交互 | 入口点、对外端点清单、依赖的外部服务、配置项 |
| **Functional** | 运行期功能元素、职责与接口 | 模块/包结构、公开接口、路由表 |
| **Information** | 数据的存储、流动、所有权与生命周期 | schema、迁移脚本、序列化格式、保留策略 |
| **Concurrency** | 并发结构、进程/线程、协调与同步 | 线程/协程创建点、锁、队列、通道 |
| **Development** | 代码如何组织、构建、测试 | 构建文件、workspace 定义、CI 配置、测试布局 |
| **Deployment** | 运行时物理环境、节点、依赖的第三方 | Dockerfile、compose、k8s/helm、部署文档 |
| **Operational** | 如何安装、运维、监控、升级、排障 | 指标端点、日志、运维端点、备份/迁移工具、告警规则 |

### 横切透视（perspectives）

透视不是视图，是**跨视图施加的质量关切**：Security、Performance & Scalability、Availability & Resilience、Evolution、Location、Development Resource、Internationalization 等。

**这正好对应 42010:2022 的 aspect 机制**——透视让「安全」「性能」这类横切关注点有正式位置，不必硬塞进某个视图，也避免了追溯矩阵变成全打勾。

### 为什么默认选它

- 7 视角对 42010 那五类必须考虑的 concern 覆盖最全。
- **有 Operational 视角**——这是 4+1 和 C4 都缺的，而对基础设施类、服务类开源项目（可观测性、retention、集群运维、升级路径）恰好是重点。
- 透视机制与 2022 版的 aspect 概念天然对齐。

## 备选一：Kruchten 4+1

出自 Kruchten 1995 年 IEEE Software 论文。五个视图：**Logical**（功能与领域结构）、**Process**（并发与运行期）、**Development**（代码组织）、**Physical**（部署到硬件），**+ Scenarios**（用例，贯穿并验证其余四个）。

**适用**：读者熟悉这套词汇；项目本身用 4+1 描述过自己。

**短板**（选它前须知）：

- 早于 42010，**没有 correspondence 概念**——而这恰是逆向 AD 的强项，用 4+1 会让 6.9 无处安放（须自行补一节）。
- **没有 Operational 视角**，运维与可观测性只能挤进 Physical，对基础设施项目是硬伤。
- 没有独立的 Information 视图，数据模型只能塞进 Logical。

## 备选二：C4

Simon Brown 提出的四个缩放层级：**System Context → Container → Component → Code**（最后一层通常可选）。

**适用**：工程团队沟通、快速上手、给贡献者画一张能看懂的图。前两层性价比极高。

**短板**：**C4 作者本人明确表示 C4 不是完整的架构描述**——它只解决静态结构的缩放层级，不覆盖并发、信息、运维。若用户要 C4，正确做法是**用 C4 承载 Functional/Development 视角的构件，其余条款另行补齐**，而不是把 C4 当作整份 AD。

## 备选三：SEI Views and Beyond

出自 *Documenting Software Architectures: Views and Beyond*（Clements 等）。三大视图类别：

- **Module views**：实现单元及其关系（分解、使用、泛化、分层）。
- **Component-and-connector (C&C) views**：运行期元素及其交互路径。
- **Allocation views**：软件元素到环境的映射（部署、实现、工作分配）。

**"Beyond views" 部分**是其精华，要求文档包含视图之外的内容：文档路线图、视图模板说明、系统概览、**视图间映射**、理由（rationale）、索引与术语表。

**注意**：视图间映射与 rationale 正对应 42010 的 6.9 与 6.10。V&B 的 module/C&C/allocation 三分与 42010 概念契合度高，是严谨场景的好选择；代价是术语对非 SEI 背景读者门槛较高。

## 选择指引

| 情形 | 选择 |
|---|---|
| 默认，尤其基础设施/服务类项目 | R&W 7 视角 + 透视 |
| 用户指定了某套 | 用用户的，但补齐 42010 缺失条款 |
| 只要快速上手、给贡献者看 | C4 前两层承载结构，速览档产出 |
| 需要严谨的模块/运行期/分配三分 | Views and Beyond |
| 项目自己已用某套描述过 | 沿用它，降低读者认知成本；差异处补充 |

三条通用纪律：

1. **无论用哪套，都要在 AD 中写明为什么选它**（官方模板 must）。
2. **视图数量由 concern 驱动，不由目录条目数驱动。** 没有并发的项目不需要 Concurrency 视图——写一句「本系统为单进程单线程模型，该视角不适用（证据：…）」比硬编一个空视图强得多。
3. **跨目录混用要声明。** 例如「结构用 C4 的 Container/Component 层级表达，运维与信息另设视角」——说清楚，读者才不会困惑于记法不统一。

## 常被遗漏的两项

多数模板（尤其 4+1 与 C4）**普遍不覆盖** 42010 的这两项，用它们时必须自行补：

- **6.9 对应关系与规则**（含已知不一致）
- **6.10 决策与理由**

Views and Beyond 是例外——它的 "beyond views" 明确包含视图间映射与 rationale。
