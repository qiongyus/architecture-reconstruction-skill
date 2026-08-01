# 取证与一致性检查工具

> **使用前请自行确认工具当前的维护状态与安装方式。** 本文按语言归类可用手段，不保证每个工具在你读到时仍活跃维护——先 `--version` 跑通再依赖它。

## 原则：先用语言自带的，再上第三方

语言原生工具链的依赖信息最可靠、无需安装、不会与项目构建冲突。只有在需要可视化或规则强制时才引入第三方工具。

## 依赖分析（生成模块级依赖图）

| 语言 | 原生手段 | 第三方 |
|---|---|---|
| Go | `go list -deps`、`go mod graph`、`go list -json ./...` | `godepgraph`、`go-callvis` |
| Rust | `cargo metadata --format-version 1`、`cargo tree` | `cargo-modules`、`cargo-depgraph` |
| JS/TS | `tsc --traceResolution`、workspace 定义 | `dependency-cruiser`、`madge` |
| Python | `importlib` / AST 遍历 | `pydeps`、`import-linter`、`grimp` |
| Java/Kotlin | `jdeps`（JDK 自带）、`gradle dependencies` | `jQAssistant`、`Structure101`、`Sonargraph` |
| C/C++ | `include-what-you-use`、编译数据库 `compile_commands.json` | `cinclude2dot` |
| 通用 | — | `Structurizr`（图即代码）、`Understand` |

### 最省事的起点

多数情况下不需要专门工具。用 grep 统计跨模块引用即可得到足够精确的依赖矩阵：

```bash
# Go：统计各 app 子包对 lib 的引用分布
grep -rho 'yourmod/lib/[a-z0-9_/]*' app/ | sort | uniq -c | sort -rn

# Rust：统计 crate 间引用
grep -rho 'use crate::[a-z0-9_]*' src/ | sort | uniq -c | sort -rn

# TS：统计跨目录 import
grep -rhoE "from '[.@][^']*'" src/ | sort | uniq -c | sort -rn
```

**要点**：依赖分析的价值不在工具精度，而在**聚类抽象**——把几百个包归并成 5–20 个构建块。这一步是人的判断，工具只提供原料。

## 架构一致性检查（把对应规则固化进 CI）

这是 42010 的 6.9 能变成防腐层的关键。发现值得保持的规则后立刻固化：

| 语言 | 工具 | 规则形态 |
|---|---|---|
| Java/Kotlin | **ArchUnit** | 单元测试形式的架构断言 |
| JS/TS | **dependency-cruiser** | `.dependency-cruiser.js` 里的 forbidden 规则 |
| Python | **import-linter** | `.importlinter` 的 contracts（layers、forbidden、independence） |
| Go | `go-arch-lint`、或自写 `go list` + 断言测试 | 自定义 |
| Rust | 自写测试解析 `cargo metadata`；或 `cargo-deny`（偏许可证/安全） | 自定义 |
| 通用 | `jQAssistant`、`Sonargraph`、`Lattix` | 图查询 / DSM |

**最低成本的做法**：不装任何工具，写一个断言测试遍历依赖并检查禁止边。十几行代码，跟着仓库走，不引入新依赖。

```bash
# 例：Go 中断言领域层不依赖 HTTP
! grep -rq 'net/http' lib/domain/ || { echo "违规：domain 层引用了 net/http"; exit 1; }
```

## 运行期取证（静态分析的盲区）

静态分析看不到反射、依赖注入、插件加载、异步分发。这些必须动态验证：

| 手段 | 用途 |
|---|---|
| 调试器断点 / 单步 | 确认关键路径的实际调用链 |
| 结构化日志 + trace id | 跨组件的请求流转 |
| OpenTelemetry / 分布式追踪 | 服务间调用拓扑 |
| `strace` / `lsof` / `ss` | 实际打开的文件、监听的端口、外连目标 |
| `pprof` / 火焰图 | 热路径，验证性能相关的结构推断 |
| 容器编排的实际状态 | 部署视图的验证 |

**最省事的运行期证据**：跑项目自己的集成测试并开启详细日志，日志里的调用序列就是免费的行为视图素材。

## git 证据

```bash
# 检查是否浅克隆（决定 git 证据是否可用）
[ -f .git/shallow ] && echo "浅克隆：历史截断于 $(git log --reverse --format=%ad --date=short | head -1)"

# 改动热点（架构敏感点）
git log --format=format: --name-only --since='2 years ago' \
  | grep -v '^$' | sort | uniq -c | sort -rn | head -30

# 共变分析（隐性耦合）：找出常一起改动的文件对
git log --format='%H' --name-only | awk '
  /^[0-9a-f]{40}$/ {c=$0; next}
  NF {f[c]=f[c]" "$0}
  END {for (k in f) print f[k]}' \
  | tr ' ' '\n' | sort | uniq -c | sort -rn | head

# 贡献集中度（谁是事实上的维护者）
git shortlog -sn --since='1 year ago' | head -15
```

排除大规模格式化提交后再统计热点，否则一次 gofmt 会把所有文件推到榜首。

## 图的表达

优先 **diagrams-as-code**，与代码同仓库、可 diff、可 CI 校验：

- **Mermaid**：GitHub/GitLab 原生渲染，无需构建。`flowchart`、`classDiagram`、`sequenceDiagram`、`stateDiagram-v2` 覆盖多数需要。
- **Structurizr DSL**：C4 的原生表达，一份模型生成多视图，与 42010 的「一个构件出现在多个视图」契合。
- **PlantUML**：表达力最强，需要渲染环境。
- **D2**、**Graphviz DOT**：布局质量好，适合自动生成的依赖图。

**不要手绘导出图片**——它无法 diff，一旦代码变化就悄悄过期，正是 AD 腐化的主要途径。

## 生成代码与 vendor 的识别

分析前必须排除，否则规模统计和依赖图都会失真：

```bash
# 常见生成物
find . -name '*.pb.go' -o -name '*_generated.go' -o -name '*.qtpl.go' \
       -o -name '*.g.dart' -o -name '*_pb2.py' -o -name '*.generated.ts'

# 常见 vendor / 构建产物目录
find . -maxdepth 3 -type d \( -name vendor -o -name node_modules -o -name target \
       -o -name dist -o -name build -o -name .venv \)
```

但**生成链本身要记录**——「protobuf 手写解析而非 protoc」「前端产物 checked-in 而非构建时生成」这类事实属于开发视图的重要内容。

## 条件编译与 feature flag

只看默认配置会漏掉整块结构：

```bash
grep -rho '#\[cfg(feature = "[a-z_]*")\]' src/ | sort -u        # Rust
grep -rho '//go:build [a-z_ ]*' . | sort -u                      # Go build tags
grep -rho 'process.env.[A-Z_]*' src/ | sort -u                   # Node
```

枚举出各 feature 组合，说明它们如何改变结构（例如开源版与企业版的切分点）。这常常是重要的架构决策证据。
