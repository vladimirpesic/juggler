# CKG Test Suite - Comprehensive Entity Extraction Verification

This repository contains a comprehensive test suite for the Code Knowledge Graph (CKG) system, designed to verify that all structural elements from various programming languages are properly extracted and stored in the SQLite database.

## 📁 Test Files Created

The following test files have been created in the `test/` directory, each containing **every structural element** that the respective language supports, including:

### 📊 Language Coverage (21 Languages)

| Language     | File          | Size     | Key Structural Elements                                         |
|--------------|---------------|----------|-----------------------------------------------------------------|
| C            | test.c        | 2.8 KB   | Functions, Structs, Enums, Unions                               |
| C++          | test.cpp      | 6.5 KB   | Classes, Functions, Structs, Enums, Namespaces, Unions          |
| C#           | test.cs       | 11.6 KB  | Classes, Functions, Structs, Enums, Interfaces, Namespaces      |
| Dart         | test.dart     | 6.2 KB   | Classes, Functions, Enums, Interfaces, Modules                  |
| Elixir       | test.ex       | 8.3 KB   | Functions, Modules                                              |
| Gleam        | test.gleam    | 8.0 KB   | Functions, Modules                                              |
| Go           | test.go       | 11.8 KB  | Functions, Structs, Interfaces, Modules (packages)              |
| Java         | test.java     | 10.1 KB  | Classes, Functions, Enums, Interfaces                           |
| JavaScript   | test.js       | 12.6 KB  | Functions, Classes, Components                                  |
| Kotlin       | test.kt       | 14.0 KB  | Classes, Functions, Enums, Interfaces                           |
| PHP          | test.php      | 5.4 KB   | Classes, Functions, Enums, Interfaces, Traits                   |
| Python       | test.py       | 7.1 KB   | Functions, Classes, Modules                                     |
| Ruby         | test.rb       | 6.3 KB   | Classes, Functions, Modules                                     |
| Rust         | test.rs       | 11.0 KB  | Functions, Structs, Enums, Traits, Modules                      |
| Scala        | test.scala    | 9.6 KB   | Functions, Classes, Traits                                      |
| Solidity     | test.sol      | 10.2 KB  | Contracts, Functions, Structs, Enums, Interfaces                |
| Svelte       | test.svelte   | 16.3 KB  | Components, Functions                                           |
| Swift        | test.swift    | 17.8 KB  | Classes, Functions, Structs, Enums, Interfaces, Extensions      |
| TypeScript   | test.ts       | 14.5 KB  | Functions, Classes, Enums, Interfaces, Namespaces, Type Aliases |
| Vue          | test.vue      | 21.5 KB  | Components, Functions                                           |
| Zig          | test.zig      | 25.5 KB  | Functions, Structs, Enums, Unions                               |

## 🔧 Comprehensive Test Script (`test_ckg_extraction.py`)

Performs comprehensive entity extraction verification:

```bash
python test_ckg_extraction.py
```

**Features:**

- 🔍 **Discovery**: Automatically discovers all test files in the `test/` directory
- 🚀 **Execution**: Runs the CKG tool on all test files
- 📊 **Analysis**: Analyzes the generated SQLite database for extracted entities
- 📋 **Reporting**: Generates detailed reports showing:
  - Entity extraction counts per language
  - Coverage percentages for expected structural elements
  - Examples of extracted entities
  - Files where entities were found
- 💾 **Export**: Saves detailed JSON reports for further analysis
- ✅ **Validation**: Validates extraction completeness with configurable thresholds

### Command Line Options

```bash
# Run with default settings
python test_ckg_extraction.py

# Specify custom test directory
python test_ckg_extraction.py --test-dir /path/to/test/files

# Specify custom output directory
python test_ckg_extraction.py --output-dir ./results

# Enable verbose output
python test_ckg_extraction.py --verbose
```

## 📈 Expected Entity Types by Language

The test script validates extraction of the following entity types for each language:

