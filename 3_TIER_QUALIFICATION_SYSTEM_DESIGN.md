# 3-Tier Qualification System Design
**Meta-Analysis Research Platform**
**Date:** November 22, 2025
**Based on Professor's Feedback**

---

## EXECUTIVE SUMMARY

This document outlines a complete redesign of the platform's pricing and qualification system based on academic best practices and professor feedback. The new system implements:

1. **3-Tier Pricing Structure** (Researcher → Reviewer → Editor)
2. **Rigorous Qualification Requirements** for each tier
3. **Application & Approval Workflow** with admin review
4. **Appeal Process** for denied applications
5. **Automatic Verification** where possible (ORCID, Google Scholar)
6. **Manual Verification** for credentials (CV, publications, degrees)

---

## 1. THREE-TIER STRUCTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                    TIER 1: RESEARCHER                           │
│                                                                 │
│  Price: $49/month or FREE (limited features)                   │
│  Access: Meta-analysis creation, research direction tool       │
│  Qualifications: Basic registration (email verification)       │
│  No approval required                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   TIER 2: PEER REVIEWER                         │
│                                                                 │
│  Price: $99/month (includes Tier 1)                            │
│  Access: Peer review tool + reviewer matching + earnings       │
│  Qualifications:                                                │
│    ✓ Verified PhD or terminal degree                          │
│    ✓ Minimum 3 peer-reviewed publications                     │
│    ✓ CV/Resume upload                                          │
│    ✓ Google Scholar profile (verified)                         │
│    ✓ ORCID profile (verified)                                  │
│    ✓ No ethical violations                                     │
│  REQUIRES ADMIN APPROVAL                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      TIER 3: EDITOR                             │
│                                                                 │
│  Price: $149/month (includes Tier 1 + 2)                       │
│  Access: Editorial dashboard + review approval + all tools     │
│  Qualifications:                                                │
│    ✓ All Tier 2 requirements PLUS:                            │
│    ✓ Minimum H-index ≥ 10 (field-adjusted)                    │
│    ✓ Minimum 10 publications in peer-reviewed journals        │
│    ✓ 20+ completed peer reviews (verified)                    │
│    ✓ Editorial experience OR 2 letters of recommendation      │
│    ✓ Active researcher (publications in last 3 years)         │
│  REQUIRES SENIOR ADMIN APPROVAL                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. DETAILED QUALIFICATION REQUIREMENTS

### 2.1 Tier 1: Researcher (Basic Access)

**Purpose:** Access meta-analysis tools and research direction features

**Monthly Price:**
- **FREE Plan:** 3 meta-analyses/month, watermarked reports
- **Paid Plan:** $49/month - Unlimited analyses, publication-ready reports

**Registration Requirements:**
```json
{
  "required_fields": {
    "email": "Valid email address (must verify via email link)",
    "password": "Minimum 8 characters (uppercase, lowercase, digit)",
    "full_name": "Full legal name",
    "institution": "University/research institution",
    "country": "Country of residence"
  },
  "optional_fields": {
    "department": "Department or school",
    "position": "Academic position/title",
    "research_interests": "Brief description"
  },
  "verification_required": {
    "email_confirmation": "Click link sent to email (24-hour expiration)",
    "captcha": "Human verification"
  },
  "approval_process": "AUTOMATIC (no admin review)",
  "access_granted": "IMMEDIATELY upon email verification"
}
```

**What You Can Do:**
- ✅ Create meta-analyses (3/month free, unlimited paid)
- ✅ Use research direction tool
- ✅ Access knowledge base and tutorials
- ✅ Save and export results
- ❌ Submit peer reviews
- ❌ Earn money from reviews
- ❌ Approve reviews (editor function)

**No Credentials Required** - This is the entry tier for researchers to try the platform.

---

### 2.2 Tier 2: Peer Reviewer (Professional Access)

**Purpose:** Conduct peer reviews, get matched with manuscripts, earn money

**Monthly Price:** $99/month
- Includes all Tier 1 features
- Access to peer review tool
- Eligible for reviewer matching
- Earn from approved reviews ($20-50 per review based on quality)
- $20/month contribution goes to reviewer payout pool

**Application Requirements:**

#### **A. Academic Credentials (REQUIRED)**

```json
{
  "degree_verification": {
    "degree_type": "PhD, MD, JD, or equivalent terminal degree",
    "institution": "Accredited university",
    "field_of_study": "Specific discipline",
    "graduation_year": "Year degree awarded",
    "verification_method": [
      "Upload degree certificate/diploma (PDF, max 5MB)",
      "Provide university registrar contact for verification",
      "OR institutional email address (@university.edu)"
    ],
    "required": true
  },

  "publication_record": {
    "minimum_publications": 3,
    "publication_types": [
      "Peer-reviewed journal articles",
      "Book chapters in academic press",
      "Conference proceedings (top-tier venues)"
    ],
    "verification_method": [
      "Upload CV/Resume (PDF, max 10MB)",
      "Provide DOIs or links to publications",
      "Google Scholar profile URL (auto-verify citation count)"
    ],
    "required": true,
    "admin_review": "Manual verification of publication quality"
  },

  "orcid_profile": {
    "orcid_id": "Format: 0000-0001-2345-6789",
    "verification_method": "API call to ORCID public registry",
    "checks": [
      "Profile exists and is public",
      "At least 3 works listed",
      "Employment history present",
      "Education history present"
    ],
    "required": true,
    "automatic": true
  },

  "google_scholar_profile": {
    "profile_url": "Public Google Scholar profile URL",
    "verification_method": "Web scraping via scholarly library",
    "checks": [
      "Profile is public and accessible",
      "Minimum 3 publications listed",
      "H-index ≥ 3 (field-adjusted)",
      "Recent publication activity (last 5 years)"
    ],
    "required": true,
    "automatic": true
  }
}
```

#### **B. Research Expertise (REQUIRED)**

```json
{
  "expertise_domains": {
    "description": "Select 1-5 primary research areas",
    "options": [
      "Psychology", "Neuroscience", "Medicine", "Biology",
      "Computer Science", "Physics", "Chemistry", "Engineering",
      "Social Sciences", "Education", "Business", "Economics",
      "Environmental Science", "Mathematics", "Statistics"
    ],
    "custom_allowed": true,
    "minimum": 1,
    "maximum": 5,
    "required": true
  },

  "expertise_keywords": {
    "description": "Specific areas of expertise (for matching)",
    "minimum": 10,
    "maximum": 30,
    "examples": [
      "cognitive psychology", "fMRI", "neural networks",
      "machine learning", "clinical trials", "meta-analysis"
    ],
    "autocomplete": true,
    "required": true
  },

  "research_methodologies": {
    "description": "Research methods you are qualified to review",
    "options": [
      "Meta-analysis", "Systematic Review", "RCT",
      "Longitudinal Study", "Cross-sectional Study",
      "Qualitative Research", "Mixed Methods", "Case Study",
      "Experimental Design", "Survey Research", "fMRI",
      "Computational Modeling", "Statistical Analysis"
    ],
    "minimum": 3,
    "required": true
  }
}
```

