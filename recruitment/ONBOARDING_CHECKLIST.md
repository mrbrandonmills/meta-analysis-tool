# Onboarding Checklist for Beta Testers

## Overview
Step-by-step checklist to ensure each beta tester successfully onboards and completes their first review. This document is for the Platform Team to track progress and provide support.

---

## Pre-Onboarding (Before They Start)

### Internal Preparation
- [ ] Beta tester selected and confirmed participation
- [ ] Generate unique onboarding link (with promo code: FOUNDING10)
- [ ] Add to Beta Testers spreadsheet (tracking sheet)
- [ ] Add to private Slack/Discord community (invite sent)
- [ ] Prepare personalized welcome email
- [ ] Set calendar reminder: Check progress in 3 days, 7 days, 14 days

---

## Phase 1: Account Creation (Day 0)

### What the User Does:
- [ ] Receives welcome email with unique signup link
- [ ] Clicks link and creates account (email + password)
- [ ] Verifies email address (confirmation link)
- [ ] Logs in for first time

### Platform Team Actions:
- [ ] Send welcome email with signup link
- [ ] Monitor for account creation (should happen within 24-48 hours)
- [ ] If no activity after 48 hours: Send gentle reminder email
- [ ] Tag in system: "Account Created" (timestamp)

### Success Criteria:
- Account created within 48 hours
- Email verified
- First login completed

---

## Phase 2: Onboarding Profile (Day 0-2)

### What the User Does (30+ Data Points):

**Basic Information:**
- [ ] Full name
- [ ] Institution/Affiliation
- [ ] Department
- [ ] Job title (Assistant Professor, Associate Professor, etc.)
- [ ] Email (pre-filled from account)
- [ ] Phone (optional)

**Research Profile:**
- [ ] Google Scholar URL (required)
- [ ] ORCID iD (if available)
- [ ] ResearchGate profile (optional)
- [ ] Personal/Lab website (optional)
- [ ] Primary research specialty (dropdown: Cognitive, Clinical, Social, Developmental, Neuroscience)
- [ ] Secondary research areas (multi-select, up to 3)
- [ ] Research keywords (free text, up to 10)

