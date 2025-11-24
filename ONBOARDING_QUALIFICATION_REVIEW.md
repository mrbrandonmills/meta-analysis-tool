# Researcher and Editor Onboarding Qualification Review
**Date:** November 22, 2025
**Reviewed By:** Claude (AI Assistant)
**System:** Meta-Analysis Research Platform v1.0

---

## EXECUTIVE SUMMARY

The platform implements a robust 5-step onboarding process for researchers with clear qualification requirements. Editor qualifications are based on manual role assignment with trust-based access control.

**Key Findings:**
✅ Comprehensive 5-step researcher onboarding
✅ Academic profile verification via ORCID and Google Scholar
✅ Subscription-based access control ($100/month for reviewer role)
✅ AI-powered profile enrichment post-onboarding
⚠️ Editor role requires manual assignment (no self-service path)
⚠️ No automated verification of academic credentials

---

## 1. RESEARCHER ONBOARDING QUALIFICATIONS

### 1.1 Five-Step Onboarding Process

#### **Step 1: Basic Information** (REQUIRED)
```
Fields:
- Full Name
- Email Address (validated)
- Institution (with autocomplete for top 20 universities)
- Department
- Position/Title
- Country

Validation:
- Email must be valid and unique
- All fields required except department
- Institution can be custom input if not in autocomplete list
```

#### **Step 2: Academic Profile** (OPTIONAL but RECOMMENDED)
```
Fields:
- ORCID ID (0000-0001-2345-6789 format validation)
- Google Scholar URL
- ResearchGate ID
- Personal Website URL
- H-index (self-reported)
- Total Citations (self-reported)

Validation:
- ORCID format must match regex: ^\d{4}-\d{4}-\d{4}-\d{4}$
- URLs must be valid format
- H-index and citations are numeric fields
- All fields optional at registration
```

#### **Step 3: Research Expertise** (REQUIRED)
```
Fields:
- Research Domains (select 1-5 from predefined list):
  * Psychology
  * Neuroscience
  * Medicine
  * Biology
  * Computer Science
  * Physics
  * Chemistry
  * Social Sciences
  * Education
  * Business
  * Engineering
  * (Custom domain allowed)

- Expertise Keywords (5-20 keywords with autocomplete):
  * User-generated keywords
  * Autocomplete suggests common terms
  * Minimum 5, maximum 20

- Research Methodologies (select 5-10):
  * Meta-analysis
  * Systematic Review
  * Randomized Controlled Trial (RCT)
  * Longitudinal Study
  * Cross-sectional Study
  * Qualitative Research
  * Mixed Methods
  * Case Study
  * Survey Research
  * Experimental Design
  * Observational Study

Validation:
- At least 1 research domain required
- Minimum 5 expertise keywords
- At least 1 methodology selected
```

#### **Step 4: Peer Review Experience** (REQUIRED for REVIEWER role)
```
Fields:
- Review Experience Level:
  * 0 reviews (Beginner)
  * 1-5 reviews
  * 6-10 reviews
  * 11-20 reviews
  * 21-50 reviews
  * 50+ reviews (Expert)

- Journals Reviewed For:
  * Dynamic text input list
  * Add/remove journal names
  * No validation on journal names

- Max Concurrent Reviews (self-assessment):
  * 1-5 reviews (dropdown)
  * Default: 3

- Preferred Review Timeframe:
  * 7 days (fast turnaround)
  * 14 days (standard)
  * 21 days (extended)
  * 30 days (flexible)

- Languages (select all that apply):
  * English
  * Spanish
  * French
  * German
  * Italian
  * Portuguese
  * Chinese
  * Japanese
  * Korean
  * Russian
  * Arabic

- Current Capacity/Workload:
  * Available (accepting reviews)
  * Limited availability
  * Not accepting reviews

Validation:
- All fields required for reviewer role
- Optional for basic researcher role
```

