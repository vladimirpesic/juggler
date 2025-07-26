"""
Python language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Python code.
It extracts functions, classes, and other code constructs from Python AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    FunctionEntry,
    ModuleEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_python(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_module: ModuleEntry | None = None,
) -> None:
    """
    Recursively visit the Python AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
        parent_module: The parent module if current node is within a module
    """
    # Handle function definitions
    if root_node.type == "function_definition":
        function_name_node = root_node.child_by_field_name("name")
        if function_name_node:
            function_entry = FunctionEntry(
                name=function_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Determine parent relationships
            if parent_function and parent_class:
                # Determine if the function is a method of the class or a function within a function
                if (
                    parent_function.start_line >= parent_class.start_line
                    and parent_function.end_line <= parent_class.end_line
                ):
                    function_entry.parent_function = parent_function.name
                else:
                    function_entry.parent_class = parent_class.name
            elif parent_function:
                function_entry.parent_function = parent_function.name
            elif parent_class:
                function_entry.parent_class = parent_class.name

            ckg_db._insert_entry(function_entry)
            parent_function = function_entry

    # Handle class definitions
    elif root_node.type == "class_definition":
        class_name_node = root_node.child_by_field_name("name")
        if class_name_node:
            class_body_node = root_node.child_by_field_name("body")
            class_methods = ""
            class_fields = ""

            class_entry = ClassEntry(
                name=class_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract methods and fields from class body
            if class_body_node:
                for child in class_body_node.children:
                    function_definition_node = None
                    if child.type == "decorated_definition":
                        function_definition_node = child.child_by_field_name(
                            "definition"
                        )
                    elif child.type == "function_definition":
                        function_definition_node = child

                    if function_definition_node:
                        method_name_node = function_definition_node.child_by_field_name(
                            "name"
                        )
                        if method_name_node:
                            parameters_node = (
                                function_definition_node.child_by_field_name(
                                    "parameters"
                                )
                            )
                            return_type_node = child.child_by_field_name("return_type")

                            class_method_info = method_name_node.text.decode()  # type: ignore
                            if parameters_node:
                                class_method_info += f"{parameters_node.text.decode()}"  # type: ignore
                            if return_type_node:
                                class_method_info += (
                                    f" -> {return_type_node.text.decode()}"  # type: ignore
                                )
                            class_methods += f"- {class_method_info}\n"

                    # Handle assignments as potential class fields
                    elif child.type == "assignment":
                        target_node = child.child_by_field_name("left")
                        if target_node:
                            class_fields += f"- {target_node.text.decode()}\n"  # type: ignore

            class_entry.methods = class_methods.strip() if class_methods != "" else None
            class_entry.fields = class_fields.strip() if class_fields != "" else None
            parent_class = class_entry
            ckg_db._insert_entry(class_entry)

    # Handle module-level imports to extract modules
    elif root_node.type == "import_statement":
        # Extract imported module names
        for child in root_node.children:
            if child.type == "dotted_name":
                module_name = child.text.decode()  # type: ignore
                module_entry = ModuleEntry(
                    name=module_name,
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )
                ckg_db._insert_entry(module_entry)

    elif root_node.type == "import_from_statement":
        # Extract module names from "from ... import ..." statements
        module_name_node = root_node.child_by_field_name("module_name")
        if module_name_node:
            module_name = module_name_node.text.decode()  # type: ignore
            module_entry = ModuleEntry(
                name=module_name,
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )
            ckg_db._insert_entry(module_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_python(
                ckg_db, child, file_path, parent_class, parent_function, parent_module
            )
