// A thin, headless wrapper around libmgba for the QA scripts in tools/qa.
// Python drives it through ctypes (tools/qa/emu.py); everything here is one
// emulator instance per handle, no threads, no audio, no BIOS file needed.
//
// Build: cc -O2 -shared -fPIC -o tools/qa/libqa.so tools/qa/libqa.c -lmgba
// (tools/qa/build.sh does this and is run by .devcontainer/setup.sh).

#include <mgba/flags.h>
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba-util/vfs.h>

#include <fcntl.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

struct QA {
    struct mCore *core;
    color_t *video;
    unsigned width, height;
};

static void QuietLog(struct mLogger *logger, int category, enum mLogLevel level, const char *format, va_list args)
{
    (void)logger; (void)category; (void)level; (void)format; (void)args;
}

static struct mLogger sQuiet = { .log = QuietLog };

// rom: path to the .gba. sav: path to a 128K flash save that the game may
// write to, or NULL to start with no save. Returns NULL on failure.
struct QA *qa_open(const char *rom, const char *sav)
{
    struct QA *qa;
    struct mCore *core;

    mLogSetDefaultLogger(&sQuiet);
    core = mCoreFind(rom);
    if (!core)
        return NULL;
    if (!core->init(core))
        return NULL;
    mCoreInitConfig(core, NULL);
    qa = calloc(1, sizeof(*qa));
    qa->core = core;
    core->desiredVideoDimensions(core, &qa->width, &qa->height);
    qa->video = calloc(qa->width * qa->height, sizeof(color_t));
    core->setVideoBuffer(core, qa->video, qa->width);
    if (!mCoreLoadFile(core, rom))
        goto fail;
    if (sav) {
        struct VFile *vf = VFileOpen(sav, O_RDWR);
        if (!vf || !core->loadSave(core, vf))
            goto fail;
    }
    core->reset(core);
    return qa;

fail:
    core->deinit(core);
    free(qa->video);
    free(qa);
    return NULL;
}

void qa_close(struct QA *qa)
{
    qa->core->deinit(qa->core);
    free(qa->video);
    free(qa);
}

void qa_reset(struct QA *qa) { qa->core->reset(qa->core); }

// Keys use the GBA bit order: A B SELECT START RIGHT LEFT UP DOWN R L.
void qa_set_keys(struct QA *qa, unsigned keys) { qa->core->setKeys(qa->core, keys); }

void qa_run(struct QA *qa, int frames)
{
    while (frames-- > 0)
        qa->core->runFrame(qa->core);
}

unsigned qa_frame(struct QA *qa) { return qa->core->frameCounter(qa->core); }

void qa_read(struct QA *qa, unsigned addr, unsigned char *out, int len)
{
    for (int i = 0; i < len; i++)
        out[i] = qa->core->busRead8(qa->core, addr + i);
}

void qa_write(struct QA *qa, unsigned addr, const unsigned char *in, int len)
{
    for (int i = 0; i < len; i++)
        qa->core->busWrite8(qa->core, addr + i, in[i]);
}

// Copies the last frame as width*height RGB triplets into out.
void qa_screen(struct QA *qa, unsigned char *out)
{
    for (unsigned i = 0; i < qa->width * qa->height; i++) {
        unsigned c = qa->video[i];
        out[i * 3 + 0] = c & 0xFF;
        out[i * 3 + 1] = (c >> 8) & 0xFF;
        out[i * 3 + 2] = (c >> 16) & 0xFF;
    }
}

unsigned qa_state_size(struct QA *qa) { return qa->core->stateSize(qa->core); }
int qa_save_state(struct QA *qa, void *buf) { return qa->core->saveState(qa->core, buf); }
int qa_load_state(struct QA *qa, const void *buf) { return qa->core->loadState(qa->core, buf); }
