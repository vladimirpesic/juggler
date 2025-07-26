"""
Scala language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Scala code.
It extracts classes, objects, traits, functions, and other code constructs from Scala AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    FunctionEntry,
    TraitEntry,
    TypeAliasEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_scala(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_trait: TraitEntry | None = None,
) -> None:
    """
    Recursively visit the Scala AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
        parent_trait: The parent trait if current node is within a trait
    """
    # Handle class declarations
    if root_node.type == "class_definition":
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
            template_body = root_node.child_by_field_name("template_body")
            class_methods = ""
            class_fields = ""

            if template_body:
                for child in template_body.children:
                    if child.type == "function_definition":
                        method_name = child.child_by_field_name("name")
                        if method_name:
                            class_methods += f"- {method_name.text.decode()}\n"  # type: ignore
                    elif child.type == "val_definition":
                        pattern = child.child_by_field_name("pattern")
                        if pattern:
                            for pattern_child in pattern.children:
                                if pattern_child.type == "identifier":
                                    class_fields += f"- {pattern_child.text.decode()}\n"  # type: ignore
                                    break
                    elif child.type == "var_definition":
                        pattern = child.child_by_field_name("pattern")
                        if pattern:
                            for pattern_child in pattern.children:
                                if pattern_child.type == "identifier":
                                    class_fields += f"- {pattern_child.text.decode()}\n"  # type: ignore
                                    break

            class_entry.methods = class_methods.strip() if class_methods != "" else None
            class_entry.fields = class_fields.strip() if class_fields != "" else None
            parent_class = class_entry
            ckg_db._insert_entry(class_entry)

    # Handle object declarations
    elif root_node.type == "object_definition":
        object_name_node = root_node.child_by_field_name("name")
        if object_name_node:
            object_entry = ClassEntry(
                name=object_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract methods from object body
            template_body = root_node.child_by_field_name("template_body")
            object_methods = ""

            if template_body:
                for child in template_body.children:
                    if child.type == "function_definition":
                        method_name = child.child_by_field_name("name")
                        if method_name:
                            object_methods += f"- {method_name.text.decode()}\n"  # type: ignore

            object_entry.methods = (
                object_methods.strip() if object_methods != "" else None
            )
            parent_class = object_entry
            ckg_db._insert_entry(object_entry)

    # Handle trait declarations
    elif root_node.type == "trait_definition":
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
            template_body = root_node.child_by_field_name("template_body")
            trait_methods = ""

            if template_body:
                for child in template_body.children:
                    if child.type == "function_definition":
                        method_name = child.child_by_field_name("name")
                        if method_name:
                            trait_methods += f"- {method_name.text.decode()}\n"  # type: ignore
                    elif child.type == "function_declaration":
                        method_name = child.child_by_field_name("name")
                        if method_name:
                            trait_methods += f"- {method_name.text.decode()}\n"  # type: ignore

            trait_entry.methods = trait_methods.strip() if trait_methods != "" else None
            parent_trait = trait_entry
            ckg_db._insert_entry(trait_entry)

    # Handle type alias declarations
    elif root_node.type == "type_definition":
        type_name_node = root_node.child_by_field_name("name")
        if type_name_node:
            type_node = root_node.child_by_field_name("type")
            target_type = type_node.text.decode() if type_node else None  # type: ignore

            type_alias_entry = TypeAliasEntry(
                name=type_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
                target_type=target_type,
            )
            ckg_db._insert_entry(type_alias_entry)

    # Handle function definitions
    elif root_node.type == "function_definition":
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
            elif parent_function:
                function_entry.parent_function = parent_function.name

            ckg_db._insert_entry(function_entry)
            parent_function = function_entry

    # Handle function declarations (abstract methods in traits)
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

            if parent_trait:
                function_entry.parent_class = parent_trait.name
            elif parent_class:
                function_entry.parent_class = parent_class.name

            ckg_db._insert_entry(function_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_scala(
                ckg_db, child, file_path, parent_class, parent_function, parent_trait
            )
