#!/usr/bin/env python3
"""intent_lint: every repo states why it exists, in the file every harness reads, with a date.

Class it blocks (2026-10-03): a session opens a repo and loads stale handoff state instead of
the repo's purpose. Found across the 24-repo fleet: no repo had an intent statement; three had a
root SPEC.md of three different kinds (one normative, one historical for a site no domain serves,
one a ROM candidate), and two repos still named a May 2026 arc as "active". A missing or stale
"why" is invisible until a session acts on it.

Rule (deterministic, stdlib-only). A checked repo MUST have:
  1. AGENTS.md (the cross-harness file) holding one block fenced by
     <!-- intent:begin --> ... <!-- intent:end -->
  2. Inside the block, a non-empty bullet for each field:
       Why · Done looks like · Not this · Status · Last verified · Spec
  3. Status is one of: live | active | dormant | archived
  4. Last verified starts with an ISO date (YYYY-MM-DD) and says how it was verified (text after
     the date). The date is no older than --max-age days (default 90), except for Status
     `archived`: a finished repo does not go stale, so its age is not checked.
  5. If a root SPEC.md exists, the Spec field names SPEC.md and its standing:
     normative | historical | candidate. A spec nobody vouches for is drift.
  6. If CLAUDE.md exists it imports @AGENTS.md; if it does not exist, FAIL (Claude Code
     auto-loads CLAUDE.md only, so the intent would be invisible to it). Exception: AGENTS.md
     carries <!-- intent:claude-md-payload --> when CLAUDE.md is the repo's product (e.g. a
     backup of ~/.claude), where an import line would travel with the payload.

Canon template + rationale: flashesofbrilliance/arcs-v9 _PATTERNS/2026-10-03-repo-intent-block.md
Runs in every repo via the reusable workflow .github/workflows/intent-lint.yml in this repo.

Usage: python3 scripts/intent_lint.py <repo-dir> [...] [--max-age N] [--today YYYY-MM-DD]
       python3 scripts/intent_lint.py --self-test
Exit 1 on any FAIL.
"""
import datetime as dt
import os
import re
import sys
import tempfile

FIELDS = ["Why", "Done looks like", "Not this", "Status", "Last verified", "Spec"]
STATUSES = {"live", "active", "dormant", "archived"}
STANDINGS = {"normative", "historical", "candidate"}
BLOCK_RE = re.compile(r"<!-- intent:begin -->(.*?)<!-- intent:end -->", re.S)
FIELD_RE = re.compile(r"^\s*[-*]\s*\*\*(.+?):\*\*\s*(.*)$")


def parse_block(text):
    m = BLOCK_RE.search(text)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        f = FIELD_RE.match(line)
        if f:
            out[f.group(1).strip()] = f.group(2).strip()
    return out


def check_repo(path, max_age=90, today=None):
    today = today or dt.date.today()
    errs = []
    agents = os.path.join(path, "AGENTS.md")
    if not os.path.isfile(agents):
        return ["no AGENTS.md"]
    block = parse_block(open(agents, encoding="utf-8").read())
    if block is None:
        return ["AGENTS.md has no <!-- intent:begin --> ... <!-- intent:end --> block"]
    for f in FIELDS:
        if not block.get(f):
            errs.append(f"field missing or empty: {f}")
    status = block.get("Status", "").split()[0].strip("`*.,").lower() if block.get("Status") else ""
    if status and status not in STATUSES:
        errs.append(f"Status '{status}' not in {sorted(STATUSES)}")
    lv = block.get("Last verified", "")
    dm = re.match(r"(\d{4}-\d{2}-\d{2})\s*(.*)", lv)
    if lv and not dm:
        errs.append("Last verified must start with YYYY-MM-DD")
    elif dm:
        try:
            age = (today - dt.date.fromisoformat(dm.group(1))).days
            if age > max_age and status != "archived":
                errs.append(f"Last verified is {age} days old (max {max_age})")
            if age < 0:
                errs.append("Last verified is in the future")
        except ValueError:
            errs.append(f"Last verified date invalid: {dm.group(1)}")
        if len(dm.group(2).strip(" ()-:")) < 8:
            errs.append("Last verified must say how it was verified, after the date")
    if os.path.isfile(os.path.join(path, "SPEC.md")):
        spec = block.get("Spec", "")
        if "SPEC.md" not in spec:
            errs.append("root SPEC.md exists but the Spec field does not name it")
        elif not any(s in spec.lower() for s in STANDINGS):
            errs.append(f"Spec field must give SPEC.md a standing: {sorted(STANDINGS)}")
    claude = os.path.join(path, "CLAUDE.md")
    if "<!-- intent:claude-md-payload -->" in open(agents, encoding="utf-8").read():
        pass
    elif not os.path.isfile(claude):
        errs.append("no CLAUDE.md: Claude Code will not load AGENTS.md (add one line: @AGENTS.md)")
    elif "@AGENTS.md" not in open(claude, encoding="utf-8").read():
        errs.append("CLAUDE.md does not import @AGENTS.md")
    return errs


