# APA Report Generation System - Quick Start Guide

## Overview

The APA Report Generation System automatically creates publication-ready meta-analysis reports formatted according to APA 7th Edition guidelines. Generate professional Word and PDF documents with a single API call.

## Features

- **APA 7th Edition Formatting**: Complete compliance with APA formatting rules
- **Multiple Formats**: Word (.docx) and PDF export
- **Auto-Generated Content**: Abstracts, methods, results, and discussion sections
- **Custom Sections**: Override any section with your own content
- **Visualizations**: Automatic forest plots and funnel plots
- **Citation Management**: Auto-formatted references in APA style
- **Template System**: Create reusable report templates

## Quick Start

### 1. Install Dependencies

```bash
pip install python-docx reportlab Pillow matplotlib
```

### 2. Generate Your First Report

#### Using Python

```python
from app.services.apa_report_generator import APAReportGenerator

# Initialize generator
generator = APAReportGenerator()

# Your analysis data
analysis_data = {
    "id": "my-analysis",
    "title": "Effects of X on Y: A Meta-Analysis",
    "num_studies": 10,
    "pooled_effect_size": 0.5,
    "ci_lower": 0.3,
    "ci_upper": 0.7,
    "studies": [...]
}

# Generate report
result = generator.generate_report(
    analysis_data=analysis_data,
    format="both"  # Creates both Word and PDF
)

print(f"Word: {result['docx_path']}")
print(f"PDF: {result['pdf_path']}")
```

#### Using API

```bash
curl -X POST "http://localhost:8000/api/v1/meta-analysis/generate-report/analysis-123" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "both",
    "title": "My Meta-Analysis",
    "authors": ["Smith, J. D.", "Jones, A. B."],
    "institution": "University Name"
  }'
```

### 3. Download Generated Report

```bash
# Download Word document
curl -O "http://localhost:8000/api/v1/meta-analysis/report/1/download?format=docx"

# Download PDF
curl -O "http://localhost:8000/api/v1/meta-analysis/report/1/download?format=pdf"
```

## Example Usage

### Run the Example Script

```bash
cd backend
python examples/generate_sample_report.py
```

This will create:
- Sample Word document with APA formatting
- Sample PDF document
- Forest plot visualization
- Funnel plot visualization

Output will be in `backend/examples/sample_reports/`

## Report Structure

Generated reports include:

1. **Title Page**
   - Running head
   - Title (centered, bold)
   - Authors
   - Institution
   - Author note (optional)

2. **Abstract**
   - 250 words max
   - Keywords

3. **Introduction**
   - Background
   - Research question
   - Literature review

4. **Methods**
   - Search strategy
   - Inclusion/exclusion criteria
   - Statistical analysis

5. **Results**
   - Study selection (PRISMA flow)
   - Study characteristics table
   - Meta-analysis results
   - Forest plot reference

6. **Discussion**
   - Main findings
   - Limitations
   - Conclusions

7. **References**
   - APA-formatted citations
   - Alphabetically ordered
   - Hanging indent

## Customization

### Custom Sections

Override auto-generated content:

```python
custom_sections = {
    "abstract": "Your custom abstract text here...",
    "introduction": "Your custom introduction...",
    "discussion": "Your custom discussion..."
}

result = generator.generate_report(
    analysis_data=analysis_data,
    format="docx",
    custom_sections=custom_sections
)
```

### Author Information

```python
analysis_data = {
    "authors": ["Smith, John D.", "Jones, Alice B."],
    "institution": "Department of Psychology, University Name",
    "author_note": """
        Correspondence: john.smith@university.edu
        Funding: Grant R01-XY123456
    """
}
```

### Keywords

```python
analysis_data = {
    "keywords": [
        "meta-analysis",
        "mindfulness",
        "anxiety",
        "randomized controlled trial"
    ]
}
```

## API Endpoints

### Generate Report

**POST** `/api/v1/meta-analysis/generate-report/{analysis_id}`

Request body:
```json
{
  "format": "both",
  "title": "Report Title",
  "authors": ["Author 1", "Author 2"],
  "institution": "Institution Name",
  "keywords": ["keyword1", "keyword2"],
  "custom_sections": {
    "abstract": "Custom abstract..."
  }
}
```

### Get Report

**GET** `/api/v1/meta-analysis/report/{report_id}`

Returns report metadata including file paths and generation status.

### Download Report

**GET** `/api/v1/meta-analysis/report/{report_id}/download?format=docx`

Downloads the generated file.

### Customize Report

**POST** `/api/v1/meta-analysis/report/{report_id}/customize`

Update and regenerate an existing report.

### List Reports

**GET** `/api/v1/meta-analysis/reports/analysis/{analysis_id}`

List all reports for a specific analysis.

## Analysis Data Format

Required fields:

