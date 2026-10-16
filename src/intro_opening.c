#include "global.h"
#include "gflib.h"
#include "main.h"
#include "m4a.h"
#include "scanline_effect.h"
#include "new_menu_helpers.h"
#include "intro_opening.h"
#include "constants/songs.h"
#define OPENING_FRAME_COUNT 752
#define OPENING_FRAME_BYTES (240 * 96)
#define OPENING_PAGE_BYTES 0xA000
#define OPENING_VIEW_OFFSET (240 * 32)
#define OPENING_PAGE_SELECT 0x0010
#define OPENING_MUSIC_START 20
#define OPENING_ASSET __attribute__((section(".opening_movie"), aligned(4)))
static const u32 sOpeningMoviePixels[] OPENING_ASSET = INCBIN_U32("graphics/intro/opening_movie_v7/pixels.8bpp");
static const u16 sOpeningMoviePalettes[] OPENING_ASSET = INCBIN_U16("graphics/intro/opening_movie_v7/palettes.gbapal");
static const u32 sOpeningMovieFrames[] OPENING_ASSET = INCBIN_U32("graphics/intro/opening_movie_v7/frames.bin");
STATIC_ASSERT(sizeof(sOpeningMovieFrames) == OPENING_FRAME_COUNT * 8, opening_movie_frame_count);
STATIC_ASSERT(sizeof(sOpeningMoviePixels) % OPENING_FRAME_BYTES == 0, opening_movie_pixel_size);
STATIC_ASSERT(sizeof(sOpeningMoviePalettes) % 512 == 0, opening_movie_palette_size);
struct OpeningMovieState { u16 nextFrame; u16 maxVcountEnd; u8 page; bool8 ready; bool8 musicStarted; u8 reserved; IntrCallback previousVBlank; };
static EWRAM_DATA struct OpeningMovieState *sOpening = NULL;
EWRAM_DATA u16 gOpeningDroppedFrames = 0;
static void OpeningMovie_VBlank(void);
static void OpeningMovie_SetupDisplay(void)
{
 SetVBlankCallback(NULL); SetHBlankCallback(NULL); DisableInterrupts(INTR_FLAG_HBLANK);
 ScanlineEffect_Stop(); SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_FORCED_BLANK); REG_DISPCNT = DISPCNT_FORCED_BLANK;
 ResetSpriteData(); FreeAllSpritePalettes(); ResetPaletteFade(); ResetBgsAndClearDma3BusyFlags(FALSE); ClearDma3Requests();
 DmaFill32(3, 0, (void *)VRAM, 0x14000); FillPalette(RGB_BLACK, 0, PLTT_SIZE);
 SetGpuReg(REG_OFFSET_BLDCNT, 0); SetGpuReg(REG_OFFSET_BLDALPHA, 0); SetGpuReg(REG_OFFSET_BLDY, 0); SetGpuReg(REG_OFFSET_MOSAIC, 0);
 SetGpuReg(REG_OFFSET_BG2CNT, 0); SetGpuReg(REG_OFFSET_BG2PA, 0x100); SetGpuReg(REG_OFFSET_BG2PB, 0); SetGpuReg(REG_OFFSET_BG2PC, 0); SetGpuReg(REG_OFFSET_BG2PD, 0x100);
 SetGpuReg(REG_OFFSET_BG2X_L, 0); SetGpuReg(REG_OFFSET_BG2X_H, 0); SetGpuReg(REG_OFFSET_BG2Y_L, 0); SetGpuReg(REG_OFFSET_BG2Y_H, 0);
 sOpening->ready = TRUE; SetVBlankCallback(OpeningMovie_VBlank);
}
void Opening_Init(void)
{
 if (sOpening != NULL) Opening_Free();
 gOpeningDroppedFrames = 0; sOpening = AllocZeroed(sizeof(*sOpening));
 if (sOpening == NULL) { gOpeningDroppedFrames = 0xFFFF; return; }
 sOpening->previousVBlank = gMain.vblankCallback;
}
static void OpeningMovie_VBlank(void)
{
 u16 frame; u16 vcount; u16 paletteIndex; u32 pixelOffset; u8 targetPage; void *target;
 if (sOpening == NULL || !sOpening->ready) return;
 frame = sOpening->nextFrame; if (frame >= OPENING_FRAME_COUNT) return;
 vcount = REG_VCOUNT;
 if (vcount < 160 || vcount > 168 || WaitDma3Request(-1) != 0) { gOpeningDroppedFrames++; return; }
 pixelOffset = sOpeningMovieFrames[frame * 2]; paletteIndex = sOpeningMovieFrames[frame * 2 + 1] & 0xFFFF;
 targetPage = sOpening->page ^ 1; target = (u8 *)VRAM + targetPage * OPENING_PAGE_BYTES + OPENING_VIEW_OFFSET;
 DmaCopy32(3, (const u8 *)sOpeningMoviePixels + pixelOffset, target, OPENING_FRAME_BYTES);
 vcount = REG_VCOUNT;
 if (vcount < 160 || vcount >= 220) { gOpeningDroppedFrames++; return; }
 LoadPalette(sOpeningMoviePalettes + paletteIndex * 256, 0, 512); TransferPlttBuffer();
 SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_4 | DISPCNT_BG2_ON | (targetPage ? OPENING_PAGE_SELECT : 0));
 sOpening->page = targetPage; sOpening->nextFrame++;
 vcount = REG_VCOUNT; if (vcount > sOpening->maxVcountEnd) sOpening->maxVcountEnd = vcount;
}
u8 Opening_Run(void)
{
 u16 frame;
 if (sOpening == NULL) return 0;
 if (!sOpening->ready) { if (FreeTempTileDataBuffersIfPossible() || WaitDma3Request(-1) != 0) return 1; OpeningMovie_SetupDisplay(); return 1; }
 frame = sOpening->nextFrame;
 if (frame >= OPENING_MUSIC_START && !sOpening->musicStarted) { m4aSongNumStart(MUS_INTRO_FIGHT); sOpening->musicStarted = TRUE; }
 if (frame >= OPENING_FRAME_COUNT) return 0;
 if (frame < 24) return 1; if (frame < 120) return 2; if (frame < 276) return 3; if (frame < 342) return 4; if (frame < 468) return 5; return 6;
}
void Opening_Free(void)
{
 if (sOpening != NULL) { SetVBlankCallback(sOpening->previousVBlank); Free(sOpening); sOpening = NULL; }
}
