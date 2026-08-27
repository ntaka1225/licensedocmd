"""
Usage:
    python __main__.py <filename> <sheetname> [format] [-start N] [-end N]
    python __main__.py --test [format]

Arguments:
    filename   : 読み込むExcelファイルのパス
    sheetname  : 読み込むシート名
    format     : 出力フォーマット名（省略時はデフォルト）、"aggregate" で集約フォーマット
    -start N   : データ開始行（省略時は9行目）
    -end N     : データ終了行（省略時はA列空欄で自動判定）
    --test     : Excelファイル不要のダミーデータで出力確認（フォーマット指定可）
"""

import sys
import os
import argparse
from model import load_excel, START_ROW
from controller import generate_text, write_output


def main():
    args = sys.argv[1:]

    # --test オプションの判定（argparseより先に処理）
    if args and args[0] == "--test":
        format_name = args[1] if len(args) >= 2 else None
        _run_test(format_name)
        return

    # 通常実行: argparseでパース
    parser = argparse.ArgumentParser(
        prog="python __main__.py",
        add_help=False
    )
    parser.add_argument("filename",   help="Excelファイルのパス")
    parser.add_argument("sheetname",  help="シート名")
    parser.add_argument("format",     nargs="?", default=None, help="出力フォーマット")
    parser.add_argument("-start",     type=int, default=START_ROW,
                        help=f"データ開始行（省略時: {START_ROW}）")
    parser.add_argument("-end",       type=int, default=None,
                        help="データ終了行（省略時: A列空欄で自動判定）")

    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        _print_usage()
        sys.exit(1)

    # 行範囲のバリデーション
    if parsed.start < 1:
        print(f"エラー: -start は1以上を指定してください。（指定値: {parsed.start}）")
        sys.exit(1)
    if parsed.end is not None and parsed.end < parsed.start:
        print(f"エラー: -end は -start（{parsed.start}）以上を指定してください。（指定値: {parsed.end}）")
        sys.exit(1)

    if not os.path.isfile(parsed.filename):
        print(f"エラー: ファイル '{parsed.filename}' が見つかりません。")
        sys.exit(1)

    data = _load(
        parsed.filename, parsed.sheetname,
        use_dummy=False,
        start_row=parsed.start,
        end_row=parsed.end,
    )
    base = os.path.splitext(os.path.basename(parsed.filename))[0]
    _output(data, parsed.format, output_path=f"{base}_{parsed.sheetname}.txt")


def _run_test(format_name: str | None):
    print("[TEST] ダミーデータを使用してテスト実行します。")
    data = _load(filepath=None, sheetname=None, use_dummy=True)
    _output(data, format_name, output_path="test_output.txt")


def _load(filepath, sheetname, use_dummy: bool,
          start_row: int = START_ROW, end_row: int | None = None):
    try:
        return load_excel(filepath, sheetname,
                          use_dummy=use_dummy,
                          start_row=start_row,
                          end_row=end_row)
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: Excelファイルの読み込みに失敗しました。({e})")
        sys.exit(1)


def _output(data, format_name, output_path: str):
    if not data.entries:
        print("エラー: 指定範囲にデータが存在しません。")
        sys.exit(1)

    try:
        text = generate_text(data, format_name)
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    write_output(text, output_path)
    print(f"出力完了: {output_path}  ({len(data.entries)} 件)")


def _print_usage():
    print(
        "使い方:\n"
        f"  通常実行 : python __main__.py <filename> <sheetname> [format] [-start N] [-end N]\n"
        f"  テスト実行: python __main__.py --test [format]\n"
        f"\n"
        f"  -start N : データ開始行（省略時: {START_ROW}行目）\n"
        f"  -end N   : データ終了行（省略時: A列空欄で自動判定）"
    )


if __name__ == "__main__":
    main()
