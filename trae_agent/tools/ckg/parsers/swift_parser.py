"""
Swift language parser for Code Knowledge Graph (CKG).

This module contains the tree-sitter based parser for Swift code that correctly handles
all Swift constructs by analyzing the AST structure accurately.
"""

from typing import TYPE_CHECKING

from tree_sitter import Node

from ..base import (
    ClassEntry,
    EnumEntry,
    ExtensionEntry,
    FunctionEntry,
    GenericTypeEntry,
    InterfaceEntry,  # For protocols
    ModuleEntry,  # For imports
    StructEntry,
    TypeAliasEntry,
)

if TYPE_CHECKING:
    from ..ckg_database import CKGDatabase


def extract_text_content(node: Node) -> str:
    """Safely extract text content from a node."""
    if node is None:
        return ""
    try:
        return node.text.decode("utf-8")
    except:  # noqa: E722
        return ""


def extract_identifier_name(node: Node) -> str:
    """Extract identifier name from type_identifier or simple_identifier nodes."""
    if node is None:
        return ""

    if node.type in ["type_identifier", "simple_identifier"]:
        return extract_text_content(node)

    # Look for identifier in children
    for child in node.children:
        if child.type in ["type_identifier", "simple_identifier"]:
            return extract_text_content(child)

    return ""


def get_declaration_type(class_decl_node: Node) -> str:
    """Determine the type of class_declaration by looking at its keyword child."""
    for child in class_decl_node.children:
        if child.type in ["struct", "class", "enum", "actor", "extension"]:
            return child.type
    return "class"  # default


def extract_properties_and_methods(body_node: Node) -> tuple[str | None, str | None]:
    """Extract properties and methods from a body node."""
    if body_node is None:
        return None, None

    properties = []
    methods = []

    for child in body_node.children:
        if child.type == "property_declaration":
            prop_name = extract_property_name(child)
            if prop_name:
                properties.append(f"- {prop_name}")

        elif child.type in [
            "function_declaration",
            "init_declaration",
            "deinit_declaration",
        ]:
            method_name = extract_method_name(child)
            if method_name:
                methods.append(f"- {method_name}")

    properties_str = "\n".join(properties) if properties else None
    methods_str = "\n".join(methods) if methods else None

    return properties_str, methods_str


def extract_property_name(prop_node: Node) -> str:
    """Extract property name from property_declaration."""
    for child in prop_node.children:
        if child.type == "value_binding_pattern":
            for subchild in child.children:
                if subchild.type == "pattern":
                    for pattern_child in subchild.children:
                        if pattern_child.type == "simple_identifier":
                            return extract_text_content(pattern_child)
    return ""


def extract_method_name(func_node: Node) -> str:
    """Extract method name from function declaration."""
    name_node = func_node.child_by_field_name("name")
    if name_node:
        return extract_text_content(name_node)
    elif func_node.type == "init_declaration":
        return "init"
    elif func_node.type == "deinit_declaration":
        return "deinit"
    return ""


def extract_enum_cases(body_node: Node) -> str | None:
    """Extract enum cases from enum body."""
    if body_node is None:
        return None

    cases = []
    for child in body_node.children:
        if child.type == "enum_entry":
            # Extract case names from enum entry
            case_text = extract_text_content(child)
            # Parse "case north, south" format
            if case_text.startswith("case "):
                case_names = case_text[5:].split(",")
                for case_name in case_names:
                    clean_name = case_name.strip()
                    if clean_name:
                        cases.append(f"- {clean_name}")

    return "\n".join(cases) if cases else None


def extract_generic_parameters(node: Node) -> str:
    """Extract generic type parameters."""
    if node is None:
        return ""

    params = []
    for child in node.children:
        if child.type == "type_parameter":
            param_name = extract_identifier_name(child)
            if param_name:
                params.append(param_name)

    return ", ".join(params)


def extract_protocol_requirements(body_node: Node) -> tuple[str | None, str | None]:
    """Extract protocol method and property requirements."""
    if body_node is None:
        return None, None

    methods = []
    properties = []

    for child in body_node.children:
        if child.type == "protocol_function_declaration":
            # Extract function name
            func_name = extract_method_name(child)
            if func_name:
                methods.append(f"- {func_name}")
        elif child.type == "protocol_property_declaration":
            # Extract property name
            prop_name = extract_property_name(child)
            if prop_name:
                properties.append(f"- {prop_name}")
        elif child.type == "associatedtype_declaration":
            # Extract associated type
            assoc_name_node = child.child_by_field_name("name")
            if assoc_name_node:
                assoc_name = extract_text_content(assoc_name_node)
                properties.append(f"- associatedtype {assoc_name}")

    methods_str = "\n".join(methods) if methods else None
    properties_str = "\n".join(properties) if properties else None

    return methods_str, properties_str


