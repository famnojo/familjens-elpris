import requests
import datetime
import json

BIDDING_ZONE = "SE3"

def fetch_prices(zone: str, date: datetime.date):
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{date.year}/{date.strftime('%m-%d')}_{zone}.json"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Inga data för {zone} {date}")
        return None

    data = r.json()
    hours = [entry["time_start"] for entry in data]
    prices = [entry["SEK_per_kWh"] * 100 for entry in data]  # öre/kWh
    mean_price = sum(prices) / len(prices) if prices else 0

    return {
        "hours": hours,
        "prices_ore_per_kwh": prices,
        "mean_ore_per_kwh": mean_price
    }

def main():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    today_data = fetch_prices(BIDDING_ZONE, today)
    tomorrow_data = fetch_prices(BIDDING_ZONE, tomorrow)

    out = {
        "generated_at": datetime.datetime.now().isoformat(),
        "today": today_data,
        "tomorrow": tomorrow_data
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("✅ data.json uppdaterad")

if __name__ == "__main__":
    main()
