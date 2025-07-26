# Context7 Tool for Trae Agent

This document describes the Context7 tool implementation for the Trae Agent project. The Context7 tool provides access to up-to-date library documentation and code examples through the Context7 API.

## Overview

The Context7 tool integrates with the [Context7 service](https://context7.com) to provide agents with:

- **Library Search**: Find libraries by name and get Context7-compatible library IDs
- **Documentation Retrieval**: Fetch current, version-specific documentation and code examples
- **Up-to-date Information**: Access documentation directly from library sources rather than static training data

## Features

### 🔍 Library Search

- Search for libraries using natural language queries
- Get Context7-compatible library IDs for use with documentation retrieval
- View library metadata including trust scores, available versions, and code snippet counts

### 📚 Documentation Retrieval

- Fetch detailed documentation using Context7 library IDs
- Focus on specific topics (e.g., "hooks", "authentication", "routing")
- Control content length with token limits
- Access version-specific documentation

### ⚡ Smart Parameter Handling

- OpenAI-compatible parameter handling (all parameters required for strict mode)
- Other providers support optional parameters
- Comprehensive error handling and validation

## Usage

The Context7 tool supports two main actions:

### 1. Search for Libraries

```python
{
    "action": "search",
    "library_name": "react"
}
```

**Parameters:**

- `action`: Must be "search"
- `library_name`: Name of the library to search for

**Example Response:**

```plaintext
Context7 Library Search Results for 'react':
==================================================

Top matches:

1. **React**
   Library ID: `/facebook/react`
   Description: A JavaScript library for building user interfaces
   Code Snippets: 234
   Trust Score: 10/10
   Available Versions: v18.2.0, v17.0.2, v16.14.0 (and 15 more)

2. **React Router**
   Library ID: `/remix-run/react-router`
   Description: Declarative routing for React
   Code Snippets: 89
   Trust Score: 9/10
```

### 2. Get Documentation

```python
{
    "action": "get_docs",
    "library_id": "/facebook/react",
    "topic": "hooks",
    "tokens": 5000
}
```

**Parameters:**

- `action`: Must be "get_docs"
- `library_id`: Context7-compatible library ID (format: `/org/project` or `/org/project/version`)
- `topic` (optional): Focus topic for documentation
- `tokens` (optional): Maximum tokens to return (default: 10000, minimum: 10000)

**Example Response:**

```plaintext
Context7 Documentation for /facebook/react (Topic: hooks)
=========================================================

Token limit: 5000
Content length: ~1200 words

--- Documentation Content ---

# React Hooks

Hooks are a new addition in React 16.8. They let you use state and other React features without writing a class...

[Detailed documentation content here]

--- End of Documentation ---
```

## Error Handling

The tool provides comprehensive error handling for various scenarios:

### Rate Limiting

```plaintext
Error: Rate limited. Please try again later.
```

### Library Not Found

```plaintext
Error: Library not found: '/invalid/library'. Use the 'search' action to find valid library IDs.
```

### Invalid Parameters

```plaintext
Error: library_name is required when action='search'
Error: Invalid library_id format: 'invalid-format'. Must start with '/' (e.g., '/facebook/react')
```

### Network Issues

```plaintext
Error: Request timed out. Please try again.
Error: Failed to search libraries. Status code: 500
```

## Implementation Details

### Architecture

- **Base Class**: Inherits from `Tool` base class
- **HTTP Client**: Uses `httpx` for async HTTP requests
- **Error Handling**: Comprehensive error handling with specific error codes
- **Parameter Validation**: Validates library IDs and required parameters

### API Integration

- **Base URL**: `https://context7.com/api/v1`
- **Search Endpoint**: `GET /search?query={library_name}`
- **Documentation Endpoint**: `GET /{library_id}?tokens={num}&topic={topic}&type=txt`
- **Timeout**: 30 seconds per request
- **Headers**: Custom User-Agent and source identification

### Configuration

The tool is automatically configured and requires no additional setup. It uses:

- Default token limit: 10,000 tokens
- Request timeout: 30 seconds
- Automatic rate limiting detection and handling

## Integration

The Context7 tool is automatically registered in the Trae Agent tool registry as:

```python
tools_registry = {
    # ... other tools
    "context7": Context7Tool,
}
```

## Usage Examples

### Basic Library Search

```python
await tool.execute({
    "action": "search",
    "library_name": "fastapi"
})
```

### Get React Hooks Documentation

```python
await tool.execute({
    "action": "get_docs",
    "library_id": "/facebook/react",
    "topic": "hooks",
    "tokens": 8000
})
```

### Get Next.js Routing Documentation

```python
await tool.execute({
    "action": "get_docs",
    "library_id": "/vercel/next.js",
    "topic": "routing"
})
```

### Search for Python Libraries

```python
await tool.execute({
    "action": "search",
    "library_name": "django rest framework"
})
```

## Dependencies

The Context7 tool requires:
- `httpx>=0.25.0` - For async HTTP requests
- Standard library modules: `json`, `typing`

## Best Practices

1. **Always search first**: Use the search action to find valid library IDs before fetching documentation
2. **Use specific topics**: Provide topic parameters to get focused documentation
3. **Respect rate limits**: The tool handles rate limiting automatically, but avoid excessive requests
4. **Handle errors gracefully**: Check error codes and provide fallback behavior
5. **Use appropriate token limits**: Balance between getting enough information and API efficiency

## Troubleshooting

### Common Issues

**"Library not found" errors:**

- Use the search action first to find the correct library ID
- Ensure the library ID format starts with `/` (e.g., `/facebook/react`)

**Rate limiting:**

- Wait before retrying requests
- The tool automatically detects and reports rate limiting

**Empty documentation:**

- Some libraries may not have finalized documentation in Context7
- Try different library versions or alternative libraries

**Network timeouts:**

- Retry the request after a short delay
- Check internet connectivity

## Future Enhancements

Potential improvements for the Context7 tool:

1. **Caching**: Implement local caching for frequently requested documentation
2. **Batch Operations**: Support multiple library queries in a single request
3. **Version Selection**: Enhanced version selection and comparison features
4. **Search Filters**: Advanced search filtering by language, category, or trust score
5. **Offline Mode**: Fallback to cached content when API is unavailable
