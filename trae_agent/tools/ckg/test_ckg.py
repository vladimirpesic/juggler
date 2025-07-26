"""
CKG Test Script - Comprehensive Entity Extraction Verification

This script traverses through all test files in the 'test' directory and verifies that
all entities present in every file are properly extracted into the SQLite database.

The script performs the following operations:
1. Discovers all test files in the test directory
2. Maps file extensions to expected languages
3. Runs the CKG tool on the test directory
4. Analyzes the SQLite database to extract all entities
5. Generates detailed reports on entity extraction coverage
6. Validates that all expected structural elements are present
"""

import argparse
import json
import sqlite3
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

# Expected structural elements for each language
EXPECTED_ENTITIES = {
    "c": ["functions", "structs", "enums", "unions"],
    "cpp": ["functions", "classes", "structs", "enums", "namespaces", "unions"],
    "csharp": ["functions", "classes", "structs", "enums", "interfaces", "namespaces"],
    "dart": ["functions", "classes", "enums", "interfaces", "modules"],
    "elixir": ["functions", "modules"],
    "gleam": ["functions", "modules"],
    "go": ["functions", "structs", "interfaces", "modules"],
    "java": ["functions", "classes", "enums", "interfaces"],
    "javascript": ["functions", "classes", "components"],
    "kotlin": ["functions", "classes", "enums", "interfaces"],
    "php": ["functions", "classes", "enums", "interfaces", "traits"],
    "python": ["functions", "classes", "modules"],
    "ruby": ["functions", "classes", "modules"],
    "rust": ["functions", "structs", "enums", "traits", "modules"],
    "scala": ["functions", "classes", "traits"],
    "solidity": ["functions", "contracts", "structs", "enums", "interfaces"],
    "svelte": ["components", "functions"],
    "swift": ["functions", "classes", "structs", "enums", "interfaces", "extensions"],
    "typescript": [
        "functions",
        "classes",
        "enums",
        "interfaces",
        "namespaces",
        "type_aliases",
    ],
    "vue": ["components", "functions"],
    "zig": ["functions", "structs", "enums", "unions"],
}

