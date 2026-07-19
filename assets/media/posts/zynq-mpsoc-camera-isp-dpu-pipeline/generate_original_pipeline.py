#!/usr/bin/env python3
"""Generate the Original Pipeline SVG used by the blog post."""

from pathlib import Path


OUTPUT_PATH = Path(__file__).parent / "images" / "original-pipeline.svg"

CARDS = [
    {"x": 74, "width": 200, "label": "CIS", "color": "#06b6d4", "font_size": 28},
    {"x": 337, "width": 200, "label": "ISP", "color": "#3b82f6", "font_size": 28},
    {"x": 600, "width": 200, "label": "DPU", "color": "#6366f1", "font_size": 28},
    {"x": 863, "width": 200, "label": "Post", "color": "#8b5cf6", "font_size": 28},
    {"x": 1126, "width": 200, "label": "Disp", "color": "#ec4899", "font_size": 28},
]

ARROWS = [
    (274, 325),
    (537, 588),
    (800, 851),
    (1063, 1114),
]


def render_card(card: dict[str, int | str]) -> str:
    x = int(card["x"])
    width = int(card["width"])
    center = x + width // 2
    return f"""    <g>
      <rect x="{x}" y="176" width="{width}" height="88" rx="18" fill="#ffffff" stroke="#cbd5e1" filter="url(#shadow)"/>
      <rect x="{x}" y="176" width="8" height="88" rx="4" fill="{card['color']}"/>
      <text x="{center}" y="230" fill="#0f172a" font-size="{card['font_size']}" font-weight="700">{card['label']}</text>
    </g>"""


def render_arrow(start: int, end: int) -> str:
    return f"""    <path d="M {start} 220 H {end}"/>
    <path d="M {end} 211 L {end + 12} 220 L {end} 229 Z" stroke="none"/>"""


def build_svg() -> str:
    arrows = "\n".join(render_arrow(start, end) for start, end in ARROWS)
    cards = "\n".join(render_card(card) for card in CARDS)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="260" viewBox="0 0 1400 260" role="img" aria-labelledby="title desc">
  <title id="title">Original Smart Camera Pipeline</title>
  <desc id="desc">A horizontal pipeline from CIS through ISP, DPU, Post, and Disp.</desc>

  <defs>
    <filter id="shadow" x="-20%" y="-30%" width="140%" height="170%">
      <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#0f172a" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="1400" height="260" rx="28" fill="#f8fafc"/>

  <g transform="translate(0 -90)">
  <rect x="48" y="148" width="1304" height="144" rx="24" fill="none" stroke="#6366f1" stroke-width="2"/>
  <rect x="72" y="132" width="258" height="34" rx="17" fill="#6366f1"/>
  <text x="201" y="155" fill="#ffffff" font-family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif" font-size="16" font-weight="700" text-anchor="middle">Cortex-A53 (Ubuntu / Docker)</text>

  <g fill="#64748b" stroke="#64748b" stroke-width="4" stroke-linecap="round">
{arrows}
  </g>

  <g font-family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif" text-anchor="middle">
{cards}
  </g>
  </g>
</svg>
"""


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_svg(), encoding="utf-8")
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
