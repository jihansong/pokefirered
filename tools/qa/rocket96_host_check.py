"""Compile actual Rocket96 C against allocation stubs; no ROM render claim."""
from pathlib import Path
import argparse,shutil,subprocess,tempfile,json
STUB=r'''
#ifndef QA_ROCKET_STUB_H
#define QA_ROCKET_STUB_H
#include <stddef.h>
#include <string.h>
#include <assert.h>
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef u8 bool8;
#define FALSE 0
#define TRUE 1
#define MAX_SPRITES 64
#define TRAINER_PIC_JESSIE_JAMES 148
#define ST_OAM_AFFINE_OFF 0
#define ST_OAM_OBJ_NORMAL 0
#define ST_OAM_4BPP 0
#define SUBSPRITES_OFF 0
#define SUBSPRITES_ON 1
#define SUBSPRITES_IGNORE_PRIORITY 2
#define SPRITE_SHAPE(d) SPRITE_SHAPE_##d
#define SPRITE_SIZE(d) SPRITE_SIZE_##d
#define SPRITE_SHAPE_64x64 0
#define SPRITE_SHAPE_32x64 2
#define SPRITE_SHAPE_64x32 1
#define SPRITE_SHAPE_32x32 0
#define SPRITE_SIZE_64x64 3
#define SPRITE_SIZE_32x64 3
#define SPRITE_SIZE_64x32 3
#define SPRITE_SIZE_32x32 2
#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))
#define STATIC_ASSERT(e,n) typedef char n[(e)?1:-1]
#define INCBIN_U32(p) { [1151] = 0 }
#define INCBIN_U16(p) { [15] = 0 }
struct Sprite;
typedef void (*SpriteCallback)(struct Sprite *);
union AnimCmd {int x;};
union AffineAnimCmd {int x;};
struct OamData {u16 affineMode,objMode,bpp,shape,size,priority;};
struct SpriteSheet {const void *data;u16 size,tag;};
struct SpritePalette {const void *data;u16 tag;};
struct Subsprite {signed char x,y;u16 shape,size,tileOffset,priority;};
struct SubspriteTable {u8 subspriteCount;const struct Subsprite *subsprites;};
struct SpriteTemplate {u16 tileTag,paletteTag;const struct OamData *oam;
 const union AnimCmd *const *anims;const void *images;
 const union AffineAnimCmd *const *affineAnims;SpriteCallback callback;};
struct Sprite {const struct SpriteTemplate *template;const struct SubspriteTable *subspriteTables;
 SpriteCallback callback;s16 x,y,x2,data[8];u8 inUse,invisible,subspriteMode,subspriteTableNum;};
extern struct Sprite gSprites[MAX_SPRITES];
extern u8 gOamLimit;
extern const union AnimCmd *const gDummySpriteAnimTable[];
extern const union AffineAnimCmd *const gDummySpriteAffineAnimTable[];
void SpriteCB_TrainerSlideIn(struct Sprite *);
u16 GetSpriteTileStartByTag(u16);
u8 IndexOfSpritePaletteTag(u16);
u16 LoadSpriteSheet(const struct SpriteSheet *);
u8 LoadSpritePalette(const struct SpritePalette *);
void FreeSpriteTilesByTag(u16);
void FreeSpritePaletteByTag(u16);
u8 CreateSprite(const struct SpriteTemplate *,s16,s16,u8);
void DestroySprite(struct Sprite *);
void SetSubspriteTables(struct Sprite *,const struct SubspriteTable *);
#endif
'''
HOST=r'''
#include "qa_stub.h"
#include "rocket_trainer_portrait.h"
struct Sprite gSprites[MAX_SPRITES];
u8 gOamLimit=64;
const union AnimCmd *const gDummySpriteAnimTable[]={NULL};
const union AffineAnimCmd *const gDummySpriteAffineAnimTable[]={NULL};
static u16 tile;
static u8 palette;
static int failTiles,failPalette,failCreate,tileFrees,paletteFrees,allocations;
void SpriteCB_TrainerSlideIn(struct Sprite *s) {(void)s;}
u16 GetSpriteTileStartByTag(u16 t){assert(t==0xD7A0);return tile;}
u8 IndexOfSpritePaletteTag(u16 t){assert(t==0xD7A0);return palette;}
u16 LoadSpriteSheet(const struct SpriteSheet *s){
 assert(s->size==0x1200);allocations++;if(!failTiles)tile=0;return 0;
}
u8 LoadSpritePalette(const struct SpritePalette *p){
 assert(p->tag==0xD7A0);if(!failPalette)palette=4;return palette;
}
void FreeSpriteTilesByTag(u16 t){assert(t==0xD7A0 && tile!=0xFFFF);tile=0xFFFF;tileFrees++;}
void FreeSpritePaletteByTag(u16 t){assert(t==0xD7A0 && palette!=0xFF);palette=0xFF;paletteFrees++;}
u8 CreateSprite(const struct SpriteTemplate *t,s16 x,s16 y,u8 p){
 (void)p;if(failCreate)return MAX_SPRITES;
 gSprites[3].template=t;gSprites[3].x=x;gSprites[3].y=y;gSprites[3].inUse=1;
 gSprites[3].callback=t->callback;return 3;
}
void DestroySprite(struct Sprite *s){assert(s->inUse);memset(s,0,sizeof(*s));}
void SetSubspriteTables(struct Sprite *s,const struct SubspriteTable *t){
 s->subspriteTables=t;s->subspriteMode=SUBSPRITES_ON;
}
static void reset(void){
 memset(gSprites,0,sizeof(gSprites));tile=0xFFFF;palette=0xFF;
 failTiles=failPalette=failCreate=tileFrees=paletteFrees=allocations=0;gOamLimit=64;
}
static bool8 create(u8 *id){return TryCreateRocketTrainerPortrait(148,176,-240,2,30,id);}
int main(void){
 u8 id=99;int i;
 reset();
 assert(gRocketTrainerHiresEnabled==ROCKET_TRAINER_HIRES_ENABLED);
#if ROCKET_TRAINER_HIRES_ENABLED
 assert(!TryCreateRocketTrainerPortrait(128,176,-240,2,30,&id) && allocations==0);
 assert(!create(NULL) && allocations==0);
 gOamLimit=3;assert(!create(&id) && allocations==0);gOamLimit=64;
 {
  static const struct Subsprite dummy[]={{0,0,0,0,0,0}};
  static const struct SubspriteTable missing[]={{60,NULL}};
  static const struct SubspriteTable full[]={{61,dummy}};
  gSprites[0].inUse=1;gSprites[0].subspriteMode=SUBSPRITES_ON;
  gSprites[0].subspriteTables=missing;gOamLimit=5;
  assert(create(&id));assert(TryDestroyRocketTrainerPortrait(&gSprites[id]));reset();
  gSprites[0].inUse=1;gSprites[0].subspriteMode=SUBSPRITES_ON;
  gSprites[0].subspriteTables=full;
  assert(!create(&id) && allocations==0);
  gSprites[0].invisible=1;assert(create(&id));
  assert(TryDestroyRocketTrainerPortrait(&gSprites[id]));reset();id=99;
 }
 tile=0;assert(!create(&id) && tileFrees==0);tile=0xFFFF;
 palette=2;assert(!create(&id) && paletteFrees==0);palette=0xFF;
 failTiles=1;assert(!create(&id) && id==99 && tileFrees==0);reset();
 failPalette=1;assert(!create(&id) && tileFrees==1 && paletteFrees==0);reset();
 failCreate=1;assert(!create(&id) && tileFrees==1 && paletteFrees==1);reset();
 for(i=0;i<100;i++){
  assert(create(&id) && id==3 && tile==0 && palette==4);
  assert(gSprites[id].x==168 && gSprites[id].y==56 && gSprites[id].x2==-240);
  assert(gSprites[id].data[0]==2 && gSprites[id].callback==SpriteCB_TrainerSlideIn);
  assert(gSprites[id].subspriteMode==SUBSPRITES_IGNORE_PRIORITY);
  assert(gSprites[id].subspriteTables[0].subspriteCount==4);
  assert(gSprites[id].subspriteTables[0].subsprites[3].tileOffset==128);
  assert(GetTrainerPortraitExitX(&gSprites[id])==296);
  assert(TryDestroyRocketTrainerPortrait(&gSprites[id]));
  assert(!TryDestroyRocketTrainerPortrait(&gSprites[id]));
  assert(tile==0xFFFF && palette==0xFF && !gSprites[id].inUse);
 }
 assert(tileFrees==100 && paletteFrees==100);reset();
 assert(TryCreateRocketTrainerPortrait(148,200,96,-2,30,&id));
 assert(gSprites[id].x==192 && gSprites[id].x2==96 && gSprites[id].data[0]==-2);
 assert(TryDestroyRocketTrainerPortrait(&gSprites[id]));
#else
 (void)i;
 assert(!create(&id) && id==99 && allocations==0);
 assert(!TryDestroyRocketTrainerPortrait(&gSprites[0]));
#endif
 assert(GetTrainerPortraitExitX(&gSprites[0])==280);
 return 0;
}
'''
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path.cwd());ap.add_argument('--cc')
args=ap.parse_args();root=args.repo.resolve()
cc=args.cc or shutil.which('cc') or shutil.which('gcc') or shutil.which('clang')
if not cc:raise SystemExit('A host C compiler is required; no installation attempted.')
module=root/'src/rocket_trainer_portrait.c'
header=root/'include/rocket_trainer_portrait.h'
if not module.is_file() or not header.is_file():raise SystemExit('Portrait C and header must exist.')
with tempfile.TemporaryDirectory(prefix='rocket96-host-') as d:
    tmp=Path(d);(tmp/'constants').mkdir()
    (tmp/'qa_stub.h').write_text(STUB,encoding='utf-8')
    for p in ['global.h','gflib.h','battle_gfx_sfx_util.h','constants/trainers.h']:
        (tmp/p).write_text('#include "qa_stub.h"\n',encoding='utf-8')
    (tmp/'rocket_trainer_portrait.h').write_text(header.read_text(),encoding='utf-8')
    (tmp/'host.c').write_text(HOST,encoding='utf-8')
    for enabled in [0,1]:
        binary=tmp/f'test-{enabled}'
        subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror',f'-DROCKET_TRAINER_HIRES_ENABLED={enabled}',
                        '-I',str(tmp),str(module),str(tmp/'host.c'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
print(json.dumps({'status':'PASS','disabled_fallback':True,'enabled_allocation_failure_cleanup':True,
 'enabled_repeated_create_destroy_cycles':100,'real_ROM_render_or_art_validated':False}))
