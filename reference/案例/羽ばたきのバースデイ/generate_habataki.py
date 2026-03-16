# -*- coding: utf-8 -*-
"""
羽ばたきのバースデイ - ASS 華麗動態歌詞特效生成器
番剧: 天使の3P! OP  |  歌手: 大野柚布子/遠藤ゆりか/古賀葵
目标: ≥5000 FX行, 匹配参考9859行品质
"""
import re, math, random

INPUT  = r"C:\Users\Heng_Xin\Documents\Lyrics\大野柚布子／遠藤ゆりか／古賀葵 - 羽ばたきのバースデイ (67973169).ass"
OUTPUT = r"C:\Users\Heng_Xin\Documents\Lyrics\羽ばたきのバースデイ_FX.ass"
RES_X, RES_Y = 1280, 720

# --- 颜色 ---
C_PRI = "&H00AF4BF0&"; C_OUT = "&H00FFFFFF&"; C_SHD = "&H96000000&"
C_PAR = "&HEBBEBE&"; C_WAVE = "&H00D8FF&"; C_HALO1 = "&H00FCFF&"; C_HALO2 = "&HC7FEFF&"
MAU = ["&H0000FF&","&H00B4FF&","&H00FFFF&","&H8EFFE6&"]
FONT_JP = "FOT-PopJoy Std B"; FONT_CN = "方正少儿_GBK"

