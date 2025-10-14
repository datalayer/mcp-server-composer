# Changelog

All notable changes to MCP Server Composer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-14

### 🎉 Initial Release

The first production-ready release of MCP Server Composer with complete feature set.

### Added

#### Core Functionality
- Configuration system with TOML format (`mcp_server_composer.toml`)
- Environment variable substitution in configuration
- Backward compatibility with `pyproject.toml` discovery
- Process Manager for MCP server lifecycle management
- Tool Manager with 6 conflict resolution strategies (PREFIX, SUFFIX, IGNORE, ERROR, OVERRIDE, CUSTOM)
- Tool versioning and aliasing support
- Per-tool override configuration with wildcard patterns
- Conflict tracking and history

#### Server Management
- Start, stop, restart operations for MCP servers
- Process state tracking (starting, running, stopping, stopped, crashed)
- Auto-restart capability with configurable policies
- Health monitoring for all servers
- Resource limit enforcement
- STDIO transport for subprocess communication
- SSE transport for web client communication

#### REST API (32 Endpoints)
- **Health & Status:** `/health`, `/version`, `/status`, `/status/composition`, `/status/metrics`
- **Server Management:** GET/POST `/servers`, `/servers/{id}/start`, `/servers/{id}/stop`, `/servers/{id}/restart`
- **Tool Management:** GET `/tools`, GET `/tools/{name}`, POST `/tools/{name}/invoke`
- **Prompt Management:** GET `/prompts`, GET `/prompts/{name}`
- **Resource Management:** GET `/resources`, GET `/resources/{uri}`
- **Configuration:** GET/PUT `/config`, POST `/config/validate`, POST `/config/reload`
- **Translators:** GET/POST/DELETE `/translators`, `/translators/{id}/start`, `/translators/{id}/stop`
- OpenAPI/Swagger documentation at `/docs`
- Request validation with Pydantic
- Comprehensive error handling

#### Authentication & Security
- API Key authentication
- JWT token authentication
- OAuth2 client credentials flow
- mTLS (mutual TLS) support
- RBAC (Role-Based Access Control)
- Tool-level permissions
- Server-level access control
- Rate limiting (per-user, per-IP, per-tool)
- Redis-backed rate limiter
- Security headers (HSTS, X-Frame-Options, etc.)
- Request validation and sanitization
- Audit logging for security events

#### Web UI (8 Pages)
- **Dashboard:** System overview with metrics cards and status indicators
- **Server Management:** Start/stop/restart servers with real-time status
- **Tool Browser:** Search, filter, and invoke tools with interactive forms
- **Configuration Editor:** Edit and validate TOML configuration
- **Log Viewer:** Real-time log streaming with filtering and export
- **Metrics Dashboard:** Charts for CPU, memory, requests, and latency
- **Translator Management:** Create and manage protocol translators
- **Settings:** Theme switching, API configuration, preferences
- Real-time updates via WebSocket and polling
- Light and dark theme support
- Responsive design
- Built with React 18.2 + TypeScript 5.2

#### Monitoring & Observability
- Prometheus metrics integration
- Custom metrics for tools, servers, and requests
- Structured JSON logging
- Request ID tracking and correlation
- Performance monitoring
- Resource usage tracking (CPU, memory)
- Health check endpoints
- WebSocket streaming for logs and metrics
- Grafana dashboard templates

#### Protocol Translation
- STDIO ↔ SSE translator mode
- Transparent protocol bridging
- Bidirectional communication
- Multiple simultaneous translators
- Translator lifecycle management

#### Documentation
- **User Guide:** 1,100+ lines covering installation, configuration, and usage
- **API Reference:** 850+ lines documenting all endpoints and Python API
- **Deployment Guide:** 900+ lines for production deployment
- **Project History:** Complete development journey
- **Architecture Documentation:** System design and decisions
- 180+ code examples across bash, Python, JavaScript
- Troubleshooting guides
- Best practices sections

#### Deployment & Infrastructure
- Multi-stage Dockerfile for optimized images
- docker-compose.yml with full monitoring stack
- Prometheus configuration for metrics collection
- Grafana datasource and dashboard provisioning
- Nginx reverse proxy configuration with SSL
- Kubernetes deployment manifests
- Health checks and resource limits
- Non-root container user for security
- Production-ready configuration templates

