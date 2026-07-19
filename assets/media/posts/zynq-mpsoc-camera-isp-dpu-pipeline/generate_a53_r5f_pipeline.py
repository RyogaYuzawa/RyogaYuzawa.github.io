#!/usr/bin/env python3
"""Generate the A53-R5F Pipeline SVG used by the blog post."""

from pathlib import Path


OUTPUT_PATH = Path(__file__).parent / "images" / "a53-r5f-pipeline.svg"

CARDS = [
    {"x": 74, "label": "CIS", "color": "#06b6d4"},
    {"x": 337, "label": "ISP", "color": "#3b82f6"},
    {"x": 600, "label": "DPU", "color": "#6366f1"},
    {"x": 863, "label": "Post", "color": "#8b5cf6"},
    {"x": 1126, "label": "Disp", "color": "#ec4899"},
]

ARROWS = [
    (274, 325),
    (537, 588),
    (800, 851),
    (1063, 1114),
]


def render_card(card: dict[str, int | str]) -> str:
    x = int(card["x"])
    return f"""    <g>
      <rect x="{x}" y="176" width="200" height="88" rx="18" fill="#ffffff" stroke="#cbd5e1" filter="url(#shadow)"/>
      <rect x="{x}" y="176" width="8" height="88" rx="4" fill="{card['color']}"/>
      <text x="{x + 100}" y="230" fill="#0f172a" font-size="28" font-weight="700">{card['label']}</text>
    </g>"""


def render_arrow(start: int, end: int) -> str:
    return f"""    <path d="M {start} 220 H {end}"/>
    <path d="M {end} 211 L {end + 12} 220 L {end} 229 Z" stroke="none"/>"""


def build_svg() -> str:
    arrows = "\n".join(render_arrow(start, end) for start, end in ARROWS)
    cards = "\n".join(render_card(card) for card in CARDS)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="700" viewBox="0 0 1400 700" role="img" aria-labelledby="title desc">
  <title id="title">Cortex-A53 / Cortex-R5F Pipeline</title>
  <desc id="desc">A Cortex-A53 Ubuntu vision pipeline connected over OpenAMP and RPMsg to FreeRTOS communication, mailbox, periodic control, watchdog, and output-control stages on the Cortex-R5F. The periodic control task returns CONTROL_STATUS to the A53 display.</desc>

  <defs>
    <filter id="shadow" x="-20%" y="-30%" width="140%" height="170%">
      <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#0f172a" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="1400" height="700" rx="28" fill="#f8fafc"/>

  <g transform="translate(0 -90)">
  <rect x="48" y="148" width="1304" height="144" rx="24" fill="none" stroke="#6366f1" stroke-width="2"/>
  <rect x="72" y="132" width="216" height="34" rx="17" fill="#6366f1"/>
  <text x="180" y="155" fill="#ffffff" font-family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif" font-size="16" font-weight="700" text-anchor="middle">Cortex-A53 (Ubuntu)</text>

  <rect x="48" y="470" width="1304" height="280" rx="24" fill="none" stroke="#0f9f8f" stroke-width="2"/>
  <rect x="72" y="454" width="234" height="34" rx="17" fill="#0f9f8f"/>
  <text x="189" y="477" fill="#ffffff" font-family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif" font-size="16" font-weight="700" text-anchor="middle">Cortex-R5F (FreeRTOS)</text>

  <g fill="#64748b" stroke="#64748b" stroke-width="4" stroke-linecap="round">
{arrows}
    <path d="M 963 264 V 390 H 350 V 498" fill="none"/>
    <path d="M 341 498 L 350 510 L 359 498 Z" stroke="none"/>
    <path d="M 490 554 H 538"/>
    <path d="M 538 545 L 550 554 L 538 563 Z" stroke="none"/>
    <path d="M 810 554 H 858"/>
    <path d="M 858 545 L 870 554 L 858 563 Z" stroke="none"/>
    <path d="M 1040 598 V 638"/>
    <path d="M 1031 638 L 1040 650 L 1049 638 Z" stroke="none"/>
  </g>

  <rect x="520" y="338" width="260" height="104" rx="18" fill="#ffffff" stroke="#94a3b8"/>
  <text x="650" y="378" fill="#0f172a" font-family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif" font-size="17" font-weight="700" text-anchor="middle">Vision Result</text>
  <text x="650" y="413" fill="#475569" font-family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif" font-size="16" font-weight="700" text-anchor="middle">OpenAMP / RPMsg</text>

  <g fill="#0f9f8f" stroke="#0f9f8f" stroke-width="4" stroke-linecap="round">
    <path d="M 1210 554 H 1226 V 276" fill="none"/>
    <path d="M 1217 276 L 1226 264 L 1235 276 Z" stroke="none"/>
  </g>
  <rect x="1123" y="335" width="206" height="64" rx="18" fill="#ffffff" stroke="#0f9f8f"/>
  <text x="1226" y="361" fill="#0f766e" font-family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" text-anchor="middle">CONTROL_STATUS</text>
  <text x="1226" y="385" fill="#475569" font-family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" text-anchor="middle">OpenAMP / RPMsg</text>

  <g font-family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif" text-anchor="middle">
{cards}
    <g>
      <rect x="210" y="510" width="280" height="88" rx="18" fill="#ffffff" stroke="#99d8d0" filter="url(#shadow)"/>
      <rect x="210" y="510" width="8" height="88" rx="4" fill="#0f9f8f"/>
      <text x="350" y="547" fill="#0f172a" font-size="19" font-weight="700">RPMsg Task / RX Callback</text>
      <text x="350" y="575" fill="#64748b" font-size="14" font-weight="600">Priority 2 · Validate + Copy</text>
    </g>
    <g>
      <rect x="550" y="510" width="260" height="88" rx="18" fill="#ffffff" stroke="#99d8d0" filter="url(#shadow)"/>
      <rect x="550" y="510" width="8" height="88" rx="4" fill="#14b8a6"/>
      <text x="680" y="561" fill="#0f172a" font-size="19" font-weight="700">Latest-Value Mailbox</text>
    </g>
    <g>
      <rect x="870" y="510" width="340" height="88" rx="18" fill="#ffffff" stroke="#99d8d0" filter="url(#shadow)"/>
      <rect x="870" y="510" width="8" height="88" rx="4" fill="#2dd4bf"/>
      <text x="1040" y="549" fill="#0f172a" font-size="21" font-weight="700">10 ms Periodic Control Task</text>
      <text x="1040" y="576" fill="#64748b" font-size="15" font-weight="600">Priority 4</text>
    </g>
    <g>
      <rect x="790" y="650" width="500" height="88" rx="18" fill="#ffffff" stroke="#99d8d0" filter="url(#shadow)"/>
      <rect x="790" y="650" width="8" height="88" rx="4" fill="#5eead4"/>
      <text x="1040" y="687" fill="#0f172a" font-size="21" font-weight="700">Watchdog / Output Control</text>
      <text x="1040" y="715" fill="#64748b" font-size="15" font-weight="600">Future: GPIO / PWM / Motor / Servo</text>
    </g>
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
