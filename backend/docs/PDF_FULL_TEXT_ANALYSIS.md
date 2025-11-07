# PDF Download and Full-Text Analysis

## Overview

This system implements comprehensive PDF download and full-text analysis capabilities for the meta-analysis screening phase. It extends the basic title/abstract screening with detailed full-text analysis using Claude AI.

## Architecture

### Components

1. **PDFDownloadService** (`app/services/pdf_download_service.py`)
   - Multi-source PDF downloading
   - Rate limiting and retry logic
   - Duplicate detection via file hashing
   - Storage abstraction (local/S3/GCS)

2. **PDFTextExtractor** (`app/services/pdf_text_extractor.py`)
   - Text extraction from PDFs (pdfplumber, PyPDF2)
   - Section detection (Abstract, Methods, Results, etc.)
   - Statistical pattern extraction
   - Study characteristics detection
   - Quality assessment

3. **FullTextScreeningAgent** (`app/agents/specialized/full_text_screening.py`)
   - Comprehensive PICO extraction
   - Study quality assessment
   - Detailed screening decisions
   - Data extraction for meta-analysis

4. **Database Models** (`app/models/pdf_metadata.py`)
   - `PDFMetadata`: Download tracking and metadata
   - `FullTextExtraction`: Extracted and structured text
   - `FullTextScreening`: Screening results and decisions

5. **API Endpoints** (`app/api/v1/meta_analysis.py`)
   - PDF download endpoints
   - Text extraction endpoints
   - Full-text screening endpoints
   - Status checking endpoints

6. **Celery Tasks** (`app/workers/tasks/pdf_processing.py`)
   - Async batch PDF downloading
   - Async batch text extraction
   - Complete workflow orchestration

## Workflow

### Complete Full-Text Screening Workflow

```
1. Search & Title/Abstract Screening
   ↓
2. Download PDFs
   - Try multiple sources (PMC, arXiv, Europe PMC, etc.)
   - Handle rate limits and retries
   - Store with deduplication
   ↓
3. Extract Text
   - Extract full text from PDF
   - Detect document sections
   - Extract statistics and study characteristics
   - Assess extraction quality
   ↓
4. Full-Text Screening
   - Apply inclusion/exclusion criteria
   - Extract PICO components
   - Assess study quality
   - Extract data for meta-analysis
   ↓
5. Human Review (if flagged)
   ↓
6. Data Extraction & Meta-Analysis
```

## Supported PDF Sources

### 1. PubMed Central (PMC)
- **Coverage**: Open access articles from PubMed
- **Identifier**: PMC ID (e.g., PMC123456)
- **URL Format**: `https://www.ncbi.nlm.nih.gov/pmc/articles/{PMC_ID}/pdf/`

### 2. arXiv
- **Coverage**: Preprints in physics, math, CS, etc.
- **Identifier**: arXiv ID (e.g., 2301.12345)
- **URL Format**: `https://arxiv.org/pdf/{ARXIV_ID}.pdf`

### 3. Europe PMC
- **Coverage**: Life sciences literature
- **Identifier**: PMID
- **URL Format**: `https://www.ebi.ac.uk/europepmc/webservices/rest/{PMID}/fullTextXML`

### 4. bioRxiv / medRxiv
- **Coverage**: Biology and medical preprints
- **Identifier**: DOI
- **URL Format**: `https://www.biorxiv.org/content/{DOI}v1.full.pdf`

### 5. Unpaywall
- **Coverage**: Open access versions of paywalled articles
- **API**: Unpaywall REST API
- **Requires**: Email address for API access

### 6. Direct DOI Resolution
- **Coverage**: Publisher-hosted PDFs
- **Note**: May encounter paywalls

## API Usage

### 1. Download PDFs

```bash
POST /api/v1/meta-analysis/download-pdfs/{analysis_id}

Request Body:
{
  "paper_ids": ["uuid1", "uuid2"],  # Optional: specific papers
  "max_concurrent": 5               # Max parallel downloads
}

Response:
{
  "analysis_id": "uuid",
  "status": "completed",
  "total": 10,
  "success": 8,
  "failed": 1,
  "paywall": 1,
  "already_downloaded": 0,
  "message": "Downloaded 8 of 10 PDFs"
}
```

