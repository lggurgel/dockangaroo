# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-11-18

### Added
- Initial release of Bitcoin Puzzle Solver - Kangaroo Edition
- Pollard's Kangaroo algorithm implementation using Jean-Luc Pons' Kangaroo
- Docker-based distributed solving with 10 parallel workers
- Single configuration file (`config.env`) for all settings
- Real-time monitoring via `kangaroo_monitor.py`
- Statistics viewer via `stats.py`
- Automatic checkpoint and resume functionality
- Support for CPU and GPU modes
- Comprehensive README with donation section
- MIT License
- Contributing guidelines
- GitHub issue templates

### Features
- Configurable puzzle number and target public key
- Adjustable worker count and resource limits
- Distinguished Point (DP) strategy for efficient collision detection
- Auto-save work files every 60 seconds (configurable)
- Solution detection and saving to `results/`
- Docker Compose orchestration for easy deployment
- GPU support via `docker-compose.gpu.yml` (requires NVIDIA GPU)

### Documentation
- Complete README with quick start guide
- Configuration examples for different CPU counts
- Performance expectations and reality check
- Security best practices
- Troubleshooting guide
- Contributing guidelines
- License file

## [Unreleased]

### Planned Features
- Multi-machine coordination
- Web-based monitoring dashboard
- Improved GPU kernel optimization
- Cloud deployment templates (AWS, GCP, Azure)
- Telegram/Discord notifications on solution found
- Better DP merging strategies

