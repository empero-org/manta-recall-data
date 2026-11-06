"""Rebuild the context and questions of a Manta recall run from the published filings text.

    python scripts/build_prompts.py --run 88m_20 --out prompts_88m_20
    python scripts/build_prompts.py --run 10m_20 --out prompts_10m_20
    python scripts/build_prompts.py --run 10m_50_lookalike --out prompts_10m_50

The context is the start of haystack/sp500_filings.txt.xz (read compressed), up to the run's filings_end_char, with each memo planted at
its char_offset (needles/needles_<run>.json):

    \\n\\nInternal memo: the vault access code for the <office> office is <code>.\\n\\n

Each question is asked as a user turn of its own after the whole context, with thinking off. Writes <out>/context.txt
and <out>/questions.jsonl. Standard library only.
"""

import argparse
import json
import lzma
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build(run: str) -> tuple[str, list[dict]]:
    spec = json.loads((ROOT / "needles" / f"needles_{run}.json").read_text())
    with lzma.open(ROOT / "haystack" / "sp500_filings.txt.xz", "rt", encoding="utf-8") as fh:
        filings = fh.read(spec["filings_end_char"])
    pieces, last = [], 0
    for n in spec["needles"]:
        pieces.append(filings[last : n["char_offset"]])
        pieces.append(f"\n\nInternal memo: the vault access code for the {n['office']} office is {n['code']}.\n\n")
        last = n["char_offset"]
    pieces.append(filings[last:])
    return "".join(pieces), spec["needles"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, choices=["10m_20", "88m_20", "10m_50_lookalike"])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    context, needles = build(args.run)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "context.txt").write_text(context, encoding="utf-8")
    with open(out / "questions.jsonl", "w") as fh:
        for n in needles:
            fh.write(json.dumps(n) + "\n")
    print(json.dumps({"run": args.run, "context_chars": len(context), "needles": len(needles), "out": str(out)}))


if __name__ == "__main__":
    main()
