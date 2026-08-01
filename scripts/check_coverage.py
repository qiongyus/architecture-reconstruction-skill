#!/usr/bin/env python3
"""核对 AD 的 42010 完备性约束，并生成追溯矩阵。

用法:
    python3 check_coverage.py <ad-dir-or-manifest> [--emit-matrix]

读取 <ad-dir>/ad-manifest.yaml（或 .json），核对下列可机械判定的约束：

  1. 每个 concern 至少被一个 viewpoint 框定        （42010 官方模板 must）
  2. 每个 view 的管辖 viewpoint 已被规约            （6.7）
  3. 每个已声明的 viewpoint 至少被一个 view 使用    （否则不该声明）
  4. 每个 concern 至少关联一个 stakeholder          （6.4 追溯矩阵）
  5. 每个 stakeholder 至少关联一个 concern
  6. 八类必须考虑的 stakeholder 已覆盖或显式声明不适用
  7. 五类必须考虑的 concern 已覆盖或显式声明不适用
  8. 每条 concern/stakeholder 标注了置信度（逆向场景纪律）

--emit-matrix 额外输出 concern↔stakeholder 与 concern↔view 两张 markdown 矩阵，
可直接贴进 AD——不要手工维护矩阵，它必然与正文脱节。

违规时退出码非零，可直接用于 CI。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 42010 官方 AD 模板规定「适用时必须识别」的干系人类别
MANDATORY_STAKEHOLDER_CATEGORIES = [
    "users", "operators", "acquirers", "owners",
    "suppliers", "developers", "builders", "maintainers",
]

# 官方模板规定「必须考虑」的关注点类别
MANDATORY_CONCERN_CATEGORIES = {
    "purpose": "该实体的目的是什么",
    "suitability": "架构对达成这些目的的适宜性",
    "feasibility": "构建与部署的可行性",
    "risks": "全生命周期中对干系人的风险与影响",
    "evolution": "如何被维护与演进",
}

VALID_CONFIDENCE = {"fact", "high", "medium", "low", "gap"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    def emit(self) -> int:
        for m in self.notes:
            print(f"  \033[36m·\033[0m {m}")
        for m in self.warnings:
            print(f"  \033[33m⚠\033[0m {m}")
        for m in self.errors:
            print(f"  \033[31m✗\033[0m {m}")
        print()
        if self.errors:
            print(f"\033[31m不合规：{len(self.errors)} 项违规，{len(self.warnings)} 项警告\033[0m")
            return 1
        if self.warnings:
            print(f"\033[33m基本合规：0 项违规，{len(self.warnings)} 项警告\033[0m")
            return 0
        print("\033[32m合规：全部约束通过\033[0m")
        return 0


def load_manifest(target: Path) -> dict:
    if target.is_dir():
        candidates = [target / "ad-manifest.yaml", target / "ad-manifest.yml",
                      target / "ad-manifest.json"]
        found = [c for c in candidates if c.exists()]
        if not found:
            sys.exit(f"在 {target} 下未找到 ad-manifest.yaml / .json\n"
                     f"可从 assets/ad-skeleton/ad-manifest.yaml 复制一份作为起点。")
        path = found[0]
    else:
        path = target
        if not path.exists():
            sys.exit(f"文件不存在: {path}")

    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        sys.exit("读取 YAML 需要 pyyaml（pip install pyyaml），"
                 "或把 manifest 改写为 ad-manifest.json。")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        sys.exit(f"{path} 顶层应是映射（mapping），实际是 {type(data).__name__}")
    return data


def ids(items: list[dict], kind: str, rep: Report) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            rep.error(f"{kind}[{i}] 应是映射，实际是 {type(item).__name__}")
            continue
        _id = item.get("id")
        if not _id:
            rep.error(f"{kind}[{i}] 缺少 id 字段")
            continue
        if _id in out:
            rep.error(f"{kind} id 重复: {_id}")
        out[_id] = item
    return out


def check(data: dict, rep: Report) -> dict:
    stakeholders = ids(data.get("stakeholders") or [], "stakeholders", rep)
    concerns = ids(data.get("concerns") or [], "concerns", rep)
    viewpoints = ids(data.get("viewpoints") or [], "viewpoints", rep)
    views = ids(data.get("views") or [], "views", rep)
    aspects = ids(data.get("aspects") or [], "aspects", rep)
    perspectives = ids(data.get("perspectives") or [], "perspectives", rep)

    if not concerns:
        rep.error("未声明任何 concern —— 42010 6.4 是必需项")
    if not viewpoints:
        rep.error("未声明任何 viewpoint —— 42010 6.6 是必需项")
    if not views:
        rep.error("未声明任何 view —— 42010 6.7 是必需项")

    rep.note(f"规模：{len(stakeholders)} 干系人 / {len(concerns)} 关注点 / "
             f"{len(perspectives)} 干系人视角 / {len(aspects)} 方面 / "
             f"{len(viewpoints)} 视角 / {len(views)} 视图")

    # 约束 1：每个 concern 至少被一个 viewpoint 框定
    framed: dict[str, list[str]] = {c: [] for c in concerns}
    for vp_id, vp in viewpoints.items():
        for c in vp.get("frames") or []:
            if c not in concerns:
                rep.error(f"viewpoint '{vp_id}' 框定了未声明的 concern '{c}'")
            else:
                framed[c].append(vp_id)
        if not vp.get("rationale"):
            rep.error(f"viewpoint '{vp_id}' 缺少 rationale —— "
                      f"官方模板要求为每个所用视角提供理由")
    for c, vps in framed.items():
        if not vps:
            rep.error(f"concern '{c}' 未被任何 viewpoint 框定 —— "
                      f"违反「每个 concern 至少被一个 viewpoint 框定」")

    # 约束 2 / 3：view↔viewpoint 双向完整
    used_vps: set[str] = set()
    for v_id, v in views.items():
        vp = v.get("viewpoint")
        if not vp:
            rep.error(f"view '{v_id}' 未指明管辖 viewpoint（6.7 必需）")
        elif vp not in viewpoints:
            rep.error(f"view '{v_id}' 的管辖 viewpoint '{vp}' 未被规约")
        else:
            used_vps.add(vp)
    for vp_id in viewpoints:
        if vp_id not in used_vps:
            rep.warn(f"viewpoint '{vp_id}' 已规约但没有任何 view 使用它 —— "
                     f"要么补视图，要么删掉该视角声明")

    # 约束 4 / 5：concern↔stakeholder 双向关联
    sh_of_concern: dict[str, list[str]] = {}
    for c_id, c in concerns.items():
        shs = c.get("stakeholders") or []
        for s in shs:
            if s not in stakeholders:
                rep.error(f"concern '{c_id}' 关联了未声明的 stakeholder '{s}'")
        sh_of_concern[c_id] = [s for s in shs if s in stakeholders]
        if not sh_of_concern[c_id]:
            rep.error(f"concern '{c_id}' 未关联任何 stakeholder —— "
                      f"追溯矩阵不完整（6.4 must）")
        for a in c.get("aspects") or []:
            if a not in aspects:
                rep.warn(f"concern '{c_id}' 引用了未声明的 aspect '{a}'")
    covered_sh = {s for lst in sh_of_concern.values() for s in lst}
    for s_id in stakeholders:
        if s_id not in covered_sh:
            rep.warn(f"stakeholder '{s_id}' 没有任何关注点 —— "
                     f"要么补 concern，要么它不是真的干系人")

    # 约束 6：八类必须考虑的干系人
    declared_cats: set[str] = set()
    for s in stakeholders.values():
        for cat in s.get("categories") or []:
            declared_cats.add(cat)
    na_sh = data.get("stakeholder_categories_na") or {}
    for cat in MANDATORY_STAKEHOLDER_CATEGORIES:
        if cat not in declared_cats and cat not in na_sh:
            rep.error(f"必须考虑的干系人类别 '{cat}' 既未识别、也未在 "
                      f"stakeholder_categories_na 中声明不适用及理由")

    # 约束 7：五类必须考虑的关注点
    declared_ccats: set[str] = set()
    for c in concerns.values():
        for cat in c.get("categories") or []:
            declared_ccats.add(cat)
    na_c = data.get("concern_categories_na") or {}
    for cat, desc in MANDATORY_CONCERN_CATEGORIES.items():
        if cat not in declared_ccats and cat not in na_c:
            rep.error(f"必须考虑的关注点类别 '{cat}'（{desc}）既未覆盖、"
                      f"也未在 concern_categories_na 中声明不适用及理由")

    # 约束 8：逆向场景的置信度纪律
    for kind, coll in (("stakeholder", stakeholders), ("concern", concerns)):
        for _id, item in coll.items():
            conf = item.get("confidence")
            if not conf:
                rep.warn(f"{kind} '{_id}' 未标注 confidence "
                         f"（取值：{'/'.join(sorted(VALID_CONFIDENCE))}）")
            elif conf not in VALID_CONFIDENCE:
                rep.error(f"{kind} '{_id}' 的 confidence '{conf}' 非法")

    # perspectives 引用检查
    for p_id, p in perspectives.items():
        for c in p.get("concerns") or []:
            if c not in concerns:
                rep.warn(f"perspective '{p_id}' 引用了未声明的 concern '{c}'")

    return {"stakeholders": stakeholders, "concerns": concerns,
            "viewpoints": viewpoints, "views": views,
            "framed": framed, "sh_of_concern": sh_of_concern}


def matrix(rows: list[str], cols: list[str], cell, row_label, col_label) -> str:
    if not rows or not cols:
        return "_（数据不足，无法生成矩阵）_\n"
    head = "| 关注点 | " + " | ".join(col_label(c) for c in cols) + " |"
    sep = "|---|" + "---|" * len(cols)
    lines = [head, sep]
    for r in rows:
        cells = " | ".join(cell(r, c) for c in cols)
        lines.append(f"| {row_label(r)} | {cells} |")
    return "\n".join(lines) + "\n"


def emit_matrices(m: dict) -> None:
    concerns, stakeholders = m["concerns"], m["stakeholders"]
    views, framed = m["views"], m["framed"]

    def cname(c: str) -> str:
        st = concerns[c].get("statement", c)
        st = st if len(st) <= 40 else st[:38] + "…"
        return f"**{c}** {st}"

    print("\n### 关注点↔干系人 追溯矩阵（42010 6.4，官方模板 must）\n")
    print(matrix(
        list(concerns), list(stakeholders),
        lambda c, s: "×" if s in m["sh_of_concern"].get(c, []) else "",
        cname,
        lambda s: stakeholders[s].get("name", s),
    ))

    # concern → view：经 viewpoint 传递
    view_of_vp: dict[str, list[str]] = {}
    for v_id, v in views.items():
        view_of_vp.setdefault(v.get("viewpoint"), []).append(v_id)

    def in_view(c: str, v: str) -> str:
        vp = views[v].get("viewpoint")
        return "×" if vp in framed.get(c, []) else ""

    print("\n### 关注点↔视图 覆盖矩阵（经视角传递，用于核对 6.8 覆盖）\n")
    print(matrix(
        list(concerns), list(views),
        in_view, cname,
        lambda v: views[v].get("name", v),
    ))


def main() -> int:
    ap = argparse.ArgumentParser(description="核对 AD 的 42010 完备性约束")
    ap.add_argument("target", type=Path, help="AD 目录或 manifest 文件路径")
    ap.add_argument("--emit-matrix", action="store_true",
                    help="额外输出可直接贴进 AD 的追溯矩阵")
    args = ap.parse_args()

    data = load_manifest(args.target)
    rep = Report()
    print(f"核对 AD manifest: {args.target}\n")
    m = check(data, rep)
    code = rep.emit()
    if args.emit_matrix:
        emit_matrices(m)
    return code


if __name__ == "__main__":
    sys.exit(main())
