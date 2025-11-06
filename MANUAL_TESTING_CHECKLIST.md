# MANUAL TESTING CHECKLIST
## Meta-Analysis Research Platform

**Version:** 1.0
**Date:** 2025-11-05
**Tester Name:** _________________
**Environment:** Production / Staging / Local

---

## Instructions

This checklist complements the automated test suite. Some tests require human judgment and cannot be fully automated.

**How to use:**
1. Complete tests in order (dependencies exist)
2. Mark each test: ✅ PASS | ❌ FAIL | ⚠️ DEGRADED | ⊘ SKIP
3. Record actual results in the "Notes" column
4. Take screenshots for any failures
5. Report bugs using the Bug Report Template

---

## Test Category 1: User Interface & Experience

### 1.1 Registration & Login UI

| ID | Test | Status | Notes |
|----|------|--------|-------|
| UI-1.1 | Registration form displays all fields correctly | ☐ | |
| UI-1.2 | Password field masks characters | ☐ | |
| UI-1.3 | "Show password" toggle works | ☐ | |
| UI-1.4 | Error messages display in red below fields | ☐ | |
| UI-1.5 | Success message after registration | ☐ | |
| UI-1.6 | Login form remembers email (optional) | ☐ | |
| UI-1.7 | "Forgot password" link present | ☐ | |
| UI-1.8 | Responsive design works on mobile | ☐ | |

### 1.2 Dashboard UI

| ID | Test | Status | Notes |
|----|------|--------|-------|
| UI-2.1 | Dashboard loads within 3 seconds | ☐ | |
| UI-2.2 | "Create New Project" button prominently displayed | ☐ | |
| UI-2.3 | Recent projects list shows correctly | ☐ | |
| UI-2.4 | Project cards show status badges | ☐ | |
| UI-2.5 | Navigation menu accessible | ☐ | |
| UI-2.6 | User profile menu in top-right | ☐ | |
| UI-2.7 | Logout button works | ☐ | |

### 1.3 Search Configuration UI

| ID | Test | Status | Notes |
|----|------|--------|-------|
| UI-3.1 | Research question text area large enough (3+ lines) | ☐ | |
| UI-3.2 | Database checkboxes clearly labeled | ☐ | |
| UI-3.3 | All 4 databases shown: PubMed, arXiv, Europe PMC, CORE | ☐ | |
| UI-3.4 | Search terms input accepts comma-separated values | ☐ | |
| UI-3.5 | Date range picker intuitive | ☐ | |
| UI-3.6 | "Peer-reviewed only" checkbox present | ☐ | |
| UI-3.7 | Advanced options collapsible | ☐ | |
| UI-3.8 | "Run Search" button clearly visible | ☐ | |

### 1.4 Search Results UI

| ID | Test | Status | Notes |
|----|------|--------|-------|
| UI-4.1 | Loading spinner displays during search | ☐ | |
| UI-4.2 | Progress indicator shows database being searched | ☐ | |
| UI-4.3 | Results display in cards/list format | ☐ | |
| UI-4.4 | Each result shows: title, authors, year, abstract | ☐ | |
| UI-4.5 | "Show more" button expands full abstract | ☐ | |
| UI-4.6 | Results grouped by database | ☐ | |
| UI-4.7 | Duplicate indicator shows if study appears in multiple databases | ☐ | |
| UI-4.8 | Pagination works (if >50 results) | ☐ | |
| UI-4.9 | Export results button present | ☐ | |

### 1.5 Screening Interface UI

| ID | Test | Status | Notes |
|----|------|--------|-------|
| UI-5.1 | Study displayed one at a time (or in list) | ☐ | |
| UI-5.2 | Include/Exclude/Uncertain buttons clearly labeled | ☐ | |
| UI-5.3 | Keyboard shortcuts work (I=Include, E=Exclude, U=Uncertain) | ☐ | |
| UI-5.4 | Progress bar shows: X of Y studies screened | ☐ | |
| UI-5.5 | Inclusion/exclusion criteria displayed on side | ☐ | |
| UI-5.6 | "Previous" button to review last decision | ☐ | |
| UI-5.7 | "Add note" option for uncertain studies | ☐ | |
| UI-5.8 | Decision counts update in real-time | ☐ | |

### 1.6 Statistical Results UI

