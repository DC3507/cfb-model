# model.py — minimal working model that ranks teams using SP+ and saves CSV

import glob, os, yaml
import pandas as pd
import numpy as np

# ---- load config
with open("config.yaml", "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)
W = CFG.get("weights", {})
w_sp = float(W.get("sp_plus", 140.0))

# ---- find latest SP+ file
sp_files = sorted(glob.glob("data/sp_plus_*.csv"))
if not sp_files:
    raise FileNotFoundError("No SP+ file found in data/ (expected sp_plus_YYYY.csv). Run fetch_spplus.py first.")
sp_path = sp_files[-1]
sp = pd.read_csv(sp_path)

# ---- normalize column names across CFBD variants
sp.columns = [c.strip().lower() for c in sp.columns]

def pick(*cands):
    for c in cands:
        if c in sp.columns:
            return c
    return None

# season
season_col = pick("year", "season")
if season_col is None:
    raise ValueError(f"Could not find season/year column in SP+ file. Found columns: {list(sp.columns)}")
sp = sp.rename(columns={season_col: "season"})

# team (sometimes 'team' is nested object in API; but CSV should be plain)
team_col = pick("team")
if team_col is None:
    raise ValueError("Could not find 'team' column in SP+ file.")
sp = sp.rename(columns={team_col: "team"})

# overall rating
ovr_col = pick("rating", "sp", "overall", "sp_rating")
if ovr_col is None:
    raise ValueError("Could not find overall SP+ rating column. Looked for rating/sp/overall.")
sp = sp.rename(columns={ovr_col: "sp_ovr"})

# offense / defense / special teams
off_col = pick("offenserating", "offense_rating", "offense")
def_col = pick("defenserating", "defense_rating", "defense")
st_col  = pick("specialteamsrating", "special_teams_rating", "specialteams", "st")

# Create the columns with NaN if they don't exist, then rename existing
for col, target in [(off_col, "sp_off"), (def_col, "sp_def"), (st_col, "sp_st")]:
    if col is None:
        sp[target] = pd.NA
    else:
        sp = sp.rename(columns={col: target})

# Keep the expected set
sp = sp[["season", "team", "sp_ovr", "sp_off", "sp_def", "sp_st"]].copy()

sp = sp[["season","team","sp_ovr","sp_off","sp_def","sp_st"]].copy()

# ---- z-score SP+ per season
def zscore(series: pd.Series) -> pd.Series:
    s = series.astype(float)
    std = s.std(ddof=0)
    if std == 0 or pd.isna(std):
        return (s - s.mean())  # all zeros if constant
    return (s - s.mean()) / std

sp["z_sp_ovr"] = sp.groupby("season")["sp_ovr"].transform(zscore)

# ---- minimal “power” = weighted z(SP+)
sp["power"] = w_sp * sp["z_sp_ovr"]
sp["rank"]  = sp.groupby("season")["power"].rank(ascending=False, method="dense").astype(int)

# ---- save output
os.makedirs("data", exist_ok=True)
out_cols = ["season","rank","team","power","sp_ovr","sp_off","sp_def","sp_st"]
sp[out_cols].sort_values(["season","rank"]).to_csv("data/team_power.csv", index=False)

print("✅ Wrote data/team_power.csv")
