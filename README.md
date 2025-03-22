### Test MCP servers
- `sse`

```bash
mcp-inspector uv run ~/git/devopsnextgenx/ai-psat-generator/mcp-src/mcp-sse.py --transport sse --port 1111
```

- `stdio`
```bash
mcp-inspector uv run --directory ~/git/devopsnextgenx/ai-psat-generator/mcp-src mcp-stdio.py
```

### ROO code
- run mcp server sse `uv run ~/git/devopsnextgenx/ai-psat-generator/mcp-src/mcp-sse.py --transport sse --port 1111`


```json
{
  "mcpServers": {
    "stdio": {
      "command": "/home/shared/pyenv/bin/py",
      "args": [
        "~/git/devopsnextgenx/ai-psat-generator/mcp-src/mcp-stdio.py"
      ],
      "env": {},
      "disabled": true,
      "alwaysAllow": [
        "calculateSum",
        "encryptBase64",
        "decryptBase64",
        "echo"
      ]
    },
    "sse": {
      "url": "http://localhost:1111/sse",
      "alwaysAllow": [],
      "disabled": false
    }
  }
}
```