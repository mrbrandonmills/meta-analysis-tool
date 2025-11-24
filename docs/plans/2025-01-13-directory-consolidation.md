# Directory Consolidation Implementation Plan

> **For Claude:** This is a repository cleanup task, not a code implementation. Execute steps manually without subagents.

**Goal:** Consolidate three meta-analysis-tool directories into one canonical source, removing duplicate outdated clones.

**Architecture:** Preserve the active working directory (`/Volumes/Super Mastery/meta-analysis-tool`) as source of truth, commit any uncommitted work, then safely remove outdated duplicate directories.

**Tech Stack:** Git, Bash

---

## Current State Analysis

**Directory 1: `/Volumes/Super Mastery/meta-analysis-tool`** (KEEP - SOURCE OF TRUTH)
- 264 files
- Latest commit: `ef19f37` "fix: Require authentication for dashboard access"
- Last modified: Nov 12, 18:20
- Contains ESPN demo at `frontend/src/components/demo/HighlightDemo.tsx`
- Has uncommitted changes:
  - Modified: `.gitignore`
  - Untracked: `AGENTS.md`, `backend/alembic/versions/004_add_pdf_full_text_models.py`, frontend test files
- Connected to: `https://github.com/mrbrandonmills/meta-analysis-tool.git`
- Branch: `main` (up to date with origin/main)

**Directory 2: `/Volumes/Super Mastery/meta-analysis-tool-gh`** (DELETE - OUTDATED)
- 203 files
- Latest commit: `03fcf32` "Fix 11 frontend test failures"
- Last modified: Nov 8, 14:42
- 5 days behind Directory 1

**Directory 3: `/Volumes/Super Mastery/meta-analysis-tool-gh-2`** (DELETE - DUPLICATE)
- 203 files
- Identical to Directory 2
- Last modified: Nov 8, 14:45

---

## Task 1: Commit Uncommitted Work in Main Directory

**Files:**
- Working directory: `/Volumes/Super Mastery/meta-analysis-tool`

**Step 1: Review uncommitted changes**

```bash
cd "/Volumes/Super Mastery/meta-analysis-tool"
git status
git diff .gitignore
```

Expected output: Show what changed in .gitignore and list untracked files

**Step 2: Stage and commit the .gitignore changes**

```bash
git add .gitignore
git commit -m "chore: Update .gitignore for better file exclusions"
```

Expected: Commit created successfully

**Step 3: Stage and commit AGENTS.md**

```bash
git add AGENTS.md
git commit -m "docs: Add AGENTS.md documentation"
```

Expected: Commit created successfully

**Step 4: Stage and commit backend migration**

```bash
git add backend/alembic/versions/004_add_pdf_full_text_models.py
git commit -m "feat: Add PDF full text models migration"
```

Expected: Commit created successfully

**Step 5: Stage and commit frontend tests**

```bash
git add frontend/tests/
git commit -m "test: Add hook and API client integration tests"
```

Expected: Commit created successfully

**Step 6: Push all commits to GitHub**

```bash
git push origin main
```

Expected: All commits pushed to remote

**Step 7: Verify clean working directory**

```bash
git status
```

Expected output: "working tree clean"

---

## Task 2: Backup Check Before Deletion

**Files:**
- All three directories

**Step 1: Verify GitHub is up to date**

```bash
cd "/Volumes/Super Mastery/meta-analysis-tool"
git fetch origin
git status
```

Expected: "Your branch is up to date with 'origin/main'"

**Step 2: Verify ESPN demo exists in main directory**

```bash
ls -lh "/Volumes/Super Mastery/meta-analysis-tool/frontend/src/components/demo/HighlightDemo.tsx"
```

Expected: File exists, ~33KB size

**Step 3: Check for any unique content in outdated directories**

```bash
cd "/Volumes/Super Mastery/meta-analysis-tool-gh"
git log --oneline -5

cd "/Volumes/Super Mastery/meta-analysis-tool-gh-2"
git log --oneline -5
```

Expected: Both show commit `03fcf32` as latest (older than main directory)

**Step 4: Confirm no uncommitted work in outdated directories**

```bash
cd "/Volumes/Super Mastery/meta-analysis-tool-gh"
git status

cd "/Volumes/Super Mastery/meta-analysis-tool-gh-2"
git status
```

Expected: Both show "working tree clean" (no uncommitted changes)

---

## Task 3: Remove Outdated Duplicate Directories

**Files:**
- Delete: `/Volumes/Super Mastery/meta-analysis-tool-gh`
- Delete: `/Volumes/Super Mastery/meta-analysis-tool-gh-2`

**Step 1: Delete first outdated directory**

```bash
rm -rf "/Volumes/Super Mastery/meta-analysis-tool-gh"
```

Expected: Directory removed silently

**Step 2: Verify first directory is gone**

```bash
ls -la "/Volumes/Super Mastery" | grep "meta-analysis-tool-gh"
```

