"""
C language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for C code.
It extracts functions, structs, enums, unions, and other code constructs from C AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    EnumEntry,
    FunctionEntry,
    StructEntry,
    UnionEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_c(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_struct: StructEntry | None = None,
    parent_function: FunctionEntry | None = None,
) -> None:
    """
    Recursively visit the C AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_struct: The parent struct if current node is within a struct
        parent_function: The parent function if current node is within a function
    """
    # Handle function definitions
    if root_node.type == "function_definition":
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

                ckg_db._insert_entry(function_entry)
                parent_function = function_entry

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

            if struct_body_node:
                for child in struct_body_node.children:
                    if child.type == "field_declaration":
                        struct_fields += f"- {child.text.decode()}\n"  # type: ignore

            struct_entry.fields = struct_fields.strip() if struct_fields != "" else None
            parent_struct = struct_entry
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
            ckg_db._insert_entry(enum_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_c(ckg_db, child, file_path, parent_struct, parent_function)
