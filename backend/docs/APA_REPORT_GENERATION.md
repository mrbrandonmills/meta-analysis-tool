# APA Report Generation System

## Overview

The APA Report Generation System provides comprehensive, publication-ready reports for meta-analysis results, formatted according to APA 7th Edition guidelines. The system supports both Word (.docx) and PDF exports with full customization capabilities.

## Features

### 1. APA 7th Edition Formatting
- **Font**: Times New Roman, 12pt
- **Spacing**: Double spacing throughout
- **Margins**: 1-inch margins on all sides
- **Headers**: Running head with page numbers
- **Sections**: Complete APA structure (Title Page, Abstract, Introduction, Methods, Results, Discussion, References)

### 2. Document Formats
- **Word (.docx)**: Fully editable Microsoft Word documents
- **PDF**: Publication-ready PDF documents
- **Both**: Generate both formats simultaneously

### 3. Auto-Generated Content
- Abstract (auto-generated from analysis data, max 250 words)
- Study characteristics tables
- References section (APA-formatted citations)
- Forest plots and funnel plots
- Statistical summaries

### 4. Customization Options
- Custom section content
- Author information
- Institution details
- Keywords
- Acknowledgments
- Templates for different report types

## Architecture

```
app/
├── services/
│   └── apa_report_generator.py    # Main report generation service
├── models/
│   └── report.py                  # Database models for reports
├── api/v1/
│   └── reports.py                 # API endpoints
└── templates/                     # Report templates (future)
```

## Core Components

### APAReportGenerator

Main class for generating APA-formatted reports.

```python
from app.services.apa_report_generator import APAReportGenerator

generator = APAReportGenerator(output_dir="/path/to/output")

result = generator.generate_report(
    analysis_data={
        "id": "analysis-123",
        "title": "Effects of Mindfulness on Anxiety: A Meta-Analysis",
        "authors": ["Smith, J. D.", "Jones, A. B."],
        "institution": "University Name",
        # ... more analysis data
    },
    format="both",  # or "docx" or "pdf"
    custom_sections={
        "abstract": "Custom abstract text...",
        "introduction": "Custom introduction text..."
    }
)

print(result)
# {
#     "docx_path": "/path/to/output/report_123_20240115.docx",
#     "pdf_path": "/path/to/output/report_123_20240115.pdf",
#     "generated_at": "2024-01-15T10:30:00"
# }
```

### APACitationFormatter

Handles APA-style citation formatting.

```python
from app.services.apa_report_generator import APACitationFormatter

formatter = APACitationFormatter()

# Journal article citation
citation = formatter.format_journal_article(
    authors=["Hofmann, S. G.", "Sawyer, A. T.", "Witt, A. A."],
    year=2010,
    title="The effect of mindfulness-based therapy on anxiety and depression",
    journal="Journal of Consulting and Clinical Psychology",
    volume=78,
    issue=2,
    pages="169-183",
    doi="10.1037/a0018555"
)

print(citation)
# Hofmann, S. G., Sawyer, A. T., & Witt, A. A. (2010). The effect of
# mindfulness-based therapy on anxiety and depression. Journal of Consulting
# and Clinical Psychology, 78(2), 169-183. https://doi.org/10.1037/a0018555

# In-text citation
in_text = formatter.format_in_text_citation(["Hofmann", "Sawyer", "Witt"], 2010)
print(in_text)
# (Hofmann et al., 2010)
```

### Visualization Generation

Generate forest plots and funnel plots:

```python
# Forest plot
forest_path = generator.generate_forest_plot(
    studies=[
        {
            "authors": ["Smith, J."],
            "effect_size": 0.5,
            "ci_lower": 0.3,
            "ci_upper": 0.7
        },
        # ... more studies
    ]
)

# Funnel plot (for publication bias assessment)
funnel_path = generator.generate_funnel_plot(
    studies=[
        {
            "effect_size": 0.5,
            "standard_error": 0.1
        },
        # ... more studies
    ]
)
```

