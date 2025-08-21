# merge_sp_into_features.py
# - If data/features.csv exists: merge SP+ into it
# - If it doesn't: build a minimal features set from team_power.csv
import os
import pandas as pd
import yaml

FEATURES_PATH = "data/features.csv"        # your existing features file (if you have one)
TEAM_POWER_PATH = "data/team_power.csv"    # created by model.py
OUT_PATH = "data/features_with_sp.csv"

if not os.path.exists(TEAM_POWER_PATH):
    raise FileNotFoundError("team_power.csv not found. Run: python model.py first.")

# Load team_power (contains season, team, sp_ovr, etc.)
tp = pd.read_csv(TEAM_POWER_PATH)
current_season = int(tp["season"].max())
tp_cur = tp[tp["season"] == current_season].copy()

# Load existing features, or create a minimal one from team list
if os.path.exists(FEATURES_PATH):
    features = pd.read_csv(FEATURES_PATH)
    # if features has season, keep current season rows
    if "season" in features.columns:
        features = features[features["season"] == current_season]
else:
    # minimal starter: just team + season
    features = tp_cur[["team"]].drop_duplicates().copy()
    features["season"] = current_season

# Load weight from config.yaml (optional; default 140 if missing)
w_sp = 140.0
if os.path.exists("config.yaml"):
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
        w_sp = float(((cfg.get("weights") or {}).get("sp_plus")) or w_sp)

# Merge SP+ (overall) into features, compute weighted contribution
out = features.merge(tp_cur[["team", "sp_ovr"]], on="team", how="left")
out["sp_ovr"] = out["sp_ovr"].fillna(0.0)
out["sp_plus_weighted"] = out["sp_ovr"] * w_sp

# Save
os.makedirs("data", exist_ok=True)
out.to_csv(OUT_PATH, index=False)
print(f"✅ Wrote {OUT_PATH} for season {current_season}. Rows: {len(out)}")