```python
{
    "id": "unique-id",
    "title": "Report Title",
    "num_studies": 10,
    "pooled_effect_size": 0.5,
    "studies": [
        {
            "authors": ["Author, A."],
            "year": 2020,
            "title": "Study Title",
            "journal": "Journal Name",
            "effect_size": 0.5,
            "ci_lower": 0.3,
            "ci_upper": 0.7
        }
    ]
}
```

Optional fields for richer reports:

```python
{
    "ci_lower": 0.3,
    "ci_upper": 0.7,
    "p_value": 0.001,
    "i_squared": 42.3,
    "databases": ["PubMed", "PsycINFO"],
    "search_terms": ["term1", "term2"],
    "inclusion_criteria": ["criterion 1", "criterion 2"],
    "exclusion_criteria": ["criterion 1", "criterion 2"],
    "limitations": ["limitation 1", "limitation 2"]
}
```

## Visualizations

### Forest Plot

```python
forest_path = generator.generate_forest_plot(
    studies=[
        {
            "authors": ["Smith"],
            "effect_size": 0.5,
            "ci_lower": 0.3,
            "ci_upper": 0.7
        }
    ]
)
```

### Funnel Plot

```python
funnel_path = generator.generate_funnel_plot(
    studies=[
        {
            "effect_size": 0.5,
            "standard_error": 0.1
        }
    ]
)
```

## Templates

### Create Template

```bash
curl -X POST "http://localhost:8000/api/v1/report-templates" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clinical Psychology Report",
    "description": "Template for clinical meta-analyses",
    "sections": {
      "include_author_note": true,
      "include_acknowledgments": true
    },
    "is_public": true
  }'
```

### List Templates

```bash
curl "http://localhost:8000/api/v1/report-templates?public_only=true"
```

## Database Migration

Apply the migration to create report tables:

```bash
cd backend
alembic upgrade head
```

This creates:
- `reports` table
- `report_templates` table
- Associated indexes

## Testing

Run the test suite:

```bash
pytest tests/test_report_generation.py -v
```

Test coverage:
- Citation formatting
- Document generation
- API endpoints
- Visualizations
- Edge cases

## Troubleshooting

### Import Error: No module named 'docx'

```bash
pip install python-docx
```

### PDF Generation Fails

Ensure ReportLab is installed:
```bash
pip install reportlab
```

### Font Not Found

The system uses Times New Roman by default. On systems without this font, edit `APAFormatConfig.FONT_NAME` in `apa_report_generator.py`.

### Large Reports Timeout

Use background tasks:
```python
background_tasks.add_task(generate_report, analysis_id)
```

## Advanced Usage

### Background Generation

```python
from fastapi import BackgroundTasks

@router.post("/generate")
async def generate(background_tasks: BackgroundTasks):
    background_tasks.add_task(
        generator.generate_report,
        analysis_data,
        "both"
    )
    return {"status": "generating"}
```

### Custom Output Directory

```python
from pathlib import Path

generator = APAReportGenerator(
    output_dir=Path("/custom/path")
)
```

### Batch Generation

```python
for analysis in analyses:
    generator.generate_report(
        analysis_data=analysis,
        format="pdf"
    )
```

## File Locations

```
backend/
├── app/
│   ├── services/
│   │   └── apa_report_generator.py  # Main generator
│   ├── models/
│   │   └── report.py                # Database models
│   └── api/v1/
│       └── reports.py               # API endpoints
├── tests/
│   └── test_report_generation.py    # Test suite
├── examples/
│   └── generate_sample_report.py    # Example script
├── docs/
│   └── APA_REPORT_GENERATION.md    # Full documentation
└── alembic/versions/
    └── 005_add_report_tables.py    # Database migration
```

## Configuration

### APA Format Settings

Edit `APAFormatConfig` class:

```python
class APAFormatConfig:
    FONT_NAME = "Times New Roman"
    FONT_SIZE = 12
    LINE_SPACING = 2.0
    MARGIN_INCHES = 1.0
    ABSTRACT_MAX_WORDS = 250
    INCLUDE_RUNNING_HEAD = True
    INCLUDE_PAGE_NUMBERS = True
```

## Best Practices

1. **Data Quality**: Ensure complete study metadata for accurate citations
2. **Review**: Always review auto-generated content before publication
3. **Customization**: Use custom sections for unique requirements
4. **Formats**: Use Word for editing, PDF for distribution
5. **Templates**: Create templates for recurring report types

## Support

- **Documentation**: `/docs/APA_REPORT_GENERATION.md`
- **API Docs**: `http://localhost:8000/docs`
- **Examples**: `backend/examples/`
- **Tests**: `backend/tests/test_report_generation.py`

## Next Steps

1. Run the example script to see the system in action
2. Review the full documentation in `docs/APA_REPORT_GENERATION.md`
3. Integrate with your meta-analysis workflow
4. Customize templates for your needs
5. Explore API endpoints in Swagger UI (`/docs`)

## Contributing

To add features or fix bugs:

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Submit a pull request

## License

[Your license here]