## API Endpoints

### Generate Report

**POST** `/api/v1/meta-analysis/generate-report/{analysis_id}`

Generate a new report for a meta-analysis.

```json
{
  "format": "both",
  "title": "Effects of Mindfulness on Anxiety: A Meta-Analysis",
  "authors": ["Smith, J. D.", "Jones, A. B."],
  "institution": "University Name",
  "author_note": "Correspondence concerning this article should be addressed to...",
  "keywords": ["meta-analysis", "mindfulness", "anxiety", "RCT"],
  "custom_sections": {
    "abstract": "Custom abstract text...",
    "introduction": "Custom introduction text...",
    "discussion": "Custom discussion text..."
  }
}
```

Response:
```json
{
  "id": 1,
  "analysis_id": "analysis-123",
  "title": "Effects of Mindfulness on Anxiety: A Meta-Analysis",
  "format": "both",
  "status": "completed",
  "docx_path": "/tmp/reports/report_123_20240115.docx",
  "pdf_path": "/tmp/reports/report_123_20240115.pdf",
  "generated_at": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:29:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Download Report

**GET** `/api/v1/meta-analysis/report/{report_id}/download?format=docx`

Download a generated report file.

Query Parameters:
- `format`: File format to download (`docx` or `pdf`)

Returns: File download

### Customize Report

**POST** `/api/v1/meta-analysis/report/{report_id}/customize`

Customize and regenerate an existing report.

```json
{
  "title": "Updated Title",
  "authors": ["Smith, J. D.", "Jones, A. B.", "Brown, K. L."],
  "custom_sections": {
    "abstract": "Revised abstract text..."
  }
}
```

### List Reports

**GET** `/api/v1/meta-analysis/reports/analysis/{analysis_id}`

List all reports for a specific analysis.

### Template Management

**POST** `/api/v1/report-templates`

Create a new report template.

```json
{
  "name": "Clinical Psychology Report",
  "description": "Template for clinical psychology meta-analyses",
  "sections": {
    "include_author_note": true,
    "include_acknowledgments": true,
    "discussion_subsections": ["Clinical Implications", "Future Research"]
  },
  "style_config": {
    "include_running_head": true,
    "include_page_numbers": true
  },
  "is_public": true
}
```

**GET** `/api/v1/report-templates`

List available templates.

**GET** `/api/v1/report-templates/{template_id}`

Get a specific template.

**DELETE** `/api/v1/report-templates/{template_id}`

Delete a template.

## Report Structure

### 1. Title Page
- Running head (first 50 characters of title, uppercase)
- Full title (bold, centered)
- Author names (centered)
- Institution (centered)
- Author note (optional)

### 2. Abstract
- "Abstract" heading (bold, centered)
- Abstract text (250 words max)
- Keywords (italic label)

### 3. Introduction
- "Introduction" heading (bold, centered)
- Background and context
- Research question subsection
- Literature review

### 4. Methods
- "Methods" heading (bold, centered)
- Search Strategy subsection
  - Databases searched
  - Search terms used
  - Search date
- Inclusion and Exclusion Criteria subsection
  - Bulleted list of inclusion criteria
  - Bulleted list of exclusion criteria
- Statistical Analysis subsection
  - Analysis method (e.g., random-effects model)
  - Effect size measure
  - Heterogeneity assessment
  - Publication bias evaluation

### 5. Results
- "Results" heading (bold, centered)
- Study Selection subsection
  - Number of records identified
  - Screening process
  - Final number included
- Study Characteristics subsection
  - Table 1: Characteristics of Included Studies
- Meta-Analysis Results subsection
  - Pooled effect size with confidence interval
  - Heterogeneity statistics
  - Reference to forest plot (Figure 1)

### 6. Discussion
- "Discussion" heading (bold, centered)
- Main findings interpretation
- Limitations subsection
  - Bulleted list of study limitations
- Conclusions subsection
  - Summary of findings
  - Implications for practice and research

### 7. References
- "References" heading (bold, centered)
- APA-formatted citations (hanging indent)
- Alphabetically ordered by first author

## Customization Guide

### Custom Sections

Override auto-generated content with custom text:

```python
custom_sections = {
    "abstract": """
        This meta-analysis examined the effects of mindfulness-based
        interventions on anxiety levels in adult populations. A systematic
        search identified 25 randomized controlled trials with 1,847
        participants. Results showed a moderate effect size (d = 0.63,
        95% CI [0.48, 0.78], p < .001), indicating significant reductions
        in anxiety following mindfulness interventions.
    """,
    "introduction": """
        Anxiety disorders represent one of the most prevalent mental health
        conditions worldwide, affecting approximately 264 million people...
    """,
    "discussion": """
        The present meta-analysis provides strong evidence that mindfulness-based
        interventions significantly reduce anxiety symptoms in adult populations...
    """
}
```

### Author Information

```python
report_data = {
    "authors": [
        "Smith, John D.",
        "Jones, Alice B.",
        "Brown, Katherine L."
    ],
    "institution": "Department of Psychology, University Name",
    "author_note": """
        John D. Smith, Department of Psychology, University Name.

        This research was supported by Grant R01-MH123456 from the
        National Institute of Mental Health.

        Correspondence concerning this article should be addressed to
        John D. Smith, Department of Psychology, University Name,
        123 Main St, City, State 12345. Email: john.smith@university.edu
    """
}
```

### Keywords

```python
keywords = [
    "meta-analysis",
    "mindfulness",
    "anxiety",
    "randomized controlled trial",
    "systematic review"
]
```

## Analysis Data Format

The report generator expects analysis data in the following format:

```python
analysis_data = {
    # Basic Information
    "id": "analysis-123",
    "title": "Report Title",
    "topic": "research topic",
    "research_question": "What is the research question?",

    # Study Counts
    "num_studies": 25,
    "num_participants": 1847,
    "num_identified": 458,
    "num_screened": 156,

    # Effect Sizes and Statistics
    "pooled_effect_size": 0.63,
    "ci_lower": 0.48,
    "ci_upper": 0.78,
    "p_value": 0.001,
    "i_squared": 42.3,

    # Methods Information
    "year_range": "2010-2024",
    "search_date": "January 15, 2024",
    "databases": ["PubMed", "PsycINFO", "Web of Science"],
    "search_terms": ["mindfulness", "anxiety", "RCT"],
    "inclusion_criteria": [
        "Randomized controlled trials",
        "Adult participants (age 18+)",
        "Validated anxiety outcome measure"
    ],
    "exclusion_criteria": [
        "Non-English language",
        "Insufficient statistical data"
    ],
    "analysis_method": "random-effects model",

    # Report Metadata
    "authors": ["Smith, J. D.", "Jones, A. B."],
    "institution": "University Name",
    "keywords": ["meta-analysis", "mindfulness", "anxiety"],
    "limitations": [
        "Limited to English-language publications",
        "Moderate heterogeneity across studies"
    ],

    # Individual Studies
    "studies": [
        {
            "authors": ["Hofmann, S. G.", "Sawyer, A. T."],
            "year": 2010,
            "title": "The effect of mindfulness-based therapy",
            "journal": "Journal of Consulting and Clinical Psychology",
            "volume": 78,
            "issue": 2,
            "pages": "169-183",
            "doi": "10.1037/a0018555",
            "sample_size": 209,
            "design": "RCT",
            "effect_size": 0.59,
            "ci_lower": 0.23,
            "ci_upper": 0.95,
            "standard_error": 0.18,
            "quality_rating": "High"
        },
        # ... more studies
    ]
}
```

## Database Schema

### Report Model

```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY,
    analysis_id VARCHAR NOT NULL,
    title VARCHAR(500) NOT NULL,
    format VARCHAR(10) NOT NULL,  -- 'docx', 'pdf', 'both'
    status VARCHAR(20) NOT NULL,  -- 'pending', 'generating', 'completed', 'failed'
    authors JSON,
    institution VARCHAR(500),
    author_note TEXT,
    custom_sections JSON,
    keywords JSON,
    docx_path VARCHAR(1000),
    pdf_path VARCHAR(1000),
    num_studies INTEGER,
    pooled_effect_size VARCHAR(50),
    generated_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id)
);
```

### ReportTemplate Model

```sql
CREATE TABLE report_templates (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    sections JSON NOT NULL,
    style_config JSON,
    is_public INTEGER DEFAULT 0,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing

Run the test suite:

```bash
pytest tests/test_report_generation.py -v
```

Test coverage includes:
- Citation formatting (all APA rules)
- Document generation (Word and PDF)
- Visualization generation (forest and funnel plots)
- API endpoints
- Edge cases and error handling

## Best Practices

### 1. Data Quality
- Ensure all required fields are present in analysis data
- Validate effect sizes and confidence intervals
- Include complete study metadata for proper citations

### 2. Customization
- Use custom sections sparingly - auto-generated content follows APA guidelines
- Always review generated reports before publication
- Keep abstracts under 250 words (APA requirement)

### 3. Performance
- Generate visualizations in background tasks for large datasets
- Cache generated reports to avoid regeneration
- Use appropriate format (Word for editing, PDF for distribution)

### 4. Error Handling
- Check report status before attempting download
- Handle missing or incomplete analysis data gracefully
- Provide meaningful error messages to users

## Examples

### Example 1: Basic Report Generation

```python
from app.services.apa_report_generator import APAReportGenerator

generator = APAReportGenerator()

analysis_data = {
    "id": "test-001",
    "title": "My Meta-Analysis",
    "num_studies": 10,
    "pooled_effect_size": 0.5,
    "studies": [...]
}

result = generator.generate_report(
    analysis_data=analysis_data,
    format="docx"
)

print(f"Report saved to: {result['docx_path']}")
```

### Example 2: Custom Sections

```python
custom_sections = {
    "abstract": "This meta-analysis examined...",
    "introduction": "Background: Anxiety is a common..."
}

result = generator.generate_report(
    analysis_data=analysis_data,
    format="both",
    custom_sections=custom_sections
)
```

### Example 3: API Usage

```bash
# Generate report
curl -X POST "http://localhost:8000/api/v1/meta-analysis/generate-report/analysis-123" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "docx",
    "title": "My Meta-Analysis",
    "authors": ["Smith, J."],
    "institution": "University Name"
  }'

# Download report
curl -O "http://localhost:8000/api/v1/meta-analysis/report/1/download?format=docx"
```

## Troubleshooting

### Issue: Reports fail to generate

**Solution**: Check that all required dependencies are installed:
```bash
pip install python-docx reportlab Pillow matplotlib
```

### Issue: PDF fonts not rendering correctly

**Solution**: Ensure Times New Roman font is available on the system, or modify the font configuration in `APAFormatConfig`.

### Issue: Large reports cause timeout

**Solution**: Use background tasks for report generation:
```python
background_tasks.add_task(generate_report, analysis_id)
```

### Issue: Citations not formatting correctly

**Solution**: Verify that study data includes all required fields:
- `authors` (list)
- `year` (integer)
- `title` (string)
- `journal` (string)

## Future Enhancements

1. **Template System**: Full template editor with drag-and-drop sections
2. **Collaboration**: Multi-author editing and approval workflow
3. **Version Control**: Track report revisions and changes
4. **Export Formats**: LaTeX, HTML, Markdown
5. **Batch Generation**: Generate multiple reports simultaneously
6. **Email Delivery**: Automatic email sending with report attachments
7. **Cloud Storage**: Integration with Google Drive, Dropbox
8. **Citation Styles**: Support for additional citation styles (AMA, Chicago, etc.)

## Support

For issues or questions:
- GitHub Issues: [link]
- Documentation: `/docs`
- API Documentation: `/docs` (Swagger UI)

## License

[Your license here]
