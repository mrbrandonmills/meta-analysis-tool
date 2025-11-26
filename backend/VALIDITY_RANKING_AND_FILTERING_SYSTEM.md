# Validity Ranking & Advanced Filtering System

**Last Updated:** November 25, 2025

This document explains how the meta-analysis platform ranks study validity and provides advanced filtering options for researchers.

---

## Part 1: Validity Ranking System (CredibilityAgent)

### Overview

Every study that passes initial screening is evaluated for **credibility** and **replicability** by the CredibilityAgent. This ensures medical-grade quality assessment.

### Credibility Levels

Studies are ranked into **4 levels** with color coding:

| Level | Color | Score Range | Description |
|-------|-------|-------------|-------------|
| **HIGH** | 🟢 Green | 80-100 | Peer-reviewed, rigorous, replicable |
| **MEDIUM** | 🟡 Yellow | 60-79 | Sound but minor limitations |
| **LOW** | 🟠 Orange | 40-59 | Significant concerns or preprints |
| **VERY LOW** | 🔴 Red | 0-39 | Major methodological flaws |

---

### HIGH CREDIBILITY (🟢 Green: 80-100)

**Criteria:**
- ✅ Peer-reviewed in **reputable journal** (impact factor > 3)
- ✅ **Rigorous methodology:** Randomized, controlled, blinded
- ✅ **Adequate sample size:** Powered study with enough participants
- ✅ **Clear statistical reporting:** P-values, effect sizes, confidence intervals
- ✅ **No major conflicts of interest**
- ✅ **Replicable methods:** Detailed, reproducible procedures
- ✅ **Consistent with literature:** Findings align with existing research

**Examples:**
- New England Journal of Medicine RCT with 500+ participants
- Nature study with rigorous experimental design
- JAMA systematic review with pre-registered protocol

**Typical Scores:** 85-95

---

### MEDIUM CREDIBILITY (🟡 Yellow: 60-79)

**Criteria:**
- ✅ Peer-reviewed in **moderate journal** OR high-quality preprint
- ⚠️ **Generally sound methodology** but minor limitations
- ⚠️ **Adequate but not optimal sample size**
- ✅ Good statistical reporting
- ⚠️ Minor methodological concerns
- ✅ Mostly replicable

**Examples:**
- Mid-tier journal publication with adequate design
- Well-designed preprint from established researchers
- Observational study with good controls

**Typical Scores:** 65-75

---

### LOW CREDIBILITY (🟠 Orange: 40-59)

**Criteria:**
- ⚠️ **Preprint** OR peer-reviewed with concerns
- ❌ **Methodological limitations:** Poor controls, confounding variables
- ❌ **Small or underpowered sample:** Not enough participants
- ⚠️ **Incomplete statistical reporting**
- ❌ **Potential bias issues:** Industry funding, conflicts
- ❌ **Difficult to replicate:** Vague methods

**Examples:**
- Preprint with unclear methodology
- Small pilot study (n < 30)
- Industry-funded research without independent replication

**Typical Scores:** 45-55

---

### VERY LOW CREDIBILITY (🔴 Red: 0-39)

**Criteria:**
- ❌ **Major methodological flaws:** No controls, poor design
- ❌ **Serious bias or conflicts of interest**
- ❌ **Very small sample or poor design:** Case reports, anecdotes
- ❌ **Poor or missing statistical reporting**
- ❌ **Cannot be replicated:** Methods not described
- ❌ **Contradicts well-established findings** without adequate explanation

**Examples:**
- Case reports or single-subject designs
- Predatory journal publications
- Serious conflicts of interest
- Retracted or controversial studies

**Typical Scores:** 20-35

---

## Evaluation Factors

The CredibilityAgent evaluates studies across **7 key dimensions**:

### 1. Publication Status
- **Peer-reviewed > Preprint > Unpublished**
- Peer-reviewed journals have quality control
- Preprints can be high-quality but unreviewed
- Publication venue matters (Nature > local journal)

### 2. Journal Quality
- **High-impact > Mid-tier > Low-impact > Predatory**
- Impact factor considered (though not sole criterion)
- Predatory journals = automatic LOW/VERY LOW
- Evaluated using Journal Citation Reports (JCR)

### 3. Study Design
- **RCT > Controlled > Observational > Case study**
- Randomized Controlled Trials (RCTs) are gold standard
- Controlled studies without randomization still valuable
- Observational studies have more bias
- Case studies = descriptive only

### 4. Sample Size
- **Large, powered > Adequate > Small > Very small**
- Power analysis: Was study designed with enough participants?
- Small n (< 30) = questionable generalizability
- Very small n (< 10) = VERY LOW credibility

