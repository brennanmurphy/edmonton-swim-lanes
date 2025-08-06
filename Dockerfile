FROM python:3.12-slim

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    ca-certificates \
    cron \
    tzdata && \
    ln -fs /usr/share/zoneinfo/America/Edmonton /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && apt-get install -y ./chrome.deb && \
    rm chrome.deb

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{ print $3 }' | cut -d '.' -f 1) && \
    DRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}") && \
    wget -q -O chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${DRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver.zip && \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf chromedriver.zip chromedriver-linux64

COPY crontab.txt /etc/cron.d/lane-cron

# Install Python packages
RUN pip install --no-cache-dir selenium beautifulsoup4 flask

# Install cron job
RUN crontab /etc/cron.d/lane-cron

# Run cron and Flask app
CMD ["bash", "-c", "cron && python3 /workspace/scraper/scrape.py && python3 /workspace/web/app.py"]
