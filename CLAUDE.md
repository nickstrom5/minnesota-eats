# Minnesota Eats (mn-eats) — notes for Claude Code sessions

Built 2026-11-06 by a side session for Nick's "build the 17 states left" (group: MN, IA, NE, ND, SD), ported from `../va-eats/` (its
official-inspection plumbing) with every fix through 11-05 (the exact-outline county lookup, the out-of-county truck rule, Utah's
street-word merge fix, Vermont's narrowed "dejavu" rule, Virginia's near-adult-venue fix, the per-state ZIP check, the delivery-only
brands, the website blocklist and `link_blocklist.py`, the Share link `Links.site + explore/#p=<id>`, OTA data, the adult-venue rules)
and wy-eats' far-listing rule. Local only: git-ignored data, no repo, no remote, nothing published. Sources: `playbook/12-sources.md`.
Brand: `playbook/05-naming.md` — **final**, Nick's decision of 2026-11-07 ("Minnesota Eats: Restaurants", Home Screen "Minnesota Eats"; the
Juicy Lucy icon; the 2024 state flag palette: Night Sky Blue #002D5D, pine #1E5B3A, Water Blue #52C9E8 fill only, snow; a pine treeline
over a Water Blue lake).

## Minnesota is different
- **No Google data at all** (rule of 2026-11-06): the UCSD snapshot is never downloaded; `listings.py` builds an empty Google table,
  `minnesota.py` writes NaN fits as null, and the keep rule is the family's (Meta 0.95, or 0.90 with a website), calibrated against the
  City of Minneapolis's list.
- **One official list:** the City of Minneapolis's food inspections (weekly) and on-sale liquor licenses (monthly), open data with the
  City's copyright waiver (`fetch_official.py`, `official.py`). Places it matches show the City's own score "96 of 100", dated (records
  through the fetch day minus 10 days), with its earlier published scores under it and the City's page linked. There's no grade of
  ours, and scores are never the default order.
  Everywhere else MDH and ~30 delegated agencies post nothing a script may read, so places link MDH's who-inspects page. "Serves
  alcohol" comes only from Minneapolis's on-sale list; elsewhere it's "—".
- **Counties and regions:** 87 counties; six detail files (Twin Cities, Central, Southern, Lakes & Northwest, Arrowhead & North Shore,
  Prairie & Southwest). `fetch_overture.py` checks the border towns (Moorhead, East Grand Forks, Duluth, Stillwater, International
  Falls, Grand Portage, La Crescent, Breckenridge, Warroad, the Northwest Angle and Luverne in; Fargo, Grand Forks, Superior, Hudson, La
  Crosse, Fort Frances, Sioux Falls, Wahpeton and Estherville out). The app's outline (`LocationService.swift`) cuts the neighbours'
  land back out, so Fargo and Grand Forks stay outside.
- **Venues:** MSP's terminals (4300 Glumack Dr, 7150 Humphrey Dr and the terminal box), Duluth and Rochester airports, US Bank Stadium,
  Target Field, Target Center, Xcel Energy Center, Allianz Field, Huntington Bank Stadium, the State Fairgrounds (1265 Snelling Ave N).
  Stores with food counters: Kwik Trip, Holiday, Cub, Hy-Vee, Lunds & Byerlys, Kowalski's, Coborn's and others.
- **Adult venues:** standalone clubs by address in `data/research/adult_venues.json`; the downtown Minneapolis clubs share blocks with
  restaurants, so they're left to the 150 m name rule. not_adult: "AfroVibes at Oga Madam" (it hid Oga Madam Kitchen).
- **Guides** (tags in `minnesota.py` TAGS; bits 1..64): Juicy Lucys (both claimants, Matt's Bar and the 5-8 Club; no winner picked),
  walleye and supper clubs, Hmong and Southeast Asian, Somali and East African, North Shore and Iron Range (smoked fish, pie, potica,
  pasties), classic counters and icons, oldest (founded at the address by 1960). Sources in `pipeline/build_research.py`, each note
  checked against what its page says (2026-11-06). Leads in `data/research/app/LEADS.md`.
- **Honors:** no MICHELIN Guide covers Minnesota. James Beard: America's Classics Al's Breakfast (2004), the Pickwick (2007),
  Kramarczuk's (2013); Best Chef: Midwest winners Alex Roberts (Alma, 2010), Isaac Becker (112 Eatery, 2011), Gavin Kaysen (Spoon and
  Stable, 2018), Christina Nguyen (Hai Hai, 2024), Karyn Tomlinson (Myriel, 2025); Best New Restaurant Owamni (2022; now Indígena by
  Owamni at the Guthrie, the old address closed) and Bûcheron (2025); 2025-26 finalists and semifinalists. Young Joni closed.

