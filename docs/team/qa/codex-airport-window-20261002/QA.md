# Airport indoor window draw order — 2026-10-02

The window frame formerly covered the heads/bodies of actors at the lounge window.
The frame must still occlude the exterior plane. The fix raises only indoor object
sprites by the window (including the follower), for both main OAM and body subsprites.
Collision elevations and save structures are unchanged. Current and previous tile
positions prevent a priority change in the middle of crossing the window area.

## Validation

- LeafGreen ROM build and symbols: PASS.
- Existing airport geometry/event suite: 14/14 PASS, including the negative control.
- Existing save compatibility suite: 6/6, loaded save blocks IDENTICAL.
- User pokemonthyl_v1.1.sav disposable copy: window-up, window-left and leaving-window
  runtime checks PASS. Player/NPC/follower priority 1 at glass, exterior plane priority 2;
  player/follower priority returns to 2 away from the glass. Screenshots inspected.
- All 7 original top-level saves remain byte-identical to the pre-test manifest.
- Delta device playback has not been tested. No commit, push or release.

Re-run: python3 tools/qa/airport_window_check.py --save saves/pokemonthyl_v1.1.sav --shots /tmp/airport-window-check

ROM SHA-256: 3b7c5bdc506dc5755b1471e850aad046e3fc3d3a8c8c547c62378a1ed8e684b0
