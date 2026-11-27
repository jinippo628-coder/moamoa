from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

S = 720  # supersampled canvas (4x of 180)

# --- background: diagonal gradient #0f131d -> #1b2232 with soft purple glow
bg = Image.new("RGB", (S, S))
d = ImageDraw.Draw(bg)
c1 = (0x0f, 0x13, 0x1d)
c2 = (0x1b, 0x22, 0x32)
for i in range(S * 2):
    t = i / (S * 2 - 1)
    col = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
    d.line([(i, 0), (0, i)], fill=col, width=2)

glow = Image.new("RGB", (S, S), (0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([S*0.10, S*0.05, S*0.90, S*0.85], fill=(92, 46, 160))
glow = glow.filter(ImageFilter.GaussianBlur(S*0.22))
bg = Image.blend(bg, Image.blend(bg, glow, 0.55), 0.35)

# --- heart outline (parametric) centered, slightly above middle
def heart_points(cx, cy, scale, n=720):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        pts.append((cx + x * scale, cy - y * scale))
    return pts

mask = Image.new("L", (S, S), 0)
md = ImageDraw.Draw(mask)
pts = heart_points(S/2, S/2 + S*0.02, S/2 * 0.0525)
md.polygon(pts, fill=255)

# soft outer shadow of heart for depth
shadow = mask.filter(ImageFilter.GaussianBlur(S*0.035))
bg.paste(Image.new("RGB", (S, S), (0, 0, 0)), (0, int(S*0.02)), shadow.point(lambda v: int(v*0.55)))

# --- heart gradient: light violet top-left -> deep purple bottom-right
hgrad = Image.new("RGB", (S, S))
hd = ImageDraw.Draw(hgrad)
p1 = (0xa7, 0x8b, 0xfa)   # violet-300
p2 = (0x6d, 0x28, 0xd9)   # violet-700
for i in range(S * 2):
    t = i / (S * 2 - 1)
    col = tuple(int(p1[k] + (p2[k] - p1[k]) * t) for k in range(3))
    hd.line([(0, i), (i, 0)], fill=col, width=2)

heart = Image.new("RGB", (S, S))
heart.paste(hgrad, (0, 0), mask)

# glossy highlight in upper-left lobe
hl = Image.new("L", (S, S), 0)
hld = ImageDraw.Draw(hl)
hld.ellipse([S*0.30, S*0.26, S*0.46, S*0.40], fill=150)
hl = hl.filter(ImageFilter.GaussianBlur(S*0.02))
hl = Image.composite(hl, Image.new("L", (S, S), 0), mask)
heart.paste(Image.new("RGB", (S, S), (255, 255, 255)), (0, 0), hl)
bg.paste(heart, (0, 0), mask)

# --- '뫄' in the heart
txt = Image.new("RGBA", (S, S), (0, 0, 0, 0))
td = ImageDraw.Draw(txt)
font = ImageFont.truetype("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf", int(S*0.30))
bbox = td.textbbox((0, 0), "뫄", font=font)
tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
tx = S/2 - tw/2 - bbox[0]
ty = S/2 + S*0.045 - th/2 - bbox[1]
# shadow
for dx, dy in [(0, 6), (0, 10)]:
    td.text((tx+dx, ty+dy), "뫄", font=font, fill=(30, 10, 60, 120))
# face
td.text((tx, ty), "뫄", font=font, fill=(255, 248, 255, 255))
bg = Image.alpha_composite(bg.convert("RGBA"), txt).convert("RGB")

# --- small block-grid accent under the heart (puzzle hint)
bd = ImageDraw.Draw(bg)
bs = int(S*0.036)
gap = int(bs*0.55)
x0 = S/2 - (bs*2 + gap*1.5)/2
y0 = S*0.855
for row, cols in enumerate([3, 2]):
    total = cols*bs + (cols-1)*gap
    sx = S/2 - total/2
    for c in range(cols):
        x = sx + c*(bs+gap)
        y = y0 + row*(bs+gap)
        alpha_col = (0xa7,0x8b,0xfa) if (row==0 and c==1) else (0x8f,0x9a,0xb8)
        bd.rounded_rectangle([x, y, x+bs, y+bs], radius=int(bs*0.22), fill=alpha_col)

bg.resize((180, 180), Image.LANCZOS).save("deploy-moamoa/apple-touch-icon.png", optimize=True)
bg.resize((512, 512), Image.LANCZOS).save("deploy-moamoa/icon-preview-512.png", optimize=True)
print("saved")