# --- 图形 ---
S_FEA = "m 26 37 l 38 27 l 45 19 l 52 11 l 57 7 b 66 0 72 9 64 29 l 59 26 l 62 31 b 58 36 52 43 46 47 l 41 44 l 44 48 b 41 52 37 56 33 58 l 28 52 l 30 58 l 27 61 l 24 58 l 24 61 l 21 58 l 17 61 l 17 59 b 11 62 6 64 0 64 l 0 60 b 5 60 12 57 16 54 l 14 51 l 18 51 l 17 47 l 20 50 l 20 42 l 24 38 l 25 45"
S_NOTE = [
    "m 0 0 l 0 0 l 0 7 b 0 7 0 6 -1 7 b -1 7 -3 8 -2 9 b -2 9 -1 10 0 9 b 0 9 1 8 1 8 b 1 8 1 7 1 7 l 1 1 l 7 0 l 7 6 b 7 6 6 5 5 6 b 5 6 3 7 4 8 b 4 8 5 9 6 8 b 6 8 8 8 8 7 b 8 6 8 6 8 6 l 8 -1",
    "m 0 0 l 0 0 l 0 9 b 0 9 -1 8 -3 9 b -3 9 -5 10 -4 12 b -4 12 -3 13 -1 12 b -1 12 1 11 1 10 b 1 10 1 9 1 9 l 1 -1",
    "m 0 0 l 0 0 l 0 0 l 0 9 b 0 9 -1 8 -3 9 b -3 9 -5 10 -4 12 b -4 12 -3 13 -1 12 b -1 12 1 11 1 10 b 1 10 1 9 1 9 l 1 1 b 2 2 3 2 2 6 b 5 2 2 1 1 0",
]
S_HB_EXT = "m 0 0 m -1 31 l 0 31 l 3 30 l 5 32 l 6 31 l 8 24 l 10 45 l 11 33 l 14 32 l 18 32 l 22 30 l 25 32 l 33 31 l 43 30 l 46 26 l 49 30 l 51 31 l 53 3 l 55 33 l 58 33 l 63 36 l 68 28 l 74 29 l 83 30 l 88 29 l 90 28 l 93 30 l 96 30 l 98 0 l 101 32 l 105 29 l 122 29 l 122 30 l 105 30 l 101 33 l 98 8 l 97 31 l 93 31 l 90 29 l 83 31 l 73 30 l 68 29 l 63 37 l 58 34 l 54 34 l 53 13 l 52 32 l 49 31 l 46 27 l 43 31 l 33 32 l 25 33 l 22 31 l 18 33 l 14 33 l 11 34 l 10 48 l 8 28 l 7 32 l 5 33 l 3 31 l 0 32 l -4 30 l -33 30 l -33 29 l -4 29 m 122 29 l 126 20 l 133 44 l 138 23 l 144 36 l 149 31 l 151 27 l 153 29 l 157 31 l 161 29 l 175 8 l 181 31 l 187 47 l 195 40 l 198 32 l 199 23 l 209 26 l 221 17 l 222 23 l 236 22 l 244 27 l 247 24 l 250 24 l 261 1 l 263 41 l 270 27 l 271 34 l 275 1 l 280 29 l 286 12 l 289 31 l 294 12 l 307 29 l 329 29 l 339 7 l 339 39 l 341 29 l 377 29 l 377 30 l 342 30 l 339 43 l 338 11 l 329 30 l 306 30 l 294 14 l 289 34 l 286 15 l 280 32 l 275 7 l 271 36 l 270 29 l 263 43 l 260 4 l 251 25 l 247 25 l 244 28 l 236 23 l 221 24 l 220 19 l 209 27 l 200 24 l 199 32 l 196 41 l 187 49 l 180 31 l 175 10 l 162 30 l 157 32 l 153 30 l 151 29 l 150 32 l 144 37 l 138 25 l 133 46 l 126 22 l 123 30 l 122 30"
S_FLOWER = [
    "m 21 21 b 6 -7 46 -7 29 21 b 49 -2 63 34 30 28 b 63 44 31 65 25 32 b 26 65 -12 45 21 29 b -13 38 0 -5 21 21 m 25 22 b 21 22 21 28 25 28 b 29 28 29 22 25 22",
    "m 13 12 b 4 -4 28 -4 18 12 b 30 -1 38 20 18 17 b 38 26 19 39 15 19 b 16 39 -7 27 13 17 b -8 23 0 -3 13 12 m 15 13 b 13 13 13 17 15 17 b 18 17 18 13 15 13",
    "m 8 7 b 2 -2 17 -2 11 7 b 18 -1 23 11 11 9 b 23 14 11 21 9 10 b 9 21 -4 15 8 9 b -5 13 0 -2 8 7 m 9 7 b 8 7 8 9 9 9 b 11 9 11 7 9 7",
]
S_LEAF = "m 20 29 b 24 29 26 30 29 32 b 31 30 33 28 36 28 b 32 27 30 25 30 23 b 31 21 35 19 37 19 b 35 18 34 18 33 17 b 34 14 35 12 38 10 b 36 11 34 11 32 11 b 31 10 31 8 32 7 b 30 9 27 12 25 13 b 25 10 26 7 27 4 b 25 5 24 5 22 5 b 21 2 20 -1 19 -4 b 18 -1 17 2 16 5 b 14 5 13 4 11 3 b 12 6 13 10 13 13 b 10 12 8 9 6 7 b 7 8 7 10 6 11 b 4 11 2 11 0 10 b 2 12 4 15 4 17 b 3 18 2 18 1 18 b 4 19 6 22 8 24 b 7 27 5 29 3 31 b 8 29 13 29 18 29 b 18 32 18 35 17 38 b 15 39 17 42 19 38 b 20 35 20 32 20 29"
S_CIRCLE = "m 5 0 b 2 0 0 2 0 5 b 0 8 2 10 5 10 b 8 10 10 8 10 5 b 10 2 8 0 5 0"
S_WING = "m 17 33 b 12 41 6 26 15 24 b 29 25 26 50 15 49 b 9 51 -4 41 2 22 b 11 3 28 -2 45 0 b 58 3 40 24 31 25 b 52 32 39 42 30 36 b 36 47 31 47 25 40 l 25 40 b 26 32 24 22 14 23 b 3 26 11 43 18 35 b 18 33 17 33 17 33"
S_HALO = "m 0 25 b 1 10 50 11 50 25 b 51 40 -1 40 0 25 m 2 23 b -5 38 49 39 49 25 b 50 14 6 11 2 23"
GRASS = [
    "m 0 0 b 8 -10 15 -4 21 -3 b 34 -2 32 -9 30 -11 b 25 -14 20 -6 27 -7",
    "m 0 0 b 8 -10 15 -4 21 -2 b 24 0 28 5 31 5 b 36 7 40 6 43 5 b 49 -3 43 -2 41 -1 b 39 0 40 4 43 2",
    "m 0 0 b 8 -10 15 -4 21 -2 b 24 0 28 5 31 5 b 36 7 40 6 43 5 b 47 3 50 1 54 0 b 58 0 57 3 55 3",
    "m 0 0 b 8 -10 15 -4 21 -2 b 24 0 28 4 30 6 b 31 8 33 11 34 14 b 34 18 38 19 40 18 b 44 18 42 11 40 15",
]
FLOURISH = [
    "m 0 0 m 34 -36 b 43 -52 35 -67 29 -69 b 22 -71 16 -69 13 -64 b 8 -57 13 -51 16 -49 b 21 -45 26 -50 25 -55 b 24 -58 20 -57 21 -56",
    "m 0 0 m 34 -36 b 40 -47 38 -56 37 -60 b 32 -72 24 -70 18 -69 b 14 -67 12 -63 10 -59 b 4 -55 2 -57 0 -60 b 0 -62 1 -64 2 -64 b 5 -65 5 -62 5 -61",
    "m 0 0 m 39 -34 b 51 -45 63 -39 68 -36 b 74 -32 81 -21 86 -22 b 100 -21 104 -35 97 -40 b 90 -45 84 -40 86 -35 b 90 -29 94 -34 92 -36",
    "m 0 0 m 39 -34 b 51 -45 63 -39 68 -36 b 78 -30 79 -25 86 -17 b 99 -8 104 -15 109 -16 b 123 -18 125 -14 127 -11",
    "m 0 0 m 39 -34 b 51 -45 63 -39 68 -36 b 78 -30 79 -25 86 -17 b 90 -13 90 -4 86 -1 b 79 3 76 -3 77 -6 b 78 -11 84 -9 82 -6",
    "m 0 0 m 39 -34 b 51 -45 63 -39 68 -36 b 79 -29 76 -21 74 -17 b 72 -13 67 -10 64 -8 b 57 -3 63 2 66 -1 b 67 -1 69 -5 65 -4",
]

