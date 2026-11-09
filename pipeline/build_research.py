"""Writes data/research/app/*.json (hand-checked Minnesota guides), data/research/michelin.json, jbf.json and closed.json from the
compact lists below. Ported from va-eats/pipeline/build_research.py.

Each entry cites the pages that name it, read on 2026-11-06: dated articles (Minnesota Monthly, Tasting Table, Sahan Journal, Racket,
MPR News) and official visitor-bureau pages and listings (Visit Saint Paul, Visit Duluth, the Iron Range Tourism Bureau, the North Shore
Visitor guide), each current in 2026. Explore Minnesota and the Star Tribune answer scripts with a bot check, and Mpls.St.Paul Magazine,
Eater Twin Cities, Pioneer Press, MinnPost and the Duluth News Tribune disallow Claude in robots.txt, so none is cited.
The address comes from the map listing we already hold for that name in that town (site/minnesota.json); a name that isn't found exactly
once in its town (or at the street number given) is left out and listed in data/research/app/LEADS.md. A place the map data doesn't
show as a place to eat is added only with the street address its listing gives (ADDR).
Usage: ../.venv/bin/python build_research.py   (then minnesota.py)"""
import json, os, re
from brands import brand_of
from common import norm_name
ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "data", "research")
d = json.load(open(os.path.join(ROOT, "site", "minnesota.json")))
C, M = d["cols"], d["meta"]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("'", "").replace("’", ""))).strip()

# each dated on its face, or an official visitor-bureau page or listing current in 2026 (read 2026-11-06)
MM = "https://www.minnesotamonthly.com/"
DETOURS = MM + "general/delicious-dining-detours/"                                            # 2026-04-03
BRACKET = MM + "burger-bracket-challenge/"                                                    # 2026 participants
ICONIC = MM + "food-drink/minnesotas-most-iconic-foods/"                                      # 2023-06-15 (founding years)
LUCY18 = MM + "food-drink/the-best-juicy-lucy-did-bon-apptit-get-it-right/"                   # 2018-09-13 (which spots serve one)
TT_BURGER = "https://www.tastingtable.com/2240937/best-cheeseburger-every-us-state/"           # 2026-08-23
TT_LUCY = "https://www.tastingtable.com/1297407/midwest-juicy-lucy-reinvented-traditional-cheeseburgers/"   # 2023-05-29
TT_KRAM = "https://www.tastingtable.com/2088189/kramarczuk-sausage-company-old-world-deli-minneapolis/"     # 2026-02-08
TT_OLDREST = "https://www.tastingtable.com/1975409/oldest-restaurant-every-state-still-open/"  # 2025-09-23
TT_OLDBAR = "https://www.tastingtable.com/1786324/oldest-bar-every-state/"                    # 2025-02-17
VSP = "https://www.visitsaintpaul.com/blog/"
VSP_HMONG = VSP + "hmong-history-and-saint-paul/"                                             # Visit Saint Paul (© 2026)
VSP_SEA = VSP + "dine-at-these-vietnamese-restaurants-in-saint-paul/"                         # Visit Saint Paul (© 2026)
VSP_HALLS = VSP + "food-halls-and-markets/"                                                   # Visit Saint Paul (© 2026; names 2026's best new restaurant)
VSP_ICONS = VSP + "saint-paul-restaurant-icons/"                                              # Visit Saint Paul (© 2026)
SAHAN = "https://sahanjournal.com/business-work/afro-deli-south-minneapolis-martiya-restaurant/"   # 2026-11-05
DLH = "https://visitduluth.com/food-drink/restaurants/"                                       # Visit Duluth listings (2025-26)
DLH_COZY = "https://visitduluth.com/blog/warm-up-with-cozy-comfort-food-in-duluth/"           # updated 2026-09-21
NSV = "https://northshorevisitor.com/"
NSV_61 = NSV + "restaurants/scenic-61/"                                                       # North Shore Visitor (events through Nov 2026)
NSV_TH = NSV + "restaurants/two-harbors/"
NSV_DOCK = NSV + "business/dockside-fish-market/"
IRB = "https://ironrange.org/"
IRB_FOODS = IRB + "three-foods-you-need-to-try-on-the-range-and-where-to-find-them/"         # Iron Range Tourism Bureau (© 2026)
IRB_SUNRISE = IRB + "listings/sunrise-bakery/"
MPR_MICKEYS = "https://www.mprnews.org/story/2024/10/03/downtown-st-pauls-landmark-mickeys-diner-is-back-open-for-business"   # 2024-10-03 (reopening)
RACKET_MAR26 = "https://racketmn.com/a-bunch-of-new-breweries-and-sports-bars-are-in-the-works-plus-a-bait-shop"   # 2026-03-31
JBF26 = "https://www.jamesbeard.org/stories/james-beard-award-semifinalists-2026"                   # 2026-01-21
JBF26N = "https://www.jamesbeard.org/stories/james-beard-awards-restaurant-and-chef-nominees-2026"  # 2026-03-31
JBF25 = "https://www.jamesbeard.org/stories/the-2025-james-beard-award-semifinalists"               # 2025-01-22
JBF25N = "https://www.jamesbeard.org/stories/2025-james-beard-awards-restaurant-and-chef-nominees"  # 2025-04-02
JBF25W = "https://www.jamesbeard.org/stories/the-2025-james-beard-award-winners"                    # 2025-06-16
JBF24W = "https://www.jamesbeard.org/stories/the-2024-james-beard-award-winners"                    # 2024-06-03
JBF22W = "https://www.jamesbeard.org/stories/the-2022-james-beard-award-winners"                    # 2022-05-09
ARCH = "https://archive.jamesbeard.org/awards/search?categories%5BRestaurant+=&+Chef%5D=1&ranks%5BWinner%5D=1&year=&keyword="
ARCH_MPLS, ARCH_DLH = ARCH + "Minneapolis", ARCH + "Duluth"
ARCH_ALS = "https://archive.jamesbeard.org/chef/als-breakfast-2"
SP_, MPLS = "St. Paul", "Minneapolis"

