#!/usr/bin/env python3
"""Compile the repository's capture handoff and memory owners as a 32-bit host test.

No ROM, save, emulator, or third-party Python package is needed. GPU, sound,
task scheduling and decompression are test doubles; allocation and ownership
code is extracted unchanged from the checkout on every invocation.
"""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile


def function(source, name):
    pattern = r"^[^\n;{}]*\b" + re.escape(name) + r"\([^;]*?\)\s*\n\{.*?^\}"
    match = re.search(pattern, source, re.M | re.S)
    if not match:
        raise AssertionError("Missing C function: " + name)
    return match.group()


def declaration(source, name, kind="object"):
    if kind == "struct":
        pattern = r"^struct " + name + r"\s*\n\{.*?^\};"
    else:
        pattern = r"^[^\n;{}]*\b" + name + r"\b[^;]*?=\s*\{.*?\};"
    match = re.search(pattern, source, re.M | re.S)
    if not match:
        raise AssertionError("Missing C declaration: " + name)
    return match.group()


PRELUDE = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
typedef uint8_t u8; typedef int8_t s8;
typedef uint16_t u16; typedef int16_t s16;
typedef uint32_t u32; typedef int32_t s32;
typedef u8 bool8; typedef u16 bool16; typedef u32 bool32;
#define TRUE 1
#define FALSE 0
#define EWRAM_DATA
#define COMMON_DATA
#define MAX_BATTLERS_COUNT 4
#define NATIONAL_DEX_COUNT 386
#define WINDOWS_MAX 32
#define PIXEL_FILL(n) ((n)|((n)<<4))
#define BG_SCREEN_SIZE 2048
#define BG_ATTR_MAPSIZE 0
#define BG_TILE_FIND_FREE_SPACE 0
#define BG_TILE_ALLOC 1
#define COPYWIN_GFX 2
#define FONT_SMALL 0
#define FONT_NORMAL 1
#define PALETTES_ALL 0xffffffff
#define RGB_WHITE 0x7fff
#define RGB_BLACK 0
#define BATTLE_TYPE_LINK 2
#define BATTLE_TYPE_TRAINER 8
#define BATTLE_TYPE_DOUBLE 1
#define BATTLE_TYPE_MULTI 64
#define B_POSITION_OPPONENT_LEFT 1
#define MON_DATA_SPECIES 0
#define SPECIES_NONE 0
#define TASK_ID 1
#define SHINY_ODDS 8
#define FLAG_SET_SEEN 1
#define FLAG_SET_CAUGHT 2
#define FLAG_GET_SEEN 3
#define FLAG_GET_CAUGHT 4
#define INTR_FLAG_VBLANK 1
#define PERSISTENT_HEAP_USABLE_SIZE 80128
#define TEXT_LEFT 0
#define TEXT_CENTER 1
#define FREE_AND_SET_NULL(p) do { Free(p); (p)=NULL; } while (0)
#define FREE_IF_NOT_NULL(p) do { if(p) Free(p); } while (0)
#define NELEMS(a) (sizeof(a)/sizeof((a)[0]))
static jmp_buf exhausted;
static int alloc_failure_expected, failures, sequence, reset_seq, callback_seq;
static int first_free_seq, dex_seq, dma_busy, bg_busy, picture_calls;
static int return_picture_calls, invalid_windows;
static u32 expected_species = 232, expected_otid = 0x12345678, expected_pid = 0x87654321;
static void qa_assert(int ok, const char *file, int line) {
    if (ok) return;
    if (alloc_failure_expected && line == 174) { failures++; longjmp(exhausted, 1); }
    fprintf(stderr, "allocator assertion %s:%d\n", file, line); abort();
}
#define ABSPATH(s) (s)
#define AGB_ASSERT_EX(ok,file,line) qa_assert((ok),(file),(line))
#define CpuFill32(v,p,n) memset((p),(v),(n))
static u8 gHeap[1], vram[0x18000];
#define VRAM vram
#define VRAM_SIZE sizeof(vram)
#define BG_PLTT_SIZE 512
static u16 gPlttBufferFaded[256];
void *Alloc(u32); void *AllocZeroed(u32); void Free(void *);
void FreeAllWindowBuffers(void);
static void note_free(void) { if (!first_free_seq) first_free_seq=++sequence; }
'''

HARDWARE = r'''
static void *bg_buffers[4];
static u8 gWindowTileAutoAllocEnabled;
static void *GetBgTilemapBuffer(u8 bg) { return bg_buffers[bg]; }
static void SetBgTilemapBuffer(u8 bg, void *p) { bg_buffers[bg]=p; }
static u16 GetBgAttribute(u8 bg, u8 attr) { (void)bg;(void)attr; return 2048; }
static int BgTileAllocOp(u8 bg,int a,int n,int op) { (void)bg;(void)a;(void)n;(void)op; return 0; }
static void BattleMainCB2(void) {}
static void VBlankCB(void) {}
static void VBlankCB_Battle(void) {}
static void Task_PokedexScreen(u8 id) { (void)id; }
static void Task_DexScreen_RegisterMonToPokedex(u8 id) { (void)id; }
static void Task_DexScreen_RegisterNonKantoMonBeforeNationalDex(u8 id) { (void)id; }
struct { u8 active,bufferTransferDisabled; } gPaletteFade;
struct { void (*callback2)(void); u8 state; } gMain;
struct { void (*func)(u8); u8 isActive; } gTasks[16];
struct { u32 otId,personality; } gBattleMons[4];
static u8 gEnemyParty[1],gBattleCommunication[8],script[2];
static u8 *gBattlescriptCurrInstr;
static u32 gBattleTypeFlags;
static u16 gBattle_BG3_X;
static u16 GetMonData(const void *p, int field, const void *out) { (void)p;(void)field;(void)out; return expected_species; }
static int WaitDma3Request(int id) { (void)id; return dma_busy ? -1 : 0; }
static void VBlankIntrWait(void) { assert(!dma_busy); }
static void SetVBlankCallback(void (*cb)(void)) { if (cb==NULL) callback_seq=++sequence; }
static void ResetSpriteData(void) { reset_seq=++sequence; }
static void BeginNormalPaletteFade(u32 a,int b,int c,int d,int e) { (void)a;(void)b;(void)c;(void)d;(void)e; }
static int IsDma3ManagerBusyWithBgCopy(void) { return bg_busy; }
static void InitBattleBgsVideo(void) {}
static void LoadBattleTextboxAndBackground(void) {}
static void ShowBg(u8 bg) { (void)bg; }
static u16 CreateMonPicSprite_HandleDeoxys(u16 species,u32 otid,u32 pid,int front,int x,int y,int pal,u16 tag) {
    assert(species==expected_species && otid==expected_otid && pid==expected_pid);
    assert(front==TRUE && x==120 && y==64 && pal==0 && tag==0xffff);
    return_picture_calls++; return 0;
}
static u8 CreateTask(void (*fn)(u8),int priority) { (void)priority;gTasks[0].func=fn;gTasks[0].isActive=1;return 0; }
static void ResetTasks(void) { memset(gTasks,0,sizeof(gTasks)); }
static int IsNationalPokedexEnabled(void) { return TRUE; }
static u16 SpeciesToNationalPokedexNum(u16 s) { return s; }
static u8 GetStoryRegionalDex(void) { return 0; }
static u16 NationalToRegionalDex(u8 r,u16 n) { (void)r;return n; }
static int DexScreen_GetSetPokedexFlag(u16 s,u8 flag,bool8 ix) { (void)s;(void)flag;(void)ix;return TRUE; }
static int DexScreen_GetDexCount(u8 flag,bool8 which) { (void)flag;(void)which;return 1; }
static int DexScreen_LookUpCategoryBySpecies(u16 s) { assert(s==expected_species);return TRUE; }
static void ResetBgsAndClearDma3BusyFlags(int clear) { (void)clear; memset(bg_buffers,0,sizeof(bg_buffers)); }
static void FillWindowPixelBuffer(u8 id,u8 fill) {
    if(id>=WINDOWS_MAX || !gWindows[id].tileData) { invalid_windows++; return; }
    memset(gWindows[id].tileData,fill,32*gWindows[id].window.width*gWindows[id].window.height);
}
static int DecompressPic_HandleDeoxys(u16 species,u32 pid,bool8 front,u8 *dest,bool8 trainer) {
    (void)pid;(void)front;(void)trainer; assert(species>0 && species<412); memset(dest,0x65,8192);picture_calls++;return 0;
}
#define NOOP(...) ((void)0)
#define CopyToBgTilemapBufferRect_ChangePalette NOOP
#define PutWindowTilemap NOOP
#define CopyWindowToVram NOOP
#define CopyToWindowPixelBuffer NOOP
#define DexScreen_PrintMonDexNo NOOP
#define DexScreen_AddTextPrinterParameterized NOOP
#define BlitBitmapRectToWindow NOOP
#define LoadPicPaletteBySlot NOOP
#define DexScreen_DexPageZoomEffectFrame NOOP
#define FillBgTilemapBufferRect_Palette0 NOOP
#define DexScreen_PrintMonCategory NOOP
#define DexScreen_PrintMonHeight NOOP
#define DexScreen_PrintMonWeight NOOP
#define DexScreen_PrintMonAbilities NOOP
#define DexScreen_DrawMonFootprint NOOP
#define DexScreen_PrintMonFlavorText NOOP
#define DexScreen_PrintControlInfo NOOP
#define m4aSoundVSyncOff NOOP
#define ResetPaletteFade NOOP
#define ScanlineEffect_Stop NOOP
#define InitBgsFromTemplates NOOP
#define DecompressAndLoadBgGfxUsingHeap NOOP
#define DeactivateAllTextPrinters NOOP
#define m4aSoundVSyncOn NOOP
#define EnableInterrupts NOOP
#define DexScreen_InitRegionalView NOOP
#define SetBGMVolume_SuppressHelpSystemReduction NOOP
#define ChangeBgX NOOP
#define ChangeBgY NOOP
#define LoadPalette NOOP
#define FillBgTilemapBufferRect NOOP
#define BGMVolumeMax_EnableHelpSystemReduction NOOP
#define UpdatePaletteFade NOOP
static const u8 sCategoryPageIconCoords[4][4][4] = {{{0}}};
static u32 DexScreen_GetDefaultPersonality(u16 species) { (void)species;return 0; }
'''

TESTS = r'''
static u32 largest_block(void) {
    struct MemBlock *p=sHeapStart; u32 n=0;
    do { if(!p->flag && p->size>n)n=p->size;p=p->next; } while(p!=sHeapStart);
    return n;
}
static u8 arena[114688+64], *live_battle;
static void setup(u32 heap_size) {
    memset(arena,0x9d,sizeof(arena));
    InitHeap(arena,heap_size);
    memset(bg_buffers,0,sizeof(bg_buffers));
    memset(gWindows,0,sizeof(gWindows));
    for(unsigned i=0;i<WINDOWS_MAX;i++)gWindows[i].window.bg=0xff;
    memset(gBattleCommunication,0,sizeof(gBattleCommunication));
    memset(gTasks,0,sizeof(gTasks));
    gBattleTypeFlags=0;gMain.callback2=BattleMainCB2;gPaletteFade.active=0;
    sequence=callback_seq=reset_seq=first_free_seq=dex_seq=picture_calls=return_picture_calls=invalid_windows=0;
    dma_busy=bg_busy=0;gBattlescriptCurrInstr=script;
    gBattleMons[1].otId=expected_otid;gBattleMons[1].personality=expected_pid;
    gMonSpritesGfxPtr=NULL;
}
static void battle_fixture(void) {
    /* Opaque live battle state remains allocated through registration. Its
       contents are a canary, not a replacement implementation of battle state. */
    live_battle=AllocZeroed(12288);assert(live_battle);memset(live_battle,0xa7,12288);
    AllocateMonSpritesGfx();
    struct WindowTemplate windows[]={{0,0,0,28,4,0,0},{0,0,0,14,4,0,0},{0,0,0,12,4,0,0},{255,0,0,0,0,0,0}};
    assert(InitWindows(windows));
}
static void check_tail(u32 heap_size) {
    for(unsigned i=heap_size;i<sizeof(arena);i++)assert(arena[i]==0x9d);
}
static void check_gate(void) {
    setup(80128);battle_fixture();
    Cmd_displaydexinfo();assert(gBattleCommunication[0]==1);
    u32 before=largest_block();struct MonSpritesGfx *cache=gMonSpritesGfxPtr;
    gPaletteFade.active=1;Cmd_displaydexinfo();
    assert(gBattleCommunication[0]==1 && gMonSpritesGfxPtr==cache && largest_block()==before && !dex_seq && !first_free_seq);
    gPaletteFade.active=0;dma_busy=1;Cmd_displaydexinfo();
    assert(gBattleCommunication[0]==1 && gMonSpritesGfxPtr==cache && largest_block()==before && !dex_seq && !first_free_seq && !reset_seq);
    check_tail(80128);
}
static void check_link(void) {
    setup(114688);battle_fixture();gBattleTypeFlags=BATTLE_TYPE_LINK;
    struct MonSpritesGfx *cache=gMonSpritesGfxPtr;
    Cmd_displaydexinfo();Cmd_displaydexinfo();
    assert(cache==gMonSpritesGfxPtr && !callback_seq_before_dex && !reset_seq_before_dex);
}
static void run_case(u32 heap_size,int slots,int negative) {
    setup(heap_size);battle_fixture();alloc_failure_expected=negative;
    if(setjmp(exhausted)) {
        assert(negative && heap_size==80128);check_tail(heap_size);
        printf("old-lifetime heap=%u slots=%d exhausted (expected)\n",heap_size,slots);return;
    }
    Cmd_displaydexinfo();Cmd_displaydexinfo();
    assert(gBattleCommunication[0]==2 && gTasks[gBattleCommunication[TASK_ID]].isActive);
    if(!negative) {
        assert(!gMonSpritesGfxPtr && first_free_seq>reset_seq_before_dex && reset_seq_before_dex>callback_seq_before_dex);
        assert(dex_seq>first_free_seq);
    }
    for(int i=0;i<slots;i++)assert(DexScreen_DrawMonPicInCategoryPage(expected_species,i,slots));
    sPokedexScreenData->dexSpecies=expected_species;
    assert(DexScreen_DrawMonDexPage(TRUE));
    assert(!invalid_windows && picture_calls==slots+1 && CheckHeap());
    Cmd_displaydexinfo();assert(gBattleCommunication[0]==2);
    gTasks[0].isActive=0;gMain.callback2=NULL;Cmd_displaydexinfo();assert(gBattleCommunication[0]==2);
    gMain.callback2=BattleMainCB2;gPaletteFade.active=1;Cmd_displaydexinfo();assert(gBattleCommunication[0]==2);
    gPaletteFade.active=0;gMain.state=2;assert(DoClosePokedex());sPokedexScreenData=NULL;
    Cmd_displaydexinfo();assert(gBattleCommunication[0]==3);
    Cmd_displaydexinfo();assert(gBattleCommunication[0]==4);
    bg_busy=1;Cmd_displaydexinfo();assert(gBattleCommunication[0]==4 && !return_picture_calls);
    bg_busy=0;Cmd_displaydexinfo();assert(gBattleCommunication[0]==5 && return_picture_calls==1);
    gPaletteFade.active=1;Cmd_displaydexinfo();assert(gBattlescriptCurrInstr==script);
    gPaletteFade.active=0;Cmd_displaydexinfo();assert(gBattlescriptCurrInstr==script+1);
    FreeMonSpritesGfx();FreeMonSpritesGfx();assert(CheckHeap());check_tail(heap_size);
    FreeAllWindowBuffers();FreeAllWindowBuffers();
    for(unsigned i=0;i<12288;i++)assert(live_battle[i]==0xa7);
    printf("%s heap=%u slots=%d pass, pictures=%d\n",negative?"old-lifetime":"fixed",heap_size,slots,picture_calls);
}
int main(void) {
#ifndef ALLOW_NATIVE_ABI
    _Static_assert(sizeof(void*)==4,"Use a 32-bit compiler (-m32)");
    _Static_assert(sizeof(struct MemBlock)==16,"GBA allocator header ABI");
    _Static_assert(sizeof(struct MonSpritesGfx)==0x180,"GBA graphics-cache ABI");
#endif
    printf("ABI pointer=%zu allocator-header=%zu cache=%zu\n",sizeof(void*),sizeof(struct MemBlock),sizeof(struct MonSpritesGfx));
#ifdef OLD_LIFETIME
    for(int slots=1;slots<=4;slots++)run_case(80128,slots,1);
    assert(failures>0);alloc_failure_expected=0;
    for(int slots=1;slots<=4;slots++)run_case(114688,slots,1);
#else
    check_gate();check_link();
    for(int repeat=0;repeat<2;repeat++)for(int slots=1;slots<=4;slots++) {
        run_case(80128,slots,0);run_case(114688,slots,0);
    }
#endif
    puts("PASS: compiled capture/window/cache/allocator ownership tests");return 0;
}
'''


def make_harness(root):
    sources = {}
    def read(path):
        sources[path] = (root / path).read_text(encoding="utf-8")
        return sources[path]
    malloc = read("src/malloc.c")
    window = read("src/window.c")
    gfx = read("src/battle_gfx_sfx_util.c")
    dex = read("src/pokedex_screen.c")
    sprites = read("src/trainer_pokemon_sprites.c")
    battle = read("src/battle_script_commands.c")
    reshow = read("src/reshow_battle_screen.c")
    sprite_header = read("include/sprite.h")
    battle_header = read("include/battle.h")
    window_header = read("include/window.h")
    pieces = [PRELUDE]
    pieces += [declaration(window_header,n,"struct") for n in ("WindowTemplate","Window")]
    pieces += [declaration(sprite_header,n,"struct") for n in ("SpriteFrameImage","SpriteTemplate")]
    # SpriteTemplate's callback uses the project's forward typedef.
    pieces.insert(1,"struct Sprite; typedef void (*SpriteCallback)(struct Sprite *);\n")
    pieces += [declaration(battle_header,"MonSpritesGfx","struct")]
    pieces += ["struct ListMenuItem {const u8 *label; s32 index;};\n"]
    pieces += [declaration(dex,"PokedexScreenData","struct")]
    pieces += ["static struct PokedexScreenData *sPokedexScreenData;\n"]
    pieces += ["static struct MonSpritesGfx *gMonSpritesGfxPtr;\nstatic const struct SpriteTemplate gSpriteTemplates_Battlers[4]={{0}};\n"]
    pieces += ["static struct Window gWindows[WINDOWS_MAX];\nstatic void *gWindowBgTilemapBuffers[4];\nstatic u8 gWindowClearTile;\n"]
    pieces += [re.sub(r'^#include[^\n]*\n','',malloc,flags=re.M)]
    # Instrument Free at the call boundary; the allocator body above is unchanged.
    pieces += ["static void tracked_free(void *p) { note_free(); Free(p); }\n#define Free tracked_free\n"]
    pieces += [HARDWARE, declaration(window,"sDummyWindowTemplate")]
    pieces += [function(window,"nullsub_8"), function(window,"GetNumActiveWindowsOnBg")]
    pieces += [function(window,n) for n in ("InitWindows","AddWindow","FreeAllWindowBuffers")]
    if "AllocateMonSpritesGfxForPositions" in gfx:
        pieces += [function(gfx,"AllocateMonSpritesGfxForPositions")]
    pieces += [function(gfx,n) for n in ("AllocateMonSpritesGfx","FreeMonSpritesGfx")]
    pieces += [function(reshow,"ReshowBattleScreenDummy")]
    pieces += [declaration(dex,n) for n in ("sWindowTemplates","sDexScreenDataInitialState","sWindowTemplate_CategoryMonIcon","sWindowTemplate_CategoryMonInfo","sWindowTemplate_DexEntry_MonPic","sWindowTemplate_DexEntry_SpeciesStats","sWindowTemplate_DexEntry_FlavorText")]
    pieces += [function(sprites,n) for n in ("CreateTrainerCardSprite","LoadMonPicInWindow")]
    pieces += [function(dex,n) for n in ("DexScreen_LoadMonPicInWindow","DexScreen_DrawMonPicInCategoryPage","DexScreen_DrawMonDexPage","DexScreen_LoadResources","DoClosePokedex")]
    pieces += ["static int callback_seq_before_dex,reset_seq_before_dex;\n"]
    register = function(dex,"DexScreen_RegisterMonToPokedex")
    register = register.replace("DexScreen_RegisterMonToPokedex(","actual_register(",1)
    pieces += [register]
    pieces += ["static u8 DexScreen_RegisterMonToPokedex(u16 species) { dex_seq=++sequence; callback_seq_before_dex=callback_seq; reset_seq_before_dex=reset_seq; return actual_register(species); }\n"]
    cmd = function(battle,"Cmd_displaydexinfo")
    # The negative control keeps the same state machine and drops only the
    # new resource handoff. A broken no-free mutation must exhaust the heap.
    old = cmd
    old = re.sub(r'\s*if \(!\(gBattleTypeFlags & BATTLE_TYPE_LINK\)\)\s*\{[^{}]*\}',"",old)
    old = re.sub(r'^\s*ReshowBattleScreenDummy\(\);\s*$',"",old,flags=re.M)
    pieces += ["#ifdef OLD_LIFETIME\n",old,"\n#else\n",cmd,"\n#endif\n",TESTS]
    return "\n".join(pieces), sources


def decode_lz(raw):
    assert len(raw)>=4 and raw[0]==0x10, "Not GBA LZ77"
    size=int.from_bytes(raw[1:4],"little")
    assert size<=8192, size
    output=bytearray();index=4
    while len(output)<size:
        flags=raw[index];index+=1
        for bit in range(7,-1,-1):
            if len(output)>=size: break
            if flags & (1<<bit):
                pair=int.from_bytes(raw[index:index+2],"big");index+=2
                length=(pair>>12)+3;distance=(pair&4095)+1
                assert distance<=len(output) and len(output)+length<=size
                for _ in range(length):output.append(output[-distance])
            else:
                output.append(raw[index]);index+=1
    return bytes(output)


def validate_data(root,built=False):
    """Inspect actual table references and PNG IHDR bounds, without ROM copies."""
    categories = (root/"src/data/pokemon/pokedex_categories.h").read_text()
    pages = re.findall(r'static const u16\s+\w+_Page\d+\[\]\s*=\s*\{(.*?)\};',categories,re.S)
    counts = collections.Counter(len(re.findall(r'\bSPECIES_[A-Z0-9_]+\b',p)) for p in pages)
    assert pages and set(counts)=={1,2,3,4}, counts
    category_species=set(re.findall(r'\bSPECIES_([A-Z0-9_]+)\b'," ".join(pages)))
    assert len(category_species)==386, len(category_species)
    table=(root/"src/data/pokemon_graphics/front_pic_table.h").read_text()
    refs=re.findall(r'SPECIES_SPRITE\(([A-Z0-9_]+),\s*(gMonFrontPic_[A-Za-z0-9_]+)\)',table)
    assert len(refs)>=412
    assert category_species <= {name for name,_ in refs}
    graphics=(root/"src/data/graphics/pokemon.h").read_text()+(root/"src/graphics.c").read_text()
    symbols=dict(re.findall(r'const u32\s+(gMonFrontPic_[A-Za-z0-9_]+)\[\]\s*=\s*INCBIN_U32\("([^"]+)"\)',graphics))
    checked=0
    for name,body in refs:
        symbol=re.search(r'gMonFrontPic_[A-Za-z0-9_]+',body)
        if not symbol or symbol.group() not in symbols:
            continue
        path=symbols[symbol.group()]
        pngs=[root/re.sub(r'\.4bpp\.lz$', '.png',path)]
        if symbol.group()=="gMonFrontPic_Castform":
            pngs=[root/("graphics/pokemon/castform/"+form+"/front.png") for form in ("normal","sunny","rainy","snowy")]
        picture_bytes=0
        for png in pngs:
            raw=png.read_bytes()
            assert raw[:8]==b'\x89PNG\r\n\x1a\n'
            width,height=struct.unpack('>II',raw[16:24])
            assert width==64 and height%64==0,(name,width,height)
            picture_bytes+=width*height//2
        assert picture_bytes<=8192,(name,picture_bytes)
        if built:
            assert len(decode_lz((root/path).read_bytes()))==picture_bytes,(name,path)
        checked+=1
    assert checked>=386, checked
    assert all("SPECIES_SPRITE(UNOWN_"+suffix+"," in table for suffix in [chr(x) for x in range(66,91)]+["EMARK","QMARK"])
    palettes_checked=0
    if built:
        palette_symbols=dict(re.findall(r'const u32\s+(gMon(?:Shiny)?Palette_[A-Za-z0-9_]+)\[\]\s*=\s*INCBIN_U32\("([^"]+)"\)',graphics))
        for table_name in ("palette_table.h","shiny_palette_table.h"):
            palette_table=(root/"src/data/pokemon_graphics"/table_name).read_text()
            for symbol in re.findall(r'SPECIES_(?:SHINY_)?PAL\([^,]+,\s*(\w+)\)',palette_table):
                decoded=decode_lz((root/palette_symbols[symbol]).read_bytes())
                assert len(decoded)==(128 if symbol.endswith("Castform") else 32),(symbol,len(decoded))
                palettes_checked+=1
        assert palettes_checked>=878,palettes_checked
    return {"category_pages":len(pages),"category_species":len(category_species),"category_page_sizes":dict(sorted(counts.items())),"front_picture_png_bounds_checked":checked,"front_picture_lz_decoded":checked if built else 0,"palette_lz_decoded":palettes_checked,"scratch_bytes":8192}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument("--cc",default=os.environ.get("CC","gcc"))
    parser.add_argument("--native-abi",action="store_true",help="Supplemental host-only run; CI must use default 32-bit ABI")
    parser.add_argument("--built-assets",action="store_true",help="Also decode the build's front-picture and palette LZ streams")
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    source,inputs=make_harness(args.root)
    report={"scope":"compiled host ownership regression, not an emulator or iOS test","abi":"native supplemental" if args.native_abi else "32-bit GBA-compatible pointers/allocator header","data":validate_data(args.root,args.built_assets),"sources_sha256":{p:hashlib.sha256(s.encode()).hexdigest() for p,s in inputs.items()},"runs":[]}
    with tempfile.TemporaryDirectory(prefix="capture-dex-") as directory:
        tmp=Path(directory);c=tmp/"capture.c";c.write_text(source)
        for name,defines in [("fixed",[]),("old-lifetime",["-DOLD_LIFETIME"])]:
            exe=tmp/(name+(".exe" if os.name=="nt" else ""))
            cmd=[args.cc,"-std=gnu11","-O0","-g","-Werror=implicit-function-declaration","-Werror=return-type"]
            cmd += ["-DALLOW_NATIVE_ABI"] if args.native_abi else ["-m32"]
            cmd+=defines+[str(c),"-o",str(exe)]
            subprocess.run(cmd,check=True)
            result=subprocess.run([str(exe)],check=True,text=True,capture_output=True)
            print(result.stdout,end="")
            report["runs"].append({"variant":name,"stdout":result.stdout,"exit_code":result.returncode})
    report["status"]="PASS"
    if args.report:
        args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":"PASS","abi":report["abi"],"data":report["data"]},sort_keys=True))


if __name__=="__main__":
    main()
