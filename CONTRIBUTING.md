# Contributing to Mundi.ai Fork

Thank you for your interest in contributing to this fork of Mundi.ai! This document provides guidelines for contributing to the development of this enhanced version.

## 🏗️ Development Setup

### Prerequisites
- Docker & Docker Compose
- Git
- GitHub account
- Recommended: 8GB+ RAM for development

### Getting Started
1. **Fork and Clone**
   ```bash
   git clone https://github.com/Rhovasti/mundi.ai.git
   cd mundi.ai
   git submodule update --init --recursive
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env for your local configuration
   ```

3. **Development Environment**
   ```bash
   # Full build (first time)
   docker compose build
   
   # Development mode with hot reload
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up app
   ```

## 🔄 Development Workflow

### Branch Strategy
- `main`: Stable releases
- `development`: Active development branch
- `feature/feature-name`: Feature branches
- `fix/issue-description`: Bug fixes

### Making Changes
1. **Create Feature Branch**
   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/your-feature-name
   ```

2. **Development**
   - Use development Docker Compose for hot reload
   - Backend changes: Edit files in `src/`, server auto-reloads
   - Frontend changes: Edit files in `frontendts/src/`, Vite handles HMR
   - Database changes: Create Alembic migrations

3. **Testing**
   ```bash
   # Run tests
   pytest
   
   # Run specific test categories
   pytest -m s3        # S3/MinIO tests
   pytest -m postgres  # PostgreSQL tests
   pytest -m asyncio   # Async tests
   ```

4. **Commit Guidelines**
   - Use descriptive commit messages
   - Follow conventional commits format
   - Include co-author attribution for AI assistance:
     ```
     🤖 Generated with [Claude Code](https://claude.ai/code)
     
     Co-Authored-By: Claude <noreply@anthropic.com>
     ```

## 🎯 Areas for Contribution

### High Priority
- **Enhanced AI Features**: Better geospatial analysis, map interpretation
- **Performance Optimization**: Query optimization, caching strategies
- **Additional Data Formats**: More import/export formats
- **Documentation**: Code documentation, tutorials, examples

### Medium Priority
- **UI/UX Improvements**: Enhanced user interface, accessibility
- **Extended Symbology**: Advanced styling and visualization
- **Collaboration Features**: Enhanced real-time editing
- **Mobile Responsiveness**: Mobile-friendly interface

### Development Guidelines
- **Follow existing code style**: Use project's linting configuration
- **Write tests**: Include tests for new features
- **Document changes**: Update relevant documentation
- **Maintain AGPLv3 compliance**: Ensure all network-accessible modifications have source available

## 📝 Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Write docstrings for functions and classes
- Use async/await for I/O operations

### TypeScript (Frontend)
- Follow existing ESLint configuration
- Use TypeScript strict mode
- Prefer functional components with hooks
- Use proper prop typing

## 🧪 Testing

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src

# Specific markers
pytest -m "not slow"  # Skip slow tests
pytest -m integration # Only integration tests
```

### Writing Tests
- Place tests alongside source files (test_*.py)
- Use pytest fixtures for setup
- Mark tests appropriately (@pytest.mark.s3, etc.)
- Test both success and error cases

## 📚 Documentation

### CLAUDE.md
This file provides context for AI assistants working on the codebase. Update it when:
- Adding new essential commands
- Changing architecture significantly
- Adding new testing approaches
- Modifying development workflow

### Code Documentation
- Document complex functions with docstrings
- Add inline comments for non-obvious logic
- Update README.md for significant changes

## 🔒 License Compliance

This fork maintains the original AGPLv3 license:

### Requirements
- **Source Availability**: All modifications to network-accessible code must have source available
- **Attribution**: Maintain original copyright notices
- **License Propagation**: Derived works must use compatible licenses

### Best Practices
- Include proper attribution in commit messages
- Document any new dependencies and their licenses
- Ensure Docker images don't violate license terms

## 🚀 Deployment

### Production Deployment
- Use the main Docker Compose setup
- Set appropriate environment variables
- Ensure proper backup strategies for data/ directory
- Monitor resource usage and performance

### Environment Variables
See `.env.example` for all available configuration options.

## 🐛 Reporting Issues

1. **Check existing issues** in both this fork and upstream repository
2. **Provide detailed reproduction steps**
3. **Include environment information** (OS, Docker version, etc.)
4. **Attach logs** when relevant

## 💬 Community

- **Upstream Discord**: [Join BuntingLabs Discord](https://discord.gg/V63VbgH8dT) for general Mundi questions
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

## 🙏 Attribution

This fork builds upon the excellent work of [BuntingLabs](https://github.com/BuntingLabs) and the original [Mundi.ai](https://github.com/BuntingLabs/mundi.ai) contributors. We maintain full compliance with the AGPLv3 license and provide proper attribution.

All modifications are made available under the same AGPLv3 license terms.