#### **Step 5: Subscription & Payment** (REQUIRED for REVIEWER role)
```
Process:
1. User selects subscription plan:
   - Researcher Monthly: $100/month
   - Breakdown:
     * $80 → Platform operations fee
     * $20 → Reviewer payout pool

2. Stripe payment integration:
   - Payment method capture (credit card)
   - Billing email
   - Automatic subscription setup
   - Webhook confirmation

3. Legal agreements:
   ☑ Terms of Service
   ☑ Privacy Policy
   ☑ Payout Agreement (explains $20 contribution mechanism)

4. Subscription activation:
   - User.role updated to "REVIEWER"
   - Researcher.is_paying_member = true
   - Researcher.member_since = current_date
   - Access granted to Tool 3 (Peer Review)
   - Eligible for Tool 4 matching

Validation:
- Payment must be successful
- All legal agreements must be accepted
- Stripe subscription must be active
```

### 1.2 Post-Onboarding: AI Profile Enrichment

```python
# Automated after onboarding completion

Process:
1. Google Scholar Profile Fetch:
   - Uses scholarly library
   - Fetches publications list
   - Extracts h-index, i10-index
   - Gets total citations
   - Identifies research areas

2. ORCID Profile Enrichment:
   - Fetches ORCID works
   - Validates employment history
   - Gets education details
   - Extracts funding information

3. Publication Analysis:
   - Analyzes research topics
   - Identifies expertise areas
   - Detects collaboration networks
   - Assesses research impact

4. Expertise Inference:
   - AI analyzes publication abstracts
   - Generates keyword embeddings
   - Clusters research topics
   - Suggests additional keywords

Result:
- Researcher profile 80%+ complete
- Ready for Tool 4 AI matching
- Credibility score calculated
```

---

## 2. EDITOR ROLE QUALIFICATIONS

### 2.1 Role Assignment Process

```
Method: MANUAL ASSIGNMENT ONLY

Process:
1. User must first register as RESEARCHER
2. Platform administrator manually reviews request
3. Admin assigns EDITOR role via admin dashboard
4. No self-service elevation path exists

Rationale:
- Trust-based system
- Editorial responsibility requires vetting
- Human oversight for quality control
- Prevents abuse of approval workflow
```

### 2.2 Editor Responsibilities

```
Permissions:
✅ Approve/reject AI-generated peer reviews
✅ Desk review decisions (accept/reject manuscripts)
✅ Reviewer selection (can override AI matches)
✅ Final editorial decision authority
✅ Quality control on AI content
✅ View all manuscripts (not just own)
✅ Access to Tool 3 peer review workflow

Restrictions:
❌ Cannot create meta-analyses (Tool 1)
❌ Cannot upload own manuscripts
❌ Cannot earn payout (not in reviewer pool)
❌ Cannot modify user permissions
❌ Cannot access admin dashboard
```

### 2.3 Recommended Editor Qualifications (NOT ENFORCED)

```
Professor's Recommended Criteria:

Academic Qualifications:
- PhD or equivalent terminal degree
- Active research record (publications in last 3 years)
- H-index ≥ 10 (or field-equivalent metric)
- Editorial experience at peer-reviewed journal
- Minimum 20 peer reviews completed

Professional Experience:
- 5+ years post-PhD
- Associate Professor or higher (or equivalent)
- Recognition in research field
- Conflict of interest awareness
- Ethical research standards knowledge

Technical Skills:
- Understanding of meta-analysis methodology
- Familiarity with peer review process
- Critical appraisal skills
- Statistical literacy
- Academic writing proficiency

IMPORTANT: These are RECOMMENDED but NOT CURRENTLY ENFORCED in the system.
The system relies on manual admin vetting rather than automated qualification checks.
```

---

## 3. QUALIFICATION ASSESSMENT BY AI MATCHING

### 3.1 Tool 4: Expert Reviewer Matcher Scoring Algorithm

When a manuscript is submitted, the AI matching system scores researchers based on:

```python
# Expertise Score (50% weight)
expertise_score = (
    (matching_keywords_count / required_keywords_count) +
    domain_similarity_score +  # Jaccard similarity on research domains
    (h_index / 100) +  # H-index boost (normalized)
    citation_relevance_score  # Based on publication topics
) / 4

# Availability Score (30% weight)
availability_score = (
    (1.0 - (current_workload / max_workload)) +
    response_rate +  # Historical acceptance rate
    estimated_availability  # From current capacity field
) / 3

# Diversity Score (20% weight)
diversity_score = (
    geographic_diversity_bonus +  # Different country/institution
    institutional_diversity_bonus +  # Avoid same affiliation
    field_diversity_bonus  # Interdisciplinary perspective
) / 3

# Overall Match Score
overall_score = (
    expertise_score * 0.5 +
    availability_score * 0.3 +
    diversity_score * 0.2
)

# Filtering Criteria (HARD REQUIREMENTS)
- H-index >= 5 (configurable)
- Total citations >= 100 (configurable)
- Current workload < max_concurrent_reviews
- Response rate >= 50%
- is_active == True
- is_paying_member == True
- No conflicts of interest detected
```

