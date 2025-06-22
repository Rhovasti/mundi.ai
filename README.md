# Mundi Fork

> **Note**: This is a fork of [BuntingLabs/mundi.ai](https://github.com/BuntingLabs/mundi.ai) - an open source, AI-native web GIS platform. All credit for the original work goes to BuntingLabs and contributors.

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
# Clone this fork
git clone https://github.com/Rhovasti/mundi.ai.git
cd mundi.ai

# Initialize submodules
git submodule update --init --recursive

# Copy environment configuration
cp .env.example .env

# Build and start (may take 30-60 minutes on first run)
docker compose build
docker compose up app
```

Access Mundi at **http://localhost:8000**

### Development Mode
```bash
# Start with hot reload and exposed service ports
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up app
```

## 🔗 Fork Information

- **Original Repository**: [BuntingLabs/mundi.ai](https://github.com/BuntingLabs/mundi.ai)
- **Fork Purpose**: Enhanced development environment and additional features
- **License**: AGPLv3 (maintained from original)
- **Attribution**: Full credit to BuntingLabs for the original Mundi.ai platform

## Documentation

Get started with Mundi using our guides:

- [Making your first map](https://docs.mundi.ai/getting-started/making-your-first-map/)
- [Self-hosting Mundi](https://docs.mundi.ai/guides/self-hosting-mundi/)
- [Connecting to PostGIS](https://docs.mundi.ai/guides/connecting-to-postgis/)

Find more at [docs.mundi.ai](https://docs.mundi.ai).

## Comparing open source Mundi and cloud/enterprise Mundi

Mundi has both open source and cloud/enterprise versions. This is because we think the future
of GIS software is open source and AI-native, while enabling corporations to sponsor its development.

|                        | Open source Mundi        | Mundi Cloud / Enterprise         |
|------------------------|--------------------------|----------------------------------|
| Third-party services   | None                     | Integrated                       |
| Optimized for          | Local/open LLMs          | Frontier & proprietary models    |
| Multiplayer?           | Single player            | Team collaboration               |
| Support                | Community                | SLAs available                   |
| License                | AGPLv3                   | Commercial                       |

## License

Mundi is licensed as [AGPLv3](./LICENSE).
