"""
Elixir language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Elixir code.
It extracts modules, functions, structs, protocols, and other code constructs from Elixir AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    FunctionEntry,
    InterfaceEntry,  # For protocols
    ModuleEntry,
    StructEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_elixir(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_module: ModuleEntry | None = None,
    parent_function: FunctionEntry | None = None,
) -> None:
    """
    Recursively visit the Elixir AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_module: The parent module if current node is within a module
        parent_function: The parent function if current node is within a function
    """
    # Handle module declarations
    if root_node.type == "call" and len(root_node.children) >= 2:
        # Check if this is a defmodule call
        function_name = root_node.children[0]
        if (
            function_name.type == "identifier"
            and function_name.text.decode() == "defmodule"  # type: ignore
        ):  # type: ignore
            # Get module name from arguments
            arguments = root_node.children[1]
            if arguments and len(arguments.children) > 0:
                module_name_node = arguments.children[0]
                if module_name_node:
                    module_entry = ModuleEntry(
                        name=module_name_node.text.decode(),  # type: ignore
                        file_path=file_path,
                        body=root_node.text.decode(),  # type: ignore
                        start_line=root_node.start_point[0] + 1,
                        end_line=root_node.end_point[0] + 1,
                    )
                    parent_module = module_entry
                    ckg_db._insert_entry(module_entry)

        # Check if this is a defstruct call
        elif (
            function_name.type == "identifier"
            and function_name.text.decode() == "defstruct"  # type: ignore
        ):  # type: ignore
            if parent_module:
                struct_entry = StructEntry(
                    name=parent_module.name,
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract fields from defstruct
                arguments = root_node.children[1]
                struct_fields = ""
                if arguments:
                    for child in arguments.children:
                        if child.type == "list":
                            for field in child.children:
                                if field.type == "atom":
                                    struct_fields += f"- {field.text.decode()}\n"  # type: ignore
                                elif field.type == "keyword_list":
                                    for kw in field.children:
                                        if kw.type == "keywords":
                                            for pair in kw.children:
                                                if pair.type == "pair":
                                                    key = pair.children[0]
                                                    if key.type == "atom":
                                                        struct_fields += (
                                                            f"- {key.text.decode()}\n"  # type: ignore
                                                        )

                struct_entry.fields = (
                    struct_fields.strip() if struct_fields != "" else None
                )
                ckg_db._insert_entry(struct_entry)

        # Check if this is a defprotocol call
        elif (
            function_name.type == "identifier"
            and function_name.text.decode() == "defprotocol"  # type: ignore
        ):  # type: ignore
            arguments = root_node.children[1]
            if arguments and len(arguments.children) > 0:
                protocol_name_node = arguments.children[0]
                if protocol_name_node:
                    protocol_entry = InterfaceEntry(
                        name=protocol_name_node.text.decode(),  # type: ignore
                        file_path=file_path,
                        body=root_node.text.decode(),  # type: ignore
                        start_line=root_node.start_point[0] + 1,
                        end_line=root_node.end_point[0] + 1,
                    )
                    ckg_db._insert_entry(protocol_entry)

        # Check for function definitions (def, defp, defmacro, etc.)
        elif function_name.type == "identifier" and function_name.text.decode() in [  # type: ignore
            "def",
            "defp",
            "defmacro",
            "defmacrop",
        ]:  # type: ignore
            arguments = root_node.children[1]
            if arguments and len(arguments.children) > 0:
                func_def = arguments.children[0]
                if func_def.type == "call":
                    func_name_node = func_def.children[0]
                    if func_name_node:
                        function_entry = FunctionEntry(
                            name=func_name_node.text.decode(),  # type: ignore
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
                elif func_def.type == "identifier":
                    # Simple function definition without parameters
                    function_entry = FunctionEntry(
                        name=func_def.text.decode(),  # type: ignore
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

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_elixir(
                ckg_db, child, file_path, parent_module, parent_function
            )
