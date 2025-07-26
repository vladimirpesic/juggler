import hashlib
import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Literal

from tree_sitter import Parser
from tree_sitter_language_pack import get_parser
from utils.constants import LOCAL_STORAGE_PATH

from .base import (
    ClassEntry,
    ComponentEntry,
    ContractEntry,
    EnumEntry,
    ExtensionEntry,
    FunctionEntry,
    GenericTypeEntry,
    InterfaceEntry,
    ModuleEntry,
    NamespaceEntry,
    StructEntry,
    TraitEntry,
    TypeAliasEntry,
    UnionEntry,
    extension_to_language,
)
from .parsers import (
    recursive_visit_c,
    recursive_visit_cpp,
    recursive_visit_csharp,
    recursive_visit_dart,
    recursive_visit_elixir,
    recursive_visit_gleam,
    recursive_visit_go,
    recursive_visit_java,
    recursive_visit_javascript,
    recursive_visit_kotlin,
    recursive_visit_php,
    recursive_visit_python,
    recursive_visit_ruby,
    recursive_visit_rust,
    recursive_visit_scala,
    recursive_visit_solidity,
    recursive_visit_svelte,
    recursive_visit_swift,
    recursive_visit_typescript,
    recursive_visit_vue,
    recursive_visit_zig,
)

CKG_DATABASE_PATH = LOCAL_STORAGE_PATH / "ckg"
CKG_STORAGE_INFO_FILE = CKG_DATABASE_PATH / "storage_info.json"
CKG_DATABASE_EXPIRY_TIME = 60 * 60 * 24 * 7  # 1 week in seconds


"""
Known issues:
1. When a subdirectory of a codebase that has already been indexed, the CKG is built again for this subdirectory.
2. The rebuilding logic can be improved by only rebuilding for files that have been modified.
3. For JavaScript and TypeScript, the AST is not complete: anonymous functions, arrow functions, etc., are not parsed.
"""


def get_ckg_database_path(codebase_snapshot_hash: str) -> Path:
    """Get the path to the CKG database for a codebase path."""
    return CKG_DATABASE_PATH / f"{codebase_snapshot_hash}.db"


