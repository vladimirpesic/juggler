"""
TypeScript language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for TypeScript code.
It extracts functions, classes, interfaces, enums, types, and other code constructs from TypeScript AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    EnumEntry,
    FunctionEntry,
    InterfaceEntry,
    NamespaceEntry,
    TypeAliasEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_typescript(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_interface: InterfaceEntry | None = None,
    parent_namespace: NamespaceEntry | None = None,
) -> None:
    """
    Recursively visit the TypeScript AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
        parent_interface: The parent interface if current node is within an interface
        parent_namespace: The parent namespace if current node is within a namespace
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
                    elif child.type == "property_signature":
                        fields += f"- {child.text.decode()}\n"  # type: ignore

            class_entry.methods = methods.strip() if methods != "" else None
            class_entry.fields = fields.strip() if fields != "" else None
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
            interface_properties = ""

            if interface_body_node:
                for child in interface_body_node.children:
                    if child.type == "method_signature":
                        interface_methods += f"- {child.text.decode()}\n"  # type: ignore
                    elif child.type == "property_signature":
                        interface_properties += f"- {child.text.decode()}\n"  # type: ignore

            interface_entry.methods = (
                interface_methods.strip() if interface_methods != "" else None
            )
            interface_entry.properties = (
                interface_properties.strip() if interface_properties != "" else None
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
                    if child.type == "property_identifier":
                        enum_variants += f"- {child.text.decode()}\n"  # type: ignore

            enum_entry.variants = enum_variants.strip() if enum_variants != "" else None
            if parent_class:
                enum_entry.parent_class = parent_class.name
            ckg_db._insert_entry(enum_entry)

    # Handle type alias declarations
    elif root_node.type == "type_alias_declaration":
        type_name_node = root_node.child_by_field_name("name")
        if type_name_node:
            type_alias_entry = TypeAliasEntry(
                name=type_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            type_node = root_node.child_by_field_name("type")
            if type_node:
                type_alias_entry.target_type = type_node.text.decode()  # type: ignore

            ckg_db._insert_entry(type_alias_entry)

    # Handle namespace declarations
    elif (
        root_node.type == "namespace_declaration"
        or root_node.type == "module_declaration"
        or root_node.type == "internal_module"
    ):
        namespace_name_node = root_node.child_by_field_name("name")
        if namespace_name_node:
            namespace_entry = NamespaceEntry(
                name=namespace_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            namespace_body_node = root_node.child_by_field_name("body")
            namespace_members = ""

            if namespace_body_node:
                for child in namespace_body_node.children:
                    if child.type in [
                        "class_declaration",
                        "interface_declaration",
                        "function_declaration",
                        "enum_declaration",
                        "type_alias_declaration",
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
            recursive_visit_typescript(
                ckg_db,
                child,
                file_path,
                parent_class,
                parent_function,
                parent_interface,
                parent_namespace,
            )