# (name as the source writes it or as our listing spells it, town as our listing has it, street number to pick the location (or
# None), note, founded, founded_note, [sources])
GUIDES = {
 "juicy lucy": [   # the cheese-stuffed burger; Matt's Bar and the 5-8 Club both claim the original
  ("Matt's Bar and Grill", MPLS, "3500", "Matt's Bar, where the Jucy Lucy (spelled without the i) is believed to have been invented: American cheese sealed inside the patty.",
   1954, "Minnesota Monthly (2023): Matt's Bar opened in 1954.", [TT_BURGER, ICONIC, TT_LUCY]),
  ("5-8 Club", MPLS, "5800", "The other claimant to the original Juicy Lucy, opened as a speakeasy, with more burger options than Matt's.",
   1928, "Minnesota Monthly (2023): the 5-8 Club opened as a speakeasy in 1928.", [ICONIC, TT_LUCY, BRACKET]),
  ("Blue Door Pub", SP_, "1811", "The Blue Door Pub on Selby Avenue, Jason DeRusha's top Juicy Lucy pick in Minnesota Monthly (2018).",
   None, None, [BRACKET, LUCY18]),
  ("Groveland Tap", SP_, "1834", "A Mac-Groveland tap with a long list of beers and a well-seared Juicy Lucy.", None, None, [BRACKET, LUCY18]),
  ("The Nook", SP_, "492", "A bar with a bowling alley downstairs, known for its melty, well-seasoned Juicy Lucy.", None, None, [BRACKET, LUCY18])],
 "walleye supper": [   # supper clubs and the lake-country walleye they serve
  ("Bar Harbor Supper Club", "Lake Shore", "8164", "A supper club and chophouse in Lake Shore, known for its pistachio-stuffed walleye.",
   None, None, [DETOURS]),
  ("Lonesome Pine Restaurant & Bar", "Deerwood", "13726", "An old-school supper club on Bay Lake.", None, None, [DETOURS]),
  ("The Pines Restaurant", "Grand Rapids", "12", "Farm-to-table cooking with walleye, wild rice and halibut.", None, None, [DETOURS, JBF26]),
  ("Birch's on the Lake Brewhouse & Supperclub", "Long Lake", "1310", "A brewhouse and supper club in Long Lake, in Minnesota Monthly's 2026 Burger Bracket.", None, None, [BRACKET])],
 "hmong southeast asian": [   # St. Paul's Hmong, Lao, Thai, Vietnamese and Cambodian kitchens (Visit Saint Paul)
  ("Hmongtown Marketplace", SP_, None, "An indoor-outdoor Hmong marketplace with more than 125 stores and 11 restaurants, known for stuffed chicken wings and papaya salad.",
   None, None, [VSP_HMONG, VSP_HALLS]),
  ("Hmong Village Shopping Center", SP_, None, "An East Side market with more than 20 food stalls, Hmong fusion alongside the traditional staples.",
   None, None, [VSP_HMONG, VSP_HALLS]),
  ("Hoa Bien Vietnamese Restaurant", SP_, "1105", "Frogtown's Vietnamese kitchen, serving traditional dishes since 1978.", None, None, [VSP_SEA]),
  ("Trung Nam French Bakery", SP_, "739", "A French bakery with Vietnamese flair on University Avenue in Frogtown, serving banh mi.", None, None, [VSP_SEA]),
  ("Bangkok Thai Deli", SP_, "333", "A no-frills Thai deli in the Little Mekong stretch of University Avenue.", None, None, [VSP_SEA]),
  ("Ruam Mit", SP_, "367", "Family-owned for more than 35 years, cooking Thai and Lao recipes downtown.", None, None, [VSP_SEA]),
  ("Sawatdee Saint Paul", SP_, "486", "Sawatdee, which Visit Saint Paul calls the first Thai restaurant in the five-state area, serving since the early 1980s.", None, None, [VSP_SEA]),
  ("Soul Lao", SP_, "2465", "A former food truck turned restaurant, cooking Laotian dishes.", None, None, [VSP_SEA])],
 "east african": [   # Somali and East African kitchens
  ("Afro Deli & Grill", MPLS, "720", "Abdirahman Kahin's Afro Deli, which developed the chapati wrap (one of its three Twin Cities locations).",
   None, None, [SAHAN, ICONIC]),
  ("Afro Deli & Grill", SP_, "5", "Afro Deli's downtown St. Paul location, home of the chapati wrap it developed.", None, None, [SAHAN, ICONIC]),
  ("Deg Deg Grill", MPLS, "912", "Sadiq Ali's Somali grill at the 24 Mall, open since 2009 (deg deg means \"quick\").", None, None, [SAHAN]),
  ("Deg Deg Grill Karmel Mall", MPLS, "2910", "Deg Deg Grill's kitchen in Karmel Mall, south Minneapolis.", None, None, [SAHAN]),
  ("Karibu Grocery & Deli", SP_, "719", "An East Side deli with East African and Afro-Mediterranean plates and halal take-and-bake meals.", None, None, [VSP_HALLS])],
 "north shore range": [   # North Shore smoked fish and pie, Iron Range potica and pasties
  ("Russ Kendall's Smokehouse", "Knife River", None, "Smoked lake trout, whitefish and salmon, plus jerky and sausage, on the North Shore's Scenic 61.",
   None, None, [NSV_61]),
  ("Lou's Fish House", "Two Harbors", None, "Smoked fish, smoked shrimp and cheese by the highway, with hard-scooped ice cream.", None, None, [NSV_TH]),
  ("Betty's Pies", "Two Harbors", "1633", "A North Shore pie café that began as a fish stand in 1957 and added pies in 1958.", None, None, [NSV_TH]),
  ("The Fisherman's Daughter", "Grand Marais", "418", "At Dockside Fish Market: fresh and smoked wild-caught Lake Superior fish by the pound, fish and chips and a deli.",
   None, None, [NSV_DOCK]),
  ("Angry Trout Cafe", "Grand Marais", "408", "Lake Superior fish served dock-to-table.", None, None, [DETOURS]),
  ("Northern Waters Smokehaus", "Duluth", "394", "Duluth's smoked-fish specialists, with smoked meats and a long list of sandwiches.", None, None, [DLH]),
  ("New Scenic Café", "Duluth", "5461", "A café on North Shore Drive with a changing menu and a garden setting.", None, None, [DLH, NSV_61]),
  ("Duluth Grill", "Duluth", "118", "Known for its banana cream pie.", None, None, [DLH_COZY, DLH]),
  ("Sunrise Bakery", "Hibbing", "2601", "The Iron Range bakery known for potica, a rolled dough filled with nuts and spices.", None, None, [IRB_SUNRISE, IRB_FOODS]),
  ("Pep's Bake Shop", "Virginia", None, "One of the Iron Range Tourism Bureau's picks for potica.", None, None, [IRB_FOODS]),
  ("Carlson's Pasty and Sausage Kitchen", "Biwabik", "113", "One of the Iron Range Tourism Bureau's picks for pasties.", None, None, [IRB_FOODS])],
 "classic counter": [   # Visit Saint Paul's icons and other long-running counters, delis and cafés
  ("Mickey's Diner", SP_, "36", "The 1939 dining car downtown, reopened in October 2024: hash browns, smashed burgers and shakes.",
   1939, "Visit Saint Paul: a dining car harkening back to 1939.", [VSP_ICONS, MPR_MICKEYS]),
  ("Boca Chica Restaurante Mexicano y Cantina", SP_, "11", "A family-run West Side Mexican restaurant since 1964, known for carnitas and enchiladas.",
   1964, "Visit Saint Paul: since 1964.", [VSP_ICONS]),
  ("El Burrito Mercado", SP_, "175", "The West Side's Mexican market since 1979, with a deli, restaurant and cantina.", None, None, [VSP_ICONS, VSP_HALLS]),
  ("Cecils Deli & Restaurant", SP_, "651", "Highland Park's deli for more than 70 years: pastrami on rye and matzo ball soup.", None, None, [VSP_ICONS]),
  ("Cafe Latte", SP_, "850", "Grand Avenue's cafeteria-style comfort food for 40 years, with a pizza and wine bar.", None, None, [VSP_ICONS]),
  ("DeGidio's Restaurant & Bar", SP_, "425", "Red-sauce pasta and the old-school hot dago, with roots going back to Prohibition.", None, None, [VSP_ICONS]),
  ("Yarusso Bros Italian Restaurant", SP_, "635", "Payne Avenue Italian from a family that opened its first tavern in 1932, with early bocce lanes.", None, None, [VSP_ICONS]),
  ("Mancini's Char House", SP_, "531", "West Seventh's steakhouse with a 1970s bar and the pickle plate.", None, None, [VSP_ICONS]),
  ("Sweeney's Saloon", SP_, "96", "A neighborhood pub since 1979 with an Art Deco bar, wings and hard-shell tacos.", None, None, [VSP_ICONS]),
  ("W.A. Frost & Company", SP_, "374", "New American dining in Cathedral Hill since 1975, with a shaded patio.", None, None, [VSP_ICONS]),
  ("Moscow on the Hill", SP_, "371", "Russian and Ukrainian comfort food since 1994: stroganoff and pelmeni.", None, None, [VSP_ICONS]),
  ("Kramarczuk's Sausage", MPLS, "215", "An old-world Ukrainian deli, bakery and cafeteria at the same address since 1967: house sausages, pierogi and cabbage rolls.",
   None, None, [TT_KRAM]),
  ("Val's Rapid Service", "St. Cloud", "628", "Val's: cheap burgers (cheeseburgers under $2.50) and a drive-up chocolate shake.", None, None, [DETOURS]),
  ("Dan's Bar and Grill", "Hampton", "8485", "A long-running burger spot in New Trier; the Buddha burger has two cheeses and mushrooms.", None, None, [DETOURS]),
  ("The Hubbell House", "Mantorville", "502", "Tasting Table names it Minnesota's oldest restaurant still open: the stagecoach-era hotel Frank Mantor built in Mantorville.",
   None, None, [TT_OLDREST])],
 "oldest": [
  ("Neumanns Bar", "North St. Paul", "2531", "Minnesota's oldest bar, with the Prohibition-era speakeasy upstairs still there to see.",
   1887, "Tasting Table's oldest bar in every state (February 2025): Neumann's Bar, open since 1887.", [TT_OLDBAR]),
  ("Pickwick Restaurant and Pub", "Duluth", "508", "Duluth's landmark restaurant and full bar on East Superior Street, serving pub food; an America's Classic.",
   1914, "Visit Duluth: an area landmark since 1914.", [DLH, ARCH_DLH])],
}
# street addresses for places the map data doesn't show as a place to eat: from their own listing (or the map listing that our keep
# rule set aside)
ADDR = {("Hmongtown Marketplace", SP_): "217 Como Ave", ("Hmong Village Shopping Center", SP_): "1001 Johnson Pkwy",
        ("Russ Kendall's Smokehouse", "Knife River"): "149 Scenic Dr", ("Lou's Fish House", "Two Harbors"): "1319 MN-61",
        ("Pep's Bake Shop", "Virginia"): "318 Chestnut St", ("Blue Door Pub", SP_): "1811 Selby Ave"}