### 5. Statistical Rigor
- **Complete reporting > Partial > Poor**
- Must report: effect sizes, confidence intervals, p-values
- Pre-registration bonus (reduces p-hacking)
- Missing statistics = concern

### 6. Replicability
- **Detailed methods > Adequate > Vague > Cannot replicate**
- Can another researcher reproduce this study?
- Open data/code = replicability bonus
- Proprietary methods = concern

### 7. Funding & Bias
- **Independent > Institutional > Industry (potential bias)**
- Industry funding not automatic exclusion
- But requires scrutiny for conflicts of interest
- Independent replication preferred

---

## Example Credibility Assessment

### Study Example:
**Title:** "Effects of Mindfulness Meditation on Anxiety: A Randomized Controlled Trial"
**Journal:** Journal of Clinical Psychology (Impact Factor: 3.8)
**Sample Size:** n = 120 participants
**Design:** Randomized, waitlist control, 8-week intervention
**Statistics:** Effect size (d = 0.64), CI, p < .001

### CredibilityAgent Evaluation:

**Credibility Level:** **HIGH (🟢 Green)**
**Score:** 88/100

**Reasoning:**
```
✅ Publication credibility: Peer-reviewed in reputable journal (IF 3.8)
✅ Study design: Randomized controlled trial with waitlist control
✅ Sample size: Adequately powered (n=120, sufficient for effect detection)
✅ Statistical rigor: Complete reporting (effect sizes, CI, p-values)
✅ Replicability: Detailed methods section, intervention manual cited
⚠️ Minor limitation: Single-site study (limits generalizability)

Overall: Strong study suitable for meta-analysis inclusion.
```

**Strengths:**
- Randomized design reduces bias
- Adequate sample size
- Clear statistical reporting
- Reputable journal

**Concerns:**
- Single site (limits generalizability)
- Waitlist control (not active control)

**Replicability:** YES - Methods clearly described, intervention standardized

---

## How Studies Are Sorted

After credibility evaluation, studies are **automatically sorted**:

1. **HIGH credibility** (🟢 Green) - listed first
2. **MEDIUM credibility** (🟡 Yellow)
3. **LOW credibility** (🟠 Orange)
4. **VERY LOW credibility** (🔴 Red) - listed last

This ensures researchers see the most reliable studies first.

---

## Filtering Options

### Option 1: Peer-Review Only

**Setting:** `peer_review_only: true`

When enabled:
- ❌ Excludes all preprints (arXiv, bioRxiv, etc.)
- ❌ Excludes non-peer-reviewed sources
- ✅ Only includes peer-reviewed journal articles

**Use When:**
- Medical/clinical meta-analyses
- Regulatory submissions
- High-stakes research
- Want maximum credibility

### Option 2: Include Preprints

**Setting:** `peer_review_only: false` (default)

When enabled:
- ✅ Includes peer-reviewed articles
- ✅ Includes high-quality preprints
- 🟡 Preprints typically rated MEDIUM or LOW

**Use When:**
- Rapidly emerging fields (COVID research)
- Want comprehensive coverage
- Aware of preprint limitations

---

## Part 2: Pre-Search Database Selection

### Current Implementation

Researchers can already select databases before searching!

**API Endpoint:**
```bash
POST /meta-analysis/create
{
  "research_question": "...",
  "databases": [
    "pubmed",
    "arxiv",
    "google_scholar",
    "scopus"
  ]
}
```

### Available Databases

**FREE (Always Available):**
- `pubmed` - 36M biomedical papers
- `arxiv` - 2M preprints
- `europepmc` - 42M life sciences papers
- `core` - 280M open access papers
- `doaj` - 2M open access journals
- `semantic_scholar` - 200M papers with AI analysis
- `crossref` - 140M DOI records
- `base` - 340M academic documents

**SUBSCRIPTION (Requires API Key):**
- `google_scholar` - 389M papers (needs SerpApi)
- `scopus` - 84M papers (needs institutional key)
- `web_of_science` - 90M papers (needs institutional key)
- `ieee_xplore` - 5M CS/engineering papers (needs key)
- `jstor` - 12M humanities papers (needs institutional key)
- `sciencedirect` - 18M science papers (needs institutional key)

### Check Available Databases

**Endpoint:**
```bash
GET /databases/available
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "free_databases": [
    "pubmed", "arxiv", "europepmc", "core",
    "doaj", "semantic_scholar", "crossref", "base"
  ],
  "subscription_databases": [
    "google_scholar", "scopus"
  ],
  "total_available": 10,
  "estimated_total_papers": "1.4 billion"
}
```

Shows only databases the user has access to!

---

## Part 3: Researcher Geographic Filtering (NEW FEATURE)

### Design Specification

This is a **new feature** to filter studies by researcher location/affiliation.