| ID | Test | Status | Notes |
|----|------|--------|-------|
| UI-6.1 | Forest plot displays correctly | ☐ | |
| UI-6.2 | Forest plot is interactive (hover shows details) | ☐ | |
| UI-6.3 | Funnel plot displays correctly | ☐ | |
| UI-6.4 | Statistical summary table readable | ☐ | |
| UI-6.5 | Heterogeneity statistics highlighted | ☐ | |
| UI-6.6 | Publication bias section present | ☐ | |
| UI-6.7 | "Download plots" buttons work | ☐ | |
| UI-6.8 | Interpretation text is clear and actionable | ☐ | |

---

## Test Category 2: Research Question 1 - Full Workflow

### RQ1: "What is the effect of exercise on depression?"

**Configuration:**
- Databases: PubMed, Europe PMC
- Date range: 2015-2024
- Peer-reviewed only: Yes
- Expected results: 20+ studies

| ID | Step | Expected Result | Actual Result | Status | Notes |
|----|------|-----------------|---------------|--------|-------|
| RQ1-1 | Create project with RQ1 | Project created with ID | | ☐ | |
| RQ1-2 | Configure search | All fields populated correctly | | ☐ | |
| RQ1-3 | Run search | Completes in < 60 seconds | | ☐ | |
| RQ1-4 | Verify PubMed results | 20+ studies returned | | ☐ | |
| RQ1-5 | Verify Europe PMC results | 10+ studies returned | | ☐ | |
| RQ1-6 | Check deduplication | Duplicates removed, count shown | | ☐ | |
| RQ1-7 | Review study quality | Studies have titles, abstracts, authors | | ☐ | |
| RQ1-8 | Manual spot-check 5 studies | All 5 are about exercise/depression | | ☐ | |
| RQ1-9 | Screen studies | AI provides include/exclude recommendations | | ☐ | |
| RQ1-10 | Verify AI decisions | Agree with 4/5 random AI decisions | | ☐ | |
| RQ1-11 | Override 1 AI decision | Manual override works | | ☐ | |
| RQ1-12 | Complete screening | 10-15 studies included | | ☐ | |
| RQ1-13 | Quality assessment | Risk of bias assessed for all | | ☐ | |
| RQ1-14 | Data extraction | Sample sizes, means, SDs extracted | | ☐ | |
| RQ1-15 | Run meta-analysis | Pooled effect calculated | | ☐ | |
| RQ1-16 | Verify effect size | Large effect favoring exercise (d < -0.5) | | ☐ | |
| RQ1-17 | Check heterogeneity | I² reported, interpretation provided | | ☐ | |
| RQ1-18 | Check publication bias | Egger's test result shown | | ☐ | |
| RQ1-19 | Review forest plot | Plot displays all studies correctly | | ☐ | |
| RQ1-20 | Review funnel plot | Plot shows study distribution | | ☐ | |
| RQ1-21 | Generate report | APA-format report generated | | ☐ | |
| RQ1-22 | Export CSV | CSV downloads with all data | | ☐ | |
| RQ1-23 | Export Excel | Multi-sheet Excel file downloads | | ☐ | |
| RQ1-24 | Export forest plot PNG | High-resolution image downloads | | ☐ | |
| RQ1-25 | Open exported files | All files open correctly | | ☐ | |

**Overall RQ1 Assessment:**
- Total time to complete: _______ minutes
- Major issues found: _______
- Ready for publication: YES / NO

---

## Test Category 3: Research Question 2 - Full Workflow

### RQ2: "Does mindfulness reduce anxiety?"

**Configuration:**
- Databases: PubMed, arXiv, CORE
- Date range: 2015-2024
- Peer-reviewed only: No (include preprints)
- Expected results: 15+ studies

| ID | Step | Expected Result | Actual Result | Status | Notes |
|----|------|-----------------|---------------|--------|-------|
| RQ2-1 | Create project with RQ2 | Project created | | ☐ | |
| RQ2-2 | Run multi-database search | 3 databases searched | | ☐ | |
| RQ2-3 | Verify arXiv preprints included | At least 3 preprints found | | ☐ | |
| RQ2-4 | Check peer-review flag | Studies tagged correctly | | ☐ | |
| RQ2-5 | Complete workflow | All stages work | | ☐ | |
| RQ2-6 | Verify different effect size | Effect size different from RQ1 | | ☐ | |
| RQ2-7 | Generate report | Report reflects preprint inclusion | | ☐ | |

**Overall RQ2 Assessment:**
- Preprints handled correctly: YES / NO
- Different from RQ1 workflow: YES / NO

---

## Test Category 4: Research Question 3 - Full Workflow

### RQ3: "Impact of diet on cardiovascular disease"