#### **C. Peer Review Experience (REQUIRED)**

```json
{
  "review_experience": {
    "total_reviews_completed": {
      "description": "Total peer reviews completed in career",
      "minimum": 3,
      "verification_method": [
        "Publons/Web of Science reviewer profile",
        "Letters from journal editors",
        "List of journals reviewed for (will be verified)"
      ],
      "required": true
    },

    "journals_reviewed_for": {
      "description": "List journals you have reviewed for",
      "format": "Journal name, year(s), number of reviews",
      "example": "Nature Neuroscience, 2022-2024, 5 reviews",
      "verification": "Admin will verify with journal editors",
      "minimum": 2,
      "required": true
    },

    "review_quality_evidence": {
      "description": "Evidence of review quality (optional)",
      "options": [
        "Outstanding Reviewer awards",
        "Thank-you letters from editors",
        "Publons profile with verified reviews",
        "Editor recommendations"
      ],
      "required": false,
      "bonus": "Speeds up approval process"
    }
  },

  "review_capacity": {
    "max_concurrent_reviews": {
      "description": "Maximum reviews you can handle simultaneously",
      "options": [1, 2, 3, 4, 5],
      "default": 3,
      "required": true
    },

    "preferred_timeframe": {
      "description": "Preferred time to complete a review",
      "options": [7, 14, 21, 30],
      "unit": "days",
      "default": 14,
      "required": true
    },

    "review_languages": {
      "description": "Languages you can review in",
      "options": [
        "English", "Spanish", "French", "German", "Italian",
        "Portuguese", "Chinese", "Japanese", "Korean", "Russian", "Arabic"
      ],
      "minimum": 1,
      "required": true
    }
  },

  "ethical_standards": {
    "conflicts_of_interest": {
      "question": "Have you ever been found to have undisclosed conflicts of interest in peer review?",
      "answer": "Yes/No",
      "if_yes": "Provide explanation and context",
      "required": true,
      "disqualifying_if_yes": false
    },

    "research_misconduct": {
      "question": "Have you ever been found responsible for research misconduct?",
      "answer": "Yes/No",
      "if_yes": "Automatic rejection",
      "required": true,
      "disqualifying_if_yes": true
    },

    "cope_guidelines": {
      "question": "Do you agree to follow COPE (Committee on Publication Ethics) guidelines?",
      "link": "https://publicationethics.org/",
      "required": true,
      "must_accept": true
    }
  }
}
```

#### **D. Supporting Documents (REQUIRED)**

```json
{
  "cv_resume": {
    "description": "Complete academic CV or resume",
    "format": "PDF only",
    "max_size": "10 MB",
    "must_include": [
      "Education history with degrees and institutions",
      "Employment history (current position)",
      "Publications list (all peer-reviewed works)",
      "Grants and funding (if applicable)",
      "Awards and honors (if applicable)",
      "Professional service (editorial boards, etc.)"
    ],
    "required": true,
    "admin_review": "Thorough manual review"
  },

  "degree_certificate": {
    "description": "PhD/terminal degree diploma or certificate",
    "format": "PDF or image (JPG, PNG)",
    "max_size": "5 MB",
    "alternative": "Official transcript OR registrar verification letter",
    "required": true,
    "admin_review": "Manual verification"
  },

  "publication_evidence": {
    "description": "Links or DOIs for your 3 best publications",
    "format": "Text input with URLs",
    "verification": [
      "Must be peer-reviewed journals",
      "Must be indexed in PubMed, Web of Science, or Scopus",
      "Admin will verify author name matches applicant"
    ],
    "required": true
  },

  "institutional_verification": {
    "description": "Verification of current affiliation",
    "options": [
      "Institutional email address (@university.edu)",
      "Department website listing your profile",
      "Letter from department head"
    ],
    "required": true,
    "automatic": "Email domain verification where possible"
  }
}
```

**Application Review Process:**

```
1. Submit Application
   ↓
2. Automatic Verification (ORCID, Google Scholar, email domain)
   ↓ (Pass)
3. Admin Reviews Documents (CV, degree, publications)
   ↓ (2-5 business days)
4. Decision:
   ├─ APPROVED → Access granted, subscription activated
   ├─ DENIED → Email with reason, appeal instructions
   └─ MORE INFO NEEDED → Request additional documents
```

**Appeal Process (If Denied):**

```json
{
  "appeal_submission": {
    "method": "Email to appeals@meta-analysis-platform.com",
    "subject_line": "Tier 2 Application Appeal - [Your Name]",
    "required_content": [
      "Application ID number",
      "Reason for appeal",
      "Additional evidence or clarification",
      "Supporting documents (if applicable)"
    ],
    "response_time": "7 business days"
  },

  "appeal_review": {
    "reviewer": "Senior admin or academic advisory board",
    "criteria": [
      "Were all requirements actually met?",
      "Was there a procedural error?",
      "Are there extenuating circumstances?",
      "Can applicant provide additional verification?"
    ],
    "possible_outcomes": [
      "Appeal approved - access granted",
      "Appeal denied - remain at Tier 1",
      "Request for additional information"
    ]
  },

  "tier_1_access": {
    "guarantee": "Even if denied Tier 2, you retain full Tier 1 access",
    "can_reapply": "Yes, after 6 months or when qualifications improve"
  }
}
```

---

### 2.3 Tier 3: Editor (Editorial Access)

**Purpose:** Approve peer reviews, manage editorial workflow, highest trust level

**Monthly Price:** $149/month
- Includes all Tier 1 + Tier 2 features
- Access to editorial dashboard
- Approve/reject peer reviews
- Assign reviewers to manuscripts
- Final editorial decisions
- Priority support

**Application Requirements:**

#### **A. All Tier 2 Requirements PLUS:**

```json
{
  "enhanced_qualifications": {
    "h_index_requirement": {
      "minimum": 10,
      "field_adjusted": true,
      "adjustments": {
        "mathematics_physics": 10,
        "computer_science_engineering": 12,
        "life_sciences_medicine": 15,
        "social_sciences_humanities": 8
      },
      "verification": "Google Scholar + manual cross-check",
      "required": true
    },

    "publication_requirements": {
      "minimum_total_publications": 10,
      "peer_reviewed_journals": true,
      "impact_factor_requirement": "At least 3 in Q1/Q2 journals",
      "recency": "At least 2 publications in last 3 years",
      "verification": "Manual review of CV + Google Scholar",
      "required": true
    },

    "peer_review_volume": {
      "minimum_reviews": 20,
      "verified_reviews": true,
      "verification_sources": [
        "Publons/Web of Science verified reviews",
        "Letters from 2+ journal editors confirming review count",
        "Editorial board membership documentation"
      ],
      "required": true
    },

    "active_researcher": {
      "definition": "Currently engaged in research",
      "evidence": [
        "Publications in last 3 years",
        "Active grants or funding",
        "Current academic appointment",
        "Conference presentations in last 2 years"
      ],
      "required": true
    }
  }
}
```

