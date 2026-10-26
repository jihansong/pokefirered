#include <cstdio>
#include <cstdlib>
#include <cstdarg>
#include <cstring>
#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <chrono>
#include <cerrno>
#include <stdexcept>
#include <cctype>
#include <climits>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <csignal>
#include "System.h"
#include "Util.h"
#include "gba/GBA.h"
#include "gba/Globals.h"
#include "gba/Sound.h"
#include "gba/Flash.h"
#include "gba/RTC.h"
#include "common/SoundDriver.h"

// Headless host only. The pinned emulator CPU, BIOS, DMA and renderer are unchanged.
static uint64_t hostFrames=0,drawCount=0,lastActual=0;
static unsigned lastRequested=0;
static bool lastComplete=true;
static uint32_t hostKeys=0;
static int videoFd=-1;
static bool videoOn=false,videoError=false;
static uint64_t videoFrames=0;
static void emitVideoFrame();
int emulating=1;
bool cpuIsMultiBoot=false;
int skipBios=0,useBios=0,skipSaveGameBattery=0,skipSaveGameCheats=0;
bool speedHack=false,speedup=false;
const char*loadDotCodeFile=NULL;
const char*saveDotCodeFile=NULL;
int cheatsEnabled=0,cpuDisableSfx=0,layerEnable=0xff00,layerSettings=0xff00;
int rtcEnabled=1,saveType=3;
uint16_t systemColorMap16[0x10000];
uint32_t systemColorMap32[0x10000];
uint16_t systemGbPalette[24];
int systemRedShift=0,systemGreenShift=8,systemBlueShift=16;
int systemColorDepth=32,systemVerbose=0,systemFrameSkip=0;
int systemSaveUpdateCounter=0,systemSpeed=100;
void log(const char *fmt, ...){ va_list a;va_start(a,fmt);vfprintf(stderr,fmt,a);va_end(a); }
void systemMessage(int n,const char*fmt,...){fprintf(stderr,"CORE_MESSAGE %d ",n);va_list a;va_start(a,fmt);vfprintf(stderr,fmt,a);va_end(a);fputc('\n',stderr);}
void systemScreenMessage(const char*s){fprintf(stderr,"CORE_SCREEN %s\n",s);}
void systemFrame(){hostFrames++;}
bool systemPauseOnFrame(){return false;}
void systemDrawScreen(){drawCount++;if(videoOn)emitVideoFrame();}
bool systemReadJoypads(){return true;}
uint32_t systemReadJoypad(int){return hostKeys;}
uint32_t systemGetClock(){return (uint32_t)(hostFrames*1000/60);}
void system10Frames(int){}
void systemShowSpeed(int){}
void systemSetTitle(const char*){}
void systemScreenCapture(int){}
void systemUpdateMotionSensor(){}
int systemGetSensorX(){return 0;}
int systemGetSensorY(){return 0;}
int systemGetSensorZ(){return 0;}
uint8_t systemGetSensorDarkness(){return 0xe8;}
void systemCartridgeRumble(bool){}
void systemPossibleCartridgeRumble(bool){}
void updateRumbleFrame(){}
bool systemCanChangeSoundQuality(){return true;}
void systemOnWriteDataToSoundBuffer(const uint16_t*,int){}
void systemOnSoundShutdown(){}
void systemGbPrint(uint8_t*,int,int,int,int,int){}
void systemGbBorderOn(){}
void Sm60FPS_Init(){}
bool Sm60FPS_CanSkipFrame(){return false;}
void Sm60FPS_Sleep(){}
void DbgMsg(const char*,...){}
static void noOutput(const char*,uint32_t){}
static void noSignal(int,int){}
void (*dbgOutput)(const char*,uint32_t)=noOutput;
void (*dbgSignal)(int,int)=noSignal;
bool enableRegBreak=false;
uint8_t lowRegBreakCounter[4]={},medRegBreakCounter[4]={},highRegBreakCounter[4]={},statusRegBreakCounter[4]={};
void breakReg_check(int){}
void clearBreakRegList(){}
bool dexp_eval(char*,uint32_t*){return false;}
bool debuggerBreakOnExecution(uint32_t,uint8_t){return false;}
bool debuggerBreakOnRead(uint32_t,int){return false;}
bool debuggerBreakOnWrite(uint32_t,uint32_t,int){return false;}
void debuggerBreakOnWrite(uint32_t,uint32_t,uint32_t,int,int){}
class NullSound:public SoundDriver{public:bool init(long){return true;}void pause(){}void reset(){}void resume(){}void write(uint16_t*,int){}};
SoundDriver*systemSoundInit(){return new NullSound();}

