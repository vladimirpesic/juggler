# Selenium Tool

## Overview
Comprehensive web automation tool for the Trae Agent framework using Selenium WebDriver. Supports Chrome/Firefox with 24+ actions for web interaction, testing, and automation.

## Quick Start

```python
from trae_agent.tools.selenium_tool import SeleniumTool

selenium_tool = SeleniumTool()

# Basic workflow
await selenium_tool.execute({"action": "start_browser", "browser": "chrome"})
await selenium_tool.execute({"action": "navigate", "url": "https://example.com"})
await selenium_tool.execute({"action": "click", "selector": "#button"})
await selenium_tool.execute({"action": "stop_browser"})
```

## Actions Reference

### Browser Management

- **start_browser**: `{"action": "start_browser", "browser": "chrome|firefox", "headless": false, "options": {}}`
- **stop_browser**: `{"action": "stop_browser"}`
- **navigate**: `{"action": "navigate", "url": "https://example.com"}`
- **refresh/back/forward**: `{"action": "refresh|back|forward"}`

### Element Interaction

- **click**: `{"action": "click", "selector": "#id", "selector_type": "css"}`
- **type**: `{"action": "type", "selector": "#input", "text": "hello"}`
- **clear**: `{"action": "clear", "selector": "#input"}`

### Information Retrieval

- **get_text**: `{"action": "get_text", "selector": "h1"}`
- **get_attribute**: `{"action": "get_attribute", "selector": "#link", "attribute": "href"}`
- **get_title/get_url/get_page_source**: `{"action": "get_title"}`

### Advanced Interactions

- **select_dropdown**: `{"action": "select_dropdown", "selector": "select", "value": "option1"}`
- **scroll**: `{"action": "scroll", "x": 0, "y": 500}` or `{"selector": "#element"}`
- **hover**: `{"action": "hover", "selector": "#menu"}`
- **wait_for_element**: `{"action": "wait_for_element", "selector": "#loading", "timeout": 10}`

### JavaScript & Visual

- **execute_js**: `{"action": "execute_js", "javascript": "return document.title;"}`
- **screenshot**: `{"action": "screenshot", "filename": "page.png"}`
- **is_visible/is_enabled**: `{"action": "is_visible", "selector": "#element"}`

### Cookie Management

- **get_cookies**: `{"action": "get_cookies"}`
- **set_cookie**: `{"action": "set_cookie", "cookie_name": "key", "cookie_value": "value"}`

## Selector Types

- **css** (default): `"#id"`, `".class"`, `"div > p"`
- **xpath**: `"//div[@class='content']"`
- **id**: `"submit-button"`
- **class/name/tag**: `"btn-primary"`, `"email"`, `"input"`
- **link_text/partial_link_text**: `"Click Here"`, `"Click"`

## Example Use Cases

### Google Search

```python
await selenium_tool.execute({"action": "start_browser", "headless": False})
await selenium_tool.execute({"action": "navigate", "url": "https://google.com"})
await selenium_tool.execute({"action": "type", "selector": "input[name='q']", "text": "selenium"})
await selenium_tool.execute({"action": "execute_js", "javascript": "document.querySelector('input[name=\"q\"]').form.submit();"})
await selenium_tool.execute({"action": "wait_for_element", "selector": "#search", "timeout": 15})
await selenium_tool.execute({"action": "screenshot", "filename": "results.png"})
await selenium_tool.execute({"action": "stop_browser"})
```

### Form Filling

```python
await selenium_tool.execute({"action": "start_browser", "headless": True})
await selenium_tool.execute({"action": "navigate", "url": "https://forms.example.com"})
await selenium_tool.execute({"action": "type", "selector": "input[name='firstname']", "text": "John"})
await selenium_tool.execute({"action": "type", "selector": "input[name='lastname']", "text": "Doe"})
await selenium_tool.execute({"action": "select_dropdown", "selector": "#country", "value": "US"})
await selenium_tool.execute({"action": "click", "selector": "#submit"})
await selenium_tool.execute({"action": "stop_browser"})
```

### Web Scraping

```python
await selenium_tool.execute({"action": "start_browser", "headless": True})
await selenium_tool.execute({"action": "navigate", "url": "https://data.example.com"})
await selenium_tool.execute({"action": "wait_for_element", "selector": "h1"})

title = await selenium_tool.execute({"action": "get_title"})
heading = await selenium_tool.execute({"action": "get_text", "selector": "h1"})
paragraphs = await selenium_tool.execute({
    "action": "execute_js", 
    "javascript": "return Array.from(document.querySelectorAll('p')).map(p => p.textContent);"
})

await selenium_tool.execute({"action": "stop_browser"})
```

## Implementation Details

### Files Structure

- **`trae_agent/tools/selenium_tool.py`**: Main implementation (31KB)
- **`trae_agent/tools/__init__.py`**: Integration with tools registry
- **Tool Registration**: Available as `"selenium"` in tools_registry

### Features

- ✅ 24 implemented actions across 8 categories
- ✅ Chrome & Firefox support with auto-driver management
- ✅ Headless mode support
- ✅ Async/await compatibility
- ✅ Comprehensive error handling
- ✅ Multi-selector support (CSS, XPath, ID, etc.)
- ✅ Cookie management
- ✅ JavaScript execution
- ✅ Screenshot capabilities
- ✅ Form handling & dropdown selection

### Dependencies

- `selenium>=4.15.0`
- `webdriver-manager>=4.0.0`

## Best Practices

1. Always start browser before other actions
2. Use `wait_for_element` for dynamic content
3. Use headless mode for better performance
4. Take screenshots for debugging
5. Always call `stop_browser` when done
6. Set appropriate timeouts (default: 10s)
7. Use CSS selectors for speed, XPath for complex selections

## Error Handling

- Browser not started detection
- Element not found with clear messages
- Timeout errors with configurable limits
- JavaScript execution error capture
- Comprehensive WebDriver exception handling
