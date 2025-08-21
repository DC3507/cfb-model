# make_rankings.py
import pandas as pd
from pathlib import Path

# Input and output files
features_path = Path("data/features_with_sp.csv")
rankings_path = Path("data/rankings.csv")

if not features_path.exists():
    raise FileNotFoundError("Missing data/features_with_sp.csv — run earlier steps first.")

df = pd.read_csv(features_path)

# Make sure required columns exist
if "season" not in df.columns:
    df["season"] = 2025
if "team" not in df.columns:
    raise ValueError("'team' column missing in features_with_sp.csv")

# Choose a power metric
if "sp_plus_weighted" in df.columns:
    df["power"] = df["sp_plus_weighted"]
elif "sp_ovr" in df.columns:
    df["power"] = df["sp_ovr"] * 140.0  # fallback scale
else:
    raise ValueError("Need sp_plus_weighted or sp_ovr column.")

# Rank teams within each season
df["rank"] = df.groupby("season")["power"].rank(ascending=False, method="dense").astype(int)

# Keep clean output
out = df[["season", "rank", "team", "power"]].sort_values(["season", "rank"])
rankings_path.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(rankings_path, index=False)

print(f"✅ Wrote {rankings_path.resolve()} with {len(out)} rows")
