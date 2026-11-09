// Minnesota Eats icon concepts (2026-11-06), drawn in the shared Eats Ranked style (state-prompts/ICON-STYLE.md): one flat, level,
// centred food on Night Sky Blue #002D5D (the 2024 state flag; Nick's decision, 2026-11-07), no backing shape, no text or texture, no team mark.
// Food hexes: bun #E1A95F, patty #6E3B1F, cheese #FFC62F; walleye #C9A84C, eye #F2EEDC; dish #E8E4DC,
// hotdish filling #8B4A2B, tots #D9A35B.
//   A  a Juicy Lucy cut open: bun, patty and the molten cheese core, side elevation
//   B  a walleye, side elevation
//   C  a tater-tot hotdish from above
// Usage, from mn-eats/: swift scripts/icon-concepts.swift <out dir>   -> concept-{a,b,c}-1024.png
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let NIGHT: UInt32 = 0x002D5D, BUN: UInt32 = 0xE1A95F, PATTY: UInt32 = 0x6E3B1F, CHEESE: UInt32 = 0xFFC62F
let WALLEYE: UInt32 = 0xC9A84C, EYE: UInt32 = 0xF2EEDC, DISH: UInt32 = 0xE8E4DC, FILLING: UInt32 = 0x8B4A2B, TOT: UInt32 = 0xD9A35B

func R(_ s: CGFloat, _ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
    CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
}

/// A: the Juicy Lucy, cut through the middle so the cheese core shows. CoreGraphics y-up, s = canvas size. Identical to make-brand.swift's lucy().
func lucy(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(BUN))
    c.addPath(R(s, 0.14, 0.24, 0.72, 0.13, 0.06)); c.fillPath()          // the bottom bun
    c.addPath(R(s, 0.14, 0.50, 0.72, 0.25, 0.12)); c.fillPath()          // the top bun, domed
    c.fill(CGRect(x: 0.14 * s, y: 0.50 * s, width: 0.72 * s, height: 0.10 * s))   // its flat underside
    c.setFillColor(rgb(PATTY)); c.addPath(R(s, 0.155, 0.35, 0.69, 0.17, 0.07)); c.fillPath()   // the patty, a little narrower than the bun
    c.setFillColor(rgb(CHEESE))
    c.addPath(R(s, 0.25, 0.400, 0.50, 0.075, 0.0375)); c.fillPath()     // the molten core
    c.addPath(R(s, 0.60, 0.300, 0.075, 0.14, 0.0375)); c.fillPath()     // and the cheese running out over the bottom bun, off to one side
}

/// A2: the same Juicy Lucy with the core alone (no drip).
func lucyCore(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(BUN))
    c.addPath(R(s, 0.14, 0.24, 0.72, 0.13, 0.06)); c.fillPath()
    c.addPath(R(s, 0.14, 0.50, 0.72, 0.25, 0.12)); c.fillPath()
    c.fill(CGRect(x: 0.14 * s, y: 0.50 * s, width: 0.72 * s, height: 0.10 * s))
    c.setFillColor(rgb(PATTY)); c.addPath(R(s, 0.155, 0.35, 0.69, 0.17, 0.07)); c.fillPath()
    c.setFillColor(rgb(CHEESE)); c.addPath(R(s, 0.24, 0.400, 0.52, 0.075, 0.0375)); c.fillPath()
}

/// B: a walleye, side view, facing left.
func walleye(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(WALLEYE))
    let tail = CGMutablePath()
    tail.move(to: CGPoint(x: 0.74 * s, y: 0.50 * s)); tail.addLine(to: CGPoint(x: 0.86 * s, y: 0.66 * s))
    tail.addQuadCurve(to: CGPoint(x: 0.86 * s, y: 0.34 * s), control: CGPoint(x: 0.82 * s, y: 0.50 * s)); tail.closeSubpath()
    c.addPath(tail); c.fillPath()
    let fin = CGMutablePath()
    fin.move(to: CGPoint(x: 0.38 * s, y: 0.60 * s)); fin.addQuadCurve(to: CGPoint(x: 0.62 * s, y: 0.61 * s), control: CGPoint(x: 0.50 * s, y: 0.76 * s))
    fin.closeSubpath(); c.addPath(fin); c.fillPath()
    c.fillEllipse(in: CGRect(x: 0.14 * s, y: 0.36 * s, width: 0.66 * s, height: 0.28 * s))   // the body
    c.setFillColor(rgb(EYE)); c.fillEllipse(in: CGRect(x: 0.215 * s, y: 0.48 * s, width: 0.09 * s, height: 0.09 * s))
    c.setFillColor(rgb(NIGHT)); c.fillEllipse(in: CGRect(x: 0.238 * s, y: 0.503 * s, width: 0.044 * s, height: 0.044 * s))
}

/// C: a tater-tot hotdish from above: the dish, the filling, three rows of tots.
func hotdish(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(DISH)); c.addPath(R(s, 0.14, 0.25, 0.72, 0.50, 0.08)); c.fillPath()
    c.setFillColor(rgb(FILLING)); c.addPath(R(s, 0.19, 0.30, 0.62, 0.40, 0.05)); c.fillPath()
    c.setFillColor(rgb(TOT))
    for row in 0..<3 {
        for col in 0..<4 {
            c.addPath(R(s, 0.22 + CGFloat(col) * 0.145, 0.33 + CGFloat(row) * 0.125, 0.125, 0.095, 0.0475)); c.fillPath()
        }
    }
}

func render(_ n: Int, _ path: String, _ draw: (CGContext, CGFloat) -> Void) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(NIGHT)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n))
    draw(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "playbook/brand"
render(1024, out + "/concept-a-1024.png", lucy)
render(1024, out + "/concept-b-1024.png", walleye)
render(1024, out + "/concept-c-1024.png", hotdish)
render(1024, out + "/concept-a2-1024.png", lucyCore)
