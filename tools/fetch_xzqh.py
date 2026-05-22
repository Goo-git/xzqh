#!/usr/bin/env python3
"""Fetch China administrative division codes from dmfw.mca.gov.cn.

The script downloads the current province-level full trees from the Ministry of
Civil Affairs public page and exports a flattened Excel workbook.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


BASE_URL = "https://dmfw.mca.gov.cn"
PUBLISH_PAGE = f"{BASE_URL}/XzqhVersionPublish.html"
DEFAULT_TIMEOUT = 60
LEVEL_NAMES = {
    0: "全国",
    1: "省级",
    2: "地级",
    3: "县级",
    4: "乡级",
}


def request_text(url: str, timeout: int, retries: int = 6) -> str:
    last_error: Exception | None = None
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
        ),
        "Referer": PUBLISH_PAGE,
        "Accept": "application/json,text/html,*/*",
    }
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(60, 2 * attempt * attempt))
    raise RuntimeError(f"request failed after {retries} attempts: {url}") from last_error


def request_json(url: str, timeout: int, retries: int = 6) -> dict[str, Any]:
    last_payload: dict[str, Any] | None = None
    for attempt in range(1, retries + 1):
        text = request_text(url, timeout)
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"response is not JSON: {url}") from exc
        if payload.get("status") == 200:
            return payload
        last_payload = payload
        message = str(payload.get("message") or "")
        if "频繁" not in message or attempt == retries:
            break
        time.sleep(min(60, 3 * attempt * attempt))
    raise RuntimeError(f"unexpected status from {url}: {last_payload!r}")


def parse_table_name(page_html: str) -> str:
    match = re.search(r"tableName\s*=\s*['\"]([^'\"]+)['\"]", page_html)
    if not match:
        stamp = dt.datetime.now().strftime("%Y%m%d")
        return f"Xzqh_{stamp}"
    return match.group(1)


def parse_data_date(page_html: str) -> str:
    match = re.search(r"数据截止日期为(\d{4}年\d{1,2}月\d{1,2}日)", page_html)
    return match.group(1) if match else ""


def parse_provinces(page_html: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r'<div\s+class="provinceBtn"\s+code="([^"]+)"\s+val="([^"]+)"',
        re.IGNORECASE,
    )
    provinces = []
    for code, name in pattern.findall(page_html):
        provinces.append({"code": html.unescape(code), "name": html.unescape(name)})
    if not provinces:
        raise RuntimeError("no provinces found on publish page")
    return provinces


def fetch_tree(code: str, max_level: int, timeout: int) -> dict[str, Any]:
    query = urllib.parse.urlencode(
        {
            "code": code,
            "trimCode": "true",
            "maxLevel": str(max_level),
        }
    )
    url = f"{BASE_URL}/xzqh/getList?{query}"
    payload = request_json(url, timeout)
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"province payload has no data object: {code}")
    normalize_children(data)
    return data


def fetch_province_tree(code: str, timeout: int) -> dict[str, Any]:
    return fetch_tree(code, 3, timeout)


def fetch_county_tree(code: str, timeout: int) -> dict[str, Any]:
    return fetch_tree(code, 4, timeout)


def normalize_children(node: dict[str, Any]) -> None:
    children = node.get("children")
    if children is None:
        node["children"] = []
        return
    if not isinstance(children, list):
        raise RuntimeError(f"unexpected children value for {node.get('code')}: {children!r}")
    for child in children:
        normalize_children(child)


def safe_filename(code: str, name: str) -> str:
    raw = f"{code}_{name}"
    return re.sub(r'[<>:"/\\|?*\s]+', "_", raw).strip("_")


def sort_key(code: str) -> tuple[int, str]:
    return (0, code) if code.isdigit() else (1, code)


def collect_nodes_by_level(node: dict[str, Any], level: int) -> list[dict[str, Any]]:
    result = []
    if int(node.get("level") or 0) == level:
        result.append(node)
    for child in node.get("children", []):
        result.extend(collect_nodes_by_level(child, level))
    return result


def has_township_data(province_tree: dict[str, Any]) -> bool:
    counties = collect_nodes_by_level(province_tree, 3)
    return bool(counties) and all(node.get("children") for node in counties)


def enrich_county_children(
    province_tree: dict[str, Any],
    timeout: int,
    workers: int,
    county_sleep: float = 0.0,
    autosave_path: Path | None = None,
) -> int:
    counties = collect_nodes_by_level(province_tree, 3)
    if not counties:
        return 0

    by_code = {str(node.get("code") or ""): node for node in counties}
    fetched = 0
    pending_codes = [code for code, node in by_code.items() if code and not node.get("children")]
    if workers <= 1:
        for code in pending_codes:
            county_tree = fetch_county_tree(code, timeout)
            by_code[code]["children"] = county_tree.get("children", [])
            fetched += 1
            if autosave_path and fetched % 10 == 0:
                write_json(autosave_path, province_tree)
            if county_sleep > 0:
                time.sleep(county_sleep)
        if autosave_path:
            write_json(autosave_path, province_tree)
        return fetched

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {
            executor.submit(fetch_county_tree, code, timeout): code
            for code in pending_codes
        }
        for future in concurrent.futures.as_completed(future_map):
            code = future_map[future]
            county_tree = future.result()
            by_code[code]["children"] = county_tree.get("children", [])
            fetched += 1
            if county_sleep > 0:
                time.sleep(county_sleep)
    if autosave_path:
        write_json(autosave_path, province_tree)
    return fetched


def flatten_tree(
    node: dict[str, Any],
    rows: list[dict[str, str]],
    lineage: list[dict[str, Any]] | None = None,
) -> None:
    lineage = list(lineage or [])
    code = str(node.get("code") or "")
    name = str(node.get("name") or "")
    level = int(node.get("level") or 0)
    current = {
        "code": code,
        "name": name,
        "level": str(level),
        "level_name": LEVEL_NAMES.get(level, str(level)),
        "type": str(node.get("type") or ""),
    }

    province = first_level(lineage, 1)
    city = first_level(lineage, 2)
    county = first_level(lineage, 3)
    if level == 1:
        province = current
    elif level == 2:
        city = current
    elif level == 3:
        county = current

    parent = lineage[-1] if lineage else {}
    path_parts = [str(item.get("name") or "") for item in lineage if item.get("name")]
    if name:
        path_parts.append(name)

    rows.append(
        {
            "code": code,
            "name": name,
            "level": str(level),
            "level_name": LEVEL_NAMES.get(level, str(level)),
            "type": str(node.get("type") or ""),
            "parent_code": str(parent.get("code") or ""),
            "parent_name": str(parent.get("name") or ""),
            "province_code": str(province.get("code") or ""),
            "province_name": str(province.get("name") or ""),
            "city_code": str(city.get("code") or ""),
            "city_name": str(city.get("name") or ""),
            "county_code": str(county.get("code") or ""),
            "county_name": str(county.get("name") or ""),
            "name_path": "/".join(path_parts),
        }
    )

    lineage.append(current)
    for child in sorted(node.get("children", []), key=lambda item: sort_key(str(item.get("code") or ""))):
        flatten_tree(child, rows, lineage)


def first_level(lineage: list[dict[str, Any]], level: int) -> dict[str, Any]:
    for item in lineage:
        if str(item.get("level")) == str(level):
            return item
    return {}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def xml_text(value: Any) -> str:
    return escape(str(value), {'"': "&quot;"})


def column_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def sheet_xml(rows: list[list[Any]], widths: list[int] | None = None) -> str:
    cols = ""
    if widths:
        cols = "<cols>" + "".join(
            f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>'
            for i, width in enumerate(widths, start=1)
        ) + "</cols>"
    xml_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            ref = f"{column_name(col_index)}{row_index}"
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{xml_text(value)}</t></is></c>')
        xml_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
        'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        f"{cols}<sheetData>{''.join(xml_rows)}</sheetData>"
        "</worksheet>"
    )


def workbook_xml(sheet_names: list[str]) -> str:
    sheets = "".join(
        f'<sheet name="{xml_text(name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{sheets}</sheets></workbook>"
    )


def workbook_rels_xml(sheet_count: int) -> str:
    rels = []
    for idx in range(1, sheet_count + 1):
        rels.append(
            f'<Relationship Id="rId{idx}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{idx}.xml"/>'
        )
    rels.append(
        f'<Relationship Id="rId{sheet_count + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(rels)}</Relationships>"
    )


def content_types_xml(sheet_count: int) -> str:
    sheet_overrides = "".join(
        '<Override PartName="/xl/worksheets/sheet{idx}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'.format(
            idx=idx
        )
        for idx in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        f"{sheet_overrides}</Types>"
    )


def root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/></Relationships>'
    )


def styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        "</styleSheet>"
    )


def write_xlsx(path: Path, sheets: list[tuple[str, list[list[Any]], list[int] | None]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml(len(sheets)))
        archive.writestr("_rels/.rels", root_rels_xml())
        archive.writestr("xl/workbook.xml", workbook_xml([sheet[0] for sheet in sheets]))
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(len(sheets)))
        archive.writestr("xl/styles.xml", styles_xml())
        for idx, (_name, rows, widths) in enumerate(sheets, start=1):
            archive.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml(rows, widths))


def build_excel_rows(rows: list[dict[str, str]]) -> list[list[str]]:
    columns = [
        ("code", "行政区划代码"),
        ("name", "行政区划名称"),
        ("level", "层级"),
        ("level_name", "层级名称"),
        ("type", "类型"),
        ("parent_code", "父级代码"),
        ("parent_name", "父级名称"),
        ("province_code", "省级代码"),
        ("province_name", "省级名称"),
        ("city_code", "地级代码"),
        ("city_name", "地级名称"),
        ("county_code", "县级代码"),
        ("county_name", "县级名称"),
        ("name_path", "名称路径"),
    ]
    excel_rows = [[title for _key, title in columns]]
    for row in rows:
        excel_rows.append([row.get(key, "") for key, _title in columns])
    return excel_rows


def code6(code: str) -> str:
    if not code.isdigit():
        return code
    if len(code) <= 2:
        return code.zfill(2) + "0000"
    if len(code) <= 4:
        return code.zfill(4) + "00"
    return code[:6]


def build_province_city_county_rows(rows: list[dict[str, str]]) -> list[list[str]]:
    excel_rows = [["code", "name", "level", "province", "city", "county"]]
    for row in rows:
        level = row.get("level", "")
        if level not in {"1", "2", "3"}:
            continue
        code = code6(row.get("code", ""))
        if code.isdigit() and len(code) == 6:
            province, city, county = code[:2], code[2:4], code[4:6]
        else:
            province, city, county = code, "", ""
        excel_rows.append([code, row.get("name", ""), level, province, city, county])
    return excel_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch administrative division codes from dmfw.mca.gov.cn")
    parser.add_argument("--output-dir", default="data", help="output directory, default: data")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout seconds")
    parser.add_argument("--sleep", type=float, default=0.2, help="sleep seconds between province requests")
    parser.add_argument("--workers", type=int, default=2, help="parallel county requests, default: 2")
    parser.add_argument("--county-sleep", type=float, default=0.3, help="sleep seconds between county requests")
    parser.add_argument("--no-townships", action="store_true", help="only fetch province/city/county levels")
    parser.add_argument("--reuse", action="store_true", help="reuse existing province JSON files when present")
    return parser.parse_args()


class FetchCancelled(Exception):
    """Raised when the caller's should_cancel() returns True between provinces."""