### Use Cases

1. **US-Only Studies**
   - Healthcare policy research
   - Insurance/regulatory context
   - FDA-related research

2. **North America (US + Canada)**
   - Regional health patterns
   - Similar healthcare systems

3. **Developed Nations Only**
   - OECD countries
   - Similar economic contexts

4. **Exclude Certain Countries**
   - Due to data quality concerns
   - Differing methodologies

5. **Specific Institutions**
   - University-based research only
   - Exclude industry-affiliated studies

---

### Implementation Plan

#### Database Schema Changes

**New Table: `study_affiliations`**
```sql
CREATE TABLE study_affiliations (
    id UUID PRIMARY KEY,
    study_id UUID REFERENCES papers(id),
    institution VARCHAR(500),
    country VARCHAR(100),
    country_code VARCHAR(3),  -- ISO 3166-1 alpha-3
    state_province VARCHAR(100),
    institution_type VARCHAR(50),  -- university, hospital, industry, government
    is_primary_affiliation BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_study_affiliations_country ON study_affiliations(country_code);
CREATE INDEX idx_study_affiliations_state ON study_affiliations(state_province);
CREATE INDEX idx_study_affiliations_type ON study_affiliations(institution_type);
```

#### API Changes

**Update `MetaAnalysisRequest` Model:**
```python
class GeographicFilter(BaseModel):
    """Geographic filtering options."""

    # Include/exclude by country
    include_countries: List[str] = Field(
        default_factory=list,
        description="ISO 3166-1 alpha-3 country codes to include (e.g., ['USA', 'CAN'])"
    )
    exclude_countries: List[str] = Field(
        default_factory=list,
        description="ISO 3166-1 alpha-3 country codes to exclude"
    )

    # Include/exclude by region
    include_regions: List[str] = Field(
        default_factory=list,
        description="Regions to include (e.g., ['North America', 'Europe', 'OECD'])"
    )

    # US states (if include_countries contains 'USA')
    include_us_states: List[str] = Field(
        default_factory=list,
        description="US state codes to include (e.g., ['CA', 'NY'])"
    )

    # Institution type filtering
    include_institution_types: List[str] = Field(
        default_factory=list,
        description="Types: university, hospital, industry, government, research_institute"
    )
    exclude_institution_types: List[str] = Field(
        default_factory=list,
        description="Exclude specific institution types"
    )

    # Require specific affiliation characteristics
    require_university_affiliation: bool = False
    exclude_industry_funded: bool = False


class MetaAnalysisRequest(BaseModel):
    """Request to create a new meta-analysis."""

    research_question: str
    topic: str
    inclusion_criteria: List[str] = Field(default_factory=list)
    exclusion_criteria: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=lambda: ["pubmed", "arxiv"])
    peer_review_only: bool = False
    expert_name: str | None = None

    # NEW: Geographic filtering
    geographic_filter: GeographicFilter | None = None
```

---

### Example Usage

#### Example 1: US + Canada Only
```bash
POST /meta-analysis/create
{
  "research_question": "Effects of mindfulness on anxiety",
  "databases": ["pubmed", "google_scholar"],
  "geographic_filter": {
    "include_countries": ["USA", "CAN"]
  }
}
```

#### Example 2: US States Only (California, New York, Massachusetts)
```bash
{
  "research_question": "...",
  "geographic_filter": {
    "include_countries": ["USA"],
    "include_us_states": ["CA", "NY", "MA"]
  }
}
```

#### Example 3: OECD Countries (Developed Nations)
```bash
{
  "research_question": "...",
  "geographic_filter": {
    "include_regions": ["OECD"]
  }
}
```

Regions would map to countries:
- **OECD:** USA, CAN, GBR, DEU, FRA, JPN, AUS, etc. (38 countries)
- **North America:** USA, CAN, MEX
- **Europe:** All EU countries + UK, Switzerland, Norway
- **Asia-Pacific:** JPN, AUS, NZL, KOR, SGP, etc.

#### Example 4: University Research Only, Exclude Industry
```bash
{
  "research_question": "...",
  "geographic_filter": {
    "require_university_affiliation": true,
    "exclude_industry_funded": true
  }
}
```

---

### Affiliation Extraction Process

#### Step 1: Extract from Database Metadata

Most databases provide author affiliation data:

**PubMed Example:**
```xml
<AffiliationInfo>
  <Affiliation>Department of Psychology, University of California, Los Angeles, USA</Affiliation>
</AffiliationInfo>
```

**Parse:**
- Institution: "University of California, Los Angeles"
- Country: "USA"
- State: "California" or "CA"
- Type: "university"

#### Step 2: Use AI for Complex Parsing

For ambiguous affiliations, use LLM:

