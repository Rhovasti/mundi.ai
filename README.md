# Eno-Mundi

> **Fantasy World GIS Platform**: Built on [BuntingLabs/mundi.ai](https://github.com/BuntingLabs/mundi.ai), Eno-Mundi is a specialized GIS platform for exploring the Eno fantasy world with interactive maps, detailed geography, and AI-native features. All credit for the original Mundi platform goes to BuntingLabs and contributors.

<h4 align="center">
  <a href="https://github.com/BuntingLabs/mundi.ai/actions/workflows/cicd.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/BuntingLabs/mundi.ai/cicd.yml?label=CI" alt="GitHub Actions Workflow Status" />
  </a>
  <a href="https://github.com/BuntingLabs/mundi.ai/actions/workflows/ruff.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/BuntingLabs/mundi.ai/ruff.yml?label=Lint" alt="GitHub Actions Lint Status" />
  </a>
  <a href="https://discord.gg/V63VbgH8dT">
    <img src="https://dcbadge.limes.pink/api/server/V63VbgH8dT?style=plastic" alt="Discord" />
  </a>
  <a href="https://github.com/BuntingLabs/mundi.ai/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/BuntingLabs/mundi.ai" alt="GitHub License" />
  </a>
</h4>

![Mundi](./docs/src/assets/social.png)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 4GB+ RAM recommended

### Get Started
```bash
# Clone the Eno-Mundi repository
git clone https://github.com/Rhovasti/Eno-Mundi.git
cd Eno-Mundi

# Initialize submodules
git submodule update --init --recursive

# Copy environment configuration
cp .env.example .env

# Build and start (may take 30-60 minutes on first run)
docker compose build
docker compose up app
```

Access Eno-Mundi at **http://localhost:8000**

### Exploring the Eno Fantasy World
Once running, navigate to the Eno project:
- **Main Eno Map**: http://localhost:8000/project/BxvFhuzMcnuy
- **Features**: Interactive fantasy geography with cities, villages, rivers, lakes, biomes, and roads
- **Coordinate System**: Professional EPSG:3857 (Web Mercator) projection with proper alignment

### Development Mode
```bash
# Start with hot reload and exposed service ports
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up app
```

## 🌍 Eno Fantasy World Features

### Geographic Data
- **Custom Relief Map**: High-resolution topographic imagery of the Eno world
- **Fantasy Cities**: Major settlements with detailed population and cultural data
- **Villages**: Smaller communities scattered across the landscape  
- **Natural Features**: Rivers, lakes, and diverse biomes
- **Infrastructure**: Road networks connecting settlements
- **Political Boundaries**: States and regions with fantasy governance

### Technical Specifications
- **Coordinate System**: EPSG:3857 (Web Mercator) for web compatibility
- **Vector Data**: GeoJSON format with proper georeferencing
- **Basemap Provider**: MapTiler integration (temporary solution)
- **Future Plans**: Migration to self-hosted tile server for full open-source solution

## 🔗 Project Information

- **Based On**: [BuntingLabs/mundi.ai](https://github.com/BuntingLabs/mundi.ai)
- **Purpose**: Fantasy world GIS platform for the Eno universe
- **License**: AGPLv3 (maintained from original)
- **Attribution**: Full credit to BuntingLabs for the original Mundi.ai platform

## Documentation

### Eno-Mundi Specific
- **Main Project URL**: http://localhost:8000/project/BxvFhuzMcnuy
- **API Endpoints**: 
  - Vector layers: `http://localhost:8000/api/eno/vector`
  - Cities: `http://localhost:8000/api/eno/vector/cities`
  - Rivers: `http://localhost:8000/api/eno/vector/rivers`
  - And more...

### Original Mundi Documentation
For general platform guidance:
- [Making your first map](https://docs.mundi.ai/getting-started/making-your-first-map/)
- [Self-hosting Mundi](https://docs.mundi.ai/guides/self-hosting-mundi/)
- [Connecting to PostGIS](https://docs.mundi.ai/guides/connecting-to-postgis/)

Find more at [docs.mundi.ai](https://docs.mundi.ai).

## Technical Architecture

### Current Implementation
- **Backend**: Python/FastAPI with PostgreSQL + PostGIS
- **Frontend**: React 18 + TypeScript + MapLibre GL
- **Coordinate System**: EPSG:3857 (Web Mercator)
- **Vector Data**: GeoJSON with proper georeferencing
- **Basemap**: MapTiler (temporary proprietary solution)

### Future Roadmap
- **Self-hosted Tiles**: Replace MapTiler with open-source tile server
- **Local Coordinate Pipeline**: Implement transformation from original Eno data
- **Enhanced Fantasy Features**: Expanded world-building tools and AI integration
- **Performance Optimization**: Improved loading for large fantasy datasets

## License

Mundi is licensed as [AGPLv3](./LICENSE).
