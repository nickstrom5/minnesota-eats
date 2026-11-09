import SwiftUI
import UIKit
import CoreText

/// Minnesota palette: the 2024 state flag's (Nick's decision, 2026-11-07; playbook/05-naming.md), light only: Night Sky Blue #002D5D
/// (13.7:1 on white) for titles, tint, the honors and oldest cards; North Woods pine #1E5B3A (white on it 8.0:1) for the hand-checked
/// guide cards and chips; Water Blue #52C9E8 only as a fill (hand-checked pins and the title shadow, Night Sky Blue on it 7.1:1; as
/// text on white it's 1.9:1); snow white #FAF9F6 pages. The names `green`/`gold` are kept from Wisconsin Eats so the shared views read
/// the same; here `green` is Night Sky Blue and `gold` is pine.
enum Theme {
    static let green = Color(hex: 0x002D5D)      // Night Sky Blue: titles, tint, primary text accents
    static let green2 = Color(hex: 0x24528A)     // a lighter night blue for small labels (7.9:1 on white)
    static let gold = Color(hex: 0x1E5B3A)       // North Woods pine: card fills under white text, chips
    static let goldSoft = Color(hex: 0xDCEBE1)   // soft pine
    static let lime = Color(hex: 0x52C9E8)       // Water Blue, fills only (hand-checked pins, the title shadow), under Night Sky Blue
    static let limeSoft = Color(hex: 0xD6F2FA)
    static let sand = Color(hex: 0xFAF9F6)       // the Home background, snow white
    static let red = Color(hex: 0x1E5B3A)        // honors chips (pine)
    static let sandstone = Color(hex: 0x144029)  // a darker pine accent (11.4:1 on white)
    static let teal = Color(hex: 0x52C9E8)       // Water Blue: the lake in the header band (a fill)
    static let ink = Color(hex: 0x1A1A1A)
    static let ink2 = Color(hex: 0x2E3440)
    static let muted = Color(hex: 0x5B6270)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xF1EFEA)
    static let surface3 = Color(hex: 0xE4E0D6)
    static let rule = Color(hex: 0xE4E0D6)
    static let rule2 = Color(hex: 0xCCC6B8)
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "STONE CRAB", "1 MICHELIN STAR".
struct Chip: View {
    enum Style { case gold, green, red, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .green || style == .red ? Color.white : style == .dashed ? Theme.muted : style == .gold ? Theme.ink : Theme.green)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .gold ? Theme.goldSoft : style == .green ? Theme.green : style == .red ? Theme.red
                                                       : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// Minnesota Eats' lettering: the system face drawn compressed and heavy for titles and guide names (like a show poster), and the
/// system monospaced face for numbers, dates and small labels. No bundled fonts.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

/// Numbers, dates and small labels in the system monospaced face, scaled like DisplayFont.
struct MonoFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .semibold
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight, design: .monospaced))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }

    func monoFont(_ size: CGFloat, weight: Font.Weight = .semibold) -> some View {
        modifier(MonoFont(size: size, weight: weight))
    }
}

/// The header band: a pine treeline along a lake shore. Spruce and pine of uneven heights, the nearest darkest, over a strip of
/// Water Blue with a thin Night Sky Blue shoreline.
struct Stripes: View {
    var height: CGFloat = 6

    /// (x center 0..1, height 0..1) for each tree, back row then front row
    static let trees: [[(CGFloat, CGFloat)]] = [
        [(0.03, 0.62), (0.10, 0.80), (0.17, 0.66), (0.25, 0.90), (0.33, 0.70), (0.41, 0.84), (0.50, 0.64), (0.58, 0.92), (0.66, 0.72),
         (0.74, 0.86), (0.82, 0.68), (0.90, 0.88), (0.97, 0.70)],
        [(0.06, 0.48), (0.14, 0.58), (0.21, 0.44), (0.29, 0.62), (0.37, 0.50), (0.46, 0.56), (0.54, 0.46), (0.62, 0.60), (0.70, 0.50),
         (0.78, 0.57), (0.86, 0.45), (0.94, 0.55)]]

    var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height, shore = h * 0.74
            for (row, trees) in Self.trees.enumerated() {
                for (x, rise) in trees {
                    let top = shore - shore * rise, half = h * 0.16
                    var p = Path()
                    p.move(to: CGPoint(x: x * w, y: top))
                    p.addLine(to: CGPoint(x: x * w + half, y: shore))
                    p.addLine(to: CGPoint(x: x * w - half, y: shore))
                    p.closeSubpath()
                    ctx.fill(p, with: .color(Theme.gold.opacity(row == 0 ? 0.55 : 1.0)))
                }
            }
            // the lake under the trees, with a thin Night Sky Blue line at the shore
            ctx.fill(Path(CGRect(x: 0, y: shore, width: w, height: h - shore)), with: .color(Theme.teal))
            ctx.fill(Path(CGRect(x: 0, y: shore, width: w, height: max(1, h * 0.06))), with: .color(Theme.green))
        }
        .frame(height: height * 2.4)
        .clipShape(RoundedRectangle(cornerRadius: 3))
        .accessibilityHidden(true)
    }
}

extension View {
    /// An inline navigation title in the display type. UINavigationBar.appearance() didn't reach every SwiftUI bar on iOS 27
    /// (the Map title went from compressed blue to plain black after a push and pop; place titles were always plain), so the
    /// title is our own view in the bar. The navigation title is still set, for the back button and VoiceOver.
    func inlineTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title).displayFont(19, weight: .heavy).foregroundStyle(Theme.green)
                        .lineLimit(1).minimumScaleFactor(0.7)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }
}
