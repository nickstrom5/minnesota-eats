"""Download the Overture Maps extracts that minnesota.py reads -> data/mn/

- overture_mn_bbox.parquet     every place in Minnesota's bounding box (name, category, address, point)
- overture_mn_sources.parquet  which datasets each Minnesota eating/drinking listing came from (Meta, Foursquare, ...)
- mn_shapes.json               simplified state and county outlines for the map
- mn_state_detail.geojson      the state outline at full detail, for the in-state test

Reads the public Overture bucket over S3 with DuckDB (no account needed). Ported from va-eats/pipeline/fetch_overture.py.
Minnesota: land division areas; the "counties" are its 87. The script checks the towns on its lines (the Red River's twin cities,
the St. Croix and Mississippi river towns, Duluth and Superior, the Rainy River and the Northwest Angle) so a North Dakota, South
Dakota, Iowa, Wisconsin or Canadian listing stays out.
"""
import os, json, time
import duckdb
from shapely import wkb
from shapely.geometry import mapping, Polygon

RELEASE = "2026-10-21.0"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "mn")
# Minnesota (43.50°N–49.38°N, 89.49°W–97.24°W) plus a margin for the border towns (Fargo-Moorhead, Superior, Hudson, La Crosse)
BBOX = "bbox.xmin BETWEEN -97.4 AND -89.3 AND bbox.ymin BETWEEN 43.4 AND 49.5"
EAT = "('restaurant','casual_eatery','bar','fast_food_restaurant','coffee_shop','cafe','smoothie_juice_bar','brewery','food_court')"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
places = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*.parquet"

t = time.time()
if not os.path.exists(f"{OUT}/overture_mn_bbox.parquet"):
    con.execute(f"""
COPY (
  SELECT id, names.primary AS name, basic_category AS cat, taxonomy.primary AS tax, taxonomy.hierarchy AS hier, confidence,
         operating_status AS status, brand.names.primary AS brand, addresses[1].freeform AS street, addresses[1].locality AS city,
         addresses[1].postcode AS zip, addresses[1].region AS region, ST_Y(geometry) AS lat, ST_X(geometry) AS lon, websites[1] AS web,
         phones[1] AS phone
  FROM read_parquet('{places}', hive_partitioning=1) WHERE {BBOX}
) TO '{OUT}/overture_mn_bbox.parquet' (FORMAT PARQUET)""")
    print("places in bbox", round(time.time() - t), "s", flush=True)
if not os.path.exists(f"{OUT}/overture_mn_sources.parquet"):
    con.execute(f"""
COPY (
  SELECT id, list_transform(sources, lambda x: x.dataset) AS ds, list_transform(sources, lambda x: x.update_time) AS ut,
         list_transform(sources, lambda x: x.record_id) AS rid,
         len(socials) AS n_soc, len(websites) AS n_web, len(phones) AS n_ph
  FROM read_parquet('{places}', hive_partitioning=1)
  WHERE {BBOX} AND basic_category IN {EAT}
) TO '{OUT}/overture_mn_sources.parquet' (FORMAT PARQUET)""")
    print("sources", round(time.time() - t), "s", flush=True)

areas = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=divisions/type=division_area/*.parquet"
rows = con.execute(f"""
  SELECT subtype, names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-MN' AND subtype IN ('region', 'county') AND class = 'land'
    AND bbox.xmin > -97.5 AND bbox.xmax < -89.2 AND bbox.ymin > 43.3 AND bbox.ymax < 49.6""").fetchall()


def rings(geom, tol, min_area):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in polys]


out = {"state": None, "counties": []}
for sub, name, g in rows:
    geom = wkb.loads(bytes(g)).buffer(0)
    if sub == "region":
        json.dump(mapping(geom.simplify(0.0005, preserve_topology=True)), open(f"{OUT}/mn_state_detail.geojson", "w"))
        out["state"] = [[r] for r in rings(geom, 0.002, 0.000005)]
    else:
        out["counties"].append({"name": name, "c": rings(geom, 0.004, 0.00002)})
# full-detail county polygons for assigning each place to a county (not shipped)
json.dump({name: mapping(wkb.loads(bytes(g)).buffer(0).simplify(0.0003, preserve_topology=True))
           for sub, name, g in rows if sub == "county"}, open(f"{OUT}/mn_counties_detail.geojson", "w"))
json.dump(out, open(f"{OUT}/mn_shapes.json", "w"), separators=(",", ":"))
print("outlines: state", len(out["state"] or []), "rings +", len(out["counties"]), "counties;", round(time.time() - t), "s total")
# border towns: each must fall on the right side of the detailed state outline
from shapely.geometry import shape, Point
st = shape(json.load(open(f"{OUT}/mn_state_detail.geojson")))
for nm, lon, lat, want in [("Moorhead", -96.7676, 46.8738, True), ("East Grand Forks", -97.0245, 47.9300, True), ("Duluth", -92.1005, 46.7867, True),
                           ("Stillwater", -92.8060, 45.0564, True), ("International Falls", -93.4108, 48.6011, True), ("Grand Portage", -89.6848, 47.9636, True),
                           ("Winona", -91.6393, 44.0499, True), ("La Crescent", -91.3040, 43.8283, True), ("Breckenridge", -96.5878, 46.2633, True),
                           ("Warroad", -95.3144, 48.9053, True), ("Angle Inlet (Northwest Angle)", -95.0640, 49.3450, True), ("Luverne", -96.2128, 43.6541, True),
                           ("Fargo, ND", -96.7898, 46.8772, False), ("Grand Forks, ND", -97.0329, 47.9253, False), ("Superior, WI", -92.1041, 46.7208, False),
                           ("Hudson, WI", -92.7569, 44.9747, False), ("La Crosse, WI", -91.2396, 43.8014, False), ("Fort Frances, ON", -93.4002, 48.6089, False),
                           ("Sioux Falls, SD", -96.7311, 43.5446, False), ("Wahpeton, ND", -96.6059, 46.2652, False), ("Estherville, IA", -94.8328, 43.4016, False)]:
    ok = st.contains(Point(lon, lat))
    print(f"  {nm}: {'inside' if ok else 'outside'}{'' if ok == want else '  <-- WRONG'}")
print("counties:", len(out["counties"]), sorted(c["name"] for c in out["counties"]))

# the neighbours' land (North Dakota, South Dakota, Iowa, Wisconsin, Manitoba, Ontario): listings.py widens Minnesota's outline ~300 m
# for shores, but only where no neighbour's land is, so a Fargo, Superior or Hudson listing on the far side of the river stays out
nb = con.execute(f"""
  SELECT region, ST_AsWKB(geometry) FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE ((country = 'US' AND region IN ('US-ND', 'US-SD', 'US-IA', 'US-WI')) OR (country = 'CA' AND region IN ('CA-MB', 'CA-ON')))
    AND subtype = 'region' AND class = 'land'""").fetchall()
from shapely.ops import unary_union
from shapely.geometry import box
near = box(-97.5, 43.3, -89.2, 49.6)
nbg = unary_union([wkb.loads(bytes(g)).buffer(0).intersection(near) for _, g in nb])
json.dump(mapping(nbg.simplify(0.0002, preserve_topology=True)), open(f"{OUT}/mn_neighbors.geojson", "w"))
print("neighbours:", sorted(r for r, _ in nb))
