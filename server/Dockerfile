# Multi-stage build for smaller image size
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    python3-dev \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 \
    libjpeg62-turbo \
    libcairo2 \
    fontconfig \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Set the locale
RUN sed -i '/da_DK.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    rm -rf /usr/share/locale/* /usr/share/man/* /usr/share/doc/*
ENV LANG=da_DK.UTF-8 \
    LANGUAGE=da_DK:da \
    LC_ALL=da_DK.UTF-8

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN useradd -m -u 1000 weatherboard && \
    mkdir -p /srv/weatherboard /usr/share/fonts && \
    chown -R weatherboard:weatherboard /srv/weatherboard

WORKDIR /srv/weatherboard

# Copy application code
COPY --chown=weatherboard:weatherboard . .

# Add fonts and clean cache
RUN cp /srv/weatherboard/fonts/Roboto* /usr/share/fonts/ && \
    fc-cache && \
    rm -rf /root/.cache /tmp/*

# Switch to non-root user
USER weatherboard

# Set Python path
ENV PYTHONPATH=/srv/weatherboard/server/ \
    PYTHONUNBUFFERED=1 \
    PORT=80 

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:$PORT/health')" || exit 1

EXPOSE 80

# Use exec form for better signal handling
CMD ["gunicorn", "--bind", ":80", "--workers", "1", "--threads", "8", "--access-logfile", "-", "server:app"]
