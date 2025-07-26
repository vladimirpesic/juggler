# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import tempfile
import unittest
from pathlib import Path

from trae_agent.tools.base import ToolCallArguments
from trae_agent.tools.ckg_tool import CKGTool


class TestCKGTool(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tool = CKGTool()

        # Create temporary directory with test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create test Python file
        python_file = self.temp_path / "test_code.py"
        python_file.write_text("""
class TestClass:
    def __init__(self):
        self.value = 0
    
    def test_method(self):
        return "test"

def standalone_function():
    return "standalone"

class AnotherClass:
    def special_method(self):
        return "special"
""")

        # Create test JavaScript file
        js_file = self.temp_path / "test_code.js"
        js_file.write_text("""
class TestJSClass {
    constructor() {
        this.value = 0;
    }
    
    testMethod() {
        return "test";
    }
}

function standaloneJSFunction() {
    return "standalone";
}
""")

    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()

    async def test_tool_initialization(self):
        """Test that the CKGTool initializes correctly."""
        self.assertEqual(self.tool.get_name(), "ckg")
        self.assertIn("Query the code knowledge graph", self.tool.get_description())

        params = self.tool.get_parameters()
        param_names = [p.name for p in params]
        self.assertIn("command", param_names)
        self.assertIn("path", param_names)
        self.assertIn("identifier", param_names)
        self.assertIn("print_body", param_names)

    async def test_search_function(self):
        """Test searching for functions."""
        args = ToolCallArguments(
            {
                "command": "search_function",
                "path": str(self.temp_path),
                "identifier": "standalone_function",
                "print_body": False,
            }
        )

        result = await self.tool.execute(args)
        self.assertIsNone(result.error)
        self.assertIn("Found 1 functions named standalone_function", result.output)
        self.assertIn("test_code.py", result.output)

    async def test_search_class(self):
        """Test searching for classes."""
        args = ToolCallArguments(
            {
                "command": "search_class",
                "path": str(self.temp_path),
                "identifier": "TestClass",
                "print_body": False,
            }
        )

        result = await self.tool.execute(args)
        self.assertIsNone(result.error)
        self.assertIn("Found 1 classes named TestClass", result.output)
        self.assertIn("Methods:", result.output)
        self.assertIn("__init__", result.output)
        self.assertIn("test_method", result.output)

    async def test_search_class_method(self):
        """Test searching for class methods."""
        args = ToolCallArguments(
            {
                "command": "search_class_method",
                "path": str(self.temp_path),
                "identifier": "test_method",
                "print_body": False,
            }
        )

        result = await self.tool.execute(args)
        self.assertIsNone(result.error)
        self.assertIn("Found 1 class methods named test_method", result.output)
        self.assertIn("within class TestClass", result.output)

    async def test_print_body_parameter(self):
        """Test the print_body parameter functionality."""
        # Test without body
        args_no_body = ToolCallArguments(
            {
                "command": "search_function",
                "path": str(self.temp_path),
                "identifier": "standalone_function",
                "print_body": False,
            }
        )

        result_no_body = await self.tool.execute(args_no_body)
        self.assertIsNone(result_no_body.error)
        self.assertNotIn("def standalone_function", result_no_body.output)

        # Test with body
        args_with_body = ToolCallArguments(
            {
                "command": "search_function",
                "path": str(self.temp_path),
                "identifier": "standalone_function",
                "print_body": True,
            }
        )

        result_with_body = await self.tool.execute(args_with_body)
        self.assertIsNone(result_with_body.error)
        self.assertIn("def standalone_function", result_with_body.output)

    async def test_nonexistent_identifier(self):
        """Test searching for non-existent identifiers."""
        args = ToolCallArguments(
            {
                "command": "search_function",
                "path": str(self.temp_path),
                "identifier": "NonExistentFunction",
                "print_body": False,
            }
        )

        result = await self.tool.execute(args)
        self.assertIsNone(result.error)
        self.assertIn("No functions named NonExistentFunction found", result.output)

    async def test_invalid_path_error(self):
        """Test error handling for invalid paths."""
        args = ToolCallArguments(
            {
                "command": "search_function",
                "path": "/non/existent/path",
                "identifier": "test",
                "print_body": False,
            }
        )

        result = await self.tool.execute(args)
        self.assertIsNotNone(result.error)
        self.assertIn("does not exist", result.error)

    async def test_missing_parameters(self):
        """Test error handling for missing required parameters."""
        # Missing command
        args = ToolCallArguments({"path": str(self.temp_path), "identifier": "test"})

        result = await self.tool.execute(args)
        self.assertIsNotNone(result.error)
        self.assertIn("No command provided", result.error)

        # Missing path
        args = ToolCallArguments({"command": "search_function", "identifier": "test"})

        result = await self.tool.execute(args)
        self.assertIsNotNone(result.error)
        self.assertIn("No path provided", result.error)

        # Missing identifier
        args = ToolCallArguments({"command": "search_function", "path": str(self.temp_path)})

        result = await self.tool.execute(args)
        self.assertIsNotNone(result.error)
        self.assertIn("No identifier provided", result.error)

    async def test_invalid_command(self):
        """Test error handling for invalid commands."""
        args = ToolCallArguments(
            {
                "command": "invalid_command",
                "path": str(self.temp_path),
                "identifier": "test",
                "print_body": False,
            }
        )

        result = await self.tool.execute(args)
        self.assertIsNotNone(result.error)
        self.assertIn("Invalid command", result.error)

    async def test_multi_language_support(self):
        """Test that CKGTool works with multiple programming languages."""
        # Test JavaScript class search
        args = ToolCallArguments(
            {
                "command": "search_class",
                "path": str(self.temp_path),
                "identifier": "TestJSClass",
                "print_body": False,
            }
        )

        result = await self.tool.execute(args)
        self.assertIsNone(result.error)
        self.assertIn("Found 1 classes named TestJSClass", result.output)
        self.assertIn("constructor", result.output)
        self.assertIn("testMethod", result.output)

        # Test JavaScript function search
        args = ToolCallArguments(
            {
                "command": "search_function",
                "path": str(self.temp_path),
                "identifier": "standaloneJSFunction",
                "print_body": False,
            }
        )

        result = await self.tool.execute(args)
        self.assertIsNone(result.error)
        self.assertIn("Found 1 functions named standaloneJSFunction", result.output)

    async def test_database_persistence(self):
        """Test that the database is reused across multiple calls."""
        # First call to initialize database
        args1 = ToolCallArguments(
            {
                "command": "search_function",
                "path": str(self.temp_path),
                "identifier": "standalone_function",
                "print_body": False,
            }
        )

        result1 = await self.tool.execute(args1)
        self.assertIsNone(result1.error)

        # Second call should reuse the same database
        args2 = ToolCallArguments(
            {
                "command": "search_class",
                "path": str(self.temp_path),
                "identifier": "TestClass",
                "print_body": False,
            }
        )

        result2 = await self.tool.execute(args2)
        self.assertIsNone(result2.error)
        self.assertIn("Found 1 classes named TestClass", result2.output)


if __name__ == "__main__":
    unittest.main()