// Plain-file I/O adapter; no save-state restore or game memory write interface.
uint8_t*utilLoad(const char*p,bool(*)(const char*),uint8_t*b,int&n){FILE*f=fopen(p,"rb");if(!f)return NULL;fseek(f,0,SEEK_END);int s=ftell(f);rewind(f);if(s>n&&b){fclose(f);return NULL;}if(!b)b=(uint8_t*)malloc(s);n=(int)fread(b,1,s,f);fclose(f);return b;}
bool utilIsGBAImage(const char*){return true;}
bool utilWritePNGFile(const char*,int,int,uint8_t*){return false;}
bool utilWriteBMPFile(const char*,int,int,uint8_t*){return false;}
void utilWriteData(gzFile f,variable_desc*v){for(;v->address;v++)gzwrite(f,v->address,v->size);}
void utilReadData(gzFile f,variable_desc*v){for(;v->address;v++)gzread(f,v->address,v->size);}
void utilReadDataSkip(gzFile f,variable_desc*v){for(;v->address;v++)gzseek(f,v->size,SEEK_CUR);}
int utilReadInt(gzFile f){int x=0;gzread(f,&x,4);return x;}
void utilWriteInt(gzFile f,int x){gzwrite(f,&x,4);}
int utilGzWrite(gzFile f,const voidp b,unsigned n){return gzwrite(f,b,n);}
int utilGzRead(gzFile f,voidp b,unsigned n){return gzread(f,b,n);}
z_off_t utilGzSeek(gzFile f,z_off_t o,int w){return gzseek(f,o,w);}
int utilGzClose(gzFile f){return gzclose(f);}
gzFile utilGzOpen(const char*p,const char*m){return gzopen(p,m);}
gzFile utilMemGzOpen(char*,int,const char*){fprintf(stderr,"UNSUPPORTED_HOST_SAVE_STATE\n");abort();}
long utilGzMemTell(gzFile){abort();}
void utilPutDword(uint8_t*p,uint32_t v){memcpy(p,&v,4);}


