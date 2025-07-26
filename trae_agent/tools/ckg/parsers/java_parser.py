"""
Java language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Java code.
It extracts functions, classes, interfaces, enums and other code constructs from Java AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    EnumEntry,
    FunctionEntry,
    InterfaceEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_java(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_interface: InterfaceEntry | None = None,
) -> None:
    """
    Recursively visit the Java AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
        parent_interface: The parent interface if current node is within an interface
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

            class_body_node = root_node.child_by_field_name("body")
            class_methods = ""
            class_fields = ""

            if class_body_node:
                for child in class_body_node.children:
                    if child.type == "field_declaration":
                        class_fields += f"- {child.text.decode()}\n"  # type: ignore
                    elif child.type == "method_declaration":
                        method_builder = ""
                        for method_property in child.children:
                            if method_property.type == "block":
                                break
                            method_builder += f"{method_property.text.decode()} "  # type: ignore
                        method_builder = method_builder.strip()
                        class_methods += f"- {method_builder}\n"

            class_entry.methods = class_methods.strip() if class_methods != "" else None
            class_entry.fields = class_fields.strip() if class_fields != "" else None
            parent_class = class_entry
            ckg_db._insert_entry(class_entry)

    # Handle interface declarations
    elif root_node.type == "interface_declaration":
        interface_name_node = root_node.child_by_field_name("name")
        if interface_name_node:
            interface_entry = InterfaceEntry(
                name=interface_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            interface_body_node = root_node.child_by_field_name("body")
            interface_methods = ""

            if interface_body_node:
                for child in interface_body_node.children:
                    if child.type == "method_declaration":
                        method_builder = ""
                        for method_property in child.children:
                            if method_property.type == "block":
                                break
                            method_builder += f"{method_property.text.decode()} "  # type: ignore
                        method_builder = method_builder.strip()
                        interface_methods += f"- {method_builder}\n"

            interface_entry.methods = (
                interface_methods.strip() if interface_methods != "" else None
            )
            parent_interface = interface_entry
            ckg_db._insert_entry(interface_entry)

    # Handle enum declarations
    elif root_node.type == "enum_declaration":
        enum_name_node = root_node.child_by_field_name("name")
        if enum_name_node:
            enum_entry = EnumEntry(
                name=enum_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            enum_body_node = root_node.child_by_field_name("body")
            enum_variants = ""

            if enum_body_node:
                for child in enum_body_node.children:
                    if child.type == "enum_constant":
                        enum_variants += f"- {child.text.decode()}\n"  # type: ignore

            enum_entry.variants = enum_variants.strip() if enum_variants != "" else None
            if parent_class:
                enum_entry.parent_class = parent_class.name
            ckg_db._insert_entry(enum_entry)

    # Handle method declarations
    elif root_node.type == "method_declaration":
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
            elif parent_interface:
                method_entry.parent_class = (
                    parent_interface.name
                )  # Store interface as parent_class for consistency

            ckg_db._insert_entry(method_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_java(
                ckg_db,
                child,
                file_path,
                parent_class,
                parent_function,
                parent_interface,
            )
