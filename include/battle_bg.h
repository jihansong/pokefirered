#ifndef GUARD_BATTLE_BG_H
#define GUARD_BATTLE_BG_H

#include "bg.h"

extern const struct BgTemplate gBattleBgTemplates[];

void InitBattleBgsVideo(void);
void DrawBattleEntryBackground(void);
void InitLinkBattleVsScreen(u8 taskId);
void LoadBattleMenuWindowGfx(void);
void LoadBattleTextboxAndBackground(void);
void BattleInitBgsAndWindows(void);
bool8 BattlePrepareWindow(u8 windowId);
void BattleReleaseLevelUpWindows(void);
void DrawMainBattleBackground(void);

#endif // GUARD_BATTLE_BG_H
