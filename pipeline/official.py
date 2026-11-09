"""Official records for Minnesota -> one table of licensed food businesses (playbook/12-sources.md).

Minnesota has no statewide inspection data and no statewide grade. The Department of Health (MDH) and about 30 delegated city and
county agencies inspect restaurants; only the City of Minneapolis publishes its inspections in bulk (open data, copyright waived):
its food facilities with a point, and every inspection since January 2023 with the City's own 0-100 score (100 minus points for each
violation: Priority 1 is 4 points, Priority 2 is 2, Priority 3 is 0; 91 or lower brings a follow-up). The score is shown as the City
publishes it, labeled official and dated, never turned into a grade. Minneapolis's on-sale liquor, wine and beer licenses (open
data, monthly) say which Minneapolis places pour; elsewhere "Serves alcohol" is unknown (DPS-AGE's lookup is search-only), never "no".

load() returns: jur, lic (our id), name, keys (name keys), addr, city, zip, num, street, lat, lon, kind, active, ltype, insp, biz.
"""
import os, re, json, datetime
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd
from common import norm_name, RAW, name_sim, _stems, GENERIC, canon_city

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TRL TRAIL WAY HWY CIR "
            "CIRCLE PLZ SQ MALL BND PASS XING RUN ROW WALK RDG LOOP FWY FREEWAY EXPY EXPRESSWAY PIKE PK PKE".split())


def road(a):
    """One spelling for numbered roads. Minnesota writes one road as 'Route 100', 'US 7', 'Rt 2', 'MN 100' or 'MN Route 100', so every
    numbered US or state route is 'SH n' (as in ri-eats); 'N INTERSTATE 95' = 'I-95'; 'COUNTY ROAD 5' = 'CR 5'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(US|MN|SR|SH|CR|I|IH|RT|RTE)-(\w)", r"\1 \2", a)
    a = re.sub(r"\b(?:INTERSTATE(?: HIGHWAY| HWY)?|IH|I H)\s*(?=\d)", "I ", a)
    a = re.sub(r"\b(?:US|U S)\s+(?:HIGHWAY|HWY)\b", "US", a)
    a = re.sub(r"\b(?:FARM[- ]TO[- ]MARKET(?: ROAD| RD)?|FARM (?:ROAD|RD)|F M)\b", "FM", a)
    a = re.sub(r"\b(?:RANCH[- ]TO[- ]MARKET(?: ROAD| RD)?|RANCH (?:ROAD|RD)|RR|RM)\b(?=\s*\d)", "RM", a)
    a = re.sub(r"\b(?:STATE (?:HIGHWAY|HWY|ROAD|RD|ROUTE|RTE)|SR|SH|VERMONT (?:ROUTE|RTE|HIGHWAY|HWY)|MN (?:ROUTE|RTE|RT|HIGHWAY|HWY)|MN|"
               r"US (?:ROUTE|RTE|RT)|US|ROUTE|RTE|RT|HWY)\b\.?(?=\s*\d)", "SH", a)
    a = re.sub(r"\b(?:COUNTY (?:HIGHWAY|HWY|ROAD|RD)|CO RD|CTY (?:HWY|RD)|CR)\b", "CR", a)
    a = re.sub(r"\bHIGHWAY\b", "HWY", a)
    return re.sub(r"\b(US|SH|CR|HWY|FM|RM|I) (\w+)\s*-\s*\w+", r"\1 \2", a)


ORD = {"FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH", "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH",
       "EIGHTH": "8TH", "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH"}


def street_key(a):
    """'2505 Monroe St' -> ('2505', 'MONROE'); '1000 OSAGE STREET' -> ('1000', 'OSAGE'); 'E Colfax Ave' keeps 'COLFAX'."""
    if not isinstance(a, str):
        return None, None
    a = re.sub(r"[.,#]", " ", road(a))
    # "20940-A North Frederick Ave": a hyphenated unit letter is part of the number (Maryland's Montgomery County wrote them so)
    m = re.match(r"^\s*(\d+)(?:-?[A-Z])?(?:\s*-\s*\d+[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    words = [w for w in m.group(2).split() if w]
    if len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(w)
    core = [ORD.get(w, w) for w in core]
    return m.group(1), " ".join(core[:3]) or None


def street_compat(a, b):
    """Same street, or one is a whole-word prefix of the other: Boulder's 2025 set sometimes truncates ("1206 CENTAUR" = Centaur Village Dr)."""
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a == b or a.startswith(b + " ") or b.startswith(a + " ")


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Monroe St' -> {'2505'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        v = re.sub(r"\s*\((?:MOBILE|MOBILE UNIT|COMMISSARY|CATERING|SPECIAL EVENT|SPEC EVENT|TEMP(?:ORARY)? EVENT|CP|INSIDE [^)]*)\)\s*$", "", v, flags=re.I)
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out


