# Generates the Transmitter and Receiver circuit diagrams (SVG + PNG).
# Usage:  pip install cairosvg   (needs the DejaVu Sans font installed)
#         python tools/gen_diagrams.py docs
import html, textwrap, cairosvg

FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"
NAVY = "#1F3A5F"
FILL = "#F4F7FB"
GRAY = "#5B6573"
C = dict(vbat="#B71C1C", vneg="#6D4C41", v5="#EF6C00", v33="#AD1457",
         gnd="#212121", spi="#1565C0", uart="#2E7D32", rf="#6A1B9A", i2c="#00838F")


def esc(s):
    return html.escape(s, quote=False)


class Sheet:
    def __init__(self, w, h):
        self.w, self.h, self.el = w, h, []

    def a(self, s):
        self.el.append(s)

    def rect(self, x, y, w, h, fill="none", stroke=NAVY, sw=2, dash=None, rx=6):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, color, sw=2.6, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{d}/>')

    def wire(self, pts, color, sw=2.8, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.a(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{d}/>')

    def text(self, x, y, t, size=14, weight="normal", fill="#1a1a1a", anchor="start", style="normal"):
        self.a(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" font-style="{style}">{esc(t)}</text>')

    def dot(self, x, y, color, r=4.5):
        self.a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

    def pin(self, x, y, color):
        self.a(f'<circle cx="{x}" cy="{y}" r="5.5" fill="#fff" stroke="{color}" stroke-width="2.4"/>')

    def svg(self):
        body = "\n".join(self.el)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>{body}</svg>')


# ---------- reusable drawing helpers ----------
def part(s, x, y, w, h, title, sub=None, sub2=None, dash=None, fill=FILL, stroke=NAVY, ty=0):
    s.rect(x, y, w, h, fill, stroke, 2.2, dash)
    s.text(x + 14, y + 26 + ty, title, 16, "bold", NAVY)
    if sub:
        s.text(x + 14, y + 46 + ty, sub, 12.5, "normal", GRAY)
    if sub2:
        s.text(x + 14, y + 64 + ty, sub2, 12.5, "normal", GRAY)


def lpin(s, x, y, label, color):  # pin on a left edge, label inside
    s.pin(x, y, color)
    s.text(x + 12, y + 5, label, 14, "bold", "#222")


def rpin(s, x, y, label, color):  # pin on a right edge, label inside
    s.pin(x, y, color)
    s.text(x - 12, y + 5, label, 14, "bold", "#222", "end")


def tpin(s, x, y, label, color):  # pin on a top edge, label inside below
    s.pin(x, y, color)
    s.text(x, y + 24, label, 13.5, "bold", "#222", "middle")


def bpin(s, x, y, label, color):  # pin on a bottom edge, label inside above
    s.pin(x, y, color)
    s.text(x, y - 12, label, 13.5, "bold", "#222", "middle")


def netlabel(s, x, y, t, color, anchor="middle", size=12.5):
    s.text(x, y, t, size, "bold", color, anchor)


def capacitor(s, x, y1, y2, color, label):
    s.dot(x, y1, color)
    s.dot(x, y2, color)
    mid = (y1 + y2) / 2
    s.wire([(x, y1), (x, mid - 6)], color, 2.4)
    s.wire([(x - 15, mid - 6), (x + 15, mid - 6)], "#222", 3.2)
    s.a(f'<path d="M{x-15},{mid+5} Q{x},{mid+17} {x+15},{mid+5}" fill="none" stroke="#222" stroke-width="3.2"/>')
    s.wire([(x, mid + 11), (x, y2)], color, 2.4)
    s.text(x - 22, mid - 6, "+", 15, "bold", "#222", "end")
    s.text(x + 24, mid + 5, label, 14, "bold", "#222")


def antenna(s, x, y, color, l1, l2, side="right"):
    s.wire([(x, y), (x, y + 24)], color, 2.8)
    s.wire([(x - 19, y + 56), (x, y + 24), (x + 19, y + 56)], color, 2.8)
    if side == "right":
        s.text(x + 34, y + 34, l1, 15, "bold", NAVY)
        s.text(x + 34, y + 53, l2, 12.5, "normal", GRAY)
    else:
        s.text(x - 34, y + 34, l1, 15, "bold", NAVY, "end")
        s.text(x - 34, y + 53, l2, 12.5, "normal", GRAY, "end")


def region(s, x, y, w, h, title):
    s.rect(x, y, w, h, "none", "#9AA7B8", 1.6, "9 6", rx=10)
    s.text(x + 16, y + 24, title, 13, "bold", GRAY)


def bom(s, x, y, w, title, cols, rows):
    header_h, row_h = 26, 20
    total_h = 30 + header_h + len(rows) * row_h
    s.rect(x, y, w, 30, NAVY, NAVY, 1, rx=4)
    s.text(x + 14, y + 21, title, 14.5, "bold", "#fff")
    s.rect(x, y + 30, w, header_h, "#DDE6F0", "#9AA7B8", 1, rx=0)
    for cname, cx, canchor in cols:
        s.text(x + cx, y + 48, cname, 12.5, "bold", NAVY, canchor)
    cy = y + 30 + header_h
    for i, r in enumerate(rows):
        fill = "#FFFFFF" if i % 2 else "#F7F9FC"
        s.rect(x, cy, w, row_h, fill, "#D5DCE6", 1, rx=0)
        for (cname, cx, canchor), val in zip(cols, r):
            weight = "bold" if cname == "Ref" else "normal"
            s.text(x + cx, cy + 14.5, val, 12.5, weight, "#1a1a1a", canchor)
        cy += row_h
    s.rect(x, y, w, total_h, "none", NAVY, 1.6, rx=4)


def notes(s, x, y, w, h, items, wrap=44):
    s.rect(x, y, w, h, "#FFFDF5", "#C9B458", 1.6, rx=6)
    s.text(x + 14, y + 26, "BUILD NOTES", 14, "bold", "#7A6A1D")
    cy = y + 52
    for i, itm in enumerate(items, 1):
        s.text(x + 14, cy, f"{i}.", 13.5, "bold", "#7A6A1D")
        for line in textwrap.wrap(itm, width=wrap):
            s.text(x + 34, cy, line, 13.5, "normal", "#222")
            cy += 19
        cy += 7


def legend(s, x, y, w, entries, per_row=4):
    h = 76 if per_row > 4 else 112
    s.rect(x, y, w, h, "#fff", "#9AA7B8", 1.4, rx=6)
    s.text(x + 14, y + 24, "NET COLOUR KEY", 12.5, "bold", GRAY)
    col_w = (w - 40) / per_row
    for i, (label, color, dash) in enumerate(entries):
        col = i % per_row
        row = i // per_row
        lx = x + 14 + col * col_w
        ly = y + 48 + row * 36
        s.line(lx, ly, lx + 36, ly, color, 3.2, dash)
        s.text(lx + 44, ly + 4, label, 13, "normal", "#222")


def titleblock(s, x, y, w, h, title, subtitle, rev, note):
    s.rect(x, y, w, h, "#fff", NAVY, 2, rx=4)
    s.text(x + 16, y + 28, title, 19, "bold", NAVY)
    s.text(x + 16, y + 52, subtitle, 14.5, "bold", "#222")
    s.text(x + 16, y + 74, rev, 13, "normal", GRAY)
    s.text(x + 16, y + 94, note, 13, "normal", GRAY)


# =====================================================================
#  TRANSMITTER
# =====================================================================
def transmitter():
    W, H = 1900, 1360
    s = Sheet(W, H)
    s.rect(10, 10, W - 20, H - 20, "none", "#222", 2.2, rx=2)
    s.text(40, 60, "Project Verona — Romeo (Transmitter) Circuit Diagram", 30, "bold", NAVY)
    s.text(40, 88, "ESP32 Dev Module · Ra-02 SX1278 433 MHz LoRa · u-blox GPS · Li-ion battery with charger, switch and 5 V boost", 15, "normal", GRAY)

    region(s, 40, 110, 900, 340, "POWER SUPPLY")
    region(s, 40, 470, 1440, 730, "CONTROLLER · RADIO · GPS")

    part(s, 60, 170, 170, 150, "BT1  Battery", "Li-ion 3.7 V", "1000 mAh or more")
    s.wire([(88, 266), (132, 266)], "#222", 3.4)
    s.wire([(98, 278), (122, 278)], "#222", 5)
    s.text(146, 270, "+", 15, "bold", "#222")

    part(s, 330, 170, 210, 150, "U4  TP4056", "Type-C charger board", "with battery protection")
    part(s, 350, 370, 170, 64, "J2  USB-C", "5 V charge input")
    part(s, 700, 170, 210, 150, "U5  MT3608", "Boost converter", "set output to 5.0 V")

    part(s, 700, 530, 280, 464, "U1  ESP32 Dev Module", "classic ESP32 · 3.3 V logic", ty=62)
    part(s, 240, 590, 200, 404, "U2  Ra-02 LoRa", "SX1278 · 433 MHz")
    part(s, 1240, 590, 200, 228, "U3  GY-GPS6MV2", "u-blox NEO-6M / NEO-7M")
    part(s, 240, 1034, 200, 60, "J1  Pigtail", "u.FL → SMA bulkhead")

    # power supply wires
    s.wire([(230, 258), (330, 258)], C["vbat"]); netlabel(s, 280, 248, "VBAT+", C["vbat"])
    s.wire([(230, 296), (330, 296)], C["vneg"]); netlabel(s, 280, 286, "VBAT−", C["vneg"])
    s.wire([(435, 370), (435, 320)], C["v5"]); netlabel(s, 447, 352, "VBUS +5 V", C["v5"], "start")
    s.wire([(540, 258), (600, 258)], C["vbat"]); netlabel(s, 570, 248, "VSW_IN", C["vbat"])
    # switch SW1
    s.a(f'<circle cx="600" cy="258" r="5.5" fill="#fff" stroke="{C["vbat"]}" stroke-width="2.4"/>')
    s.wire([(603, 255), (646, 235)], "#222", 3)
    s.a(f'<circle cx="654" cy="258" r="5.5" fill="#fff" stroke="{C["vbat"]}" stroke-width="2.4"/>')
    s.wire([(660, 258), (700, 258)], C["vbat"]); netlabel(s, 680, 279, "VSW_OUT", C["vbat"])
    s.text(618, 196, "SW1  Power switch", 14, "bold", NAVY, "middle")
    s.text(618, 214, "SPST, 1 A or more", 12.5, "normal", GRAY, "middle")
    s.wire([(540, 296), (700, 296)], C["gnd"]); netlabel(s, 620, 316, "GND (OUT−)", C["gnd"])
    # U5 outputs -> D1 -> ESP32
    s.wire([(780, 320), (780, 348)], C["v5"])
    s.wire([(780, 376), (780, 530)], C["v5"])
    s.wire([(840, 320), (840, 530)], C["gnd"])
    # D1 (optional, dashed)
    s.a('<polygon points="767,348 793,348 780,374" fill="#fff" stroke="#78909C" stroke-width="2.2" stroke-dasharray="4 3"/>')
    s.line(767, 376, 793, 376, "#78909C", 2.4, "4 3")
    s.text(760, 360, "D1  1N5819", 13.5, "bold", "#455A64", "end")
    s.text(760, 378, "optional (note 6)", 12, "normal", GRAY, "end")
    netlabel(s, 792, 508, "+5 V", C["v5"], "start", 14)
    netlabel(s, 852, 508, "GND", C["gnd"], "start", 14)
    # RV1 trimmer symbol
    s.rect(861, 262, 34, 12, "#fff", "#444", 1.8, rx=1)
    s.line(864, 294, 894, 260, "#444", 1.8)
    s.a('<polygon points="894,260 884,264 891,270" fill="#444"/>')
    s.text(878, 254, "RV1", 12, "bold", "#444", "middle")

    # --- LoRa <-> ESP32 wires
    rows = [650, 694, 738, 782, 826, 870, 914, 958]
    lora_names = ["3.3V", "GND", "NSS", "RST", "DIO0", "SCK", "MISO", "MOSI"]
    esp_names = ["3V3", "GND", "D5", "D14", "D26", "D18", "D19", "D23"]
    cols = [C["v33"], C["gnd"]] + [C["spi"]] * 6
    nets = ["", "", "LORA_NSS", "LORA_RST", "LORA_DIO0", "LORA_SCK", "LORA_MISO", "LORA_MOSI"]
    for y, c in zip(rows, cols):
        s.wire([(440, y), (700, y)], c)
    netlabel(s, 490, 642, "+3V3", C["v33"])
    netlabel(s, 490, 686, "GND", C["gnd"])
    for y, n, c in zip(rows, nets, cols):
        if n:
            netlabel(s, 570, y - 8, n, c)
    capacitor(s, 560, 650, 694, "#222", "C1  100 µF")
    # --- ESP32 <-> GPS
    grows = rows[:4]
    gcols = [C["v33"], C["gnd"], C["uart"], C["uart"]]
    for y, c in zip(grows, gcols):
        s.wire([(980, y), (1240, y)], c)
    netlabel(s, 1110, 642, "+3V3", C["v33"])
    netlabel(s, 1110, 686, "GND", C["gnd"])
    netlabel(s, 1110, 730, "GPS_TX  →  D32", C["uart"])
    netlabel(s, 1110, 774, "GPS_RX  ←  D33", C["uart"])
    # --- RF
    s.wire([(340, 994), (340, 1034)], C["rf"], 2.8, "7 5")
    s.wire([(340, 1094), (340, 1118)], C["rf"], 2.8, "7 5")
    antenna(s, 340, 1118, C["rf"], "ANT1  433 MHz", "SMA rubber-duck antenna")
    s.wire([(1340, 818), (1340, 880)], C["rf"], 2.8, "7 5")
    netlabel(s, 1352, 852, "u.FL cable", C["rf"], "start")
    antenna(s, 1340, 880, C["rf"], "ANT2  GPS patch", "ceramic antenna, u.FL", "left")

    # --- pins (drawn last)
    rpin(s, 230, 258, "+", C["vbat"]); rpin(s, 230, 296, "−", C["vneg"])
    lpin(s, 330, 258, "B+", C["vbat"]); lpin(s, 330, 296, "B−", C["vneg"])
    rpin(s, 540, 258, "OUT+", C["vbat"]); rpin(s, 540, 296, "OUT−", C["gnd"])
    bpin(s, 435, 320, "5 V in", C["v5"])
    s.pin(435, 370, C["v5"])
    lpin(s, 700, 258, "IN+", C["vbat"]); lpin(s, 700, 296, "IN−", C["gnd"])
    bpin(s, 780, 320, "OUT+", C["v5"]); bpin(s, 840, 320, "OUT−", C["gnd"])
    tpin(s, 780, 530, "VIN", C["v5"]); tpin(s, 840, 530, "GND", C["gnd"])
    for y, ln, en, c in zip(rows, lora_names, esp_names, cols):
        rpin(s, 440, y, ln, c)
        lpin(s, 700, y, en, c)
    for y, n, c in zip(grows, ["3V3", "GND", "D32", "D33"], gcols):
        rpin(s, 980, y, n, c)
    for y, n, c in zip(grows, ["VCC", "GND", "TX", "RX"], gcols):
        lpin(s, 1240, y, n, c)
    bpin(s, 340, 994, "u.FL", C["rf"])
    s.pin(340, 1034, C["rf"]); s.pin(340, 1094, C["rf"])
    bpin(s, 1340, 818, "u.FL", C["rf"])
    s.text(254, 944, "DIO1–DIO5 not used", 12, "normal", GRAY, style="italic")
    s.text(254, 962, "(2.54 mm breakout)", 12, "normal", GRAY, style="italic")
    s.text(1110, 860, "D32 / D33: plain GPIO used as", 11.5, "normal", GRAY, "middle", "italic")
    s.text(1110, 878, "UART2 in software; not the", 11.5, "normal", GRAY, "middle", "italic")
    s.text(1110, 896, "board's RX2 / TX2 pins.", 11.5, "normal", GRAY, "middle", "italic")
    s.text(1110, 914, "Dn = board silkscreen = GPIOn", 11.5, "normal", GRAY, "middle", "italic")

    # --- BOM
    cols_b = [("Ref", 14, "start"), ("Component", 80, "start"), ("Specification", 360, "start"), ("Qty", 846, "end")]
    rowsb = [
        ("BT1", "Li-ion cell", "3.7 V, 1000 mAh or more", "1"),
        ("U4", "TP4056 charger board", "Type-C, with protection (incl. J2)", "1"),
        ("SW1", "Power switch", "SPST, rated 1 A or more", "1"),
        ("U5", "MT3608 boost module", "set to 5.0 V (incl. RV1 trimmer)", "1"),
        ("D1", "Schottky diode (optional)", "1N5819", "1"),
        ("U1", "ESP32 Dev Module", "classic ESP32, 30 or 38 pin", "1"),
        ("U2", "Ra-02 LoRa module", "SX1278, 433 MHz, on breakout board", "1"),
        ("U3", "GPS module", "GY-GPS6MV2, NEO-6M or NEO-7M", "1"),
        ("C1", "Electrolytic capacitor", "100 µF, 10 V or higher", "1"),
        ("J1", "Pigtail cable", "u.FL (IPEX) to SMA-female", "1"),
        ("ANT1", "433 MHz antenna", "SMA rubber-duck", "1"),
        ("ANT2", "GPS patch antenna", "ceramic, u.FL cable (with U3)", "1"),
        ("–", "Breadboard", "full size or two half-size", "1"),
        ("–", "Jumper wires", "male-to-male", "20"),
    ]
    bom(s, 1000, 110, 860, "BILL OF MATERIALS — ROMEO (TRANSMITTER)", cols_b, rowsb)

    # --- notes
    notes(s, 1500, 470, 360, 560, [
        "Set U5 to 5.0 V with a multimeter before connecting it to U1.",
        "Battery − goes to U4 B− only. All load grounds use OUT−. Never join B− and OUT−.",
        "Switch SW1 off while charging through J2.",
        "Fit the 433 MHz antenna to U2 before applying power.",
        "GPS TX goes to D32 and GPS RX to D33 (TX and RX cross over). D32/D33 are ordinary pins, not the board's RX2/TX2.",
        "D1 is optional. If omitted, wire U5 OUT+ straight to VIN. Fit it to allow USB and battery together.",
        "U1 has only two GND pins (one per header, common inside the board). U5's ground uses the one next to VIN; all other grounds use a breadboard − rail tied to the GND pin next to 3V3.",
        "Tags with the same name are one connection: tie every +3V3 tag to one breadboard + rail and every GND tag to the − rail.",
        "U2 and U3 signals are 3.3 V only. Never connect U2 to 5 V.",
    ])

    # --- legend + title block
    legend(s, 40, 1222, 900, [
        ("VBAT+ / switched +", C["vbat"], None), ("VBAT− (battery)", C["vneg"], None),
        ("+5 V", C["v5"], None), ("+3V3", C["v33"], None),
        ("GND", C["gnd"], None), ("SPI / control", C["spi"], None),
        ("UART", C["uart"], None), ("RF cable", C["rf"], "7 5"),
    ])
    titleblock(s, 1320, 1222, 540, 112, "Project Verona",
               "Romeo (Transmitter) — Circuit Diagram",
               "Sheet 1 of 2 · Rev 1.1 · 15 Nov 2026",
               "Board: ESP32 Dev Module · all logic 3.3 V")
    return s


# =====================================================================
#  RECEIVER
# =====================================================================
def receiver():
    W, H = 1700, 1340
    s = Sheet(W, H)
    s.rect(10, 10, W - 20, H - 20, "none", "#222", 2.2, rx=2)
    s.text(40, 60, "Project Verona — Juliet (Receiver / Base) Circuit Diagram", 30, "bold", NAVY)
    s.text(40, 88, "ESP32 Dev Module · Ra-02 SX1278 433 MHz LoRa · 16×2 I2C LCD · powered and read over USB", 15, "normal", GRAY)

    region(s, 640, 110, 380, 300, "COMPUTER AND USB")
    region(s, 40, 430, 980, 730, "CONTROLLER · RADIO")
    region(s, 1100, 480, 400, 350, "DISPLAY")

    part(s, 700, 150, 280, 80, "PC  Computer", "Arduino Serial Monitor, 9600 baud")
    part(s, 700, 300, 280, 70, "J3  USB cable", "micro-USB or USB-C data cable")
    part(s, 700, 470, 280, 464, "U1  ESP32 Dev Module", "classic ESP32 · 3.3 V logic", ty=36)
    part(s, 240, 530, 200, 404, "U2  Ra-02 LoRa", "SX1278 · 433 MHz")
    part(s, 240, 974, 200, 60, "J1  Pigtail", "u.FL → SMA bulkhead")
    part(s, 1180, 530, 240, 228, "U3  LCD 16×2", "HD44780 + I2C backpack")

    # USB wires
    xs = [780, 840, 900]
    uc = [C["v5"], C["gnd"], C["uart"]]
    for x, c in zip(xs, uc):
        s.wire([(x, 230), (x, 300)], c)
        s.wire([(x, 370), (x, 470)], c)
    netlabel(s, 768, 268, "VBUS +5 V", C["v5"], "end")
    netlabel(s, 852, 268, "GND", C["gnd"], "start")
    netlabel(s, 912, 268, "D+ / D−", C["uart"], "start")
    for x, c in zip(xs, uc):
        s.pin(x, 230, c); s.pin(x, 300, c); s.pin(x, 370, c)
    tpin(s, 780, 470, "5V (USB)", C["v5"]); tpin(s, 840, 470, "GND", C["gnd"]); tpin(s, 900, 470, "D± (USB)", C["uart"])
    netlabel(s, 792, 456, "+5 V", C["v5"], "start", 14)
    netlabel(s, 852, 456, "GND", C["gnd"], "start", 14)

    # LoRa wires
    rows = [590, 634, 678, 722, 766, 810, 854, 898]
    lora_names = ["3.3V", "GND", "NSS", "RST", "DIO0", "SCK", "MISO", "MOSI"]
    esp_names = ["3V3", "GND", "D5", "D14", "D26", "D18", "D19", "D23"]
    cols = [C["v33"], C["gnd"]] + [C["spi"]] * 6
    nets = ["", "", "LORA_NSS", "LORA_RST", "LORA_DIO0", "LORA_SCK", "LORA_MISO", "LORA_MOSI"]
    for y, c in zip(rows, cols):
        s.wire([(440, y), (700, y)], c)
    netlabel(s, 490, 582, "+3V3", C["v33"])
    netlabel(s, 490, 626, "GND", C["gnd"])
    for y, n, c in zip(rows, nets, cols):
        if n:
            netlabel(s, 570, y - 8, n, c)
    capacitor(s, 560, 590, 634, "#222", "C1  100 µF")
    for y, ln, en, c in zip(rows, lora_names, esp_names, cols):
        rpin(s, 440, y, ln, c)
        lpin(s, 700, y, en, c)
    s.text(254, 884, "DIO1–DIO5 not used", 12, "normal", GRAY, style="italic")
    s.text(254, 902, "(2.54 mm breakout)", 12, "normal", GRAY, style="italic")

    # LCD wires (I2C)
    lrows = rows[:4]
    lcols = [C["v5"], C["gnd"], C["i2c"], C["i2c"]]
    for y, c in zip(lrows, lcols):
        s.wire([(980, y), (1180, y)], c)
    netlabel(s, 1080, 582, "+5 V (VIN)", C["v5"])
    netlabel(s, 1080, 626, "GND", C["gnd"])
    netlabel(s, 1080, 670, "I2C_SDA", C["i2c"])
    netlabel(s, 1080, 714, "I2C_SCL", C["i2c"])
    for y, n, c in zip(lrows, ["VIN", "GND", "D21", "D22"], lcols):
        rpin(s, 980, y, n, c)
    for y, n, c in zip(lrows, ["VCC", "GND", "SDA", "SCL"], lcols):
        lpin(s, 1180, y, n, c)
    s.text(1300, 790, "Shows Lat on row 1 and Lon on row 2", 12, "normal", GRAY, "middle", "italic")
    s.text(1300, 808, "I2C address 0x27 (or 0x3F)", 12, "normal", GRAY, "middle", "italic")

    s.text(966, 796, "No GPS and no battery. USB 5 V", 11.5, "normal", GRAY, "end", "italic")
    s.text(966, 814, "reaches the VIN pin on the board;", 11.5, "normal", GRAY, "end", "italic")
    s.text(966, 832, "the board makes 3V3 for U2.", 11.5, "normal", GRAY, "end", "italic")
    s.text(966, 850, "Dn = board silkscreen = GPIOn", 11.5, "normal", GRAY, "end", "italic")

    # RF
    s.wire([(340, 934), (340, 974)], C["rf"], 2.8, "7 5")
    s.wire([(340, 1034), (340, 1058)], C["rf"], 2.8, "7 5")
    antenna(s, 340, 1058, C["rf"], "ANT1  433 MHz", "SMA rubber-duck antenna")
    bpin(s, 340, 934, "u.FL", C["rf"]); s.pin(340, 974, C["rf"]); s.pin(340, 1034, C["rf"])

    cols_b = [("Ref", 14, "start"), ("Component", 76, "start"), ("Specification", 300, "start"), ("Qty", 586, "end")]
    rowsb = [
        ("U1", "ESP32 Dev Module", "classic ESP32, 30 or 38 pin", "1"),
        ("U2", "Ra-02 LoRa module", "SX1278, 433 MHz, on breakout board", "1"),
        ("U3", "LCD with I2C backpack", "16x2 HD44780 + PCF8574, 5 V", "1"),
        ("C1", "Electrolytic capacitor", "100 µF, 10 V or higher", "1"),
        ("J1", "Pigtail cable", "u.FL (IPEX) to SMA-female", "1"),
        ("ANT1", "433 MHz antenna", "SMA rubber-duck", "1"),
        ("J3", "USB data cable", "micro-USB or USB-C, to match U1", "1"),
        ("–", "Breadboard", "half-size or larger", "1"),
        ("–", "Jumper wires", "male-to-male (8 LoRa + 4 LCD + spares)", "14"),
    ]
    bom(s, 1060, 110, 600, "BILL OF MATERIALS — JULIET (RECEIVER)", cols_b, rowsb)

    notes(s, 1060, 850, 600, 345, [
        "Wire U2 exactly as on Romeo: the eight connections are identical.",
        "U3 LCD: VCC to VIN (5 V), GND to GND, SDA to D21, SCL to D22.",
        "U1 has only two GND pins (one per header). One serves U2 and C1, the other serves U3. All GND tags are one net: use the breadboard − rail.",
        "Install the LiquidCrystal I2C library and upload juliet.ino.",
        "Blank LCD: try address 0x3F in the sketch and turn the blue contrast screw.",
        "The LCD backpack pulls I2C up to 5 V. A 0.96 inch SSD1306 OLED at 3.3 V is a safer alternative.",
        "Fit the 433 MHz antenna to U2 before connecting USB. U2 is 3.3 V only.",
    ], wrap=62)

    legend(s, 40, 1190, 1000, [
        ("VBUS +5 V", C["v5"], None), ("+3V3", C["v33"], None), ("GND", C["gnd"], None),
        ("SPI / control", C["spi"], None), ("I2C", C["i2c"], None), ("USB data", C["uart"], None),
        ("RF cable", C["rf"], "7 5"),
    ], per_row=7)
    titleblock(s, 1120, 1210, 540, 112, "Project Verona",
               "Juliet (Receiver / Base) — Circuit Diagram",
               "Sheet 2 of 2 · Rev 1.1 · 15 Nov 2026",
               "Board: ESP32 Dev Module · all logic 3.3 V")
    return s


if __name__ == "__main__":
    import os
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "docs"
    os.makedirs(out, exist_ok=True)
    for name, fn in (("Romeo_Circuit_Diagram", transmitter), ("Juliet_Circuit_Diagram", receiver)):
        sh = fn()
        svg = sh.svg()
        with open(os.path.join(out, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=os.path.join(out, name + ".png"), scale=1.5)
        print("wrote", os.path.join(out, name))