# --- 罗马音→假名 ---
R2H = {
    'a':'あ','i':'い','u':'う','e':'え','o':'お',
    'ka':'か','ki':'き','ku':'く','ke':'け','ko':'こ',
    'sa':'さ','shi':'し','si':'し','su':'す','se':'せ','so':'そ',
    'ta':'た','chi':'ち','ti':'ち','tsu':'つ','tu':'つ','te':'て','to':'と',
    'na':'な','ni':'に','nu':'ぬ','ne':'ね','no':'の',
    'ha':'は','hi':'ひ','fu':'ふ','hu':'ふ','he':'へ','ho':'ほ',
    'ma':'ま','mi':'み','mu':'む','me':'め','mo':'も',
    'ya':'や','yu':'ゆ','yo':'よ',
    'ra':'ら','ri':'り','ru':'る','re':'れ','ro':'ろ',
    'wa':'わ','wo':'を','n':'ん',
    'ga':'が','gi':'ぎ','gu':'ぐ','ge':'げ','go':'ご',
    'za':'ざ','ji':'じ','zi':'じ','zu':'ず','ze':'ぜ','zo':'ぞ',
    'da':'だ','de':'で','do':'ど',
    'ba':'ば','bi':'び','bu':'ぶ','be':'べ','bo':'ぼ',
    'pa':'ぱ','pi':'ぴ','pu':'ぷ','pe':'ぺ','po':'ぽ',
    'kya':'きゃ','kyu':'きゅ','kyo':'きょ',
    'sha':'しゃ','shu':'しゅ','sho':'しょ',
    'cha':'ちゃ','chu':'ちゅ','cho':'ちょ',
    'nya':'にゃ','nyu':'にゅ','nyo':'にょ',
    'hya':'ひゃ','hyu':'ひゅ','hyo':'ひょ',
    'mya':'みゃ','myu':'みゅ','myo':'みょ',
    'rya':'りゃ','ryu':'りゅ','ryo':'りょ',
    'gya':'ぎゃ','gyu':'ぎゅ','gyo':'ぎょ',
    'ja':'じゃ','ju':'じゅ','jo':'じょ',
    'bya':'びゃ','byu':'びゅ','byo':'びょ',
    'pya':'ぴゃ','pyu':'ぴゅ','pyo':'ぴょ',
    'tto':'っと','tte':'って','tta':'った','kka':'っか','sshi':'っし',
    'ppa':'っぱ','ppi':'っぴ','ppu':'っぷ','dyi':'ぢ','-':'ー',
}
def r2h(roma):
    roma=roma.strip().lower()
    if not roma: return ""
    out=""
    for tok in roma.split():
        if tok in R2H: out+=R2H[tok]; continue
        i=0
        while i<len(tok):
            ok=False
            for L in range(min(4,len(tok)-i),0,-1):
                s=tok[i:i+L]
                if s in R2H: out+=R2H[s]; i+=L; ok=True; break
            if not ok:
                if i+1<len(tok) and tok[i]==tok[i+1] and tok[i] not in 'aeioun':
                    out+='っ'; i+=1
                else: out+=tok[i]; i+=1
    return out

# --- 解析 ---
def pt(ts):
    m=re.match(r'(\d+):(\d+):(\d+)\.(\d+)',ts.strip())
    if not m: return 0
    return int(m[1])*3600000+int(m[2])*60000+int(m[3])*1000+int(m[4])*10
def ft(ms):
    if ms<0: ms=0
    h=ms//3600000; ms%=3600000; m=ms//60000; ms%=60000; s=ms//1000; cs=(ms%1000)//10
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
def parse_kf(text):
    sy=[]; p=re.split(r'\{\\kf(\d+)\}',text); i=1
    while i<len(p): sy.append((int(p[i]),p[i+1] if i+1<len(p) else "")); i+=2
    return sy
def parse_dl(l):
    m=re.match(r'(Dialogue|Comment):\s*(\d+),([^,]+),([^,]+),([^,]*),([^,]*),(\d+),(\d+),(\d+),([^,]*),(.*)',l)
    if not m: return None
    return {"style":m[5].strip(),"text":m[11],"start_ms":pt(m[3]),"end_ms":pt(m[4])}