META = json.load(open(os.path.join(OFF, "meta.json"))) if os.path.exists(os.path.join(OFF, "meta.json")) else {}
LIST_DATE = (META.get("minneapolis") or {}).get("fetched")   # the day we read the City's feed
# Reports post within 7 business days of an inspection: anything in the last 10 days before the fetch may be incomplete, so the
# records run "through" 10 days before it and later inspections are left out until the next run
THROUGH = ((datetime.date.fromisoformat(LIST_DATE) - datetime.timedelta(days=10)).isoformat() if LIST_DATE else None)
# the City's page that explains its scores and links its inspection lookup (the lookup dashboard can pop a sign-in box)
MPLS_PAGE = "https://www.minneapolismn.gov/business-services/business-assistance/run/food-safety/health-inspection-reports/"
# MDH's page on who inspects where (MDH and the delegated agencies); MDH posts no reports online
INSPECTIONS_URL = "https://www.health.state.mn.us/communities/environment/food/license/index.html"
ONPREM_T = ("Minneapolis on-sale liquor license", "Minneapolis on-sale wine license", "Minneapolis on-sale beer license")
MAKER_T = ("Minneapolis brewery taproom license", "Minneapolis distillery cocktail room license")
LTYPE = {"BLLiquor": ONPREM_T[0], "BLWine": ONPREM_T[1], "BLBeer": ONPREM_T[2], "BLBrewery": MAKER_T[0], "BLDistill": MAKER_T[1]}
DRINKS = {"BLLiquor": ["beer", "wine", "liquor"], "BLWine": ["wine", "beer"], "BLBeer": ["beer"], "BLBrewery": ["beer"], "BLDistill": ["liquor"]}


def score_text(sc):
    """The City's score as shown: '96 of 100'."""
    return f"{int(sc)} of 100"


# every score 0..100 as text, in order: the app indexes results by position
RESULTS = tuple(score_text(x) for x in range(100, -1, -1))


def liq_kind(t):
    """A license type as shown -> on-premises or retail (Minneapolis's list is on-sale only)."""
    if not isinstance(t, str):
        return None
    return "onprem" if t in ONPREM_T or t in MAKER_T else "retail" if "off-sale" in t else None


COLUMNS = ["jur", "lic", "name", "dba", "holder", "keys", "addr", "city", "zip", "num", "street", "lat", "lon", "kind", "active", "ltype",
           "insp", "issued", "biz", "drinks", "county"]


def _zip(z):
    z = re.sub(r"\D", "", str(z or ""))
    return z[:5] if len(z) >= 5 else ""


def _addr(a):
    """'2790 VETERANS MEMORIAL BLVD STE 130' -> '2790 Veterans Memorial Blvd Ste 130'."""
    a = re.sub(r"\s+", " ", a or "").strip()
    return re.sub(r"\b([A-Z]{2,})\b", lambda m: m.group(1).title(), a)


def _city(c):
    return canon_city(" ".join(w.capitalize() for w in str(c or "").split())) if isinstance(c, str) and c.strip() else None


def _ms(v):
    """An ArcGIS date (epoch milliseconds, UTC) -> YYYY-MM-DD in Minnesota's time (the district's own day)."""
    if not isinstance(v, (int, float)):
        return None
    d = datetime.datetime.fromtimestamp(v / 1000, datetime.timezone.utc) - datetime.timedelta(hours=4)
    return d.date().isoformat()


CT = ZoneInfo("America/Chicago")


def _ms(v):
    """An ArcGIS date (epoch milliseconds, UTC) -> YYYY-MM-DD in Minneapolis's time (the City's own day)."""
    if not isinstance(v, (int, float)):
        return None
    return datetime.datetime.fromtimestamp(v / 1000, datetime.timezone.utc).astimezone(CT).date().isoformat()


def _mpls_addr(a):
    """'3804 GRAND AVE S' -> '3804 Grand Ave S'; '1404 QUINCY ST NE' -> '1404 Quincy St NE'."""
    a = _addr(a)
    return re.sub(r"\b(Ne|Nw|Se|Sw)\b", lambda m: m.group(1).upper(), a)


# the City's facility categories that are a place to go out to eat; the rest (institutions, groceries, board-and-lodging homes, meat
# markets, caterers, food shelves, wholesalers) stay out. Trucks and carts are mobile.
MPLS_FOOD = {"RESTAURANT"}
MPLS_TRUCK = {"FOOD TRUCK", "FOOD CART", "LIMITED MOBILE"}


