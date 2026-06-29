from typing import Optional
from model import OSSData, OSSEntry

SEPARATOR = "=" * 64


def get_formatter(format_name: Optional[str] = None):
    """フォーマット名からフォーマッター関数を返す。未指定はデフォルト。"""
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


def format_default(entry: OSSEntry) -> str:
    lines = [
        SEPARATOR,
        entry.oss_name,
        f"Copyright: {entry.copyright}",
        f"License: {entry.license_name}",
        "---",
        entry.license_text,
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


