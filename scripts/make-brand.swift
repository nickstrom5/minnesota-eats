// Minnesota Eats brand (Nick's decision, 2026-11-07: the name, icon A and the 2024 state flag palette): the app icon is concept A of
// scripts/icon-concepts.swift, a Juicy Lucy cut open to its cheese core, on Night Sky Blue; the shared Eats Ranked icon style,
// state-prompts/ICON-STYLE.md, no backing shape. No team logo, wordmark or horns, no state seal, no "Explore Minnesota" lines.
// Usage, from mn-eats/: swift scripts/make-brand.swift   -> MinnesotaEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png,
// docs/ favicons and touch icons, docs/og.png. scripts/make-site.py draws the same mark as its inline SVG: change both together.
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let NIGHT: UInt32 = 0x002D5D, BUN: UInt32 = 0xE1A95F, PATTY: UInt32 = 0x6E3B1F, CHEESE: UInt32 = 0xFFC62F
let PINE: UInt32 = 0x1E5B3A, WATER: UInt32 = 0x52C9E8, SNOW: UInt32 = 0xFAF9F6

func R(_ s: CGFloat, _ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
    CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
}

/// A: the Juicy Lucy. CoreGraphics y-up, s = canvas size. Identical to icon-concepts.swift's concept A.
func lucy(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(BUN))
    c.addPath(R(s, 0.14, 0.24, 0.72, 0.13, 0.06)); c.fillPath()          // the bottom bun
    c.addPath(R(s, 0.14, 0.50, 0.72, 0.25, 0.12)); c.fillPath()          // the top bun, domed
    c.fill(CGRect(x: 0.14 * s, y: 0.50 * s, width: 0.72 * s, height: 0.10 * s))   // its flat underside
    c.setFillColor(rgb(PATTY)); c.addPath(R(s, 0.155, 0.35, 0.69, 0.17, 0.07)); c.fillPath()   // the patty
    c.setFillColor(rgb(CHEESE))
    c.addPath(R(s, 0.25, 0.400, 0.50, 0.075, 0.0375)); c.fillPath()     // the molten core
    c.addPath(R(s, 0.60, 0.300, 0.075, 0.14, 0.0375)); c.fillPath()     // and the cheese running out over the bottom bun, off to one side
}

func render(_ n: Int, _ path: String, background: Bool) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: background ? CGImageAlphaInfo.noneSkipLast.rawValue : CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true)
    if background { ctx.setFillColor(rgb(NIGHT)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n)) }
    lucy(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
render(1024, "MinnesotaEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", background: true)
try? FileManager.default.createDirectory(atPath: "docs", withIntermediateDirectories: true)
for (n, name) in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (32, "favicon-32.png")] {
    render(n, "docs/" + name, background: true)
}

/// The share image (1200 x 630): Night Sky Blue, the Juicy Lucy at the left, the name and tagline at the right, and the app's header band along
/// the bottom: a pine treeline along a lake shore, on snow white (Theme.swift's Stripes.trees).
func og(_ path: String) {
    let W = 1200, H = 630
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(NIGHT)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    let band: CGFloat = 70, shore: CGFloat = 18
    ctx.setFillColor(rgb(SNOW)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: Int(band)))
    let trees: [[(CGFloat, CGFloat)]] = [
        [(0.03, 0.62), (0.10, 0.80), (0.17, 0.66), (0.25, 0.90), (0.33, 0.70), (0.41, 0.84), (0.50, 0.64), (0.58, 0.92), (0.66, 0.72),
         (0.74, 0.86), (0.82, 0.68), (0.90, 0.88), (0.97, 0.70)],
        [(0.06, 0.48), (0.14, 0.58), (0.21, 0.44), (0.29, 0.62), (0.37, 0.50), (0.46, 0.56), (0.54, 0.46), (0.62, 0.60), (0.70, 0.50),
         (0.78, 0.57), (0.86, 0.45), (0.94, 0.55)]]
    for (row, ts) in trees.enumerated() {
        for (x, rise) in ts {
            let top = shore + (band - shore) * rise, half: CGFloat = 16
            let p = CGMutablePath(); p.move(to: CGPoint(x: x * CGFloat(W), y: top))
            p.addLine(to: CGPoint(x: x * CGFloat(W) + half, y: shore)); p.addLine(to: CGPoint(x: x * CGFloat(W) - half, y: shore)); p.closeSubpath()
            ctx.setFillColor(rgb(PINE).copy(alpha: row == 0 ? 0.55 : 1.0)!); ctx.addPath(p); ctx.fillPath()
        }
    }
    ctx.setFillColor(rgb(WATER)); ctx.fill(CGRect(x: 0, y: 0, width: CGFloat(W), height: shore))
    ctx.setFillColor(rgb(NIGHT)); ctx.fill(CGRect(x: 0, y: shore - 3, width: CGFloat(W), height: 3))
    ctx.saveGState(); ctx.translateBy(x: 40, y: 90); lucy(ctx, 500); ctx.restoreGState()
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
    let title = NSFont(name: "AvenirNextCondensed-Heavy", size: 80) ?? NSFont.boldSystemFont(ofSize: 70)
    let sub = NSFont(name: "AvenirNextCondensed-DemiBold", size: 34) ?? NSFont.boldSystemFont(ofSize: 30)
    NSAttributedString(string: "MINNESOTA", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 560, y: 380))
    NSAttributedString(string: "EATS", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 560, y: 296))
    NSAttributedString(string: "JUICY LUCYS, WALLEYE & SUPPER CLUBS", attributes: [.font: sub, .foregroundColor: NSColor(srgbRed: 0.322, green: 0.788, blue: 0.910, alpha: 1)]).draw(at: NSPoint(x: 564, y: 246))
    NSGraphicsContext.restoreGraphicsState()
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
og("docs/og.png")
