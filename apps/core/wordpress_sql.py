import re
from pathlib import Path


INSERT_RE = re.compile(
    r"INSERT INTO `(?P<table>[^`]+)`\s*\((?P<columns>.*?)\)\s*VALUES\s*(?P<values>.*);",
    re.DOTALL,
)


def iter_wordpress_rows(sql_path, prefix, wanted_tables):
    """Stream selected INSERT rows from a phpMyAdmin MySQL dump."""
    sql_path = Path(sql_path)
    wanted_full_names = {f"{prefix}{name}" for name in wanted_tables}
    statement_lines = []
    collecting = False
    quoted = False
    escaped = False

    with sql_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        for line in handle:
            if not collecting:
                if not line.startswith("INSERT INTO `"):
                    continue
                table_match = re.match(r"INSERT INTO `([^`]+)`", line)
                if not table_match or table_match.group(1) not in wanted_full_names:
                    continue
                collecting = True
                statement_lines = []
                quoted = False
                escaped = False

            statement_lines.append(line)
            complete, quoted, escaped = _scan_statement_line(line, quoted, escaped)
            if not complete:
                continue

            statement = "".join(statement_lines)
            collecting = False
            match = INSERT_RE.match(statement.strip())
            if not match:
                continue
            full_table = match.group("table")
            table = full_table[len(prefix):]
            columns = re.findall(r"`([^`]+)`", match.group("columns"))
            for values in parse_mysql_values(match.group("values")):
                if len(values) == len(columns):
                    yield table, dict(zip(columns, values))


def _scan_statement_line(line, quoted, escaped):
    for char in line:
        if escaped:
            escaped = False
            continue
        if char == "\\" and quoted:
            escaped = True
            continue
        if char == "'":
            quoted = not quoted
            continue
        if char == ";" and not quoted:
            return True, quoted, escaped
    return False, quoted, escaped


def parse_mysql_values(text):
    """Parse MySQL VALUES tuples without executing SQL."""
    rows = []
    index = 0
    length = len(text)

    while index < length:
        while index < length and text[index] in " \t\r\n,":
            index += 1
        if index >= length:
            break
        if text[index] != "(":
            index += 1
            continue
        index += 1
        row = []

        while index < length:
            while index < length and text[index].isspace():
                index += 1
            if index < length and text[index] == ")":
                index += 1
                rows.append(row)
                break

            value, index = _parse_mysql_value(text, index)
            row.append(value)

            while index < length and text[index].isspace():
                index += 1
            if index < length and text[index] == ",":
                index += 1
                continue
            if index < length and text[index] == ")":
                index += 1
                rows.append(row)
                break
    return rows


def _parse_mysql_value(text, index):
    if text[index] == "'":
        index += 1
        output = []
        escape_map = {
            "0": "\0",
            "b": "\b",
            "n": "\n",
            "r": "\r",
            "t": "\t",
            "Z": "\x1a",
            "\\": "\\",
            "'": "'",
            '"': '"',
        }
        while index < len(text):
            char = text[index]
            if char == "\\" and index + 1 < len(text):
                index += 1
                output.append(escape_map.get(text[index], text[index]))
                index += 1
                continue
            if char == "'":
                return "".join(output), index + 1
            output.append(char)
            index += 1
        return "".join(output), index

    end = index
    while end < len(text) and text[end] not in ",)":
        end += 1
    raw = text[index:end].strip()
    if raw.upper() == "NULL":
        return None, end
    if re.fullmatch(r"-?\d+", raw):
        return int(raw), end
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw), end
    return raw, end
