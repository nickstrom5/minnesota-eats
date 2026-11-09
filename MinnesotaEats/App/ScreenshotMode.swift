import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, lucys, walleye, hmong, african, north, classics, honors, oldest, detail, map, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // downtown Minneapolis (Nicollet Mall), so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 44.9778, longitude: -93.2716)
        // by name and town, ignoring case, so a rebuild with a slightly different casing still finds the place; the hand-checked one first
        let pick = { (n: String, town: String?) -> Place? in
            let hits = model.places.filter { $0.name.caseInsensitiveCompare(n) == .orderedSame && (town == nil || $0.city == town) }
            return hits.first(where: \.handChecked) ?? hits.first
        }
        for p in [pick("Matt's Bar and Grill", "Minneapolis"), pick("Mickey's Diner", "St. Paul"), pick("Northern Waters Smokehaus", "Duluth")]
            .compactMap({ $0 }) where !model.isSaved(p) {
            model.toggleSaved(p)
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        switch name {
        case "lucys": open(.lucys)
        case "walleye":
            // Brainerd, in lake country
            model.screenshotLocation = CLLocation(latitude: 46.3580, longitude: -94.2008)
            open(.walleye)
        case "hmong", "african":
            // St. Paul's University Avenue (Little Mekong)
            model.screenshotLocation = CLLocation(latitude: 44.9556, longitude: -93.1180)
            open(name == "hmong" ? .hmong : .african)
        case "north":
            // Duluth's Canal Park
            model.screenshotLocation = CLLocation(latitude: 46.7840, longitude: -92.0940)
            open(.north)
        case "classics":
            // downtown St. Paul
            model.screenshotLocation = CLLocation(latitude: 44.9470, longitude: -93.0940)
            open(.classics)
        case "honors": open(.honors)
        case "oldest": open(.oldest)
        case "detail":
            // Mickey's Diner: a classic counter with its 1939 founding year and its note
            model.screenshotLocation = CLLocation(latitude: 44.9470, longitude: -93.0940)
            open(.classics)
            if let p = pick("Mickey's Diner", "St. Paul") ?? model.places.first {
                model.selectedPlace = p; model.guidesPath.append(.place(p))
            }
        case "map": model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place": a different
        // honored or hand-checked one per shot.
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "home": pick("Mickey's Diner", "St. Paul")
        case "lucys": pick("5-8 Club", "Minneapolis")
        case "walleye": pick("Bar Harbor Supper Club", "Lake Shore")
        case "hmong": pick("Hoa Bien Vietnamese Restaurant", "St. Paul")
        case "african": pick("Afro Deli & Grill", "St. Paul")
        case "north": pick("Northern Waters Smokehaus", "Duluth")
        case "classics": pick("Boca Chica Restaurante Mexicano y Cantina", "St. Paul")
        case "map": pick("Matt's Bar and Grill", "Minneapolis")
        case "honors": pick("Spoon and Stable", "Minneapolis")
        case "oldest": pick("Neumann's Bar", "North St. Paul")
        case "saved": pick("Mickey's Diner", "St. Paul")
        case "about": nil
        default: pick("Mickey's Diner", "St. Paul")
        }
        model.selectedPlace = place
    }
}
