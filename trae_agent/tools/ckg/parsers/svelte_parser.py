"""
Svelte language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Svelte code.
It extracts components, scripts, and other code constructs from Svelte AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ComponentEntry,
    FunctionEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_svelte(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_component: ComponentEntry | None = None,
    parent_function: FunctionEntry | None = None,
) -> None:
    """
    Recursively visit the Svelte AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_component: The parent component if current node is within a component
        parent_function: The parent function if current node is within a function
    """
    # For Svelte files, we'll treat the whole file as a component
    if root_node.type == "document" or root_node.type == "source_file":
        # Extract the component name from the file path
        import os

        component_name = os.path.splitext(os.path.basename(file_path))[0]

        component_entry = ComponentEntry(
            name=component_name,
            file_path=file_path,
            body=root_node.text.decode(),  # type: ignore
            start_line=root_node.start_point[0] + 1,
            end_line=root_node.end_point[0] + 1,
        )

        # Extract scripts, props, and template from component
        component_methods = ""
        component_props = ""
        component_template = ""

        for child in root_node.children:
            if child.type == "script_element":
                # Extract functions from script
                for script_child in child.children:
                    if script_child.type == "raw_text":
                        script_content = script_child.text.decode()  # type: ignore
                        # Simple extraction of function declarations
                        import re

                        function_matches = re.findall(
                            r"function\s+(\w+)|const\s+(\w+)\s*=.*?=>", script_content
                        )
                        for match in function_matches:
                            func_name = match[0] or match[1]
                            if func_name:
                                component_methods += f"- {func_name}\n"

                        # Extract props (export let statements)
                        prop_matches = re.findall(
                            r"export\s+let\s+(\w+)", script_content
                        )
                        for prop in prop_matches:
                            component_props += f"- {prop}\n"

            elif child.type in ["element", "text", "mustache"]:
                # This represents the template part
                component_template += child.text.decode()  # type: ignore

        component_entry.methods = (
            component_methods.strip() if component_methods != "" else None
        )
        component_entry.props = (
            component_props.strip() if component_props != "" else None
        )
        component_entry.template = (
            component_template.strip() if component_template != "" else None
        )
        parent_component = component_entry
        ckg_db._insert_entry(component_entry)

    # Handle script elements
    elif root_node.type == "script_element":
        for child in root_node.children:
            if child.type == "raw_text":
                script_content = child.text.decode()  # type: ignore
                # Extract function declarations from script content
                import re

                # Function declarations
                function_matches = re.finditer(  # type: ignore
                    r"function\s+(\w+)\s*\([^)]*\)\s*{", script_content
                )
                for match in function_matches:
                    function_entry = FunctionEntry(
                        name=match.group(1),
                        file_path=file_path,
                        body=script_content[
                            match.start() :
                        ],  # Simplified - would need proper parsing
                        start_line=root_node.start_point[0] + 1,
                        end_line=root_node.end_point[0] + 1,
                    )

                    if parent_component:
                        function_entry.parent_class = parent_component.name
                    elif parent_function:
                        function_entry.parent_function = parent_function.name

                    ckg_db._insert_entry(function_entry)

                # Arrow function declarations
                arrow_matches = re.finditer(
                    r"(?:const|let|var)\s+(\w+)\s*=.*?=>", script_content
                )
                for match in arrow_matches:
                    function_entry = FunctionEntry(
                        name=match.group(1),
                        file_path=file_path,
                        body=script_content[match.start() :],  # Simplified
                        start_line=root_node.start_point[0] + 1,
                        end_line=root_node.end_point[0] + 1,
                    )

                    if parent_component:
                        function_entry.parent_class = parent_component.name
                    elif parent_function:
                        function_entry.parent_function = parent_function.name

                    ckg_db._insert_entry(function_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_svelte(
                ckg_db, child, file_path, parent_component, parent_function
            )