```python
async def parse_affiliation(affiliation_text: str) -> Dict:
    """Parse affiliation using AI."""
    prompt = f"""
    Extract structured data from this author affiliation:

    "{affiliation_text}"

    Extract:
    - Institution name
    - Country (ISO 3166-1 alpha-3 code)
    - State/province (if applicable)
    - Institution type (university, hospital, industry, government, research_institute)

    Return as JSON.
    """

    # Use Claude/GPT to parse
    result = await ai_service.parse(prompt)
    return result
```

#### Step 3: Geocoding Service

Use external service for validation:
- **OpenCage Geocoding API**
- **Google Geocoding API**
- **GeoNames API**

Verifies country/region mapping.

---

### Filtering Logic

#### ScreeningAgent Integration

Add geographic filtering to ScreeningAgent:

```python
# In ScreeningAgent.process()
if geo_filter := input_data.get("geographic_filter"):
    # Filter studies by geography
    filtered_studies = []

    for study in studies:
        # Get affiliations for this study
        affiliations = await self._get_study_affiliations(study)

        # Check if study meets geographic criteria
        if self._meets_geographic_criteria(affiliations, geo_filter):
            filtered_studies.append(study)
        else:
            excluded.append({
                "study": study,
                "reason": "Geographic filter: Outside specified regions"
            })

    studies = filtered_studies
```

---

### Frontend UI Design

#### Database Selection Screen

```
┌─────────────────────────────────────────────┐
│ Select Databases to Search                  │
├─────────────────────────────────────────────┤
│                                             │
│ FREE DATABASES (1.04B papers)              │
│ ☑ PubMed (36M)                             │
│ ☑ arXiv (2M)                               │
│ ☑ Europe PMC (42M)                         │
│ ☑ CORE (280M)                              │
│ ☑ DOAJ (2M)                                │
│ ☑ Semantic Scholar (200M)                  │
│ ☑ Crossref (140M)                          │
│ ☑ BASE (340M)                              │
│                                             │
│ SUBSCRIPTION DATABASES                      │
│ ☑ Google Scholar (389M) ✅ Key added       │
│ ☐ Scopus (84M) ⚠️  Add API key             │
│ ☐ Web of Science (90M) ⚠️  Add API key     │
│ ☐ IEEE Xplore (5M) ⚠️  Add API key         │
│                                             │
│ [Add New API Key]                          │
│                                             │
│ Selected: 9 databases, ~1.4B papers        │
└─────────────────────────────────────────────┘
```

#### Geographic Filter Screen

```
┌─────────────────────────────────────────────┐
│ Geographic Filters (Optional)               │
├─────────────────────────────────────────────┤
│                                             │
│ ○ All countries (default)                  │
│ ○ Specific countries                       │
│   [Select countries...] ▼                  │
│                                             │
│ ○ Region-based                             │
│   ☐ North America                          │
│   ☐ Europe                                 │
│   ☐ Asia-Pacific                           │
│   ☐ OECD Countries (developed nations)     │
│                                             │
│ ○ US States only                           │
│   [Select states...] ▼                     │
│                                             │
│ Institution Type Filters:                  │
│ ☑ Universities                             │
│ ☑ Hospitals/Medical Centers                │
│ ☑ Research Institutes                      │
│ ☐ Industry/Pharmaceutical                  │
│ ☑ Government Agencies                      │
│                                             │
│ Advanced:                                  │
│ ☐ Require university affiliation           │
│ ☐ Exclude industry-funded studies          │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Summary

### Validity Ranking ✅ (Already Implemented)
- **4 credibility levels:** HIGH, MEDIUM, LOW, VERY LOW
- **7 evaluation factors:** Publication status, journal quality, study design, sample size, statistics, replicability, funding
- **Automatic scoring:** 0-100 scale
- **Color coding:** Green, yellow, orange, red
- **Sorting:** Studies automatically sorted by credibility

### Database Selection ✅ (Already Implemented)
- Researchers select databases before search
- 8 FREE databases always available
- 6 SUBSCRIPTION databases with BYOK
- `/databases/available` shows what user can access

### Geographic Filtering 📋 (Design Complete, Ready to Implement)
- Filter by country, region, or US state
- Filter by institution type
- Exclude industry-funded studies
- Require university affiliation
- Affiliation extraction from metadata
- AI-powered parsing for complex affiliations

---

## Next Steps

1. ✅ **Validity ranking:** Already working
2. ✅ **Database selection:** Already working
3. ⏳ **Geographic filtering:** Design complete, ready to build
   - Add `study_affiliations` table
   - Add `geographic_filter` to API
   - Implement affiliation extraction
   - Add frontend UI

---

**Created:** November 25, 2025
**Status:** Validity ranking live, database selection live, geographic filtering designed