```python
EXPECTED_ENTITIES = {
    'c': ['functions', 'structs', 'enums', 'unions'],
    'cpp': ['functions', 'classes', 'structs', 'enums', 'namespaces', 'unions'],
    'csharp': ['functions', 'classes', 'structs', 'enums', 'interfaces', 'namespaces'],
    'dart': ['functions', 'classes', 'enums', 'interfaces', 'modules'],
    'elixir': ['functions', 'modules'],
    'gleam': ['functions', 'modules'],
    'go': ['functions', 'structs', 'interfaces', 'modules'],
    'java': ['functions', 'classes', 'enums', 'interfaces'],
    'javascript': ['functions', 'classes', 'components'],
    'kotlin': ['functions', 'classes', 'enums', 'interfaces'],
    'php': ['functions', 'classes', 'enums', 'interfaces', 'traits'],
    'python': ['functions', 'classes', 'modules'],
    'ruby': ['functions', 'classes', 'modules'],
    'rust': ['functions', 'structs', 'enums', 'traits', 'modules'],
    'scala': ['functions', 'classes', 'traits'],
    'solidity': ['functions', 'contracts', 'structs', 'enums', 'interfaces'],
    'svelte': ['components', 'functions'],
    'swift': ['functions', 'classes', 'structs', 'enums', 'interfaces', 'extensions'],
    'typescript': ['functions', 'classes', 'enums', 'interfaces', 'namespaces', 'type_aliases'],
    'vue': ['components', 'functions'],
    'zig': ['functions', 'structs', 'enums', 'unions']
}
```

## 📊 Sample Test Report Output

When you run the comprehensive test, you'll get a detailed report like this:

```plaintext
================================================================================
CKG ENTITY EXTRACTION TEST REPORT
================================================================================

Database Path: test_output/ckg.db
Total Test Files: 21
Languages Tested: 21

📊 LANGUAGE COVERAGE SUMMARY:
--------------------------------------------------------------------------------
✅ PYTHON       | Files:  1 | Entities:   15 | Coverage: 100.0%
✅ JAVA         | Files:  1 | Entities:   18 | Coverage: 100.0%
✅ RUST         | Files:  1 | Entities:   25 | Coverage: 100.0%
⚠️  SOLIDITY    | Files:  1 | Entities:   12 | Coverage:  80.0%
✅ SWIFT        | Files:  1 | Entities:   22 | Coverage: 100.0%
...
--------------------------------------------------------------------------------
TOTAL ENTITIES EXTRACTED: 347

🔍 PYTHON DETAILED REPORT
------------------------------------------------------------
Files (1):
  📄 test.py (7,126 bytes)

Expected Entity Types: functions, classes, modules

Entity Extraction Results:
  ✅ functions        | Count:   8 | Files: 1 | Examples: main, add, divide
  ✅ classes          | Count:   5 | Files: 1 | Examples: Person, Calculator, Vehicle
  ✅ modules          | Count:   2 | Files: 1 | Examples: math_utils, data_processor
```

## 🚀 Run Comprehensive Tests

   ```bash
   python test_ckg_extraction.py
   ```

- Check console output for immediate feedback
- Examine `test_output/test_report.json` for detailed JSON results
- Inspect `test_output/ckg.db` for the SQLite database

## 🎯 Test Success Criteria

The test suite considers extraction successful when:

- ✅ **All test files are processed** without critical errors
- ✅ **Database is created** and contains extracted entities
- ✅ **Coverage threshold** is met (≥50% of expected entity types found per language)
- ✅ **Entity counts** are reasonable (>0 entities per language)
- ✅ **No critical parsing failures** occur

## 📝 Output Files

After running the comprehensive test, you'll find:

- `test_output/ckg.db` - SQLite database with extracted entities
- `test_output/test_report.json` - Detailed JSON report
- Console output with comprehensive analysis

## 🛠️ Customization

You can customize the test suite by:

- **Adding new languages**: Create test files and update `EXPECTED_ENTITIES`
- **Modifying thresholds**: Adjust coverage requirements in the validation logic
- **Adding entity types**: Extend the expected entities for existing languages
- **Custom output formats**: Modify the reporting functions

## 📋 Requirements

- Python 3.7+
- SQLite3
- CKG tool components (`run.py`, `ckg/` directory)
- Test files in the `test/` directory

---

This comprehensive test suite ensures that the CKG system properly extracts and catalogs all structural elements from source code across 21 different programming languages, providing confidence that the code knowledge graph accurately represents the codebase structure.
