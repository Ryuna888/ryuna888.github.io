from pathlib import Path
import base64
import re

root = Path(__file__).resolve().parents[1]
index_path = root / "index.html"
assets = root / "assets"
assets.mkdir(exist_ok=True)

html = index_path.read_text(encoding="utf-8")
pattern = re.compile(r'data:image/([a-zA-Z0-9.+-]+);base64,([^\"\']+)')
matches = list(pattern.finditer(html))

if len(matches) < 2:
    raise SystemExit(f"Expected at least 2 embedded images, found {len(matches)}")

outputs = [
    (assets / "portrait.jpg", "assets/portrait.jpg"),
    (assets / "kagerou-no-uma.png", "assets/kagerou-no-uma.png"),
]

replacements = []
for i, m in enumerate(matches):
    if i >= len(outputs):
        raise SystemExit(f"Unexpected extra embedded image at position {i+1}")
    out_path, public_path = outputs[i]
    out_path.write_bytes(base64.b64decode(m.group(2)))
    replacements.append(public_path)

it = iter(replacements)
html = pattern.sub(lambda _: next(it), html)

threads_url = "https://www.threads.com/@ryuna.8.krm?igshid=NTc4MTIwNjQ2YQ=="
instagram_json = '        "https://www.instagram.com/ryuna.8.krm/",'
if threads_url not in html:
    html = html.replace(instagram_json, instagram_json + f'\n        "{threads_url}",', 1)

instagram_link = '<a class="soon-badge" href="https://www.instagram.com/ryuna.8.krm/" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">Instagram</a>'
threads_link = f'<a class="soon-badge" href="{threads_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">Threads</a>'
if threads_link not in html:
    html = html.replace(instagram_link, instagram_link + "\n            " + threads_link, 1)

masterledger = "https://ryuna888.github.io/MasterLedger/"
if masterledger not in html:
    raise SystemExit("MasterLedger public URL not found in homepage")
if "HARATA KAZUYA" not in html or "HATATA KAZUYA" in html:
    raise SystemExit("Name spelling safety check failed")
if "data:image" in html:
    raise SystemExit("Embedded image data remains after conversion")

index_path.write_text(html, encoding="utf-8")

for p in [assets / ".gitkeep", assets / "portrait-placeholder.txt"]:
    if p.exists():
        p.unlink()

print(f"index.html: {index_path.stat().st_size} bytes")
print(f"portrait.jpg: {(assets / 'portrait.jpg').stat().st_size} bytes")
print(f"kagerou-no-uma.png: {(assets / 'kagerou-no-uma.png').stat().st_size} bytes")
print("Homepage image extraction and link checks completed.")
