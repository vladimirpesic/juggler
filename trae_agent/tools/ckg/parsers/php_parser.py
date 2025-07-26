"""
PHP language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for PHP code.
It extracts classes, interfaces, traits, functions, and other code constructs from PHP AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    EnumEntry,
    FunctionEntry,
    InterfaceEntry,
    NamespaceEntry,
    TraitEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_php(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_interface: InterfaceEntry | None = None,
    parent_trait: TraitEntry | None = None,
    parent_namespace: NamespaceEntry | None = None,
) -> None:
    """
    Recursively visit the PHP AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
        parent_interface: The parent interface if current node is within an interface
        parent_trait: The parent trait if current node is within a trait
        parent_namespace: The parent namespace if current node is within a namespace
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

            if parent_class:
                function_entry.parent_class = parent_class.name
            elif parent_trait:
                function_entry.parent_class = parent_trait.name
            elif parent_interface:
                function_entry.parent_class = parent_interface.name
            elif parent_function:
                function_entry.parent_function = parent_function.name

            ckg_db._insert_entry(function_entry)
            parent_function = function_entry

    # Handle method definitions
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
            elif parent_trait:
                method_entry.parent_class = parent_trait.name
            elif parent_interface:
                method_entry.parent_class = parent_interface.name

            ckg_db._insert_entry(method_entry)

    # Handle class declarations
    elif root_node.type == "class_declaration":
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
            class_body_node = root_node.child_by_field_name("body")
            class_methods = ""
            class_fields = ""

            if class_body_node:
                for child in class_body_node.children:
                    if child.type == "method_declaration":
                        method_name = child.child_by_field_name("name")
                        if method_name:
                            class_methods += f"- {method_name.text.decode()}\n"  # type: ignore
                    elif child.type == "property_declaration":
                        class_fields += f"- {child.text.decode()}\n"  # type: ignore

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

            # Extract methods from interface body
            interface_body_node = root_node.child_by_field_name("body")
            interface_methods = ""

            if interface_body_node:
                for child in interface_body_node.children:
                    if child.type == "method_declaration":
                        method_name = child.child_by_field_name("name")
                        if method_name:
                            interface_methods += f"- {method_name.text.decode()}\n"  # type: ignore

            interface_entry.methods = (
                interface_methods.strip() if interface_methods != "" else None
            )
            parent_interface = interface_entry
            ckg_db._insert_entry(interface_entry)

    # Handle trait declarations
    elif root_node.type == "trait_declaration":
        trait_name_node = root_node.child_by_field_name("name")
        if trait_name_node:
            trait_entry = TraitEntry(
                name=trait_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract methods from trait body
            trait_body_node = root_node.child_by_field_name("body")
            trait_methods = ""

            if trait_body_node:
                for child in trait_body_node.children:
                    if child.type == "method_declaration":
                        method_name = child.child_by_field_name("name")
                        if method_name:
                            trait_methods += f"- {method_name.text.decode()}\n"  # type: ignore

            trait_entry.methods = trait_methods.strip() if trait_methods != "" else None
            parent_trait = trait_entry
            ckg_db._insert_entry(trait_entry)

    # Handle enum declarations (PHP 8.1+)
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

            # Extract enum cases from enum body
            enum_body_node = root_node.child_by_field_name("body")
            enum_variants = ""

            if enum_body_node:
                for child in enum_body_node.children:
                    if child.type == "enum_case":
                        case_name_node = child.child_by_field_name("name")
                        if case_name_node:
                            enum_variants += f"- {case_name_node.text.decode()}\n"  # type: ignore

            enum_entry.variants = enum_variants.strip() if enum_variants != "" else None
            ckg_db._insert_entry(enum_entry)

    # Handle namespace declarations
    elif root_node.type == "namespace_definition":
        namespace_name_node = root_node.child_by_field_name("name")
        if namespace_name_node:
            namespace_entry = NamespaceEntry(
                name=namespace_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract members from namespace body
            namespace_body_node = root_node.child_by_field_name("body")
            namespace_members = ""

            if namespace_body_node:
                for child in namespace_body_node.children:
                    if child.type in [
                        "class_declaration",
                        "interface_declaration",
                        "trait_declaration",
                        "function_definition",
                    ]:
                        name_node = child.child_by_field_name("name")
                        if name_node:
                            namespace_members += (
                                f"- {child.type}: {name_node.text.decode()}\n"  # type: ignore
                            )

            namespace_entry.members = (
                namespace_members.strip() if namespace_members != "" else None
            )
            parent_namespace = namespace_entry
            ckg_db._insert_entry(namespace_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_php(
                ckg_db,
                child,
                file_path,
                parent_class,
                parent_function,
                parent_interface,
                parent_trait,
                parent_namespace,
            )
