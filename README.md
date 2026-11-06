---
pretty_name: Manta long-context recall (10M and 88M tokens)
license: cc-by-4.0
language: [en]
tags: [long-context, needle-in-a-haystack, retrieval, evaluation, sec-filings]
size_categories: [n<1K]
---

# Manta long-context recall

This is the data behind the recall numbers in the Manta launch (2026-11-06). It has every question and answer, plus the full filings text, so anyone can rebuild the exact contexts.

| Context | Codes hidden | Recalled |
|---|---|---|
| **88M tokens** (88,000,000) | 20 | **18 / 20 (90%)** |
| **10M tokens** (10,485,760) | 20 | **17 / 20 (85%)**, pass@3: 18 / 20 |
| **10M tokens** (10,485,760) | 50 look-alike codes | **43 / 50 (86%)** |

The 10M and 88M runs with 20 codes use the same 20 codes. Each answer is one greedy answer, unless it says pass@3. The three samples per question for pass@3 use temperature 0.7, top_p 0.8, top_k 20.

## The test

- **The haystack:** S&P 500 SEC filings (10-K and 10-Q), as plain text, cut to the context length.
- **The memos:** short memos are planted in it at depths spread evenly from 5% to 95%. Each reads:

  ```
  Internal memo: the vault access code for the <office> office is <code>.
  ```

- **The questions:** each question is its own user turn after the whole context, with thinking off:

  ```
  Above is a long collection of filings. What is the vault access code for the <office> office? Answer with the code only.
  ```

- **Scoring:** an answer is right if it contains the exact code.

The codes come in four shapes, in turn:
- common words, e.g. `DELTA-5033-CANYON`
- rare animal and colour words, e.g. `OKAPI-0227-MAUVE`
- random consonants, e.g. `DZNR-9326-WTM`
- digits only, e.g. `112-81-5948`

Every memo has its own office and its own code, and no code is contained in another. With 50 memos many offices look alike: Tulsa and Tucson, Riga and Reykjavik. Every miss in these runs is the code of a different memo. None is an invented code.

## Rebuilding a context

```
python scripts/build_prompts.py --run 88m_20 --out prompts_88m_20
python scripts/build_prompts.py --run 10m_20 --out prompts_10m_20
python scripts/build_prompts.py --run 10m_50_lookalike --out prompts_10m_50
```

The script writes the context as text and the run's questions. It needs only the Python standard library.

## Files

```
results/    one row per question: code, depth, answer, right or wrong, and which memo a miss came from
            10m_20.jsonl  88m_20.jsonl  10m_50_lookalike.jsonl  results.csv  summary.json
needles/    each run's memos: office, code, depth and where in the filings text it was planted
haystack/   sp500_filings.txt.xz  the filings, 88M tokens of text (346 MB unpacked), 1,269 filings
            sp500_manifest.json   each filing: ticker, CIK, company, form, filing date, where it is in the text
raw/        88m_20_transcript.jsonl  the 88M run, question by question: office, depth, question, answer
scripts/    build_prompts.py  verify.py
SHA256SUMS
```

`python scripts/verify.py` recounts every number above from the rows.

## Note

- **Choice of setting after seeing results.** One setting was chosen after seeing results on the 50-code set. The 88M run was not used for any choice; it was run afterwards, as a check.

## Source and license

The haystack is the text of public SEC filings, from SEC EDGAR. The results, the scripts and this card are released under CC BY 4.0.