def is_git_repository(folder_path: Path) -> bool:
    """Check if the folder is a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=folder_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def get_git_status_hash(folder_path: Path) -> str:
    """Get hash for git repository (clean or dirty)."""
    try:
        # Check if we have any uncommitted changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=folder_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Get the current commit hash
        commit_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=folder_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        base_hash = commit_result.stdout.strip()

        # If no uncommitted changes, just use the commit hash
        if not status_result.stdout.strip():
            return f"git-clean-{base_hash}"

        # If there are uncommitted changes, include them in the hash
        uncommitted_hash = hashlib.md5(status_result.stdout.encode()).hexdigest()[:8]
        return f"git-dirty-{base_hash}-{uncommitted_hash}"

    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        # Fallback to file metadata hash if git commands fail
        return get_file_metadata_hash(folder_path)


def get_file_metadata_hash(folder_path: Path) -> str:
    """Get hash based on file metadata (name, mtime, size) for non-git repositories."""
    hash_md5 = hashlib.md5()

    for file in folder_path.glob("**/*"):
        if file.is_file() and not file.name.startswith("."):
            stat = file.stat()
            hash_md5.update(file.name.encode())
            hash_md5.update(str(stat.st_mtime).encode())  # modification time
            hash_md5.update(str(stat.st_size).encode())  # file size

    return f"metadata-{hash_md5.hexdigest()}"


def get_folder_snapshot_hash(folder_path: Path) -> str:
    """Get the hash of the folder snapshot, to make sure that the CKG is up to date."""
    # Strategy 1: Git repository
    if is_git_repository(folder_path):
        return get_git_status_hash(folder_path)

    # Strategy 2: Non-git repository - file metadata
    return get_file_metadata_hash(folder_path)


def clear_older_ckg():
    """Iterate over all the files in the CKG storage directory and delete the ones that are older than 1 week."""
    for file in CKG_DATABASE_PATH.glob("**/*"):
        if (
            file.is_file()
            and not file.name.startswith(".")
            and file.name.endswith(".db")
            and file.stat().st_mtime < datetime.now().timestamp() - CKG_DATABASE_EXPIRY_TIME
        ):
            try:
                file.unlink()
            except Exception as e:
                print(f"error deleting older CKG database - {file.absolute().as_posix()}: {e}")


SQL_LIST = {
    "functions": """
    CREATE TABLE IF NOT EXISTS functions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL,
        parent_function TEXT,
        parent_class TEXT
    )""",
    "classes": """
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        fields TEXT,
        methods TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "structs": """
    CREATE TABLE IF NOT EXISTS structs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        fields TEXT,
        methods TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "enums": """
    CREATE TABLE IF NOT EXISTS enums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        enum_values TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "interfaces": """
    CREATE TABLE IF NOT EXISTS interfaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        methods TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "traits": """
    CREATE TABLE IF NOT EXISTS traits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        methods TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "modules": """
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        exports TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "namespaces": """
    CREATE TABLE IF NOT EXISTS namespaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        members TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "type_aliases": """
    CREATE TABLE IF NOT EXISTS type_aliases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        target_type TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "components": """
    CREATE TABLE IF NOT EXISTS components (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        props TEXT,
        methods TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "contracts": """
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        functions TEXT,
        events TEXT,
        modifiers TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "extensions": """
    CREATE TABLE IF NOT EXISTS extensions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        extended_type TEXT,
        methods TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "unions": """
    CREATE TABLE IF NOT EXISTS unions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        fields TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
    "generic_types": """
    CREATE TABLE IF NOT EXISTS generic_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        body TEXT NOT NULL,
        type_parameters TEXT,
        constraints TEXT,
        start_line INTEGER NOT NULL,
        end_line INTEGER NOT NULL
    )""",
}


class CKGDatabase:
    def __init__(self, codebase_path: Path):
        self._db_connection: sqlite3.Connection
        self._codebase_path: Path = codebase_path

        if not CKG_DATABASE_PATH.exists():
            CKG_DATABASE_PATH.mkdir(parents=True, exist_ok=True)

        ckg_storage_info: dict[str, str] = {}

        # to save time and storage, we try to reuse the existing database if the codebase snapshot hash is the same
        # get the existing codebase snapshot hash from the storage info file
        if CKG_STORAGE_INFO_FILE.exists():
            with open(CKG_STORAGE_INFO_FILE, "r") as f:
                ckg_storage_info = json.load(f)
                if codebase_path.absolute().as_posix() in ckg_storage_info:
                    existing_codebase_snapshot_hash = ckg_storage_info[
                        codebase_path.absolute().as_posix()
                    ]
                else:
                    existing_codebase_snapshot_hash = ""
        else:
            existing_codebase_snapshot_hash = ""

        current_codebase_snapshot_hash = get_folder_snapshot_hash(codebase_path)
        if existing_codebase_snapshot_hash == current_codebase_snapshot_hash:
            # we can reuse the existing database
            database_path = get_ckg_database_path(existing_codebase_snapshot_hash)
        else:
            # we need to create a new database and delete the old one
            database_path = get_ckg_database_path(existing_codebase_snapshot_hash)
            if database_path.exists():
                database_path.unlink()
            database_path = get_ckg_database_path(current_codebase_snapshot_hash)

            ckg_storage_info[codebase_path.absolute().as_posix()] = current_codebase_snapshot_hash
            with open(CKG_STORAGE_INFO_FILE, "w") as f:
                json.dump(ckg_storage_info, f)

        if database_path.exists():
            # reuse existing database
            self._db_connection = sqlite3.connect(database_path)
        else:
            # create new database with tables and build the CKG
            self._db_connection = sqlite3.connect(database_path)
            for sql in SQL_LIST.values():
                self._db_connection.execute(sql)
            self._db_connection.commit()
            self._construct_ckg()

    def __del__(self):
        self._db_connection.close()

    def update(self):
        """Update the CKG database."""
        self._construct_ckg()

    def _construct_ckg(self) -> None:
        """Initialise the code knowledge graph."""

        # lazy load the parsers for the languages when needed
        language_to_parser: dict[str, Parser] = {}
        for file in self._codebase_path.glob("**/*"):
            # skip hidden files and files in a hidden directory
            if (
                file.is_file()
                and not file.name.startswith(".")
                and "/." not in file.absolute().as_posix()
            ):
                extension = file.suffix
                # ignore files with unknown extensions
                if extension not in extension_to_language:
                    continue
                language = extension_to_language[extension]

                language_parser = language_to_parser.get(language)
                if not language_parser:
                    language_parser = get_parser(language)  # type: ignore
                    language_to_parser[language] = language_parser

                tree = language_parser.parse(file.read_bytes())
                root_node = tree.root_node

                match language:
                    case "python":
                        recursive_visit_python(self, root_node, file.absolute().as_posix())
                    case "java":
                        recursive_visit_java(self, root_node, file.absolute().as_posix())
                    case "cpp":
                        recursive_visit_cpp(self, root_node, file.absolute().as_posix())
                    case "c":
                        recursive_visit_c(self, root_node, file.absolute().as_posix())
                    case "typescript":
                        recursive_visit_typescript(self, root_node, file.absolute().as_posix())
                    case "javascript":
                        recursive_visit_javascript(self, root_node, file.absolute().as_posix())
                    case "rust":
                        recursive_visit_rust(self, root_node, file.absolute().as_posix())
                    case "go":
                        recursive_visit_go(self, root_node, file.absolute().as_posix())
                    case "ruby":
                        recursive_visit_ruby(self, root_node, file.absolute().as_posix())
                    case "php":
                        recursive_visit_php(self, root_node, file.absolute().as_posix())
                    case "csharp":
                        recursive_visit_csharp(self, root_node, file.absolute().as_posix())
                    case "dart":
                        recursive_visit_dart(self, root_node, file.absolute().as_posix())
                    case "elixir":
                        recursive_visit_elixir(self, root_node, file.absolute().as_posix())
                    case "gleam":
                        recursive_visit_gleam(self, root_node, file.absolute().as_posix())
                    case "kotlin":
                        recursive_visit_kotlin(self, root_node, file.absolute().as_posix())
                    case "scala":
                        recursive_visit_scala(self, root_node, file.absolute().as_posix())
                    case "solidity":
                        recursive_visit_solidity(self, root_node, file.absolute().as_posix())
                    case "svelte":
                        recursive_visit_svelte(self, root_node, file.absolute().as_posix())
                    case "swift":
                        recursive_visit_swift(self, root_node, file.absolute().as_posix())
                    case "vue":
                        recursive_visit_vue(self, root_node, file.absolute().as_posix())
                    case "zig":
                        recursive_visit_zig(self, root_node, file.absolute().as_posix())
                    case _:
                        continue

    def _insert_entry(
        self,
        entry: FunctionEntry
        | ClassEntry
        | StructEntry
        | EnumEntry
        | InterfaceEntry
        | TraitEntry
        | ModuleEntry
        | NamespaceEntry
        | TypeAliasEntry
        | ComponentEntry
        | ContractEntry
        | ExtensionEntry
        | UnionEntry
        | GenericTypeEntry,
    ) -> None:
        """
        Insert entry into db.

        Args:
            entry: the entry to insert

        Returns:
            None
        """
        # TODO: add try catch block to avoid connection problem.
        match entry:
            case FunctionEntry():
                self._insert_function(entry)
            case ClassEntry():
                self._insert_class(entry)
            case StructEntry():
                self._insert_struct(entry)
            case EnumEntry():
                self._insert_enum(entry)
            case InterfaceEntry():
                self._insert_interface(entry)
            case TraitEntry():
                self._insert_trait(entry)
            case ModuleEntry():
                self._insert_module(entry)
            case NamespaceEntry():
                self._insert_namespace(entry)
            case TypeAliasEntry():
                self._insert_type_alias(entry)
            case ComponentEntry():
                self._insert_component(entry)
            case ContractEntry():
                self._insert_contract(entry)
            case ExtensionEntry():
                self._insert_extension(entry)
            case UnionEntry():
                self._insert_union(entry)
            case GenericTypeEntry():
                self._insert_generic_type(entry)

        self._db_connection.commit()

    def _insert_function(self, entry: FunctionEntry) -> None:
        """
        Insert function entry including functions and class methodsinto db.

        Args:
            entry: the entry to insert

        Returns:
            None
        """
        self._db_connection.execute(
            """
                INSERT INTO functions (name, file_path, body, start_line, end_line, parent_function, parent_class)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.start_line,
                entry.end_line,
                entry.parent_function,
                entry.parent_class,
            ),
        )

    def _insert_class(self, entry: ClassEntry) -> None:
        """
        Insert class entry into db.

        Args:
            entry: the entry to insert

        Returns:
            None
        """
        self._db_connection.execute(
            """
                INSERT INTO classes (name, file_path, body, fields, methods, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.fields,
                entry.methods,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_struct(self, entry: StructEntry) -> None:
        """Insert struct entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO structs (name, file_path, body, fields, methods, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.fields,
                entry.methods,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_enum(self, entry: EnumEntry) -> None:
        """Insert enum entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO enums (name, file_path, body, enum_values, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.variants,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_interface(self, entry: InterfaceEntry) -> None:
        """Insert interface entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO interfaces (name, file_path, body, methods, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.methods,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_trait(self, entry: TraitEntry) -> None:
        """Insert trait entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO traits (name, file_path, body, methods, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.methods,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_module(self, entry: ModuleEntry) -> None:
        """Insert module entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO modules (name, file_path, body, exports, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.exports,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_namespace(self, entry: NamespaceEntry) -> None:
        """Insert namespace entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO namespaces (name, file_path, body, members, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.members,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_type_alias(self, entry: TypeAliasEntry) -> None:
        """Insert type alias entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO type_aliases (name, file_path, body, target_type, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.target_type,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_component(self, entry: ComponentEntry) -> None:
        """Insert component entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO components (name, file_path, body, props, methods, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.props,
                entry.methods,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_contract(self, entry: ContractEntry) -> None:
        """Insert contract entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO contracts (name, file_path, body, functions, events, modifiers, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.functions,
                entry.events,
                entry.modifiers,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_extension(self, entry: ExtensionEntry) -> None:
        """Insert extension entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO extensions (name, file_path, body, extended_type, methods, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.extended_type,
                entry.methods,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_union(self, entry: UnionEntry) -> None:
        """Insert union entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO unions (name, file_path, body, fields, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.variants,
                entry.start_line,
                entry.end_line,
            ),
        )

    def _insert_generic_type(self, entry: GenericTypeEntry) -> None:
        """Insert generic type entry into db."""
        self._db_connection.execute(
            """
                INSERT INTO generic_types (name, file_path, body, type_parameters, constraints, start_line, end_line)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.name,
                entry.file_path,
                entry.body,
                entry.type_parameters,
                entry.constraints,
                entry.start_line,
                entry.end_line,
            ),
        )

    def query_function(
        self,
        identifier: str,
        entry_type: Literal["function", "class_method"] = "function",
    ) -> list[FunctionEntry]:
        """
        Search for a function in the database.

        Args:
            identifier: the identifier of the function to search for

        Returns:
            a list of function entries
        """
        records = self._db_connection.execute(
            """SELECT name, file_path, body, start_line, end_line, parent_function, parent_class FROM functions WHERE name = ?""",
            (identifier,),
        ).fetchall()
        function_entries: list[FunctionEntry] = []
        for record in records:
            match entry_type:
                case "function":
                    if record[6] is None:
                        function_entries.append(
                            FunctionEntry(
                                name=record[0],
                                file_path=record[1],
                                body=record[2],
                                start_line=record[3],
                                end_line=record[4],
                                parent_function=record[5],
                                parent_class=record[6],
                            )
                        )
                case "class_method":
                    if record[6] is not None:
                        function_entries.append(
                            FunctionEntry(
                                name=record[0],
                                file_path=record[1],
                                body=record[2],
                                start_line=record[3],
                                end_line=record[4],
                                parent_function=record[5],
                                parent_class=record[6],
                            )
                        )
        return function_entries

    def query_class(self, identifier: str) -> list[ClassEntry]:
        """
        Search for a class in the database.

        Args:
            identifier: the identifier of the class to search for

        Returns:
            a list of class entries
        """
        records = self._db_connection.execute(
            """SELECT name, file_path, body, fields, methods, start_line, end_line FROM classes WHERE name = ?""",
            (identifier,),
        ).fetchall()
        class_entries: list[ClassEntry] = []
        for record in records:
            class_entries.append(
                ClassEntry(
                    name=record[0],
                    file_path=record[1],
                    body=record[2],
                    fields=record[3],
                    methods=record[4],
                    start_line=record[5],
                    end_line=record[6],
                )
            )
        return class_entries
