# Code Knowledge Graph (CKG)

A comprehensive code analysis tool that extracts structural entities from source code across 21+ programming languages and stores them in an SQLite database for efficient querying and analysis.

## 📋 Overview

CKG parses source code files using Tree-sitter parsers to extract code entities like functions, classes, interfaces, enums, and more. The extracted data is stored in a normalized SQLite database, enabling powerful code search, analysis, and knowledge graph construction.

## 🚀 Features

- **Multi-language Support**: 21+ programming languages including Python, JavaScript, Java, C++, Rust, Go, and more
- **Comprehensive Entity Extraction**: Functions, classes, structs, enums, interfaces, traits, modules, namespaces, and more
- **SQLite Database**: Fast, lightweight storage with 15 specialized entity tables
- **Smart Caching**: Hash-based caching system to avoid re-processing unchanged codebases
- **Detailed Testing Suite**: Comprehensive validation across all supported languages

## 🎯 Supported Languages & Entities

| Language   | Functions | Classes | Structs | Enums | Interfaces | Traits | Modules | Other |
|------------|-----------|---------|---------|-------|------------|--------|---------|-------|
| **C**      | ✅        | ❌      | ✅      | ✅    | ❌         | ❌     | ❌      | Unions |
| **C++**    | ✅        | ✅      | ✅      | ✅    | ❌         | ❌     | ❌      | Namespaces, Unions |
| **C#**     | ✅        | ✅      | ✅      | ✅    | ✅         | ❌     | ❌      | Namespaces |
| **Java**   | ✅        | ✅      | ❌      | ✅    | ✅         | ❌     | ❌      | |
| **Python** | ✅        | ✅      | ❌      | ❌    | ❌         | ❌     | ❌      | |
| **Rust**   | ✅        | ❌      | ✅      | ✅    | ❌         | ✅     | ✅      | |
| **Go**     | ✅        | ❌      | ✅      | ❌    | ✅         | ❌     | ❌      | |
| **TypeScript** | ✅    | ✅      | ❌      | ✅    | ✅         | ❌     | ❌      | Type Aliases, Namespaces |
| **Elixir** | ✅        | ❌      | ❌      | ❌    | ❌         | ❌     | ✅      | |
| **Scala**  | ✅        | ✅      | ❌      | ❌    | ❌         | ✅     | ❌      | |
| **Solidity** | ✅      | ❌      | ✅      | ✅    | ❌         | ❌     | ❌      | Contracts |
| **Svelte** | ✅        | ❌      | ❌      | ❌    | ❌         | ❌     | ❌      | Components |
| **+9 more** | ... | ... | ... | ... | ... | ... | ... | ... |

## 🏗️ Architecture

```plaintext
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Source Code   │ -> │  Tree-sitter     │ -> │  Entity         │
│   (.py, .js,    │    │  Parsers         │    │  Extractors     │
│    .java, etc.) │    │  (21 languages)  │    │  (Per language) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        v
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Query Tools   │ <- │   SQLite DB      │ <- │  CKG Database   │
│   (Search, etc.)│    │   (15 tables)    │    │  Builder        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📦 Installation

1. **Clone the repository**:

   ```bash
   git clone git@gitlab.fatdragon.dev:dev-army-ai/playground/ckg.git
   cd ckg
   ```

2. **Create Python virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:

   ```bash
   python run.py --help
   ```

## 🔧 Usage

### Basic Usage - Extract Code Knowledge Graph

```bash
# Extract entities from a codebase
python run.py --input-dir ./my_project --output-dir ./output --database-name project.db

# Extract from current directory
python run.py --input-dir . --output-dir ./ckg_output --database-name codebase.db

# With verbose output
python run.py --input-dir ./src --output-dir ./analysis --database-name app.db --verbose
```

### Testing & Validation

```bash
# Run comprehensive test suite (validates all 21 languages)
python test_ckg_extraction.py

