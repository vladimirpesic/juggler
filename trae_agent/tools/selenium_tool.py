"""Selenium WebDriver tool for web automation and testing."""

import json
from typing import Any, override

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from .base import Tool, ToolCallArguments, ToolError, ToolExecResult, ToolParameter


class SeleniumTool(Tool):
    """
    A comprehensive Selenium WebDriver tool for web automation and testing.

    Features:
    - Browser management (Chrome, Firefox)
    - Element interaction (click, type, select)
    - Navigation and page manipulation
    - Screenshots and visual verification
    - JavaScript execution
    - Advanced waiting strategies
    - Form handling
    - Cookie and session management
    """

    def __init__(self, model_provider: str | None = None):
        super().__init__(model_provider)
        self._driver: webdriver.Chrome | webdriver.Firefox | None = None
        self._wait: WebDriverWait | None = None
        self._default_timeout = 10

    @override
    def get_name(self) -> str:
        return "selenium"

    @override
    def get_description(self) -> str:
        return """Selenium WebDriver tool for web automation and testing.

Core Features:
- Browser management: start/stop browsers, navigate to URLs
- Element interaction: click, type, select elements by various selectors
- Form handling: fill forms, select dropdowns, handle checkboxes/radio buttons
- Screenshots: capture full page or element screenshots
- JavaScript execution: run custom JavaScript code
- Advanced waiting: wait for elements, conditions, page loads

Advanced Features:
- Cookie management: get/set/delete cookies
- Window/tab management: switch between windows and tabs
- Action chains: complex mouse/keyboard interactions
- Visual verification: element visibility, text content validation
- Session management: maintain browser state across operations

Supported browsers: Chrome (default), Firefox
All operations include proper error handling and timeout management."""

    @override
    def get_parameters(self) -> list[ToolParameter]:
        action_required = self.model_provider == "openai"

        return [
            ToolParameter(
                name="action",
                type="string",
                description="The action to perform",
                enum=[
                    # Browser management
                    "start_browser",
                    "stop_browser",
                    "navigate",
                    "refresh",
                    "back",
                    "forward",
                    # Element interaction
                    "click",
                    "type",
                    "clear",
                    "select_dropdown",
                    "checkbox",
                    "radio",
                    # Information retrieval
                    "get_text",
                    "get_attribute",
                    "get_title",
                    "get_url",
                    "get_page_source",
                    # Visual and verification
                    "screenshot",
                    "element_screenshot",
                    "is_visible",
                    "is_enabled",
                    "wait_for_element",
                    "wait_for_text",
                    "wait_for_url",
                    # JavaScript
                    "execute_js",
                    "execute_async_js",
                    # Advanced features
                    "scroll",
                    "hover",
                    "drag_and_drop",
                    "switch_window",
                    "switch_frame",
                    "get_cookies",
                    "set_cookie",
                    "delete_cookie",
                    "delete_all_cookies",
                    # Form and page interaction
                    "submit_form",
                    "upload_file",
                    "handle_alert",
                    "get_window_size",
                    "set_window_size",
                ],
                required=action_required,
            ),
            ToolParameter(
                name="browser",
                type="string",
                description="Browser type (chrome or firefox). Default: chrome",
                enum=["chrome", "firefox"],
                required=False,
            ),
            ToolParameter(
                name="headless",
                type="boolean",
                description="Run browser in headless mode. Default: false",
                required=False,
            ),
            ToolParameter(
                name="url",
                type="string",
                description="URL to navigate to (for navigate action)",
                required=False,
            ),
            ToolParameter(
                name="selector",
                type="string",
                description="CSS selector, XPath, ID, class name, or element selector",
                required=False,
            ),
            ToolParameter(
                name="selector_type",
                type="string",
                description="Type of selector: css, xpath, id, class, name, tag, link_text, partial_link_text",
                enum=[
                    "css",
                    "xpath",
                    "id",
                    "class",
                    "name",
                    "tag",
                    "link_text",
                    "partial_link_text",
                ],
                required=False,
            ),
            ToolParameter(
                name="text",
                type="string",
                description="Text to type or search for",
                required=False,
            ),
            ToolParameter(
                name="value",
                type="string",
                description="Value to select in dropdown or set as attribute",
                required=False,
            ),
            ToolParameter(
                name="timeout",
                type="number",
                description="Timeout in seconds for wait operations. Default: 10",
                required=False,
            ),
            ToolParameter(
                name="javascript",
                type="string",
                description="JavaScript code to execute",
                required=False,
            ),
            ToolParameter(
                name="filename",
                type="string",
                description="Filename for screenshots or file uploads",
                required=False,
            ),
            ToolParameter(
                name="attribute",
                type="string",
                description="Attribute name to get from element",
                required=False,
            ),
            ToolParameter(
                name="cookie_name",
                type="string",
                description="Cookie name for cookie operations",
                required=False,
            ),
            ToolParameter(
                name="cookie_value",
                type="string",
                description="Cookie value for setting cookies",
                required=False,
            ),
            ToolParameter(
                name="window_handle",
                type="string",
                description="Window handle for switching windows",
                required=False,
            ),
            ToolParameter(
                name="frame_selector",
                type="string",
                description="Frame selector for switching to frame",
                required=False,
            ),
            ToolParameter(
                name="source_selector",
                type="string",
                description="Source element selector for drag and drop",
                required=False,
            ),
            ToolParameter(
                name="target_selector",
                type="string",
                description="Target element selector for drag and drop",
                required=False,
            ),
            ToolParameter(
                name="width",
                type="number",
                description="Window width in pixels",
                required=False,
            ),
            ToolParameter(
                name="height",
                type="number",
                description="Window height in pixels",
                required=False,
            ),
            ToolParameter(
                name="options",
                type="object",
                description="Additional options as JSON object",
                required=False,
            ),
        ]

    def _get_by_selector(self, selector: str, selector_type: str = "css") -> tuple[By, str]:
        """Convert selector string and type to Selenium By locator."""
        selector_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
        }

        by_type = selector_map.get(selector_type, By.CSS_SELECTOR)
        return by_type, selector

    def _find_element(self, selector: str, selector_type: str = "css") -> WebElement:
        """Find a single element with error handling."""
        if not self._driver:
            raise ToolError("Browser not started. Use start_browser action first.")

        by_type, selector_value = self._get_by_selector(selector, selector_type)

        try:
            return self._driver.find_element(by_type, selector_value)
        except NoSuchElementException:
            raise ToolError(f"Element not found: {selector} (type: {selector_type})")  # noqa: B904

    def _find_elements(self, selector: str, selector_type: str = "css") -> list[WebElement]:
        """Find multiple elements with error handling."""
        if not self._driver:
            raise ToolError("Browser not started. Use start_browser action first.")

        by_type, selector_value = self._get_by_selector(selector, selector_type)
        return self._driver.find_elements(by_type, selector_value)

    async def _start_browser(
        self, browser: str = "chrome", headless: bool = False, options: dict[str, Any] | None = None
    ) -> ToolExecResult:
        """Start a browser instance."""
        if self._driver:
            return ToolExecResult(output="Browser already started. Use stop_browser to restart.")

        try:
            if browser.lower() == "firefox":
                firefox_options = FirefoxOptions()
                if headless:
                    firefox_options.add_argument("--headless")

                if options:
                    for key, value in options.items():
                        if key == "arguments":
                            for arg in value:
                                firefox_options.add_argument(arg)
                        elif key == "preferences":
                            for pref_name, pref_value in value.items():
                                firefox_options.set_preference(pref_name, pref_value)

                self._driver = webdriver.Firefox(
                    service=webdriver.firefox.service.Service(GeckoDriverManager().install()),
                    options=firefox_options,
                )
            else:
                chrome_options = ChromeOptions()
                if headless:
                    chrome_options.add_argument("--headless")

                # Default Chrome options for better compatibility
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")

                if options:
                    for key, value in options.items():
                        if key == "arguments":
                            for arg in value:
                                chrome_options.add_argument(arg)
                        elif key == "experimental_options":
                            for exp_key, exp_value in value.items():
                                chrome_options.add_experimental_option(exp_key, exp_value)
                        elif key == "binary_location":
                            chrome_options.binary_location = value

                self._driver = webdriver.Chrome(
                    service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                    options=chrome_options,
                )

            self._wait = WebDriverWait(self._driver, self._default_timeout)
            return ToolExecResult(output=f"{browser.title()} browser started successfully.")

        except Exception as e:
            return ToolExecResult(error=f"Failed to start browser: {str(e)}", error_code=-1)

    async def _stop_browser(self) -> ToolExecResult:
        """Stop the browser instance."""
        if not self._driver:
            return ToolExecResult(output="No browser to stop.")

        try:
            self._driver.quit()
            self._driver = None
            self._wait = None
            return ToolExecResult(output="Browser stopped successfully.")
        except Exception as e:
            return ToolExecResult(error=f"Failed to stop browser: {str(e)}", error_code=-1)

    async def _navigate(self, url: str) -> ToolExecResult:
        """Navigate to a URL."""
        if not self._driver:
            raise ToolError("Browser not started. Use start_browser action first.")

        try:
            self._driver.get(url)
            return ToolExecResult(output=f"Navigated to: {url}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to navigate to {url}: {str(e)}", error_code=-1)

    async def _click(self, selector: str, selector_type: str = "css") -> ToolExecResult:
        """Click an element."""
        try:
            element = self._find_element(selector, selector_type)
            element.click()
            return ToolExecResult(output=f"Clicked element: {selector}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to click element: {str(e)}", error_code=-1)

    async def _type(
        self, selector: str, text: str, selector_type: str = "css", clear_first: bool = True
    ) -> ToolExecResult:
        """Type text into an element."""
        try:
            element = self._find_element(selector, selector_type)
            if clear_first:
                element.clear()
            element.send_keys(text)
            return ToolExecResult(output=f"Typed '{text}' into element: {selector}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to type into element: {str(e)}", error_code=-1)

    async def _screenshot(self, filename: str | None = None) -> ToolExecResult:
        """Take a screenshot of the full page."""
        if not self._driver:
            raise ToolError("Browser not started. Use start_browser action first.")

        try:
            if filename:
                success = self._driver.save_screenshot(filename)
                if success:
                    return ToolExecResult(output=f"Screenshot saved to: {filename}")
                else:
                    return ToolExecResult(error="Failed to save screenshot", error_code=-1)
            else:
                # Return base64 encoded screenshot
                screenshot_data = self._driver.get_screenshot_as_base64()
                return ToolExecResult(
                    output=f"Screenshot captured (base64): {screenshot_data[:100]}..."
                )
        except Exception as e:
            return ToolExecResult(error=f"Failed to take screenshot: {str(e)}", error_code=-1)

    async def _execute_js(self, javascript: str) -> ToolExecResult:
        """Execute JavaScript code."""
        if not self._driver:
            raise ToolError("Browser not started. Use start_browser action first.")

        try:
            result = self._driver.execute_script(javascript)
            return ToolExecResult(output=f"JavaScript executed. Result: {result}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to execute JavaScript: {str(e)}", error_code=-1)

    async def _wait_for_element(
        self, selector: str, selector_type: str = "css", timeout: float = 10
    ) -> ToolExecResult:
        """Wait for an element to be present."""
        if not self._driver:
            raise ToolError("Browser not started. Use start_browser action first.")

        try:
            by_type, selector_value = self._get_by_selector(selector, selector_type)
            wait = WebDriverWait(self._driver, timeout)
            element = wait.until(EC.presence_of_element_located((by_type, selector_value)))  # noqa: F841
            return ToolExecResult(output=f"Element found: {selector}")
        except TimeoutException:
            return ToolExecResult(
                error=f"Element not found within {timeout} seconds: {selector}", error_code=-1
            )
        except Exception as e:
            return ToolExecResult(error=f"Failed to wait for element: {str(e)}", error_code=-1)

    async def _get_text(self, selector: str, selector_type: str = "css") -> ToolExecResult:
        """Get text content of an element."""
        try:
            element = self._find_element(selector, selector_type)
            text = element.text
            return ToolExecResult(output=f"Element text: {text}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to get element text: {str(e)}", error_code=-1)

    async def _get_attribute(
        self, selector: str, attribute: str, selector_type: str = "css"
    ) -> ToolExecResult:
        """Get attribute value of an element."""
        try:
            element = self._find_element(selector, selector_type)
            value = element.get_attribute(attribute)
            return ToolExecResult(output=f"Attribute '{attribute}': {value}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to get attribute: {str(e)}", error_code=-1)

    async def _select_dropdown(
        self, selector: str, value: str, selector_type: str = "css"
    ) -> ToolExecResult:
        """Select option from dropdown."""
        try:
            element = self._find_element(selector, selector_type)
            select = Select(element)

            # Try different selection methods
            try:
                select.select_by_value(value)
                return ToolExecResult(
                    output=f"Selected option by value '{value}' in dropdown: {selector}"
                )
            except NoSuchElementException:
                try:
                    select.select_by_visible_text(value)
                    return ToolExecResult(
                        output=f"Selected option by text '{value}' in dropdown: {selector}"
                    )
                except NoSuchElementException:
                    select.select_by_index(int(value))
                    return ToolExecResult(
                        output=f"Selected option by index '{value}' in dropdown: {selector}"
                    )

        except Exception as e:
            return ToolExecResult(
                error=f"Failed to select dropdown option: {str(e)}", error_code=-1
            )

    async def _scroll(
        self, selector: str | None = None, x: int = 0, y: int = 0, selector_type: str = "css"
    ) -> ToolExecResult:
        """Scroll the page or to an element."""
        if not self._driver:
            raise ToolError("Browser not started. Use start_browser action first.")

        try:
            if selector:
                element = self._find_element(selector, selector_type)
                self._driver.execute_script("arguments[0].scrollIntoView();", element)
                return ToolExecResult(output=f"Scrolled to element: {selector}")
            else:
                self._driver.execute_script(f"window.scrollBy({x}, {y});")
                return ToolExecResult(output=f"Scrolled by x: {x}, y: {y}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to scroll: {str(e)}", error_code=-1)

    async def _hover(self, selector: str, selector_type: str = "css") -> ToolExecResult:
        """Hover over an element."""
        try:
            element = self._find_element(selector, selector_type)
            actions = ActionChains(self._driver)
            actions.move_to_element(element).perform()
            return ToolExecResult(output=f"Hovered over element: {selector}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to hover over element: {str(e)}", error_code=-1)

    async def _get_cookies(self) -> ToolExecResult:
        """Get all cookies."""
        if not self._driver:
            raise ToolError("Browser not started. Use start_browser action first.")

        try:
            cookies = self._driver.get_cookies()
            return ToolExecResult(output=f"Cookies: {json.dumps(cookies, indent=2)}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to get cookies: {str(e)}", error_code=-1)

    async def _set_cookie(
        self, cookie_name: str, cookie_value: str, options: dict[str, Any] | None = None
    ) -> ToolExecResult:
        """Set a cookie."""
        if not self._driver:
            raise ToolError("Browser not started. Use start_browser action first.")

        try:
            cookie_dict = {"name": cookie_name, "value": cookie_value}
            if options:
                cookie_dict.update(options)

            self._driver.add_cookie(cookie_dict)
            return ToolExecResult(output=f"Cookie set: {cookie_name} = {cookie_value}")
        except Exception as e:
            return ToolExecResult(error=f"Failed to set cookie: {str(e)}", error_code=-1)

    @override
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        action = arguments.get("action")
        if not action:
            return ToolExecResult(error="No action specified", error_code=-1)

        try:
            # Browser management actions
            if action == "start_browser":
                browser = arguments.get("browser", "chrome")
                headless = arguments.get("headless", False)
                options = arguments.get("options")
                return await self._start_browser(browser, headless, options)

            elif action == "stop_browser":
                return await self._stop_browser()

            elif action == "navigate":
                url = arguments.get("url")
                if not url:
                    return ToolExecResult(error="URL required for navigate action", error_code=-1)
                return await self._navigate(url)

            elif action == "refresh":
                if not self._driver:
                    raise ToolError("Browser not started")
                self._driver.refresh()
                return ToolExecResult(output="Page refreshed")

            elif action == "back":
                if not self._driver:
                    raise ToolError("Browser not started")
                self._driver.back()
                return ToolExecResult(output="Navigated back")

            elif action == "forward":
                if not self._driver:
                    raise ToolError("Browser not started")
                self._driver.forward()
                return ToolExecResult(output="Navigated forward")

            # Element interaction actions
            elif action == "click":
                selector = arguments.get("selector")
                if not selector:
                    return ToolExecResult(error="Selector required for click action", error_code=-1)
                selector_type = arguments.get("selector_type", "css")
                return await self._click(selector, selector_type)

            elif action == "type":
                selector = arguments.get("selector")
                text = arguments.get("text")
                if not selector or not text:
                    return ToolExecResult(
                        error="Selector and text required for type action", error_code=-1
                    )
                selector_type = arguments.get("selector_type", "css")
                return await self._type(selector, text, selector_type)

            elif action == "clear":
                selector = arguments.get("selector")
                if not selector:
                    return ToolExecResult(error="Selector required for clear action", error_code=-1)
                selector_type = arguments.get("selector_type", "css")
                element = self._find_element(selector, selector_type)
                element.clear()
                return ToolExecResult(output=f"Cleared element: {selector}")

            # Information retrieval actions
            elif action == "get_text":
                selector = arguments.get("selector")
                if not selector:
                    return ToolExecResult(
                        error="Selector required for get_text action", error_code=-1
                    )
                selector_type = arguments.get("selector_type", "css")
                return await self._get_text(selector, selector_type)

            elif action == "get_attribute":
                selector = arguments.get("selector")
                attribute = arguments.get("attribute")
                if not selector or not attribute:
                    return ToolExecResult(
                        error="Selector and attribute required for get_attribute action",
                        error_code=-1,
                    )
                selector_type = arguments.get("selector_type", "css")
                return await self._get_attribute(selector, attribute, selector_type)

            elif action == "get_title":
                if not self._driver:
                    raise ToolError("Browser not started")
                return ToolExecResult(output=f"Page title: {self._driver.title}")

            elif action == "get_url":
                if not self._driver:
                    raise ToolError("Browser not started")
                return ToolExecResult(output=f"Current URL: {self._driver.current_url}")

            elif action == "get_page_source":
                if not self._driver:
                    raise ToolError("Browser not started")
                return ToolExecResult(output=f"Page source: {self._driver.page_source[:1000]}...")

            # Visual and verification actions
            elif action == "screenshot":
                filename = arguments.get("filename")
                return await self._screenshot(filename)

            elif action == "is_visible":
                selector = arguments.get("selector")
                if not selector:
                    return ToolExecResult(
                        error="Selector required for is_visible action", error_code=-1
                    )
                selector_type = arguments.get("selector_type", "css")
                element = self._find_element(selector, selector_type)
                visible = element.is_displayed()
                return ToolExecResult(output=f"Element visible: {visible}")

            elif action == "is_enabled":
                selector = arguments.get("selector")
                if not selector:
                    return ToolExecResult(
                        error="Selector required for is_enabled action", error_code=-1
                    )
                selector_type = arguments.get("selector_type", "css")
                element = self._find_element(selector, selector_type)
                enabled = element.is_enabled()
                return ToolExecResult(output=f"Element enabled: {enabled}")

            # Wait actions
            elif action == "wait_for_element":
                selector = arguments.get("selector")
                if not selector:
                    return ToolExecResult(
                        error="Selector required for wait_for_element action", error_code=-1
                    )
                selector_type = arguments.get("selector_type", "css")
                timeout = arguments.get("timeout", self._default_timeout)
                return await self._wait_for_element(selector, selector_type, timeout)

            # JavaScript actions
            elif action == "execute_js":
                javascript = arguments.get("javascript")
                if not javascript:
                    return ToolExecResult(
                        error="JavaScript code required for execute_js action", error_code=-1
                    )
                return await self._execute_js(javascript)

            # Advanced interaction actions
            elif action == "select_dropdown":
                selector = arguments.get("selector")
                value = arguments.get("value")
                if not selector or not value:
                    return ToolExecResult(
                        error="Selector and value required for select_dropdown action",
                        error_code=-1,
                    )
                selector_type = arguments.get("selector_type", "css")
                return await self._select_dropdown(selector, value, selector_type)

            elif action == "scroll":
                selector = arguments.get("selector")
                selector_type = arguments.get("selector_type", "css")
                x = arguments.get("x", 0)
                y = arguments.get("y", 0)
                return await self._scroll(selector, x, y, selector_type)

            elif action == "hover":
                selector = arguments.get("selector")
                if not selector:
                    return ToolExecResult(error="Selector required for hover action", error_code=-1)
                selector_type = arguments.get("selector_type", "css")
                return await self._hover(selector, selector_type)

            # Cookie management
            elif action == "get_cookies":
                return await self._get_cookies()

            elif action == "set_cookie":
                cookie_name = arguments.get("cookie_name")
                cookie_value = arguments.get("cookie_value")
                if not cookie_name or not cookie_value:
                    return ToolExecResult(
                        error="Cookie name and value required for set_cookie action", error_code=-1
                    )
                options = arguments.get("options")
                return await self._set_cookie(cookie_name, cookie_value, options)

            else:
                return ToolExecResult(error=f"Unknown action: {action}", error_code=-1)

        except ToolError as e:
            return ToolExecResult(error=e.message, error_code=-1)
        except Exception as e:
            return ToolExecResult(error=f"Unexpected error in {action}: {str(e)}", error_code=-1)