CUISINE = {("Hmongtown Marketplace", SP_): "Southeast Asian", ("Hmong Village Shopping Center", SP_): "Southeast Asian",
           ("Russ Kendall's Smokehouse", "Knife River"): "Seafood", ("Lou's Fish House", "Two Harbors"): "Seafood",
           ("Pep's Bake Shop", "Virginia"): "Bakery & Sweets", ("Blue Door Pub", SP_): "Burgers", ("Matt's Bar and Grill", MPLS): "Burgers",
           ("5-8 Club", MPLS): "Burgers", ("Groveland Tap", SP_): "Burgers", ("The Nook", SP_): "Burgers",
           ("Soul Lao", SP_): "Southeast Asian", ("Ruam Mit", SP_): "Thai",
           ("Afro Deli & Grill", MPLS): "African", ("Afro Deli & Grill", SP_): "African", ("Deg Deg Grill", MPLS): "African",
           ("Deg Deg Grill Karmel Mall", MPLS): "African", ("Karibu Grocery & Deli", SP_): "African", ("Kramarczuk's Sausage", MPLS): "European"}
KINDS = {k: [k] for k in ("juicy lucy", "walleye supper", "hmong southeast asian", "east african", "north shore range", "classic counter", "oldest")}
KINDS["oldest"] = ["oldest"]

