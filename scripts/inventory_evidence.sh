#!/usr/bin/env bash
# 证据源清点：对一个仓库根目录，报告架构重建所需各类证据的存在情况与陷阱。
#
# 用法: bash inventory_evidence.sh <repo-root>
#
# 设计要点：重点是告出「哪些证据源不存在」——据此判断哪些结论根本没有依据可给，
# 以及检测会让证据说谎的陷阱（浅克隆、squash 导入、生成代码、vendor）。

set -uo pipefail
ROOT="${1:-.}"
cd "$ROOT" 2>/dev/null || { echo "无法进入目录: $ROOT" >&2; exit 1; }

PRUNE_NAMES='node_modules target .git vendor dist build .venv __pycache__ .next .tox venv'
PRUNE=""
for n in $PRUNE_NAMES; do PRUNE="$PRUNE -name $n -o"; done
PRUNE="${PRUNE% -o}"

SECT_HIT=0

section() { SECT_HIT=0; printf '\n\033[1m%s\033[0m\n' "$1"; }

hit() { # hit <label> <maxdepth> <find-expr...>
  local label="$1"; shift
  local depth="$1"; shift
  local out
  out=$(find . -maxdepth "$depth" \( $PRUNE \) -prune -o \( "$@" \) -print 2>/dev/null \
        | head -8 | sed 's|^\./||' | paste -sd' ' -)
  if [ -n "$out" ]; then
    printf '  \033[32m✓\033[0m %-16s %s\n' "$label" "$out"
    SECT_HIT=1
  fi
}

# fallback <label> <msg>：仅当本节一无所获时才报缺失
fallback() {
  [ "$SECT_HIT" = 0 ] && printf '  \033[31m✗\033[0m %-16s %s\n' "$1" "$2"
  return 0
}

echo "════════════════════════════════════════════════════════════"
echo " 证据源清点: $(pwd)"
echo "════════════════════════════════════════════════════════════"

section "[1] 构建与依赖清单 —— 模块边界最硬的证据"
hit "Go"          2 -name go.mod
hit "Rust"        3 -name Cargo.toml
hit "Node"        2 -name package.json -o -name pnpm-workspace.yaml -o -name turbo.json -o -name lerna.json
hit "Python"      2 -name pyproject.toml -o -name setup.py -o -name setup.cfg -o -name requirements.txt
hit "JVM"         2 -name pom.xml -o -name build.gradle -o -name build.gradle.kts -o -name settings.gradle
hit "Ruby/PHP"    2 -name Gemfile -o -name composer.json
hit "C/C++"       2 -name CMakeLists.txt -o -name meson.build -o -name compile_commands.json
hit "构建编排"     2 -name Makefile -o -name Makefile.toml -o -name justfile -o -name Taskfile.yml
fallback "构建清单" "无 —— 模块边界只能靠目录结构猜（置信度上限：低）"

section "[2] 入口点 —— 圈定全部功能面"
hit "main"        3 -name 'main.*' -o -name 'index.ts' -o -name 'index.js' -o -name '__main__.py'
hit "cmd/app 目录" 2 -name cmd -type d -o -name app -type d -o -name apps -type d -o -name bin -type d
fallback "入口点" "未自动识别 —— 需人工定位（库项目可能本就没有）"

section "[3] 部署与运行时拓扑"
hit "容器"        3 -name 'Dockerfile*' -o -name 'docker-compose*' -o -name 'Containerfile*' -o -name '*.dockerfile'
hit "k8s/helm"    4 -name Chart.yaml -o -name kustomization.yaml -o -name 'statefulset*.y*ml' -o -name 'deployment*.y*ml'
hit "部署目录"     3 -name deployment -type d -o -name deploy -type d -o -name charts -type d -o -name manifests -type d
hit "CI"          3 -path '*.github/workflows*' -name '*.y*ml' -o -name '.gitlab-ci.yml' -o -name 'Jenkinsfile' -o -path '*.circleci*' -name 'config.yml'
hit "服务单元"     3 -name '*.service' -o -name '*.systemd'
fallback "部署证据" "无 —— 部署视图无依据，应声明为缺口"

section "[4] 数据模型与持久化"
hit "迁移"        4 -name migrations -type d -o -name migration -type d -o -name 'migrate' -type d
hit "schema"      3 -name 'schema*.sql' -o -name '*.sql' -o -name 'schema' -type d
hit "IDL"         4 -name '*.proto' -o -name '*.thrift' -o -name '*.avsc' -o -name '*.graphql' -o -name 'openapi*.y*ml' -o -name 'swagger*.json'
fallback "数据模型" "无 —— 信息视图需从结构体/序列化代码反推"

section "[5] 文字考古 —— 唯一能恢复 rationale 的来源"
hit "README"      1 -iname 'readme*'
hit "docs 目录"    2 -name docs -type d -o -name doc -type d -o -name website -type d
hit "架构文档"     3 -iname 'architecture*' -o -iname 'design*.md' -o -iname '*DESIGN*.md' -o -iname 'internals*.md'
hit "ADR/RFC"     4 -name adr -type d -o -name rfcs -type d -o -name rfc -type d -o -iname '*adr*.md' -o -iname 'proposals' -type d
hit "治理"        2 -iname 'contributing*' -o -iname 'governance*' -o -iname 'CODEOWNERS' -o -iname 'MAINTAINERS*' -o -iname 'CLAUDE.md' -o -iname 'AGENTS.md'
hit "变更记录"     2 -iname 'changelog*' -o -iname 'CHANGES*' -o -iname 'NEWS*'
fallback "文字材料" "无 —— 6.10 决策理由全部为缺口，必须显式声明"