def run(
    args: argparse.Namespace,
    on_log=print,
    on_progress=None,
    should_cancel=None,
) -> None:
    """Execute the fetch pipeline with pluggable log / progress / cancel hooks.

    - ``on_log(msg)``: receives each line that the CLI used to print().
    - ``on_progress(done, total)``: called after each province completes (and
      once before the loop with done=0); pass None to skip.
    - ``should_cancel()``: polled between provinces; raise FetchCancelled if it
      returns True.
    """
    output_root = Path(args.output_dir)
    page_html = request_text(PUBLISH_PAGE, args.timeout)
    table_name = parse_table_name(page_html)
    data_date = parse_data_date(page_html)
    provinces = parse_provinces(page_html)

    version_dir = output_root / table_name
    province_dir = version_dir / "provinces"
    all_rows: list[dict[str, str]] = []
    province_index = []

    on_log(f"tableName: {table_name}")
    if data_date:
        on_log(f"dataDate: {data_date}")
    on_log(f"provinceCount: {len(provinces)}")
    if on_progress is not None:
        on_progress(0, len(provinces))

    for index, province in enumerate(provinces, start=1):
        if should_cancel is not None and should_cancel():
            on_log("cancelled by user")
            raise FetchCancelled()
        code = province["code"]
        name = province["name"]
        file_name = f"{safe_filename(code, name)}.json"
        json_path = province_dir / file_name
        on_log(f"[{index:02d}/{len(provinces):02d}] fetching {code} {name}")
        tree = read_json(json_path) if args.reuse and json_path.exists() else fetch_province_tree(code, args.timeout)
        county_requests = 0
        if not args.no_townships and not has_township_data(tree):
            county_requests = enrich_county_children(
                tree,
                args.timeout,
                args.workers,
                county_sleep=args.county_sleep,
                autosave_path=json_path,
            )
            write_json(json_path, tree)
        elif not json_path.exists():
            write_json(json_path, tree)
        before = len(all_rows)
        flatten_tree(tree, all_rows)
        province_index.append(
            {
                "code": code,
                "name": name,
                "file": f"provinces/{file_name}",
                "rows": len(all_rows) - before,
                "countyRequests": county_requests,
            }
        )
        if on_progress is not None:
            on_progress(index, len(provinces))
        if args.sleep > 0 and index < len(provinces):
            time.sleep(args.sleep)

    all_rows.sort(key=lambda row: sort_key(row["code"]))
    write_json(version_dir / "province_index.json", province_index)

    fetched_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    metadata = [
        ["字段", "值"],
        ["来源页面", PUBLISH_PAGE],
        ["版本表名", table_name],
        ["数据截止日期", data_date],
        ["抓取时间", fetched_at],
        ["省级 JSON 数", str(len(province_index))],
        ["汇总记录数", str(len(all_rows))],
    ]
    excel_rows = build_excel_rows(all_rows)
    pcc_rows = build_province_city_county_rows(all_rows)
    write_xlsx(
        version_dir / f"{table_name}_行政区划代码汇总.xlsx",
        [
            ("行政区划代码", excel_rows, [14, 24, 8, 10, 14, 16, 24, 12, 22, 12, 22, 12, 22, 70]),
            ("省市区", pcc_rows, [14, 24, 8, 12, 10, 10]),
            ("元数据", metadata, [18, 80]),
        ],
    )
    on_log(f"saved: {version_dir}")
    on_log(f"rows: {len(all_rows)}")


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
