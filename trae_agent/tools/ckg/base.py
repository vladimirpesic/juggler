from dataclasses import dataclass


# Define dataclasses for CKG entries
@dataclass
class FunctionEntry:
    """
    dataclass for function entry.
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    parent_function: str | None = None
    parent_class: str | None = None


@dataclass
class ClassEntry:
    """
    dataclass for class entry.
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    fields: str | None = None
    methods: str | None = None


@dataclass
class EnumEntry:
    """
    dataclass for enum entry.
    Supported by: C, C++, C#, Java, Kotlin, Rust, Swift, Go, TypeScript, Dart
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    variants: str | None = None
    parent_class: str | None = None


@dataclass
class InterfaceEntry:
    """
    dataclass for interface entry.
    Supported by: C#, Java, Kotlin, TypeScript, Swift (protocols), Dart, Go
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    methods: str | None = None
    properties: str | None = None


@dataclass
class StructEntry:
    """
    dataclass for struct entry.
    Supported by: C, C++, C#, Rust, Swift, Go, Zig
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    fields: str | None = None
    methods: str | None = None  # C# and Swift support methods in structs


@dataclass
class TraitEntry:
    """
    dataclass for trait entry.
    Supported by: Rust, Scala, PHP (traits)
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    methods: str | None = None
    associated_types: str | None = None


@dataclass
class ModuleEntry:
    """
    dataclass for module entry.
    Supported by: Python, Ruby, Elixir, Rust, Go (packages), Dart
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    exports: str | None = None
    imports: str | None = None


@dataclass
class NamespaceEntry:
    """
    dataclass for namespace entry.
    Supported by: C++, C#, TypeScript
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    members: str | None = None


@dataclass
class TypeAliasEntry:
    """
    dataclass for type alias entry.
    Supported by: TypeScript, Kotlin, Rust, Swift, Scala, Go
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    target_type: str | None = None


@dataclass
class ComponentEntry:
    """
    dataclass for component entry.
    Supported by: Vue, Svelte, JavaScript/TypeScript (React)
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    props: str | None = None
    methods: str | None = None
    template: str | None = None


@dataclass
class ContractEntry:
    """
    dataclass for smart contract entry.
    Supported by: Solidity
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    functions: str | None = None
    events: str | None = None
    modifiers: str | None = None
    state_variables: str | None = None


@dataclass
class ExtensionEntry:
    """
    dataclass for extension entry.
    Supported by: Swift, Kotlin, C#, Dart
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    extended_type: str | None = None
    methods: str | None = None


@dataclass
class UnionEntry:
    """
    dataclass for union entry.
    Supported by: C, C++, Rust (union types), TypeScript (union types), Zig
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    variants: str | None = None


@dataclass
class GenericTypeEntry:
    """
    dataclass for generic type definitions.
    Supported by: Java, C#, Kotlin, TypeScript, Swift, Rust, Scala, Dart
    """

    name: str
    file_path: str
    body: str
    start_line: int
    end_line: int
    type_parameters: str | None = None
    constraints: str | None = None


extension_to_language = {
    ".c": "c",
    ".h": "c",
    ".c++": "cpp",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".cs": "csharp",
    ".dart": "dart",
    ".ex": "elixir",
    ".exs": "elixir",
    ".gleam": "gleam",
    ".go": "go",
    ".java": "java",
    ".cjs": "javascript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".php": "php",
    ".php3": "php",
    ".php4": "php",
    ".php5": "php",
    ".phtml": "php",
    ".py": "python",
    ".pyw": "python",
    ".rb": "ruby",
    ".rbw": "ruby",
    ".rs": "rust",
    ".sc": "scala",
    ".scala": "scala",
    ".sol": "solidity",
    ".svelte": "svelte",
    ".swift": "swift",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".vue": "vue",
    ".zig": "zig",
}
