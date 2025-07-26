from pathlib import Path
from typing import override

from .base import Tool, ToolCallArguments, ToolExecResult, ToolParameter
from .ckg.ckg_database import CKGDatabase
from .run import MAX_RESPONSE_LEN

CKGToolCommands = [
    "search_function",
    "search_class",
    "search_class_method",
    "search_struct",
    "search_enum",
    "search_interface",
    "search_trait",
    "search_module",
    "search_namespace",
    "search_type_alias",
    "search_component",
    "search_contract",
    "search_extension",
    "search_union",
    "search_generic_type",
]


class CKGTool(Tool):
    """Tool to construct and query the code knowledge graph of a codebase."""

    def __init__(self, model_provider: str | None = None) -> None:
        super().__init__(model_provider)

        # We store the codebase path with built CKG in the following format:
        # {
        #     "codebase_path": {
        #         "db_connection": sqlite3.Connection,
        #         "codebase_snapshot_hash": str,
        #     }
        # }
        self._ckg_databases: dict[Path, CKGDatabase] = {}

    @override
    def get_model_provider(self) -> str | None:
        return self._model_provider

    @override
    def get_name(self) -> str:
        return "ckg"

    @override
    def get_description(self) -> str:
        return """Query the code knowledge graph of a codebase.
* State is persistent across command calls and discussions with the user
* The `search_function` command searches for functions in the codebase
* The `search_class` command searches for classes in the codebase
* The `search_class_method` command searches for class methods in the codebase
* The `search_struct` command searches for structs in the codebase
* The `search_enum` command searches for enums in the codebase
* The `search_interface` command searches for interfaces in the codebase
* The `search_trait` command searches for traits in the codebase
* The `search_module` command searches for modules in the codebase
* The `search_namespace` command searches for namespaces in the codebase
* The `search_type_alias` command searches for type aliases in the codebase
* The `search_component` command searches for components in the codebase
* The `search_contract` command searches for smart contracts in the codebase
* The `search_extension` command searches for extensions in the codebase
* The `search_union` command searches for unions in the codebase
* The `search_generic_type` command searches for generic types in the codebase
* If a `command` generates a long output, it will be truncated and marked with `<response clipped>`
* If multiple entries are found, the tool will return all of them until the truncation is reached.
* By default, the tool will print function or class bodies as well as the file path and line number of the function or class. You can disable this by setting the `print_body` parameter to `false`.
* The CKG is not completely accurate, and may not be able to find all functions or classes in the codebase.
"""

    @override
    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="command",
                type="string",
                description=f"The command to run. Allowed options are {', '.join(CKGToolCommands)}.",
                required=True,
                enum=CKGToolCommands,
            ),
            ToolParameter(
                name="path",
                type="string",
                description="The path to the codebase.",
                required=True,
            ),
            ToolParameter(
                name="identifier",
                type="string",
                description="The identifier of the code construct to search for in the code knowledge graph.",
                required=True,
            ),
            ToolParameter(
                name="print_body",
                type="boolean",
                description="Whether to print the body of the function or class. This is enabled by default.",
                required=False,
            ),
        ]

    @override
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        command = str(arguments.get("command")) if "command" in arguments else None
        if command is None:
            return ToolExecResult(
                error=f"No command provided for the {self.get_name()} tool",
                error_code=-1,
            )
        path = str(arguments.get("path")) if "path" in arguments else None
        if path is None:
            return ToolExecResult(
                error=f"No path provided for the {self.get_name()} tool",
                error_code=-1,
            )
        identifier = str(arguments.get("identifier")) if "identifier" in arguments else None
        if identifier is None:
            return ToolExecResult(
                error=f"No identifier provided for the {self.get_name()} tool",
                error_code=-1,
            )
        print_body = bool(arguments.get("print_body")) if "print_body" in arguments else True

        codebase_path = Path(path)
        if not codebase_path.exists():
            return ToolExecResult(
                error=f"Codebase path {path} does not exist",
                error_code=-1,
            )
        if not codebase_path.is_dir():
            return ToolExecResult(
                error=f"Codebase path {path} is not a directory",
                error_code=-1,
            )

        ckg_database = self._ckg_databases.get(codebase_path)
        if ckg_database is None:
            ckg_database = CKGDatabase(codebase_path)
            self._ckg_databases[codebase_path] = ckg_database

        match command:
            case "search_function":
                return ToolExecResult(
                    output=self._search_function(ckg_database, identifier, print_body)
                )
            case "search_class":
                return ToolExecResult(
                    output=self._search_class(ckg_database, identifier, print_body)
                )
            case "search_class_method":
                return ToolExecResult(
                    output=self._search_class_method(ckg_database, identifier, print_body)
                )
            case "search_struct":
                return ToolExecResult(
                    output=self._search_struct(ckg_database, identifier, print_body)
                )
            case "search_enum":
                return ToolExecResult(
                    output=self._search_enum(ckg_database, identifier, print_body)
                )
            case "search_interface":
                return ToolExecResult(
                    output=self._search_interface(ckg_database, identifier, print_body)
                )
            case "search_trait":
                return ToolExecResult(
                    output=self._search_trait(ckg_database, identifier, print_body)
                )
            case "search_module":
                return ToolExecResult(
                    output=self._search_module(ckg_database, identifier, print_body)
                )
            case "search_namespace":
                return ToolExecResult(
                    output=self._search_namespace(ckg_database, identifier, print_body)
                )
            case "search_type_alias":
                return ToolExecResult(
                    output=self._search_type_alias(ckg_database, identifier, print_body)
                )
            case "search_component":
                return ToolExecResult(
                    output=self._search_component(ckg_database, identifier, print_body)
                )
            case "search_contract":
                return ToolExecResult(
                    output=self._search_contract(ckg_database, identifier, print_body)
                )
            case "search_extension":
                return ToolExecResult(
                    output=self._search_extension(ckg_database, identifier, print_body)
                )
            case "search_union":
                return ToolExecResult(
                    output=self._search_union(ckg_database, identifier, print_body)
                )
            case "search_generic_type":
                return ToolExecResult(
                    output=self._search_generic_type(ckg_database, identifier, print_body)
                )
            case _:
                return ToolExecResult(error=f"Invalid command: {command}", error_code=-1)

    def _search_function(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a function in the ckg database."""

        entries = ckg_database.query_function(identifier, entry_type="function")

        if len(entries) == 0:
            return f"No functions named {identifier} found."

        output = f"Found {len(entries)} functions named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_class(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a class in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No classes named {identifier} found."

        output = f"Found {len(entries)} classes named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Fields:\n{entry.fields}\n"
            if entry.methods:
                output += f"Methods:\n{entry.methods}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_class_method(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a class method in the ckg database."""

        entries = ckg_database.query_function(identifier, entry_type="class_method")

        if len(entries) == 0:
            return f"No class methods named {identifier} found."

        output = f"Found {len(entries)} class methods named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line} within class {entry.parent_class}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_struct(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a struct in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No structs named {identifier} found."

        output = f"Found {len(entries)} structs named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Fields:\n{entry.fields}\n"
            if entry.methods:
                output += f"Methods:\n{entry.methods}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_enum(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for an enum in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No enums named {identifier} found."

        output = f"Found {len(entries)} enums named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Variants:\n{entry.fields}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_interface(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for an interface in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No interfaces named {identifier} found."

        output = f"Found {len(entries)} interfaces named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Properties:\n{entry.fields}\n"
            if entry.methods:
                output += f"Methods:\n{entry.methods}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_trait(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a trait in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No traits named {identifier} found."

        output = f"Found {len(entries)} traits named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Associated Types:\n{entry.fields}\n"
            if entry.methods:
                output += f"Methods:\n{entry.methods}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_module(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a module in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No modules named {identifier} found."

        output = f"Found {len(entries)} modules named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Imports:\n{entry.fields}\n"
            if entry.methods:
                output += f"Exports:\n{entry.methods}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_namespace(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a namespace in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No namespaces named {identifier} found."

        output = f"Found {len(entries)} namespaces named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Members:\n{entry.fields}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_type_alias(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a type alias in the ckg database."""

        entries = ckg_database.query_function(identifier, entry_type="function")

        if len(entries) == 0:
            return f"No type aliases named {identifier} found."

        output = f"Found {len(entries)} type aliases named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_component(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a component in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No components named {identifier} found."

        output = f"Found {len(entries)} components named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Props:\n{entry.fields}\n"
            if entry.methods:
                output += f"Methods:\n{entry.methods}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_contract(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a smart contract in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No contracts named {identifier} found."

        output = f"Found {len(entries)} contracts named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"State Variables:\n{entry.fields}\n"
            if entry.methods:
                output += f"Functions:\n{entry.methods}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_extension(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for an extension in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No extensions named {identifier} found."

        output = f"Found {len(entries)} extensions named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Extended Type:\n{entry.fields}\n"
            if entry.methods:
                output += f"Methods:\n{entry.methods}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_union(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a union in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No unions named {identifier} found."

        output = f"Found {len(entries)} unions named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Variants:\n{entry.fields}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output

    def _search_generic_type(
        self, ckg_database: CKGDatabase, identifier: str, print_body: bool = True
    ) -> str:
        """Search for a generic type in the ckg database."""

        entries = ckg_database.query_class(identifier)

        if len(entries) == 0:
            return f"No generic types named {identifier} found."

        output = f"Found {len(entries)} generic types named {identifier}:\n"

        index = 1
        for entry in entries:
            output += f"{index}. {entry.file_path}:{entry.start_line}-{entry.end_line}\n"
            if entry.fields:
                output += f"Type Parameters:\n{entry.fields}\n"
            if entry.methods:
                output += f"Constraints:\n{entry.methods}\n"
            if print_body:
                output += f"{entry.body}\n\n"

            index += 1

            if len(output) > MAX_RESPONSE_LEN:
                output = (
                    output[:MAX_RESPONSE_LEN]
                    + f"\n<response clipped> {len(entries) - index + 1} more entries not shown"
                )
                break

        return output
