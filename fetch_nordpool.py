#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Root-only variant: run this on your computer to generate a fresh data.json,
# then upload that single file to GitHub (root). No GitHub Actions required.
import os, json, datetime as dt, pytz
import pandas as pd
from nordpool import elspot

BIDDING_ZONE = "SE3"
CURRENCY = "SEK"
TZ = pytz.timezone("Europe/Stockholm")
HOURS_AHEAD = 36
WINDOWS = [1,2,3]
TOP_K = 3
OUT_PATH = os.path.join(os.path.dirname(__file__), "data.json")  # root

def fetch_prices(zone: str, hours: int):
    spot = elspot.Prices()
    data = spot.hourly(areas=[zone], currency=CURRENCY)
    df = pd.DataFrame(data['areas'][zone]['values'])
    df['start'] = pd.to_datetime(df['start']).dt.tz_convert(TZ)
    df['end'] = pd.to_datetime(df['end']).dt.tz_convert(TZ)
    df = df.sort_values('start').reset_index(drop=True)
    now = dt.datetime.now(TZ)
    future = df[df['end'] >= now].head(hours)
    return future

def compute_windows(series, durations, top_k=3):
    res = {}
    vals = series.values
    for N in durations:
        if N <= 0 or N > len(vals):
            continue
        s = pd.Series(vals).rolling(N).sum().dropna().values
        order = s.argsort()[:top_k]
        items = []
        for idx in order:
            start_idx = int(idx)
            end_idx = start_idx + N
            start_ts = series.index[start_idx]
            end_ts = series.index[end_idx-1] + pd.Timedelta(hours=1)
            avg_price = s[start_idx] / N
            items.append({
                "start": start_ts.isoformat(),
                "end": end_ts.isoformat(),
                "avg_ore_per_kwh": float(avg_price)
            })
        res[N] = items
    return res

def main():
    df = fetch_prices(BIDDING_ZONE, HOURS_AHEAD)
    series = pd.Series(df['value'].astype(float).values, index=df['start'])
    mean_val = float(series.mean())
    out = {
        "generated_at": dt.datetime.now(TZ).isoformat(),
        "bidding_zone": BIDDING_ZONE,
        "hours": [ts.isoformat() for ts in series.index],
        "prices_ore_per_kwh": [float(v) for v in series.values],
        "mean_ore_per_kwh": mean_val,
        "windows": compute_windows(series, WINDOWS, TOP_K)
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Skrev {OUT_PATH}. Ladda upp den till GitHub-repots rot för att uppdatera sidan.")

if __name__ == "__main__":
    main()