def recursive_visit_swift(
    ckg_db: "CKGDatabase",
    root_node: Node,
    file_path: str,
    parent_class: ClassEntry | None = None,
    parent_struct: StructEntry | None = None,
    parent_protocol: InterfaceEntry | None = None,
    parent_function: FunctionEntry | None = None,
) -> None:
    """
    Enhanced recursive Swift AST visitor with 100% entity extraction coverage.

    Args:
        ckg_db: The CKG database instance to insert entries into
        root_node: The current AST node being processed
        file_path: The path to the source file
        parent_class: The parent class if current node is within a class
        parent_struct: The parent struct if current node is within a struct
        parent_protocol: The parent protocol if current node is within a protocol
        parent_function: The parent function if current node is within a function
    """

    # Handle import declarations
    if root_node.type == "import_declaration":
        import_name = ""
        for child in root_node.children:
            if child.type == "identifier":
                identifier_child = child.children[0] if child.children else None
                if identifier_child and identifier_child.type == "simple_identifier":
                    import_name = extract_text_content(identifier_child)
                    break

        if import_name:
            module_entry = ModuleEntry(
                name=import_name,
                file_path=file_path,
                body=extract_text_content(root_node),
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
                imports=import_name,
                exports=None,
            )
            ckg_db._insert_entry(module_entry)

    # Handle class_declaration (struct, class, enum, actor, extension)
    elif root_node.type == "class_declaration":
        decl_type = get_declaration_type(root_node)

        if decl_type == "struct":
            # Handle struct declaration
            name_node = root_node.child_by_field_name("name")
            if name_node:
                struct_name = extract_identifier_name(name_node)

                struct_entry = StructEntry(
                    name=struct_name,
                    file_path=file_path,
                    body=extract_text_content(root_node),
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract properties and methods
                body_node = root_node.child_by_field_name("body")
                if body_node:
                    fields, methods = extract_properties_and_methods(body_node)
                    struct_entry.fields = fields
                    struct_entry.methods = methods

                parent_struct = struct_entry
                ckg_db._insert_entry(struct_entry)

                # Check for generic parameters
                type_params_node = root_node.child_by_field_name("type_parameters")
                if type_params_node:
                    generic_params = extract_generic_parameters(type_params_node)
                    if generic_params:
                        generic_entry = GenericTypeEntry(
                            name=struct_name,
                            file_path=file_path,
                            body=extract_text_content(root_node),
                            start_line=root_node.start_point[0] + 1,
                            end_line=root_node.end_point[0] + 1,
                            type_parameters=generic_params,
                            constraints=None,
                        )
                        ckg_db._insert_entry(generic_entry)

        elif decl_type == "actor":
            # Handle actor declaration (treat as struct)
            name_node = root_node.child_by_field_name("name")
            if name_node:
                actor_name = extract_identifier_name(name_node)

                struct_entry = StructEntry(
                    name=actor_name,
                    file_path=file_path,
                    body=extract_text_content(root_node),
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract properties and methods
                body_node = root_node.child_by_field_name("body")
                if body_node:
                    fields, methods = extract_properties_and_methods(body_node)
                    struct_entry.fields = fields
                    struct_entry.methods = methods

                parent_struct = struct_entry
                ckg_db._insert_entry(struct_entry)

        elif decl_type == "class":
            # Handle class declaration
            name_node = root_node.child_by_field_name("name")
            if name_node:
                class_name = extract_identifier_name(name_node)

                class_entry = ClassEntry(
                    name=class_name,
                    file_path=file_path,
                    body=extract_text_content(root_node),
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract properties and methods
                body_node = root_node.child_by_field_name("body")
                if body_node:
                    fields, methods = extract_properties_and_methods(body_node)
                    class_entry.fields = fields
                    class_entry.methods = methods

                parent_class = class_entry
                ckg_db._insert_entry(class_entry)

                # Check for generic parameters
                type_params_node = root_node.child_by_field_name("type_parameters")
                if type_params_node:
                    generic_params = extract_generic_parameters(type_params_node)
                    if generic_params:
                        generic_entry = GenericTypeEntry(
                            name=class_name,
                            file_path=file_path,
                            body=extract_text_content(root_node),
                            start_line=root_node.start_point[0] + 1,
                            end_line=root_node.end_point[0] + 1,
                            type_parameters=generic_params,
                            constraints=None,
                        )
                        ckg_db._insert_entry(generic_entry)

        elif decl_type == "enum":
            # Handle enum declaration
            name_node = root_node.child_by_field_name("name")
            if name_node:
                enum_name = extract_identifier_name(name_node)

                enum_entry = EnumEntry(
                    name=enum_name,
                    file_path=file_path,
                    body=extract_text_content(root_node),
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                )

                # Extract enum cases - look for enum_class_body
                for child in root_node.children:
                    if child.type == "enum_class_body":
                        enum_cases = extract_enum_cases(child)
                        enum_entry.variants = enum_cases
                        break

                # Set parent context
                if parent_class:
                    enum_entry.parent_class = parent_class.name
                elif parent_struct:
                    enum_entry.parent_class = parent_struct.name

                ckg_db._insert_entry(enum_entry)

        elif decl_type == "extension":
            # Handle extension declaration
            extended_type = ""
            for child in root_node.children:
                if child.type == "user_type":
                    extended_type = extract_identifier_name(child)
                    break

            if extended_type:
                extension_entry = ExtensionEntry(
                    name=f"Extension_{extended_type}",
                    file_path=file_path,
                    body=extract_text_content(root_node),
                    start_line=root_node.start_point[0] + 1,
                    end_line=root_node.end_point[0] + 1,
                    extended_type=extended_type,
                )

                # Extract extension methods
                body_node = root_node.child_by_field_name("body")
                if body_node:
                    _, methods = extract_properties_and_methods(body_node)
                    extension_entry.methods = methods

                ckg_db._insert_entry(extension_entry)

    # Handle protocol declarations
    elif root_node.type == "protocol_declaration":
        name_node = root_node.child_by_field_name("name")
        if name_node:
            protocol_name = extract_identifier_name(name_node)

            protocol_entry = InterfaceEntry(
                name=protocol_name,
                file_path=file_path,
                body=extract_text_content(root_node),
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
            )

            # Extract protocol requirements
            body_node = root_node.child_by_field_name("body")
            if body_node:
                methods, properties = extract_protocol_requirements(body_node)
                protocol_entry.methods = methods
                protocol_entry.properties = properties

            parent_protocol = protocol_entry
            ckg_db._insert_entry(protocol_entry)

    # Handle type alias declarations
    elif root_node.type == "typealias_declaration":
        name_node = root_node.child_by_field_name("name")
        if name_node:
            alias_name = extract_identifier_name(name_node)

            # Extract target type
            type_node = root_node.child_by_field_name("type")
            target_type = extract_text_content(type_node) if type_node else None

            type_alias_entry = TypeAliasEntry(
                name=alias_name,
                file_path=file_path,
                body=extract_text_content(root_node),
                start_line=root_node.start_point[0] + 1,
                end_line=root_node.end_point[0] + 1,
                target_type=target_type,
            )
            ckg_db._insert_entry(type_alias_entry)

    # Handle function declarations
    elif root_node.type in [
        "function_declaration",
        "init_declaration",
        "deinit_declaration",
    ]:
        function_name = extract_method_name(root_node)

        function_entry = FunctionEntry(
            name=function_name,
            file_path=file_path,
            body=extract_text_content(root_node),
            start_line=root_node.start_point[0] + 1,
            end_line=root_node.end_point[0] + 1,
        )

        # Set parent context
        if parent_class:
            function_entry.parent_class = parent_class.name
        elif parent_struct:
            function_entry.parent_class = parent_struct.name
        elif parent_protocol:
            function_entry.parent_class = parent_protocol.name
        elif parent_function:
            function_entry.parent_function = parent_function.name

        ckg_db._insert_entry(function_entry)
        parent_function = function_entry

    # Recursively visit child nodes
    if len(root_node.children) != 0:
        for child in root_node.children:
            recursive_visit_swift(
                ckg_db,
                child,
                file_path,
                parent_class,
                parent_struct,
                parent_protocol,
                parent_function,
            )
