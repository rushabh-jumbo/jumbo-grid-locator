import csv
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

# Public CSV stored in your GitHub repo
CSV_URL = "https://raw.githubusercontent.com/rushabh-jumbo/jumbo-grid-locator/main/JB-grids.csv"

app = FastAPI()

def locate_box(lat: float, lon: float) -> str:
    r = requests.get(CSV_URL, timeout=10)
    r.raise_for_status()
    reader = csv.DictReader(r.text.splitlines())

    for row in reader:
        top_left_lat = float(row["top_left_lat"])
        bottom_left_lat = float(row["bottom_left_lat"])
        top_left_lon = float(row["top_left_lon"])
        top_right_lon = float(row["top_right_lon"])

        if (
            lat <= top_left_lat and
            lat >= bottom_left_lat and
            lon >= top_left_lon and
            lon <= top_right_lon
        ):
            return row["grid_id"]

    return ""


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Jumbo Grid Locator</title>

<style>
body { font-family: system-ui, Arial, sans-serif; max-width: 580px; margin: 48px auto; padding: 0 16px; color:#111; }
h1 { font-size: 22px; font-weight:600; margin-bottom: 12px; text-align:center; }
#logo { display:block; margin:0 auto 24px; height:64px; }
label { display:block; margin:14px 0 6px; font-weight:600; }
input { width:100%; padding:10px; border:1px solid #ccc; border-radius:8px; font-size:14px; }
button { margin-top:20px; padding:12px 14px; width:100%; border:0; border-radius:8px; background:#111827; color:#fff; font-weight:600; cursor:pointer; font-size:15px; }
#out { margin-top:20px; padding:14px; background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px; white-space:pre-wrap; font-size:15px; }
small { color:#6b7280; font-size:13px; line-height:1.45; display:block; margin-bottom:12px; }
</style>
</head>
<body>

<img id="logo" src="https://res.cloudinary.com/dewcjgpc7/image/upload/v1749615389/app-logo-text_srpmgr.webp" alt="App Logo" />

<h1>Jumbo Grid Locator</h1>

<small>
<b>How to copy Latitude & Longitude from Google Maps:</b><br><br>
1. Search the building in Google Maps<br>
2. Place a pin on the **exact** building (tap once on mobile / left-click on desktop)<br>
3. **Right-click on the pin** → Click the **first row** (this copies the lat,long)<br>
4. Paste directly into the first input below (e.g. <i>12.91614, 77.67739</i>)<br>
5. Or paste lat & lon separately in both fields
</small>

<label for="lat">Latitude (or paste "lat,lon")</label>
<input id="lat" placeholder="12.916142142189111" />

<label for="lon">Longitude</label>
<input id="lon" placeholder="77.67739598212604" />

<button id="go">Find Grid</button>

<div id="out"></div>

<script>
const latEl = document.getElementById('lat');
const lonEl = document.getElementById('lon');
const outEl = document.getElementById('out');
const btn = document.getElementById('go');

function parseInputs() {
  const trySplit = (v) => {
    if (!v) return null;
    if (v.includes(',')) {
      const [a,b] = v.split(',');
      return { lat: a.trim(), lon: b.trim() };
    }
    return null;
  };
  let lat = latEl.value.trim();
  let lon = lonEl.value.trim();
  const s1 = trySplit(lat);
  const s2 = trySplit(lon);
  if (s1) { lat = s1.lat; lon = s1.lon; }
  else if (s2) { lat = s2.lat; lon = s2.lon; }
  return { lat, lon };
}

async function locate() {
  outEl.textContent = "";
  btn.disabled = true;
  try {
    const { lat, lon } = parseInputs();
    if (!lat || !lon) { outEl.textContent = "Enter latitude and longitude."; return; }
    const coords = `${lat},${lon}`;
    const res = await fetch(`/locate?coords=${encodeURIComponent(coords)}`);
    const data = await res.json();
    outEl.textContent = data.box ? `✅ Grid ID: ${data.box}` : "❌ No grid found at this location.";
  } catch {
    outEl.textContent = "Server error. Try again.";
  } finally {
    btn.disabled = false;
  }
}

btn.addEventListener('click', locate);
[latEl, lonEl].forEach(el => el.addEventListener('keydown', e => { if (e.key === 'Enter') locate(); }));
</script>

</body>
</html>
"""


@app.get("/locate")
def locate(coords: str):
    try:
        lat_str, lon_str = coords.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
    except:
        raise HTTPException(status_code=400, detail="Invalid format. Use /locate?coords=lat,lon")

    return {"box": locate_box(lat, lon)}