### 2. Check PDF Status

```bash
GET /api/v1/meta-analysis/pdf-status/{analysis_id}

Response:
{
  "analysis_id": "uuid",
  "total_papers": 10,
  "downloaded": 8,
  "pending": 1,
  "failed": 1,
  "paywall": 1,
  "extraction_completed": 7,
  "extraction_pending": 1,
  "download_stats": [
    {
      "paper_id": "uuid",
      "download_status": "success",
      "extraction_status": "completed",
      "pdf_source": "pubmed_central",
      "file_size_bytes": 1234567,
      "page_count": 12
    }
  ]
}
```

### 3. Extract Text from PDFs

```bash
POST /api/v1/meta-analysis/extract-text/{analysis_id}

Response:
{
  "analysis_id": "uuid",
  "status": "completed",
  "total": 8,
  "success": 7,
  "failed": 0,
  "requires_ocr": 1,
  "message": "Extracted text from 7 of 8 PDFs"
}
```

### 4. Perform Full-Text Screening

```bash
POST /api/v1/meta-analysis/full-text-screen/{analysis_id}

Request Body:
{
  "inclusion_criteria": [
    "Randomized controlled trial",
    "Adult participants (18+)",
    "Anxiety as primary outcome"
  ],
  "exclusion_criteria": [
    "Non-English language",
    "Qualitative studies"
  ],
  "study_type": "RCT",
  "outcome_measures": ["anxiety", "depression"]
}

Response:
{
  "analysis_id": "uuid",
  "total_screened": 7,
  "included": 5,
  "excluded": 1,
  "uncertain": 1,
  "quality_summary": {
    "total_included": 5,
    "with_randomization": 5,
    "with_blinding": 4,
    "with_adequate_sample": 4,
    "with_effect_size": 5,
    "randomization_rate": 1.0,
    "blinding_rate": 0.8,
    "adequate_sample_rate": 0.8,
    "effect_size_reporting_rate": 1.0
  },
  "message": "Screened 7 full-text studies"
}
```

### 5. Get Study Full-Text Details

```bash
GET /api/v1/meta-analysis/study/{study_id}/full-text

Response:
{
  "study_id": "uuid",
  "paper": {
    "title": "Study Title",
    "authors": ["Smith J", "Johnson A"],
    "year": 2023,
    "journal": "Journal Name",
    "doi": "10.1234/test"
  },
  "pdf_metadata": {
    "download_status": "success",
    "pdf_source": "pubmed_central",
    "page_count": 12,
    "file_size_bytes": 1234567
  },
  "extraction": {
    "word_count": 8500,
    "sections": {
      "abstract": "...",
      "methods": "...",
      "results": "...",
      "discussion": "..."
    },
    "tables_detected": 3,
    "figures_detected": 5,
    "references_count": 45,
    "extraction_quality": 0.85,
    "statistics_found": [
      {"text": "p < 0.001", "pattern": "p value"},
      {"text": "d = 0.68", "pattern": "effect size"}
    ],
    "study_design_mentions": ["RCT", "randomized controlled trial"],
    "intervention_mentions": ["mindfulness", "intervention group"],
    "outcome_measures": ["anxiety", "depression"]
  },
  "screening": {
    "decision": "include",
    "confidence": 0.92,
    "reasoning": "Meets all inclusion criteria...",
    "pico_extraction": {
      "Population": "Adults aged 18-65 with anxiety disorder",
      "Intervention": "8-week mindfulness-based intervention",
      "Comparison": "Waitlist control",
      "Outcome": "Beck Anxiety Inventory (BAI)"
    },
    "study_quality_indicators": {
      "Study Design": "Randomized controlled trial",
      "Sample Size": "Adequate (n=200)",
      "Randomization": "Yes, computer-generated",
      "Blinding": "Assessor-blinded",
      "Attrition": "Low (8% at post-treatment)"
    },
    "data_extraction_preview": {
      "Effect Size": "0.68",
      "Confidence Interval": "[0.45, 0.91]",
      "P-value": "<0.001",
      "Sample Size": "200"
    },
    "needs_human_review": false,
    "concerns": []
  }
}
```

