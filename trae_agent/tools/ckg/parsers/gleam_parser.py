"""
Gleam language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Gleam code.
It extracts functions, types, modules, and other code constructs from Gleam AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    EnumEntry,
    FunctionEntry,
    ModuleEntry,
    TypeAliasEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_gleam(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_module: ModuleEntry | None = None,
    parent_function: FunctionEntry | None = None,
) -> None:
    """
    Recursively visit the Gleam AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_module: The parent module if current node is within a module
        parent_function: The parent function if current node is within a function
    """
    # Handle function declarations
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

            if parent_module:
                function_entry.parent_class = parent_module.name
            elif parent_function:
                function_entry.parent_function = parent_function.name

            ckg_db._insert_entry(function_entry)
            parent_function = function_entry

    # Handle function declarations (alternative node type)
    elif root_node.type == "function":
        function_name_node = root_node.child_by_field_name("name")
        if function_name_node:
            function_entry = FunctionEntry(
                name=function_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            if parent_module:
                function_entry.parent_class = parent_module.name
            elif parent_function:
                function_entry.parent_function = parent_function.name

            ckg_db._insert_entry(function_entry)
            parent_function = function_entry

    # Handle anonymous functions (lambdas)
    elif root_node.type == "anonymous_function":
        # Anonymous functions get a generic name based on location
        function_entry = FunctionEntry(
            name=f"anonymous_fn_line_{root_node.start_point[0] + 1}",
            file_path=file_path,
            body=root_node.text.decode(),  # type: ignore
            start_line=root_node.start_point[0] + 1,
            end_line=root_node.end_point[0] + 1,
        )

        if parent_function:
            function_entry.parent_function = parent_function.name

        ckg_db._insert_entry(function_entry)
        parent_function = function_entry

    # Handle type alias declarations
    elif root_node.type == "type_alias":
        type_name_node = root_node.child_by_field_name("name")
        if type_name_node:
            type_definition_node = root_node.child_by_field_name("definition")
            target_type = (
                type_definition_node.text.decode() if type_definition_node else None  # type: ignore
            )

            type_alias_entry = TypeAliasEntry(
                name=type_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
                target_type=target_type,
            )
            ckg_db._insert_entry(type_alias_entry)

    # Handle custom type declarations (similar to enums/ADTs)
    elif root_node.type == "custom_type":
        type_name_node = root_node.child_by_field_name("name")
        if type_name_node:
            # Treat custom types as enums since they are algebraic data types
            enum_entry = EnumEntry(
                name=type_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract constructors/variants
            constructors_node = root_node.child_by_field_name("constructors")
            constructors_text = ""
            if constructors_node:
                for child in constructors_node.children:
                    if child.type == "constructor":
                        constructor_name = child.child_by_field_name("name")
                        if constructor_name:
                            constructors_text += f"- {constructor_name.text.decode()}\n"  # type: ignore

            enum_entry.variants = (
                constructors_text.strip() if constructors_text != "" else None
            )
            ckg_db._insert_entry(enum_entry)

    # Handle type definitions (alternative syntax)
    elif root_node.type == "type_definition":
        type_name_node = root_node.child_by_field_name("name")
        if type_name_node:
            # Check if it's a variant type (enum-like) or alias
            body_node = root_node.child_by_field_name("body")
            if body_node and body_node.type == "variant_type":
                # This is an enum-like type
                enum_entry = EnumEntry(
                    name=type_name_node.text.decode(),  # type: ignore
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract variants
                variants_text = ""
                for child in body_node.children:
                    if child.type == "variant":
                        variant_name = child.child_by_field_name("name")
                        if variant_name:
                            variants_text += f"- {variant_name.text.decode()}\n"  # type: ignore

                enum_entry.variants = (
                    variants_text.strip() if variants_text != "" else None
                )
                ckg_db._insert_entry(enum_entry)
            else:
                # This is a type alias
                type_alias_entry = TypeAliasEntry(
                    name=type_name_node.text.decode(),  # type: ignore
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                    target_type=body_node.text.decode() if body_node else None,  # type: ignore
                )
                ckg_db._insert_entry(type_alias_entry)

    # Handle import statements (treat as module references)
    elif root_node.type == "import":
        module_name_node = root_node.child_by_field_name("module")
        if module_name_node:
            module_entry = ModuleEntry(
                name=module_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract imports/exports
            unqualified_imports = root_node.child_by_field_name("unqualified_imports")
            imports_text = ""
            if unqualified_imports:
                for child in unqualified_imports.children:
                    if child.type == "unqualified_import":
                        import_name = child.child_by_field_name("name")
                        if import_name:
                            imports_text += f"- {import_name.text.decode()}\n"  # type: ignore

            module_entry.imports = imports_text.strip() if imports_text != "" else None
            ckg_db._insert_entry(module_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_gleam(
                ckg_db, child, file_path, parent_module, parent_function
            )