def parse_ass(fp):
    with open(fp,"r",encoding="utf-8-sig") as f: lines=f.read().split('\n')
    O,T,R=[],[],[]
    for l in lines:
        l=l.rstrip('\r\n')
        if not l.startswith('Dialogue:'): continue
        d=parse_dl(l)
        if not d: continue
        if d["style"]=="orig": d["syls"]=parse_kf(d["text"]); O.append(d)
        elif d["style"]=="ts": T.append(d)
        elif d["style"]=="roma": d["syls"]=parse_kf(d["text"]); R.append(d)
    return O,T,R

def is_kanji(c): p=ord(c); return 0x4E00<=p<=0x9FFF or 0x3400<=p<=0x4DBF or 0xF900<=p<=0xFAFF
def is_kana(c): p=ord(c); return 0x3040<=p<=0x309F or 0x30A0<=p<=0x30FF

def cw(ch,fs=36):
    if ord(ch)>0x7F: return fs*0.92
    elif ch==' ': return fs*0.33
    elif ch in '!?.': return fs*0.35
    else: return fs*0.5
def tw(text,fs=36): return sum(cw(c,fs) for c in text)

def syl_pos(syls,fs=36):
    ws=[tw(t,fs) for _,t in syls]; tot=sum(ws); sx=RES_X/2-tot/2
    pos=[]; x=sx
    for w in ws: pos.append((x+w/2,w)); x+=w
    return pos,tot

def hsv2c(h,s,v):
    c=v*s; x=c*(1-abs((h/60)%2-1)); m=v-c
    if h<60: r,g,b=c,x,0
    elif h<120: r,g,b=x,c,0
    elif h<180: r,g,b=0,c,x
    elif h<240: r,g,b=0,x,c
    elif h<300: r,g,b=x,0,c
    else: r,g,b=c,0,x
    R,G,B=int((r+m)*255),int((g+m)*255),int((b+m)*255)
    return f"&H{B:02X}{G:02X}{R:02X}&"
def rfc(): return hsv2c(random.uniform(79,124),0.8,1.0)

# --- 段落分类 ---
def classify(idx,t):
    if idx<=2: return "info"
    if t<15000: return "OP"
    if t<41000: return "OP2"
    if t<61700: return "OP3"
    if t<84000: return "OP4"
    if t<86000: return "OP5"
    if t<98000: return "OP2"    # verse B
    if t<136000: return "OP3"   # pre-chorus 2
    if t<178000: return "OP4"   # chorus B
    if t<239000: return "OP5"   # bridge+interlude
    if t<296000: return "OP2"   # verse C
    if t<346000: return "OP"    # transition
    if t<352000: return "OP4"   # final chorus start
    if t<406000: return "OP4"   # final chorus
    return "OP5"                # ending

# --- 效果模板 ---
def fx_op(syls,s,e,pos):
    """OPJP: 4层/音节 (highlight+feather+lead-in+lead-out)"""
    fx=[]; y=18
    for i,(d,t) in enumerate(syls):
        if not t.strip(): continue
        ss=s+sum(x*10 for x,_ in syls[:i]); sd=d*10; se=ss+sd; cx=pos[i][0]
        # highlight
        fx.append(f"Dialogue: 1,{ft(ss)},{ft(se)},OPJP,,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y})\\fscx100\\fscy100\\t(0,200,\\fscx130\\fscy130)\\t(200,{sd},\\3c&HFFFFFF&\\fscx100\\fscy100)}}{t}")
        # feather
        rx,ry,rz=random.randint(-90,90),random.randint(-90,90),random.randint(-90,90)
        ox,oy=cx+random.randint(-80,80),y+random.randint(30,80)
        fx.append(f"Dialogue: 0,{ft(ss)},{ft(se)},OPJP,,0,0,0,fx,{{\\an5\\blur3\\1c&HFFFFFF&\\3c{C_PAR}\\t(0,{sd},\\frx{rx}\\fry{ry}\\frz{rz})\\move({ox:.0f},{oy},{cx:.0f},{y})\\fad(300,100)\\shad0\\p2}}{S_FEA}")
        # lead-in
        ls=max(s-100,0)
        fx.append(f"Dialogue: 0,{ft(ls)},{ft(ss)},OPJP,,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y})\\3c&HFFFFFF&\\fscy130\\t(0,500,\\fscy100)\\fad(500,0)}}{t}")
        # lead-out
        fx.append(f"Dialogue: 1,{ft(se)},{ft(e)},OPJP,,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y})\\fad(0,200)}}{t}")
    return fx