**Configuration:**
- Databases: PubMed, Europe PMC, CORE
- Date range: 2015-2024
- Peer-reviewed only: Yes
- Expected results: 30+ studies (larger literature)

| ID | Step | Expected Result | Actual Result | Status | Notes |
|----|------|-----------------|---------------|--------|-------|
| RQ3-1 | Create project with RQ3 | Project created | | ☐ | |
| RQ3-2 | Run search | 30+ studies found | | ☐ | |
| RQ3-3 | Handle large result set | System doesn't crash | | ☐ | |
| RQ3-4 | Screening performance | < 2 seconds per study | | ☐ | |
| RQ3-5 | Binary outcome handling | Risk ratios calculated correctly | | ☐ | |
| RQ3-6 | High heterogeneity warning | System flags high I² | | ☐ | |
| RQ3-7 | Subgroup analysis offered | Option to analyze by diet type | | ☐ | |

---

## Test Category 5: Visual Design & Accessibility

### 5.1 Visual Design

| ID | Test | Status | Notes |
|----|------|--------|-------|
| VD-1 | Color scheme professional | ☐ | |
| VD-2 | Typography readable (min 14px body text) | ☐ | |
| VD-3 | Consistent button styles | ☐ | |
| VD-4 | Icons intuitive and clear | ☐ | |
| VD-5 | White space appropriate | ☐ | |
| VD-6 | No visual glitches or overlaps | ☐ | |
| VD-7 | Loading states smooth | ☐ | |
| VD-8 | Professional for academic audience | ☐ | |

### 5.2 Accessibility

| ID | Test | Status | Notes |
|----|------|--------|-------|
| ACC-1 | Keyboard navigation works (Tab key) | ☐ | |
| ACC-2 | All buttons accessible via keyboard | ☐ | |
| ACC-3 | Color contrast meets WCAG AA (4.5:1) | ☐ | |
| ACC-4 | Alt text on all images | ☐ | |
| ACC-5 | Screen reader compatible | ☐ | |
| ACC-6 | Focus indicators visible | ☐ | |
| ACC-7 | No flashing content | ☐ | |
| ACC-8 | Zoom to 200% still usable | ☐ | |

---

## Test Category 6: Browser Compatibility

Test on multiple browsers:

| Browser | Version | Registration | Search | Workflow | Plots | Overall |
|---------|---------|--------------|--------|----------|-------|---------|
| Chrome | Latest | ☐ | ☐ | ☐ | ☐ | ☐ |
| Firefox | Latest | ☐ | ☐ | ☐ | ☐ | ☐ |
| Safari | Latest | ☐ | ☐ | ☐ | ☐ | ☐ |
| Edge | Latest | ☐ | ☐ | ☐ | ☐ | ☐ |

---

## Test Category 7: Mobile Responsiveness

Test on mobile devices:

| Device | Screen Size | Login | Dashboard | Search | Screening | Overall |
|--------|-------------|-------|-----------|--------|-----------|---------|
| iPhone 13 | 390x844 | ☐ | ☐ | ☐ | ☐ | ☐ |
| Samsung Galaxy | 360x740 | ☐ | ☐ | ☐ | ☐ | ☐ |
| iPad | 768x1024 | ☐ | ☐ | ☐ | ☐ | ☐ |

---

## Test Category 8: Error Handling & Edge Cases

### 8.1 Empty States

| ID | Scenario | Expected Behavior | Actual | Status |
|----|----------|-------------------|--------|--------|
| ES-1 | No projects yet | "Create your first project" message | | ☐ |
| ES-2 | Search returns 0 results | Helpful message with suggestions | | ☐ |
| ES-3 | All studies excluded | "No studies included" warning | | ☐ |
| ES-4 | Missing data for analysis | Clear error, can't proceed | | ☐ |

### 8.2 Session Management

| ID | Scenario | Expected Behavior | Actual | Status |
|----|----------|-------------------|--------|--------|
| SM-1 | Leave page idle 30 minutes | Session still valid | | ☐ |
| SM-2 | Leave page idle 65 minutes | Session expired, prompted to login | | ☐ |
| SM-3 | Work preserved after session timeout | Can resume after re-login | | ☐ |
| SM-4 | Multiple tabs/windows | Work syncs across tabs | | ☐ |

### 8.3 Network Issues

| ID | Scenario | Expected Behavior | Actual | Status |
|----|----------|-------------------|--------|--------|
| NET-1 | Search during slow connection | Shows loading, completes | | ☐ |
| NET-2 | Search timeout | Error message, retry option | | ☐ |
| NET-3 | Export large file | Progress indicator, completes | | ☐ |

