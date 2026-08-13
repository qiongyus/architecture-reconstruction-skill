# architecture-reconstruction

从源代码**重建既有系统的架构描述**（Architecture Description, AD），产出按 ISO/IEC/IEEE 42010:2022 第 6 章的规范性内容项组织，每条断言附代码证据与置信度，拿不到的内容显式声明为缺口而不是编造。

这是一个中文个人 skill。给 agent 读的正文在 `SKILL.md`；本 README 面向浏览仓库的人，介绍定位、内容与安装方式。

## 定位

代码里没有「架构」这个现成的东西，只有**证据**。重建出来的是 **as-built（实际建成）** 的架构描述，它与 as-intended（当初设想）几乎总有差异——这个差异不是噪声，是本次工作最有价值的产出之一（Perry & Wolf 的侵蚀 erosion 与漂移 drift）。最危险的失败模式是**编造动机**：rationale 原理上无法从代码恢复（架构知识蒸发），一份处处「之所以这样设计是为了……」却没有出处的重建文档，比留白有害得多。本 skill 全部纪律的出发点，是让每条断言的认知地位可见：

- **三级证据纪律**：【事实】/【推断】/【缺口】——`file:line` 是事实的唯一凭据（同时记 commit），推断必须写推理链与置信度，缺口是一等产出而不是失败
- **结构服务于发现**：42010 十个条目是完备性检查表，不是价值排序；从「对外产生结果的路径」逐条扫静默正确性问题、危险默认值、无告警的错误路径，每条发现写明「谁会因此做出错误判断」，且**最危险的发现必须出现在前两屏**
- **6.9 对应关系重点做**：跨视图映射与可判定规则是逆向 AD 相对正向 AD 的独有强项，并立刻固化成可执行检查（ArchUnit / dependency-cruiser / import-linter）接入 CI，防止 AD 从写完那天就开始腐化
- **决策考古四档**：有据·决策级 / 有据·收益级 / 推测 / 不可知——收益声明不当理由用，变更描述不当动机用，fork 继承的起点条件不当决策记
- **机械校验**：`scripts/check_coverage.py` 核查官方模板的 must 项「每个 concern 至少被一个 viewpoint 框定」

**产出取向是分析材料，不是合规文档。** 条款完备性是下限，价值在尖锐发现。

与相邻方法的分工：

| 要做的事 | 用什么 |
|---|---|
| 重建用例模型与场景规格（行为契约 / 黑盒） | `usecase-reconstruction` |
| 重建结构化需求、做对等重写的 parity 分析 | `requirements-reconstruction` |
| 为尚不存在的新系统做正向架构设计 | 正向架构设计，不是本 skill |
| **重建架构描述（AD，结构 / 白盒）** | **本 skill** |

三个重建型 skill 相互独立，只共享证据层，不共享代码；产出共用目标仓库 `docs/reconstruction/` 作为落盘约定根，本 skill 占 `architecture/` 子目录。

## 依据地基

| 层 | 依据 |
|---|---|
| 内容项清单（十条） | 42010:2022 第 6 章；第 4 章规定声明一致性即须满足第 6 章，tailoring 既不要求也不允许 |
| 逐条 must/should | 42010 官方 AD 模板与官方 FAQ（如 concern↔stakeholder 追溯矩阵、逐条对应规则「成立或列出全部违反」均为 must） |
| 默认视角目录 | Rozanski & Woods 7 视角 + perspective 机制——42010 刻意不规定视图目录，必须外挂；另备 4+1 / C4 / SEI Views & Beyond 及取舍（`references/viewpoint-catalogs.md`） |
| 侵蚀 / 漂移 / 知识蒸发 | Perry & Wolf；architectural knowledge vaporization 文献 |

一致性声明按诚实形态处理：6.2 干系人 / 6.3 视角 / 6.10 决策理由**结构性拿不到**，重建 AD 不可能「自然合规」——以「假说 + 显式缺口声明」形态在文档头一次性声明。2022 版 6.10 的正文措辞无法从公开材料确证，引用条款时照实标注为未确证，不因位于第 6 章就断言强制。

## 工作流一览

| Step | 内容 |
|---|---|
| 0 | 定这份 AD 的目的（贡献代码 / fork 维护 / 集成评估 / 安全审计 / 重构）——目的不同该恢复的视图完全不同，**唯一值得打断用户的问题** |
| 1 | 证据清点与规模评估（`scripts/inventory_evidence.sh`，8 类证据源，报告哪些**不存在**；检测浅克隆防 git 证据说谎） |
| 2 | 反推干系人与关注点（6.2–6.5），全部标推断；concern 的强证据是代码里的显式投入，优先级不可恢复不伪造 |
| 3 | 选定视角目录并核对完备性（6.6，`scripts/check_coverage.py`）；视图数量由 concern 驱动，不硬凑 |
| 4 | 建视图与视图构件（6.7/6.8）：构件 + 动机段 + 证据 + Known Issues；每图 5–20 个承载大意思的元素 |
| 5 | 对应关系与规则（6.9）：跨视图映射逐行附证据，规则固化成 CI 可执行检查 |
| 6 | 决策考古（6.10）：四档证据地位，备选方案与代价才算决策级理由 |
| 7 | 缺口、不一致与漂移：as-built vs as-intended 逐条列出，附两边证据 |
| 8 | 自检（13 项清单） |

产出按规模分三档：速览（单文件 `ARCHITECTURE.md`）／标准（`AD-00` 至 `AD-99` 系列，每视图一文件）／完整（标准档 + 机器可读证据库 + 一致性检查规则）。内容项不减，只改承载。落盘目录统一为 `docs/reconstruction/architecture/`（子项目重建时插一级 `<target-slug>`）。

## 内容

```
SKILL.md                                  正文：本质、证据纪律、尖锐发现、内容项、工作流、自检
references/
  ad-content-items.md                     42010 第 6 章逐条要求、官方模板 must/should、完整自检清单
  viewpoint-catalogs.md                   R&W / 4+1 / C4 / Views&Beyond 四套视角目录及选择指引
  evidence-discipline.md                  证据源清单与陷阱、置信度判据、标注约定
  tooling.md                              按语言的依赖分析与架构一致性检查工具
scripts/
  inventory_evidence.sh                   Step 1 证据清点：8 类证据源存在性与规模、浅克隆检测、规模分级
  check_coverage.py                       Step 3 完备性核对：每个 concern 至少被一个 viewpoint 框定
assets/ad-skeleton/
  ARCHITECTURE.md                         速览档单文件产出
  AD-00-overview.md                       标准档：范围目的、档位与缺口一次性声明、最危险的发现
  AD-01-stakeholders-concerns.md          标准档：干系人假说与 concern↔stakeholder 追溯矩阵
  AD-02-viewpoints.md                     标准档：视角选择及理由
  AD-1x-view-TEMPLATE.md                  标准档：单视图模板（构件/动机/证据/Known Issues）
  AD-90-correspondences.md                标准档：对应关系与规则、一致性分析
  AD-91-decisions.md                      标准档：决策考古（四档证据地位）
  AD-99-gaps.md                           标准档：缺口、不一致与漂移
  ad-manifest.yaml                        机器可读附属品，check_coverage.py 的校验对象
```

## 安装

```bash
rsync -a --exclude .git <本仓库>/ ~/.agents/skills/architecture-reconstruction/
ln -s ../../.agents/skills/architecture-reconstruction ~/.claude/skills/architecture-reconstruction
```

依赖：`bash` + `grep`/`find`（清点脚本）、`python3`（覆盖核对脚本，仅用标准库）。