def fx_op2(syls,s,e,pos):
    """OPJP2: ~8层/音节 (5×notes+highlight+waveform+falling-lead-in)"""
    fx=[]; y=26; cc=0
    tw_=sum(pos[i][1] for i in range(len(syls)) if syls[i][1].strip())
    ll=RES_X/2-tw_/2-50; lr=RES_X/2+tw_/2+50
    for i,(d,t) in enumerate(syls):
        if not t.strip(): continue
        cc+=1; ss=s+sum(x*10 for x,_ in syls[:i]); sd=d*10; cx=pos[i][0]
        # 5× note particles
        for j in range(5):
            ps=max(0,ss-int(10+(sd/5)*j)); pe=ss+700+int((sd/5)*j)
            ns=S_NOTE[random.randint(0,2)]; dx=random.randint(-20,20); dy=random.randint(-130,-70)
            fx.append(f"Dialogue: 2,{ft(ps)},{ft(pe)},OPJP 2,,0,0,0,fx,{{\\p1\\an5\\fad(10,100)\\move({cx+dx:.0f},{y},{cx+random.randint(-20,20):.0f},{y+dy})\\fad(0,250)\\blur3\\shad0\\1c&HFFFFFF&\\3c{C_PAR}\\fscx150\\fscy150\\p1}}{ns}")
        # highlight
        fx.append(f"Dialogue: 1,{ft(ss)},{ft(ss+sd+300)},OPJP 2,,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y-10})\\fad(0,100)\\t(0,100,\\3c&HFFFFFF&\\fscx130\\fscy130)\\t(100,{sd},\\3c{C_OUT}\\fscx100\\fscy100\\bord3\\blur3)}}{t}")
        # heartbeat waveform
        ws=s-300+(cc-1)*700; we=e+300+(cc-1)*50
        fx.append(f"Dialogue: 0,{ft(max(0,ws))},{ft(we)},OPJP 2,,0,0,0,fx,{{\\clip({ll:.0f},{y-50},{lr:.0f},{y+50})\\an5\\move({RES_X/2-700:.0f},{y},{RES_X/2+1000:.0f},{y},0,6000)\\fad(0,300)\\bord0\\shad0\\1c&H000000&\\3c{C_WAVE}\\fscx50\\fscy50\\p1}}{S_HB_EXT}")
        # falling lead-in
        ls=s-700+(cc-1)*30
        fx.append(f"Dialogue: 1,{ft(max(0,ls))},{ft(ss)},OPJP 2,,0,0,0,fx,{{\\an5\\frx360\\move({RES_X/2:.0f},{y-70},{cx:.0f},{y-10},0,200)\\t(0,500,\\bord2\\frx0)\\t(0,200,\\fscx100\\fscy100)}}{t}")
    return fx

def fx_op3(syls,s,e,pos,is2=False):
    """OPJP3: 双行 (highlight+lead-in+lead-out)"""
    fx=[]; sty="OPJP 3-2" if is2 else "OPJP 3-1"; y=58 if is2 else 23
    for i,(d,t) in enumerate(syls):
        if not t.strip(): continue
        ss=s+sum(x*10 for x,_ in syls[:i]); sd=d*10; se=ss+sd; cx=pos[i][0]
        fx.append(f"Dialogue: 1,{ft(ss)},{ft(se)},{sty},,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y})\\fscx100\\fscy100\\t(0,200,\\fscx130\\fscy130)\\t(200,{sd},\\3c&HFFFFFF&\\fscx100\\fscy100)}}{t}")
        fx.append(f"Dialogue: 0,{ft(max(s-100,0))},{ft(ss)},{sty},,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y})\\3c&HFFFFFF&\\fscy130\\t(0,500,\\fscy100)\\fad(500,0)}}{t}")
        fx.append(f"Dialogue: 1,{ft(se)},{ft(e)},{sty},,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y})\\fad(0,200)}}{t}")
    return fx