#### **B. Editorial Experience (REQUIRED - One of the Following)**

```json
{
  "option_1_editorial_board": {
    "description": "Current or past editorial board membership",
    "acceptable_roles": [
      "Editor-in-Chief",
      "Associate Editor",
      "Section Editor",
      "Editorial Board Member"
    ],
    "journal_requirements": [
      "Peer-reviewed academic journal",
      "Indexed in major database (PubMed, Web of Science, Scopus)",
      "Established publication record (at least 2 years old)"
    ],
    "verification": [
      "Journal website listing your name",
      "Letter from Editor-in-Chief",
      "Contract or appointment letter"
    ],
    "duration": "At least 1 year of service",
    "required_if_choosing_this_option": true
  },

  "option_2_recommendations": {
    "description": "Letters of recommendation from established editors",
    "number_required": 2,
    "recommender_requirements": {
      "current_role": "Editor or Associate Editor at peer-reviewed journal",
      "h_index": "Minimum 15",
      "relationship": "Can attest to your editorial judgment and integrity"
    },
    "letter_must_address": [
      "How long they've known you professionally",
      "Your qualifications for editorial work",
      "Your judgment and decision-making abilities",
      "Your knowledge of peer review best practices",
      "Any specific editorial work they've observed"
    ],
    "format": "Official letterhead, signed, dated within last 6 months",
    "submission": "Direct from recommender to editors@platform.com",
    "required_if_choosing_this_option": true
  },

  "option_3_guest_editor": {
    "description": "Guest editor for special issue or journal",
    "requirements": [
      "Served as guest editor for peer-reviewed journal",
      "Managed at least 5 manuscript submissions",
      "Issue published or in press"
    ],
    "verification": [
      "Published issue listing you as guest editor",
      "Letter from journal Editor-in-Chief",
      "Table of contents with your editorial"
    ],
    "required_if_choosing_this_option": true
  }
}
```

#### **C. Additional Editor Requirements**

```json
{
  "editorial_training": {
    "description": "Evidence of editorial training or knowledge",
    "options": [
      "Completed editorial training course (e.g., EASE, CSE)",
      "Attended editor workshop at major conference",
      "Certification in peer review or editing",
      "Demonstrated knowledge of COPE guidelines"
    ],
    "verification": "Certificate or transcript",
    "required": false,
    "bonus": "Speeds up approval"
  },

  "conflict_management": {
    "question": "Describe your approach to managing conflicts of interest in peer review",
    "format": "500-1000 word essay",
    "evaluation": "Admin reviews for understanding of ethical issues",
    "required": true
  },

  "editorial_philosophy": {
    "question": "What is your philosophy on peer review and editorial decision-making?",
    "format": "500-1000 word essay",
    "evaluation": "Demonstrates thoughtful approach to editorial responsibilities",
    "required": true
  },

  "time_commitment": {
    "question": "How much time per week can you commit to editorial duties?",
    "minimum": "5 hours per week",
    "expected_duties": [
      "Review submitted peer reviews (1-2 hours)",
      "Assign reviewers to manuscripts (1-2 hours)",
      "Make editorial decisions (1-2 hours)",
      "Respond to author/reviewer queries (1 hour)"
    ],
    "required": true
  }
}
```

#### **D. References and Background Check**

```json
{
  "professional_references": {
    "description": "Contact information for 3 professional references",
    "reference_requirements": {
      "relationship": "Colleague, supervisor, or collaborator",
      "duration": "Known you for at least 2 years",
      "can_attest_to": "Your research integrity and professional judgment"
    },
    "admin_will_contact": true,
    "questions_asked": [
      "How long have you known the applicant?",
      "In what capacity?",
      "Can you attest to their research integrity?",
      "Would you trust them with editorial decisions?",
      "Any concerns we should be aware of?"
    ],
    "required": true
  },

  "ethics_verification": {
    "description": "Background check for research misconduct",
    "checks": [
      "ORI (Office of Research Integrity) database search",
      "Retraction Watch database search",
      "PubPeer flagged publications",
      "Self-disclosure of any investigations"
    ],
    "disqualifying_findings": [
      "Confirmed research misconduct",
      "Unreported conflicts of interest with consequences",
      "Multiple retractions for ethical reasons"
    ],
    "required": true,
    "automatic": "Admin performs searches"
  }
}
```

**Application Review Process:**

```
1. Submit Tier 3 Application (must already be approved Tier 2)
   ↓
2. Automatic Verification (H-index, publication count, ORCID)
   ↓ (Pass)
3. Senior Admin Reviews Documents
   ├─ CV and publications (verify quality)
   ├─ Editorial experience (verify authenticity)
   ├─ Letters of recommendation (assess quality)
   └─ Essays (evaluate editorial philosophy)
   ↓ (5-10 business days)
4. Reference Checks (admin contacts 3 references)
   ↓
5. Ethics Background Check (ORI, Retraction Watch, PubPeer)
   ↓
6. Academic Advisory Board Review (if borderline case)
   ↓
7. Final Decision:
   ├─ APPROVED → Access granted, subscription activated
   ├─ DENIED → Email with reason, appeal instructions
   └─ MORE INFO NEEDED → Request additional documents/clarification
```

**Appeal Process (If Denied):**

```json
{
  "appeal_submission": {
    "method": "Email to editor-appeals@meta-analysis-platform.com",
    "required_content": [
      "Application ID",
      "Detailed reason for appeal",
      "Additional evidence of qualifications",
      "Explanation of any concerns raised"
    ],
    "response_time": "10 business days"
  },

  "appeal_review": {
    "reviewer": "Academic Advisory Board (3 independent senior editors)",
    "blind_review": "Applicant identity hidden from board",
    "decision_final": true,
    "possible_outcomes": [
      "Appeal approved - Tier 3 access granted",
      "Appeal denied - remain at Tier 2",
      "Conditional approval - probationary period (90 days)"
    ]
  },

  "probationary_approval": {
    "description": "Conditional Tier 3 access with monitoring",
    "duration": "90 days",
    "requirements": [
      "Review and approve at least 10 peer reviews",
      "Maintain quality standards (no valid complaints)",
      "Respond to authors/reviewers promptly",
      "Follow COPE guidelines"
    ],
    "evaluation": "After 90 days, full approval or revert to Tier 2",
    "monitoring": "Senior admin reviews all decisions"
  }
}
```

---

## 3. PRICING & REVENUE MODEL

### 3.1 Subscription Pricing

