#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Hämtar SE3-priser för idag + (om tillgängligt) imorgon från elprisetjustnu.se
# och skriver båda dagarna tydligt separerade i data.json (root).
import json, datetime as dt, pytz, requests
import pandas as pd

ZONE = "SE3"
TZ = pytz.timezone("Europe/Stockholm")
OUT_PATH = "data.json"

def fetch_day(d: dt.datetime):
    """Hämta en dags priser för ZONE. Returnerar DataFrame med kolumner start,end,value(öre)."""
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{d:%Y}/{d:%m-%d}_{ZONE}.json"
    r = requests.get(url, timeout=20)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    items = r.json()
    df = pd.DataFrame(items)
    # API ger ISO8601 UTC
    df["start"] = pd.to_datetime(df["time_start"], utc=True).dt.tz_convert(TZ)
    df["end"]   = pd.to_datetime(df["time_end"],   utc=True).dt.tz_convert(TZ)
    # SEK/kWh -> öre/kWh
    df["value"] = (df["SEK_per_kWh"].astype(float) * 100.0)
    return df[["start","end","value"]].sort_values("start").reset_index(drop=True)

def to_payload(df: pd.DataFrame, now: dt.datetime):
    """Bygger JSON-struktur för en dag: visar resterande timmar om 'idag', annars alla timmar."""
    if df is None or df.empty:
        return {"date":"", "hours":[], "prices_ore_per_kwh":[], "mean_ore_per_kwh":0}
    # Om dagen är idag: visa från nu och framåt; annars alla timmar
    is_today = (df["start"].iloc[0].date() == now.date())
    use = df[df["end"] >= now] if is_today else df
    hours = [ts.isoformat() for ts in use["start"]]
    prices = [float(v) for v in use["value"]]
    mean_all = float(df["value"].mean())  # dygnsmedel (på hela dygnet)
    date_str = df["start"].iloc[0].date().isoformat()
    return {
        "date": date_str,
        "hours": hours,
        "prices_ore_per_kwh": prices,
        "mean_ore_per_kwh": mean_all
    }

def main():
    now = dt.datetime.now(TZ)
    today = fetch_day(now)
    tomorrow = fetch_day(now + dt.timedelta(days=1))  # kan vara None innan publicering

    payload = {
        "generated_at": now.isoformat(),
        "bidding_zone": ZONE,
        "today": to_payload(today, now),
        "tomorrow": to_payload(tomorrow, now) if tomorrow is not None else {
            "date":"", "hours":[], "prices_ore_per_kwh":[], "mean_ore_per_kwh":0
        }
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Klart: skrev {OUT_PATH}")

if __name__ == "__main__":
    main()
