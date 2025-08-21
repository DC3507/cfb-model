import requests
import pandas as pd
import os

def fetch_spplus(year=2025, outdir="./data"):
    url = f"https://api.collegefootballdata.com/ratings/sp?year={year}"
    headers = {"Authorization": f"Bearer {os.environ['CFBD_API_KEY']}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    os.makedirs(outdir, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(f"{outdir}/sp_plus_{year}.csv", index=False)
    print(f"✅ Saved SP+ data for {year} to {outdir}/sp_plus_{year}.csv")

if __name__ == "__main__":
    fetch_spplus(year=2025)
