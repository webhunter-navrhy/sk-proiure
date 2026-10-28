"""Hero PRO iURE v9 (28. 10. 2026) – obrázok z vizuálu klienta, prekreslený načisto.

Predloha: „úvodná stránka final 3“ (mail 19. 10. 2026). Rovnaká kompozícia ako vo vizuáli:
rovnaký úbežník, rovnaký sklon okrajov labyrintu, muž s aktovkou v rovnakom mieste a veľkosti,
justícia v rovnakej póze a mieste (silueta vyrezaná priamo z jeho vizuálu).
Úpravy podľa klienta (19. 10. + 23. 10.): čiernobiely, bez oblakov/svetelných pruhov a tieňovania,
trochu užšia cesta, kompaktnejší labyrint, čiary labyrintu súvislé a dotiahnuté (žiadne
prerušené a rozmazané čiary ako v AI obrázku), jemná (svetlejšia) silueta justície.

  python3 -I hero_gen.py <podklady> <vystup_dir>
"""
import sys, random
import numpy as np
import cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

POD, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
VIZ = POD / 'INBOX_14089_úvodná_stránka_final_3.png'
MAN = POD / 'INBOX_14089_Právník_kráčí_labyrintem_k_světlu.png'

# ---- geometria odmeraná z vizuálu (výrez obrázka x 690–1536, y 0–480 → mierka K) ----
CROP_X0 = 690
W = 2000
K = W / 846.0
H = int(round(480 * K))           # 1135
VPX, VPY = 458 * K, 205 * K       # úbežník (koniec cesty pod sochou)
SS = 3                            # supersampling
ZB = 2.2                          # hĺbka spodného okraja
F = (H - VPY) * ZB                # ohnisko (kamera vo výške 1)
U = 1.72                          # polovičná šírka labyrintu (okraje so sklonom ako vo vizuáli)
HALF_PATH = 0.092                 # cesta trochu užšia ako vo vizuáli
NSIDE = 13                        # stĺpcov na každej strane (kompaktnejší ako vo vizuáli)
CELL = (U - HALF_PATH) / NSIDE
Z_START = ZB - 0.35
Z_END = 90.0
ROWS = int((Z_END - Z_START) / CELL)
T = 0.16 * CELL                  # hrúbka steny (zvislé steny)
WALL = np.array([40, 42, 46], np.float32) / 255     # takmer čierna
PARA = np.array([35, 39, 52], np.float32) / 255     # § tmavomodrošedé ako vo vizuáli


def proj(u, z):
    return VPX + F * u / z, VPY + F / z


def z_of_y(y):
    return F / np.maximum(y - VPY, 1e-3)


# ---------- bludisko: dokonalé (každá chodba súvislá), s dlhšími rovnými úsekmi ----------
def maze(ncols, nrows, seed):
    rnd = random.Random(seed)
    east = np.zeros((nrows, ncols), bool)
    north = np.zeros((nrows, ncols), bool)
    seen = np.zeros((nrows, ncols), bool)
    start = (0, ncols // 2)
    stack = [start]; seen[start] = True; last = None
    while stack:
        r, c = stack[-1]
        nb = [(dr, dc) for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0))
              if 0 <= r + dr < nrows and 0 <= c + dc < ncols and not seen[r + dr, c + dc]]
        if not nb:
            stack.pop(); last = None; continue
        if last in nb and rnd.random() < 0.62:
            d = last
        else:
            d = rnd.choices(nb, [1.6 if dr == 0 else 1.0 for dr, dc in nb])[0]
        dr, dc = d; rr, cc = r + dr, c + dc
        if dc == 1: east[r, c] = True
        elif dc == -1: east[r, cc] = True
        elif dr == 1: north[r, c] = True
        else: north[rr, c] = True
        seen[rr, cc] = True; stack.append((rr, cc)); last = d
    return east, north


mask = np.zeros((H * SS, W * SS), np.uint8)       # steny
pmask = np.zeros((H * SS, W * SS), np.uint8)      # paragrafy
SHIFT = 4


def poly(img, pts):
    p = np.array([[x * SS * (1 << SHIFT), y * SS * (1 << SHIFT)] for x, y in pts], np.int64).astype(np.int32)
    cv2.fillPoly(img, [p], 255, lineType=cv2.LINE_AA, shift=SHIFT)


def quad(u1, z1, u2, z2):
    z1 = max(z1, 0.3); z2 = max(z2, 0.3)
    poly(mask, [proj(u1, z1), proj(u2, z1), proj(u2, z2), proj(u1, z2)])


def tz(z):
    # vodorovné steny: hrúbka v hĺbke tak, aby na obraze pôsobili podobne silno ako zvislé
    return min(T * z * 0.78, 0.26 * CELL)


