import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote

LINK = re.compile(r'(?<!!)\[[^]]+\]\(([^)]+)\)')
HEADING = re.compile(r'^#{1,6}\s+(.+)$', re.M)
CLAIM = re.compile(r'\b(?:always|never|guaranteed|100%|zero downtime|fully secure|compliant)\b', re.I)
OWNER = re.compile(r'^owner:\s*\S+', re.M | re.I)
REVIEW = re.compile(r'^reviewed:\s*\d{4}-\d{2}-\d{2}', re.M | re.I)

def slug(s):
    return re.sub(r'[^\w-]', '', re.sub(r'\s+', '-', s.strip().lower()))

def audit(root):
    root = Path(root).resolve()
    files = sorted(p for p in root.rglob('*.md') if '.git' not in p.parts)
    findings = []
    for p in files:
        source = p.read_text(encoding='utf-8')
        rel = p.relative_to(root).as_posix()
        def add(rule, severity, line, message):
            findings.append(dict(file=rel, rule=rule, severity=severity, line=line, message=message))
        if not OWNER.search(source[:1000]):
            add('ownership', 'warning', 1, 'Missing owner: metadata')
        if not REVIEW.search(source[:1000]):
            add('review-date', 'warning', 1, 'Missing reviewed: YYYY-MM-DD metadata')
        for m in CLAIM.finditer(source):
            add('claim-risk', 'warning', source.count('\n', 0, m.start()) + 1, f'Absolute claim: {m.group()} (verify evidence and scope)')
        for m in LINK.finditer(source):
            target = unquote(m.group(1).split(' ', 1)[0].strip('<>'))
            if not target or target.startswith(('http:', 'https:', 'mailto:', '#')):
                continue
            pathpart, _, anchor = target.partition('#')
            destination = (p.parent / pathpart).resolve() if pathpart else p
            if root not in destination.parents and destination != root:
                add('link-escape', 'error', source.count('\n', 0, m.start()) + 1, target)
                continue
            if destination.is_dir():
                destination = destination / 'index.md'
            if not destination.exists():
                add('broken-link', 'error', source.count('\n', 0, m.start()) + 1, target)
            elif anchor and destination.suffix.lower() == '.md':
                headings = [slug(h) for h in HEADING.findall(destination.read_text(encoding='utf-8'))]
                if anchor not in headings:
                    add('broken-anchor', 'error', source.count('\n', 0, m.start()) + 1, target)
    return dict(files_scanned=len(files), findings=findings, errors=sum(x['severity']=='error' for x in findings), warnings=sum(x['severity']=='warning' for x in findings))

def main():
    parser = argparse.ArgumentParser(description='Audit Markdown documentation for ownership, claims and local link integrity')
    parser.add_argument('path', nargs='?', default='docs')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--strict', action='store_true', help='Fail on warnings as well as errors')
    args = parser.parse_args()
    result = audit(args.path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Scanned {result['files_scanned']} files: {result['errors']} errors, {result['warnings']} warnings")
        for item in result['findings']:
            print(f"{item['file']}:{item['line']}: {item['severity']} [{item['rule']}] {item['message']}")
    raise SystemExit(1 if result['errors'] or (args.strict and result['warnings']) else 0)

if __name__ == '__main__':
    main()