```
┌────────────────────────────────────────────────────────┐
│                  TIER 1: RESEARCHER                    │
│                                                        │
│  FREE PLAN:                                            │
│    Price: $0/month                                     │
│    Features:                                           │
│      • 3 meta-analyses per month                      │
│      • Watermarked reports                             │
│      • Research direction tool (limited)               │
│      • Knowledge base access                           │
│                                                        │
│  PAID PLAN:                                            │
│    Price: $49/month                                    │
│    Features:                                           │
│      • Unlimited meta-analyses                         │
│      • Publication-ready reports (no watermark)        │
│      • Research direction tool (full access)           │
│      • Priority support                                │
│      • Export to multiple formats                      │
│      • Advanced analytics                              │
│                                                        │
│  Annual Discount: $490/year (save $98 = 2 months)     │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                 TIER 2: PEER REVIEWER                  │
│                                                        │
│  Price: $99/month                                      │
│  Includes: All Tier 1 Paid features PLUS:             │
│    • Access to peer review tool                        │
│    • Eligible for reviewer matching                    │
│    • Earn $20-50 per approved review                   │
│    • Contribute $20/month to payout pool               │
│    • Reviewer dashboard with analytics                 │
│    • Professional profile page                         │
│    • Continuing education credits (CEU)                │
│                                                        │
│  Earnings Potential:                                   │
│    • 2 reviews/month = $40-100 earned                  │
│    • Net cost: $99 - $70 (avg) = $29/month             │
│    • Active reviewers often break even or profit       │
│                                                        │
│  Annual Discount: $990/year (save $198 = 2 months)    │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                    TIER 3: EDITOR                      │
│                                                        │
│  Price: $149/month                                     │
│  Includes: All Tier 1 + Tier 2 features PLUS:         │
│    • Editorial dashboard                               │
│    • Review approval workflow                          │
│    • Manuscript assignment tools                       │
│    • All 4 platform tools (full access)                │
│    • Quality control analytics                         │
│    • Direct support line                               │
│    • Platform governance participation                 │
│    • Editor recognition badge                          │
│                                                        │
│  Contribution to Payout Pool: $30/month                │
│  Net Cost After Typical Reviews: ~$49-99/month         │
│                                                        │
│  Annual Discount: $1,490/year (save $298 = 2 months)  │
└────────────────────────────────────────────────────────┘
```

### 3.2 Revenue Breakdown

```
Example: 100 Active Users

Tier 1 (50 users @ $49/month):
├─ Monthly Revenue: $2,450
└─ Annual Revenue: $29,400

Tier 2 (40 users @ $99/month):
├─ Monthly Revenue: $3,960
├─ Payout Pool Contribution: $800 ($20 × 40)
├─ Platform Revenue: $3,160
└─ Annual Platform Revenue: $37,920

Tier 3 (10 users @ $149/month):
├─ Monthly Revenue: $1,490
├─ Payout Pool Contribution: $300 ($30 × 10)
├─ Platform Revenue: $1,190
└─ Annual Platform Revenue: $14,280

Total Monthly Revenue: $7,900
Total Payout Pool: $1,100/month ($13,200/year)
Total Platform Revenue: $6,800/month ($81,600/year)

Operating Costs: ~$2,000-3,000/month
Net Profit: ~$4,500-5,500/month ($54,000-66,000/year)
Profit Margin: 65-70%
```

### 3.3 Payout Pool Distribution

```
Reviewer Earnings Model:

Monthly Pool: $1,100 (from example above)
Total Approved Reviews: 50 (across all reviewers)

Base Payout per Review: $1,100 ÷ 50 = $22

Quality Multiplier:
├─ 5.0 stars (exceptional): 1.5× = $33 per review
├─ 4.0-4.9 stars (excellent): 1.2× = $26.40 per review
├─ 3.5-3.9 stars (good): 1.0× = $22 per review
└─ Below 3.5 (needs improvement): 0.5× = $11 per review

Example Reviewer (Tier 2):
├─ Completed 3 reviews this month
├─ Average rating: 4.5 stars
├─ Earnings: 3 × $26.40 = $79.20
├─ Subscription cost: $99
├─ Net cost: $19.80/month

Active reviewers who maintain quality often break even or earn money.
```

---

## 4. APPLICATION & APPROVAL WORKFLOW

### 4.1 User Journey Maps

#### **Journey 1: Researcher → Peer Reviewer Application**

```
Step 1: Register as Tier 1 (Free or Paid)
├─ Complete basic registration
├─ Verify email address
└─ Access meta-analysis tools

Step 2: Explore Platform (days/weeks)
├─ Create meta-analyses
├─ Use research direction tool
├─ See "Become a Reviewer" call-to-action
└─ Click "Apply for Tier 2"

Step 3: Application Page
├─ Review qualification requirements
├─ See expected approval timeline (2-5 days)
├─ Understand pricing ($99/month)
└─ Click "Start Application"

Step 4: Complete Application Form
├─ Part 1: Academic Credentials
│   ├─ Degree information
│   ├─ Upload degree certificate
│   ├─ Upload CV/Resume
│   └─ Link ORCID and Google Scholar
│
├─ Part 2: Research Expertise
│   ├─ Select domains (1-5)
│   ├─ Add keywords (10-30)
│   └─ Choose methodologies (3+)
│
├─ Part 3: Peer Review Experience
│   ├─ Total reviews completed (min 3)
│   ├─ Journals reviewed for
│   ├─ Review capacity and timeframe
│   └─ Languages
│
├─ Part 4: Publications
│   ├─ Provide DOIs/URLs for 3 best papers
│   └─ Auto-verify via CrossRef/PubMed
│
└─ Part 5: Ethics & Compliance
    ├─ Conflicts of interest disclosure
    ├─ Research misconduct question
    └─ Accept COPE guidelines

Step 5: Submit Application
├─ Review all information
├─ Digital signature
├─ Submit for review
└─ Receive confirmation email

Step 6: Automatic Verification (1-24 hours)
├─ ORCID profile verified via API
├─ Google Scholar scraped and validated
├─ Email domain checked (institutional?)
├─ Publication DOIs validated via CrossRef
└─ If all pass → move to manual review

Step 7: Manual Admin Review (2-5 business days)
├─ Admin reviews CV and degree certificate
├─ Verifies publication quality (journal rankings)
├─ Checks journals reviewed for (may contact editors)
├─ Reviews ethical disclosures
└─ Makes decision: APPROVE / DENY / MORE INFO

Step 8A: APPROVED
├─ Receive approval email
├─ Subscription automatically created
├─ Charge $99/month
├─ Access to Tier 2 features granted
├─ Profile badge updated: "Verified Reviewer"
└─ Welcome to reviewer dashboard

Step 8B: DENIED
├─ Receive denial email with specific reasons
├─ Appeal instructions provided
├─ Still retain full Tier 1 access
└─ Can reapply in 6 months

Step 8C: MORE INFO NEEDED
├─ Email requesting specific additional documents
├─ 14-day deadline to provide info
└─ Review continues once submitted

Step 9: Appeal Process (if denied)
├─ Email appeals@platform.com with case
├─ Provide additional evidence
├─ Senior admin or advisory board reviews
├─ Final decision within 7 days
└─ If approved → Step 8A; if denied → remain Tier 1
```

