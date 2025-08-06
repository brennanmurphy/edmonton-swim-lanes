from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import defaultdict
import re
import sqlite3

# === Step 1: Date setup ===
target_dates = [
    (datetime.today() + timedelta(days=i)).strftime('%a%d%b') for i in range(3)
]
excluded_date = (datetime.today() + timedelta(days=3)).strftime('%a%d%b')

print("✅ Collecting data for:", target_dates)
print("⛔️ Excluding rows with date:", excluded_date)

# === Step 2: Headless browser setup ===
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

base_url = "https://movelearnplay.edmonton.ca"
initial_url = f"{base_url}/COE/public/category/browse/KSCLANE"

driver = webdriver.Chrome(options=options)
driver.get(initial_url)

page_number = 1
seen_pages = set()
collected_rows = []

while True:
    print(f"\n--- Scraping page {page_number} ---")

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#classTimetableSchedule .table-bordered"))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.select_one("#classTimetableSchedule .table-bordered")

    if not table:
        print("Table not found.")
        break

    rows = table.find_all("tr")
    any_target_date_on_page = False

    for row in rows:
        cols = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
        if not cols or len(cols) < 1:
            continue
        row_date = cols[0]

        if row_date == excluded_date:
            continue

        if row_date in target_dates:
            collected_rows.append(cols)
            any_target_date_on_page = True

    if not any_target_date_on_page:
        print("No more matching dates on this page. Stopping.")
        break

    # Check for next page
    pagination = soup.select_one("ul.pagination")
    if not pagination:
        print("No pagination found.")
        break

    next_link = pagination.find("a", attrs={"data-page": str(page_number + 1)})
    if not next_link:
        print("No more pages.")
        break

    href = next_link.get("href")
    if not href or href in seen_pages:
        print("Already seen this page or invalid href.")
        break

    seen_pages.add(href)
    driver.get(base_url + href)
    page_number += 1

driver.quit()

# === Step 3: Parse collected rows ===
parsed_rows = []

for row in collected_rows:
    time_str = row[1]
    activity_str = row[2] if len(row) > 2 else ""
    lane_desc = row[3] if len(row) > 3 else ""
    location = row[4] if len(row) > 4 else ""

    # Parse time
    match = re.match(r'^([\d: ]+[APMapm]+) - ([\d: ]+[APMapm]+)(\d+\s+mins)$', time_str)
    if not match:
        continue
    try:
        start_time = datetime.strptime(match.group(1).strip(), "%I:%M %p")
        end_time = datetime.strptime(match.group(2).strip(), "%I:%M %p")
    except ValueError:
        continue

    # Parse date
    date_str = row[0]
    try:
        row_date = datetime.strptime(date_str, "%a%d%b").replace(year=datetime.today().year)
    except ValueError:
        continue

    # Parse lane count
    lane_match = re.search(r'-\s*(\d+)\s+Lanes', activity_str)
    if lane_match:
        lanes = int(lane_match.group(1))
    else:
        lanes = len(re.findall(r'\bmeter\b', lane_desc, flags=re.IGNORECASE))

    parsed_rows.append({
        "date": row_date.date(),
        "start_time": start_time,
        "end_time": end_time,
        "lanes": lanes,
        "activity": activity_str,
        "location": location
    })

# === Step 4: Accumulate lanes per 30-minute block ===
lane_blocks = defaultdict(int)

for entry in parsed_rows:
    current_time = entry["start_time"]
    end_time = entry["end_time"]
    date = entry["date"]
    while current_time < end_time:
        block_key = (date, current_time.strftime("%H:%M"))
        lane_blocks[block_key] += entry["lanes"]
        current_time += timedelta(minutes=15)

# === Step 5: Save results to SQLite ===
db_path = "/workspace/scraper/lanes.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS lanes (
        date TEXT,
        time_block TEXT,
        total_lanes INTEGER,
        PRIMARY KEY (date, time_block)
    )
''')

for (date, time_block), total in lane_blocks.items():
    c.execute('''
        INSERT OR REPLACE INTO lanes (date, time_block, total_lanes)
        VALUES (?, ?, ?)
    ''', (str(date), time_block, total))

conn.commit()
conn.close()

print(f"\n✅ Scrape complete. {len(parsed_rows)} sessions parsed.")
print(f"✅ {len(lane_blocks)} lane time blocks saved to SQLite: {db_path}")