def fx_op4(syls,s,e,pos):
    """OPJP4: 副歌华丽 (lead-in+highlight+lead-out+flowers+flourish+grass)"""
    fx=[]; y=700; ns=sum(1 for _,t in syls if t.strip()); sc=0
    for i,(d,t) in enumerate(syls):
        if not t.strip(): continue
        sc+=1; ss=s+sum(x*10 for x,_ in syls[:i]); sd=d*10; se=ss+sd; cx=pos[i][0]
        # lead-in
        ls=s-1000+i*50
        fx.append(f"Dialogue: 4,{ft(max(0,ls))},{ft(ss)},OPJP 4,,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y})\\fad(300,0)}}{t}")
        # highlight
        fx.append(f"Dialogue: 5,{ft(ss)},{ft(se)},OPJP 4,,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y})\\t(0,33,\\fscx120\\fscy120\\1c&HFFFFFF&)\\t(33,{sd},\\fscx100\\fscy100\\1c{C_PRI})}}{t}")
        # lead-out
        fo=e-800+int((i/max(ns,1))*800)
        fx.append(f"Dialogue: 4,{ft(se)},{ft(fo)},OPJP 4,,0,0,0,fx,{{\\an5\\pos({cx:.0f},{y})\\fad(0,300)}}{t}")
        # flowers (2-3 per syl)
        for _ in range(random.randint(2,3)):
            fl=S_FLOWER[random.randint(0,2)]; fc=random.choice(MAU)
            ir=random.randint(-100,0); er=random.randint(50,300)*random.choice([-1,1])
            dx=random.randint(-50,50); dy=random.randint(-30,30)
            fs_=max(0,se-sd-random.randint(0,300)); fe_=se+500
            fx.append(f"Dialogue: 2,{ft(fs_)},{ft(fe_)},OPJP 4,,0,0,0,fx,{{\\c{fc}\\bord0\\fscx20\\fscy20\\an5\\frz{ir}\\move({cx+20:.0f},{y-10},{cx+dx:.0f},{y+dy})\\fad(0,500)\\t(0,300,\\fscx70\\fscy70)\\t(\\frz{er})\\p1}}{fl}")
    # flourish (per line)
    if pos:
        fx0=pos[0][0]; yb=y+70
        for fp in FLOURISH:
            gc=rfc(); npts=15
            for pi in range(npts):
                t_=pi/max(npts-1,1); ldur=e-s
                ss_=s-1000+int(ldur*(t_**1.0)); se_=ss_+int(ldur+800-1000*t_)+random.randint(0,300)
                sc_=int(60-30*t_); ang=t_*math.pi*2
                px=fx0-70+pi*8+random.randint(-5,5); py=yb+math.sin(ang)*30+random.randint(-10,10)
                px2=px+random.randint(-3,3); py2=py+random.randint(-3,3)
                fx.append(f"Dialogue: 0,{ft(max(0,ss_))},{ft(se_)},OPJP 4,,0,0,0,fx,{{\\an5\\fscx{sc_}\\fscy{sc_}\\1c&H0000FF&\\bord0\\shad0\\blur1\\move({px:.0f},{py:.0f},{px2:.0f},{py2:.0f})\\t(100,200,\\alpha&H88&\\1c{gc})\\fad(0,500)\\p1}}{S_CIRCLE}")
    # grass (per syl)
    for i,(d,t) in enumerate(syls):
        if not t.strip(): continue
        cx=pos[i][0]; ss_=s+sum(x*10 for x,_ in syls[:i])
        for gi in range(min(3,len(GRASS))):
            gc=rfc()
            for pi in range(8):
                t_=pi/7; ldur=e-s
                sg=s-1200+int(ss_-s)-random.randint(0,300)
                eg=sg+int(ldur+1200-(ss_-s)-800*t_)
                ang=t_*math.pi; px=cx+pi*5*random.choice([-1,1]); py=y+math.sin(ang)*20
                sc_=int((40-20*t_)*(1.5-0.5*(i/max(ns,1))))
                fx.append(f"Dialogue: 0,{ft(max(0,sg))},{ft(max(eg,sg+100))},OPJP 4,,0,0,0,fx,{{\\an5\\fscx{sc_}\\fscy{sc_}\\1c&H0000FF&\\bord0\\shad0\\blur1\\pos({px:.0f},{py:.0f})\\t(100,200,\\alpha&H88&\\1c{gc})\\fad(0,500)\\p1}}{S_CIRCLE}")
    return fx

