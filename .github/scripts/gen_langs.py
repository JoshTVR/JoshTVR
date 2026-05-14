import os, math, json, urllib.request

token = os.environ.get('GH_TOKEN', '')

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "roadmap-action",
        "Authorization": f"Bearer {token}" if token else "",
    })
    with urllib.request.urlopen(req) as r:
        return json.load(r)

repos = fetch("https://api.github.com/users/JoshTVR/repos?per_page=100&type=owner")
public = [r for r in repos if not r.get("fork") and not r.get("private")]

lang_bytes = {}
for repo in public:
    try:
        langs = fetch(f"https://api.github.com/repos/JoshTVR/{repo['name']}/languages")
        for lang, b in langs.items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + b
    except:
        pass

top = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)[:6]
total = sum(b for _, b in top) or 1

COLORS = {
    "TypeScript": "#3178c6", "Python": "#3776ab", "JavaScript": "#f1e05a",
    "CSS": "#563d7c", "HTML": "#e34c26", "C#": "#178600",
    "SQL": "#f59e0b", "HLSL": "#7c3aed", "ShaderLab": "#4f46e5",
    "MDX": "#29b5e8", "Dockerfile": "#2496ed", "Shell": "#89e051",
}
FALLBACK = ["#7c3aed", "#4f46e5", "#2563eb", "#29b5e8", "#34d399", "#f59e0b"]

CX, CY, R = 150, 135, 75
CIRC = 2 * math.pi * R
GAP = 4

segs = []
cum = 0
for i, (lang, b) in enumerate(top):
    pct = b / total
    dash = max(pct * CIRC - GAP, 0)
    color = COLORS.get(lang, FALLBACK[i % len(FALLBACK)])
    segs.append((lang, pct, dash, cum, color))
    cum += pct * CIRC

lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">')
lines.append('  <defs>')
lines.append('    <pattern id="gl" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">')
lines.append('      <circle cx="1" cy="1" r=".8" fill="#21262d"/>')
lines.append('    </pattern>')
lines.append('  </defs>')
lines.append('  <rect width="300" height="300" rx="12" fill="#0d1117"/>')
lines.append('  <rect width="300" height="300" rx="12" fill="url(#gl)"/>')
lines.append(f'  <text x="{CX}" y="20" text-anchor="middle" font-family="\'Courier New\',monospace" font-size="9" fill="#3d444d" letter-spacing="4">LANGUAGES</text>')
lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="#161b22" stroke-width="28"/>')
for lang, pct, dash, start, color in segs:
    lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{color}" stroke-width="26" stroke-dasharray="{dash:.2f} {CIRC:.2f}" stroke-dashoffset="{-start:.2f}" transform="rotate(-90 {CX} {CY})" opacity=".9"/>')
lines.append(f'  <text x="{CX}" y="{CY-10}" text-anchor="middle" font-family="\'Courier New\',monospace" font-size="10" fill="#484f58">repos</text>')
lines.append(f'  <text x="{CX}" y="{CY+12}" text-anchor="middle" font-family="\'Courier New\',monospace" font-size="24" font-weight="bold" fill="#8b949e">{len(public)}</text>')
for i, (lang, pct, _, _, color) in enumerate(segs):
    col = i % 2
    row = i // 2
    lx = 29 + col * 142
    ly = 236 + row * 20
    lines.append(f'  <circle cx="{lx}" cy="{ly-4}" r="4" fill="{color}"/>')
    lines.append(f'  <text x="{lx+10}" y="{ly}" font-family="\'Courier New\',monospace" font-size="10" fill="#8b949e">{lang} <tspan fill="{color}">{pct*100:.1f}%</tspan></text>')
lines.append('</svg>')

with open('langs.svg', 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f"langs.svg generated - {[l for l, _ in top]}")