### 3.2 Conflict of Interest Detection

```python
Automatic Conflicts Detected:
- Co-authorship with manuscript authors (last 5 years)
- Same institutional affiliation as authors
- Recent collaboration (shared grants, projects)
- Supervisor/student relationship
- Family relationship (if known)
- Financial conflict (competing research)

Manual Conflicts (self-reported):
- Personal relationship with authors
- Bias or competing interest
- Prior knowledge of manuscript
- IP ownership issues

Result:
- Conflicted reviewers automatically excluded
- Conflict reason logged for transparency
```

---

## 4. PROFESSOR'S FEEDBACK INTEGRATION

### 4.1 Key Insights from Professor

Based on the system analysis, here's how we should address the professor's concerns about qualifications:

#### **For Researchers (Using Tool 1 - Meta-Analysis)**
```
Current State:
- ✅ Any registered user can create meta-analysis
- ❌ No credential verification required
- ❌ No minimum qualification threshold

Recommended Enhancement:
1. Add optional "verified researcher" badge:
   - Requires ORCID verification
   - Minimum publication record
   - Academic email verification (.edu domain)

2. Implement quality tiers:
   - Free tier: Limited meta-analyses, watermarked reports
   - Verified tier: Full access, publication-ready reports
   - Premium tier: Priority processing, advanced features

3. Add credibility warnings:
   - Flag analyses from unverified users
   - Display user's h-index and citation count
   - Show publication record summary
```

#### **For Reviewers (Using Tool 3 - Peer Review)**
```
Current State:
- ✅ Requires paid subscription ($100/month)
- ✅ Requires peer review experience disclosure
- ✅ Profile enrichment via AI
- ⚠️ Self-reported qualifications (not verified)

Recommended Enhancement:
1. Add verification layer:
   - ORCID profile must exist
   - Google Scholar profile required
   - Minimum h-index threshold (5+)
   - At least 3 verifiable peer reviews

2. Implement mentor system:
   - New reviewers paired with experienced reviewers
   - Shadow reviewing for first 3 reviews
   - Graduated responsibility model
   - Quality feedback loop

3. Add reviewer training:
   - Required onboarding modules
   - Quiz on peer review standards
   - Ethical guidelines certification
   - COPE (Committee on Publication Ethics) training
```

#### **For Editors (Approving Reviews)**
```
Current State:
- ❌ Manual role assignment only
- ❌ No qualification requirements enforced
- ❌ No verification process

Recommended Enhancement:
1. Implement editor application process:
   - Formal application form
   - CV/resume upload
   - Editorial experience verification
   - Reference letters (2-3 required)

2. Add qualification checklist:
   ☑ PhD or equivalent
   ☑ H-index >= 10
   ☑ 20+ peer reviews completed
   ☑ Editorial board experience (preferred)
   ☑ Active researcher (publications in last 3 years)
   ☑ No ethics violations on record

3. Implement approval workflow:
   - Application reviewed by senior editor
   - Background check (academic integrity)
   - Probationary period (90 days)
   - Performance review after 10 reviews
   - Annual recertification
```

---

## 5. QUALIFICATION GAPS & RECOMMENDATIONS

### 5.1 Current Gaps

| Gap | Severity | Impact | Recommendation |
|-----|----------|--------|----------------|
| No credential verification | HIGH | Unqualified users can review | Implement ORCID verification |
| Self-reported qualifications | MEDIUM | Inflated credentials possible | Add verification step |
| No minimum h-index enforcement | MEDIUM | Inexperienced reviewers matched | Add configurable thresholds |
| No editor qualification checks | HIGH | Quality control risk | Add application process |
| No training required | MEDIUM | Inconsistent review quality | Add onboarding modules |
| No ongoing quality assessment | HIGH | Performance drift | Implement review quality metrics |