## Background Processing with Celery

For large batches, use Celery tasks for async processing:

```python
from app.workers.tasks.pdf_processing import (
    download_pdfs_batch_task,
    extract_text_batch_task,
    full_pdf_workflow_task
)

# Download PDFs asynchronously
task = download_pdfs_batch_task.delay(paper_ids, analysis_id)
result = task.get()  # Wait for completion

# Complete workflow
task = full_pdf_workflow_task.delay(paper_ids, analysis_id)
result = task.get()
```

## Configuration

Configuration options in `app/core/config.py`:

```python
# PDF Processing Configuration
pdf_storage_dir: str = "./downloads/pdfs"
pdf_max_file_size_mb: int = 50
pdf_download_timeout_seconds: int = 30
pdf_rate_limit_per_second: float = 3.0
pdf_max_retries: int = 3
pdf_cleanup_days: int = 30
```

Environment variables:
```bash
# Optional: Email for Unpaywall API
PUBMED_EMAIL=your.email@example.com

# Storage configuration
PDF_STORAGE_DIR=./downloads/pdfs
PDF_MAX_FILE_SIZE_MB=50
PDF_RATE_LIMIT_PER_SECOND=3.0
```

## Section Detection

The system automatically detects these sections:

- **Abstract**: Summary of the study
- **Introduction**: Background and context
- **Methods**: Study design, participants, procedures
- **Results**: Findings and statistical analyses
- **Discussion**: Interpretation and implications
- **Conclusion**: Summary of findings
- **References**: Cited literature
- **Acknowledgments**: Funding and acknowledgments

Section detection uses pattern matching with common academic paper headers.

## Statistical Pattern Extraction

Automatically extracts:
- **P-values**: `p < 0.05`, `p = 0.001`
- **Effect sizes**: `d = 0.68`, `OR = 1.5`
- **Confidence intervals**: `95% CI [0.45, 0.91]`
- **Sample sizes**: `n = 200`, `N = 150`
- **Correlations**: `r = 0.45`
- **Means and SDs**: `mean = 45.2, SD = 10.1`

## Study Characteristics Extraction

Automatically detects:
- **Study designs**: RCT, cohort study, case-control
- **Interventions**: Intervention group, treatment arm
- **Outcomes**: Primary outcome, secondary outcome
- **Sample information**: Sample size mentions

## Quality Assessment

Extraction quality is assessed based on:
- Text length and completeness
- Section detection success
- Character distribution (reasonable text vs. gibberish)
- Paragraph structure

Quality scores range from 0.0 to 1.0:
- **>0.7**: High quality extraction
- **0.5-0.7**: Moderate quality
- **<0.5**: Poor quality (may need OCR)

## Error Handling

### Download Errors

- **No URL Available**: No open access version found
- **HTTP 403**: Paywall detected, marked for manual retrieval
- **HTTP 429**: Rate limited, automatic retry with backoff
- **Timeout**: Network timeout, automatic retry
- **Connection Error**: Network issue, automatic retry

### Extraction Errors

- **File Not Found**: PDF file missing or moved
- **Minimal Text**: Likely scanned PDF, requires OCR
- **Corrupted PDF**: PDF file damaged or invalid
- **Permission Error**: Cannot read file

### Screening Flags

Studies are flagged for human review when:
- Confidence score < 0.7
- Critical information missing
- Conflicting evidence about criteria
- Methodological concerns detected
- Unclear reporting

## OCR Support (Future)

For scanned PDFs with minimal extractable text:

1. PDFs marked with `is_ocr_required = True`
2. Can integrate OCR engines:
   - Tesseract OCR (open source)
   - Google Cloud Vision API
   - AWS Textract
   - Azure Computer Vision

## Best Practices

### 1. Rate Limiting
- Respect source rate limits (default: 3 requests/second)
- Use batch processing for large numbers
- Implement exponential backoff for retries

### 2. Storage Management
- Regularly clean up old PDFs (default: 30 days)
- Consider cloud storage (S3/GCS) for production
- Implement file hash-based deduplication