def vwall(u, z0, z1):            # stena pozdĺž hĺbky (zvislá na obraze), predĺžená na spoje
    quad(u - T / 2, z0 - tz(z0) / 2, u + T / 2, z1 + tz(z1) / 2)


def hwall(u0, u1, z):            # stena naprieč (vodorovná na obraze)
    quad(min(u0, u1) - T / 2, z - tz(z) / 2, max(u0, u1) + T / 2, z + tz(z) / 2)


font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia Bold.ttf', 400)
GL = Image.new('L', (420, 480), 0)
ImageDraw.Draw(GL).text((210, 250), '§', font=font, fill=255, anchor='mm', stroke_width=7, stroke_fill=255)
gl_box = GL.getbbox(); GL = GL.crop(gl_box)


def paragraf(u0, u1, z0, z1):
    """§ v izbičke (u0..u1, z0..z1): stojí vzpriamene ako vo vizuáli, zmenšený podľa hĺbky."""
    gw, gh = GL.size
    xl, yb = proj(u0, z0); xr, _ = proj(u1, z0)
    _, yt = proj(u0, z1)
    xl2, _ = proj(u0, z1); xr2, _ = proj(u1, z1)
    cx = (xl + xr + xl2 + xr2) / 4; cy = (yb + yt) / 2
    rh = yb - yt; rw = (xr - xl + xr2 - xl2) / 2
    h = rh * 0.78
    w = min(rw * 0.46, h * gw / gh)
    tw, th = max(2, int(round(w * SS))), max(2, int(round(h * SS)))
    g = np.asarray(GL.resize((tw, th), Image.LANCZOS))
    x0 = int(round(cx * SS - tw / 2)); y0 = int(round(cy * SS - th / 2))
    x0c, y0c = max(x0, 0), max(y0, 0)
    x1c, y1c = min(x0 + tw, W * SS), min(y0 + th, H * SS)
    if x1c <= x0c or y1c <= y0c:
        return
    reg = pmask[y0c:y1c, x0c:x1c]
    np.maximum(reg, g[y0c - y0:y1c - y0, x0c - x0:x1c - x0], out=reg)


for side, seed in ((-1, 11), (1, 29)):
    e, n = maze(NSIDE, ROWS, seed)
    rnd = random.Random(seed * 7)

    def U_(c):   # u súradnica hranice medzi stĺpcom c-1 a c (c = 0 je okraj cesty)
        return side * (HALF_PATH + c * CELL)

    def Z_(r):
        return Z_START + r * CELL

    # izbičky s § (2 stĺpce × 3 riadky) ako vo vizuáli, v popredí
    rooms = []
    for _ in range(400):
        r = rnd.randrange(0, int((6.8 - Z_START) / CELL) - 4)
        c = rnd.randrange(1, NSIDE - 2)
        if any(abs(r - rr) < 6 and abs(c - cc) < 4 for rr, cc in rooms):
            continue
        rooms.append((r, c))
        if len(rooms) >= 9:
            break
    for r, c in rooms:
        # vnútro otvorené, obvod uzavretý s jedným vchodom
        for rr in range(r, r + 4):
            e[rr, c] = True
            if c > 0: e[rr, c - 1] = False
            e[rr, c + 1] = False
        for cc in (c, c + 1):
            n[r, cc] = n[r + 1, cc] = n[r + 2, cc] = True
            n[r + 3, cc] = False
            if r > 0: n[r - 1, cc] = False
        if rnd.random() < 0.5:
            n[r - 1 if r > 0 else r + 3, c + rnd.randint(0, 1)] = True
        else:
            e[r + rnd.randint(0, 3), c + 1] = True
        paragraf(min(U_(c), U_(c + 2)), max(U_(c), U_(c + 2)), Z_(r), Z_(r + 4))

    for r in range(ROWS):
        z0, z1 = Z_(r), Z_(r + 1)
        for c in range(NSIDE):
            if c < NSIDE - 1 and not e[r, c]:
                vwall(U_(c + 1), z0, z1)
            if r < ROWS - 1 and not n[r, c]:
                hwall(U_(c), U_(c + 1), z1)
    # okraj cesty: súvislá stena so vchodmi do labyrintu
    r = 0
    while r < ROWS:
        L = rnd.randint(5, 11)
        vwall(U_(0), Z_(r), Z_(min(r + L, ROWS)))
        r += L + 1
    # vonkajší okraj labyrintu
    vwall(U_(NSIDE), Z_(0), Z_(ROWS))

# ---------- zmenšenie, zoslabenie do diaľky (bez hmly a mrakov) ----------
def down(m):
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


