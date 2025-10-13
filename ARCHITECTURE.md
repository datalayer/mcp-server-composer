<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

[![Datalayer](https://assets.datalayer.tech/datalayer-25.svg)](https://datalayer.io)

[![Become a Sponsor](https://img.shields.io/static/v1?label=Become%20a%20Sponsor&message=%E2%9D%A4&logo=GitHub&style=flat&color=1ABC9C)](https://github.com/sponsors/datalayer)

# ✨ MCP Server Composer

[![PyPI - Version](https://img.shields.io/pypi/v/mcp-server-composer)](https://pypi.org/project/mcp-server-composer)

[![Github Actions Status](https://github.com/datalayer/mcp-server-composer/workflows/Build/badge.svg)](https://github.com/datalayer/mcp-server-composer/actions/workflows/build.yml)

# Architecture

The MCP Server Composer is a Python facade for multiple `Managed MCP Servers`.

The MCP Servers exposes all the tools of the managed MCP Servers as a single MCP Servers, aggregating the tools.

A `Managed MCP Server`can be:

- `Embedded` based on a list of python packages located in a `mcp_server_composer.toml` file.
- `Proxied` which are external MCP Server accessible via `STDIO` and `Streamable HTTP`. The startup commands of those `Proxied` MCP Servers is located in the `mcp_server_composer.toml` file.

The supported exposed `transports` are the officiel MCP transports, namely `STDIO` and `Streamable HTTP`.

In terms of security:

- A configurable `Authn` (authentication) middleware is to be defined in `mcp_server_composer.toml`.
- A configurable `Authz` (authorization) middleware is to be defined in `mcp_server_composer.toml`.

The MCP Composer has some internal services:

- `Process Manager` responsible to start and monitor the Proxied MCP Servers
- `Tool Manager` responsible to resolved any naming conflict during the tool aggregation

The MCP Server Composer exposes its functionality via API (REST endpoints) and a UI (User Interface). The endpoints and UI are secured with the configurable `Authn` and `Authz`.