#### **Journey 2: Peer Reviewer → Editor Application**

```
Step 1: Must be Approved Tier 2 Reviewer
├─ Active subscription for at least 3 months
├─ Completed at least 5 peer reviews
├─ Average review quality ≥ 4.0/5.0
└─ No ethical violations

Step 2: Editor Application CTA
├─ See "Apply to Become an Editor" in dashboard
├─ Review enhanced qualification requirements
├─ Understand pricing ($149/month, includes Tier 2)
└─ Click "Apply for Tier 3"

Step 3: Enhanced Application Form
├─ Part 1: All Tier 2 info pre-filled and re-verified
│
├─ Part 2: Enhanced Qualifications
│   ├─ H-index verification (minimum 10)
│   ├─ Publication count (minimum 10 peer-reviewed)
│   └─ Recent publications (2+ in last 3 years)
│
├─ Part 3: Editorial Experience (Choose ONE)
│   ├─ Option A: Editorial board membership
│   │   ├─ Journal name and role
│   │   ├─ Duration of service
│   │   ├─ Upload verification (website screenshot OR letter)
│   │   └─ Contact info for Editor-in-Chief
│   │
│   ├─ Option B: Letters of recommendation (2 required)
│   │   ├─ Recommender 1 details (name, institution, role)
│   │   ├─ Recommender 2 details
│   │   ├─ Letters sent directly to editors@platform.com
│   │   └─ Must be from current journal editors
│   │
│   └─ Option C: Guest editor experience
│       ├─ Journal and special issue details
│       ├─ Number of manuscripts handled
│       └─ Upload published issue or letter
│
├─ Part 4: Editorial Philosophy Essays
│   ├─ Conflict of interest management (500-1000 words)
│   └─ Peer review philosophy (500-1000 words)
│
├─ Part 5: Professional References
│   ├─ Reference 1: Name, email, phone, relationship
│   ├─ Reference 2: Name, email, phone, relationship
│   └─ Reference 3: Name, email, phone, relationship
│
└─ Part 6: Time Commitment
    ├─ Hours per week available (minimum 5)
    └─ Start date preference

Step 4: Submit Application
├─ Review all information
├─ Digital signature confirming accuracy
├─ Submit for senior admin review
└─ Receive confirmation email

Step 5: Automatic Enhanced Verification (1-24 hours)
├─ H-index check via Google Scholar
├─ Publication count validation
├─ Recent publication verification
├─ Background check initiation:
│   ├─ ORI database search
│   ├─ Retraction Watch search
│   └─ PubPeer search
└─ If all pass → move to manual review

Step 6: Senior Admin Review (5-10 business days)
├─ Verify editorial experience authenticity
├─ Read and evaluate essays for editorial judgment
├─ Review CV for leadership and service
├─ Check background searches for red flags
└─ Make preliminary decision

Step 7: Reference Checks (2-3 days)
├─ Admin contacts 3 professional references
├─ Asks standardized questions about applicant
├─ Records responses
└─ Evaluates overall recommendation strength

Step 8: Advisory Board Review (if needed)
├─ Borderline cases go to Academic Advisory Board
├─ 3 independent senior editors review blind application
├─ Vote on approval
└─ Final decision made

Step 9A: APPROVED (Full Approval)
├─ Receive approval email
├─ Tier 2 subscription upgraded to Tier 3
├─ Charge $149/month (prorated for current month)
├─ Access to editorial dashboard granted
├─ Profile badge: "Verified Editor"
└─ Welcome to editorial team

Step 9B: APPROVED (Probationary)
├─ Conditional approval for 90 days
├─ Full access but all decisions monitored
├─ Must approve 10 reviews with quality
├─ Re-evaluation after 90 days
└─ Either full approval or revert to Tier 2

Step 9C: DENIED
├─ Receive denial email with specific reasons
├─ Appeal instructions (to academic board)
├─ Remain at Tier 2 with full access
└─ Can reapply in 12 months

Step 10: Appeal Process (if denied)
├─ Submit appeal to editor-appeals@platform.com
├─ Academic Advisory Board reviews
├─ Blind review process (identity hidden)
├─ Final decision within 10 days
├─ No further appeals (decision is final)
└─ If approved → Step 9A or 9B; if denied → Tier 2
```

---

## 5. DATABASE MODEL UPDATES

### 5.1 New Models Required