### 3. Error Recovery
- Monitor download/extraction failures
- Retry failed items with backoff
- Flag items needing manual intervention

### 4. Quality Control
- Review uncertain screening decisions
- Validate PICO extraction accuracy
- Cross-check extracted statistics

### 5. Resource Management
- Limit concurrent downloads (default: 5)
- Use Celery for background processing
- Monitor disk space usage

## Troubleshooting

### PDFs Not Downloading

1. Check paper has valid identifiers (DOI, PMID, PMC ID, arXiv ID)
2. Verify network connectivity to sources
3. Check rate limiting isn't blocking requests
4. Try different sources manually
5. Consider paywalls (may need institutional access)

### Text Extraction Failing

1. Verify PDF file exists and is not corrupted
2. Check if PDF is scanned (needs OCR)
3. Try different extraction backend (pdfplumber vs PyPDF2)
4. Inspect PDF manually to verify it's readable

### Low Quality Extractions

1. Check extraction quality score
2. Review detected sections
3. Verify text makes sense (not garbled)
4. Consider alternative PDF sources
5. May need OCR for scanned documents

### Screening Not Working

1. Verify text extraction completed successfully
2. Check sections were detected correctly
3. Review inclusion/exclusion criteria clarity
4. Examine agent reasoning for decisions
5. Adjust criteria if needed

## Performance Considerations

### Download Performance
- Parallel downloads: 5 concurrent by default
- Rate limiting: 3 requests/second per source
- Average time: 5-30 seconds per PDF

### Extraction Performance
- Average time: 2-10 seconds per PDF (depends on size)
- Memory usage: ~50-200 MB per PDF
- CPU intensive for large PDFs

### Screening Performance
- Average time: 30-60 seconds per study (Claude API)
- Depends on text length and complexity
- Can process multiple studies in parallel

## Testing

### Unit Tests
```bash
pytest tests/unit/test_services/test_pdf_download.py
pytest tests/unit/test_services/test_pdf_extractor.py
```

### Integration Tests
```bash
pytest tests/integration/test_full_text_workflow.py -m integration
```

### Manual Testing
```bash
# Download PDFs for a test analysis
curl -X POST http://localhost:8000/api/v1/meta-analysis/download-pdfs/test-id \
  -H "Content-Type: application/json" \
  -d '{"max_concurrent": 3}'

# Check status
curl http://localhost:8000/api/v1/meta-analysis/pdf-status/test-id

# Extract text
curl -X POST http://localhost:8000/api/v1/meta-analysis/extract-text/test-id

# Screen full texts
curl -X POST http://localhost:8000/api/v1/meta-analysis/full-text-screen/test-id \
  -H "Content-Type: application/json" \
  -d '{
    "inclusion_criteria": ["RCT", "Adults"],
    "exclusion_criteria": ["Qualitative"]
  }'
```

## Future Enhancements

1. **OCR Integration**: Support for scanned PDFs
2. **Cloud Storage**: S3/GCS backend for scalability
3. **Advanced NLP**: Better section and entity detection
4. **Parallel Processing**: Distributed task queue
5. **Caching**: Redis cache for repeated downloads
6. **Monitoring**: Prometheus metrics for tracking
7. **Additional Sources**: More PDF repositories
8. **Citation Extraction**: Parse and link references
9. **Figure/Table Extraction**: Extract and analyze visual data
10. **Version Control**: Track PDF versions and updates

## Security Considerations

1. **File Validation**: Verify downloaded files are PDFs
2. **Size Limits**: Enforce maximum file size (default: 50 MB)
3. **Path Traversal**: Sanitize file paths
4. **Access Control**: Authenticate API requests
5. **Rate Limiting**: Prevent abuse of download endpoints
6. **Data Privacy**: Handle PHI/PII appropriately
7. **Storage Security**: Encrypt files at rest if needed

## License & Attribution

Please respect copyright and fair use when downloading PDFs:
- Only download open access articles when possible
- Respect paywalls and publisher restrictions
- Use institutional access when available
- Follow terms of service for each source
- Attribute sources appropriately

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review error messages in API responses
- Consult troubleshooting section above
- Check database for detailed error tracking
