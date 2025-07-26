"""
Ruby language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Ruby code.
It extracts classes, modules, methods, and other code constructs from Ruby AST.
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


def recursive_visit_ruby(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_module: ModuleEntry | None = None,
) -> None:
    """
    Recursively visit the Ruby AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
        parent_module: The parent module if current node is within a module
    """
    # Handle method definitions
    if root_node.type == "method":
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
            elif parent_module:
                method_entry.parent_class = parent_module.name
            elif parent_function:
                method_entry.parent_function = parent_function.name

            ckg_db._insert_entry(method_entry)
            parent_function = method_entry

    # Handle class definitions
    elif root_node.type == "class":
        class_name_node = root_node.child_by_field_name("name")
        if class_name_node:
            class_entry = ClassEntry(
                name=class_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract methods and fields from class body
            class_methods = ""
            class_fields = ""

            for child in root_node.children:
                if child.type == "method":
                    method_name = child.child_by_field_name("name")
                    if method_name:
                        class_methods += f"- {method_name.text.decode()}\n"  # type: ignore
                elif child.type in ["assignment", "instance_variable"]:
                    class_fields += f"- {child.text.decode()}\n"  # type: ignore

            class_entry.methods = class_methods.strip() if class_methods != "" else None
            class_entry.fields = class_fields.strip() if class_fields != "" else None
            parent_class = class_entry
            ckg_db._insert_entry(class_entry)

    # Handle module definitions
    elif root_node.type == "module":
        module_name_node = root_node.child_by_field_name("name")
        if module_name_node:
            module_entry = ModuleEntry(
                name=module_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract exports from module body
            module_exports = ""

            for child in root_node.children:
                if child.type in ["method", "class", "module"]:
                    name_node = child.child_by_field_name("name")
                    if name_node:
                        module_exports += f"- {child.type}: {name_node.text.decode()}\n"  # type: ignore

            module_entry.exports = (
                module_exports.strip() if module_exports != "" else None
            )
            parent_module = module_entry
            ckg_db._insert_entry(module_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_ruby(
                ckg_db, child, file_path, parent_class, parent_function, parent_module
            )