```python
# app/models/tier_applications.py

from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum
import uuid
from datetime import datetime
from app.db.base_class import Base

class ApplicationTier(str, enum.Enum):
    """Tier being applied for"""
    TIER_2_REVIEWER = "tier_2_reviewer"
    TIER_3_EDITOR = "tier_3_editor"

class ApplicationStatus(str, enum.Enum):
    """Application status"""
    SUBMITTED = "submitted"
    AUTO_VERIFICATION_IN_PROGRESS = "auto_verification_in_progress"
    AUTO_VERIFICATION_PASSED = "auto_verification_passed"
    AUTO_VERIFICATION_FAILED = "auto_verification_failed"
    MANUAL_REVIEW_PENDING = "manual_review_pending"
    MANUAL_REVIEW_IN_PROGRESS = "manual_review_in_progress"
    REFERENCES_CHECK_IN_PROGRESS = "references_check_in_progress"
    ADVISORY_BOARD_REVIEW = "advisory_board_review"
    MORE_INFO_REQUESTED = "more_info_requested"
    APPROVED = "approved"
    DENIED = "denied"
    APPEALED = "appealed"
    APPEAL_APPROVED = "appeal_approved"
    APPEAL_DENIED = "appeal_denied"

class DenialReason(str, enum.Enum):
    """Reasons for denial"""
    INSUFFICIENT_PUBLICATIONS = "insufficient_publications"
    DEGREE_NOT_VERIFIED = "degree_not_verified"
    H_INDEX_TOO_LOW = "h_index_too_low"
    INSUFFICIENT_REVIEW_EXPERIENCE = "insufficient_review_experience"
    NO_EDITORIAL_EXPERIENCE = "no_editorial_experience"
    ETHICAL_CONCERNS = "ethical_concerns"
    RESEARCH_MISCONDUCT_FOUND = "research_misconduct_found"
    WEAK_REFERENCES = "weak_references"
    INCOMPLETE_APPLICATION = "incomplete_application"
    OTHER = "other"

class TierApplication(Base):
    """
    Application for Tier 2 (Reviewer) or Tier 3 (Editor) access.
    """
    __tablename__ = "tier_applications"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Application details
    tier_applied_for = Column(Enum(ApplicationTier), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False)

    # Academic credentials
    degree_type = Column(String(100))  # PhD, MD, JD, etc.
    degree_institution = Column(String(255))
    degree_field = Column(String(255))
    degree_year = Column(Integer)

    # Document uploads (file paths)
    degree_certificate_path = Column(String(500))
    cv_resume_path = Column(String(500))

    # ORCID verification
    orcid_id = Column(String(19))  # 0000-0001-2345-6789
    orcid_verified = Column(Boolean, default=False)
    orcid_verification_date = Column(DateTime)
    orcid_data = Column(JSONB)  # Fetched from ORCID API

    # Google Scholar verification
    google_scholar_url = Column(String(500))
    google_scholar_verified = Column(Boolean, default=False)
    google_scholar_verification_date = Column(DateTime)
    google_scholar_data = Column(JSONB)  # Scraped data
    h_index = Column(Integer)
    total_citations = Column(Integer)

    # Publications
    publication_dois = Column(JSONB)  # List of DOIs for key publications
    total_peer_reviewed_publications = Column(Integer)
    publications_last_3_years = Column(Integer)

    # Peer review experience (Tier 2)
    total_reviews_completed = Column(Integer)
    journals_reviewed_for = Column(JSONB)  # List of {journal, years, count}
    publons_profile_url = Column(String(500))
    max_concurrent_reviews = Column(Integer)
    preferred_review_timeframe_days = Column(Integer)
    review_languages = Column(JSONB)  # List of language codes

    # Editorial experience (Tier 3 only)
    editorial_experience_type = Column(String(50))  # "board", "recommendations", "guest_editor"
    editorial_board_journal = Column(String(255))
    editorial_board_role = Column(String(100))
    editorial_board_years = Column(String(50))
    editorial_board_verification_path = Column(String(500))
    guest_editor_details = Column(JSONB)

    # Letters of recommendation (Tier 3 only)
    recommendation_letters = Column(JSONB)  # List of {recommender, institution, received_date, file_path}

    # Essays (Tier 3 only)
    conflict_management_essay = Column(Text)
    editorial_philosophy_essay = Column(Text)

    # References (Tier 3 only)
    professional_references = Column(JSONB)  # List of {name, email, phone, relationship}
    references_contacted = Column(Boolean, default=False)
    reference_responses = Column(JSONB)  # Admin notes from reference calls

    # Ethics and compliance
    conflicts_of_interest_disclosed = Column(Boolean)
    conflict_details = Column(Text)
    research_misconduct_question = Column(Boolean)  # Have you been found responsible?
    misconduct_details = Column(Text)
    cope_guidelines_accepted = Column(Boolean)

    # Background checks (automatic)
    ori_check_performed = Column(Boolean, default=False)
    ori_check_date = Column(DateTime)
    ori_findings = Column(Text)
    retraction_watch_check_performed = Column(Boolean, default=False)
    retraction_watch_findings = Column(JSONB)
    pubpeer_check_performed = Column(Boolean, default=False)
    pubpeer_findings = Column(JSONB)

    # Review process
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    auto_verification_completed_at = Column(DateTime)
    manual_review_started_at = Column(DateTime)
    manual_review_completed_at = Column(DateTime)
    reviewed_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Decision
    decision_made_at = Column(DateTime)
    approved = Column(Boolean)
    denial_reasons = Column(JSONB)  # List of DenialReason values
    denial_explanation = Column(Text)
    admin_notes = Column(Text)

    # Appeal
    appeal_submitted = Column(Boolean, default=False)
    appeal_submitted_at = Column(DateTime)
    appeal_reason = Column(Text)
    appeal_additional_evidence = Column(JSONB)
    appeal_reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    appeal_decided_at = Column(DateTime)
    appeal_approved = Column(Boolean)
    appeal_explanation = Column(Text)

    # Probationary approval (Tier 3 only)
    probationary_approval = Column(Boolean, default=False)
    probationary_start_date = Column(DateTime)
    probationary_end_date = Column(DateTime)
    probationary_reviews_required = Column(Integer, default=10)
    probationary_reviews_completed = Column(Integer, default=0)
    probationary_quality_threshold = Column(Float, default=4.0)
    probationary_evaluation_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels"""
    TIER_1_FREE = "tier_1_free"
    TIER_1_PAID = "tier_1_paid"
    TIER_2_REVIEWER = "tier_2_reviewer"
    TIER_3_EDITOR = "tier_3_editor"


# Update existing Subscription model
class Subscription(Base):
    """Enhanced subscription model with tier support"""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Tier information
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.TIER_1_FREE, nullable=False)

    # Pricing
    monthly_amount_cents = Column(Integer)  # 0, 4900, 9900, or 14900
    payout_contribution_cents = Column(Integer, default=0)  # 0, 0, 2000, or 3000

    # Stripe
    stripe_subscription_id = Column(String(255))
    stripe_customer_id = Column(String(255))
    stripe_price_id = Column(String(255))

    # Status
    status = Column(String(50))  # active, canceled, past_due, etc.
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QualificationVerification(Base):
    """Track verification attempts for researcher qualifications"""
    __tablename__ = "qualification_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey("tier_applications.id", ondelete="CASCADE"))

    # Verification type
    verification_type = Column(String(50))  # "orcid", "google_scholar", "pubmed", "crossref"

    # Results
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime, default=datetime.utcnow)
    data_retrieved = Column(JSONB)
    error_message = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 5.2 Update User Model

```python
# app/models/user.py (additions)

class UserRole(str, enum.Enum):
    """Enhanced user roles aligned with tiers"""
    TIER_1_RESEARCHER = "tier_1_researcher"  # Default for all new users
    TIER_2_REVIEWER = "tier_2_reviewer"      # Approved reviewer
    TIER_3_EDITOR = "tier_3_editor"          # Approved editor
    ADMIN = "admin"                          # Platform admin
    SUPER_ADMIN = "super_admin"              # Full system access

class User(Base):
    __tablename__ = "users"

    # ... existing fields ...

    # Tier and role
    current_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.TIER_1_FREE)
    role = Column(Enum(UserRole), default=UserRole.TIER_1_RESEARCHER)

    # Verification status
    credentials_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)

    # Profile badges
    verified_researcher_badge = Column(Boolean, default=False)
    verified_reviewer_badge = Column(Boolean, default=False)
    verified_editor_badge = Column(Boolean, default=False)

    # Application tracking
    has_pending_tier_2_application = Column(Boolean, default=False)
    has_pending_tier_3_application = Column(Boolean, default=False)
    tier_2_approval_date = Column(DateTime)
    tier_3_approval_date = Column(DateTime)

    # Quality metrics (for reviewers/editors)
    total_reviews_completed = Column(Integer, default=0)
    average_review_quality_score = Column(Float)
    total_reviews_approved = Column(Integer, default=0)
    total_reviews_rejected = Column(Integer, default=0)

    # ... rest of existing fields ...