## Rebuild
```bash
cd pipeline
../.venv/bin/python check_sources.py URL...   # a new host first
../.venv/bin/python fetch_overture.py && ../.venv/bin/python fetch_extras.py && ../.venv/bin/python fetch_official.py
../.venv/bin/python geocode_official.py && ../.venv/bin/python geocode_census.py && ../.venv/bin/python listings.py
../.venv/bin/python calibrate.py && ../.venv/bin/python minnesota.py && ../.venv/bin/python build_research.py && ../.venv/bin/python minnesota.py
MN_APP=1 ../.venv/bin/python minnesota.py && cd .. && cp data/app/places.json data/app/detail-*.json MinnesotaEats/Resources/
.venv/bin/python pipeline/check_websites.py && .venv/bin/python pipeline/check_websites.py --retry-transient   # then re-export
.venv/bin/python scripts/make-site.py && .venv/bin/python scripts/publish_app_data.py && .venv/bin/python scripts/publish_app_data.py --check
.venv/bin/python scripts/qa-site.py --static
```
`data/chain_auv.json` is a copy of wy-eats'. The `.venv` is on the python.org framework Python 3.12 with the family's versions.

## App, site, screenshots
- App: `MinnesotaEats/` (XcodeGen `project.yml`, bundle `com.minnesotaeats.ios`, display "Minnesota Eats"), tests in
  `MinnesotaEatsTests/` (a 13-place Minnesota fixture; data guards: adult venues, blocklisted and multi-URL websites, bad and legal names,
  non-restaurants, listed twice, no Google data, Minneapolis-only scores and on-sale licenses) and `MinnesotaEatsUITests/`. Build and
  test only with Xcode 1.app (27.2, 27B52); Xcode.app is a beta. Run `xcodegen generate` whenever `Resources/*.json` changes.
- Site: `scripts/make-site.py` writes `docs/` and `playbook/site-numbers.json`; `scripts/explore.js` is the web app; `scripts/qa-site.py`
  the QA. Site URL for now: nickstrom5.github.io/minnesota-eats (no CNAME). City pages: Minneapolis, St. Paul, Duluth.
- Screenshots: `scripts/capture-screenshots.sh <sim>` (ScreenshotMode pins downtown Minneapolis; Brainerd for walleye, University Ave for
  Hmong and East African, Duluth for the North Shore, downtown St. Paul for classics and the Mickey's detail), then
  `scripts/site-images.sh`, then make-site + qa-site. App Store frames: `scripts/appstore-screenshots.py`. Listing:
  `playbook/app-store/listing.json`. Icons: `scripts/icon-concepts.swift`, `scripts/make-brand.swift`.

## Status
See the end of this file (written when the build finished).

### Status (2026-11-08 11:10): final
- **Ready to publish; nothing public.** No repo, commit, push, Pages, App Store Connect record or build upload; all of those wait for
  Nick's yes.
- Data: 10,238 restaurants (10,814 places) in 711 towns, 87 counties; 50 hand-checked guide places (5 Juicy Lucys, 4 walleye and supper
  clubs, 8 Hmong and Southeast Asian, 5 Somali and East African, 11 North Shore and Iron Range, 15 classic counters, 5 oldest), 22 James
  Beard honorees (3 America's Classics). Official list: the City of Minneapolis's food inspections and on-sale liquor licenses (open
  data, copyright waived): 914 places show the City's own score, dated, and 333 show "Serves alcohol"; elsewhere both are "—".
- Late fixes (2026-11-06): the site's merge had hidden every score from the web pages ("0 Minneapolis places"), now 914 with list items
  labeled "City of Minneapolis inspection"; the "Ask for early access" mail subject named Virginia's app; two "Rusty Nail" bars were
  hidden as nail salons; Neumann's Bar's spelling in the tests and the iPad screenshot pick.
- Tests (Xcode 1.app 27.2, iOS 27.0), final runs on the 2024 flag palette: iPad 13" (M5) 49 unit + 6 UI tests passed (2026-11-08;
  4.63 s to Home). iPhone 17 Pro Max: 49 unit tests and 5 UI tests passed (2026-11-07). Its launch-time test first measured 7.18 s
  on a busy Mac (load 16.2, just under the level where it skips itself), then passed alone on a quiet machine (5.25 s to Home, the
  limit 6 s; 2026-11-08 11:09).
- Site: `docs/` regenerated 2026-11-07 in the flag palette with the new screenshots; `qa-site.py --static` and the full headless-Chrome
  run both OK (2026-11-08 10:43); `publish_app_data.py --check` OK.
- App Store: 8 iPhone and 6 iPad frames in `playbook/app-store/`, rebuilt 2026-11-08 from new screenshots in the flag palette (the home
  frame shows 10,238 restaurants; the detail caption reads "Guide places, checked by hand"); `listing.json` (Minnesota Eats:
  Restaurants; support and privacy on nickstrom5.github.io/minnesota-eats/).
- Brand final (Nick, 2026-11-07): name, Juicy Lucy icon, and the 2024 flag palette that replaced Vikings purple and gold (app theme,
  icon, site, og.png and frame colors regenerated). An AGE records request is being drafted by the parent session.
