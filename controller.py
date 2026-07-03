from typing import Optional
from model import OSSData, OSSEntry

SEPARATOR      = "=" * 64
LICENSE_SEP    = "-" * 70   # [Licenses]セクションの区切り（------...）
TEXT_SEP       = "-" * 40   # ライセンス種別とOSS名の後の区切り
COPYRIGHT_INDENT = "    "   # 4スペース
OSS_INDENT       = "    "   # 4スペース

COPYRIGHT_PREFIX = "Copyright: "
DEFAULT_INDENT   = " " * len(COPYRIGHT_PREFIX)  # defaultフォーマット用11文字


# ------------------------------------------------------------------ #
# デフォルトフォーマット                                                #
# ------------------------------------------------------------------ #

def format_default(entry: OSSEntry) -> str:
    copyright_str    = ("\n" + DEFAULT_INDENT).join(entry.copyrights)
    license_str      = ", ".join(entry.license_names)
    license_text_str = "\n".join(entry.license_texts)

    lines = [
        SEPARATOR,
        entry.oss_name,
        f"Copyright: {copyright_str}",
        f"License: {license_str}",
        "---",
        license_text_str,
        "",
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------ #
# 集約フォーマット                                                      #
# ------------------------------------------------------------------ #

def _build_license_groups(data: OSSData) -> list[dict]:
    """
    [Licenses]セクション用グループリストを生成する。
    ライセンス原文（license_textsを改行結合した文字列）が同一のエントリを集約。
    各グループ:
        "license_names" : list[str]  ライセンス種別（重複除去・順序維持）
        "oss_names"     : list[str]  OSS名リスト（登場順）
        "license_text"  : str        ライセンス原文
    """
    groups: dict[str, dict] = {}
    for entry in data.entries:
        key = "\n".join(entry.license_texts)
        if key not in groups:
            groups[key] = {
                "license_names": [],
                "oss_names":     [],
                "license_text":  key,
            }
        g = groups[key]
        g["oss_names"].append(entry.oss_name)
        for ln in entry.license_names:
            if ln not in g["license_names"]:
                g["license_names"].append(ln)

    return list(groups.values())


def _format_copyrights_section(data: OSSData) -> str:
    """
    [Copyrights]セクションを生成する。
    全OSSを上から順に列挙し、Copyright表記を4スペースインデントで記載。
    """
    lines = [
        "[Copyrights]",
        SEPARATOR,
    ]
    for entry in data.entries:
        lines.append(entry.oss_name)
        for copyright in entry.copyrights:
            # Copyrightが複数行のセル内改行を含む場合も各行インデント
            for line in copyright.splitlines():
                lines.append(f"{COPYRIGHT_INDENT}{line}")
    return "\n".join(lines)


def _format_licenses_section(data: OSSData) -> str:
    """
    [Licenses]セクションを生成する。
    ライセンス原文が同一のエントリを集約し、カンマ区切りでOSS名を列挙。
    """
    groups = _build_license_groups(data)

    lines = [
        "[Licenses]",
        SEPARATOR,
    ]
    for g in groups:
        license_str = ", ".join(g["license_names"])
        oss_str     = ", ".join(g["oss_names"])
        lines.append(LICENSE_SEP)
        lines.append(license_str)
        lines.append(f"{OSS_INDENT}{oss_str}:")
        lines.append(TEXT_SEP)
        lines.append(g["license_text"])
        lines.append("")

    return "\n".join(lines)


def generate_aggregate_text(data: OSSData) -> str:
    copyrights_section = _format_copyrights_section(data)
    licenses_section   = _format_licenses_section(data)
    return copyrights_section + "\n\n\n" + licenses_section + "\n"


# ------------------------------------------------------------------ #
# フォーマット選択・テキスト生成                                         #
# ------------------------------------------------------------------ #

_VALID_FORMATS = {None, "default", "aggregate"}


def get_formatter(format_name: Optional[str] = None):
    if format_name not in _VALID_FORMATS:
        raise ValueError(
            f"未知のフォーマット '{format_name}' です。利用可能: "
            f"{[f for f in _VALID_FORMATS if f]}"
        )
    return format_name


def generate_text(data: OSSData, format_name: str | None = None) -> str:
    get_formatter(format_name)  # バリデーション

    if format_name == "aggregate":
        return generate_aggregate_text(data)

    # default（またはNone）
    blocks = [format_default(entry) for entry in data.entries]
    return "\n".join(blocks) + "\n" + SEPARATOR + "\n"


def write_output(text: str, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
