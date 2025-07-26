"""
JavaScript language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for JavaScript code.
It extracts functions, classes, and other code constructs from JavaScript AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    ComponentEntry,
    FunctionEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_javascript(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
) -> None:
    """
    Recursively visit the JavaScript AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
    """
    # Handle class declarations
    if root_node.type == "class_declaration":
        class_name_node = root_node.child_by_field_name("name")
        if class_name_node:
            class_entry = ClassEntry(
                name=class_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            methods = ""
            fields = ""
            class_body_node = root_node.child_by_field_name("body")

            if class_body_node:
                for child in class_body_node.children:
                    if child.type == "method_definition":
                        method_builder = ""
                        for method_property in child.children:
                            if method_property.type == "statement_block":
                                break
                            method_builder += f"{method_property.text.decode()} "  # type: ignore
                        method_builder = method_builder.strip()
                        methods += f"- {method_builder}\n"
                    elif child.type == "public_field_definition":
                        fields += f"- {child.text.decode()}\n"  # type: ignore
                    elif child.type == "field_definition":
                        fields += f"- {child.text.decode()}\n"  # type: ignore

            class_entry.methods = methods.strip() if methods != "" else None
            class_entry.fields = fields.strip() if fields != "" else None
            parent_class = class_entry
            ckg_db._insert_entry(class_entry)

    # Handle class expressions (assigned to variables)
    elif root_node.type == "class_expression":
        # Try to find parent assignment to get the name
        class_name = "AnonymousClass"
        parent_node = root_node.parent if hasattr(root_node, "parent") else None
        if parent_node and parent_node.type == "variable_declarator":
            name_node = parent_node.child_by_field_name("name")
            if name_node:
                class_name = name_node.text.decode()  # type: ignore

        class_entry = ClassEntry(
            name=class_name,
            file_path=file_path,
            body=root_node.text.decode(),  # type: ignore
            start_line=root_node.start_point[0] + 1,
            end_line=root_node.end_point[0] + 1,
        )

        methods = ""
        fields = ""
        class_body_node = root_node.child_by_field_name("body")

        if class_body_node:
            for child in class_body_node.children:
                if child.type == "method_definition":
                    method_builder = ""
                    for method_property in child.children:
                        if method_property.type == "statement_block":
                            break
                        method_builder += f"{method_property.text.decode()} "  # type: ignore
                    method_builder = method_builder.strip()
                    methods += f"- {method_builder}\n"
                elif child.type in ["public_field_definition", "field_definition"]:
                    fields += f"- {child.text.decode()}\n"  # type: ignore

        class_entry.methods = methods.strip() if methods != "" else None
        class_entry.fields = fields.strip() if fields != "" else None
        parent_class = class_entry
        ckg_db._insert_entry(class_entry)

    # Handle function declarations
    elif root_node.type == "function_declaration":
        function_name_node = root_node.child_by_field_name("name")
        if function_name_node:
            function_entry = FunctionEntry(
                name=function_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            if parent_class:
                function_entry.parent_class = parent_class.name
            elif parent_function:
                function_entry.parent_function = parent_function.name

            ckg_db._insert_entry(function_entry)
            parent_function = function_entry

    # Handle function expressions (const myFunc = function() {})
    elif root_node.type == "function_expression" or root_node.type == "arrow_function":
        # For function expressions, we need to look at the parent context
        # to determine the name (if it's assigned to a variable)
        function_name = f"anonymous_fn_line_{root_node.start_point[0] + 1}"

        # Try to get name from parent assignment or variable declaration
        if hasattr(root_node, "parent") and root_node.parent:
            parent_node = root_node.parent
            if parent_node.type == "variable_declarator":
                name_node = parent_node.child_by_field_name("name")
                if name_node:
                    function_name = name_node.text.decode()  # type: ignore
            elif parent_node.type == "assignment_expression":
                left_node = parent_node.child_by_field_name("left")
                if left_node:
                    function_name = left_node.text.decode()  # type: ignore

        function_entry = FunctionEntry(
            name=function_name,
            file_path=file_path,
            body=root_node.text.decode(),  # type: ignore
            start_line=root_node.start_point[0] + 1,
            end_line=root_node.end_point[0] + 1,
        )

        if parent_class:
            function_entry.parent_class = parent_class.name
        elif parent_function:
            function_entry.parent_function = parent_function.name

        ckg_db._insert_entry(function_entry)
        parent_function = function_entry

    # Handle JSX elements (React components)
    elif root_node.type in ["jsx_element", "jsx_self_closing_element"]:
        component_name = None

        # Extract component name from jsx_opening_element or jsx_self_closing_element
        if root_node.type == "jsx_element":
            opening_element = root_node.child_by_field_name("open_tag")
            if opening_element:
                name_node = opening_element.child_by_field_name("name")
                if name_node:
                    component_name = name_node.text.decode()  # type: ignore
        elif root_node.type == "jsx_self_closing_element":
            name_node = root_node.child_by_field_name("name")
            if name_node:
                component_name = name_node.text.decode()  # type: ignore

        # Only create component entries for custom components (capitalized names)
        if component_name and component_name[0].isupper():
            component_entry = ComponentEntry(
                name=component_name,
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )
            ckg_db._insert_entry(component_entry)

    # Handle method definitions
    elif root_node.type == "method_definition":
        method_name_node = root_node.child_by_field_name("name")
        if method_name_node:
            method_entry = FunctionEntry(
                name=method_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            if parent_class:
                method_entry.parent_class = parent_class.name

            ckg_db._insert_entry(method_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_javascript(
                ckg_db, child, file_path, parent_class, parent_function
            )
