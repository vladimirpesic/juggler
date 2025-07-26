"""
Solidity language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Solidity code.
It extracts contracts, functions, events, modifiers, and other code constructs from Solidity AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ContractEntry,
    EnumEntry,
    FunctionEntry,
    InterfaceEntry,
    StructEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_solidity(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_contract: ContractEntry | None = None,
    parent_function: FunctionEntry | None = None,
) -> None:
    """
    Recursively visit the Solidity AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_contract: The parent contract if current node is within a contract
        parent_function: The parent function if current node is within a function
    """
    # Handle contract declarations
    if root_node.type == "contract_declaration":
        contract_name_node = root_node.child_by_field_name("name")
        if contract_name_node:
            contract_entry = ContractEntry(
                name=contract_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract functions, events, modifiers, and state variables from contract body
            contract_body = root_node.child_by_field_name("body")
            contract_functions = ""
            contract_events = ""
            contract_modifiers = ""
            contract_state_vars = ""

            if contract_body:
                for child in contract_body.children:
                    if child.type == "function_definition":
                        function_name = child.child_by_field_name("name")
                        if function_name:
                            contract_functions += f"- {function_name.text.decode()}\n"  # type: ignore
                    elif child.type == "constructor_definition":
                        contract_functions += "- constructor\n"
                    elif child.type == "fallback_receive_definition":
                        contract_functions += "- fallback/receive\n"
                    elif child.type == "event_definition":
                        event_name = child.child_by_field_name("name")
                        if event_name:
                            contract_events += f"- {event_name.text.decode()}\n"  # type: ignore
                    elif child.type == "modifier_definition":
                        modifier_name = child.child_by_field_name("name")
                        if modifier_name:
                            contract_modifiers += f"- {modifier_name.text.decode()}\n"  # type: ignore
                    elif child.type == "state_variable_declaration":
                        for var_child in child.children:
                            if var_child.type == "variable_declaration":
                                var_name = var_child.child_by_field_name("name")
                                if var_name:
                                    contract_state_vars += (
                                        f"- {var_name.text.decode()}\n"  # type: ignore
                                    )
                                    break

            contract_entry.functions = (
                contract_functions.strip() if contract_functions != "" else None
            )
            contract_entry.events = (
                contract_events.strip() if contract_events != "" else None
            )
            contract_entry.modifiers = (
                contract_modifiers.strip() if contract_modifiers != "" else None
            )
            contract_entry.state_variables = (
                contract_state_vars.strip() if contract_state_vars != "" else None
            )
            parent_contract = contract_entry
            ckg_db._insert_entry(contract_entry)

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

            # Extract functions from interface body
            interface_body = root_node.child_by_field_name("body")
            interface_methods = ""

            if interface_body:
                for child in interface_body.children:
                    if child.type == "function_definition":
                        function_name = child.child_by_field_name("name")
                        if function_name:
                            interface_methods += f"- {function_name.text.decode()}\n"  # type: ignore

            interface_entry.methods = (
                interface_methods.strip() if interface_methods != "" else None
            )
            ckg_db._insert_entry(interface_entry)

    # Handle library declarations (similar to contracts)
    elif root_node.type == "library_declaration":
        library_name_node = root_node.child_by_field_name("name")
        if library_name_node:
            library_entry = ContractEntry(
                name=library_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract functions from library body
            library_body = root_node.child_by_field_name("body")
            library_functions = ""

            if library_body:
                for child in library_body.children:
                    if child.type == "function_definition":
                        function_name = child.child_by_field_name("name")
                        if function_name:
                            library_functions += f"- {function_name.text.decode()}\n"  # type: ignore

            library_entry.functions = (
                library_functions.strip() if library_functions != "" else None
            )
            parent_contract = library_entry
            ckg_db._insert_entry(library_entry)

    # Handle struct declarations
    elif root_node.type == "struct_declaration":
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
            struct_body = root_node.child_by_field_name("body")
            struct_fields = ""

            if struct_body:
                for child in struct_body.children:
                    if child.type == "struct_member":
                        member_name = child.child_by_field_name("name")
                        if member_name:
                            struct_fields += f"- {member_name.text.decode()}\n"  # type: ignore

            struct_entry.fields = struct_fields.strip() if struct_fields != "" else None
            ckg_db._insert_entry(struct_entry)

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

            # Extract enum values
            enum_body = root_node.child_by_field_name("body")
            enum_variants = ""

            if enum_body:
                for child in enum_body.children:
                    if child.type == "enum_value":
                        value_name = child.child_by_field_name("name")
                        if value_name:
                            enum_variants += f"- {value_name.text.decode()}\n"  # type: ignore

            enum_entry.variants = enum_variants.strip() if enum_variants != "" else None
            if parent_contract:
                enum_entry.parent_class = parent_contract.name
            ckg_db._insert_entry(enum_entry)

    # Handle function definitions
    elif root_node.type in [
        "function_definition",
        "constructor_definition",
        "modifier_definition",
    ]:
        function_name_node = root_node.child_by_field_name("name")
        function_name = (
            function_name_node.text.decode() if function_name_node else root_node.type  # type: ignore
        )

        function_entry = FunctionEntry(
            name=function_name,  # type: ignore
            file_path=file_path,
            body=root_node.text.decode(),  # type: ignore
            start_line=root_node.start_point[0] + 1,
            end_line=root_node.end_point[0] + 1,
        )

        if parent_contract:
            function_entry.parent_class = parent_contract.name
        elif parent_function:
            function_entry.parent_function = parent_function.name

        ckg_db._insert_entry(function_entry)
        parent_function = function_entry

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_solidity(
                ckg_db, child, file_path, parent_contract, parent_function
            )
