import csv
import requests
from fastapi import FastAPI

CSV_URL = "https://raw.githubusercontent.com/<username>/<repo>/main/JumboBoxes.csv"

def locate_box(lat, lon):
    r = requests.get(CSV_URL)
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

app = FastAPI()

@app.get("/locate")
def locate(lat: float, lon: float):
    return {"box": locate_box(lat, lon)}
