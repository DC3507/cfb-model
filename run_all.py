import subprocess

if __name__ == "__main__":
    subprocess.run(["python", "update_pipeline.py"], check=True)
    subprocess.run(["python", "model.py"], check=True)
    subprocess.run(["python", "backtest.py"], check=True)