```

---

## 6. API ENDPOINTS NEEDED

### 6.1 Tier Application Endpoints

```python
# app/api/v1/tier_applications.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from uuid import UUID
from app.models.tier_applications import TierApplication, ApplicationTier, ApplicationStatus
from app.schemas.tier_applications import *

router = APIRouter(prefix="/tier-applications", tags=["tier-applications"])

@router.post("/tier-2/apply", response_model=TierApplicationResponse)
async def apply_for_tier_2(
    application_data: Tier2ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit Tier 2 (Peer Reviewer) application.

    Requirements:
    - User must be at least Tier 1
    - No pending applications
    - Complete all required fields
    - Upload CV and degree certificate
    """
    # Check eligibility
    if current_user.has_pending_tier_2_application:
        raise HTTPException(400, "You already have a pending Tier 2 application")

    if current_user.current_tier == SubscriptionTier.TIER_2_REVIEWER:
        raise HTTPException(400, "You are already a Tier 2 reviewer")

    # Create application
    application = TierApplication(
        user_id=current_user.id,
        tier_applied_for=ApplicationTier.TIER_2_REVIEWER,
        status=ApplicationStatus.SUBMITTED,
        **application_data.dict()
    )
    db.add(application)

    # Mark user as having pending application
    current_user.has_pending_tier_2_application = True

    await db.commit()
    await db.refresh(application)

    # Trigger automatic verification (background task)
    background_tasks.add_task(run_automatic_verification, application.id)

    # Send confirmation email
    background_tasks.add_task(
        send_email,
        to=current_user.email,
        subject="Tier 2 Application Received",
        template="tier_2_application_submitted.html",
        context={"user": current_user, "application": application}
    )

    return application


@router.post("/tier-3/apply", response_model=TierApplicationResponse)
async def apply_for_tier_3(
    application_data: Tier3ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit Tier 3 (Editor) application.

    Requirements:
    - User must be approved Tier 2 reviewer
    - Active Tier 2 subscription for at least 3 months
    - Completed at least 5 reviews with avg quality ≥ 4.0
    - No pending applications
    """
    # Check eligibility
    if current_user.current_tier != SubscriptionTier.TIER_2_REVIEWER:
        raise HTTPException(400, "Must be an approved Tier 2 reviewer to apply for Tier 3")

    if current_user.has_pending_tier_3_application:
        raise HTTPException(400, "You already have a pending Tier 3 application")

    # Check subscription duration
    tier_2_duration = (datetime.utcnow() - current_user.tier_2_approval_date).days
    if tier_2_duration < 90:
        raise HTTPException(400, f"Must be Tier 2 for at least 90 days (current: {tier_2_duration} days)")

    # Check review performance
    if current_user.total_reviews_completed < 5:
        raise HTTPException(400, "Must have completed at least 5 peer reviews")

    if current_user.average_review_quality_score < 4.0:
        raise HTTPException(400, f"Average review quality must be ≥ 4.0 (current: {current_user.average_review_quality_score:.2f})")

    # Create application
    application = TierApplication(
        user_id=current_user.id,
        tier_applied_for=ApplicationTier.TIER_3_EDITOR,
        status=ApplicationStatus.SUBMITTED,
        **application_data.dict()
    )
    db.add(application)

    # Mark user as having pending application
    current_user.has_pending_tier_3_application = True

    await db.commit()
    await db.refresh(application)

    # Trigger enhanced verification (background task)
    background_tasks.add_task(run_enhanced_verification, application.id)

    # Send confirmation email
    background_tasks.add_task(
        send_email,
        to=current_user.email,
        subject="Tier 3 Application Received",
        template="tier_3_application_submitted.html",
        context={"user": current_user, "application": application}
    )

    return application


@router.post("/{application_id}/upload-cv", response_model=UploadResponse)
async def upload_cv(
    application_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload CV/Resume for application."""
    application = await db.get(TierApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(404, "Application not found")

    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")

    if file.size > 10 * 1024 * 1024:  # 10 MB
        raise HTTPException(400, "File size must be less than 10 MB")

    # Save file to storage
    file_path = await save_upload_to_storage(file, f"cv/{application_id}")

    # Update application
    application.cv_resume_path = file_path
    await db.commit()

    return {"file_path": file_path, "message": "CV uploaded successfully"}


@router.post("/{application_id}/upload-degree", response_model=UploadResponse)
async def upload_degree_certificate(
    application_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload degree certificate for application."""
    # Similar to upload_cv but for degree certificate
    # ... implementation ...


@router.get("/my-applications", response_model=List[TierApplicationResponse])
async def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all applications for current user."""
    result = await db.execute(
        select(TierApplication)
        .where(TierApplication.user_id == current_user.id)
        .order_by(TierApplication.created_at.desc())
    )
    applications = result.scalars().all()
    return applications


@router.get("/{application_id}", response_model=TierApplicationDetailResponse)
async def get_application_details(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a specific application."""
    application = await db.get(TierApplication, application_id)

    if not application:
        raise HTTPException(404, "Application not found")

    # Users can only view their own applications (unless admin)
    if application.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(403, "Not authorized to view this application")

    return application


@router.post("/{application_id}/appeal", response_model=AppealResponse)
async def submit_appeal(
    application_id: UUID,
    appeal_data: AppealSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit an appeal for a denied application.

    Requirements:
    - Application must be denied
    - Cannot already have pending appeal
    - Must provide reason and any additional evidence
    """
    application = await db.get(TierApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(404, "Application not found")

    if application.status != ApplicationStatus.DENIED:
        raise HTTPException(400, "Can only appeal denied applications")

    if application.appeal_submitted:
        raise HTTPException(400, "Appeal already submitted for this application")

    # Update application with appeal
    application.appeal_submitted = True
    application.appeal_submitted_at = datetime.utcnow()
    application.appeal_reason = appeal_data.reason
    application.appeal_additional_evidence = appeal_data.additional_evidence
    application.status = ApplicationStatus.APPEALED

    await db.commit()

    # Notify admin team
    background_tasks.add_task(
        send_admin_notification,
        subject=f"New Appeal: {current_user.full_name}",
        message=f"User {current_user.email} has appealed application {application_id}"
    )

    # Send confirmation to user
    background_tasks.add_task(
        send_email,
        to=current_user.email,
        subject="Appeal Submitted",
        template="appeal_submitted.html",
        context={"user": current_user, "application": application}
    )

    return {
        "message": "Appeal submitted successfully",
        "application_id": application_id,
        "expected_response_time_days": 7 if application.tier_applied_for == ApplicationTier.TIER_2_REVIEWER else 10
    }


@router.get("/status/{application_id}", response_model=ApplicationStatusResponse)
async def check_application_status(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check the current status of an application."""
    application = await db.get(TierApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(404, "Application not found")

    # Calculate estimated time remaining
    status_timeline = get_status_timeline(application)

    return {
        "application_id": application_id,
        "status": application.status,
        "submitted_at": application.submitted_at,
        "estimated_decision_date": status_timeline.estimated_decision_date,
        "days_in_review": (datetime.utcnow() - application.submitted_at).days,
        "current_step": status_timeline.current_step,
        "total_steps": status_timeline.total_steps,
        "can_appeal": application.status == ApplicationStatus.DENIED and not application.appeal_submitted
    }
```

### 6.2 Admin Review Endpoints

```python
# app/api/v1/admin/tier_applications.py

router = APIRouter(prefix="/admin/tier-applications", tags=["admin", "tier-applications"])

@router.get("/pending", response_model=List[TierApplicationSummary])
async def get_pending_applications(
    tier: Optional[ApplicationTier] = None,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all pending applications for admin review."""
    query = select(TierApplication).where(
        TierApplication.status.in_([
            ApplicationStatus.MANUAL_REVIEW_PENDING,
            ApplicationStatus.AUTO_VERIFICATION_PASSED
        ])
    )

    if tier:
        query = query.where(TierApplication.tier_applied_for == tier)

    query = query.order_by(TierApplication.submitted_at.asc())

    result = await db.execute(query)
    applications = result.scalars().all()
    return applications


@router.post("/{application_id}/review", response_model=ReviewDecisionResponse)
async def review_application(
    application_id: UUID,
    decision: AdminReviewDecision,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin reviews and makes decision on application.

    Possible actions:
    - APPROVE: Grant access to requested tier
    - DENY: Reject application with reasons
    - REQUEST_MORE_INFO: Ask applicant for additional documents
    - PROBATIONARY_APPROVE: Conditional approval (Tier 3 only)
    """
    application = await db.get(TierApplication, application_id)

    if not application:
        raise HTTPException(404, "Application not found")

    if decision.action == "APPROVE":
        await approve_application(application, current_admin, db)
    elif decision.action == "DENY":
        await deny_application(application, decision.reasons, decision.explanation, current_admin, db)
    elif decision.action == "REQUEST_MORE_INFO":
        await request_more_info(application, decision.requested_info, current_admin, db)
    elif decision.action == "PROBATIONARY_APPROVE":
        if application.tier_applied_for != ApplicationTier.TIER_3_EDITOR:
            raise HTTPException(400, "Probationary approval only available for Tier 3")
        await probationary_approve(application, current_admin, db)

    await db.commit()

    return {"application_id": application_id, "decision": decision.action, "message": "Decision recorded"}


async def approve_application(
    application: TierApplication,
    admin: User,
    db: AsyncSession
):
    """Approve application and grant tier access."""
    application.status = ApplicationStatus.APPROVED
    application.approved = True
    application.decision_made_at = datetime.utcnow()
    application.reviewed_by_admin_id = admin.id

    # Update user tier and role
    user = await db.get(User, application.user_id)

    if application.tier_applied_for == ApplicationTier.TIER_2_REVIEWER:
        user.current_tier = SubscriptionTier.TIER_2_REVIEWER
        user.role = UserRole.TIER_2_REVIEWER
        user.tier_2_approval_date = datetime.utcnow()
        user.verified_reviewer_badge = True
        user.has_pending_tier_2_application = False

        # Create subscription (Stripe integration)
        await create_tier_2_subscription(user, db)

    elif application.tier_applied_for == ApplicationTier.TIER_3_EDITOR:
        user.current_tier = SubscriptionTier.TIER_3_EDITOR
        user.role = UserRole.TIER_3_EDITOR
        user.tier_3_approval_date = datetime.utcnow()
        user.verified_editor_badge = True
        user.has_pending_tier_3_application = False

        # Upgrade subscription (Stripe integration)
        await upgrade_to_tier_3_subscription(user, db)

    user.credentials_verified = True
    user.verification_date = datetime.utcnow()

    # Send approval email
    await send_email(
        to=user.email,
        subject=f"Application Approved - Welcome to Tier {application.tier_applied_for.value.split('_')[1]}!",
        template="application_approved.html",
        context={"user": user, "application": application, "tier": application.tier_applied_for}
    )


async def deny_application(
    application: TierApplication,
    reasons: List[DenialReason],
    explanation: str,
    admin: User,
    db: AsyncSession
):
    """Deny application with reasons."""
    application.status = ApplicationStatus.DENIED
    application.approved = False
    application.denial_reasons = [r.value for r in reasons]
    application.denial_explanation = explanation
    application.decision_made_at = datetime.utcnow()
    application.reviewed_by_admin_id = admin.id

    # Update user
    user = await db.get(User, application.user_id)
    if application.tier_applied_for == ApplicationTier.TIER_2_REVIEWER:
        user.has_pending_tier_2_application = False
    else:
        user.has_pending_tier_3_application = False

    # Send denial email with appeal instructions
    await send_email(
        to=user.email,
        subject="Application Decision - Appeal Available",
        template="application_denied.html",
        context={
            "user": user,
            "application": application,
            "reasons": reasons,
            "explanation": explanation,
            "appeal_email": "appeals@meta-analysis-platform.com"
        }
    )
```

---

## 7. FRONTEND COMPONENTS

### 7.1 Application Flow Components

```typescript
// frontend/src/pages/onboarding/tier-2-application.tsx

import { useState } from 'react';
import { useRouter } from 'next/router';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { ApplicationWizard } from '@/components/onboarding/ApplicationWizard';
import { Tier2Requirements } from '@/components/onboarding/Tier2Requirements';

export default function Tier2ApplicationPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);

  const applicationMutation = useMutation({
    mutationFn: (data) => api.post('/tier-applications/tier-2/apply', data),
    onSuccess: (data) => {
      router.push(`/applications/${data.application_id}/status`);
    }
  });

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-4xl font-bold mb-4">Apply for Tier 2: Peer Reviewer</h1>

      <Tier2Requirements className="mb-8" />

      <ApplicationWizard
        totalSteps={5}
        currentStep={currentStep}
        onStepChange={setCurrentStep}
        onSubmit={applicationMutation.mutate}
        loading={applicationMutation.isLoading}
      >
        <Step1AcademicCredentials />
        <Step2ResearchExpertise />
        <Step3PeerReviewExperience />
        <Step4Publications />
        <Step5EthicsCompliance />
      </ApplicationWizard>
    </div>
  );
}
```

---

This is Part 1 of the 3-Tier System Design. Would you like me to continue with:
- Part 2: Detailed implementation code for automatic verification
- Part 3: Email templates and admin dashboard
- Part 4: Testing strategy for the new tier system
- Or jump straight into implementing this system?

Let me know which part you'd like to focus on next!
