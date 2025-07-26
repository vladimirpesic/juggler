"""
Dart language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Dart code.
It extracts classes, functions, enums, mixins, extensions, and other code constructs from Dart AST.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    EnumEntry,
    ExtensionEntry,
    FunctionEntry,
    InterfaceEntry,
    ModuleEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def recursive_visit_dart(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_function: FunctionEntry | None = None,
    parent_module: ModuleEntry | None = None,
) -> None:
    """
    Recursively visit the Dart AST and insert entries into the database.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_function: The parent function if current node is within a function
        parent_module: The parent module if current node is within a module
    """
    # Handle class declarations
    if root_node.type == "class_definition":
        class_name_node = root_node.child_by_field_name("name")
        if class_name_node:
            # Check if this is an abstract class (interface in Dart)
            has_abstract = False
            for child in root_node.children:
                if child.type == "abstract":
                    has_abstract = True
                    break

            if has_abstract:
                # Treat abstract classes as interfaces in Dart
                interface_entry = InterfaceEntry(
                    name=class_name_node.text.decode(),  # type: ignore
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract methods from class body
                class_body = root_node.child_by_field_name("body")
                interface_methods = ""

                if class_body:
                    for child in class_body.children:
                        if child.type in [
                            "method_signature",
                            "function_signature",
                            "getter_signature",
                        ]:
                            method_name = child.child_by_field_name("name")
                            if method_name:
                                interface_methods += f"- {method_name.text.decode()}\n"  # type: ignore

                interface_entry.methods = (
                    interface_methods.strip() if interface_methods != "" else None
                )
                ckg_db._insert_entry(interface_entry)
            else:
                # Regular class
                class_entry = ClassEntry(
                    name=class_name_node.text.decode(),  # type: ignore
                    file_path=file_path,
                    body=root_node.text.decode(),  # type: ignore
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract methods and fields from class body
                class_body = root_node.child_by_field_name("body")
                class_methods = ""
                class_fields = ""

                if class_body:
                    for child in class_body.children:
                        if child.type in [
                            "method_signature",
                            "function_signature",
                            "getter_signature",
                            "constructor_signature",
                            "constant_constructor_signature",
                            "factory_constructor_signature",
                        ]:
                            method_name = child.child_by_field_name("name")
                            if method_name:
                                class_methods += f"- {method_name.text.decode()}\n"  # type: ignore
                        elif child.type in [
                            "static_final_declaration",
                            "initialized_variable_definition",
                        ]:
                            # Extract field names
                            for grandchild in child.children:
                                if grandchild.type == "identifier":
                                    class_fields += f"- {grandchild.text.decode()}\n"  # type: ignore
                                    break

                class_entry.methods = (
                    class_methods.strip() if class_methods != "" else None
                )
                class_entry.fields = (
                    class_fields.strip() if class_fields != "" else None
                )
                parent_class = class_entry
                ckg_db._insert_entry(class_entry)

    # Handle mixin declarations
    elif root_node.type == "mixin_declaration":
        mixin_name_node = root_node.child_by_field_name("name")
        if mixin_name_node:
            mixin_entry = ClassEntry(
                name=mixin_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract methods from mixin body
            mixin_body = root_node.child_by_field_name("body")
            mixin_methods = ""

            if mixin_body:
                for child in mixin_body.children:
                    if child.type in [
                        "method_signature",
                        "function_signature",
                        "getter_signature",
                    ]:
                        method_name = child.child_by_field_name("name")
                        if method_name:
                            mixin_methods += f"- {method_name.text.decode()}\n"  # type: ignore

            mixin_entry.methods = mixin_methods.strip() if mixin_methods != "" else None
            parent_class = mixin_entry
            ckg_db._insert_entry(mixin_entry)

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
                    if child.type == "enum_constant":
                        variant_name = child.child_by_field_name("name")
                        if variant_name:
                            enum_variants += f"- {variant_name.text.decode()}\n"  # type: ignore

            enum_entry.variants = enum_variants.strip() if enum_variants != "" else None
            if parent_class:
                enum_entry.parent_class = parent_class.name
            ckg_db._insert_entry(enum_entry)

    # Handle extension declarations
    elif root_node.type == "extension_declaration":
        extension_name_node = root_node.child_by_field_name("name")
        if extension_name_node:
            # Get the extended type by looking for 'on' keyword and following type
            extended_type = None
            for child in root_node.children:
                if child.type == "on":
                    # Find the next sibling that's a type
                    for sibling in root_node.children:
                        if sibling.start_point > child.end_point and sibling.type in [
                            "type_identifier",
                            "identifier",
                        ]:
                            extended_type = sibling.text.decode()  # type: ignore
                            break
                    break

            extension_entry = ExtensionEntry(
                name=extension_name_node.text.decode(),  # type: ignore
                file_path=file_path,
                body=root_node.text.decode(),  # type: ignore
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
                extended_type=extended_type,
            )

            # Extract methods from extension body
            extension_body = root_node.child_by_field_name("body")
            extension_methods = ""

            if extension_body:
                for child in extension_body.children:
                    if child.type in [
                        "method_signature",
                        "function_signature",
                        "getter_signature",
                    ]:
                        method_name = child.child_by_field_name("name")
                        if method_name:
                            extension_methods += f"- {method_name.text.decode()}\n"  # type: ignore

            extension_entry.methods = (
                extension_methods.strip() if extension_methods != "" else None
            )
            ckg_db._insert_entry(extension_entry)

    # Handle function/method signatures (the actual function definitions in Dart AST)
    elif root_node.type in [
        "function_signature",
        "method_signature",
        "getter_signature",
        "operator_signature",
        "constructor_signature",
        "constant_constructor_signature",
        "factory_constructor_signature",
    ]:
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
            elif parent_function:
                function_entry.parent_function = parent_function.name

            ckg_db._insert_entry(function_entry)
            parent_function = function_entry

    # Handle local function declarations (nested functions)
    elif root_node.type == "local_function_declaration":
        # Extract function name from the signature
        function_signature = None
        for child in root_node.children:
            if child.type == "function_signature":
                function_signature = child
                break

        if function_signature:
            function_name_node = function_signature.child_by_field_name("name")
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
                elif parent_function:
                    function_entry.parent_function = parent_function.name

                ckg_db._insert_entry(function_entry)
                parent_function = function_entry

    # Handle module-level imports as modules
    elif root_node.type == "import_or_export":
        # Extract library name from import
        for child in root_node.children:
            if child.type == "library_import":
                for grandchild in child.children:
                    if grandchild.type == "import_specification":
                        for ggchild in grandchild.children:
                            if ggchild.type == "configurable_uri":
                                for gggchild in ggchild.children:
                                    if gggchild.type == "uri":
                                        for ggggchild in gggchild.children:
                                            if ggggchild.type == "string_literal":
                                                import_text = (
                                                    ggggchild.text.decode().strip("'\"")
                                                )  # type: ignore
                                                if (
                                                    import_text
                                                    and not import_text.startswith(".")
                                                ):
                                                    module_entry = ModuleEntry(
                                                        name=import_text,
                                                        file_path=file_path,
                                                        body=root_node.text.decode(),  # type: ignore
                                                        start_line=root_node.start_point[
                                                            0
                                                        ]
                                                        + 1,
                                                        end_line=root_node.end_point[0]
                                                        + 1,
                                                    )
                                                    ckg_db._insert_entry(module_entry)
                                                break

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_dart(
                ckg_db, child, file_path, parent_class, parent_function, parent_module
            )