# Test with custom settings
python test_ckg_extraction.py --test-dir ./my_tests --output-dir ./test_results

# Verbose testing
python test_ckg_extraction.py --verbose
```

## 🗄️ Database Schema

The SQLite database contains 15 specialized tables:

| Table           | Purpose                         | Key Columns                                 |
|-----------------|---------------------------------|---------------------------------------------|
| `functions`     | Function definitions            | `name`, `file_path`, `body`, `parent_class` |
| `classes`       | Class definitions               | `name`, `file_path`, `fields`, `methods`    |
| `structs`       | Struct definitions              | `name`, `file_path`, `fields`               |
| `enums`         | Enumeration types               | `name`, `file_path`, `enum_values`          |
| `interfaces`    | Interface definitions           | `name`, `file_path`, `methods`              |
| `traits`        | Trait definitions (Rust, Scala) | `name`, `file_path`, `methods`              |
| `modules`       | Module definitions              | `name`, `file_path`, `exports`              |
| `namespaces`    | Namespace definitions           | `name`, `file_path`, `members`              |
| `contracts`     | Smart contracts (Solidity)      | `name`, `file_path`, `functions`            |
| `components`    | UI components (Svelte, Vue)     | `name`, `file_path`, `props`                |
| `type_aliases`  | Type definitions                | `name`, `file_path`, `target_type`          |
| `extensions`    | Class extensions                | `name`, `file_path`, `extended_type`        |
| `unions`        | Union types                     | `name`, `file_path`, `fields`               |
| `generic_types` | Generic type definitions        | `name`, `file_path`, `type_parameters`      |

## 🔍 Querying the Database

```python
import sqlite3

# Connect to generated database
conn = sqlite3.connect('output/project.db')
cursor = conn.cursor()

# Find all functions in a specific file
cursor.execute("SELECT name, body FROM functions WHERE file_path LIKE '%main.py%'")
functions = cursor.fetchall()

# Get all classes with their methods
cursor.execute("""
    SELECT c.name as class_name, f.name as method_name 
    FROM classes c 
    LEFT JOIN functions f ON c.name = f.parent_class
""")
class_methods = cursor.fetchall()

# Count entities by language
cursor.execute("""
    SELECT 
        CASE 
            WHEN file_path LIKE '%.py' THEN 'Python'
            WHEN file_path LIKE '%.js' THEN 'JavaScript'
            WHEN file_path LIKE '%.java' THEN 'Java'
            ELSE 'Other'
        END as language,
        COUNT(*) as count
    FROM functions
    GROUP BY language
""")
language_stats = cursor.fetchall()
```

## 🔄 Execution Flow

### 1. **Input Processing**

- Discover source files in input directory
- Filter by supported extensions (.py, .js, .java, etc.)
- Generate codebase hash for caching

### 2. **Parsing Phase**

- Load appropriate Tree-sitter parser for each language
- Parse source files into Abstract Syntax Trees (AST)
- Handle parsing errors gracefully

### 3. **Entity Extraction**

- Visit AST nodes using language-specific extractors
- Extract entities: functions, classes, interfaces, etc.
- Capture metadata: location, parameters, relationships

### 4. **Database Storage**

- Create SQLite database with 15 entity tables
- Insert extracted entities with proper relationships
- Commit transactions for data integrity

### 5. **Caching & Optimization**

- Store database hash in `~/.ckg/ckg/storage_info.json`
- Reuse existing databases for unchanged codebases
- Enable incremental updates

## File Structure

```plaintext
ckg/
├── run.py                    # Main CLI tool
├── test_ckg_extraction.py    # Test suite
├── ckg/
│   ├── ckg_database.py       # Core database operations
│   ├── base.py               # Entity definitions
│   └── parsers/              # Language-specific parsers
│       ├── python_parser.py
│       ├── javascript_parser.py
│       └── ... (21 parsers)
├── test/                     # Test files for all languages
└── requirements.txt
```
