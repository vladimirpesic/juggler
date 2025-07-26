"""
C++ language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for C++ code.
It extracts functions, classes, structs, namespaces, and other code constructs from C++ AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    EnumEntry,
    FunctionEntry,
    NamespaceEntry,
    StructEntry,
    UnionEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_cpp(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_namespace: NamespaceEntry | None = None,
) -> None:
    """
    Recursively visit the C++ AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
        parent_namespace: The parent namespace if current node is within a namespace
    """
    # Handle class specifiers
    if root_node.type == "class_specifier":
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
                    if child.type == "function_definition":
                        method_builder = ""
                        for method_property in child.children:
                            if method_property.type == "compound_statement":
                                break
                            method_builder += f"{method_property.text.decode()} "  # type: ignore
                        method_builder = method_builder.strip()
                        class_methods += f"- {method_builder}\n"
                    elif child.type == "field_declaration":
                        child_is_property = True
                        for child_property in child.children:
                            if child_property.type == "function_declarator":
                                child_is_property = False
                                break
                        if child_is_property:
                            class_fields += f"- {child.text.decode()}\n"  # type: ignore
                        else:
                            class_methods += f"- {child.text.decode()}\n"  # type: ignore

            class_entry.methods = class_methods.strip() if class_methods != "" else None
            class_entry.fields = class_fields.strip() if class_fields != "" else None
            parent_class = class_entry
            ckg_db._insert_entry(class_entry)

    # Handle struct specifiers
    elif root_node.type == "struct_specifier":
        struct_name_node = root_node.child_by_field_name("name")
        if struct_name_node:
            struct_entry = StructEntry(
                name=struct_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            struct_body_node = root_node.child_by_field_name("body")
            struct_fields = ""
            struct_methods = ""

            if struct_body_node:
                for child in struct_body_node.children:
                    if child.type == "field_declaration":
                        struct_fields += f"- {child.text.decode()}\n"  # type: ignore
                    elif child.type == "function_definition":
                        method_builder = ""
                        for method_property in child.children:
                            if method_property.type == "compound_statement":
                                break
                            method_builder += f"{method_property.text.decode()} "  # type: ignore
                        method_builder = method_builder.strip()
                        struct_methods += f"- {method_builder}\n"

            struct_entry.fields = struct_fields.strip() if struct_fields != "" else None
            struct_entry.methods = (
                struct_methods.strip() if struct_methods != "" else None
            )
            ckg_db._insert_entry(struct_entry)

    # Handle union specifiers
    elif root_node.type == "union_specifier":
        union_name_node = root_node.child_by_field_name("name")
        if union_name_node:
            union_entry = UnionEntry(
                name=union_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            union_body_node = root_node.child_by_field_name("body")
            union_variants = ""

            if union_body_node:
                for child in union_body_node.children:
                    if child.type == "field_declaration":
                        union_variants += f"- {child.text.decode()}\n"  # type: ignore

            union_entry.variants = (
                union_variants.strip() if union_variants != "" else None
            )
            ckg_db._insert_entry(union_entry)

    # Handle enum specifiers
    elif root_node.type == "enum_specifier":
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
                    if child.type == "enumerator":
                        enum_variants += f"- {child.text.decode()}\n"  # type: ignore

            enum_entry.variants = enum_variants.strip() if enum_variants != "" else None
            if parent_class:
                enum_entry.parent_class = parent_class.name
            ckg_db._insert_entry(enum_entry)

    # Handle namespace definitions
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

            namespace_body_node = root_node.child_by_field_name("body")
            namespace_members = ""

            if namespace_body_node:
                for child in namespace_body_node.children:
                    if child.type in [
                        "class_specifier",
                        "struct_specifier",
                        "function_definition",
                        "enum_specifier",
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

    # Handle function definitions
    elif root_node.type == "function_definition":
        function_declarator_node = root_node.child_by_field_name("declarator")
        if function_declarator_node:
            function_name_node = function_declarator_node.child_by_field_name(
                "declarator"
            )
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

                ckg_db._insert_entry(function_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_cpp(
                ckg_db,
                child,
                file_path,
                parent_class,
                parent_function,
                parent_namespace,
            )
