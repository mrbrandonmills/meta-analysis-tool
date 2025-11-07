#!/bin/bash
#
# Install APA Report Generation dependencies
#

echo "============================================================"
echo "Installing APA Report Generation System Dependencies"
echo "============================================================"
echo ""

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found. Please run from the backend directory."
    exit 1
fi

# Install the new dependencies
echo "Installing document generation libraries..."
pip install python-docx==1.1.0
pip install reportlab==4.0.7
pip install Pillow==10.1.0

echo ""
echo "============================================================"
echo "Installation Complete"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Apply database migration: alembic upgrade head"
echo "  2. Verify installation: python verify_report_system.py"
echo "  3. Run example: python examples/generate_sample_report.py"
echo ""
