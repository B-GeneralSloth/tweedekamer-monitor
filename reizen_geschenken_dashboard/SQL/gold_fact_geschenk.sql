WITH gold_persoon AS (
  SELECT p.id, p.titels, p.roepnaam, p.achternaam, p.overlijdensdatum, p.woonplaats, p.land, fzp.van, fzp.tot_en_met, f.afkorting
  FROM silver.persoon as p, silver.fractie_zetel_persoon as fzp, silver.fractie as f, silver.fractie_zetel as fz
  WHERE p.id = fzp.persoon_id
  AND fzp.fractie_zetel_id = fz.id
  AND fz.fractie_id = f.id
  )
  SELECT g.id, g.persoon_id, p.roepnaam, p.achternaam, g.datum, g.gewicht, g.omschrijving, p.afkorting, p.overlijdensdatum
  FROM silver.persoon_geschenk as g
  INNER JOIN gold_persoon as p ON
  p.id = g.persoon_id
  AND g.datum BETWEEN p.van AND COALESCE(p.tot_en_met, CURRENT_DATE)