"""Bounded read-only remote lookup for the original343/349 dex evidence."""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

root = Path(sys.argv[1]).resolve()
deadline = time.monotonic() + 15
found, scanned, excluded_summaries = [], 0, 0
literal = re.compile(r'dex[\s_-]*(?:down|up|scroll)(?!_frames)|pokedex[\s_-]*(?:performance|scroll)', re.I)
python_provenance = re.compile(r'dex_down_frames|dex_up_frames|remaining_dex_scroll_lag')
counter = re.compile(r'"(?:callbacks|processing|main|task_frames|count)"\s*:\s*(?:343|349)\b')
for base in (root / 'tools/qa', root / 'work', root / 'outputs'):
    for directory, children, files in os.walk(base):
        children[:] = sorted((child for child in children if child not in ('.git', 'node_modules', '__pycache__', '.venv', '.cache')),
                             key=lambda child: (not any(key in child.lower() for key in ('dex', 'perf', 'budget', 'font')), child))
        if time.monotonic() > deadline or len(found) >= 12:
            break
        for filename in sorted(files, key=lambda name: (not any(key in name.lower() for key in ('dex', 'perf', 'budget')), name)):
            if time.monotonic() > deadline or len(found) >= 12:
                break
            path = Path(directory) / filename
            if path.suffix not in ('.py', '.json'):
                continue
            if any(key in filename.lower() for key in ('status', 'manifest', 'metadata', 'animation-recreation')):
                continue
            if path.stat().st_size > 1000000:
                continue
            data = path.read_bytes()
            text = data.decode('utf-8', errors='replace')
            scanned += 1
            if path.suffix == '.json':
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed, dict) and ('performance_current' in parsed
                                                or ('regions' in parsed and 'save_current' in parsed)
                                                or ('parallel_ownership' in parsed and 'endings' in parsed)):
                    excluded_summaries += 1
                    continue
            match = literal.search(text) or counter.search(text)
            if path.suffix == '.py':
                match = match or python_provenance.search(text)
            if not match:
                continue
            # Keep the immutable source/report identity, not a proposed file path.
            found.append(dict(path=str(path.relative_to(root)), bytes=len(data),
                              sha256=hashlib.sha256(data).hexdigest(),
                              line=text[:match.start()].count('\n') + 1,
                              context=text[max(0, match.start()-180):match.end()+360]))
    if time.monotonic() > deadline or len(found) >= 12:
        break
print(json.dumps(dict(scope='bounded read-only provenance lookup, not a runtime test',
                      files_scanned=scanned, time_limit_seconds=15, found=found,
                      excluded_embedded_project_statuses=excluded_summaries,
                      truncated=time.monotonic()>deadline or len(found)>=12, write_operations=0), indent=2))
