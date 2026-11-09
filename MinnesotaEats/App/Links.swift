import Foundation

/// The app's web pages and support address, in one place.
/// The site is GitHub Pages at the project address until minnesota.eatsranked.com resolves (Nick adds a Cloudflare CNAME
/// minnesota -> nickstrom5.github.io, DNS only; then scripts/make-site.py sets CUSTOM_DOMAIN). GitHub forwards these github.io
/// links to the custom domain after the switch, so a shipped build keeps working; point them at the new domain in the next update.
enum Links {
    static let site = URL(string: "https://nickstrom5.github.io/minnesota-eats/")!
    /// The app's data updates: scripts/publish_app_data.py writes docs/data/app/ (OTA-DATA.md).
    static let appData = URL(string: site.absoluteString + "data/app/")!
    static let privacy = URL(string: site.absoluteString + "privacy.html")!
    static let terms = URL(string: site.absoluteString + "terms.html")!
    /// DPS Alcohol & Gambling Enforcement: it licenses with the cities and counties (its license search is search-only, not read)
    static let licenses = URL(string: "https://dps.mn.gov/divisions/age")!
    /// MDH's food licensing page: who inspects where (MDH and the delegated city and county agencies; MDH posts no reports online)
    static let inspections = URL(string: "https://www.health.state.mn.us/communities/environment/food/license/index.html")!
    /// the City of Minneapolis's own page on its inspection reports and scores (it links the City's lookup dashboard)
    static let minneapolisInspections = URL(string: "https://www.minneapolismn.gov/business-services/business-assistance/run/food-safety/health-inspection-reports/")!
    static let supportEmail = "nick@eatsranked.com"

    static var correctionEmail: URL {
        URL(string: "mailto:\(supportEmail)?subject=Minnesota%20Eats%20correction")!
    }

    // MARK: Share

    /// The web app. It opens a place's panel from the hash, explore/#p=<id> (readHash in scripts/explore.js), using the app's ids.
    static let explore = URL(string: site.absoluteString + "explore/")!

    /// What Share sends: the place's own page in the web app, never an Apple Maps or Google link (Apple Maps has its own button).
    /// The id is escaped the way the page's encodeURIComponent would escape it. The web app lists every place
    /// the app does (a unit test checks the ids against docs/data).
    /// The web app lists restaurants only: the venues the app hides by default (stadium stands, gas-station counters) aren't there.
    static func onWeb(_ place: Place) -> Bool { !place.isVenue }
    static func share(_ place: Place) -> URL {
        guard onWeb(place), let id = place.id.addingPercentEncoding(withAllowedCharacters: uriComponent),
              let url = URL(string: explore.absoluteString + "#p=" + id) else { return explore }
        return url
    }

    /// The text that goes with the link: the place, its town and the app. No street address, which Messages turns into a Maps link.
    static func shareMessage(_ place: Place) -> String {
        [place.name, place.city ?? ""].filter { !$0.isEmpty }.joined(separator: ", ") + ", on Minnesota Eats"
    }

    /// What encodeURIComponent leaves as is.
    private static let uriComponent = CharacterSet(charactersIn: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.!~*'()")
}
