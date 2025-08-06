# Kinsmen Swim Lane Tracker 🏊

> A small project that lists the open swim lanes at the Kinsmen sport centre as the City of Edmonton's website makes it really hard to understand how many lanes are open at what time.

---

## 📦 What It Does

- Scrapes lane swim schedules from the [City of Edmonton's website](https://movelearnplay.edmonton.ca/)
- Parses lane counts per 15-minute block for the next 3 days
- Saves the data into a SQLite database
- Displays lane availability as a **color-coded heatmap** in a web browser
- Updates daily at 5:00 AM using `cron` inside the Docker container
- Manual "🔄 Refresh" button included for instant updates

---

## 🚀 How to Run

These steps assume you already have Docker installed on your system.

### 1. 📁 Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/kinsmen-lane-tracker.git
cd kinsmen-lane-tracker
```

### 2. 🐳 Build the Docker container

```bash
docker compose build
```

> ⏳ This may take a few minutes the first time as it installs Python, Firefox, GeckoDriver, and all dependencies.

### 3. ▶️ Start the container

```bash
docker compose up -d
```

This will:
- Start the Flask web server
- Run `cron` to schedule daily scraping at 5:00 AM
- Mount your `scraper/lanes.db` SQLite file

---

## 🌐 Where to Access the Site

Once the container is running, open your browser and go to:

```
http://localhost:5000
```

You’ll see a 3-day schedule of swim lanes in a **color-coded heatmap**.
- **Darker blue = more lanes available**
- **Lighter = fewer or no lanes**

Use the 🔄 **Refresh Data** button to manually update the schedule.

---

## ⚙️ Cron Timing

This container includes a cron job to auto-run the scraper at:

```
🕔 5:00 AM every day (container time)
```

You can trigger it manually using the refresh button.

---

## 🧪 Tested With

- Docker 24+
- Python 3.12
- Firefox ESR + GeckoDriver
- Flask 3.x
- Selenium + BeautifulSoup

---

## 📬 License

MIT License.  
Feel free to fork or submit pull requests.