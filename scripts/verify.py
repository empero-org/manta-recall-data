"""Recount every claimed number from the rows in results/ and raw/.  python scripts/verify.py"""
import json
from pathlib import Path

R = Path(__file__).resolve().parent.parent
rows = lambda p: [json.loads(line) for line in open(R / p)]
needles = lambda p: [r for r in rows(p) if r.get("kind") == "needle"]
a, b, c = rows("results/10m_20.jsonl"), rows("results/88m_20.jsonl"), rows("results/10m_50_lookalike.jsonl")
print("10M, 20 codes:  ", sum(r["correct"] for r in a), "/ 20   pass@3:", sum(r["pass_at_3"] for r in a), "/ 20")
print("88M, 20 codes:  ", sum(r["correct"] for r in b), "/ 20")
print("10M, 50 codes:  ", sum(r["correct"] for r in c), "/ 50")
# The same counts from the rows as they were written by the runs

assert sum(r["correct"] for r in needles("raw/88m_20_transcript.jsonl")) == sum(r["correct"] for r in b)

print("88M transcript agrees")
