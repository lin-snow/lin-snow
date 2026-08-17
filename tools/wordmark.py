#!/usr/bin/env python3
"""Render a text wordmark to a self-contained SVG of glyph outlines."""
import sys
from fontTools.ttLib import TTFont, TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Offset


def load(path, face_index):
    if path.endswith(".ttc"):
        return TTCollection(path).fonts[face_index]
    return TTFont(path)


def compose(font, text, tracking_em):
    """Return (svg path data in font units, advance width, bounds)."""
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    glyphset = font.getGlyphSet()
    tracking = tracking_em * upm

    path_pen = SVGPathPen(glyphset)
    bounds_pen = BoundsPen(glyphset)
    x = 0.0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            raise SystemExit(f"font lacks glyph for {ch!r}")
        glyph = glyphset[name]
        for pen in (path_pen, bounds_pen):
            glyph.draw(TransformPen(pen, Offset(x, 0)))
        x += glyph.width + tracking
    return path_pen.getCommands(), x - tracking, bounds_pen.bounds


def svg(text, font_path, face_index, size, tracking_em, color, pad=6):
    font = load(font_path, face_index)
    upm = font["head"].unitsPerEm
    d, _advance, (xmin, ymin, xmax, ymax) = compose(font, text, tracking_em)
    scale = size / upm
    w = (xmax - xmin) * scale + pad * 2
    h = (ymax - ymin) * scale + pad * 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.1f}" height="{h:.1f}" '
        f'viewBox="0 0 {w:.1f} {h:.1f}" role="img" aria-label="{text}">'
        f'<g transform="translate({pad - xmin * scale:.2f} {h - pad + ymin * scale:.2f}) '
        f'scale({scale:.5f} -{scale:.5f})">'
        f'<path fill="{color}" d="{d}"/></g></svg>'
    )


if __name__ == "__main__":
    text, font_path, face_index, size, tracking, color, out = (
        sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]),
        float(sys.argv[5]), sys.argv[6], sys.argv[7],
    )
    open(out, "w").write(svg(text, font_path, face_index, size, tracking, color))
    print(out)
