"""Draws the app icon and writes the sizes the app needs. Run: py src/make_icons.py"""
import pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = pathlib.Path(__file__).resolve().parent.parent
S = 2048                                    # drawn large, scaled down for smooth edges
GREEN_HI, GREEN_LO, INK = (22, 150, 106), (7, 70, 52), (10, 84, 61)
PAPER, RULE, ORANGE = (252, 253, 250), (196, 212, 203), (245, 140, 30)
u = lambda v: int(round(v * S))

def font(size):
    for name in ('segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf'):
        try: return ImageFont.truetype(name, size)
        except OSError: pass
    return ImageFont.load_default()

# background: diagonal green gradient
ramp = Image.linear_gradient('L').resize((S, S)).rotate(-35, resample=Image.BICUBIC, expand=False, fillcolor=128)
bg = Image.composite(Image.new('RGB', (S, S), GREEN_LO), Image.new('RGB', (S, S), GREEN_HI), ramp).convert('RGBA')

# the receipt: paper with a torn zigzag foot, a big euro sign and two item lines
paper = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(paper)
x0, x1, y0, y1 = u(.27), u(.71), u(.15), u(.80)
d.rounded_rectangle([x0, y0, x1, y1 - u(.04)], radius=u(.035), fill=PAPER)
teeth = 7; w = (x1 - x0) / teeth
pts = [(x0, y1 - u(.06))]
for i in range(teeth): pts += [(x0 + w * (i + .5), y1), (x0 + w * (i + 1), y1 - u(.045))]
pts += [(x1, y1 - u(.06))]
d.polygon(pts, fill=PAPER)
f = font(u(.37)); box = d.textbbox((0, 0), '€', font=f)
d.text(((x0 + x1) / 2 - (box[0] + box[2]) / 2, u(.375) - (box[1] + box[3]) / 2), '€', font=f, fill=INK)
for y, wd in ((.60, .30), (.665, .19)):
    d.rounded_rectangle([x0 + u(.065), u(y), x0 + u(.065) + u(wd), u(y) + u(.03)], radius=u(.015), fill=RULE)
paper = paper.rotate(7, resample=Image.BICUBIC, center=(S / 2, S / 2))

shadow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
shadow.paste((3, 40, 30, 150), (u(.012), u(.03)), paper.split()[3])
bg = Image.alpha_composite(bg, shadow.filter(ImageFilter.GaussianBlur(u(.022))))
bg = Image.alpha_composite(bg, paper)

# the badge: an orange tick, "this one is sorted"
badge = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(badge)
cx, cy, r = u(.685), u(.705), u(.15)
d.ellipse([cx - r - u(.022), cy - r - u(.022), cx + r + u(.022), cy + r + u(.022)], fill=GREEN_LO)
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ORANGE)
tick = [(cx - u(.068), cy + u(.004)), (cx - u(.02), cy + u(.052)), (cx + u(.07), cy - u(.05))]
d.line(tick, fill=(255, 255, 255), width=u(.042), joint='curve')
for px, py in tick: d.ellipse([px - u(.021), py - u(.021), px + u(.021), py + u(.021)], fill=(255, 255, 255))
bshadow = Image.new('RGBA', (S, S), (0, 0, 0, 0)); bshadow.paste((3, 40, 30, 120), (0, u(.018)), badge.split()[3])
bg = Image.alpha_composite(bg, bshadow.filter(ImageFilter.GaussianBlur(u(.018))))
bg = Image.alpha_composite(bg, badge).convert('RGB')

for n in (512, 192, 180):
    bg.resize((n, n), Image.LANCZOS).save(root / 'app' / f'icon-{n}.png', optimize=True)
print('icons written')
