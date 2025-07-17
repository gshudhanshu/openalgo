# ------------------------------ Builder Stage ------------------------------ #
FROM python:3.13-bookworm AS builder

# Install Node.js for CSS build process
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && apt-get install -y --no-install-recommends \
        curl build-essential nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package.json and install Node.js dependencies
COPY package*.json ./
RUN npm install

# Copy source files needed for CSS build
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY src/ ./src/
COPY templates/ ./templates/

# Create static directory and build CSS using PostCSS/Tailwind
RUN echo "🎨 Building Tailwind CSS..." && \
    mkdir -p static/css && \
    npm run build:css && \
    echo "✅ CSS build completed" && \
    ls -la static/css/ && \
    echo "📄 CSS file size:" && \
    wc -c static/css/main.css || echo "❌ CSS build failed"

# Copy Python dependencies and build
COPY pyproject.toml .

# create isolated virtual-env with uv, then add gunicorn + eventlet
RUN pip install --no-cache-dir uv && \
    uv venv .venv && \
    uv pip install --upgrade pip && \
    uv sync && \
    uv pip install gunicorn eventlet && \
    rm -rf /root/.cache
# --------------------------------------------------------------------------- #


# ------------------------------ Production Stage --------------------------- #
FROM python:3.13-slim-bookworm AS production

# 0 – set timezone to IST (Asia/Kolkata) and install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends tzdata curl && \
    ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 1 – user & workdir
RUN useradd --create-home appuser
WORKDIR /app

# 2 – copy the ready-made venv and source with correct ownership
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser . .

# 2.1 – copy built CSS files from builder stage (overwriting any existing files)
COPY --from=builder --chown=appuser:appuser /app/static/css/main.css /app/static/css/main.css

# 2.2 – verify CSS file was copied correctly
RUN echo "🔍 Verifying CSS file..." && \
    ls -la /app/static/css/main.css && \
    echo "📄 Production CSS file size:" && \
    wc -c /app/static/css/main.css && \
    echo "✅ CSS verification completed"

# 3 – create required directories with proper ownership
RUN mkdir -p /app/logs /app/db && \
    chown -R appuser:appuser /app/logs /app/db

# 4 – entrypoint script and fix line endings
COPY --chown=appuser:appuser start.sh /app/start.sh
RUN sed -i 's/\r$//' /app/start.sh && chmod +x /app/start.sh

# ---- RUNTIME ENVS --------------------------------------------------------- #
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Kolkata
# --------------------------------------------------------------------------- #

USER appuser
EXPOSE 5000
CMD ["/app/start.sh"]
