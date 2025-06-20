# Juggler Web Interface

The `juggler web` command provides a (preview) web-based chat interface for interacting with Juggler.
Do not expose this publicly - this is in a preview state as an option.

## Usage

```bash
# Start the web server on default port (3000)
juggler web

# Start on a specific port
juggler web --port 8080

# Start and automatically open in browser
juggler web --open

# Bind to a specific host
juggler web --host 0.0.0.0 --port 8080
```

## Features

- **Real-time chat interface**: Communicate with Juggler through a clean web UI
- **WebSocket support**: Real-time message streaming
- **Session management**: Each browser tab maintains its own session
- **Responsive design**: Works on desktop and mobile devices

## Architecture

The web interface is built with:
- **Backend**: Rust with Axum web framework
- **Frontend**: Vanilla JavaScript with WebSocket communication
- **Styling**: CSS with dark/light mode support

## Development Notes

### Current Implementation

The web interface provides:
1. A simple chat UI similar to the desktop Electron app
2. WebSocket-based real-time communication
3. Basic session management (messages are stored in memory)

### Future Enhancements

- [ ] Persistent session storage
- [ ] Tool call visualization
- [ ] File upload support
- [ ] Multiple session tabs
- [ ] Authentication/authorization
- [ ] Streaming responses with proper formatting
- [ ] Code syntax highlighting
- [ ] Export chat history

### Integration with Juggler Agent

The web server creates an instance of the Juggler Agent and processes messages through the same pipeline as the CLI. However, some features like:
- Extension management
- Tool confirmations
- File system interactions

...may require additional UI components to be fully functional.

## Security Considerations

Currently, the web interface:
- Binds to localhost by default for security
- Does not include authentication (planned for future)
- Should not be exposed to the internet without proper security measures

## Troubleshooting

If you encounter issues:

1. **Port already in use**: Try a different port with `--port`
2. **Cannot connect**: Ensure no firewall is blocking the port
3. **Agent not configured**: Run `juggler configure` first to set up a provider