# MICHELIN: no guide covers Minnesota (the 2026 US guides cover select states and cities; none in Minnesota)
MICHELIN = []
MI_MATCH = {}
MI_UT = None
# James Beard (facts with sources): Minnesota's wins named on jamesbeard.org pages we read (the archive's winner search for Minneapolis
# and Duluth, and the 2022-25 winner pages), and its 2025-26 nominees (finalists) and semifinalists. No Minnesota winner in 2026.
MID = "Best Chef: Midwest"
JBF = [{"name": "Al's Breakfast", "city": MPLS, "honors": ["America's Classics 2004"], "sources": [ARCH_ALS, ARCH_MPLS]},
       {"name": "Pickwick Restaurant and Pub", "city": "Duluth", "honors": ["America's Classics 2007"], "sources": [ARCH_DLH], "match_names": ["PICKWICK"]},
       {"name": "Kramarczuk's Sausage", "city": MPLS, "honors": ["America's Classics 2013"], "sources": [ARCH_MPLS, TT_KRAM], "match_names": ["KRAMARCZUKS"]},
       {"name": "Alma", "city": MPLS, "address": "528 University Ave SE",
        "honors": [f"{MID} winner 2010 (Alex Roberts)", "Outstanding Chef semifinalist 2026 (Alex Roberts)"], "sources": [ARCH_MPLS, JBF26]},
       {"name": "112 Eatery", "city": MPLS, "honors": [f"{MID} winner 2011 (Isaac Becker)"], "sources": [ARCH_MPLS]},
       {"name": "Spoon and Stable", "city": MPLS, "honors": [f"{MID} winner 2018 (Gavin Kaysen)", "Outstanding Restaurant semifinalist 2025"],
        "sources": [ARCH_MPLS, JBF25]},
       {"name": "Indígena by Owamni", "city": MPLS, "address": "806 S 2nd St",
        "honors": ["Best New Restaurant winner 2022 (as Owamni, before its 2026 move to the Guthrie Theater)"], "sources": [JBF22W, RACKET_MAR26],
        "match_names": ["INDIGENA BY OWAMNI", "INDIGENA"]},
       {"name": "Hai Hai", "city": MPLS, "honors": [f"{MID} winner 2024 (Christina Nguyen)"], "sources": [JBF24W, ARCH_MPLS]},
       {"name": "Bûcheron", "city": MPLS, "address": "4257 Nicollet Ave", "honors": ["Best New Restaurant winner 2025"], "sources": [JBF25W, JBF25N, JBF25],
        "match_names": ["BUCHERON"]},
       {"name": "Myriel", "city": SP_, "honors": [f"{MID} winner 2025 (Karyn Tomlinson)"], "sources": [JBF25W, JBF25N, JBF25]},
       {"name": "Kado no Mise", "city": MPLS, "honors": [f"{MID} finalist 2026 and 2025 (Shigeyuki Furukawa)"], "sources": [JBF26N, JBF25N, JBF26, JBF25]},
       {"name": "Diane's Place", "city": MPLS, "honors": [f"{MID} finalist 2025, semifinalist 2026 (Diane Moua)"], "sources": [JBF25N, JBF26, JBF25]},
       {"name": "Bar Brava", "city": MPLS, "honors": ["Outstanding Wine and Other Beverages Program finalist 2025"], "sources": [JBF25N, JBF25]},
       {"name": "Khaluna", "city": MPLS, "honors": ["Outstanding Chef semifinalist 2026 and 2025 (Ann Ahmed)"], "sources": [JBF26, JBF25], "match_names": ["KHALUNA"]},
       {"name": "Bar La Grassa", "city": MPLS, "honors": ["Outstanding Restaurant semifinalist 2026"], "sources": [JBF26]},
       {"name": "The Pines Restaurant", "city": "Grand Rapids", "honors": ["Emerging Chef semifinalist 2026 (Kyle Lussier)"], "sources": [JBF26]},
       {"name": "Joan's in the Park", "city": SP_, "honors": ["Outstanding Hospitality semifinalist 2026"], "sources": [JBF26]},
       {"name": "Oro by Nixta", "city": MPLS, "honors": [f"{MID} semifinalist 2026 (Gustavo and Kate Romero)"], "sources": [JBF26]},
       {"name": "Vinai", "city": MPLS, "honors": [f"{MID} semifinalist 2026 (Yia Vang)", "Best New Restaurant semifinalist 2025"], "sources": [JBF26, JBF25]},
       {"name": "Mucci's Italian", "city": SP_, "honors": ["Outstanding Hospitality semifinalist 2025"], "sources": [JBF25], "match_names": ["MUCCIS"]},
       {"name": "Hyacinth", "city": SP_, "honors": [f"{MID} semifinalist 2025 (Abraham Gessesse)"], "sources": [JBF25]},
       {"name": "Krewe Restaurant", "city": "St. Joseph", "honors": [f"{MID} semifinalist 2025 (Mateo Mackbee)"], "sources": [JBF25], "match_names": ["KREWE"]}]
