#!/usr/bin/env python3
"""Full original Basic QA; only multi-mon creation gets its measured finite budget."""
from pathlib import Path
import hashlib,json
p=Path('tools/qa/native_misty_basic_qa.py');q=p.read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
old='  for _ in range(20):'
assert q.count(old)==1
q=q.replace(old,"  for _ in range(60 if name=='CreateNPCTrainerParty' else 20):")
old="native_battery_save_tested=False,actual_device_fps_measured=False"
assert q.count(old)==1
q=q.replace(old,"native_battery_save_tested=False,creation_call_budget_frames=60,other_call_budget_frames=20,budget_basis=dict(rom_sha256='3b319b64cc1b29a1eacb7a57c50afafd935496614aa9e596b74eb556e1d38806',natural_creation_frames=[15,23,29,34,35],original_20F_failure_preserved=True),actual_device_fps_measured=False")
exec(compile(q,'<full-original-Misty-Basic-with-measured-creation-only-budget>','exec'))
