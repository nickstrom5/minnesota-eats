"""Minnesota's open official records -> data/raw/official/ (git-ignored, never public).

Checked 2026-11-06 (playbook/12-sources.md). Minnesota has no statewide inspection data and no statewide grade: MDH and about 30
delegated city and county agencies inspect restaurants, and only the City of Minneapolis publishes its inspections in bulk:
- "Food_Inspections" (City of Minneapolis open data, ArcGIS item 4eea8bf452e34f8c9d9ac07c54c0b4ab), refreshed weekly on Fridays: one
  row per violation (an inspection with none has one row), with the City's own 0-100 InspectionScore per InspectionIDNumber, the
  facility id and category, the inspection type (Routine, Follow-Up, VerRec) and date. Copyright waived by the City ("To the extent
  possible under law, City of Minneapolis has waived all copyright and related or neighboring rights to Open Data").
- "On_Sale_Liquor" (item 5042131de56d44749f6e43c0b5738b21), refreshed monthly: the City's on-sale liquor, wine and beer licenses with
  status ("Pending" isn't live). Same waiver.
St. Paul's "Liquor Licenses" layer was last edited 2025-07-01 (stale) and DPS-AGE's statewide license search is search-only and
bot-protected, so neither is read. One request at a time; inspector comments, owner and person names are not fetched.
"""
import datetime, json, os, time
import requests

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "official")
os.makedirs(os.path.join(OUT, "minneapolis"), exist_ok=True)
UA = "MinnesotaEatsDataCheck/1.0 (+https://nickstrom5.github.io/minnesota-eats/; nick@eatsranked.com)"
BASE = "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services"
S = requests.Session(); S.headers["User-Agent"] = UA


def get(url, **params):
    for attempt in range(4):
        r = S.get(url, params=params, timeout=90)
        if r.status_code == 200:
            return r.json()
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()


def arcgis(layer, fields, order="OBJECTID"):
    rows, off = [], 0
    while True:
        d = get(f"{layer}/query", where="1=1", outFields=fields, returnGeometry="false", orderByFields=order,
                resultOffset=off, resultRecordCount=4000, f="json")
        feats = d.get("features") or []
        rows += [dict(f["attributes"]) for f in feats]
        if len(feats) < 4000 and not d.get("exceededTransferLimit"):
            return rows
        off += len(feats)
        time.sleep(1)


TODAY = datetime.date.today().isoformat()
WAIVER = ("City of Minneapolis open data: 'To the extent possible under law, City of Minneapolis has waived all copyright and related "
          "or neighboring rights to Open Data.' GIS data for reference only, no warranty.")
meta = {"minneapolis": {"name": "City of Minneapolis: Food Inspections (Health Department)", "url": f"{BASE}/Food_Inspections/FeatureServer/0",
                        "item": "https://www.arcgis.com/home/item.html?id=4eea8bf452e34f8c9d9ac07c54c0b4ab", "fetched": TODAY, "terms": WAIVER,
                        "cadence": "weekly (Fridays)"},
        "minneapolis_liquor": {"name": "City of Minneapolis: On-Sale Liquor Licenses", "url": f"{BASE}/On_Sale_Liquor/FeatureServer/0",
                               "item": "https://www.arcgis.com/home/item.html?id=5042131de56d44749f6e43c0b5738b21", "fetched": TODAY,
                               "terms": WAIVER, "cadence": "monthly (last Friday)"}}
insp = arcgis(f"{BASE}/Food_Inspections/FeatureServer/0",
              "OBJECTID,HealthFacilityIDNumber,FacilityCategory,BusinessName,RiskLevel,FullAddress,ZipCode,InspectionType,DateOfInspection,"
              "InspectionIDNumber,ViolationPriority,ViolationPoints,InspectionScore,ViolationIDNumber,APN,Latitude,Longitude")
time.sleep(1)
liq = arcgis(f"{BASE}/On_Sale_Liquor/FeatureServer/0",
             "OBJECTID,apn,licenseNumber,licenseType,licenseStatus,liquorType,issueDate,expirationDate,licenseName,address,endorsements,lat,long,lastUpdateDate")
json.dump(insp, open(os.path.join(OUT, "minneapolis", "inspections.json"), "w"))
json.dump(liq, open(os.path.join(OUT, "minneapolis", "liquor.json"), "w"))
json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
print("Minneapolis inspection rows:", len(insp), "| inspections:", len({r["InspectionIDNumber"] for r in insp}),
      "| facilities:", len({r["HealthFacilityIDNumber"] for r in insp}), "| on-sale liquor licenses:", len(liq))
