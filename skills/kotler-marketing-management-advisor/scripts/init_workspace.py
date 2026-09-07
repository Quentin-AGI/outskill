#!/usr/bin/env python3
"""Create a private marketing workspace. Dry-run by default; never overwrites."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"

DIRECTORIES = (
    "company-profile",
    "facts/customers",
    "facts/competitors",
    "facts/products",
    "facts/channels",
    "facts/organization",
    "cases",
    "knowledge/hypotheses",
    "knowledge/observed-patterns",
    "knowledge/candidate-brand-knowledge",
    "knowledge/approved-brand-knowledge",
    "knowledge/retired",
    "people",
    "extensions",
    "book",
)

STARTER_FILES = {
    "company-profile/company.md": """# 企业营销配置\n\n- 企业/业务代号：\n- 品牌：\n- 市场/国家：\n- 主要顾客：\n- 核心价值主张：\n- 当前公司目标：\n- 营销负责人：\n- 更新时间：\n""",
    "company-profile/permissions.md": """# 权限与隐私\n\n- 企业事实默认可见范围：\n- 案例默认可见范围：\n- 已批准知识可见范围：\n- 外部查询授权人：\n- 默认脱敏字段：品牌、SKU、客户、供应商、人员、账号、经营指标、未公开计划\n- 个人能力档案：默认仅本人可见\n""",
    "company-profile/source-register.md": """# 企业来源登记\n\n| 来源 ID | 类型 | 提供者/机构 | 日期/更新时间 | 可见范围 | 可信度 | 备注 |\n|---|---|---|---|---|---|---|\n""",
    "cases/index.md": """# 案例索引\n\n| case_id | 核心 Goal | 成功指标/口径/期限 | 市场 | 核心决策对象 | 状态 | 最新版本 | 更新时间 |\n|---|---|---|---|---|---|---|---|\n""",
    "cases/_case-template.md": """# 营销案例主页\n\n- case_id：\n- parent_case / related_cases：\n- 核心 Goal：\n- 成功指标、口径与期限：\n- 市场：\n- 核心决策对象：\n- 决策人：\n- 当前阶段：\n- 最新咨询版本：\n- 分叉原因：\n- 继承/不继承的事实：\n""",
    "knowledge/README.md": """# 企业营销知识状态\n\n只按以下路径晋级：待验证假设 → 单次经验 → 重复模式 → 候选品牌知识 → 营销负责人批准 → 正式品牌知识。保留来源、范围、反例、版本和废止条件。\n""",
    "people/README.md": """# 个人学习档案\n\n默认不要在共享服务账号下集中保存成员档案。每位成员应在自己的操作系统账号或独立私有根中初始化工作区；未经本人主动授权，不用于经理评分或团队公开。团队案例与个人学习档案属于两个权限域，不能通过递归放宽本目录权限来共享。\n""",
    "book/README.md": """# 可选本地原书增强\n\n此处只保存私有 EPUB 元数据索引，不保存公开包内容。用 `epub_locator.py index` 生成；必要核对使用带锚点且有硬上限的 `epub_locator.py excerpt`。不要提交 EPUB、连续原文或私有索引到公共仓库。\n""",
}

TEMPLATE_COPIES = {
    "formal-consultation-record.md": "cases/_consultation-template.md",
    "review-and-knowledge-promotion.md": "cases/_review-template.md",
    "extension-manifest.md": "extensions/_manifest-template.md",
}


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--apply", action="store_true", help="Create files after reviewing the dry-run.")
    args = parser.parse_args()
    requested_destination = args.destination.expanduser()
    if requested_destination.is_symlink():
        print("error: destination must not be a symbolic link", file=sys.stderr)
        return 2
    destination = requested_destination.resolve()

    if destination == Path(destination.anchor) or within(destination, SKILL_DIR):
        print("error: destination must be a private directory outside the Skill", file=sys.stderr)
        return 2

    metadata_file = destination / ".kotler-workspace.json"
    planned = [destination / item for item in DIRECTORIES]
    planned += [destination / item for item in STARTER_FILES]
    planned += [destination / item for item in TEMPLATE_COPIES.values()]
    planned.append(metadata_file)
    collisions = [path for path in planned if path.is_file()]

    if destination.exists() and any(destination.iterdir()):
        print("error: destination must be new or empty; refusing to merge existing contents", file=sys.stderr)
        return 3

    print(f"destination: {destination}")
    print(f"mode: {'apply' if args.apply else 'dry-run'}")
    print(f"directories: {len(DIRECTORIES)}; starter files: {len(STARTER_FILES) + len(TEMPLATE_COPIES)}")
    if collisions:
        print("error: refusing to overwrite existing files:", file=sys.stderr)
        for path in collisions:
            print(f"  {path}", file=sys.stderr)
        return 3
    if not args.apply:
        print("No files changed. Re-run with --apply after reviewing the destination.")
        return 0

    old_umask = os.umask(0o077) if os.name == "posix" else None
    try:
        destination.mkdir(parents=True, exist_ok=True)
        for path in planned[: len(DIRECTORIES)]:
            path.mkdir(parents=True, exist_ok=True)
        for relative, content in STARTER_FILES.items():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        for source_name, relative in TEMPLATE_COPIES.items():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(TEMPLATES / source_name, target)
        metadata = {
            "schema_version": 1,
            "kind": "private-marketing-workspace",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "access_model": "owner-only by default; team sharing requires explicit external ACL",
        }
        metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if os.name == "posix":
            for path in [destination, *planned]:
                path.chmod(0o700 if path.is_dir() else 0o600)
    finally:
        if old_umask is not None:
            os.umask(old_umask)

    if os.name == "posix":
        bad = [
            path for path in [destination, *planned]
            if stat.S_IMODE(path.stat().st_mode) != (0o700 if path.is_dir() else 0o600)
        ]
        if bad:
            print("error: private permission verification failed", file=sys.stderr)
            return 4
        print("Private workspace created with owner-only directory/file permissions (0700/0600).")
    else:
        print("Workspace created without overwriting files. WARNING: this platform did not enforce POSIX access control; configure OS ACLs before storing private data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
