#!/usr/bin/env python3
"""check_event_wiring.py [--upstream-ref upstream/master] [--no-fail]

Static checks that an event this project added is actually wired up. Read-only.

  dead scripts   an EventScript_* label nothing can reach: not on any object,
                 sign, trigger or map script table, not referenced by a reachable
                 script, and not named from C. Retail FR/LG has unused scripts of
                 its own, so only labels this project added are reported.
  empty promise  a script whose text says the player receives something while the
                 script gives nothing (giveitem/givemon/setflag of a GOT flag).

Exit status 1 when something is reported (0 with --no-fail).
"""
import argparse, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapdata_common as C  # noqa: E402

# phrasings that only make sense when something actually changes hands
PROMISE = re.compile(r'\breceived\b|\bhere you go\b|\byou can have (this|it|these)\b'
                     r"|\bI'?ll (give you|pass this)\b|\btake this\b|\bI want you to have\b"
                     # v0.11.0: phrasings the Z3 survey found the list above missed ("take it!"
                     # only with the "!", or every "take it easy" and full BAG would count)
                     r"|\bshare this\b|\btake it!|\busing this item\b|\btrade (you|it)\b", re.I)
GIVE = ('giveitem', 'giveitem_msg', 'givemon', 'givemon_msg', 'giveegg', 'givecoins', 'givemoney',
        'bufferitemname', 'checkitemspace', 'giveitemfanfare', 'additem', 'setflag')


def script_roots(maps, scripts):
    roots, why = set(), {}
    for name, d in maps.items():
        for key in ('object_events', 'bg_events', 'coord_events'):
            for ev in d.get(key) or []:
                s = ev.get('script')
                if s and s not in ('0x0', '0', 'NULL'):
                    roots.add(s); why.setdefault(s, f'{name} {key}')
        # map script tables: every label the table names
        for lab in scripts.map_labels.get(name, []):
            if lab.endswith('_MapScripts'):
                for ref in scripts.labels[lab]['refs']:
                    roots.add(ref); why.setdefault(ref, f'{name} map script table')
    # labels named from C or from the global script data
    src = ''
    for root, _, files in os.walk(C.rel('src')):
        for f in files:
            if f.endswith('.c'):
                src += open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'\b(\w*EventScript_\w+)\b', src):
        roots.add(m.group(1)); why.setdefault(m.group(1), 'named from C')
    for f in ('data/event_scripts.s',):
        txt = open(C.rel(f)).read()
        for m in re.finditer(r'\b(\w*EventScript_\w+)\b', txt):
            roots.add(m.group(1)); why.setdefault(m.group(1), f)
    return roots, why


def reachable_from(scripts, roots):
    seen, stack = set(), [r for r in roots if r in scripts.labels]
    while stack:
        lab = stack.pop()
        if lab in seen:
            continue
        seen.add(lab)
        info = scripts.labels[lab]
        for nxt in list(info['refs']) + ([info['next']] if info['next'] else []):
            if nxt in scripts.labels and nxt not in seen:
                stack.append(nxt)
    return seen


def ours(path, cache={}):
    if path not in cache:
        cache[path] = C.git_show('upstream/master', path)
    return cache[path] is None


def in_upstream(path, label, cache={}):
    key = (path, label)
    if key not in cache:
        raw = C.git_show('upstream/master', path)
        cache[key] = bool(raw) and (label + '::') in raw
    return cache[key]


