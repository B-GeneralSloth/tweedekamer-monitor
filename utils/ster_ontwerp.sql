-- BASIS: stemmingen met datum, beperkt tot 2024
CREATE OR REPLACE TEMP VIEW v_stemming AS
SELECT
    s.id AS stemming_id,
    s.besluit_id,
    s.fractie_id,
    s.persoon_id,
    CAST(a.datum AS DATE) AS datum,
    s.soort,
    s.fractie_grootte,
    s.vergissing
FROM silver.stemming s
JOIN silver.besluit b ON s.besluit_id = b.id
JOIN silver.agendapunt ap ON b.agendapunt_id = ap.id
JOIN silver.activiteit a ON ap.activiteit_id = a.id
WHERE a.datum >= DATE '2024-01-01' AND a.datum < DATE '2025-01-01';

-- FEITENTABEL
COPY (
    SELECT * FROM v_stemming
) TO 'app/data/fact_stemming.csv' (HEADER, DELIMITER ',');

-- DIMENSIE FRACTIE
COPY (
    SELECT id AS fractie_id, naam_nl, afkorting, datum_actief, datum_inactief, aantal_zetels
    FROM silver.fractie
    WHERE id IN (SELECT DISTINCT fractie_id FROM v_stemming)
) TO 'app/data/dim_fractie.csv' (HEADER, DELIMITER ',');

-- DIMENSIE PERSOON
COPY (
    SELECT id AS persoon_id, achternaam, roepnaam, geslacht, geboortedatum, functie
    FROM silver.persoon
    WHERE id IN (SELECT DISTINCT persoon_id FROM v_stemming WHERE persoon_id IS NOT NULL)
) TO 'app/data/dim_persoon.csv' (HEADER, DELIMITER ',');

-- DIMENSIE BESLUIT
COPY (
    SELECT
        b.id AS besluit_id,
        b.besluit_soort,
        b.stemmings_soort,
        b.status,
        ap.onderwerp AS agendapunt_onderwerp,
        a.soort AS activiteit_soort,
        a.kamer
    FROM silver.besluit b
    JOIN silver.agendapunt ap ON b.agendapunt_id = ap.id
    JOIN silver.activiteit a ON ap.activiteit_id = a.id
    WHERE b.id IN (SELECT DISTINCT besluit_id FROM v_stemming)
) TO 'app/data/dim_besluit.csv' (HEADER, DELIMITER ',');

-- DIMENSIE ZAAK
COPY (
    SELECT id AS zaak_id, soort AS zaak_soort, onderwerp, titel, status, afgedaan, gestart_op
    FROM silver.zaak
    WHERE id IN (
        SELECT zaak_id FROM silver.besluit_zaak
        WHERE besluit_id IN (SELECT DISTINCT besluit_id FROM v_stemming)
    )
) TO 'app/data/dim_zaak.csv' (HEADER, DELIMITER ',');

-- BRUGTABEL BESLUIT - ZAAK
COPY (
    SELECT besluit_id, zaak_id
    FROM silver.besluit_zaak
    WHERE besluit_id IN (SELECT DISTINCT besluit_id FROM v_stemming)
) TO 'app/data/brug_besluit_zaak.csv' (HEADER, DELIMITER ',');

-- DIMENSIE DATUM
COPY (
    SELECT
        CAST(d AS DATE) AS datum,
        YEAR(d) AS jaar,
        MONTH(d) AS maandnummer,
        strftime(d, '%Y-%m') AS jaar_maand,
        ISODOW(d) AS dagnummer
    FROM generate_series(DATE '2024-01-01', DATE '2024-12-31', INTERVAL 1 DAY) AS t(d)
) TO 'app/data/dim_datum.csv' (HEADER, DELIMITER ',');