def fx_op5(syls,s,e,pos):
    """OPJP5: 终章 (butterfly+halo+feather+text-lead-in)"""
    fx=[]; y=23; cc=0; cc2=0
    for i,(d,t) in enumerate(syls):
        if not t.strip(): continue
        cc+=1; cc2+=1; ss=s+sum(x*10 for x,_ in syls[:i]); sd=d*10; se=ss+sd; cx=pos[i][0]; w=pos[i][1]
        we=se+500
        # butterfly right wing
        flap="".join(f"\\t({a},{b},\\fry{c})" for a,b,c in [(0,200,-80),(200,300,0),(300,400,-80),(400,500,0),(500,600,-80),(600,700,0),(700,800,-80),(800,900,0),(900,1000,-80),(1000,1100,0),(1100,1300,-80),(1300,1450,0),(1450,1600,-80),(1600,1700,0),(1700,1850,-80),(1850,2000,0),(2000,2200,-80),(2200,2300,0),(2300,2400,-80),(2400,2700,0)])
        fx.append(f"Dialogue: 1,{ft(ss-25)},{ft(we)},OPJP 5,,0,0,0,fx,{{\\an1\\frz10\\fad(0,200)\\move({cx+w/2:.0f},{y},{cx+w/2-50:.0f},{y-50})\\shad1\\bord0\\blur1\\3c&H000000&\\4c&H000000&\\c&HFFFFFF&\\fscx70\\fscy70{flap}\\p1}}{S_WING}")
        # butterfly left wing
        flapL="".join(f"\\t({a},{b},\\fry{c})" for a,b,c in [(0,200,250),(200,300,180),(300,400,250),(400,500,180),(500,600,250),(600,700,180),(700,800,250),(800,900,180),(900,1000,250),(1000,1100,180),(1100,1300,250),(1300,1450,180),(1450,1600,250),(1600,1700,180),(1700,1850,250),(1850,2000,180),(2000,2200,250),(2200,2300,180),(2300,2400,250),(2400,2700,180)])
        fx.append(f"Dialogue: 1,{ft(ss-25)},{ft(we)},OPJP 5,,0,0,0,fx,{{\\an1\\frz-10\\fry180\\fad(0,200)\\move({cx-w/2:.0f},{y},{cx-w/2-50:.0f},{y-50})\\shad1\\bord0\\blur1\\3c&H000000&\\4c&H000000&\\c&HFFFFFF&\\fscx70\\fscy70{flapL}\\p1}}{S_WING}")
        # halo
        fx.append(f"Dialogue: 1,{ft(ss-25)},{ft(we)},OPJP 5,,0,0,0,fx,{{\\frz5\\fscx100\\fscy50\\an5\\blur2\\fad(0,300)\\move({cx:.0f},{y-40},{cx-50:.0f},{y-90})\\bord1\\3c{C_HALO1}\\c{C_HALO2}\\p1}}{S_HALO}")
        # text highlight
        fx.append(f"Dialogue: 1,{ft(ss-25)},{ft(we)},OPJP 5,,0,0,0,fx,{{\\an5\\blur2\\fad(0,300)\\move({cx:.0f},{y},{cx-50:.0f},{y-50})\\t(0,25,\\bord10\\blur3)\\t(25,{sd},\\frz5\\3c&HFFFFFF&\\fscx100\\fscy100\\bord5\\blur2)}}{t}")
        # feather lead-in
        fs_=s-900+(cc-1)*20; fe_=se+500+(cc-1)*25
        fx.append(f"Dialogue: 1,{ft(max(0,fs_))},{ft(fe_)},OPJP 5,,0,0,0,fx,{{\\fad(0,100)\\1c&HFFFFFF&\\3c{C_PAR}\\bord1\\blur2\\fscx50\\fscy50\\an5\\frz{random.randint(-100,0)}\\move({cx:.0f},{y},{cx+random.randint(-50,50):.0f},{y+random.randint(-50,50)})\\fad(230,0)\\t(0,{e-s},\\fscy90\\fscx90\\frz{random.randint(-700,700)}\\fry{random.randint(-700,700)}\\frx{random.randint(-700,700)}\\fad(0,500))\\p3}}{S_FEA}")
        # text lead-in
        tls=s-400+(cc2-1)*35
        fx.append(f"Dialogue: 1,{ft(max(0,tls))},{ft(ss)},OPJP 5,,0,0,0,fx,{{\\an5\\3c{C_PAR}\\blur1\\move({cx+10:.0f},{y+10},{cx:.0f},{y},100,400)\\fad(230,0)\\t(0,400,\\1c\\3c&HFFFFFF&\\fscx100\\fscy100\\blur0)}}{t}")
    return fx

# --- 假名注音 ---
def gen_furi(syls,rsyls,pos,s,e,sty_base,fy):
    fx=[]
    if len(syls)!=len(rsyls): return fx
    fsty=sty_base+"-furigana"
    for i,((do,to),(dr,tr)) in enumerate(zip(syls,rsyls)):
        to=to.strip(); tr=tr.strip()
        if not to or not tr: continue
        if not any(is_kanji(c) for c in to): continue
        if all(is_kana(c) for c in to): continue
        hira=r2h(tr)
        if not hira or hira==to: continue
        cx=pos[i][0]; ss=s+sum(x*10 for x,_ in syls[:i]); sd=do*10
        fx.append(f"Dialogue: 0,{ft(max(0,s-100))},{ft(e)},{fsty},,0,0,0,fx,{{\\an5\\pos({cx:.0f},{fy})\\fad(300,300)\\t({ss-s},{ss-s+sd},\\1c&H00FFFF&)\\t({ss-s+sd},{e-s},\\1c{C_PRI})}}{hira}")
    return fx

# --- 中文 ---
def gen_cn(ts,sec,s,e):
    txt=re.sub(r'\{[^}]*\}','',ts["text"]).strip()
    if not txt: return []
    if sec=="OP4":
        return [f"Dialogue: 6,{ft(s)},{ft(e)},OPCN,,0,0,0,,{{\\fad(300,300)\\pos({RES_X/2:.0f},675)}}{txt}"]
    return [f"Dialogue: 0,{ft(s)},{ft(e)},OPCN,,0,0,0,,{{\\fad(300,300)}}{txt}"]

