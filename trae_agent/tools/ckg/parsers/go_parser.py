"""
Go language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Go code.
It extracts functions, structs, interfaces, methods, packages, and other code constructs from Go AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    FunctionEntry,
    InterfaceEntry,
    ModuleEntry,
    StructEntry,
    TypeAliasEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_go(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_struct: StructEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_interface: InterfaceEntry | None = None,
    parent_package: ModuleEntry | None = None,
) -> None:
    """
    Recursively visit the Go AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_struct: The parent struct if current node is within a struct
        parent_function: The parent function if current node is within a function
        parent_interface: The parent interface if current node is within an interface
        parent_package: The parent package if current node is within a package
    """
    # Handle function declarations
    if root_node.type == "function_declaration":
        function_name_node = root_node.child_by_field_name("name")
        if function_name_node:
            function_entry = FunctionEntry(
                name=function_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            if parent_function:
                function_entry.parent_function = parent_function.name

            ckg_db._insert_entry(function_entry)
            parent_function = function_entry

    # Handle method declarations
    elif root_node.type == "method_declaration":
        method_name_node = root_node.child_by_field_name("name")
        if method_name_node:
            # Get receiver type
            receiver_node = root_node.child_by_field_name("receiver")
            receiver_type = ""
            if receiver_node:
                # Find the type in parameter_list
                for child in receiver_node.children:
                    if child.type == "parameter_declaration":
                        type_node = child.children[-1] if child.children else None
                        if type_node:
                            receiver_type = type_node.text.decode()  # type: ignore
                            break

            method_entry = FunctionEntry(
                name=method_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            if receiver_type:
                # Clean up receiver type (remove * and package qualifiers)
                clean_type = receiver_type.replace("*", "").split(".")[-1]
                method_entry.parent_class = clean_type

            ckg_db._insert_entry(method_entry)
            parent_function = method_entry

    # Handle struct type specifications
    elif root_node.type == "type_spec":
        type_name_node = root_node.child_by_field_name("name")
        type_node = root_node.child_by_field_name("type")

        if type_name_node and type_node:
            if type_node.type == "struct_type":
                struct_entry = StructEntry(
                    name=type_name_node.text.decode(),  # type: ignore
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract fields from struct body
                struct_body_node = type_node.child_by_field_name("body")
                struct_fields = ""

                if struct_body_node:
                    for child in struct_body_node.children:
                        if child.type == "field_declaration":
                            struct_fields += f"- {child.text.decode()}\n"  # type: ignore

                struct_entry.fields = (
                    struct_fields.strip() if struct_fields != "" else None
                )
                parent_struct = struct_entry
                ckg_db._insert_entry(struct_entry)

            elif type_node.type == "interface_type":
                interface_entry = InterfaceEntry(
                    name=type_name_node.text.decode(),  # type: ignore
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract methods from interface body
                interface_body_node = type_node.child_by_field_name("body")
                interface_methods = ""

                if interface_body_node:
                    for child in interface_body_node.children:
                        if child.type == "method_spec":
                            interface_methods += f"- {child.text.decode()}\n"  # type: ignore
                        elif child.type == "type_elem":
                            # Embedded interface
                            interface_methods += f"- {child.text.decode()}\n"  # type: ignore

                interface_entry.methods = (
                    interface_methods.strip() if interface_methods != "" else None
                )
                parent_interface = interface_entry
                ckg_db._insert_entry(interface_entry)

            else:
                # Type alias
                type_alias_entry = TypeAliasEntry(
                    name=type_name_node.text.decode(),  # type: ignore
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                type_alias_entry.target_type = type_node.text.decode()  # type: ignore
                ckg_db._insert_entry(type_alias_entry)

    # Handle type aliases (different from type_spec)
    elif root_node.type == "type_alias":
        alias_name_node = root_node.child_by_field_name("name")
        alias_type_node = root_node.child_by_field_name("type")

        if alias_name_node and alias_type_node:
            type_alias_entry = TypeAliasEntry(
                name=alias_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            type_alias_entry.target_type = alias_type_node.text.decode()  # type: ignore
            ckg_db._insert_entry(type_alias_entry)

    # Handle package clause (extract package name)
    elif root_node.type == "package_clause":
        package_name_node = root_node.child_by_field_name("name")
        if package_name_node:
            package_entry = ModuleEntry(
                name=package_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            parent_package = package_entry
            ckg_db._insert_entry(package_entry)

    # Handle import declarations to extract modules from imported packages
    elif root_node.type == "import_declaration":
        # Check for import_spec children to extract module names
        for child in root_node.children:
            if child.type == "import_spec":
                # Extract module path from interpreted_string_literal
                for import_child in child.children:
                    if import_child.type == "interpreted_string_literal":
                        # Get the content of the string
                        for string_child in import_child.children:
                            if (
                                string_child.type
                                == "interpreted_string_literal_content"
                            ):
                                import_path = string_child.text.decode()  # type: ignore
                                # Create module entry for the imported package
                                module_entry = ModuleEntry(
                                    name=import_path,
                                    file_path=file_path,
                                    body=child.text.decode(),  # type: ignore
                                    start_line=child.start_point[0] + 1,
                                    end_line=child.end_point[0] + 1,
                                )
                                ckg_db._insert_entry(module_entry)
            elif child.type == "import_spec_list":
                # Handle grouped imports
                for spec_child in child.children:
                    if spec_child.type == "import_spec":
                        for import_child in spec_child.children:
                            if import_child.type == "interpreted_string_literal":
                                for string_child in import_child.children:
                                    if (
                                        string_child.type
                                        == "interpreted_string_literal_content"
                                    ):
                                        import_path = string_child.text.decode()  # type: ignore
                                        module_entry = ModuleEntry(
                                            name=import_path,
                                            file_path=file_path,
                                            body=spec_child.text.decode(),  # type: ignore
                                            start_line=spec_child.start_point[0] + 1,
                                            end_line=spec_child.end_point[0] + 1,
                                        )
                                        ckg_db._insert_entry(module_entry)

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_go(
                ckg_db,
                child,
                file_path,
                parent_struct,
                parent_function,
                parent_interface,
                parent_package,
            )