def main(argv):
    if "--self-test" in argv:
        return self_test()
    max_age, today, repos, i = 90, None, [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--max-age":
            max_age = int(argv[i + 1]); i += 2; continue
        if a == "--today":
            today = dt.date.fromisoformat(argv[i + 1]); i += 2; continue
        repos.append(a); i += 1
    if not repos:
        print(__doc__); return 2
    failed = 0
    for r in repos:
        errs = check_repo(r, max_age, today)
        name = os.path.basename(os.path.abspath(r))
        if errs:
            failed += 1
            print(f"FAIL  {name}")
            for e in errs:
                print(f"      - {e}")
        else:
            print(f"PASS  {name}")
    print(f"\n{len(repos) - failed}/{len(repos)} pass")
    return 1 if failed else 0


GOOD = """# x
<!-- intent:begin -->
## Intent
- **Why:** reason
- **Done looks like:** done
- **Not this:** not
- **Status:** active
- **Last verified:** 2026-10-01 (git log + README read)
- **Spec:** SPEC.md (normative)
<!-- intent:end -->
"""


def self_test():
    today = dt.date(2026, 10, 3)
    cases = [
        ("good", {"AGENTS.md": GOOD, "CLAUDE.md": "@AGENTS.md", "SPEC.md": "s"}, True),
        ("good, no spec", {"AGENTS.md": GOOD.replace("SPEC.md (normative)", "none"),
                           "CLAUDE.md": "@AGENTS.md"}, True),
        ("no AGENTS.md", {"CLAUDE.md": "@AGENTS.md"}, False),
        ("no block", {"AGENTS.md": "# x", "CLAUDE.md": "@AGENTS.md"}, False),
        ("bad status", {"AGENTS.md": GOOD.replace("active", "vibes"), "CLAUDE.md": "@AGENTS.md"}, False),
        ("stale date", {"AGENTS.md": GOOD.replace("2026-10-01", "2026-05-01"), "CLAUDE.md": "@AGENTS.md"}, False),
        ("stale but archived", {"AGENTS.md": GOOD.replace("2026-10-01", "2026-05-01").replace("active", "archived"),
                                "CLAUDE.md": "@AGENTS.md", "SPEC.md": "s"}, True),
        ("no how", {"AGENTS.md": GOOD.replace(" (git log + README read)", ""), "CLAUDE.md": "@AGENTS.md"}, False),
        ("spec unvouched", {"AGENTS.md": GOOD.replace("SPEC.md (normative)", "see repo"),
                            "CLAUDE.md": "@AGENTS.md", "SPEC.md": "s"}, False),
        ("spec no standing", {"AGENTS.md": GOOD.replace("(normative)", "(the spec)"),
                              "CLAUDE.md": "@AGENTS.md", "SPEC.md": "s"}, False),
        ("no CLAUDE.md", {"AGENTS.md": GOOD}, False),
        ("CLAUDE.md no import", {"AGENTS.md": GOOD, "CLAUDE.md": "# hi"}, False),
        ("CLAUDE.md is payload", {"AGENTS.md": GOOD + "<!-- intent:claude-md-payload -->\n",
                                  "CLAUDE.md": "# hi", "SPEC.md": "s"}, True),
        ("empty field", {"AGENTS.md": GOOD.replace("- **Not this:** not", "- **Not this:**"),
                         "CLAUDE.md": "@AGENTS.md"}, False),
    ]
    ok = 0
    for name, files, expect_pass in cases:
        with tempfile.TemporaryDirectory() as d:
            for fn, body in files.items():
                open(os.path.join(d, fn), "w", encoding="utf-8").write(body)
            errs = check_repo(d, 90, today)
        passed = not errs
        good = passed == expect_pass
        ok += good
        print(f"{'ok ' if good else 'BAD'}  {name}: {'pass' if passed else 'fail'} {errs if not good else ''}")
    print(f"\nself-test {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