Expected: No output (directory doesn't exist)

**Step 3: Delete second outdated directory**

```bash
rm -rf "/Volumes/Super Mastery/meta-analysis-tool-gh-2"
```

Expected: Directory removed silently

**Step 4: Verify second directory is gone**

```bash
ls -la "/Volumes/Super Mastery" | grep "meta-analysis-tool-gh-2"
```

Expected: No output (directory doesn't exist)

**Step 5: Confirm only one meta-analysis-tool directory remains**

```bash
ls -la "/Volumes/Super Mastery" | grep "meta-analysis-tool"
```

Expected output: Only one entry - `meta-analysis-tool` (not -gh or -gh-2)

---

## Task 4: Update Working Directory Reference

**Files:**
- Environment: Current working directory

**Step 1: Navigate to canonical directory**

```bash
cd "/Volumes/Super Mastery/meta-analysis-tool"
pwd
```

Expected output: `/Volumes/Super Mastery/meta-analysis-tool`

**Step 2: Verify git remote is correct**

```bash
git remote -v
```

Expected output:
```
origin  https://github.com/mrbrandonmills/meta-analysis-tool.git (fetch)
origin  https://github.com/mrbrandonmills/meta-analysis-tool.git (push)
```

**Step 3: Verify we're on main branch**

```bash
git branch --show-current
```

Expected output: `main`

**Step 4: Pull latest to ensure sync**

```bash
git pull origin main
```

Expected: "Already up to date" or latest commits pulled

**Step 5: List directory contents to confirm structure**

```bash
ls -la
```

Expected: Shows `backend/`, `frontend/`, `docs/`, `AGENTS.md`, `.git/`, etc.

---

## Task 5: Verification and Documentation

**Files:**
- Create: `/Volumes/Super Mastery/meta-analysis-tool/docs/CONSOLIDATION_COMPLETE.md`

**Step 1: Create consolidation completion document**

```bash
cat > "/Volumes/Super Mastery/meta-analysis-tool/docs/CONSOLIDATION_COMPLETE.md" << 'EOF'
# Directory Consolidation Complete

**Date:** 2025-01-13
**Status:** ✅ Complete

## Summary

Successfully consolidated three `meta-analysis-tool` directories into one canonical source.

## Actions Taken

1. **Preserved Source of Truth**
   - Directory: `/Volumes/Super Mastery/meta-analysis-tool`
   - Latest commit: `ef19f37`
   - All uncommitted work committed and pushed to GitHub

2. **Removed Duplicates**
   - Deleted: `/Volumes/Super Mastery/meta-analysis-tool-gh` (outdated, Nov 8)
   - Deleted: `/Volumes/Super Mastery/meta-analysis-tool-gh-2` (duplicate, Nov 8)

3. **Verified Integrity**
   - ✅ ESPN demo exists at `frontend/src/components/demo/HighlightDemo.tsx`
   - ✅ All commits synced with GitHub
   - ✅ Working tree clean
   - ✅ No data loss

## Current State

**Single Active Directory:** `/Volumes/Super Mastery/meta-analysis-tool`
- Git remote: `https://github.com/mrbrandonmills/meta-analysis-tool.git`
- Branch: `main`
- Status: Up to date with origin/main
- Files: 264 total (frontend, backend, docs, tests)

## What Was Removed

Both removed directories were outdated clones from Nov 8 with commit `03fcf32`, 5 days behind the main directory. They contained no unique work and were safe to delete.

EOF
```

Expected: File created

**Step 2: Commit the consolidation documentation**

```bash
git add docs/CONSOLIDATION_COMPLETE.md
git commit -m "docs: Document directory consolidation completion"
```

Expected: Commit created

**Step 3: Push documentation to GitHub**

```bash
git push origin main
```

Expected: Commit pushed successfully

**Step 4: Final verification check**

```bash
echo "=== VERIFICATION COMPLETE ==="
echo "Active directory: $(pwd)"
echo "Git status: $(git status --short | wc -l) uncommitted files"
echo "Latest commit: $(git log --oneline -1)"
echo "ESPN demo: $(ls frontend/src/components/demo/HighlightDemo.tsx 2>/dev/null && echo 'EXISTS' || echo 'MISSING')"
echo ""
echo "Removed directories:"
echo "  - meta-analysis-tool-gh: $(ls -d /Volumes/Super\ Mastery/meta-analysis-tool-gh 2>/dev/null && echo 'STILL EXISTS' || echo 'DELETED')"
echo "  - meta-analysis-tool-gh-2: $(ls -d /Volumes/Super\ Mastery/meta-analysis-tool-gh-2 2>/dev/null && echo 'STILL EXISTS' || echo 'DELETED')"
```

Expected output:
```
=== VERIFICATION COMPLETE ===
Active directory: /Volumes/Super Mastery/meta-analysis-tool
Git status: 0 uncommitted files
Latest commit: [commit hash] docs: Document directory consolidation completion
ESPN demo: EXISTS

Removed directories:
  - meta-analysis-tool-gh: DELETED
  - meta-analysis-tool-gh-2: DELETED
```

---

## Rollback Plan (If Needed)

**If something goes wrong**, you can recover the deleted directories:

```bash
# Re-clone from GitHub
cd "/Volumes/Super Mastery"
gh repo clone mrbrandonmills/meta-analysis-tool meta-analysis-tool-gh
gh repo clone mrbrandonmills/meta-analysis-tool meta-analysis-tool-gh-2

# Check out the old commit
cd meta-analysis-tool-gh
git checkout 03fcf32

cd ../meta-analysis-tool-gh-2
git checkout 03fcf32
```

However, **this should NOT be necessary** since:
1. All work is committed to GitHub
2. The removed directories contained no unique changes
3. They were 5 days outdated

---

## Success Criteria

✅ Only one `meta-analysis-tool` directory exists at `/Volumes/Super Mastery/`
✅ No uncommitted work in main directory
✅ All commits pushed to GitHub origin/main
✅ ESPN demo file exists and is accessible
✅ Git working tree is clean
✅ No data loss from removed directories

---

## Next Steps After Consolidation

1. **Continue ESPN Demo UX Refinements**
   - Add viewport detection using Framer Motion `useInView`
   - Implement reduced-motion support
   - Test autoPlay triggers when component is visible

2. **Set Working Directory**
   - Update your shell/IDE to use: `/Volumes/Super Mastery/meta-analysis-tool`
   - Remove any bookmarks to `-gh` or `-gh-2` directories

3. **Regular Maintenance**
   - Pull from GitHub regularly: `git pull origin main`
   - Commit frequently with descriptive messages
   - Push to remote after completing features