// Outputs are created only under a private startup directory. No game-state
// address appears in this protocol: the controller binds all meaning to a fresh SYM.
static int artifactFd=-1;
static std::string batteryName;
static bool exported=false;
static void configureVideo(const std::string &value) {
    if(value.empty())return;
    size_t end=0;long parsed=std::stol(value,&end);
    if(end!=value.size()||parsed<=2||parsed>INT_MAX)throw std::runtime_error("dedicated inherited video fd required");
    int fd=int(parsed),flags=fcntl(fd,F_GETFL);struct stat info;
    if(flags<0||(flags&O_ACCMODE)!=O_WRONLY||fstat(fd,&info)||!S_ISFIFO(info.st_mode))
        throw std::runtime_error("video fd must be an inherited writable pipe or FIFO");
    videoFd=fd;std::signal(SIGPIPE,SIG_IGN);
}
static void emitVideoFrame() {
    static uint8_t rgb[240*160*3];size_t offset=0;
    for(int y=0;y<160;y++)for(int x=0;x<240;x++) {
        uint32_t color=((uint32_t*)pix)[241*(y+1)+x];
        rgb[offset++]=color&255;rgb[offset++]=(color>>8)&255;rgb[offset++]=(color>>16)&255;
    }
    size_t written=0;
    while(written<sizeof(rgb)) {
        ssize_t count=write(videoFd,rgb+written,sizeof(rgb)-written);
        if(count<0&&errno==EINTR)continue;
        if(count<=0){videoError=true;videoOn=false;fprintf(stderr,"HOST_VIDEO_PIPE_ERROR\n");return;}
        written+=size_t(count);
    }
    videoFrames++;
}
static bool cleanComponent(const std::string &s) {
    if(s.empty()||s=="."||s==".."||s.size()>120)return false;
    for(unsigned char c:s)if(!std::isalnum(c)&&c!='_'&&c!='-'&&c!='.')return false;
    return true;
}
static void requireNoSymlink(const std::string &path) {
    if(path.empty()||path[0]!='/')throw std::runtime_error("absolute input path required");
    std::string prefix;std::istringstream parts(path);std::string part;
    while(std::getline(parts,part,'/')) {
        if(part.empty())continue;
        if(part=="."||part=="..")throw std::runtime_error("dot path component rejected");
        prefix+="/"+part;struct stat st;
        if(lstat(prefix.c_str(),&st)||S_ISLNK(st.st_mode))throw std::runtime_error("missing or symlink input rejected");
    }
}
static int regularInput(const std::string &path,off_t minimum,off_t maximum) {
    requireNoSymlink(path);
    int fd=open(path.c_str(),O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
    struct stat st;
    if(fd<0||fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_size<minimum||st.st_size>maximum) {
        if(fd>=0)close(fd);throw std::runtime_error("invalid regular input");
    }
    return fd;
}
static std::string descriptorPath(int fd) {
    return "/proc/self/fd/"+std::to_string(fd);
}
static void configureArtifacts(const std::string &directory,const std::string &name) {
    requireNoSymlink(directory);
    artifactFd=open(directory.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    struct stat st;
    if(artifactFd<0||fstat(artifactFd,&st)||st.st_uid!=geteuid()||(st.st_mode&077)!=0)
        throw std::runtime_error("artifact directory must be caller-owned mode 0700");
    if(!cleanComponent(name)||name.size()<5||name.substr(name.size()-4)!=".sav")
        throw std::runtime_error("new battery basename ending .sav required");
    struct stat existing;
    if(fstatat(artifactFd,name.c_str(),&existing,AT_SYMLINK_NOFOLLOW)==0||errno!=ENOENT)
        throw std::runtime_error("battery output already exists");
    batteryName=name;
}
static int newArtifact(const std::string &name) {
    if(!cleanComponent(name))throw std::runtime_error("artifact basename rejected");
    int fd=openat(artifactFd,name.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    if(fd<0)throw std::runtime_error("artifact exists or cannot be exclusively created");
    return fd;
}
static bool readable(uint32_t a,uint32_t n) {
    if(n>4096||uint64_t(a)+n>0x100000000ULL)return false;
    const uint32_t starts[]={0x02000000,0x03000000,0x04000000,0x05000000,0x06000000,0x07000000,0x08000000};
    const uint32_t sizes []={0x40000,0x8000,0x400,0x400,0x20000,0x400,0x2000000};
    for(unsigned i=0;i<7;i++)if(a>=starts[i]&&uint64_t(a)+n<=uint64_t(starts[i])+sizes[i])return true;
    return false;
}
static uint8_t rd8(uint32_t a) {
    switch(a>>24) {
    case 2:return workRAM[a&0x3ffff];case 3:return internalRAM[a&0x7fff];
    case 4:return ioMem[a&0x3ff];case 5:return paletteRAM[a&0x3ff];
    case 6:return vram[a&0x1ffff];case 7:return oam[a&0x3ff];
    case 8:case 9:return rom[a&0x1ffffff];default:return 0;
    }
}
static uint32_t rd32(uint32_t a) {
    uint32_t value=0;for(unsigned i=0;i<4;i++)value|=uint32_t(rd8(a+i))<<(8*i);return value;
}
static void status() {
    printf("{\"frame\":%llu,\"draws\":%llu,\"complete\":%s,\"requested\":%u,\"actual\":%llu,"
           "\"pc\":%u,\"lr\":%u,\"arm\":%s,\"IME\":%u,\"IE\":%u,\"IF\":%u,"
           "\"dma3src\":%u,\"dma3dst\":%u,\"dma3cnt\":%u,\"keys\":%u,\"battery_exported\":%s,"
           "\"video_on\":%s,\"video_frames\":%llu,\"video_error\":%s}\n",
           (unsigned long long)hostFrames,(unsigned long long)drawCount,lastComplete?"true":"false",
           lastRequested,(unsigned long long)lastActual,reg[15].I,reg[14].I,armState?"true":"false",
           IME,IE,IF,rd32(0x040000d4),rd32(0x040000d8),rd32(0x040000dc),hostKeys,exported?"true":"false",
           videoOn?"true":"false",(unsigned long long)videoFrames,videoError?"true":"false");
    fflush(stdout);
}
static bool runFrames(unsigned n) {
    uint64_t start=drawCount,end=start+n;lastRequested=n;lastComplete=false;
    auto began=std::chrono::steady_clock::now();
    while(drawCount<end) {
        GBASystem.emuMain(GBASystem.emuCount);
        if(videoError){lastActual=drawCount-start;return false;}
        if(std::chrono::steady_clock::now()-began>std::chrono::seconds(30)) {
            fprintf(stderr,"HOST_TIMEOUT draws=%llu pc=%08x\n",(unsigned long long)drawCount,reg[15].I);
            lastActual=drawCount-start;return false;
        }
    }
    lastActual=drawCount-start;lastComplete=lastActual==n;return lastComplete;
}
static void screenshot(const std::string &name) {
    if(name.size()<5||name.substr(name.size()-4)!=".ppm")throw std::runtime_error("PPM basename required");
    int fd=newArtifact(name);FILE *file=fdopen(fd,"wb");
    if(!file){close(fd);throw std::runtime_error("PPM stream failed");}
    bool okay=fprintf(file,"P6\n240 160\n255\n")>0;
    for(int y=0;y<160;y++)for(int x=0;x<240;x++) {
        uint32_t c=((uint32_t*)pix)[241*(y+1)+x];
        okay=okay&&fputc(c&255,file)!=EOF&&fputc((c>>8)&255,file)!=EOF&&fputc((c>>16)&255,file)!=EOF;
    }
    okay=fclose(file)==0&&okay;
    if(!okay)throw std::runtime_error("PPM write failed");
    printf("{\"screenshot\":true,\"file\":\"%s\"}\n",name.c_str());fflush(stdout);
}
static void battery(const std::string &attestation) {
    if(attestation!="normal-save-complete"||exported||hostKeys||drawCount==0)
        throw std::runtime_error("battery export requires completed normal SAVE attestation");
    // Reserve a new inode atomically. The official writer reopens our descriptor,
    // never a caller-controlled path or an existing seed. The internal Linux fd
    // path cannot redirect the operation outside this newly reserved inode.
    int fd=newArtifact(batteryName);struct stat before,after;
    if(fstat(fd,&before)){close(fd);throw std::runtime_error("battery reservation failed");}
    bool okay=CPUWriteBatteryFile(descriptorPath(fd).c_str());
    okay=okay&&fsync(fd)==0&&fstat(fd,&after)==0&&before.st_dev==after.st_dev&&before.st_ino==after.st_ino&&after.st_size==0x20000;
    close(fd);
    if(!okay)throw std::runtime_error("official battery writer failed");
    exported=true;
    printf("{\"battery\":true,\"file\":\"%s\",\"bytes\":131072}\n",batteryName.c_str());fflush(stdout);
}
int main(int argc,char **argv) {
    int result=0;bool started=false;
    try {
        std::string romPath,seedPath,directory,output,videoDescriptor;bool blank=false;
        for(int i=1;i<argc;i++) {
            std::string arg=argv[i];
            if(arg=="--blank-flash"){if(blank)throw std::runtime_error("duplicate blank option");blank=true;continue;}
            if(i+1>=argc)throw std::runtime_error("option value missing");
            std::string value=argv[++i],*target=NULL;
            if(arg=="--rom")target=&romPath;else if(arg=="--seed")target=&seedPath;
            else if(arg=="--artifact-dir")target=&directory;else if(arg=="--output")target=&output;
            else if(arg=="--video-fd")target=&videoDescriptor;
            else throw std::runtime_error("unknown option");
            if(!target->empty())throw std::runtime_error("duplicate option");*target=value;
        }
        if(romPath.empty()||directory.empty()||output.empty()||blank==!seedPath.empty())
            throw std::runtime_error("use --rom --artifact-dir --output and exactly one of --seed or --blank-flash");
        configureArtifacts(directory,output);
        configureVideo(videoDescriptor);
        int romFd=regularInput(romPath,1024,0x2000000);struct stat romStat;fstat(romFd,&romStat);
        std::vector<char> bytes(romStat.st_size);size_t used=0;
        while(used<bytes.size()){ssize_t got=read(romFd,bytes.data()+used,bytes.size()-used);if(got<=0){close(romFd);throw std::runtime_error("ROM read failed");}used+=got;}
        close(romFd);
        if(CPULoadRomData(bytes.data(),int(bytes.size()))!=int(bytes.size()))throw std::runtime_error("core ROM loader failed");
        started=true;
        // Match the official pinned file loader capacity. This only corrects
        // host video storage; CPU/BIOS/DMA/GPU sources and guest RAM are unchanged.
        uint8_t *padded=(uint8_t*)realloc(pix,4*241*162);
        if(!padded)throw std::runtime_error("video storage allocation failed");
        pix=padded;memset(pix,0,4*241*162);
        for(unsigned c=0;c<65536;c++){unsigned r=(c&31)<<3,g=((c>>5)&31)<<3,b=((c>>10)&31)<<3;systemColorMap32[c]=r|(g<<8)|(b<<16);}
        rtcEnable(true);soundInit();soundSetSampleRate(32768);soundReset();CPUInit("",false);SetSaveType(3);flashSetSize(0x20000);CPUReset();
        if(!blank) {
            int seedFd=regularInput(seedPath,0x20000,0x20000);
            bool okay=CPUReadBatteryFile(descriptorPath(seedFd).c_str());close(seedFd);
            if(!okay)throw std::runtime_error("core read-only seed load failed");
        }
        status();std::string line;
        while(std::getline(std::cin,line)) {
            std::istringstream input(line);std::string op;input>>op;
            if(op=="quit"){hostKeys=0;status();break;}
            if(op=="status"){status();continue;}
            if(op=="step") {
                unsigned keys=0,frames=0;std::string extra;
                if(!(input>>keys>>frames)||input>>extra||keys>1023||frames>12000)throw std::runtime_error("invalid step");
                hostKeys=keys;runFrames(frames);hostKeys=0;status();
            } else if(op=="read") {
                uint32_t address=0,count=0;std::string extra;
                if(!(input>>std::hex>>address>>count)||input>>extra||!readable(address,count))throw std::runtime_error("invalid read");
                printf("{\"address\":%u,\"hex\":\"",address);
                for(unsigned i=0;i<count;i++)printf("%02x",rd8(address+i));puts("\"}");fflush(stdout);
            } else if(op=="video") {
                std::string mode,extra;
                if(!(input>>mode)||input>>extra||(mode!="on"&&mode!="off"&&mode!="finish"))throw std::runtime_error("video expects on, off or finish");
                if(mode=="on"&&(videoFd<0||videoError))throw std::runtime_error("healthy inherited video pipe required");
                videoOn=mode=="on";
                if(mode=="finish"&&videoFd>=0){if(close(videoFd)<0&&errno!=EINTR)videoError=true;videoFd=-1;}
                status();
            } else if(op=="ppm"||op=="battery") {
                std::string name,extra;if(!(input>>name)||input>>extra)throw std::runtime_error("one argument required");
                if(op=="ppm")screenshot(name);else battery(name);
            } else throw std::runtime_error("unknown command");
        }
    } catch(const std::exception &error) {
        hostKeys=0;fprintf(stderr,"HOST_ERROR %s\n",error.what());result=2;
    }
    hostKeys=0;videoOn=false;if(started){soundShutdown();CPUCleanUp();}if(artifactFd>=0)close(artifactFd);if(videoFd>=0)close(videoFd);
    return result;
}
