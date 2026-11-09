# Minnesota sources and calibration (checked 2026-11-06)

## Official sources
| Source | What it has | Can a script read it? | Used |
|---|---|---|---|
| City of Minneapolis "Food_Inspections" (ArcGIS item 4eea8bf452e34f8c9d9ac07c54c0b4ab; services.arcgis.com/afSMGVsC7QlRK1kZ/.../Food_Inspections/FeatureServer/0) | 49,298 violation rows, 10,259 inspections of 2,921 facilities, 2023-01-03 to 2026-11-04; the City's own 0-100 score per inspection; refreshed weekly (Fridays) | yes; "To the extent possible under law, City of Minneapolis has waived all copyright and related or neighboring rights to Open Data" | yes: 914 places show the City's latest score, dated; records run through 2026-10-27 (fetch minus 10 days; reports post within 7 business days) |
| City of Minneapolis "On_Sale_Liquor" (item 5042131de56d44749f6e43c0b5738b21) | 634 licenses (491 Approved/Active; "Pending" isn't live), monthly | yes, same waiver | yes: 333 Minneapolis places show "Serves alcohol" |
| MDH food licensing: who inspects where (health.state.mn.us/communities/environment/food/license/index.html; locals.pdf) | MDH and about 30 delegated city and county agencies | page only | linked from every place outside Minneapolis |
| DPS Alcohol & Gambling Enforcement license search (app.dps.mn.gov/AGEDIS5) | statewide licenses | no: search-only, bot-protected (perfdrive) | no; a bulk list needs an AGE data request (Nick's call) |
| St. Paul "Liquor Licenses" (item ba5b2daf2027409f950a7f72f7f17f9b) | St. Paul licenses | yes | no: last edited 2025-07-01 (stale) |
| Ramsey, Bloomington, Edina, Maplewood, Olmsted, St. Cloud, Anoka, Washington, Hennepin | inspections | no open data or public lookup found (per the prompt, 9/27/2026) | no |
| MetroGIS 7-county parcels | building values | yes | no (no property-value board in the app) |

The City's score: a report "begins with a score of 100", Priority 1 violations take 4 points, Priority 2 take 2, Priority 3 none, and a
score of 91 or lower brings a follow-up (minneapolismn.gov health-inspection-reports page, read 2026-11-06). 100 minus the points matched
the published score in 10,199 of 10,259 inspections; the app shows the published score as is.

## Coverage of the City's list (calibrate.py)
Of Minneapolis map listings, Meta 0.95+ matched the City's food list 66%, Meta 0.90 with a website 33%, BrightQuery 0.95+ 15.5%,
Foursquare 8.7%. 51.9% of the City's 1,526 active food businesses are among the open map listings; 141-178 licensed restaurants the map
lacks are added from the City's list when their name has a food word. No Google data is read anywhere.

## Counts
App: 10,814 places, 10,236 restaurants in 711 towns (BLS QCEW 2025: 11,201 private NAICS 722 places). Overture: 21,195 eating and
drinking listings in Minnesota.

## Research hosts (check_sources.py)
Usable: minnesotamonthly.com, jamesbeard.org (and archive.jamesbeard.org), tastingtable.com, mprnews.org, sahanjournal.com, racketmn.com,
visitsaintpaul.com, visitduluth.com, northshorevisitor.com, ironrange.org, kare11.com, southernminn.com, mnhs.org.
Blocked: exploreminnesota.com and startribune.com (bot check); mspmag.com, twincities.com, twincities.eater.com, lakesuperior.com,
minnpost.com and duluthnewstribune.com (robots.txt). bringmethenews.com passes robots.txt but answers 403 to the fetcher.
