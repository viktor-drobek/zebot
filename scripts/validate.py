#!/usr/bin/env python3
"""Check a model's zebot-classify answers against the input posts and the vocabulary.

Usage: validate.py INPUT.jsonl OUTPUT.jsonl [--vocab skills/zebot-classify/vocab.md]

Reports, per line: a missing or extra id, a wrong order, an unparsable line, and a class that is
not copied exactly from vocab.md. Exits with status 1 when any problem is found.
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_VOCAB = Path(__file__).resolve().parent.parent / "skills" / "zebot-classify" / "vocab.md"


def load_vocab(path):
    return set(re.findall(r"^- `([^`]+)`\s*$", Path(path).read_text(encoding="utf-8"), re.M))


def load_jsonl(path):
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            rows.append((n, None, "blank line"))
            continue
        try:
            rows.append((n, json.loads(line), None))
        except json.JSONDecodeError as e:
            rows.append((n, None, "not JSON: %s" % e.msg))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--vocab", default=DEFAULT_VOCAB)
    a = ap.parse_args()

    vocab = load_vocab(a.vocab)
    in_ids = [r["id"] for _, r, err in load_jsonl(a.input) if not err]
    problems, out_ids = [], []
    for n, r, err in load_jsonl(a.output):
        if err:
            problems.append("line %d: %s" % (n, err))
            continue
        if set(r) != {"id", "class"}:
            problems.append("line %d: keys must be exactly id and class, got %s" % (n, sorted(r)))
        c = r.get("class")
        if c is not None and c not in vocab:
            problems.append("line %d: class not in vocab.md: %r" % (n, c))
        out_ids.append(r.get("id"))

    missing = [i for i in in_ids if i not in out_ids]
    extra = [i for i in out_ids if i not in in_ids]
    if missing:
        problems.append("missing ids: %s" % missing)
    if extra:
        problems.append("unexpected ids: %s" % extra)
    if not missing and not extra and out_ids != in_ids:
        problems.append("ids are not in input order")

    for p in problems:
        print(p)
    print("%d posts, %d answers, %d problems" % (len(in_ids), len(out_ids), len(problems)))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
