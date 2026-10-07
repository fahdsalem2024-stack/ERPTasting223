FROM python:3.12-slim

WORKDIR /app

# Install system deps + Google Chrome
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip ca-certificates \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
    libgbm1 libasound2 libxshmfence1 libxdamage1 \
    libcups2 libpango-1.0-0 libcairo2 libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Add Google Chrome signing key (modern method - no apt-key)
RUN wget -q -O /usr/share/keyrings/google-chrome.asc \
    https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.asc] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create directories
RUN mkdir -p reports/results reports/screenshots logs config/schedules web/static/uploads

# Expose port
EXPOSE 5000

# Run
CMD ["python", "web/app.py"]
