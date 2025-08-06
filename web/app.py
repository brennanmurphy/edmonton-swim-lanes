from flask import Flask, render_template, redirect, url_for, request
import sqlite3
import subprocess
from datetime import datetime

app = Flask(__name__, template_folder="")

@app.route("/")
def index():
    try:
        conn = sqlite3.connect("/workspace/scraper/lanes.db")
        c = conn.cursor()
        c.execute("SELECT date, time_block, total_lanes FROM lanes ORDER BY date, time_block")
        rows = c.fetchall()
        conn.close()
    except Exception as e:
        print("❌ Error reading from database:", e)
        rows = []

    # Transform to nested dictionary: data[date][time] = lanes
    data = {}
    all_dates = set()
    all_times = set()

    for date, time, lanes in rows:
        all_dates.add(date)
        all_times.add(time)
        data.setdefault(date, {})[time] = lanes

    sorted_dates = sorted(all_dates)
    sorted_times = sorted(all_times)

    return render_template("index.html", data=data, sorted_dates=sorted_dates, sorted_times=sorted_times)

@app.route("/refresh", methods=["POST"])
def refresh():
    print("🔄 Manual refresh requested. Running scrape.py...")
    try:
        result = subprocess.run(
            ["python3", "/workspace/scraper/scrape.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Scrape complete:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("❌ Error during scrape:\n", e.stderr)
    return redirect(url_for("index"))

if __name__ == "__main__":
    print("🚀 Starting Flask server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
