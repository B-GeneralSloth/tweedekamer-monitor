from pathlib import Path
import duckdb

map_hier = Path(__file__).resolve().parent
database = map_hier.parent / "tweedekamer.duckdb"
connection = duckdb.connect(str(database), read_only=True)

data_map = map_hier / "data"
data_map.mkdir(exist_ok=True)

for sql_bestand in sorted((map_hier / "sql").glob("*.sql")):
    df = connection.execute(sql_bestand.read_text(encoding="utf-8")).fetchdf()
    df.to_csv(data_map / f"{sql_bestand.stem}.csv", index=False)
    print(f"{sql_bestand.stem}: {len(df)} rijen opgeslagen")