wm = down(mask); pm = down(pmask)
yy = np.arange(H, dtype=np.float32)[:, None]
zz = z_of_y(yy + 0.5)
# do diaľky čiary svetlejú (ako vo vizuáli), ďaleko sa zjemnia, aby nevznikla „mora“
soft = ndimage.gaussian_filter(wm, 1.0)
soft2 = ndimage.gaussian_filter(wm, 2.6)
mix = np.clip((zz - 4.5) / 3.5, 0, 1)
mix2 = np.clip((zz - 9) / 7, 0, 1)
wm = wm * (1 - mix) + soft * mix
wm = wm * (1 - mix2) + soft2 * mix2
fade = 1 - np.exp(-np.maximum(zz - 4.0, 0) / 32.0)
wa = wm * (1 - fade) * (yy > VPY)
pa = pm * (1 - np.clip((zz - 3.0) / 4.5, 0, 1)) * 0.92
img = np.ones((H, W, 3), np.float32)
img = img * (1 - wa[..., None]) + WALL * wa[..., None]
img = img * (1 - pa[..., None]) + PARA * pa[..., None]

# ---------- justícia: silueta vyrezaná z vizuálu klienta, jemnejšia ----------
vz = Image.open(VIZ).convert('L')
bx0, by0, bx1, by1 = 1080, 60, 1250, 215
st = vz.crop((bx0, by0, bx1, by1))
up = 8
big = np.asarray(st.resize((st.width * up, st.height * up), Image.BICUBIC)).astype(np.float32) / 255
big = ndimage.gaussian_filter(big, 3)
sil = big < 0.84
sil[int(0.95 * sil.shape[0]):] = False           # spodok sa vo vizuáli stráca vo svetle
lab, nl = ndimage.label(sil)
sz = ndimage.sum(sil, lab, range(1, nl + 1))
sil = np.isin(lab, [i + 1 for i, v in enumerate(sz) if v > 4000])
sil = ndimage.binary_opening(sil, iterations=2)
tw, th = int(round((bx1 - bx0) * K)), int(round((by1 - by0) * K))
sa = cv2.resize(sil.astype(np.float32), (tw, th), interpolation=cv2.INTER_AREA)
sa = ndimage.gaussian_filter(sa, 0.6)
hh = np.linspace(0, 1, th, dtype=np.float32)[:, None]
# tón: hore jemná šedá, smerom k ceste sa rozplýva do bielej (bez svetelných pruhov)
tone = 0.79 + 0.17 * np.clip((hh - 0.40) / 0.50, 0, 1)
alpha = sa * np.clip((0.93 - hh) / 0.36, 0, 1) ** 1.2
ox, oy = int(round((bx0 - CROP_X0) * K)), int(round((by0 + 26) * K))
reg = img[oy:oy + th, ox:ox + tw]
a3 = alpha[..., None]
img[oy:oy + th, ox:ox + tw] = reg * (1 - a3) + tone[..., None] * np.array([1, 1.004, 1.012], np.float32) * a3

# ---------- muž s aktovkou (z jeho čistého ČB obrázka), poloha a veľkosť ako vo vizuáli ----------
m = Image.open(MAN).convert('L')
m = np.asarray(m.crop((745, 362, 912, 822))).astype(np.float32) / 255
mk = m < 0.62
mk = ndimage.binary_closing(mk, iterations=3)
mk = ndimage.binary_fill_holes(mk)
lab, nl = ndimage.label(mk)
sizes = ndimage.sum(mk, lab, range(1, nl + 1))
mk = lab == (np.argmax(sizes) + 1)
ma = ndimage.gaussian_filter(mk.astype(np.float32), 0.9)
man_h = int(round(132 * K))
scale = man_h / m.shape[0]
mw = int(round(m.shape[1] * scale))
mi = cv2.resize(m, (mw, man_h), interpolation=cv2.INTER_AREA)
mai = np.clip(cv2.resize(ma, (mw, man_h), interpolation=cv2.INTER_AREA), 0, 1)
feet_y = int(round(433 * K))
mx = int(round(VPX - mw / 2 + 3)); my = feet_y - man_h
reg = img[my:my + man_h, mx:mx + mw]
img[my:my + man_h, mx:mx + mw] = reg * (1 - mai[..., None]) + mi[..., None] * mai[..., None]

out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), 'RGB')
out.save(OUT / 'hero_full.png')
out.save(OUT / 'hero-lab.webp', quality=84, method=6)
# mobil: výrez okolo cesty so sochou
mob = out.crop((int(VPX - 520), int(72 * K), int(VPX + 520), H))
mob.resize((800, int(mob.height * 800 / mob.width)), Image.LANCZOS).save(OUT / 'hero-lab-m.webp', quality=82, method=6)
og = Image.new('RGB', (1200, 630), 'white')
oc = out.resize((1200, int(H * 1200 / W)), Image.LANCZOS)
og.paste(oc, (0, 630 - oc.height))
og.save(OUT / 'og.jpg', quality=86)
print('ok', out.size, 'rows', ROWS, 'cell', round(CELL, 4), 'F', round(F))
