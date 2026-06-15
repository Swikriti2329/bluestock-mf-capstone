import requests
import pandas as pd
from pathlib import Path
import time

RAW = Path("data/raw")

SCHEMES = {
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Pru_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip",
}

def fetch_nav(amfi_code, scheme_name):
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        df = pd.DataFrame(data["data"])
        df["amfi_code"] = amfi_code
        df["scheme_name"] = data["meta"]["scheme_name"]
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)
        out_path = RAW / f"live_nav_{scheme_name}.csv"
        df.to_csv(out_path, index=False)
        print(f"✅  {scheme_name}: {len(df)} rows | Latest NAV: Rs.{df['nav'].iloc[-1]:.2f}")
        return df
    except Exception as e:
        print(f"❌  {scheme_name}: Failed — {e}")
        return None

if __name__ == "__main__":
    print("🌐  Live NAV Fetcher — mfapi.in")
    print("="*45)
    for code, name in SCHEMES.items():
        fetch_nav(code, name)
        time.sleep(1)
    print("\n✅  Live NAV fetch complete!")