---

## Test Category 9: Data Integrity

### 9.1 Data Persistence

| ID | Test | Status | Notes |
|----|------|--------|-------|
| DI-1 | Create project, logout, login → project still there | ☐ | |
| DI-2 | Screen 10 studies, refresh page → decisions preserved | ☐ | |
| DI-3 | Export data, re-import → data matches | ☐ | |
| DI-4 | Change project settings → settings saved | ☐ | |

### 9.2 Data Accuracy

| ID | Test | Status | Notes |
|----|------|--------|-------|
| DA-1 | Manually verify 5 search results → all match PubMed | ☐ | |
| DA-2 | Check effect size calculation against R → matches within 1% | ☐ | |
| DA-3 | Verify study counts in PRISMA → all numbers consistent | ☐ | |
| DA-4 | Check citations in report → all formatted correctly | ☐ | |

---

## Test Category 10: Help & Documentation

| ID | Test | Status | Notes |
|----|------|--------|-------|
| DOC-1 | Help button accessible from every page | ☐ | |
| DOC-2 | Tooltips explain technical terms | ☐ | |
| DOC-3 | FAQ section answers common questions | ☐ | |
| DOC-4 | Video tutorials available | ☐ | |
| DOC-5 | Contact support option present | ☐ | |
| DOC-6 | API documentation accessible | ☐ | |

---

## Test Category 11: Print/Export Quality

| ID | Test | Expected Quality | Actual | Status |
|----|------|------------------|--------|--------|
| EXP-1 | Forest plot PNG | 300 DPI, publication-ready | | ☐ |
| EXP-2 | PDF report | Professional formatting | | ☐ |
| EXP-3 | CSV file | Opens in Excel without errors | | ☐ |
| EXP-4 | Excel file | Multiple sheets, formatting intact | | ☐ |
| EXP-5 | Citations | APA 7th edition format correct | | ☐ |

---

## Test Category 12: Performance (Manual Verification)

| ID | Test | Target | Actual | Status |
|----|------|--------|--------|--------|
| PERF-1 | Login time | < 2 seconds | | ☐ |
| PERF-2 | Dashboard load | < 3 seconds | | ☐ |
| PERF-3 | Search (PubMed only) | < 30 seconds | | ☐ |
| PERF-4 | Search (4 databases) | < 60 seconds | | ☐ |
| PERF-5 | Screening 50 studies | < 5 minutes | | ☐ |
| PERF-6 | Meta-analysis calculation | < 60 seconds | | ☐ |
| PERF-7 | Report generation | < 120 seconds | | ☐ |
| PERF-8 | Export CSV | < 5 seconds | | ☐ |

---

## Final Assessment

### Overall Rating

| Category | Pass Rate | Status |
|----------|-----------|--------|
| User Interface | __/48 | ☐ PASS ☐ FAIL |
| RQ1 Workflow | __/25 | ☐ PASS ☐ FAIL |
| RQ2 Workflow | __/7 | ☐ PASS ☐ FAIL |
| RQ3 Workflow | __/7 | ☐ PASS ☐ FAIL |
| Visual Design | __/16 | ☐ PASS ☐ FAIL |
| Browser Compatibility | __/20 | ☐ PASS ☐ FAIL |
| Mobile Responsiveness | __/15 | ☐ PASS ☐ FAIL |
| Error Handling | __/11 | ☐ PASS ☐ FAIL |
| Data Integrity | __/8 | ☐ PASS ☐ FAIL |
| Help & Documentation | __/6 | ☐ PASS ☐ FAIL |
| Export Quality | __/5 | ☐ PASS ☐ FAIL |
| Performance | __/8 | ☐ PASS ☐ FAIL |

**Total Score:** ____/176

**Pass Threshold:** 150/176 (85%)

### Production Readiness Decision

☐ **GO** - All critical tests passed, ready for production

☐ **GO WITH CAUTIONS** - Minor issues, deployable with monitoring

☐ **NO-GO** - Critical issues must be fixed before deployment

### Critical Issues Found

1. _______________________________________________________
2. _______________________________________________________
3. _______________________________________________________

### Recommendations

_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

### Sign-Off

**Tester Name:** _______________________
**Date:** _______________________
**Signature:** _______________________

**QA Manager:** _______________________
**Date:** _______________________
**Signature:** _______________________

---

**END OF MANUAL TESTING CHECKLIST**