_STRING_DIRECTIVE = re.compile(r'^\s*\.string\b')
_STRING_LITERAL = re.compile(r'^\s*\.string\s+("(?:[^"\\]|\\.)*")\s*(?:(?:@|//).*)?$')
_PLAYER_RECEIPT = re.compile(r'(?:\{(?:PLAYER|BUFFER1|STR_VAR_1)\}|\b(?:PLAYER|you|BUFFER1|STR_VAR_1))\s*$', re.I)
_PLAYER_MENTION = re.compile(r'\{(?:PLAYER|BUFFER1|STR_VAR_1)\}|\b(?:PLAYER|you|BUFFER1|STR_VAR_1)\b', re.I)
_NPC_RECEIPT = re.compile(r'\b(?:ELM|I|someone)\s*$', re.I)
def _joined_game_text(body):
    chunks = []
    for line in body.splitlines():
        if not _STRING_DIRECTIVE.match(line):continue
        match = _STRING_LITERAL.fullmatch(line)
        if not match:return None
        literal = match.group(1)[1:-1];chars=[];i=0
        while i<len(literal):
            char=literal[i]
            if char=='\\':
                i+=1
                if i==len(literal):return None
                escaped=literal[i]
                if escaped in 'nlp':chars.append(' ')
                elif escaped in ('"','\\'):chars.append(escaped)
                else:chars.extend(('\\',escaped))
            else:chars.append(char)
            i+=1
        chunks.append(''.join(chars))
    return ' '.join(''.join(chunks).split()) if chunks else None
def has_reward_promise(raw_body):
    text=_joined_game_text(raw_body)
    if text is None:return bool(PROMISE.search(raw_body))
    for match in PROMISE.finditer(text):
        if match.group(0).strip().casefold()!='received':return True
        prefix=text[:match.start()]
        if _PLAYER_RECEIPT.search(prefix):return True
        clause=re.split(r'[.!?;]',prefix)[-1]
        if _NPC_RECEIPT.search(prefix) and not _PLAYER_MENTION.search(clause):continue
        return True
    return False

def script_body(scripts, lab, seen=None):
    """Body and its reachable call/goto/fallthrough labels, including plain names."""
    if seen is None:seen=set()
    if lab in seen or lab not in scripts.labels:return ''
    seen.add(lab);info=scripts.labels[lab]
    with open(C.rel(info['file']),encoding='utf-8',errors='replace') as f:lines=f.read().split('\n')
    out,i='',info['line']
    while i<len(lines) and not C.LABEL_RE.match(lines[i]):
        out+=lines[i]+'\n';i+=1
    children=sorted(info['refs'])
    if info['next']:children.append(info['next'])
    for nxt in children:out+=script_body(scripts,nxt,seen)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--upstream-ref', default='upstream/master')
    ap.add_argument('--no-fail', action='store_true')
    a = ap.parse_args()
    maps, _ = C.load_maps()
    scripts = C.ScriptIndex(maps)
    roots, why = script_roots(maps, scripts)
    live = reachable_from(scripts, roots)

    problems = 0
    print('## dead scripts (nothing can reach them)\n')
    dead = []
    for lab, info in scripts.labels.items():
        if lab in live or 'EventScript' not in lab:
            continue
        if in_upstream(info['file'], lab):
            continue          # retail's own unused script
        dead.append((info['file'], info['line'], lab))
    for f, line, lab in sorted(dead):
        print(f'- {f}:{line} {lab}')
    problems += len(dead)
    print(f'\n{len(dead)} dead\n')

    print('## text promises something the script does not give\n')
    empty = []
    texts = {}
    for name in maps:
        p = f'data/maps/{name}/text.inc'
        if os.path.exists(C.rel(p)):
            body = open(C.rel(p), encoding='utf-8', errors='replace').read()
            for m in re.finditer(r'^(\w+)::\n((?:\s+\.string.*\n)+)', body, re.M):
                texts[m.group(1)] = m.group(2)
    for lab, info in scripts.labels.items():
        if lab not in live or not info['map']:
            continue
        body = script_body(scripts, lab)
        if any(g in body for g in GIVE):
            continue
        for ref in re.findall(r'\b\w+_Text_\w+\b', body):
            if ref in texts and has_reward_promise(texts[ref]) and not in_upstream(f'data/maps/{info["map"]}/text.inc', ref):
                empty.append((info['map'], lab, ref))
                break
    for m, lab, ref in sorted(empty):
        print(f'- {m}: {lab} shows {ref}, which promises something, but gives nothing')
    problems += len(empty)
    print(f'\n{len(empty)} empty promises\n')
    print(f'# check_event_wiring: {problems} to look at')
    sys.exit(1 if problems and not a.no_fail else 0)


if __name__ == '__main__':
    main()
