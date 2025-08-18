import requests
import json
from datetime import datetime, timedelta

ZONE = "SE3"
BASE_URL = "https://www.elprisetjustnu.se/api/v1/prices"

def fetch_prices(date, zone):
    url = f"{BASE_URL}/{date.year}/{date.strftime('%m-%d')}_{zone}.json"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Inga data för {date}")
        return None
    return r.json()

def process_data(raw):
    hours = [h["time_start"] for h in raw]
    prices = [h["SEK_per_kWh"] * 100 for h in raw]  # till öre
    mean_price = sum(prices) / len(prices)
    return hours, prices, mean_price

def main():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    today_raw = fetch_prices(today, ZONE)
    tomorrow_raw = fetch_prices(tomorrow, ZONE)

    data = {}
    if today_raw:
        h, p, m = process_data(today_raw)
        data["today_hours"] = h
        data["today_prices"] = p
        data["today_mean"] = m

    if tomorrow_raw:
        h, p, m = process_data(tomorrow_raw)
        data["tomorrow_hours"] = h
        data["tomorrow_prices"] = p
        data["tomorrow_mean"] = m

    data["generated_at"] = datetime.now().isoformat()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