def load_minneapolis():
    R = json.load(open(os.path.join(OFF, "minneapolis", "inspections.json")))
    insp, fac = {}, {}
    for r in R:
        iid, fid = r.get("InspectionIDNumber"), r.get("HealthFacilityIDNumber")
        if not iid or not fid:
            continue
        d = _ms(r.get("DateOfInspection"))
        if not d or (THROUGH and d > THROUGH):
            continue
        v = insp.setdefault(iid, {"fid": fid, "d": d, "type": r.get("InspectionType"), "score": r.get("InspectionScore"), "p1": set(), "rows": []})
        if r.get("ViolationPriority") == "Priority1" and r.get("ViolationIDNumber"):
            v["p1"].add(r["ViolationIDNumber"])
        f = fac.setdefault(fid, [])
        f.append(r)
    by = {}
    for iid, v in insp.items():
        if isinstance(v["score"], (int, float)):
            by.setdefault(v["fid"], []).append([v["d"], score_text(v["score"]), v["type"], iid])
    rows = []
    for fid, rs in fac.items():
        rs.sort(key=lambda r: r.get("DateOfInspection") or 0, reverse=True)
        last = rs[0]
        name = re.sub(r"\s+", " ", last.get("BusinessName") or "").strip()
        cat = (last.get("FacilityCategory") or "").strip()
        kind = "food" if cat in MPLS_FOOD else "truck" if cat in MPLS_TRUCK else "other"
        addr = _mpls_addr(last.get("FullAddress"))
        num, st = street_key(addr)
        la = next((r["Latitude"] for r in rs if r.get("Latitude")), None)
        lo = next((r["Longitude"] for r in rs if r.get("Longitude")), None)
        visits = sorted(by.get(fid, []), key=lambda v: v[0], reverse=True)
        latest = visits[0][0] if visits else None
        rows.append({"jur": "minneapolis", "lic": f"mpls-{fid}", "name": name, "dba": name, "holder": None, "keys": _names(name),
                     "addr": addr, "city": "Minneapolis", "zip": _zip(last.get("ZipCode")), "num": num, "street": st, "lat": la, "lon": lo,
                     "kind": kind, "active": bool(latest) and latest >= "2025-03-01",
                     "ltype": "Minneapolis food license (" + (cat.title() or "unknown") + ")", "insp": visits, "issued": None,
                     "drinks": None, "county": None, "apn": last.get("APN")})
    return rows


def load_mpls_liquor():
    rows = []
    for r in json.load(open(os.path.join(OFF, "minneapolis", "liquor.json"))):
        t = r.get("licenseType")
        if t not in LTYPE or r.get("licenseStatus") not in ("Approved", "Active"):   # "Pending" isn't live
            continue
        name = re.sub(r"\s+", " ", r.get("licenseName") or "").strip()
        addr = _mpls_addr(r.get("address"))
        num, st = street_key(addr)
        rows.append({"jur": "mpls_liquor", "lic": "mplsliq-" + (r.get("licenseNumber") or str(r.get("OBJECTID"))), "name": name, "dba": name,
                     "holder": None, "keys": _names(name), "addr": addr, "city": "Minneapolis", "zip": "", "num": num, "street": st,
                     "lat": r.get("lat"), "lon": r.get("long"), "kind": "food", "active": True, "ltype": LTYPE[t], "insp": [],
                     "issued": _ms(r.get("issueDate")), "drinks": DRINKS[t], "county": None, "apn": r.get("apn")})
    return rows


def load():
    """Minneapolis's food facilities (with the City's inspections) and its on-sale alcohol licenses, joined by business."""
    rows = []
    if os.path.exists(os.path.join(OFF, "minneapolis", "inspections.json")):
        rows += load_minneapolis()
    if os.path.exists(os.path.join(OFF, "minneapolis", "liquor.json")):
        rows += load_mpls_liquor()
    df = pd.DataFrame(rows) if rows else pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS + ["apn"]})
    for c_ in COLUMNS:
        if c_ not in df.columns:
            df[c_] = None
    df["lat"] = df["lat"].astype(float); df["lon"] = df["lon"].astype(float); df["active"] = df["active"].astype(bool)
    df["biz"] = np.arange(len(df))

    def join(a, b):
        old, new = df.at[b, "biz"], df.at[a, "biz"]
        if old != new:
            df.loc[df.biz == old, "biz"] = new
    # a liquor license joins the active Minneapolis restaurant at its address (same house number and street, or the same parcel)
    # when the names agree or share a distinctive word: one address can hold several businesses (a food hall, a hotel)
    food = df[(df.jur == "minneapolis") & df.kind.eq("food") & df.active & df.num.notna()]
    at = food.groupby("num").groups
    joined = 0
    for i in df.index[df.jur == "mpls_liquor"]:
        cand = [j for j in at.get(df.at[i, "num"], []) if street_compat(df.at[i, "street"], df.at[j, "street"])
                or (df.at[i, "apn"] and df.at[i, "apn"] == df.at[j, "apn"])]
        ki = df.at[i, "keys"] or []
        good = [j for j in cand if any(name_sim(p, q) >= 80 or ((_stems(p) - GENERIC) & (_stems(q) - GENERIC)) for p in ki for q in df.at[j, "keys"] or [])]
        if len({df.at[j, "biz"] for j in good}) == 1:
            join(good[0], i); joined += 1
    print("Minneapolis liquor licenses joined to a food facility at their address:", joined, "of", int((df.jur == "mpls_liquor").sum()))
    return df
