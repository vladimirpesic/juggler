"""
Rust language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Rust code.
It extracts functions, structs, enums, traits, implementations, and other code constructs from Rust AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    EnumEntry,
    FunctionEntry,
    ModuleEntry,
    StructEntry,
    TraitEntry,
    TypeAliasEntry,
    UnionEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_rust(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_struct: StructEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_trait: TraitEntry | None = None,
    parent_impl: ClassEntry | None = None,
    parent_module: ModuleEntry | None = None,
) -> None:
    """
    Recursively visit the Rust AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_struct: The parent struct if current node is within a struct
        parent_function: The parent function if current node is within a function
        parent_trait: The parent trait if current node is within a trait
        parent_impl: The parent impl block if current node is within an impl
        parent_module: The parent module if current node is within a module
    """
    # Handle function items
    if root_node.type == "function_item":
        function_name_node = root_node.child_by_field_name("name")
        if function_name_node:
            function_entry = FunctionEntry(
                name=function_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            if parent_impl:
                function_entry.parent_class = parent_impl.name
            elif parent_trait:
                function_entry.parent_class = parent_trait.name
            elif parent_struct:
                function_entry.parent_class = parent_struct.name
            elif parent_function:
                function_entry.parent_function = parent_function.name

            ckg_db._insert_entry(function_entry)
            parent_function = function_entry

    # Handle struct items
    elif root_node.type == "struct_item":
        struct_name_node = root_node.child_by_field_name("name")
        if struct_name_node:
            struct_entry = StructEntry(
                name=struct_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract fields from struct body
            struct_body_node = root_node.child_by_field_name("body")
            struct_fields = ""

            if struct_body_node:
                for child in struct_body_node.children:
                    if child.type == "field_declaration":
                        struct_fields += f"- {child.text.decode()}\n"  # type: ignore

            struct_entry.fields = struct_fields.strip() if struct_fields != "" else None
            parent_struct = struct_entry
            ckg_db._insert_entry(struct_entry)

    # Handle enum items
    elif root_node.type == "enum_item":
        enum_name_node = root_node.child_by_field_name("name")
        if enum_name_node:
            enum_entry = EnumEntry(
                name=enum_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract variants from enum body
            enum_body_node = root_node.child_by_field_name("body")
            enum_variants = ""

            if enum_body_node:
                for child in enum_body_node.children:
                    if child.type == "enum_variant":
                        variant_name_node = child.child_by_field_name("name")
                        if variant_name_node:
                            enum_variants += f"- {variant_name_node.text.decode()}\n"  # type: ignore

            enum_entry.variants = enum_variants.strip() if enum_variants != "" else None
            ckg_db._insert_entry(enum_entry)

    # Handle trait items
    elif root_node.type == "trait_item":
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
            trait_associated_types = ""

            if trait_body_node:
                for child in trait_body_node.children:
                    if child.type == "function_signature_item":
                        method_name_node = child.child_by_field_name("name")
                        if method_name_node:
                            trait_methods += f"- {child.text.decode()}\n"  # type: ignore
                    elif child.type == "associated_type":
                        type_name_node = child.child_by_field_name("name")
                        if type_name_node:
                            trait_associated_types += (
                                f"- {type_name_node.text.decode()}\n"  # type: ignore
                            )

            trait_entry.methods = trait_methods.strip() if trait_methods != "" else None
            trait_entry.associated_types = (
                trait_associated_types.strip() if trait_associated_types != "" else None
            )
            parent_trait = trait_entry
            ckg_db._insert_entry(trait_entry)

    # Handle impl items (treat as class-like for storing methods)
    elif root_node.type == "impl_item":
        impl_type_node = root_node.child_by_field_name("type")
        if impl_type_node:
            impl_name = impl_type_node.text.decode()  # type: ignore

            # Check if it's a trait implementation
            trait_node = root_node.child_by_field_name("trait")
            if trait_node:
                impl_name = f"{trait_node.text.decode()} for {impl_name}"  # type: ignore

            impl_entry = ClassEntry(
                name=impl_name,
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract methods from impl body
            impl_body_node = root_node.child_by_field_name("body")
            impl_methods = ""

            if impl_body_node:
                for child in impl_body_node.children:
                    if child.type == "function_item":
                        method_name_node = child.child_by_field_name("name")
                        if method_name_node:
                            impl_methods += f"- {method_name_node.text.decode()}\n"  # type: ignore

            impl_entry.methods = impl_methods.strip() if impl_methods != "" else None
            parent_impl = impl_entry
            ckg_db._insert_entry(impl_entry)

    # Handle union items
    elif root_node.type == "union_item":
        union_name_node = root_node.child_by_field_name("name")
        if union_name_node:
            union_entry = UnionEntry(
                name=union_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract fields from union body
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

    # Handle type items (type aliases)
    elif root_node.type == "type_item":
        type_name_node = root_node.child_by_field_name("name")
        if type_name_node:
            type_alias_entry = TypeAliasEntry(
                name=type_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Get the target type
            type_node = root_node.child_by_field_name("type")
            if type_node:
                type_alias_entry.target_type = type_node.text.decode()  # type: ignore

            ckg_db._insert_entry(type_alias_entry)

    # Handle mod items
    elif root_node.type == "mod_item":
        mod_name_node = root_node.child_by_field_name("name")
        if mod_name_node:
            module_entry = ModuleEntry(
                name=mod_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract exports/imports from module body
            mod_body_node = root_node.child_by_field_name("body")
            mod_exports = ""

            if mod_body_node:
                for child in mod_body_node.children:
                    if child.type in [
                        "function_item",
                        "struct_item",
                        "enum_item",
                        "trait_item",
                    ]:
                        name_node = child.child_by_field_name("name")
                        if name_node:
                            mod_exports += (
                                f"- {child.type}: {name_node.text.decode()}\n"  # type: ignore
                            )

            module_entry.exports = mod_exports.strip() if mod_exports != "" else None
            parent_module = module_entry
            ckg_db._insert_entry(module_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_rust(
                ckg_db,
                child,
                file_path,
                parent_struct,
                parent_function,
                parent_trait,
                parent_impl,
                parent_module,
            )
