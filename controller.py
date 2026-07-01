from typing import Optional
from model import OSSData, OSSEntry

SEPARATOR = "=" * 64


def get_formatter(format_name: Optional[str] = None):
    formatters = {
        None: format_default,
        "default": format_default,
        # 今後ここに追加: "format2": format_xxx,
    }
    if format_name not in formatters:
        raise ValueError(
            f"未知のフォーマット '{format_name}' です。利用可能: {[k for k in formatters if k]}"
        )
    return formatters[format_name]


COPYRIGHT_PREFIX = "Copyright: "
COPYRIGHT_INDENT = " " * len(COPYRIGHT_PREFIX)  # 11文字


def format_default(entry: OSSEntry) -> str:
    # Copyright: 1件目はプレフィックスと同行、2件目以降は11スペースでインデント
    copyright_str = ("\n" + COPYRIGHT_INDENT).join(entry.copyrights)

    # License: 複数ならカンマ区切り
    license_str = ", ".join(entry.license_names)

    # ライセンス原文: 複数なら改行で連結
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


def generate_text(data: OSSData, format_name: str | None = None) -> str:
    formatter = get_formatter(format_name)
    blocks = [formatter(entry) for entry in data.entries]
    return "\n".join(blocks) + "\n" + SEPARATOR + "\n"


def write_output(text: str, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
