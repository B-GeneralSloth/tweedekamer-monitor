WITH gold_persoon AS (
  SELECT p.id, p.titels, p.roepnaam, p.achternaam, p.overlijdensdatum, p.woonplaats, p.land, fzp.van, fzp.tot_en_met, f.afkorting
  FROM silver.persoon as p, silver.fractie_zetel_persoon as fzp, silver.fractie as f, silver.fractie_zetel as fz
  WHERE p.id = fzp.persoon_id
  AND fzp.fractie_zetel_id = fz.id
  AND fz.fractie_id = f.id
  )
  SELECT r.id, r.persoon_id, p.roepnaam, p.achternaam, r.doel, r.bestemming, r.van, r.tot_en_met, r.betaald_door, p.afkorting as fractielabel, SUM(r.tot_en_met - r.van) as reisduur, p.overlijdensdatum
  FROM silver.persoon_reis as r
  INNER JOIN gold_persoon as p ON
  p.id = r.persoon_id
  AND r.van BETWEEN p.van AND COALESCE(p.tot_en_met, CURRENT_DATE)
  GROUP BY r.id, r.persoon_id, p.roepnaam, p.achternaam, r.doel, r.bestemming, r.van, r.tot_en_met, r.betaald_door, fractielabel, p.overlijdensdatum