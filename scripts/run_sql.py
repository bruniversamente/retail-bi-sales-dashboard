"""Run the project SQL scripts with DuckDB.

Usage:
    python scripts/run_sql.py
"""

from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "retail_bi.duckdb"
SQL_FILES = [
    ROOT / "sql" / "01_create_schema_duckdb.sql",
    ROOT / "sql" / "02_data_quality_checks.sql",
    ROOT / "sql" / "03_kpi_queries.sql",
]


def main() -> None:
    con = duckdb.connect(str(DB_PATH))
    try:
        for sql_file in SQL_FILES:
            print(f"\n--- Running {sql_file.name} ---")
            sql = sql_file.read_text(encoding="utf-8")
            statements = [statement.strip() for statement in sql.split(";") if statement.strip()]
            for statement in statements:
                result = con.execute(statement)
                first_sql_line = next(
                    (line.strip().lower() for line in statement.splitlines() if line.strip() and not line.strip().startswith("--")),
                    "",
                )
                if first_sql_line.startswith("select") or first_sql_line.startswith("with"):
                    print(result.fetchdf())
    finally:
        con.close()
    print(f"\nDatabase created at: {DB_PATH}")


if __name__ == "__main__":
    main()
