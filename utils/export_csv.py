import os
from pathlib import Path

import duckdb

root = Path(__file__).resolve().parents[1]
os.chdir(root)
os.makedirs("app/data", exist_ok=True)

con = duckdb.connect()
con.execute(f"ATTACH '{root / 'tweedekamer.duckdb'}' AS tk (READ_ONLY)")
con.execute("USE tk")

sql = (root / "utils" / "ster_ontwerp.sql").read_text(encoding="utf-8")
regels = [r for r in sql.splitlines() if not r.strip().startswith("--")]
for statement in "\n".join(regels).split(";"):
    if statement.strip():
        con.execute(statement)

for naam in ["fact_stemming", "dim_fractie", "dim_persoon", "dim_besluit",
             "dim_zaak", "brug_besluit_zaak", "dim_datum"]:
    n = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('app/data/{naam}.csv')").fetchone()[0]
    print(naam, n)
    