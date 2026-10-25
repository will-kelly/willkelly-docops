# WK DocOps: evidence-first docs as code

A working Python CLI foundation for a larger documentation governance toolkit. It audits Markdown repositories for broken relative links, missing anchors, missing ownership/review metadata, and risky absolute claims. No runtime dependencies.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
wkdocops docs --json
```

Exit code is nonzero on errors; add `--strict` to fail on warnings. For each Markdown page, place `owner: TeamName` and `reviewed: YYYY-MM-DD` near the top (plain metadata or YAML front matter). This is a lightweight heuristic, not a full YAML parser.

## CI example

```yaml
name: Documentation quality
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e .
      - run: wkdocops docs --strict
```

## Roadmap: higher-order tools

1. **ClaimLedger**: extract factual assertions, evidence URLs, reviewer decisions, and expiration dates into an auditable claims registry.
2. **DocDecay**: rank content by ownership, review age, inbound links, and source-of-truth status; prioritize repair, not word count.
3. **ChangeBlast**: map Git diffs to affected pages, navigation, examples, and downstream FAQs.
4. **Answerability Lab**: generate realistic user questions and check whether published pages answer them with traceable evidence.
5. **Knowledge Contract**: validate metadata, intended audience, prerequisites, task outcome, and maintenance owner before publication.
6. **Pipeline Forensics**: record each human/AI editorial handoff, evidence check, override, and release decision.
7. **DriftWatch**: compare product configuration examples with real source schemas or API specifications.
8. **Content Cost-to-Outcome**: estimate review time, maintenance burden, and measurable content reuse instead of counting pages.

### Design principles

- Deterministic checks first; optional LLM review later.
- No automated truth claims from keyword matches.
- CI should block structural failures and surface editorial risks for human review.
- Keep source citations and decision history with the artifact.

## Limitations

Markdown heading slugs are approximated and may differ from specific static-site generators. External URLs are not fetched. Fenced code blocks and YAML metadata are not fully parsed, so false positives are possible. This is an extensible prototype, not a production compliance scanner.