#### Testing
- 265+ test cases
- 95% test coverage
- Unit tests for all modules
- Integration tests for workflows
- API endpoint tests
- Authentication/authorization tests
- Process management tests
- Transport layer tests

#### CLI Commands
- `mcp-composer serve` - Start the composer with REST API and Web UI
- `mcp-composer discover` - Discover MCP servers in configuration
- `mcp-composer invoke-tool` - Invoke a tool from command line
- `mcp-composer validate-config` - Validate configuration file
- Configuration file support via `--config` flag
- JSON output format via `--output-format json`

#### Python API
- `MCPServerComposer` class for programmatic control
- Async API for server management
- Context manager support for resource cleanup
- Server operations: `start_server`, `stop_server`, `restart_server`
- Tool operations: `list_tools`, `get_tool`, `invoke_tool`
- Prompt operations: `list_prompts`, `get_prompt`, `render_prompt`
- Resource operations: `list_resources`, `read_resource`
- Configuration operations: `load_config`, `reload_config`, `validate_config`
- Health and status queries

### Technical Specifications

#### Requirements
- Python 3.10 or higher
- Node.js 18+ (for UI development)
- Docker (optional, for containerized deployment)

#### Dependencies
**Python:**
- fastapi >= 0.104.0
- uvicorn >= 0.24.0
- pydantic >= 2.0.0
- httpx >= 0.25.0
- sse-starlette >= 1.6.0
- prometheus-client >= 0.18.0
- python-jose >= 3.3.0 (JWT)
- passlib >= 1.7.4 (password hashing)

**JavaScript:**
- react >= 18.2.0
- typescript >= 5.2.0
- vite >= 5.0.0
- recharts >= 2.10.3
- zustand >= 4.4.0
- react-router-dom >= 6.20.0

#### Performance
- Handles unlimited MCP servers (limited by system resources)
- Sub-100ms API response times
- Real-time log streaming with minimal latency
- Efficient memory usage with streaming
- Prometheus metrics for performance monitoring

#### Security
- Token-based authentication
- Role-based access control
- Rate limiting to prevent abuse
- Input validation on all endpoints
- CORS configuration for web clients
- Security headers on all responses
- Audit logging for security events
- Non-root container execution

### Known Issues
None at release time.

### Breaking Changes
None - this is the initial release.

---

## [Unreleased]

### Planned Features
- Plugin system for custom extensions
- GraphQL API support
- CLI auto-completion
- Enhanced caching strategies
- Distributed deployment support
- Advanced analytics and reporting

---

## Release Notes

### v1.0.0 Highlights

This release represents 16 weeks of development across 4 major phases:

1. **Phase 1 (Weeks 1-4):** Foundation with configuration, tool management, and process lifecycle
2. **Phase 2 (Weeks 5-8):** Security with 4 authentication methods and RBAC
3. **Phase 3 (Weeks 9-12):** REST API with 32 endpoints and monitoring
4. **Phase 4 (Weeks 13-16):** Web UI with 8 pages and comprehensive documentation

The result is a production-ready system with:
- ✅ 15,000+ lines of code
- ✅ 265+ tests with 95% coverage
- ✅ 32 REST API endpoints
- ✅ 8-page modern web interface
- ✅ 3,100+ lines of documentation
- ✅ Full Docker deployment stack

### Migration Guide

Since this is the initial release, no migration is required. For future versions, migration guides will be provided here.

### Upgrade Instructions

```bash
# Install from PyPI
pip install mcp-server-composer

# Or upgrade existing installation
pip install --upgrade mcp-server-composer

# Verify installation
mcp-composer --version
```

### Acknowledgments

Thanks to all contributors and the Model Context Protocol community for making this project possible.

---

*For detailed development history, see [PROJECT_HISTORY.md](PROJECT_HISTORY.md)*

[1.0.0]: https://github.com/datalayer/mcp-server-composer/releases/tag/v1.0.0
[Unreleased]: https://github.com/datalayer/mcp-server-composer/compare/v1.0.0...HEAD
