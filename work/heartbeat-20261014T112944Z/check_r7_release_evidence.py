"""Read-only report acceptance for the actual-heal/Brawly R7 continuation.

This checker does not run an emulator and is not a native-pass claim by itself.
"""
from pathlib import Path
import argparse, hashlib, json

ROM = 'af2677993a75979fb36f0768c390d1bad7424e61f2d569b5054d40702250d2e8'
ELF = '2549852a48935c680e06e81719b54663b9c0efa7fdaccd31d1f4683886c5d64e'
ABI = 'a1b45d0bb353e6613855e62e30072b7d872714e62992f05cea50aff10eeb6478'
USER = '917c24715ca1dd78b22d6350182648fa81f307b771fa5524595d157a0b6a6604'
CHECKPOINT = '374d437ca56d45b04e5e66d6213203fa8cef85c1e0e3c537474a4e30a5b39190'
PRIOR = '3c03a5af65d76b98198b70cd7a509f08ab54c5a58b9b8c9ed6e67089ef23f614'
STAGES = [
    '00-natural-SAVE75-no-dock-replay', '01-native-centre-entry',
    '03-actual-nurse-healed-all-six', '04-native-centre-exit',
    '05-native-Gym-entry', '06-native-Brawly-front',
    '07-Brawly-Badge02-TM08', '08-Brawly-repeat-no-duplicate',
    '09-native-Brawly-SAVE-cold', '10-Brawly-repeat-after-cold-no-duplicate',
    '11-normal-Gym-exit',
]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--expected-report-sha', required=True)
    p.add_argument('--qa-save', required=True, type=Path)
    p.add_argument('--expected-save-sha', required=True)
    args = p.parse_args()
    assert len(args.expected_report_sha)==64 and sha(args.report)==args.expected_report_sha
    assert len(args.expected_save_sha)==64 and sha(args.qa_save)==args.expected_save_sha
    r = json.loads(args.report.read_text(encoding='utf-8'))
    assert r['pass'] and r['status']=='complete' and r['protected_original_inputs_unchanged']
    assert r['runner_version']==9 and r['runner_revision']==7
    assert (r['ROM_sha256'],r['ELF_sha256'],r['ABI_manifest_sha256'],r['SAV_sha256'])==(ROM,ELF,ABI,USER)
    assert r['checkpoint_sha256']==CHECKPOINT and r['checkpoint_validation_sha256']==PRIOR
    assert r['natural_checkpoint_loaded']['counter']==75
    assert r['natural_checkpoint_loaded']['position']==[43,11,10,9]
    assert r['natural_checkpoint_loaded']['party_600_PC_33744_dex_Hoenn_flags_vars_preserved']
    assert all(r[k]==0 for k in ['RAM_writes','direct_script_calls','forced_battle_outcomes','this_test_preboot_save_edits'])
    assert not r['dock_story_replayed_this_run'] and not r['earlier_parcel_route_replayed']
    assert not r['forest_boat_replayed_this_run'] and not r.get('boat_menus',[])
    assert r['actual_nurse_heal'] and r['Brawly_completed'] and r['native_Dewford_Brawly_continuation']
    assert r['PC_33744_bytes_preserved'] and not r['full_Hoenn_campaign_tested'] and not r['actual_device_fps_measured']
    stages = r['stages'];assert [row['stage']for row in stages]==STAGES
    assert all(row['idle']for row in stages)
    assert stages[0]['location']==[43,11,10,9] and stages[3]['location']==[43,11,2,10]
    assert stages[5]['location'][2:]==[4,4] and stages[-1]['location']==[43,11,8,17]
    assert not any(stages[0][k]for k in ['Badge02','TM08_reward','Brawly_won'])
    assert all(stages[6][k]for k in ['Badge02','TM08_reward','Brawly_won'])
    assert stages[6]['TM08']==stages[0]['TM08']+1
    assert stages[6]['stage1_progress']==max(3,stages[0]['stage1_progress'])
    for row in stages:
        assert all(row[k]==stages[0][k]for k in ['scene','briney','flags','Goods','DiveBalls','ExpShare','grunt_won','twins_won','Dewford_visible'])
    for index in [7,8,9]:
        assert {k:v for k,v in stages[index].items()if k not in ['stage','frame','image']}=={k:v for k,v in stages[6].items()if k not in ['stage','frame','image']}
    heal = r['nurse_healing']
    assert heal['start'][2:]==[7,4] and heal['local']==1 and heal['nurse_xy']==[7,2]
    assert heal['counter_xy']==[7,3] and heal['counter_behavior']=='0x80'
    assert heal['cursor']==0 and heal['choice']=='YES' and heal['actual_keys']==['UP','A','A']
    assert not heal['direct_script_call'] and not heal['RAM_write']
    assert heal['menu_frame']<heal['accepted_frame']<=heal['finished_frame']
    assert heal['all_6_HP_status_PP_restored'] and heal['PC_33744_and_dex_preserved']
    assert len(heal['before'])==len(heal['after'])==6
    assert any(row['hp']<row['maxHP']for row in heal['before'])
    for old,new in zip(heal['before'],heal['after']):
        assert all(old[k]==new[k]for k in ['slot','pid','ot','species','level','maxHP','moves','maxPP','owner_matches_player','is_egg'])
        assert new['hp']==new['maxHP'] and new['hp']>0 and new['status']==0
        assert new['PP']==new['maxPP'] and new['checksum_ok']
    battle = r['actual_Brawly_win']
    assert battle['opponent']==819 and battle['outcome']==1 and battle['actual_keys'] and not battle['double']
    assert battle['actions']>0 and battle['end_frame']>battle['start_frame']
    assert len([b for b in r['battles']if b['opponent']==819])==1
    assert all(b['actual_keys'] and b['outcome']==1 for b in r['battles'])
    saved = r['native_SAVE_cold']
    assert list(saved['counter'])==[75,76] and saved['checksummed_sectors']==14
    assert Path(saved['qa_save']).name==args.qa_save.name
    assert len(r['cases'])==1 and r['cases'][0]['pass']
    assert len(r['final_party_ledger'])==6 and all(row['checksum_ok'] and row['IV_and_origin_preserved']for row in r['final_party_ledger'])
    assert r['prior_actual_Brawly_loss_retained']['not_overwritten']
    print(json.dumps(dict(status='FRESH_R7_REPORT_ACCEPTED',report_sha256=args.expected_report_sha,
                         qa_save_sha256=args.expected_save_sha,native_nurse_Brawly_SAVEcold=True,
                         full_Hoenn_campaign_tested=False,actual_device_fps_measured=False),indent=2))

if __name__=='__main__':
    main()