**Publication History:**
- [ ] Number of publications (self-reported, we'll verify via Google Scholar)
- [ ] Recent paper titles (auto-populated from Google Scholar, user confirms)
- [ ] Primary journals where you publish (multi-select)

**Peer Review Experience:**
- [ ] How many peer reviews completed in past year? (dropdown: 0-5, 6-10, 11-15, 16+)
- [ ] Which journals have you reviewed for? (free text)
- [ ] Average time per review (dropdown: <2 hours, 2-4 hours, 4-6 hours, 6+ hours)
- [ ] What do you find most challenging about peer review? (free text)

**Expertise Areas:**
- [ ] Methodologies you're expert in (multi-select: fMRI, EEG, surveys, behavioral experiments, computational modeling, etc.)
- [ ] Statistical methods (multi-select: ANOVA, regression, SEM, Bayesian, machine learning, etc.)
- [ ] Populations you study (multi-select: adults, children, clinical, animal models, etc.)

**Preferences:**
- [ ] Preferred review frequency (dropdown: 2/month, 3/month, 4/month)
- [ ] Review deadline preference (dropdown: 14 days, 21 days, 30 days)
- [ ] Anonymous vs. signed reviews (preference)
- [ ] Notification preferences (email, SMS, in-app)

**Payment Information:**
- [ ] Stripe Connect onboarding (for receiving payments)
- [ ] Tax information (W-9 for US, W-8BEN for international)
- [ ] Preferred payout method (bank transfer, debit card)

**Agreements:**
- [ ] Terms of Service (checkbox)
- [ ] Privacy Policy (checkbox)
- [ ] Reviewer Code of Conduct (checkbox)
- [ ] Consent to use anonymized data for research (optional checkbox)

### Platform Team Actions:
- [ ] Monitor onboarding progress (dashboard showing % complete)
- [ ] If stuck at <50% for 48 hours: Send "Need help?" email
- [ ] If stuck at 50-80% for 72 hours: Send "Almost there!" email
- [ ] When 100% complete: Trigger AI enrichment process
- [ ] Tag in system: "Onboarding Complete" (timestamp)

### Success Criteria:
- Profile ≥80% complete within 7 days
- Google Scholar URL provided (required for AI enrichment)
- Payment information submitted (required for payouts)
- All required checkboxes checked

---

## Phase 3: AI Enrichment (Day 2-3)

### Automated Process:

**Google Scholar Enrichment:**
- [ ] Fetch all publications from Google Scholar
- [ ] Extract titles, years, journals, citation counts
- [ ] Calculate H-index, i10-index
- [ ] Identify co-authors (for conflict detection)
- [ ] Extract research keywords from paper titles/abstracts
- [ ] Categorize papers by topic (ML clustering)

**ORCID Enrichment (if provided):**
- [ ] Fetch verified publication list
- [ ] Cross-reference with Google Scholar
- [ ] Extract additional metadata (DOIs, abstracts)

**Expertise Mapping:**
- [ ] Generate expertise vector (topics, methods, populations)
- [ ] Identify specialty strength scores
- [ ] Flag for review matching algorithm

**Conflict Detection:**
- [ ] Build co-author network
- [ ] Identify institutional affiliations
- [ ] Create exclusion list for matching

### Platform Team Actions:
- [ ] Monitor AI enrichment job (should complete in 1-24 hours)
- [ ] Review for errors (failed Scholar scrape, low data quality)
- [ ] If enrichment fails: Manual intervention (contact user for help)
- [ ] If enrichment succeeds: Send "Profile Ready!" email
- [ ] Tag in system: "AI Enrichment Complete" (timestamp)

### Success Criteria:
- At least 10 publications extracted
- H-index calculated successfully
- Expertise vector generated
- Conflict exclusions created

---

## Phase 4: Subscription Payment (Day 0-3)

### What the User Does:
- [ ] Enter payment method (credit card via Stripe)
- [ ] Review subscription details ($100/month, first month $50 with promo code)
- [ ] Confirm subscription
- [ ] Receive payment confirmation email

### Platform Team Actions:
- [ ] Monitor for successful payment (Stripe webhook)
- [ ] If payment fails: Send "Payment issue" email with retry link
- [ ] If payment succeeds: Activate account for matching
- [ ] Tag in system: "Subscription Active" (timestamp)
- [ ] Add to "Active Users" list

### Success Criteria:
- Payment successful within 3 days
- Subscription status = "Active"
- Promo code applied correctly (50% off first month)

---

## Phase 5: First Paper Match (Day 3-5)

### Automated Process:
- [ ] User enters matching pool (after onboarding + payment complete)
- [ ] Algorithm scans paper queue for matches
- [ ] Checks conflict exclusions
- [ ] Generates match score
- [ ] Assigns paper to reviewer (if score >threshold)
- [ ] Sends "New Paper Assignment" notification

### What the User Does:
- [ ] Receives email: "You have a new paper to review"
- [ ] Logs in to platform
- [ ] Views paper details (title, abstract, authors)
- [ ] Accepts or declines assignment
- [ ] If accepts: Downloads paper and begins review

### Platform Team Actions:
- [ ] Monitor for first assignment (should happen within 48 hours of completing onboarding)
- [ ] If no assignment after 48 hours: Check if papers available in their specialty
- [ ] If papers available but no match: Review matching algorithm (may need manual assignment)
- [ ] If no papers available: Send "We're building paper queue" email + set expectation
- [ ] Tag in system: "First Paper Assigned" (timestamp)

### Success Criteria:
- First paper assigned within 5 days of onboarding completion
- User accepts assignment (doesn't decline)
- User begins review (opens paper viewer)

---

## Phase 6: First Review Completion (Day 5-20)

### What the User Does:
- [ ] Reads paper thoroughly
- [ ] Uses platform review tools (annotations, comments, ratings)
- [ ] Completes review sections:
  - [ ] Overall recommendation (accept, minor revisions, major revisions, reject)
  - [ ] Strengths of paper
  - [ ] Weaknesses of paper
  - [ ] Specific feedback by section (intro, methods, results, discussion)
  - [ ] Confidential comments to editor (if applicable)
- [ ] Submits review by deadline

### Platform Team Actions:
- [ ] Monitor review progress (% complete)
- [ ] Send reminder 3 days before deadline
- [ ] Send reminder 1 day before deadline
- [ ] If deadline passes without submission: Reach out personally (not automated)
- [ ] When submitted: Send "Thank you!" email + handwritten note in mail
- [ ] Tag in system: "First Review Complete" (timestamp)
- [ ] Celebrate publicly (Slack shout-out, if they consent)

### Success Criteria:
- Review submitted by deadline (14-21 days)
- Review meets quality standards (>500 words, constructive, detailed)
- Author rates review ≥3/5 stars

---

## Phase 7: First Payment (End of Month 1)

### Automated Process:
- [ ] System calculates reviews completed in month
- [ ] Applies payment formula (2 reviews = $20, 3 = $30, 4 = $40)
- [ ] Processes payout via Stripe (first week of following month)
- [ ] Sends payment confirmation email

### What the User Does:
- [ ] Receives email: "Your payment of $[amount] has been sent"
- [ ] Checks bank account (arrives in 1-3 days)
- [ ] Confirms receipt (optional feedback form)

### Platform Team Actions:
- [ ] Monitor payout batch (should process automatically)
- [ ] Check for failed payments (bank account issues)
- [ ] If payout fails: Contact user to update payment info
- [ ] Send "How's it going?" feedback email
- [ ] Tag in system: "First Payment Sent" (timestamp)

### Success Criteria:
- Payment processed successfully
- User confirms receipt
- No payout issues or delays

---

## Post-Onboarding: Ongoing Engagement (Month 2+)

### Monthly Actions:
- [ ] Month 2: Send "How's it going?" check-in email
- [ ] Month 3: Request feedback (survey or call)
- [ ] Month 6: Eligibility for co-authorship opportunity
- [ ] Ongoing: Monitor review completion rate
- [ ] Ongoing: Respond to support requests within 24 hours

### Success Indicators:
- [ ] Completes 2+ reviews per month consistently
- [ ] Responds to emails/messages promptly
- [ ] Provides product feedback (features, bugs)
- [ ] Refers colleagues (referral bonus)
- [ ] Renews subscription after month 1

---

## Onboarding Dashboard (For Platform Team)

### Tracking Spreadsheet Columns:

| Name | Email | Date Invited | Account Created | Onboarding % | AI Enriched | Payment Status | First Paper | First Review | First Payout | Status | Notes |
|------|-------|--------------|-----------------|--------------|-------------|----------------|-------------|--------------|--------------|--------|-------|
| Dr. X | x@uni.edu | 11-12 | 11-13 | 100% | Yes | Active | 11-15 | 11-22 | 12-05 | Active | Great feedback! |
| Dr. Y | y@uni.edu | 11-12 | 11-13 | 65% | No | Pending | - | - | - | Stuck | Reached out 11-16 |

**Color Coding:**
- Green: On track
- Yellow: Minor delay or issue
- Red: Stuck, needs immediate attention

---

## Common Onboarding Issues & Solutions

### Issue 1: User Stuck at Profile Completion

**Symptoms:**
- Onboarding 50-80% complete
- No progress for 3+ days

**Diagnosis:**
- Too many fields (overwhelmed)
- Technical issue (form not saving)
- Unclear instructions

**Solution:**
- Send email: "Need help finishing your profile? I'm here to help."
- Offer to jump on 10-min call to walk through
- Consider reducing required fields (make some optional)

---

### Issue 2: Google Scholar Scraping Fails

**Symptoms:**
- AI enrichment job fails
- No publications extracted

**Diagnosis:**
- Incorrect Google Scholar URL
- Private/restricted profile
- Name mismatch (published under different name)

**Solution:**
- Email user: "We had trouble finding your publications. Can you verify your Google Scholar URL?"
- Manual data entry (as backup)
- Ask for ORCID instead (easier to scrape)

---

### Issue 3: Payment Fails

**Symptoms:**
- Stripe payment declined
- User can't complete subscription

**Diagnosis:**
- Card declined (insufficient funds, fraud alert)
- International card (not supported)
- Billing address mismatch

**Solution:**
- Email user: "Payment didn't go through. Try a different card?"
- Offer alternative payment (PayPal, bank transfer)
- As last resort: Waive first month payment (risk it for beta)

---

### Issue 4: No Papers to Assign

**Symptoms:**
- User completes onboarding
- 48+ hours pass, no paper assigned

**Diagnosis:**
- No papers in their specialty yet (small beta pool)
- Matching algorithm too strict (no matches found)
- All available papers have conflicts

**Solution:**
- Honest communication: "We're building the paper queue in your specialty. You'll be first to review when papers arrive."
- Manually assign a borderline match (with explanation: "This is slightly outside your core area, but would you be willing to review?")
- Adjust matching algorithm threshold (lower barrier)

---

### Issue 5: User Doesn't Complete First Review

**Symptoms:**
- Paper assigned
- Deadline approaching or passed
- No progress on review

**Diagnosis:**
- Too busy (life happens)
- Forgot about deadline
- Found paper too difficult
- Technical issues with review tool

**Solution:**
- Gentle reminder 3 days before deadline
- Personal email (not automated) if deadline passes: "Hey [Name], checking in on the review. Everything OK?"
- Offer deadline extension (if reasonable)
- Offer to reassign (no penalty)
- If persistent issue: May need to remove from beta

---

## Communication Templates

### Email 1: Welcome & Signup Link (Day 0)

**Subject:** Welcome to [Platform Name] - Your Signup Link Inside

Hi [First Name],

Excited to have you as a Founding Reviewer! Here's your personalized signup link:

[UNIQUE LINK]

**What to expect:**
1. Create account (2 min)
2. Complete onboarding profile (10-15 min)
3. We enrich your data overnight (automatic)
4. You're matched to first paper within 48 hours

**Your benefits:**
- 50% off first month (promo code FOUNDING10 auto-applied)
- Lifetime 20% discount after month 1
- Founding Reviewer badge
- [Other benefits]

**Need help?** Reply to this email or schedule a call: [Calendly]

Let's build the future of peer review together.

Best,
[Your Name]

---

### Email 2: Reminder (48 Hours After Signup Link, No Activity)

**Subject:** Don't miss your Founding Reviewer spot

Hi [First Name],

Just checking in - I sent your [Platform Name] signup link 2 days ago and haven't seen activity yet.

**Your link:** [UNIQUE LINK]

This link expires in 5 days, so don't miss out on:
- 50% off first month
- Lifetime 20% discount
- Founding Reviewer status

**Takes 15 minutes total.** If you're running into issues or have questions, just reply to this email.

Still interested?

Best,
[Your Name]

---

### Email 3: Stuck at Onboarding (Profile <80%, 72 Hours)

**Subject:** Need help finishing your profile?

Hi [First Name],

I see you started your [Platform Name] profile but haven't finished yet. No worries - happy to help!

**Where you're at:** [X]% complete
**What's left:** [List remaining sections]

**Common questions:**
- "Do I really need to fill out all these fields?" - Most are required for AI matching, but if something's unclear, I can help prioritize.
- "My Google Scholar link isn't working" - Make sure it's the full URL (starts with https://scholar.google.com/citations?user=...)
- "I don't have ORCID" - That's OK, it's optional.

**Want to hop on a quick call?** I can walk you through in 10 minutes: [Calendly]

Or just reply with questions.

Best,
[Your Name]

---

### Email 4: Onboarding Complete, AI Enrichment Done (Day 3)

**Subject:** Your profile is ready! First paper coming soon.

Hi [First Name],

Great news - your [Platform Name] profile is complete and enriched!

**What we found:**
- [X] publications from Google Scholar
- H-index: [X]
- Primary expertise: [areas]
- Ready for matching ✓

**What's next:**
You'll receive your first paper assignment within 48 hours. We'll match you to a paper in [their specialty] that aligns with your research.

**In the meantime:**
- Join our Slack community: [invite link]
- Check out the platform tour: [link]
- Set up your notification preferences: [link]

Excited to see your first review!

Best,
[Your Name]

---

### Email 5: First Paper Assigned (Day 3-5)

**Subject:** Your first paper is ready to review

Hi [First Name],

You've been matched to your first paper on [Platform Name]!

**Paper:** [Title]
**Topic:** [Brief description]
**Deadline:** [Date, 14-21 days from now]
**Compensation:** $[amount based on monthly total]

**Review it here:** [Link to paper]

**Need more time?** Just reply and I can extend the deadline.

**Questions about the review process?** Check the guide: [link] or reply to this email.

Looking forward to your insights!

Best,
[Your Name]

---

### Email 6: Review Deadline Reminder (3 Days Before)

**Subject:** Friendly reminder: Review due in 3 days

Hi [First Name],

Quick reminder - your review of "[Paper Title]" is due in 3 days ([Date]).

**Current status:** [X]% complete

**Need an extension?** No problem, just let me know.

**Need help with the review tool?** I'm here: [Email, Slack, Calendly]

Thanks for your work on this!

Best,
[Your Name]

---

### Email 7: First Review Complete - Thank You (Day After Submission)

**Subject:** Thank you for your first review!

Hi [First Name],

Just saw you submitted your first review - awesome work!

The author will receive it shortly, and you'll be matched to your next paper within a few days.

**Your review summary:**
- Submitted on time ✓
- Detailed feedback ✓
- Compensation: $[amount] (paid first week of next month)

**As a thank you,** I'm sending a handwritten note your way. Should arrive in 3-5 days. 📬

**Feedback?** How was the experience? Anything we should improve? Just reply.

Thanks for being a Founding Reviewer!

Best,
[Your Name]

P.S. - Here's your referral link: [unique link]. Share with colleagues. You get $50 for each one who joins!

---

### Email 8: First Payment Sent (Month 2, Week 1)

**Subject:** Payment sent: $[amount] for [X] reviews

Hi [First Name],

Your first [Platform Name] payment is on the way!

**Amount:** $[amount]
**Reviews completed:** [X]
**Payment method:** [Bank transfer / Debit card]
**Arrival:** 1-3 business days

You can view your payment history here: [link]

**Next month:**
You currently have [X] papers assigned. Complete them by end of month for $[projected amount].

Keep up the great work!

Best,
[Your Name]

---

## Success Metrics

### Onboarding Funnel:

**Invited → Account Created**
- Target: 90% within 48 hours
- Actual: ___%

**Account Created → Onboarding Started**
- Target: 100%
- Actual: ___%

**Onboarding Started → Onboarding Completed**
- Target: 80% within 7 days
- Actual: ___%

**Onboarding Completed → First Payment**
- Target: 100%
- Actual: ___%

**First Payment → First Paper Assigned**
- Target: 100% within 48 hours
- Actual: ___%

**First Paper Assigned → First Review Completed**
- Target: 80% within deadline
- Actual: ___%

**First Review Completed → Active User (Month 2)**
- Target: 70%
- Actual: ___%

### Time Metrics:

- **Median time to account creation:** Target <24 hours
- **Median time to complete onboarding:** Target <48 hours
- **Median time to first paper assignment:** Target <48 hours from onboarding
- **Median time to first review completion:** Target <14 days from assignment
- **Median time to first payment:** Target 5 days into Month 2

---

## Onboarding Team Roles

### Founder/CEO:
- Sends all personalized emails
- Personal check-ins with stuck users
- Handwritten thank-you notes
- Escalation point for issues

### CTO/Developer:
- Monitors technical onboarding (AI enrichment, payment processing)
- Fixes bugs reported during onboarding
- Adjusts matching algorithm if needed

### Customer Success (if applicable):
- Tracks onboarding dashboard daily
- Sends reminder emails (can be automated, but review first)
- Coordinates support responses
- Aggregates feedback

---

## Summary: Onboarding Success

**Goal:** Get 8/10 beta testers to complete first review within 30 days.

**Keys to success:**
1. **Clear communication** - Set expectations at every step
2. **Proactive support** - Reach out before they get stuck
3. **Remove friction** - Make onboarding as easy as possible
4. **Celebrate milestones** - Acknowledge progress (first login, first review, etc.)
5. **Human touch** - Personal emails, handwritten notes, video calls when needed

**Remember:** These are your founding users. Treat them like gold. Over-invest in onboarding now to learn what works for future cohorts.
