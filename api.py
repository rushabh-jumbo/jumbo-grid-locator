import csv
import requests
from fastapi import FastAPI, HTTPException

# Replace these after pushing to GitHub
CSV_URL = "https://raw.githubusercontent.com/<username>/<repo>/main/JumboBoxes.csv"

app = FastAPI()

def locate_box(lat, lon):
    r = requests.get(CSV_URL)
    r.raise_for_status()
    lines = r.text.splitlines()
    reader = csv.DictReader(lines)

    for row in reader:
        if (
            lat <= float(row["MaxLat"]) and
            lat > float(row["MinLat"]) and
            lon >= float(row["MinLon"]) and
            lon < float(row["MaxLon"])
        ):
            return row["BoxID"]
    return ""


@app.get("/locate")
def locate(coords: str):
    """
    Use like:
    /locate?coords=12.91614,77.67739
    """
    try:
        lat_str, lon_str = coords.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
    except:
        raise HTTPException(status_code=400, detail="Invalid coords format. Use 'lat,lon'.")

    box = locate_box(lat, lon)
    return {"box": box}
