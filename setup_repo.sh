#!/usr/bin/env bash
# =====================================================================
# setup_repo.sh — bootstrap the PoisonedRAG + RAG-Shield GitHub repo
# Run from your project root:
#   ~/Desktop/MTech AI IIT-Jodhpur*/Cohort-2-Trimester-2/Cyber-Security_ES/Major-Project-PoisonedRAG
#
# Usage:
#   chmod +x setup_repo.sh
#   ./setup_repo.sh
# =====================================================================
set -euo pipefail

REPO_NAME="poisonedrag-ragshield-group6-iitj"
GH_USER="rpaut03l"
VISIBILITY="public"            # public | private
DESC="PoisonedRAG reproduction + RAG-Shield 3-ring defense | Group 6 | CSL6010 Cyber Security | IIT Jodhpur"

echo "==> 1/7  Creating folder structure"
mkdir -p docs slides paper knowledge_base baseline defense llm_backends evaluation frontend infra report results

echo "==> 2/7  Adding folder placeholders (so empty dirs are tracked)"
for d in paper knowledge_base baseline defense llm_backends evaluation frontend infra report results; do
  [ -z "$(ls -A "$d" 2>/dev/null)" ] && echo "# $d — work-in-progress" > "$d/.gitkeep"
done

echo "==> 3/7  Sanity check: required docs present?"
for f in README.md LICENSE .gitignore docs/README.md docs/PAPER_SUMMARY.md docs/GAP_AND_FIX.md docs/VIVA_QA.md; do
  if [ ! -f "$f" ]; then echo "   MISSING: $f  (copy it in before pushing)"; fi
done
[ -f slides/PoisonedRAG_Group6_Presentation.pptx ] || echo "   NOTE: drop the .pptx into slides/ when ready"

echo "==> 4/7  git init + first commit"
git init -q 2>/dev/null || true
git add .
git commit -q -m "docs: project overview, paper summary, gap analysis, viva prep, slides" || echo "   (nothing to commit)"
git branch -M main

echo "==> 5/7  Create the GitHub repo (via gh CLI)"
if command -v gh >/dev/null 2>&1; then
  gh repo create "$GH_USER/$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin \
    --description "$DESC" --push 2>/dev/null && echo "   repo created + pushed" || {
      echo "   repo may already exist — wiring remote + pushing"
      git remote add origin "https://github.com/$GH_USER/$REPO_NAME.git" 2>/dev/null || true
      git push -u origin main
    }
else
  echo "   gh not found. Manual path:"
  echo "     1) create empty repo at github.com/new  named: $REPO_NAME"
  echo "     2) git remote add origin https://github.com/$GH_USER/$REPO_NAME.git"
  echo "     3) git push -u origin main"
fi

echo "==> 6/7  Polish the GitHub repo page (topics + homepage)"
if command -v gh >/dev/null 2>&1; then
  gh repo edit "$GH_USER/$REPO_NAME" \
    --add-topic rag --add-topic llm-security --add-topic prompt-injection \
    --add-topic knowledge-poisoning --add-topic faiss --add-topic iit-jodhpur \
    --add-topic cybersecurity --add-topic defense-in-depth 2>/dev/null || true
fi

echo "==> 7/7  Done."
echo "    Repo: https://github.com/$GH_USER/$REPO_NAME"
echo "    Verify the README + docs links render, then share with the team."
