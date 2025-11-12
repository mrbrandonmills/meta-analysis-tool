#!/usr/bin/env python3
"""
Run Alembic migrations against Railway production database
"""
import subprocess
import sys
import os

def main():
    print("🚀 Running migrations against Railway production database...")
    print("=" * 80)

    # Change to backend directory where alembic.ini is located
    os.chdir("/Users/brandon/meta-analysis-tool/backend")

    # Run Alembic migrations using Railway's environment
    print("\n🔧 Running Alembic migrations with Railway environment...")
    result = subprocess.run(
        "railway run bash -c 'cd /app/backend && alembic upgrade head'",
        shell=True,
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode == 0:
        print("\n✅ Migrations completed successfully!")
        return 0
    else:
        print(f"\n❌ Migrations failed with exit code {result.returncode}")
        return result.returncode

if __name__ == "__main__":
    sys.exit(main())