# --- ASS头 ---
def header():
    return f"""[Script Info]
; Generated by HX-Ass-Skill FX Generator
; Song: 羽ばたきのバースデイ (天使の3P! OP)
Title: 羽ばたきのバースデイ FX
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {RES_X}
PlayResY: {RES_Y}
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: OPJP,{FONT_JP},36,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,0,1
Style: OPJP 2,{FONT_JP},36,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,8,1
Style: OPJP 3-1,{FONT_JP},36,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,5,1
Style: OPJP 3-2,{FONT_JP},36,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,40,1
Style: OPJP 4,{FONT_JP},36,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,3,2.5,1,20,0,10,1
Style: OPJP 5,{FONT_JP},36,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,3,2.5,8,0,0,5,1
Style: OPJP-furigana,{FONT_JP},18,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,0,1
Style: OPJP 2-furigana,{FONT_JP},18,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,8,1
Style: OPJP 3-1-furigana,{FONT_JP},18,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,5,1
Style: OPJP 4-furigana,{FONT_JP},18,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,1.5,1.25,1,20,0,10,1
Style: OPJP 5-furigana,{FONT_JP},18,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},0,0,0,0,100,100,0,0,1,1.5,1.25,8,0,0,5,1
Style: OPCN,{FONT_CN},32,{C_PRI},&H000000FF&,{C_OUT},{C_SHD},-1,0,0,0,100,100,0,0,1,3,2.5,2,0,0,4,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# === MAIN ===
def main():
    print("="*60)
    print("  羽ばたきのバースデイ - ASS FX Generator")
    print("="*60)
    O,T,R=parse_ass(INPUT)
    print(f"  Parsed: {len(O)} orig, {len(T)} ts, {len(R)} roma")
    
    ts_map={t["start_ms"]:t for t in T}
    rm_map={r["start_ms"]:r for r in R}
    
    all_fx=[]
    # 双行缓冲
    op3_pairs=[]
    
    for idx,orig in enumerate(O):
        s,e,syls=orig["start_ms"],orig["end_ms"],orig["syls"]
        if not syls: continue
        if all(d==0 for d,_ in syls):
            txt="".join(t for _,t in syls)
            if txt.strip():
                all_fx.append(f"Dialogue: 5,{ft(s)},{ft(e)},OPJP,,0,0,0,fx,{{\\an8\\pos({RES_X/2:.0f},30)\\fad(500,500)\\blur0.5}}{txt}")
            continue
        
        sec=classify(idx,s)
        if sec=="info": continue
        
        pos,_=syl_pos(syls)
        rm=rm_map.get(s)
        rsyls=rm["syls"] if rm else []
        ts=ts_map.get(s)
        
        # 假名注音y偏移
        furi_y_map={"OP":-4,"OP2":4,"OP3":1,"OP4":678,"OP5":1}
        fy=furi_y_map.get(sec,0)
        
        if sec=="OP":
            all_fx.extend(fx_op(syls,s,e,pos))
            if rsyls: all_fx.extend(gen_furi(syls,rsyls,pos,s,e,"OPJP",fy))
        elif sec=="OP2":
            all_fx.extend(fx_op2(syls,s,e,pos))
            if rsyls: all_fx.extend(gen_furi(syls,rsyls,pos,s,e,"OPJP 2",fy))
        elif sec=="OP3":
            # 双行: 奇数行用 3-1, 偶数行用 3-2
            op3_pairs.append((syls,s,e,pos,rsyls))
            if len(op3_pairs)>=2:
                # 两行配对
                s1,s2=op3_pairs[-2],op3_pairs[-1]
                all_fx.extend(fx_op3(s1[0],s1[1],s1[2],s1[3],False))
                all_fx.extend(fx_op3(s2[0],s2[1],s2[2],s2[3],True))
                if s1[4]: all_fx.extend(gen_furi(s1[0],s1[4],s1[3],s1[1],s1[2],"OPJP 3-1",1))
                if s2[4]: all_fx.extend(gen_furi(s2[0],s2[4],s2[3],s2[1],s2[2],"OPJP 3-1",36))
            else:
                all_fx.extend(fx_op3(syls,s,e,pos,False))
                if rsyls: all_fx.extend(gen_furi(syls,rsyls,pos,s,e,"OPJP 3-1",fy))
        elif sec=="OP4":
            all_fx.extend(fx_op4(syls,s,e,pos))
            if rsyls: all_fx.extend(gen_furi(syls,rsyls,pos,s,e,"OPJP 4",fy))
        elif sec=="OP5":
            all_fx.extend(fx_op5(syls,s,e,pos))
            if rsyls: all_fx.extend(gen_furi(syls,rsyls,pos,s,e,"OPJP 5",fy))
        
        # 中文翻译
        if ts: all_fx.extend(gen_cn(ts,sec,s,e))
    
    print(f"  Generated: {len(all_fx)} FX lines")
    
    # 写入
    out=header()
    # 原始行作为注释
    with open(INPUT,"r",encoding="utf-8-sig") as f:
        for l in f:
            l=l.rstrip('\r\n')
            if l.startswith("Dialogue:"):
                out+=f"Comment: {l[len('Dialogue: '):]}\n"
    out+="; === FX lines ===\n"
    for fx in all_fx:
        out+=fx+"\n"
    
    with open(OUTPUT,"w",encoding="utf-8-sig") as f:
        f.write(out)
    
    print(f"\n  [DONE] Output: {OUTPUT}")
    print(f"  Total FX events: {len(all_fx)}")
    print(f"  Resolution: {RES_X}x{RES_Y}")
    print("="*60)

if __name__=="__main__":
    random.seed(42)
    main()
