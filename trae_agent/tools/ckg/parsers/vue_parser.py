"""
Vue language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Vue code.
It extracts components, scripts, templates, and other code constructs from Vue AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ComponentEntry,
    FunctionEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_vue(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_component: ComponentEntry | None = None,
    parent_function: FunctionEntry | None = None,
) -> None:
    """
    Recursively visit the Vue AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_component: The parent component if current node is within a component
        parent_function: The parent function if current node is within a function
    """
    # For Vue files, we'll treat the whole file as a component
    if root_node.type in ["document", "source_file", "program"]:
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
                # Extract functions and props from script
                for script_child in child.children:
                    if script_child.type == "raw_text":
                        script_content = script_child.text.decode()  # type: ignore
                        # Simple extraction using regex for common Vue patterns
                        import re

                        # Extract methods from Vue options API
                        methods_match = re.search(
                            r"methods\s*:\s*{([^}]*)}", script_content, re.DOTALL
                        )
                        if methods_match:
                            methods_content = methods_match.group(1)
                            method_matches = re.findall(
                                r"(\w+)\s*\([^)]*\)\s*{", methods_content
                            )
                            for method in method_matches:
                                component_methods += f"- {method}\n"

                        # Extract function declarations
                        function_matches = re.findall(
                            r"function\s+(\w+)|const\s+(\w+)\s*=.*?=>", script_content
                        )
                        for match in function_matches:
                            func_name = match[0] or match[1]
                            if func_name:
                                component_methods += f"- {func_name}\n"

                        # Extract props from Vue options API
                        props_match = re.search(
                            r"props\s*:\s*(?:\[([^\]]*)\]|{([^}]*)})",
                            script_content,
                            re.DOTALL,
                        )
                        if props_match:
                            props_content = props_match.group(1) or props_match.group(2)
                            if props_content:
                                # Array format: ['prop1', 'prop2']
                                array_props = re.findall(
                                    r"['\"](\w+)['\"]", props_content
                                )
                                for prop in array_props:
                                    component_props += f"- {prop}\n"

                                # Object format: { prop1: Type, prop2: {...} }
                                object_props = re.findall(r"(\w+)\s*:", props_content)
                                for prop in object_props:
                                    component_props += f"- {prop}\n"

                        # Extract props from Composition API (defineProps)
                        define_props_match = re.search(
                            r"defineProps\s*(?:<[^>]*>)?\s*\(\s*(?:\[([^\]]*)\]|{([^}]*)})",
                            script_content,
                            re.DOTALL,
                        )
                        if define_props_match:
                            props_content = define_props_match.group(
                                1
                            ) or define_props_match.group(2)
                            if props_content:
                                array_props = re.findall(
                                    r"['\"](\w+)['\"]", props_content
                                )
                                for prop in array_props:
                                    component_props += f"- {prop}\n"
                                object_props = re.findall(r"(\w+)\s*:", props_content)
                                for prop in object_props:
                                    component_props += f"- {prop}\n"

            elif child.type == "template_element":
                # Extract template content
                for template_child in child.children:
                    if template_child.type == "raw_text":
                        component_template += template_child.text.decode()  # type: ignore

            elif child.type in ["element", "text", "interpolation"]:
                # This represents template content when not in template_element
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

    # Handle component definitions (SFC structure)
    elif root_node.type == "component":
        component_name_attr = None
        # Try to extract component name from attributes
        for child in root_node.children:
            if child.type == "start_tag":
                for attr_child in child.children:
                    if (
                        attr_child.type == "attribute"
                        and "name" in attr_child.text.decode()
                    ):
                        component_name_attr = attr_child.text.decode()
                        break

        component_name = (
            component_name_attr or f"Component_line_{root_node.start_point[0] + 1}"
        )

        component_entry = ComponentEntry(
            name=component_name,
            file_path=file_path,
            body=root_node.text.decode(),  # type: ignore
            start_line=root_node.start_point[0] + 1,
            end_line=root_node.end_point[0] + 1,
        )

        ckg_db._insert_entry(component_entry)
        parent_component = component_entry

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

                # Methods from Vue options API
                methods_matches = re.finditer(r"(\w+)\s*\([^)]*\)\s*{", script_content)
                for match in methods_matches:
                    # Skip function declarations already handled above
                    preceding_text = script_content[
                        max(0, match.start() - 20) : match.start()
                    ]
                    if "function" not in preceding_text:
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

    # Handle JavaScript/TypeScript constructs within Vue files
    elif root_node.type in [
        "function_declaration",
        "function_expression",
        "arrow_function",
    ]:
        function_name_node = root_node.child_by_field_name("name")
        function_name = (
            function_name_node.text.decode()
            if function_name_node
            else f"anonymous_fn_line_{root_node.start_point[0] + 1}"
        )  # type: ignore

        function_entry = FunctionEntry(
            name=function_name,
            file_path=file_path,
            body=root_node.text.decode(),  # type: ignore
            start_line=root_node.start_point[0] + 1,
            end_line=root_node.end_point[0] + 1,
        )

        if parent_component:
            function_entry.parent_class = parent_component.name
        elif parent_function:
            function_entry.parent_function = parent_function.name

        ckg_db._insert_entry(function_entry)
        parent_function = function_entry

    # Handle method definitions within JavaScript objects
    elif root_node.type == "method_definition":
        method_name_node = root_node.child_by_field_name("name")
        if method_name_node:
            function_entry = FunctionEntry(
                name=method_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
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
            recursive_visit_vue(
                ckg_db, child, file_path, parent_component, parent_function
            )
