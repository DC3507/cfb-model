import subprocess, sys

def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    run([sys.executable, "fetch_spplus.py"])            # pulls SP+
    run([sys.executable, "model.py"])                   # writes data/team_power.csv
    run([sys.executable, "merge_sp_into_features.py"])  # writes data/features_with_sp.csv
    run([sys.executable, "make_rankings.py"])           # writes data/rankings.csv
    # Optional:
    # run([sys.executable, "backtest.py"])
