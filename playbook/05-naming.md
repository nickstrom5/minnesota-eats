# Minnesota Eats: name, icon and palette

**Final: Nick's decision of 2026-11-07 ("Yes, as proposed" on the 17-state review page).**
Name and icon A as below; the palette is the 2024 state flag's, replacing the Vikings-inspired one.

## Name
- **Minnesota Eats** (App Store name "Minnesota Eats: Restaurants", 27 characters; subtitle "Juicy Lucys & Supper Clubs"; Home Screen
  "Minnesota Eats"). It mirrors Wisconsin Eats. A web search (2026-11-06) found no app, magazine, show or podcast by that name; the
  closest are WCCO's "DeRusha Eats" podcast and Minnesota Monthly's "Favorite Eats". The prompt notes minnesotaeats.com is registered
  (not ours), and no App Store app had the name in September 2026.
- Alternatives from the prompt: **Hotdish** (hotdish.com is taken; a "Hot Dish" web app runs at hotdishapp.com) and **10,000 Plates**
  (plays on "Land of 10,000 Lakes"; 10000plates.com is registered; check USPTO for "10,000 Lakes" marks before using it).
- Avoided: "Explore Minnesota" (the state tourism brand) and its campaign lines, "Minnesota Grown" (an MDA program), anything with the
  Vikings' name, horns or logo.

## Icon (state-prompts/ICON-STYLE.md; A and B pass state-prompts/icon-style/check.swift, C passes too)
- **A, chosen (final): a Juicy Lucy cut open**, the cheese core showing and a little cheese running over the bottom bun, off to one
  side (centred, the drip made a "T", and Nick has rejected icons that read as a letter).
- B: a walleye, side view (the clearest at 60 px; Minnesota's state fish).
- C: a tater-tot hotdish from above (reads as a tray at 60 px).
Drawn by `scripts/icon-concepts.swift`; `scripts/make-brand.swift` makes the app icon, favicons, touch icons and og.png from A.

## Palette (the 2024 state flag; text contrast measured)
| Role | Hex | Contrast |
|---|---|---|
| Titles, tint, honors and oldest cards, icon background | Night Sky Blue #002D5D | 13.7:1 on white; white on it 13.7:1 |
| Hand-checked guide cards, chips | North Woods pine #1E5B3A | white on it 8.0:1 |
| Pins, the title shadow, the header's lake (fill only) | Water Blue #52C9E8 | Night Sky Blue on it 7.1:1; never text on white (1.9:1) |
| Small labels | night blue #24528A | 7.9:1 on white |
| Pages | snow white #FAF9F6 | |
The Vikings purple #4F2683 and gold #FFC62F of the first build are gone (2026-11-07). The icon's cheese stays #FFC62F, as a food color.

## Header
A pine treeline along a Water Blue lake with a thin Night Sky Blue shoreline (`Theme.swift` Stripes; the site's RAYS band; og.png).
