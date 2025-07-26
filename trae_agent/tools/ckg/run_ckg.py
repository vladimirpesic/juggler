"""
CKG Command Line Interface

This script provides a command-line interface to build Code Knowledge Graph (CKG) databases
from codebases and extract entities into SQLite databases.

Usage:
    python run.py --input-dir <input_directory> --output-dir <output_directory> --database-name <db_name>
"""

import argparse
import shutil
import sqlite3
import sys
from pathlib import Path

from ckg_database import CKGDatabase


def create_custom_database(input_dir: Path, output_dir: Path, database_name: str) -> bool:
    """
    Create a CKG database in a custom location.

    Args:
        input_dir: Directory containing source code to analyze
        output_dir: Directory where to place the output database
        database_name: Name of the database file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure input directory exists
        if not input_dir.exists():
            print(f"Error: Input directory does not exist: {input_dir}")
            return False

        if not input_dir.is_dir():
            print(f"Error: Input path is not a directory: {input_dir}")
            return False

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Path for the final database
        target_db_path = output_dir / database_name

        # Remove existing database if it exists
        if target_db_path.exists():
            target_db_path.unlink()
            print(f"Removed existing database: {target_db_path}")

        print(f"Building CKG database for: {input_dir}")
        print(f"Output location: {target_db_path}")

        # Create the CKG database (this will be stored in ~/.ckg/ckg/ initially)
        ckg_db = CKGDatabase(input_dir)  # noqa: F841

        # Find the generated database file
        # The CKGDatabase stores files in ~/.ckg/ckg/ with hash-based names
        from ckg.ckg_database import get_ckg_database_path, get_folder_snapshot_hash

        snapshot_hash = get_folder_snapshot_hash(input_dir)
        source_db_path = get_ckg_database_path(snapshot_hash)

        if not source_db_path.exists():
            print(f"Error: Expected database not found at: {source_db_path}")
            return False

        # Copy the database to the desired location
        shutil.copy2(source_db_path, target_db_path)
        print(f"Database copied to: {target_db_path}")

        # Verify the database was created and has content
        conn = sqlite3.connect(target_db_path)
        cursor = conn.cursor()

        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("Warning: Database created but contains no tables")
            conn.close()
            return False

        # Count total entities
        total_entities = 0
        table_counts = {}

        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_counts[table] = count
                total_entities += count
            except sqlite3.Error as e:
                print(f"Warning: Could not count entries in table {table}: {e}")

        conn.close()

        print("\nDatabase creation successful!")
        print(f"Tables created: {len(tables)}")
        for table, count in table_counts.items():
            print(f"  - {table}: {count} entries")
        print(f"Total entities: {total_entities}")

        return True

    except Exception as e:
        print(f"Error during database creation: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main entry point for the CKG CLI."""
    parser = argparse.ArgumentParser(
        description="Build Code Knowledge Graph (CKG) database from source code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input-dir ./src --output-dir ./output --database-name ckg.db
  %(prog)s --input-dir /path/to/code --output-dir /path/to/output --database-name project.db
        """,
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing source code to analyze",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where to place the output database",
    )

    parser.add_argument(
        "--database-name",
        type=str,
        required=True,
        help="Name of the database file (e.g., ckg.db)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        print(f"Input directory: {args.input_dir}")
        print(f"Output directory: {args.output_dir}")
        print(f"Database name: {args.database_name}")

    # Build the database
    success = create_custom_database(args.input_dir, args.output_dir, args.database_name)

    if success:
        print("\n✅ CKG database successfully created!")
        sys.exit(0)
    else:
        print("\n❌ Failed to create CKG database")
        sys.exit(1)


if __name__ == "__main__":
    main()
