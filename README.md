# Hong Kong Government Election and Legislature MCP Server

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/hkopenai/hk-election-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is an MCP server that provides access to government security incident data through a FastMCP interface.

## Features

- **Registered Electors Data**: Retrieve the number of registered electors in Hong Kong's geographical constituencies for a specified range of years.

## Data Source

- Registered electors data from Registration and Electoral Office (voterregistration.gov.hk)

## Examples

* List number of registered electors in geographical constituencies in Hong Kong between 2009 and 2024

## Setup

1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python app.py
   ```

### Running Options

- Default stdio mode: `python app.py`
- SSE mode (port 8000): `python app.py --sse`

## Cline Integration

To connect this MCP server to Cline using stdio:

1. Add this configuration to your Cline MCP settings (cline_mcp_settings.json):
```json
{
  "hk-election": {
    "disabled": false,
    "timeout": 3,
    "type": "stdio",
    "command": "uvx",
    "args": [
      "hkopenai.hk-election-mcp-server"
    ]
  }
}
```

## Testing

Tests are available in the `tests/` directory. Run with:
```bash
pytest
```
