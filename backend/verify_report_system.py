#!/usr/bin/env python3
"""Verification script for APA Report Generation System.

This script verifies that all components are properly installed and working.
Run this after installation to ensure the system is ready for production.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text: str):
    """Print a formatted header."""
    print()
    print("=" * 80)
    print(f"{BOLD}{text}{RESET}")
    print("=" * 80)


def print_success(text: str):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{RED}✗{RESET} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {text}")


def check_dependencies() -> List[Tuple[str, bool, str]]:
    """Check if required dependencies are installed."""
    results = []

    dependencies = [
        ("docx", "python-docx"),
        ("reportlab", "reportlab"),
        ("PIL", "Pillow"),
        ("matplotlib", "matplotlib"),
        ("fastapi", "fastapi"),
        ("sqlalchemy", "sqlalchemy"),
        ("pydantic", "pydantic"),
        ("loguru", "loguru"),
    ]

    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            results.append((package_name, True, "Installed"))
        except ImportError:
            results.append((package_name, False, f"Missing - install with: pip install {package_name}"))

    return results


def check_files() -> List[Tuple[str, bool, str]]:
    """Check if required files exist."""
    results = []

    files = [
        ("app/services/apa_report_generator.py", "Main service"),
        ("app/models/report.py", "Database models"),
        ("app/api/v1/reports.py", "API endpoints"),
        ("tests/test_report_generation.py", "Test suite"),
        ("docs/APA_REPORT_GENERATION.md", "Documentation"),
        ("examples/generate_sample_report.py", "Example script"),
        ("alembic/versions/005_add_report_tables.py", "Database migration"),
    ]

    for file_path, description in files:
        full_path = Path(__file__).parent / file_path
        exists = full_path.exists()
        results.append((file_path, exists, description))

    return results


def check_imports() -> List[Tuple[str, bool, str]]:
    """Check if components can be imported."""
    results = []

    try:
        from app.services.apa_report_generator import APAReportGenerator, APACitationFormatter
        results.append(("APAReportGenerator", True, "Service class"))
        results.append(("APACitationFormatter", True, "Citation formatter"))
    except ImportError as e:
        results.append(("Services", False, f"Import error: {e}"))

    try:
        from app.models.report import Report, ReportTemplate, ReportFormat, ReportStatus
        results.append(("Report models", True, "Database models"))
    except ImportError as e:
        results.append(("Models", False, f"Import error: {e}"))

    try:
        from app.api.v1 import reports
        results.append(("Report API", True, "API endpoints"))
    except ImportError as e:
        results.append(("API", False, f"Import error: {e}"))

    return results


def test_basic_functionality() -> List[Tuple[str, bool, str]]:
    """Test basic functionality."""
    results = []

    try:
        from app.services.apa_report_generator import APAReportGenerator, APACitationFormatter
        import tempfile

        # Test citation formatter
        formatter = APACitationFormatter()
        citation = formatter.format_journal_article(
            authors=["Smith, J."],
            year=2020,
            title="Test",
            journal="Journal"
        )
        if "Smith, J." in citation and "2020" in citation:
            results.append(("Citation formatting", True, "Working"))
        else:
            results.append(("Citation formatting", False, "Output incorrect"))

        # Test generator initialization
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = APAReportGenerator(output_dir=Path(tmpdir))
            results.append(("Generator initialization", True, "Working"))

            # Test abstract generation
            abstract = generator._generate_abstract({
                "research_question": "test",
                "num_studies": 10,
                "num_participants": 100,
                "pooled_effect_size": 0.5,
                "ci_lower": 0.3,
                "ci_upper": 0.7
            })
            if len(abstract) > 0:
                results.append(("Abstract generation", True, "Working"))
            else:
                results.append(("Abstract generation", False, "Empty output"))

    except Exception as e:
        results.append(("Functionality tests", False, f"Error: {e}"))

    return results


def main():
    """Run all verification checks."""
    print_header("APA REPORT GENERATION SYSTEM - VERIFICATION")

    all_passed = True

    # Check dependencies
    print_header("Checking Dependencies")
    dep_results = check_dependencies()
    for package, success, message in dep_results:
        if success:
            print_success(f"{package}: {message}")
        else:
            print_error(f"{package}: {message}")
            all_passed = False

    # Check files
    print_header("Checking Files")
    file_results = check_files()
    for file_path, exists, description in file_results:
        if exists:
            print_success(f"{file_path} ({description})")
        else:
            print_error(f"{file_path} - MISSING ({description})")
            all_passed = False

    # Check imports
    print_header("Checking Imports")
    import_results = check_imports()
    for component, success, message in import_results:
        if success:
            print_success(f"{component}: {message}")
        else:
            print_error(f"{component}: {message}")
            all_passed = False

    # Test functionality
    print_header("Testing Basic Functionality")
    func_results = test_basic_functionality()
    for test_name, success, message in func_results:
        if success:
            print_success(f"{test_name}: {message}")
        else:
            print_error(f"{test_name}: {message}")
            all_passed = False

    # Summary
    print_header("Verification Summary")

    if all_passed:
        print()
        print(f"{GREEN}{BOLD}✓ ALL CHECKS PASSED{RESET}")
        print()
        print("The APA Report Generation System is properly installed and ready to use.")
        print()
        print("Next steps:")
        print("  1. Apply database migration: alembic upgrade head")
        print("  2. Run example script: python examples/generate_sample_report.py")
        print("  3. Run tests: pytest tests/test_report_generation.py -v")
        print("  4. Start server: uvicorn app.main:app --reload")
        print("  5. View API docs: http://localhost:8000/docs")
        print()
        return 0
    else:
        print()
        print(f"{RED}{BOLD}✗ SOME CHECKS FAILED{RESET}")
        print()
        print("Please fix the errors above before using the system.")
        print()
        print("Common fixes:")
        print("  - Install missing dependencies: pip install -r requirements.txt")
        print("  - Ensure you're in the backend directory")
        print("  - Check Python version (3.9+ required)")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