section "[6] 测试 —— 前人写好的场景走查脚本"
hit "集成/e2e"    3 -name 'e2e' -type d -o -name 'integration*' -type d -o -name 'apptest' -type d -o -name 'tests' -type d -o -name 'test' -type d
hit "压测/基准"    3 -name 'bench*' -type d -o -name '*_bench*' -o -name 'benchmark*' -type d -o -name 'load*test*' -type d
fallback "测试" "无 —— 行为视图缺少可执行依据"

section "[7] 配置面 —— 外部依赖与运行时开关"
hit "配置"        2 -iname 'config*.y*ml' -o -iname 'config*.toml' -o -iname '*.env.example' -o -name 'config' -type d -o -iname '*.conf'
hit "flag 定义"    3 -name 'flags*.go' -o -name 'cli*.rs' -o -name 'args*.py' -o -name 'settings*.py'
fallback "配置面" "未自动识别 —— 需从 flag/env 读取代码反推外部依赖"

section "[8] 规模评估"
SRC=$(find . \( $PRUNE \) -prune -o -type f \( \
  -name '*.go' -o -name '*.rs' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \
  -o -name '*.py' -o -name '*.java' -o -name '*.kt' -o -name '*.rb' -o -name '*.php' \
  -o -name '*.cpp' -o -name '*.cc' -o -name '*.c' -o -name '*.h' -o -name '*.hpp' \
  -o -name '*.cs' -o -name '*.swift' -o -name '*.scala' -o -name '*.vue' -o -name '*.svelte' \
  \) -print 2>/dev/null | wc -l | tr -d ' ')
printf '  源文件数（已排除 vendor/生成目录）: %s\n' "$SRC"

if   [ "$SRC" -lt 150 ];  then TIER="速览档（单文件 ARCHITECTURE.md）"
elif [ "$SRC" -lt 1500 ]; then TIER="标准档（分文件 AD-xx 系列）"
else                            TIER="完整档（标准档 + 机器可读证据库）"
fi
printf '  \033[1m建议产出档位: %s\033[0m\n' "$TIER"

section "[9] 陷阱检测 —— 会让证据说谎的东西"

if [ -d .git ]; then
  COMMITS=$(git rev-list --count HEAD 2>/dev/null || echo 0)
  if [ -f .git/shallow ]; then
    CUT=$(git log --reverse --format=%ad --date=short 2>/dev/null | head -1)
    printf '  \033[33m⚠ 浅克隆\033[0m         历史截断于 %s（共 %s commit）\n' "$CUT" "$COMMITS"
    printf '                     → git 类结论必须标注此截断日期\n'
    printf '                     → 可用 git fetch --deepen=500 增量加深\n'
  elif [ "$COMMITS" -le 2 ]; then
    printf '  \033[33m⚠ 无有效历史\033[0m     仅 %s 个 commit（squash 导入或镜像快照）\n' "$COMMITS"
    printf '                     → 热点与共变分析不可用，声明该证据源缺失\n'
  else
    FIRST=$(git log --reverse --format=%ad --date=short 2>/dev/null | head -1)
    AUTHORS=$(git shortlog -sn HEAD 2>/dev/null | wc -l | tr -d ' ')
    printf '  \033[32m✓ git 历史完整\033[0m   %s commit, %s 贡献者, 起于 %s\n' "$COMMITS" "$AUTHORS" "$FIRST"
  fi
else
  printf '  \033[31m✗ 无 git\033[0m          热点与共变分析不可用\n'
fi

GEN=$(find . \( $PRUNE \) -prune -o -type f \( -name '*.pb.go' -o -name '*_generated.go' \
      -o -name '*.qtpl.go' -o -name '*_pb2.py' -o -name '*.generated.*' -o -name '*.g.dart' \
      -o -name '*_gen.go' \) -print 2>/dev/null | wc -l | tr -d ' ')
[ "$GEN" -gt 0 ] && printf '  \033[33m⚠ 生成代码\033[0m       %s 个文件 → 分析时排除，但记录生成链\n' "$GEN"

for d in vendor node_modules target; do
  [ -d "$d" ] && printf '  \033[33m⚠ %s/\033[0m 存在      → 已从统计排除；依赖关系仍需记录\n' "$d"
done

FEAT=$(grep -rho '#\[cfg(feature = "[a-z_0-9]*")\]' --include='*.rs' . 2>/dev/null | sort -u | wc -l | tr -d ' ')
[ "$FEAT" -gt 0 ] && printf '  \033[33m⚠ Rust feature\033[0m   %s 种条件编译 → 结构随 feature 变化，需枚举\n' "$FEAT"
TAGS=$(grep -rho '//go:build [a-z_0-9 ]*' --include='*.go' . 2>/dev/null | sort -u | wc -l | tr -d ' ')
[ "$TAGS" -gt 0 ] && printf '  \033[33m⚠ Go build tag\033[0m   %s 种 → 同上\n' "$TAGS"

echo
echo "────────────────────────────────────────────────────────────"
echo " 下一步：把标 ✗ 的证据源写进 AD 的缺口声明；"
echo " 标 ⚠ 的陷阱在相关结论处逐条标注。"
echo "────────────────────────────────────────────────────────────"