# closed or moved, each with a source
CLOSED = [{"name": "Owamni by The Sioux Chef", "address": "420 S 1st St", "city": MPLS, "match_names": ["OWAMNI", "OWAMNI BY THE SIOUX CHEF"],
           "closed_reason": "Moved in spring 2026 into the Guthrie Theater as Indígena by Owamni (806 S 2nd St); the Water Works pavilion location "
                            "stayed open through the end of April.", "sources": [RACKET_MAR26]}]


def key(s):
    """The name key without a leading "the": "Varsity" is our "The Varsity"."""
    return re.sub(r"^the ", "", norm(s))


def find(name, town, num):
    k = key(name)
    hits = [i for i, n in enumerate(C["name"]) if C["city"][i] is not None and M["cities"][C["city"][i]] == town
            and (key(n) == k or key(n).startswith(k + " ") or k.startswith(key(n) + " ") or key(n).replace(" ", "") == k.replace(" ", "")
                 or (key(n).split()[:2] == k.split()[:2] and len(k.split()) >= 2))]
    if num:
        hits = [i for i in hits if (C["addr"][i] or "").split(" ")[0] == num]
    return hits


leads, n_out = [], {}
for kind, rows in GUIDES.items():
    out = []
    for name, town, num, note, founded, fnote, srcs in rows:
        hits = find(name, town, num)
        if not hits and (name, town) in ADDR:
            out.append({"name": name, "address": ADDR[(name, town)], "city": town, "zip": None, "kinds": KINDS[kind], "dishes": [], "note": note,
                        "founded": founded, "founded_note": fnote, "website": None, "open": True, "evidence_date": "2026-10",
                        "sources": srcs, "match_names": []} | ({"cuisine": CUISINE[(name, town)]} if (name, town) in CUISINE else {}))
            continue
        if len(hits) != 1:
            leads.append(f"- {kind}: {name} ({town}{', ' + num if num else ''}) — {len(hits)} matches in our data; not added"); continue
        i = hits[0]
        out.append({"name": C["name"][i], "address": C["addr"][i], "city": town, "zip": str(C["zip"][i]) if C["zip"][i] else None,
                    "kinds": KINDS[kind], "dishes": [], "note": note, "founded": founded, "founded_note": fnote, "website": None, "open": True,
                    "evidence_date": "2026-10", "sources": srcs, "match_names": [name.upper()] if norm(name) != norm(C["name"][i]) else []})
        if brand_of(norm_name(name)):   # a chain shows under its own spelling at every branch, whatever the listing says
            out[-1]["display"] = name
        if (name, town) in CUISINE:
            out[-1]["cuisine"] = CUISINE[(name, town)]
    fn = re.sub(r"[^a-z]+", "_", kind).strip("_")
    json.dump(out, open(f"{R}/app/{fn}.json", "w"), indent=1, ensure_ascii=False)
    n_out[kind] = len(out)

