FROM python:3.12-slim

ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# ------------------------
# System deps
# ------------------------
RUN apt-get update && apt-get install -y \
    curl wget unzip gnupg ca-certificates \
    xvfb libxi6 libnss3 libgdk-pixbuf-2.0-0 \
    libxss1 libasound2 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# ------------------------
# Chrome + Chromedriver
# ------------------------
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) && \
    LATEST=$(wget -qO- https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}) && \
    wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${LATEST}/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64*

# ------------------------
# Python deps
# ------------------------
COPY backend/requirements.txt .
COPY backend/requirements-test.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-test.txt

# ------------------------
# App + tests
# ------------------------
COPY backend /app/backend
COPY tests /app/tests

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "backend.app:app"]
