#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Hämtar SE3-priser för idag + (om publicerat) imorgon från elprisetjustnu.se
# och skriver båda dagarna till data.json i det format som index.html använder.

import json
import datetime as dt
import requests

ZONE = "SE3"
OUT_PATH = "data.json"

def fetch_day(zone: str, date: dt.date):
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{date:%Y}/{date:%m-%d}_{zone}.json"
    r = requests.get(url, timeout=20)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    items = r.json()  # lista av timmar
    hours = [it["time_start"] for it in items]  # ISO8601 (UTC)
    # SEK/kWh -> öre/kWh
    prices_ore = [float(it["SEK_per_kWh"]) * 100.0 for it in items]
    mean_ore = (sum(prices_ore) / len(prices_ore)) if prices_ore else 0.0
    return {
        "hours": hours,
        "prices_ore_per_kwh": prices_ore,
        "mean_ore_per_kwh": mean_ore
    }

def main():
    # svensk tid i stämpeln
    generated_at = dt.datetime.now(dt.timezone(dt.timedelta(hours=2))).isoformat()
    today = dt.date.today()
    tomorrow = today + dt.timedelta(days=1)

    today_data = fetch_day(ZONE, today)
    tomorrow_data = fetch_day(ZONE, tomorrow)  # kan vara None innan publicering

    out = {
        "generated_at": generated_at,
        "today": today_data or {"hours": [], "prices_ore_per_kwh": [], "mean_ore_per_kwh": 0},
        "tomorrow": tomorrow_data or {"hours": [], "prices_ore_per_kwh": [], "mean_ore_per_kwh": 0}
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("✅ Skrev data.json (idag + imorgon om tillgängligt)")

if __name__ == "__main__":
    main()
