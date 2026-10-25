from wkdocops.cli import audit

def test_broken_link_and_claim(tmp_path):
    (tmp_path / 'index.md').write_text('owner: Will\nreviewed: 2026-10-19\n# Intro\nAlways works. [Bad](missing.md)\n')
    result = audit(tmp_path)
    assert result['errors'] == 1
    assert any(f['rule'] == 'claim-risk' for f in result['findings'])

def test_good_anchor(tmp_path):
    (tmp_path / 'a.md').write_text('owner: Docs\nreviewed: 2026-10-19\n[Link](b.md#hello-world)')
    (tmp_path / 'b.md').write_text('owner: Docs\nreviewed: 2026-10-19\n# Hello world')
    assert audit(tmp_path)['errors'] == 0
