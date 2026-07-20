#!/usr/bin/env python3
"""Generate the SVG diagrams for the A53/R5F Camera AI article."""

from pathlib import Path


OUTPUT_DIR = Path(__file__).parent / "images"
FONT = "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


def svg_shell(title: str, description: str, height: int, body: str, width: int = 1400) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{description}</desc>
  <defs>
    <filter id="shadow" x="-20%" y="-30%" width="140%" height="170%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#0f172a" flood-opacity="0.10"/>
    </filter>
  </defs>
  <rect width="{width}" height="{height}" rx="28" fill="#f8fafc"/>
  <g font-family="{FONT}">
{body}
  </g>
</svg>
'''


def memory_map() -> str:
    rows = [
        ("R5F firmware DDR", "0x79000000", "0x00040000", "0x7903FFFF", "#6366f1", 0x00040000),
        ("RSC_TRACE", "0x7903F000", "0x00001000", "0x7903FFFF", "#8b5cf6", 0x00001000),
        ("vring0", "0x79040000", "0x00004000", "0x79043FFF", "#0ea5e9", 0x00004000),
        ("vring1", "0x79044000", "0x00004000", "0x79047FFF", "#06b6d4", 0x00004000),
        ("RPMsg shared buffers", "0x79048000", "0x00100000", "0x79147FFF", "#14b8a6", 0x00100000),
    ]
    y = 174
    rendered = []
    maximum_size = 0x00100000
    maximum_bar_width = 460
    for label, start, size, end, color, size_bytes in rows:
        bar_width = size_bytes / maximum_size * maximum_bar_width
        size_x = 500 + bar_width + 16
        rendered.append(f'''<rect x="500" y="{y}" width="{bar_width:g}" height="72" rx="4" fill="{color}" fill-opacity="0.72" stroke="{color}" stroke-width="2"/>
    <text x="70" y="{y + 31}" fill="#0f172a" font-size="19" font-weight="750">{label}</text>
    <text x="70" y="{y + 54}" fill="#64748b" font-size="14" font-weight="600">{start} – {end}</text>
    <text x="{size_x:g}" y="{y + 44}" fill="#0f172a" font-size="16" font-weight="700">{size}</text>''')
        y += 92
    body = f'''    <text x="500" y="30" fill="#475569" font-size="14" font-weight="750">SIZE</text>
    <g transform="translate(0 -120)">
    {''.join(rendered)}
    </g>'''
    return svg_shell(
        "KV260 R5F and RPMsg memory map",
        "The reserved-memory contract places firmware, trace, two vrings, and the RPMsg shared-buffer pool at non-overlapping physical DDR addresses.",
        520,
        body,
        1100,
    )


def control_states() -> str:
    body = '''    <g transform="translate(0 -110)">
    <circle cx="135" cy="340" r="14" fill="#334155"/>
    <path d="M 149 340 H 258" fill="none" stroke="#64748b" stroke-width="4" stroke-linecap="round"/>
    <path d="M 258 334 L 270 340 L 258 346 Z" fill="#64748b"/>
    <g filter="url(#shadow)"><rect x="270" y="280" width="220" height="120" rx="24" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/></g>
    <text x="380" y="332" text-anchor="middle" fill="#0f172a" font-size="25" font-weight="800">INIT</text>
    <text x="380" y="364" text-anchor="middle" fill="#64748b" font-size="15" font-weight="600">Waiting for valid input</text>
    <g filter="url(#shadow)"><rect x="590" y="160" width="220" height="120" rx="24" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/></g>
    <text x="700" y="212" text-anchor="middle" fill="#047857" font-size="25" font-weight="800">FRESH</text>
    <text x="700" y="244" text-anchor="middle" fill="#64748b" font-size="15" font-weight="600">Apply latest result</text>
    <g filter="url(#shadow)"><rect x="590" y="420" width="220" height="120" rx="24" fill="#fffbeb" stroke="#f59e0b" stroke-width="2"/></g>
    <text x="700" y="472" text-anchor="middle" fill="#b45309" font-size="25" font-weight="800">HOLD</text>
    <text x="700" y="504" text-anchor="middle" fill="#64748b" font-size="15" font-weight="600">Retain safe bounded state</text>
    <g filter="url(#shadow)"><rect x="1010" y="280" width="240" height="120" rx="24" fill="#fef2f2" stroke="#ef4444" stroke-width="2"/></g>
    <text x="1130" y="332" text-anchor="middle" fill="#b91c1c" font-size="25" font-weight="800">FAILSAFE</text>
    <text x="1130" y="364" text-anchor="middle" fill="#64748b" font-size="15" font-weight="600">Apply deterministic safe output</text>
    <g fill="none" stroke-width="4" stroke-linecap="round">
      <path d="M 490 314 C 530 260, 545 220, 578 220" stroke="#10b981"/>
      <path d="M 700 280 V 408" stroke="#f59e0b"/>
      <path d="M 590 460 C 520 430, 520 275, 578 238" stroke="#10b981"/>
      <path d="M 810 480 C 910 480, 925 360, 998 360" stroke="#ef4444"/>
      <path d="M 380 400 V 580 Q 380 620, 420 620 H 1030 Q 1070 620, 1070 580 V 412" stroke="#ef4444"/>
    </g>
    <g stroke="none">
      <path d="M 578 214 L 590 220 L 578 226 Z" fill="#10b981"/>
      <path d="M 694 408 L 700 420 L 706 408 Z" fill="#f59e0b"/>
      <path d="M 578 232 L 590 238 L 578 244 Z" fill="#10b981"/>
      <path d="M 998 354 L 1010 360 L 998 366 Z" fill="#ef4444"/>
      <path d="M 1064 412 L 1070 400 L 1076 412 Z" fill="#ef4444"/>
    </g>
    <g font-size="14" font-weight="700" text-anchor="middle">
      <rect x="355" y="140" width="215" height="34" rx="12" fill="#f8fafc"/>
      <text x="462.5" y="162" fill="#047857">valid heartbeat + result</text>
      <rect x="712" y="320" width="242" height="34" rx="12" fill="#f8fafc"/>
      <text x="833" y="342" fill="#b45309">expired result or late inference</text>
      <rect x="330" y="460" width="190" height="34" rx="12" fill="#f8fafc"/>
      <text x="425" y="482" fill="#047857">fresh input resumes</text>
      <rect x="830" y="292" width="150" height="34" rx="12" fill="#f8fafc"/>
      <text x="905" y="314" fill="#b91c1c">long timeout</text>
      <rect x="620" y="568" width="180" height="34" rx="12" fill="#f8fafc"/>
      <text x="710" y="590" fill="#b91c1c">startup timeout</text>
    </g>
    </g>'''
    return svg_shell(
        "R5F freshness control state machine",
        "The control policy transitions among INIT, FRESH, HOLD, and FAILSAFE according to heartbeat and inference-result freshness.",
        550,
        body,
    )


def bringup_flow() -> str:
    steps = [
        ("1", "Audit target memory", "Live DT · iomem · CMA", "#6366f1"),
        ("2", "Reserve at boot", "Merge user-override.dtb", "#8b5cf6"),
        ("3", "Build + verify ELF", "Vitis 2024.2 · XSA", "#0ea5e9"),
        ("4", "Start remoteproc", "Load ELF · release R5F", "#06b6d4"),
        ("5", "Create RPMsg endpoint", "Name service · rpmsg-char", "#14b8a6"),
        ("6", "Test transport", "Fresh · stale · restart", "#10b981"),
        ("7", "Integrate camera/DPU", "Publish real vision results", "#f59e0b"),
    ]
    rendered = []
    for index, (number, title, subtitle, color) in enumerate(steps):
        row = index // 4
        col = index % 4
        if row == 1:
            col = 2 - col
        x = 55 + col * 335
        y = 150 + row * 250
        rendered.append(f'''<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="270" height="126" rx="20" fill="#ffffff" stroke="#cbd5e1"/></g>
    <circle cx="{x + 34}" cy="{y + 34}" r="21" fill="{color}"/>
    <text x="{x + 34}" y="{y + 41}" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="800">{number}</text>
    <text x="{x + 135}" y="{y + 70}" text-anchor="middle" fill="#0f172a" font-size="19" font-weight="800">{title}</text>
    <text x="{x + 135}" y="{y + 98}" text-anchor="middle" fill="#64748b" font-size="14" font-weight="600">{subtitle}</text>''')
    body = f'''    <g transform="translate(0 -115)">
    {''.join(rendered)}
    <g fill="none" stroke="#64748b" stroke-width="4" stroke-linecap="round">
      <path d="M 325 213 H 378"/>
      <path d="M 660 213 H 713"/>
      <path d="M 995 213 H 1048"/>
      <path d="M 1195 276 V 340 C 1195 420, 1100 463, 1007 463"/>
      <path d="M 725 463 H 672"/>
      <path d="M 390 463 H 337"/>
    </g>
    <g fill="#64748b" stroke="none">
      <path d="M 378 207 L 390 213 L 378 219 Z"/>
      <path d="M 713 207 L 725 213 L 713 219 Z"/>
      <path d="M 1048 207 L 1060 213 L 1048 219 Z"/>
      <path d="M 1007 457 L 995 463 L 1007 469 Z"/>
      <path d="M 672 457 L 660 463 L 672 469 Z"/>
      <path d="M 337 457 L 325 463 L 337 469 Z"/>
    </g>
    </g>'''
    return svg_shell(
        "R5F and RPMsg bring-up order",
        "A seven-stage bring-up sequence validates memory, boot-time reservation, firmware, remoteproc, RPMsg, synthetic transport, and finally camera integration.",
        450,
        body,
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    diagrams = {
        "reserved-memory-map.svg": memory_map(),
        "control-state-machine.svg": control_states(),
        "bringup-flow.svg": bringup_flow(),
    }
    for filename, content in diagrams.items():
        output = OUTPUT_DIR / filename
        output.write_text(content, encoding="utf-8")
        print(f"Generated {output}")


if __name__ == "__main__":
    main()