MI_ADDR = {}
json.dump({"restaurants": [{"name": n, "address": MI_ADDR.get(n), "city": t, "zip": None, "distinction": dist, "cuisine": cu, "green_star": False,
                             "michelin_url": MI_UT, "sources": [MI_UT], "match_names": [x.upper() for x in MI_MATCH.get(n, [])], "open": True}
                            for n, t, dist, cu in MICHELIN]}, open(f"{R}/michelin.json", "w"), indent=1, ensure_ascii=False)
json.dump([dict({"address": None}, **j, zip=None, open=True) for j in JBF], open(f"{R}/jbf.json", "w"), indent=1, ensure_ascii=False)
json.dump(CLOSED, open(f"{R}/closed.json", "w"), indent=1, ensure_ascii=False)
open(f"{R}/app/LEADS.md", "w").write("# Minnesota research leads (not yet verified)\n\nWritten by pipeline/build_research.py.\n\n" + "\n".join(leads) + """

## Waiting for a source we may use, or for the map data
- Juicy Lucys: Matt's Bar has no 2025-26 page we could read besides Tasting Table (Bring Me The News answers 403); the Blue Door Pub
  Longfellow and the 5-8 Grill & Bar in Champlin are named only as "Blue Door" / "5-8" in the 2026 bracket.
- Walleye and supper clubs: Mr. Paul's Supper Club (Edina), the Creekside Supper Club (Minneapolis, Racket 2022), Lord Fletcher's (Spring
  Park), The Pickled Loon (Grand Rapids), Wiederholt's (Hastings/Miesville) and J.D. Hoyt's have no 2025-26 page we could read; Minnesota
  Monthly's 2025 fish-fry list and KARE 11's fish-fry roundups answer 403 to the fetcher. Apostle Supper Club (St. Paul) closed.
- Hmong and Southeast Asian: On's Thai Kitchen (University Ave) isn't in our map data (only On's Thai Express on Cleveland Ave); Diane's
  Place, Vinai and Khâluna carry their James Beard honors but no page we read describes their cooking.
- East African: Martiya (Opportunity Crossing, Nicollet and Lake; Sahan Journal 2026-11-05), 7 Spices (Midtown Global Market), Wiilo
  (Karmel Mall) and Mamas Market & Deli (Little Africa Plaza) aren't in our map data.
- North Shore: the Rustic Inn Cafe's pies come from a 2017 article; the Tourist Center pasties in Hibbing aren't in our map data.
- Oldest: the Hubbell House's opening year isn't given by Tasting Table (only the 1854 land claim); Yarusso's 1932 tavern may not be
  its Payne Avenue address; Kramarczuk's (1954, at its address since 1967) and Betty's Pies (1957) are past the guide's 1960 line or not
  dated at their address. Mickey's second West Seventh listing (1950 7th St W) is unverified.
- Honors: Young Joni (Ann Kim, Best Chef 2019) closed (its space was sold in January 2026, Racket); The Bachelor Farmer, La Belle Vie
  and Lucia's are closed and not in our map data. Owamni moved to the Guthrie as Indígena by Owamni in 2026.
- Closed (not in our map data, so nothing to remove): Tavern on Grand (Russell's took 656 Grand Ave in November 2024; Russell's on Grand
  itself closed May 9, 2026), Fhima's, Pajarito's West Seventh restaurant, Sun Street Breads and HeadFlyer Brewing (Racket, 2026-03-31).
- Alcohol: DPS-AGE's license search is search-only and bot-protected; a bulk list needs an AGE data request (Nick's call). St. Paul's
  liquor-license layer was last edited 2025-07-01.
- Blocked or unusable hosts: exploreminnesota.com and startribune.com (bot check); mspmag.com, twincities.com, twincities.eater.com,
  lakesuperior.com, minnpost.com and duluthnewstribune.com disallow Claude; bringmethenews.com and some minnesotamonthly.com and
  kare11.com pages answer 403 to the fetcher.
""")
print(n_out, "| leads:", len(leads))
for l in leads: print(l)
