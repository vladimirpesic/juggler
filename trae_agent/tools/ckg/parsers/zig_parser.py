"""
Zig language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Zig code.
It extracts functions, structs, unions, enums, and other code constructs from Zig AST.
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


def recursive_visit_zig(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_struct: StructEntry | None = None,
    parent_function: FunctionEntry | None = None,
) -> None:
    """
    Recursively visit the Zig AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_struct: The parent struct if current node is within a struct
        parent_function: The parent function if current node is within a function
    """
    try:
        # Handle Decl nodes which contain various declarations
        if root_node.type == "Decl":
            # Look for FnProto (function declarations)
            fn_proto = None
            var_decl = None

            for child in root_node.children:
                if child.type == "FnProto":
                    fn_proto = child
                elif child.type == "VarDecl":
                    var_decl = child

            # Handle function declarations
            if fn_proto:
                function_name_node = None
                # Find the IDENTIFIER node which contains the function name
                for fn_child in fn_proto.children:
                    if fn_child.type == "IDENTIFIER":
                        function_name_node = fn_child
                        break

                if function_name_node:
                    function_entry = FunctionEntry(
                        name=function_name_node.text.decode(),  # type: ignore
                        file_path=file_path,
                        body=root_node.text.decode(),  # type: ignore
                        start_line=root_node.start_point[0] + 1,
                        end_line=root_node.end_point[0] + 1,
                    )

                    if parent_struct:
                        function_entry.parent_class = parent_struct.name
                    elif parent_function:
                        function_entry.parent_function = parent_function.name

                    ckg_db._insert_entry(function_entry)

            # Handle variable declarations that might be types (struct, enum, union)
            elif var_decl:
                var_name_node = None
                container_decl = None

                # Find the IDENTIFIER for the name and ContainerDecl
                for var_child in var_decl.children:
                    if var_child.type == "IDENTIFIER":
                        var_name_node = var_child
                    elif var_child.type == "ErrorUnionExpr":
                        # Look for ContainerDecl inside ErrorUnionExpr -> SuffixExpr
                        for error_child in var_child.children:
                            if error_child.type == "SuffixExpr":
                                for suffix_child in error_child.children:
                                    if suffix_child.type == "ContainerDecl":
                                        container_decl = suffix_child
                                        break

                if var_name_node and container_decl:
                    var_name = var_name_node.text.decode()

                    # Determine container type from ContainerDeclType
                    container_type = _determine_zig_container_type(container_decl)

                    if container_type == "struct":
                        struct_entry = StructEntry(
                            name=var_name,
                            file_path=file_path,
                            body=root_node.text.decode(),  # type: ignore
                            start_line=root_node.start_point[0] + 1,
                            end_line=root_node.end_point[0] + 1,
                        )

                        # Extract fields from ContainerField nodes
                        fields = _extract_zig_struct_fields(container_decl)
                        struct_entry.fields = fields
                        ckg_db._insert_entry(struct_entry)

                    elif container_type == "enum":
                        enum_entry = EnumEntry(
                            name=var_name,
                            file_path=file_path,
                            body=root_node.text.decode(),  # type: ignore
                            start_line=root_node.start_point[0] + 1,
                            end_line=root_node.end_point[0] + 1,
                        )

                        # Extract enum values
                        enum_variants = _extract_zig_enum_variants(container_decl)
                        enum_entry.variants = enum_variants
                        ckg_db._insert_entry(enum_entry)

                    elif container_type == "union":
                        union_entry = UnionEntry(
                            name=var_name,
                            file_path=file_path,
                            body=root_node.text.decode(),  # type: ignore
                            start_line=root_node.start_point[0] + 1,
                            end_line=root_node.end_point[0] + 1,
                        )

                        # Extract union variants
                        union_variants = _extract_zig_union_variants(container_decl)
                        union_entry.variants = union_variants
                        ckg_db._insert_entry(union_entry)

    except Exception:
        # Silently continue if there's any parsing error
        pass

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_zig(
                ckg_db, child, file_path, parent_struct, parent_function
            )


def _determine_zig_container_type(container_node: Node) -> str:
    """Determine if a Zig container is a struct, enum, or union."""
    # Look for ContainerDeclType child which contains the keyword
    for child in container_node.children:
        if child.type == "ContainerDeclType":
            for type_child in child.children:
                if type_child.type in ["struct", "enum", "union"]:
                    return type_child.type

    # Fallback to text analysis
    container_text = container_node.text.decode().lower()
    if "enum" in container_text[:50]:
        return "enum"
    elif "union" in container_text[:50]:
        return "union"
    else:
        return "struct"


def _extract_zig_struct_fields(container_node: Node) -> str | None:
    """Extract field names from a Zig struct container."""
    fields = []

    def visit_container_fields(node: Node) -> None:
        if node.type == "ContainerField":
            # Look for IDENTIFIER in this field
            for field_child in node.children:
                if field_child.type == "IDENTIFIER":
                    field_name = field_child.text.decode()
                    if field_name not in fields:  # Avoid duplicates
                        fields.append(field_name)
                    break

        for child in node.children:
            visit_container_fields(child)

    visit_container_fields(container_node)

    if fields:
        return "\n".join(f"- {field}" for field in fields[:20])  # Limit to 20
    return None


def _extract_zig_enum_variants(container_node: Node) -> str | None:
    """Extract enum variants from a Zig enum container."""
    variants = []

    def visit_container_fields(node: Node) -> None:
        if node.type == "ContainerField":
            # For enums, extract all identifiers in the field
            for field_child in node.children:
                if field_child.type == "IDENTIFIER":
                    variant_name = field_child.text.decode()
                    if variant_name not in variants:  # Avoid duplicates
                        variants.append(variant_name)
                    break
                elif field_child.type == "ErrorUnionExpr":
                    # For simple enum values, they might be in ErrorUnionExpr -> SuffixExpr
                    def extract_from_expr(expr_node: Node) -> None:
                        if expr_node.type == "IDENTIFIER":
                            variant_name = expr_node.text.decode()
                            if variant_name not in variants:
                                variants.append(variant_name)
                        for expr_child in expr_node.children:
                            extract_from_expr(expr_child)

                    extract_from_expr(field_child)

        for child in node.children:
            visit_container_fields(child)

    visit_container_fields(container_node)

    if variants:
        return "\n".join(f"- {variant}" for variant in variants[:15])  # Limit to 15
    return None


def _extract_zig_union_variants(container_node: Node) -> str | None:
    """Extract union variants from a Zig union container."""
    return _extract_zig_struct_fields(
        container_node
    )  # Use struct field logic for union fields
