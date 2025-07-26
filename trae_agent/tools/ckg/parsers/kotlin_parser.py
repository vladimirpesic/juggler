"""
Kotlin language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Kotlin code.
It extracts classes, functions, interfaces, enums, objects, and other code constructs from Kotlin AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    EnumEntry,
    FunctionEntry,
    InterfaceEntry,
    TypeAliasEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_kotlin(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_interface: InterfaceEntry | None = None,
) -> None:
    """
    Recursively visit the Kotlin AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
        parent_interface: The parent interface if current node is within an interface
    """
    try:
        # Handle class declarations (both regular and enum classes)
        if root_node.type == "class_declaration":
            # Find the type_identifier for the class name
            class_name_node = None
            is_interface = False
            is_enum = False

            for child in root_node.children:
                if child.type == "type_identifier":
                    class_name_node = child
                elif child.type == "interface":
                    is_interface = True
                elif child.type == "enum":
                    is_enum = True

            if class_name_node:
                class_name = class_name_node.text.decode()

                if is_interface:
                    # Handle interface
                    interface_entry = InterfaceEntry(
                        name=class_name,
                        file_path=file_path,
                        body=root_node.text.decode(),  # type: ignore
                        start_line=root_node.start_point[0] + 1,
                        end_line=root_node.end_point[0] + 1,
                    )
                    ckg_db._insert_entry(interface_entry)
                    parent_interface = interface_entry

                elif is_enum:
                    # Handle enum class
                    enum_entry = EnumEntry(
                        name=class_name,
                        file_path=file_path,
                        body=root_node.text.decode(),  # type: ignore
                        start_line=root_node.start_point[0] + 1,
                        end_line=root_node.end_point[0] + 1,
                    )

                    # Extract enum values from enum_class_body
                    enum_variants = ""
                    for child in root_node.children:
                        if child.type == "enum_class_body":
                            for enum_child in child.children:
                                if enum_child.type == "enum_entry":
                                    # Get the enum entry name
                                    for name_child in enum_child.children:
                                        if name_child.type == "simple_identifier":
                                            enum_variants += (
                                                f"- {name_child.text.decode()}\n"
                                            )
                                            break

                    enum_entry.variants = (
                        enum_variants.strip() if enum_variants != "" else None
                    )
                    ckg_db._insert_entry(enum_entry)

                else:
                    # Handle regular class
                    class_entry = ClassEntry(
                        name=class_name,
                        file_path=file_path,
                        body=root_node.text.decode(),  # type: ignore
                        start_line=root_node.start_point[0] + 1,
                        end_line=root_node.end_point[0] + 1,
                    )
                    ckg_db._insert_entry(class_entry)
                    parent_class = class_entry

        # Handle object declarations (singleton objects)
        elif root_node.type == "object_declaration":
            # Find the type_identifier for the object name
            object_name_node = None
            for child in root_node.children:
                if child.type == "type_identifier":
                    object_name_node = child
                    break

            if object_name_node:
                object_entry = ClassEntry(
                    name=object_name_node.text.decode(),  # type: ignore
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )
                ckg_db._insert_entry(object_entry)
                parent_class = object_entry

        # Handle type alias declarations
        elif root_node.type == "type_alias":
            # Find the type_identifier for the alias name
            alias_name_node = None
            target_type_node = None

            for child in root_node.children:
                if child.type == "type_identifier":
                    alias_name_node = child
                elif child.type in ["user_type", "function_type"]:
                    target_type_node = child

            if alias_name_node:
                target_type = (
                    target_type_node.text.decode() if target_type_node else None
                )  # type: ignore

                type_alias_entry = TypeAliasEntry(
                    name=alias_name_node.text.decode(),  # type: ignore
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                    target_type=target_type,
                )
                ckg_db._insert_entry(type_alias_entry)

        # Handle function declarations
        elif root_node.type == "function_declaration":
            # Find the simple_identifier for the function name
            function_name_node = None
            for child in root_node.children:
                if child.type == "simple_identifier":
                    function_name_node = child
                    break

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
                elif parent_interface:
                    function_entry.parent_class = parent_interface.name
                elif parent_function:
                    function_entry.parent_function = parent_function.name

                ckg_db._insert_entry(function_entry)
                parent_function = function_entry

    except Exception:
        # Silently continue if there's any parsing error
        pass

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_kotlin(
                ckg_db,
                child,
                file_path,
                parent_class,
                parent_function,
                parent_interface,
            )
