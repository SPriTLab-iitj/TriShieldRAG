cat > ~/sync_latest.sh << 'SYNCEOF'
#!/usr/bin/env bash
# sync_latest.sh — copy latest files from a FLAT ~/Downloads into the repo.
# Run from your project root.
set -e
D=~/Downloads

echo "==> engine"
cp $D/llm_backends.py        ragshield_core/llm_backends.py
cp $D/ring3_consensus.py     ragshield_core/ring3_consensus.py
cp $D/raglog.py              ragshield_core/raglog.py
cp $D/config.py              ragshield_core/config.py
cp $D/rag_shield.py          ragshield_core/rag_shield.py
cp $D/retriever.py           ragshield_core/retriever.py
cp $D/target_questions.json  evaluation/target_questions.json

echo "==> UI"
cp $D/_shared.py             frontend/components/_shared.py
cp $D/1_Attack_Demo.py       frontend/pages/1_Attack_Demo.py
cp $D/2_Defense_Demo.py      frontend/pages/2_Defense_Demo.py
cp $D/3_Side_by_Side.py      frontend/pages/3_Side_by_Side.py
cp $D/5_Results_Dashboard.py frontend/pages/5_Results_Dashboard.py

echo "==> docs"
cp $D/README.md              ./README.md
cp $D/QUICKSTART.md          ./QUICKSTART.md
cp $D/PROJECT_GUIDE.md       ./PROJECT_GUIDE.md

echo "==> verifying fixes are present in the repo now"
ok=0
chk(){ grep -q "$2" "$1" && echo "  [OK] $3" || { echo "  [MISS] $3 ($1)"; ok=1; }; }
chk ragshield_core/retriever.py        '"id": "c12"'              "curated docs"
chk evaluation/target_questions.json   '"n_poison": 5'            "5-poison"
chk ragshield_core/rag_shield.py       'all poison; re-retrieved' "ring1 re-retrieve fix"
chk ragshield_core/rag_shield.py       'from .raglog import log'  "logging in rag_shield"
chk ragshield_core/ring3_consensus.py  '_is_no_answer'            "ring3 tie fix"
chk frontend/components/_shared.py     'def cached_answer'        "cached_answer"
chk ragshield_core/llm_backends.py     'temperature: float = 0.0' "temp=0"
chk ragshield_core/config.py           'def retriever_backend'    "retriever_backend"
chk README.md                          'run_live'                 "docs lite-live"
[ $ok -eq 0 ] && echo "==> ALL FIXES PRESENT — ready to commit" || echo "==> SOMETHING MISSING — fix [MISS] lines first"
SYNCEOF
