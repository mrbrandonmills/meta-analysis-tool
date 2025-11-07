"""PDF text extraction service with section detection.

Extracts structured text from academic PDFs, including:
- Section detection (Introduction, Methods, Results, etc.)
- Table and figure detection
- Reference extraction
- Statistical data extraction
- OCR support for scanned PDFs
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available, PDF extraction will be limited")

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available")

from sqlalchemy.orm import Session

from app.models.pdf_metadata import (
    PDFMetadata,
    FullTextExtraction,
    SectionType,
)


class PDFTextExtractor:
    """Extract and structure text from academic PDFs.

    Features:
    - Multiple extraction backends (pdfplumber, PyPDF2)
    - Section detection using heuristics
    - Table and figure counting
    - Reference extraction
    - Quality assessment
    - Statistical pattern detection
    """

    # Common section headers in academic papers
    SECTION_PATTERNS = {
        SectionType.ABSTRACT: [
            r"^abstract\s*$",
            r"^summary\s*$",
        ],
        SectionType.INTRODUCTION: [
            r"^introduction\s*$",
            r"^1\.?\s*introduction",
            r"^background\s*$",
        ],
        SectionType.METHODS: [
            r"^methods?\s*$",
            r"^materials?\s+and\s+methods?",
            r"^methodology\s*$",
            r"^experimental\s+design",
            r"^\d+\.?\s*methods?",
        ],
        SectionType.RESULTS: [
            r"^results?\s*$",
            r"^\d+\.?\s*results?",
            r"^findings\s*$",
        ],
        SectionType.DISCUSSION: [
            r"^discussion\s*$",
            r"^\d+\.?\s*discussion",
        ],
        SectionType.CONCLUSION: [
            r"^conclusions?\s*$",
            r"^\d+\.?\s*conclusions?",
            r"^concluding\s+remarks",
        ],
        SectionType.REFERENCES: [
            r"^references?\s*$",
            r"^bibliography\s*$",
            r"^works?\s+cited",
        ],
        SectionType.ACKNOWLEDGMENTS: [
            r"^acknowledgments?\s*$",
            r"^acknowledgements?\s*$",
        ],
    }

    # Patterns for detecting statistics
    STATISTICS_PATTERNS = [
        r"p\s*[<>=]\s*0?\.\d+",  # p-values
        r"CI\s*[:\s]*\[?\d+\.?\d*\s*[-–]\s*\d+\.?\d*\]?",  # Confidence intervals
        r"95%\s+CI",
        r"[Mm]ean\s*[:\s]*\d+\.?\d*",
        r"SD\s*[:\s]*\d+\.?\d*",
        r"n\s*=\s*\d+",  # Sample sizes
        r"r\s*=\s*0?\.\d+",  # Correlations
        r"OR\s*=\s*\d+\.?\d*",  # Odds ratios
        r"RR\s*=\s*\d+\.?\d*",  # Risk ratios
        r"effect\s+size[:\s]*\d+\.?\d*",
    ]

    def __init__(self, db: Session):
        """Initialize PDF text extractor.

        Args:
            db: Database session
        """
        self.db = db

        if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
            raise ImportError(
                "No PDF extraction library available. "
                "Install pdfplumber or PyPDF2: pip install pdfplumber PyPDF2"
            )

    def extract_text_from_pdf(
        self, pdf_metadata: PDFMetadata
    ) -> Tuple[bool, Optional[FullTextExtraction]]:
        """Extract text from PDF and store in database.

        Args:
            pdf_metadata: PDF metadata with storage path

        Returns:
            Tuple of (success, full_text_extraction)
        """
        if not pdf_metadata.storage_path:
            logger.error(f"No storage path for PDF metadata {pdf_metadata.id}")
            return False, None

        file_path = Path(pdf_metadata.storage_path)
        if not file_path.exists():
            logger.error(f"PDF file not found: {file_path}")
            return False, None

        logger.info(f"Extracting text from PDF: {file_path}")

        try:
            # Extract text using preferred method
            if PDFPLUMBER_AVAILABLE:
                text, page_count, tables_count = self._extract_with_pdfplumber(file_path)
            elif PYPDF2_AVAILABLE:
                text, page_count, tables_count = self._extract_with_pypdf2(file_path)
            else:
                return False, None

            if not text or len(text.strip()) < 100:
                logger.warning(f"Extracted text too short ({len(text)} chars)")
                pdf_metadata.is_scanned = True
                pdf_metadata.is_ocr_required = True
                self.db.commit()
                return False, None

            # Detect sections
            sections = self._detect_sections(text)

            # Extract statistics
            statistics = self._extract_statistics(text)

            # Extract study characteristics
            study_design = self._extract_study_design_mentions(text)
            interventions = self._extract_intervention_mentions(text)
            outcomes = self._extract_outcome_mentions(text)
            sample_sizes = self._extract_sample_size_mentions(text)

            # Detect figures
            figures_count = self._count_figures(text)

            # Extract references
            references_count = self._count_references(sections.get(SectionType.REFERENCES, ""))

            # Calculate word count
            word_count = len(text.split())

            # Assess extraction quality
            quality_score = self._assess_extraction_quality(text, sections)

            # Create or update extraction record
            extraction = FullTextExtraction(
                pdf_metadata_id=pdf_metadata.id,
                full_text=text,
                word_count=word_count,
                sections={k.value: v for k, v in sections.items()},
                section_headings=list(sections.keys()),
                tables_detected=tables_count,
                figures_detected=figures_count,
                references_count=references_count,
                extraction_quality=quality_score,
                has_extraction_errors=quality_score < 0.5,
                statistics_found=statistics,
                outcome_measures=outcomes,
                sample_size_mentions=sample_sizes,
                study_design_mentions=study_design,
                intervention_mentions=interventions,
            )

            # Update PDF metadata
            pdf_metadata.page_count = page_count
            pdf_metadata.extraction_status = "completed"

            # Save to database
            self.db.add(extraction)
            self.db.commit()
            self.db.refresh(extraction)

            logger.info(
                f"Successfully extracted {word_count} words from PDF {pdf_metadata.id}"
            )
            return True, extraction

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            pdf_metadata.extraction_status = "failed"
            self.db.commit()
            return False, None

    def _extract_with_pdfplumber(self, file_path: Path) -> Tuple[str, int, int]:
        """Extract text using pdfplumber.

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (text, page_count, tables_count)
        """
        text_parts = []
        tables_count = 0

        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)

            for page in pdf.pages:
                # Extract text
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

                # Count tables
                tables = page.extract_tables()
                tables_count += len(tables)

        full_text = "\n\n".join(text_parts)
        return full_text, page_count, tables_count

    def _extract_with_pypdf2(self, file_path: Path) -> Tuple[str, int, int]:
        """Extract text using PyPDF2.

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (text, page_count, tables_count)
        """
        text_parts = []

        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            page_count = len(reader.pages)

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        full_text = "\n\n".join(text_parts)
        # PyPDF2 doesn't detect tables
        return full_text, page_count, 0

    def _detect_sections(self, text: str) -> Dict[SectionType, str]:
        """Detect sections in the text using pattern matching.

        Args:
            text: Full text content

        Returns:
            Dictionary mapping section types to content
        """
        sections = {}
        lines = text.split("\n")

        current_section = SectionType.UNKNOWN
        current_content = []
        section_starts = {}

        # Find section boundaries
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()

            # Check each section pattern
            section_found = None
            for section_type, patterns in self.SECTION_PATTERNS.items():
                for pattern in patterns:
                    if re.match(pattern, line_lower, re.IGNORECASE):
                        section_found = section_type
                        break
                if section_found:
                    break

            if section_found:
                # Save previous section
                if current_content:
                    content = "\n".join(current_content).strip()
                    if content:
                        sections[current_section] = content

                # Start new section
                current_section = section_found
                current_content = []
                section_starts[section_found] = i
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            content = "\n".join(current_content).strip()
            if content:
                sections[current_section] = content

        return sections

    def _extract_statistics(self, text: str) -> List[Dict[str, str]]:
        """Extract statistical mentions from text.

        Args:
            text: Full text content

        Returns:
            List of statistics found
        """
        statistics = []

        for pattern in self.STATISTICS_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                statistics.append({
                    "text": match.group(0),
                    "pattern": pattern,
                    "position": match.start(),
                })

        return statistics[:100]  # Limit to first 100

    def _extract_study_design_mentions(self, text: str) -> List[str]:
        """Extract study design mentions.

        Args:
            text: Full text content

        Returns:
            List of study design mentions
        """
        patterns = [
            r"randomized\s+controlled\s+trial",
            r"RCT",
            r"cohort\s+study",
            r"case[- ]control\s+study",
            r"cross[- ]sectional\s+study",
            r"systematic\s+review",
            r"meta[- ]analysis",
            r"observational\s+study",
            r"experimental\s+design",
            r"double[- ]blind",
        ]

        mentions = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                mentions.append(match.group(0))

        return list(set(mentions))[:20]  # Unique mentions, limit to 20

    def _extract_intervention_mentions(self, text: str) -> List[str]:
        """Extract intervention mentions.

        Args:
            text: Full text content

        Returns:
            List of intervention mentions
        """
        # This is simplified; in production, use NLP
        patterns = [
            r"intervention\s+group",
            r"treatment\s+arm",
            r"experimental\s+condition",
            r"control\s+group",
            r"placebo",
            r"drug\s+administration",
        ]

        mentions = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                mentions.append(match.group(0))

        return list(set(mentions))[:20]

    def _extract_outcome_mentions(self, text: str) -> List[str]:
        """Extract outcome measure mentions.

        Args:
            text: Full text content

        Returns:
            List of outcome mentions
        """
        patterns = [
            r"primary\s+outcome",
            r"secondary\s+outcome",
            r"outcome\s+measure",
            r"endpoint",
            r"symptom\s+severity",
            r"quality\s+of\s+life",
        ]

        mentions = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                mentions.append(match.group(0))

        return list(set(mentions))[:20]

    def _extract_sample_size_mentions(self, text: str) -> List[str]:
        """Extract sample size mentions.

        Args:
            text: Full text content

        Returns:
            List of sample size mentions
        """
        pattern = r"n\s*=\s*\d+"
        matches = re.finditer(pattern, text, re.IGNORECASE)

        mentions = [match.group(0) for match in matches]
        return list(set(mentions))[:10]

    def _count_figures(self, text: str) -> int:
        """Count figure references in text.

        Args:
            text: Full text content

        Returns:
            Number of figures
        """
        pattern = r"[Ff]igure\s+\d+"
        matches = re.findall(pattern, text)
        return len(set(matches))

    def _count_references(self, references_text: str) -> Optional[int]:
        """Count references in references section.

        Args:
            references_text: References section text

        Returns:
            Number of references or None
        """
        if not references_text:
            return None

        # Count lines that look like references (start with number)
        lines = references_text.split("\n")
        ref_count = sum(1 for line in lines if re.match(r"^\s*\d+[\.\)]\s", line))

        return ref_count if ref_count > 0 else None

    def _assess_extraction_quality(
        self, text: str, sections: Dict[SectionType, str]
    ) -> float:
        """Assess the quality of text extraction.

        Args:
            text: Extracted text
            sections: Detected sections

        Returns:
            Quality score (0.0-1.0)
        """
        score = 0.0

        # Check text length
        if len(text) > 1000:
            score += 0.2

        # Check for key sections
        key_sections = [SectionType.ABSTRACT, SectionType.METHODS, SectionType.RESULTS]
        sections_found = sum(1 for sec in key_sections if sec in sections)
        score += (sections_found / len(key_sections)) * 0.4

        # Check for reasonable character distribution
        alpha_chars = sum(1 for c in text if c.isalpha())
        if len(text) > 0 and alpha_chars / len(text) > 0.5:
            score += 0.2

        # Check for paragraph structure
        paragraphs = text.split("\n\n")
        if len(paragraphs) > 5:
            score += 0.2

        return min(score, 1.0)

    def batch_extract(self, pdf_metadata_list: List[PDFMetadata]) -> Dict[str, int]:
        """Extract text from multiple PDFs.

        Args:
            pdf_metadata_list: List of PDF metadata records

        Returns:
            Statistics dictionary
        """
        stats = {
            "total": len(pdf_metadata_list),
            "success": 0,
            "failed": 0,
            "requires_ocr": 0,
        }

        for pdf_metadata in pdf_metadata_list:
            try:
                success, extraction = self.extract_text_from_pdf(pdf_metadata)

                if success:
                    stats["success"] += 1
                elif pdf_metadata.is_ocr_required:
                    stats["requires_ocr"] += 1
                else:
                    stats["failed"] += 1

            except Exception as e:
                logger.error(
                    f"Error extracting PDF {pdf_metadata.id}: {str(e)}"
                )
                stats["failed"] += 1

        logger.info(f"Batch extraction complete: {stats}")
        return stats

    def get_extraction(self, pdf_metadata_id) -> Optional[FullTextExtraction]:
        """Get extraction for a PDF.

        Args:
            pdf_metadata_id: PDF metadata ID

        Returns:
            Full text extraction or None
        """
        return (
            self.db.query(FullTextExtraction)
            .filter(FullTextExtraction.pdf_metadata_id == pdf_metadata_id)
            .first()
        )