# Extension to language mapping (should match ckg/base.py)
EXTENSION_TO_LANGUAGE = {
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


@dataclass
class TestFile:
    """Represents a test file to be analyzed"""

    path: Path
    extension: str
    language: str
    size: int


@dataclass
class EntityStats:
    """Statistics for a specific entity type"""

    count: int = 0
    files: Set[str] = field(default_factory=set)
    examples: List[str] = field(default_factory=list)


@dataclass
class LanguageReport:
    """Report for a specific language"""

    language: str
    files: List[TestFile]
    entities: Dict[str, EntityStats] = field(default_factory=dict)
    total_entities: int = 0
    coverage_score: float = 0.0


@dataclass
class TestReport:
    """Complete test report"""

    total_files: int
    languages: Dict[str, LanguageReport]
    database_path: str
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class CKGTester:
    """Main testing class for CKG entity extraction verification"""

    def __init__(self, test_dir: Path, output_dir: Path = None):  # type: ignore
        self.test_dir = test_dir
        self.output_dir = output_dir or Path("test_output")
        self.database_path = self.output_dir / "ckg.db"
        self.report = TestReport(
            total_files=0,
            languages={},
            database_path=str(self.database_path),
            success=False,
        )

    def discover_test_files(self) -> List[TestFile]:
        """Discover all test files in the test directory"""
        test_files = []

        if not self.test_dir.exists():
            raise FileNotFoundError(f"Test directory not found: {self.test_dir}")

        for file_path in self.test_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith("."):
                extension = file_path.suffix.lower()

                if extension in EXTENSION_TO_LANGUAGE:
                    language = EXTENSION_TO_LANGUAGE[extension]
                    size = file_path.stat().st_size

                    test_file = TestFile(
                        path=file_path,
                        extension=extension,
                        language=language,
                        size=size,
                    )
                    test_files.append(test_file)

        return sorted(test_files, key=lambda x: x.language)

    def run_ckg_tool(self) -> bool:
        """Run the CKG tool to generate the database"""
        try:
            # Ensure output directory exists
            self.output_dir.mkdir(exist_ok=True)

            # Remove existing database if it exists
            if self.database_path.exists():
                self.database_path.unlink()

            # Run the CKG tool
            cmd = [
                sys.executable,
                "run.py",
                "--input-dir",
                str(self.test_dir),
                "--output-dir",
                str(self.output_dir),
                "--database-name",
                "ckg.db",
            ]

            print(f"Running CKG tool: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                self.report.errors.append(f"CKG tool failed: {result.stderr}")
                return False

            if not self.database_path.exists():
                self.report.errors.append(f"Database not created: {self.database_path}")
                return False

            print(f"CKG tool completed successfully. Database: {self.database_path}")
            return True

        except subprocess.TimeoutExpired:
            self.report.errors.append("CKG tool timed out after 5 minutes")
            return False
        except Exception as e:
            self.report.errors.append(f"Error running CKG tool: {str(e)}")
            return False

    def analyze_database(self) -> Dict[str, Dict[str, List[Dict]]]:
        """Analyze the SQLite database and extract all entities"""
        entities = defaultdict(lambda: defaultdict(list))  # type: ignore

        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()

            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            print(f"Found database tables: {tables}")

            # Define table to entity type mapping
            table_mappings = {
                "functions": "functions",
                "classes": "classes",
                "structs": "structs",
                "enums": "enums",
                "interfaces": "interfaces",
                "traits": "traits",
                "modules": "modules",
                "namespaces": "namespaces",
                "type_aliases": "type_aliases",
                "components": "components",
                "contracts": "contracts",
                "extensions": "extensions",
                "unions": "unions",
                "generic_types": "generic_types",
            }

            # Extract entities from each table
            for table_name in tables:
                if table_name in table_mappings:
                    entity_type = table_mappings[table_name]

                    try:
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()

                        for row in rows:
                            row_dict = dict(row)
                            file_path = row_dict.get("file_path", "")

                            # Extract language from file path
                            if file_path:
                                file_path_obj = Path(file_path)
                                extension = file_path_obj.suffix.lower()
                                language = EXTENSION_TO_LANGUAGE.get(extension, "unknown")

                                entities[language][entity_type].append(row_dict)

                    except sqlite3.Error as e:
                        self.report.warnings.append(f"Error querying table {table_name}: {str(e)}")

            conn.close()
            return entities  # type: ignore

        except sqlite3.Error as e:
            self.report.errors.append(f"Database analysis error: {str(e)}")
            return {}

    def generate_language_reports(
        self, test_files: List[TestFile], entities: Dict[str, Dict[str, List[Dict]]]
    ) -> None:
        """Generate detailed reports for each language"""

        # Group test files by language
        files_by_language = defaultdict(list)
        for test_file in test_files:
            files_by_language[test_file.language].append(test_file)

        # Generate report for each language
        for language, files in files_by_language.items():
            language_entities = entities.get(language, {})

            report = LanguageReport(language=language, files=files)

            # Calculate entity statistics
            total_entities = 0
            expected_entity_types = EXPECTED_ENTITIES.get(language, [])

            for entity_type in expected_entity_types:
                entity_list = language_entities.get(entity_type, [])
                entity_count = len(entity_list)
                total_entities += entity_count

                # Get unique files for this entity type
                entity_files = set()
                examples = []

                for entity in entity_list[:5]:  # Limit examples to 5
                    file_path = entity.get("file_path", "")
                    if file_path:
                        entity_files.add(Path(file_path).name)

                    entity_name = entity.get("name", "unnamed")
                    examples.append(entity_name)

                report.entities[entity_type] = EntityStats(
                    count=entity_count, files=entity_files, examples=examples
                )

            # Calculate coverage score
            found_entity_types = len(
                [
                    et
                    for et in expected_entity_types
                    if et in language_entities and language_entities[et]
                ]
            )
            expected_entity_types_count = len(expected_entity_types)

            if expected_entity_types_count > 0:
                report.coverage_score = (found_entity_types / expected_entity_types_count) * 100

            report.total_entities = total_entities
            self.report.languages[language] = report

    def print_summary_report(self) -> None:
        """Print a comprehensive summary report"""
        print("\n" + "=" * 80)
        print("CKG ENTITY EXTRACTION TEST REPORT")
        print("=" * 80)

        print(f"\nDatabase Path: {self.report.database_path}")
        print(f"Total Test Files: {self.report.total_files}")
        print(f"Languages Tested: {len(self.report.languages)}")

        if self.report.errors:
            print(f"\n❌ ERRORS ({len(self.report.errors)}):")
            for error in self.report.errors:
                print(f"  - {error}")

        if self.report.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.report.warnings)}):")
            for warning in self.report.warnings:
                print(f"  - {warning}")

        print("\n📊 LANGUAGE COVERAGE SUMMARY:")
        print("-" * 80)

        total_entities = 0
        languages_sorted = sorted(
            self.report.languages.items(),
            key=lambda x: x[1].coverage_score,
            reverse=True,
        )

        for language, lang_report in languages_sorted:
            total_entities += lang_report.total_entities
            status_icon = (
                "✅"
                if lang_report.coverage_score >= 80
                else "⚠️"
                if lang_report.coverage_score >= 50
                else "❌"
            )

            print(
                f"{status_icon} {language.upper():12} | "
                f"Files: {len(lang_report.files):2} | "
                f"Entities: {lang_report.total_entities:4} | "
                f"Coverage: {lang_report.coverage_score:5.1f}%"
            )

        print("-" * 80)
        print(f"TOTAL ENTITIES EXTRACTED: {total_entities}")

        # Detailed language reports
        print("\n📋 DETAILED LANGUAGE REPORTS:")
        print("=" * 80)

        for language, lang_report in languages_sorted:
            self.print_language_report(language, lang_report)

    def print_language_report(self, language: str, report: LanguageReport) -> None:
        """Print detailed report for a specific language"""
        print(f"\n🔍 {language.upper()} DETAILED REPORT")
        print("-" * 60)

        print(f"Files ({len(report.files)}):")
        for file in report.files:
            print(f"  📄 {file.path.name} ({file.size:,} bytes)")

        expected_entities = EXPECTED_ENTITIES.get(language, [])
        print(f"\nExpected Entity Types: {', '.join(expected_entities)}")

        print("\nEntity Extraction Results:")
        for entity_type in expected_entities:
            stats = report.entities.get(entity_type, EntityStats())
            status_icon = "✅" if stats.count > 0 else "❌"

            print(
                f"  {status_icon} {entity_type:15} | Count: {stats.count:3} | "
                f"Files: {len(stats.files)} | Examples: {', '.join(stats.examples[:3])}"
            )

        # Additional entities found (not in expected list)
        additional_entities = set(report.entities.keys()) - set(expected_entities)
        if additional_entities:
            print("\nAdditional Entities Found:")
            for entity_type in sorted(additional_entities):
                stats = report.entities[entity_type]
                print(f"  ➕ {entity_type:15} | Count: {stats.count:3}")

    def save_json_report(self) -> None:
        """Save detailed report as JSON"""
        json_path = self.output_dir / "test_report.json"

        # Convert report to JSON-serializable format
        json_data = {
            "summary": {
                "total_files": self.report.total_files,
                "database_path": self.report.database_path,
                "success": self.report.success,
                "errors": self.report.errors,
                "warnings": self.report.warnings,
            },
            "languages": {},
        }

        for language, lang_report in self.report.languages.items():
            json_data["languages"][language] = {
                "files": [
                    {"path": str(f.path), "extension": f.extension, "size": f.size}
                    for f in lang_report.files
                ],
                "total_entities": lang_report.total_entities,
                "coverage_score": lang_report.coverage_score,
                "entities": {
                    entity_type: {
                        "count": stats.count,
                        "files": list(stats.files),
                        "examples": stats.examples,
                    }
                    for entity_type, stats in lang_report.entities.items()
                },
            }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Detailed JSON report saved: {json_path}")

    def validate_extraction_completeness(self) -> bool:
        """Validate that extraction is reasonably complete"""
        issues = []

        for language, lang_report in self.report.languages.items():
            if lang_report.coverage_score < 50:
                issues.append(f"Low coverage for {language}: {lang_report.coverage_score:.1f}%")

            if lang_report.total_entities == 0:
                issues.append(f"No entities extracted for {language}")

        if issues:
            print("\n⚠️  VALIDATION ISSUES:")
            for issue in issues:
                print(f"  - {issue}")
            self.report.warnings.extend(issues)
            return False

        return True

    def run_comprehensive_test(self) -> bool:
        """Run the complete test suite"""
        try:
            print("Starting CKG comprehensive test suite...")

            # 1. Discover test files
            print("\n1. Discovering test files...")
            test_files = self.discover_test_files()
            self.report.total_files = len(test_files)

            print(f"Found {len(test_files)} test files:")
            for test_file in test_files:
                print(f"  - {test_file.path.name} ({test_file.language})")

            # 2. Run CKG tool
            print("\n2. Running CKG tool...")
            if not self.run_ckg_tool():
                return False

            # 3. Analyze database
            print("\n3. Analyzing database...")
            entities = self.analyze_database()

            if not entities:
                self.report.errors.append("No entities found in database")
                return False

            # 4. Generate reports
            print("\n4. Generating reports...")
            self.generate_language_reports(test_files, entities)

            # 5. Validate completeness
            print("\n5. Validating extraction completeness...")
            validation_success = self.validate_extraction_completeness()

            # 6. Print summary and save reports
            self.print_summary_report()
            self.save_json_report()

            # Determine overall success
            has_critical_errors = any(
                "failed" in error.lower() or "not created" in error.lower()
                for error in self.report.errors
            )
            self.report.success = not has_critical_errors and validation_success

            if self.report.success:
                print("\n🎉 TEST SUITE COMPLETED SUCCESSFULLY!")
                print(
                    f"   Total entities extracted: {sum(lr.total_entities for lr in self.report.languages.values())}"
                )
                print(
                    f"   Average coverage: {sum(lr.coverage_score for lr in self.report.languages.values()) / len(self.report.languages):.1f}%"
                )
            else:
                print("\n❌ TEST SUITE COMPLETED WITH ISSUES")
                print("   Check errors and warnings above")

            return self.report.success

        except Exception as e:
            self.report.errors.append(f"Unexpected error: {str(e)}")
            print(f"\n💥 FATAL ERROR: {str(e)}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CKG Entity Extraction Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Run tests with default settings
  %(prog)s --test-dir /path/to/test  # Specify test directory  
  %(prog)s --output-dir ./results    # Specify output directory
  %(prog)s --verbose                 # Enable verbose output
        """,
    )

    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("test"),
        help="Directory containing test files (default: ./test)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("test_output"),
        help="Output directory for results (default: ./test_output)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Run the comprehensive test
    tester = CKGTester(args.test_dir, args.output_dir)
    success = tester.run_comprehensive_test()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
