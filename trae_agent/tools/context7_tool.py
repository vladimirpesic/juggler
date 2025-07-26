"""Context7 tool for retrieving up-to-date library documentation and code examples."""

from typing import Any, override

import httpx

from .base import Tool, ToolCallArguments, ToolExecResult, ToolParameter


class Context7Tool(Tool):
    """
    Context7 tool that provides access to up-to-date library documentation and code examples.

    This tool can:
    - Search for libraries by name to get Context7-compatible library IDs
    - Fetch detailed documentation and code examples for specific libraries
    """

    def __init__(self, model_provider: str | None = None):
        super().__init__(model_provider)
        self._base_url = "https://context7.com/api/v1"
        self._default_tokens = 10000
        self._timeout = 30.0

    @override
    def get_name(self) -> str:
        return "context7"

    @override
    def get_description(self) -> str:
        return """Access up-to-date documentation and code examples for any library using Context7.

This tool can perform two main actions:
1. 'search': Search for libraries by name to find Context7-compatible library IDs
2. 'get_docs': Fetch detailed documentation and code examples using a library ID

Usage examples:
- Search for a library: action='search', library_name='react'
- Get documentation: action='get_docs', library_id='/facebook/react', topic='hooks'

The tool fetches current, version-specific documentation directly from library sources,
providing more accurate and up-to-date information than static training data."""

    @override
    def get_parameters(self) -> list[ToolParameter]:
        # For OpenAI models, all parameters must be required=True
        # For other providers, optional parameters can have required=False
        openai_mode = self.model_provider == "openai"

        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform: 'search' to find libraries, 'get_docs' to fetch documentation",
                enum=["search", "get_docs"],
                required=True,
            ),
            ToolParameter(
                name="library_name",
                type="string",
                description="Library name to search for (required when action='search')",
                required=openai_mode,
            ),
            ToolParameter(
                name="library_id",
                type="string",
                description="Context7-compatible library ID (required when action='get_docs', format: '/org/project' or '/org/project/version')",
                required=openai_mode,
            ),
            ToolParameter(
                name="topic",
                type="string",
                description="Optional topic to focus documentation on (e.g., 'hooks', 'routing', 'authentication')",
                required=openai_mode,
            ),
            ToolParameter(
                name="tokens",
                type="integer",
                description=f"Maximum number of tokens to return for documentation (default: {self._default_tokens}, minimum: {self._default_tokens})",
                required=openai_mode,
            ),
        ]

    @override
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        """Execute the Context7 tool based on the provided action."""
        try:
            action = str(arguments.get("action", "")).lower()

            if action == "search":
                return await self._search_libraries(arguments)
            elif action == "get_docs":
                return await self._get_documentation(arguments)
            else:
                return ToolExecResult(
                    error=f"Invalid action '{action}'. Must be 'search' or 'get_docs'.",
                    error_code=1,
                )
        except Exception as e:
            return ToolExecResult(
                error=f"Error executing Context7 tool: {str(e)}",
                error_code=1,
            )

    async def _search_libraries(self, arguments: ToolCallArguments) -> ToolExecResult:
        """Search for libraries by name and return Context7-compatible library IDs."""
        library_name = arguments.get("library_name")
        if not library_name:
            return ToolExecResult(
                error="library_name is required when action='search'",
                error_code=1,
            )

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/search",
                    params={"query": str(library_name)},
                    headers=self._get_headers(),
                )

                if response.status_code == 429:
                    return ToolExecResult(
                        error="Rate limited. Please try again later.",
                        error_code=429,
                    )
                elif response.status_code != 200:
                    return ToolExecResult(
                        error=f"Failed to search libraries. Status code: {response.status_code}",
                        error_code=response.status_code,
                    )

                data = response.json()
                results = data.get("results", [])

                if not results:
                    return ToolExecResult(
                        output=f"No libraries found matching '{library_name}'. Try using more specific or alternative terms.",
                        error_code=0,
                    )

                # Format search results
                formatted_results = self._format_search_results(results, str(library_name))
                return ToolExecResult(output=formatted_results, error_code=0)

        except httpx.TimeoutException:
            return ToolExecResult(
                error="Request timed out. Please try again.",
                error_code=1,
            )
        except Exception as e:
            return ToolExecResult(
                error=f"Error searching libraries: {str(e)}",
                error_code=1,
            )

    async def _get_documentation(self, arguments: ToolCallArguments) -> ToolExecResult:
        """Fetch documentation for a specific library using its Context7 ID."""
        library_id = arguments.get("library_id")
        if not library_id:
            return ToolExecResult(
                error="library_id is required when action='get_docs'",
                error_code=1,
            )

        # Validate and normalize library_id
        library_id_str = str(library_id)
        if not library_id_str.startswith("/"):
            return ToolExecResult(
                error=f"Invalid library_id format: '{library_id_str}'. Must start with '/' (e.g., '/facebook/react')",
                error_code=1,
            )

        # Remove leading slash for API call
        normalized_id = library_id_str[1:]

        # Get optional parameters
        topic = arguments.get("topic", "")
        tokens = arguments.get("tokens", self._default_tokens)

        # Ensure minimum tokens
        if isinstance(tokens, (int, float)) and tokens < self._default_tokens:
            tokens = self._default_tokens

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                params = {
                    "type": "txt",
                    "tokens": str(tokens),
                }
                if topic:
                    params["topic"] = str(topic)

                response = await client.get(
                    f"{self._base_url}/{normalized_id}",
                    params=params,
                    headers=self._get_headers({"X-Context7-Source": "trae-agent"}),
                )

                if response.status_code == 429:
                    return ToolExecResult(
                        error="Rate limited. Please try again later.",
                        error_code=429,
                    )
                elif response.status_code == 404:
                    return ToolExecResult(
                        error=f"Library not found: '{library_id_str}'. Use the 'search' action to find valid library IDs.",
                        error_code=404,
                    )
                elif response.status_code != 200:
                    return ToolExecResult(
                        error=f"Failed to fetch documentation. Status code: {response.status_code}",
                        error_code=response.status_code,
                    )

                content = response.text
                if not content or content in ["No content available", "No context data available"]:
                    return ToolExecResult(
                        error=f"No documentation available for '{library_id_str}'. The library may not be finalized in Context7.",
                        error_code=1,
                    )

                # Format the documentation response
                formatted_docs = self._format_documentation(library_id_str, content, topic, tokens)
                return ToolExecResult(output=formatted_docs, error_code=0)

        except httpx.TimeoutException:
            return ToolExecResult(
                error="Request timed out. Please try again.",
                error_code=1,
            )
        except Exception as e:
            return ToolExecResult(
                error=f"Error fetching documentation: {str(e)}",
                error_code=1,
            )

    def _get_headers(self, additional_headers: dict[str, str] | None = None) -> dict[str, str]:
        """Get HTTP headers for Context7 API requests."""
        headers = {
            "User-Agent": "trae-agent-context7-tool/1.0",
            "Accept": "application/json, text/plain",
        }
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def _format_search_results(self, results: list[dict[str, Any]], query: str) -> str:
        """Format search results for display."""
        output = [
            f"Context7 Library Search Results for '{query}':",
            "=" * 50,
            "",
            "Each result includes:",
            "- Library ID: Context7-compatible identifier for use with get_docs action",
            "- Name: Library or package name",
            "- Description: Brief summary of the library",
            "- Code Snippets: Number of available code examples",
            "- Trust Score: Authority/reliability indicator (1-10)",
            "- Versions: Available versions (if any)",
            "",
            "Top matches:",
            "",
        ]

        for i, result in enumerate(results[:10], 1):  # Limit to top 10 results
            library_id = result.get("id", "")
            name = result.get("name", "Unknown")
            description = result.get("description", "No description available")
            snippets = result.get("code_snippets", 0)
            trust_score = result.get("trust_score", 0)
            versions = result.get("versions", [])

            output.extend(
                [
                    f"{i}. **{name}**",
                    f"   Library ID: `{library_id}`",
                    f"   Description: {description}",
                    f"   Code Snippets: {snippets}",
                    f"   Trust Score: {trust_score}/10",
                ]
            )

            if versions:
                versions_str = ", ".join(versions[:5])  # Show first 5 versions
                if len(versions) > 5:
                    versions_str += f" (and {len(versions) - 5} more)"
                output.append(f"   Available Versions: {versions_str}")

            output.append("")

        output.extend(
            [
                "To get documentation for any library, use:",
                "action='get_docs', library_id='<Library ID from above>'",
                "",
                "Example: action='get_docs', library_id='/facebook/react', topic='hooks'",
            ]
        )

        return "\n".join(output)

    def _format_documentation(
        self, library_id: str, content: str, topic: str | None, tokens: int
    ) -> str:
        """Format documentation content for display."""
        header_parts = [f"Context7 Documentation for {library_id}"]
        if topic:
            header_parts.append(f"(Topic: {topic})")

        header = " ".join(header_parts)
        separator = "=" * len(header)

        output = [
            header,
            separator,
            "",
            f"Token limit: {tokens}",
            f"Content length: ~{len(content.split())} words",
            "",
            "--- Documentation Content ---",
            "",
            content,
            "",
            "--- End of Documentation ---",
            "",
            "This documentation was fetched from Context7's up-to-date library database.",
            "For different topics or more content, adjust the 'topic' and 'tokens' parameters.",
        ]

        return "\n".join(output)
