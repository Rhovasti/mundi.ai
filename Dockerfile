# tippecanoe
FROM node:20-bookworm AS tippecanoe-builder
ARG TIPPECANOE_TAG=2.77.0
RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential libsqlite3-dev zlib1g-dev \
    && git clone --depth 1 --branch ${TIPPECANOE_TAG} https://github.com/felt/tippecanoe /tmp/tippecanoe \
    && make -C /tmp/tippecanoe -j$(nproc) && make -C /tmp/tippecanoe install \
    && rm -rf /tmp/tippecanoe \
    && apt-get purge -y git build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# maplibre
FROM node:20-bookworm AS maplibre-builder
ARG MAPLIBRE_TAG=node-v6.1.0
WORKDIR /opt
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && git clone --depth 1 --recursive --branch ${MAPLIBRE_TAG} \
        https://github.com/maplibre/maplibre-native.git \
    && apt-get purge -y git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/maplibre-native/platform/node
RUN npm ci && npm pack --silent

# base runtime
FROM node:20-bookworm AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
        gdal-bin python3-gdal \
        libcairo2-dev libgles2-mesa-dev libgbm-dev \
        libuv1-dev libprotobuf-dev xserver-xorg-core xvfb x11-utils dbus xauth \
        python3-apt \
    && rm -rf /var/lib/apt/lists/*

COPY --from=tippecanoe-builder /usr/local/bin/tippecanoe* /usr/local/bin/

# tools / deps
FROM base AS tools
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y --no-install-recommends wget libpng-dev \
    && npm install -g @maplibre/maplibre-gl-style-spec \
    && wget -qO /tmp/pmtiles.tar.gz \
         https://github.com/protomaps/go-pmtiles/releases/download/v1.25.3/go-pmtiles_1.25.3_Linux_x86_64.tar.gz \
    && tar -xzf /tmp/pmtiles.tar.gz -C /usr/local/bin && chmod +x /usr/local/bin/pmtiles \
    && rm /tmp/pmtiles.tar.gz

# python/uv
FROM tools AS python-builder
COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install development headers for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgdal-dev python3-dev build-essential \
        libdbus-1-dev libdbus-glib-1-dev pkg-config \
        libgirepository1.0-dev libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv && \
    uv pip install -r requirements.txt && \
    uv pip install hyperdx-opentelemetry && \
    uv pip install opentelemetry-instrumentation-fastapi==0.55b1

# frontend app
FROM node:20-bookworm AS frontend-builder
WORKDIR /app/frontendts
COPY frontendts/package*.json ./
RUN npm install
ARG VITE_WEBSITE_DOMAIN
ARG VITE_EMAIL_VERIFICATION
COPY frontendts/ ./
ENV VITE_WEBSITE_DOMAIN=$VITE_WEBSITE_DOMAIN
ENV VITE_EMAIL_VERIFICATION=$VITE_EMAIL_VERIFICATION
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN VITE_WEBSITE_DOMAIN=${VITE_WEBSITE_DOMAIN} npx tsc -b && npx vite build && npm prune --production

# final stage
FROM tools AS final
WORKDIR /app

# Install legacy libraries for MapLibre compatibility
RUN dpkgArch="$(dpkg --print-architecture)" && \
    wget -qO /tmp/multiarch.deb \
      http://snapshot.debian.org/archive/debian/20190501T215844Z/pool/main/g/glibc/multiarch-support_2.28-10_${dpkgArch}.deb && \
    wget -qO /tmp/libjpeg8.deb \
      http://snapshot.debian.org/archive/debian/20141009T042436Z/pool/main/libj/libjpeg8/libjpeg8_8d1-2_${dpkgArch}.deb && \
    wget -qO /tmp/libicu70.deb \
      http://archive.ubuntu.com/ubuntu/pool/main/i/icu/libicu70_70.1-2ubuntu1_${dpkgArch}.deb && \
    wget -qO /tmp/libpng.deb \
      http://ftp.debian.org/debian/pool/main/libp/libpng1.6/libpng16-16_1.6.37-3_${dpkgArch}.deb && \
    apt-get purge -y libpng-dev && \
    apt-get update && \
    apt-get install -y /tmp/multiarch.deb /tmp/libjpeg8.deb /tmp/libicu70.deb && \
    dpkg -i /tmp/libpng.deb && \
    rm /tmp/*.deb && rm -rf /var/lib/apt/lists/*

# Install MapLibre and Node dependencies
COPY --from=maplibre-builder /opt/maplibre-native/platform/node/*.tgz /tmp/
RUN --mount=type=cache,target=/root/.npm \
    npm install --production --ignore-scripts /tmp/*.tgz \
    && npm install --production sharp @mapbox/geo-viewport \
    && rm -rf /tmp/*.tgz

# Copy Python virtual environment from builder
COPY --from=python-builder /app/.venv /app/.venv
COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application files
COPY . /app/
COPY --from=frontend-builder /app/frontendts/dist /app/frontendts/dist

# Setup environment
ENV DISPLAY=:99 \
    LANG=en_US.UTF-8 \
    PYTHONPATH="/app:/usr/lib/python3/dist-packages" \
    LD_LIBRARY_PATH=/usr/lib

CMD ["python", "-m", "src.wsgi"]