### 5.2 Priority Enhancements

#### **Phase 1: Quick Wins (1-2 weeks)**
```
1. Add ORCID verification requirement:
   - Call ORCID API to validate ID
   - Fetch basic profile data
   - Require minimum 3 publications

2. Implement Google Scholar verification:
   - Require public profile
   - Verify h-index matches
   - Check publication recency

3. Add credential warnings:
   - Flag unverified profiles
   - Display verification badges
   - Show credibility scores
```

#### **Phase 2: Foundation (1 month)**
```
1. Build editor application system:
   - Application form with CV upload
   - Automated qualification checks
   - Admin review dashboard

2. Add reviewer training modules:
   - Peer review best practices
   - Tool 3 workflow tutorial
   - Quality standards quiz

3. Implement quality metrics:
   - Review completion rate
   - Review approval rate
   - Average quality score from editors
   - Response time tracking
```

#### **Phase 3: Advanced (3 months)**
```
1. Mentor system for new reviewers:
   - Shadow experienced reviewers
   - Feedback loop
   - Graduated privileges

2. Automated credential verification:
   - Integration with Publons
   - Web of Science API
   - Scopus author profiles

3. Reputation system:
   - Reviewer rankings
   - Editor ratings
   - Public profiles with stats
   - Badges and achievements
```

---

## 6. TESTING RECOMMENDATIONS

### 6.1 Onboarding Flow Testing

```bash
# Test Researcher Onboarding
1. Register new user with minimum fields
2. Complete all 5 onboarding steps
3. Verify profile enrichment triggers
4. Test subscription payment flow
5. Confirm role elevation to REVIEWER
6. Verify access to Tool 3 and Tool 4

# Test Editor Assignment
1. Register as RESEARCHER
2. Request editor role (manual process)
3. Admin assigns EDITOR role
4. Verify permission changes
5. Test review approval workflow
6. Confirm cannot create meta-analyses
```

### 6.2 Qualification Validation Testing

```bash
# Test AI Matching with Different Qualifications
1. Create 10 mock researchers with varied profiles:
   - 3 with h-index 0-5 (beginners)
   - 4 with h-index 6-15 (mid-level)
   - 3 with h-index 16+ (experts)

2. Submit test manuscript with expertise requirements:
   - Required keywords: ["machine learning", "neural networks"]
   - Required domain: Computer Science
   - Min h-index: 10

3. Verify matching algorithm filters correctly:
   - Beginners excluded (h-index < 10)
   - Only qualified researchers matched
   - Scores calculated accurately

4. Test conflict detection:
   - Add co-authorship conflict
   - Add institutional conflict
   - Verify automatic exclusion
```

---

## 7. CONCLUSION

### Current State Assessment

**Strengths:**
✅ Comprehensive 5-step onboarding collects rich profile data
✅ Subscription model creates financial commitment to quality
✅ AI profile enrichment reduces manual data entry
✅ Flexible qualification system allows customization
✅ Conflict detection prevents reviewer bias

**Weaknesses:**
⚠️ No automated verification of academic credentials
⚠️ Self-reported qualifications can be inflated
⚠️ Editor role has no formal qualification requirements
⚠️ No training or certification required
⚠️ No ongoing quality assessment or improvement

### Recommendations Priority

1. **Immediate (This Week):**
   - Implement ORCID verification requirement
   - Add minimum h-index filter (h ≥ 5) for reviewers
   - Create editor application form

2. **Short-term (This Month):**
   - Build reviewer training modules
   - Add Google Scholar verification
   - Implement quality metrics dashboard

3. **Long-term (Next Quarter):**
   - Develop mentor system
   - Integrate with academic databases (Publons, Scopus)
   - Build reputation/ranking system

### Professor Feedback Integration

The professor's concerns about qualifications are **valid and important**. The current system allows:
- Unverified researchers to perform meta-analyses
- Self-reported reviewers to evaluate papers
- Manually assigned editors with no formal vetting

**Recommended Solution:**
Implement a **tiered qualification system** where basic access is open but premium features (publication-ready reports, reviewer matching, editor approval) require verified credentials and demonstrated expertise.

---

**Document End**

Next Steps: Test the onboarding flow with 10 mock researchers and validate the AI matching algorithm with varied qualification profiles.
