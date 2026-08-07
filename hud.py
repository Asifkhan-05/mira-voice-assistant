import sys
import math
import psutil
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QGraphicsOpacityEffect, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
)
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QRadialGradient,
    QLinearGradient, QFont, QPainterPath
)

# ─── Design Tokens ───────────────────────────────────────
BG_HEX       = "#0A0A1A"
GOLD_HEX     = "#C9A84C"
PURPLE_HEX   = "#7B6FD4"
TEXT_HEX     = "#E8DFC8"
MUTED_HEX    = "#5A5A72"

# ─── State Config ────────────────────────────────────────
STATES = {
    "sleeping": {
        "color":    QColor(100, 80, 200),
        "glow":     QColor(80,  60, 180),
        "label":    "SLEEPING",
        "subtitle": "Awaiting your command...",
        "mic":      "Standby",
        "mic_color":"#5A5A72",
    },
    "listening": {
        "color":    QColor(201, 168, 76),
        "glow":     QColor(180, 140, 50),
        "label":    "LISTENING",
        "subtitle": "I'm listening...",
        "mic":      "Active",
        "mic_color": GOLD_HEX,
    },
    "thinking": {
        "color":    QColor(210, 120, 40),
        "glow":     QColor(180,  90, 20),
        "label":    "THINKING",
        "subtitle": "Processing your request...",
        "mic":      "Standby",
        "mic_color":"#5A5A72",
    },
    "speaking": {
        "color":    QColor(160, 180, 230),
        "glow":     QColor(120, 140, 210),
        "label":    "SPEAKING",
        "subtitle": "",
        "mic":      "Standby",
        "mic_color":"#5A5A72",
    },
    "error": {
        "color":    QColor(200, 50, 50),
        "glow":     QColor(160, 30, 30),
        "label":    "ERROR",
        "subtitle": "An error occurred. Please try again.",
        "mic":      "Standby",
        "mic_color":"#5A5A72",
    },
    "completed": {
        "color":    QColor(50, 200, 100),
        "glow":     QColor(30, 160, 70),
        "label":    "COMPLETED",
        "subtitle": "Task completed successfully.",
        "mic":      "Standby",
        "mic_color":"#5A5A72",
    },
}

class AthenaState:
    SLEEPING  = "sleeping"
    LISTENING = "listening"
    THINKING  = "thinking"
    SPEAKING  = "speaking"
    ERROR     = "error"
    COMPLETED = "completed"

# ─── Orb Widget ───────────────────────────────────────────
class OrbWidget(QWidget):
    def __init__(self, size=320):
        super().__init__()
        self.orb_size = size
        total = size + 200
        self.setFixedSize(total, total)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.state        = "sleeping"
        self.cur_color    = QColor(STATES["sleeping"]["color"])
        self.target_color = QColor(STATES["sleeping"]["color"])
        self.cur_glow     = QColor(STATES["sleeping"]["glow"])
        self.target_glow  = QColor(STATES["sleeping"]["glow"])

        self.breath       = 0.0
        self.breath_dir   = 1
        self.breath_speed = 0.004
        self.rotation     = 0.0
        self.ripples      = []
        self.particles    = self._init_particles()
        self.transition   = 1.0

        self._ticker = QTimer()
        self._ticker.timeout.connect(self._tick)
        self._ticker.start(16)

    def _init_particles(self):
        return [
            {
                "angle":  (i / 10) * math.pi * 2,
                "radius": 120 + (i % 3) * 20,
                "speed":  0.004 + (i % 5) * 0.001,
                "size":   2 + (i % 3),
                "alpha":  0.0,
            }
            for i in range(10)
        ]

    def set_state(self, state):
        if state not in STATES:
            return
        self.state        = state
        self.target_color = QColor(STATES[state]["color"])
        self.target_glow  = QColor(STATES[state]["glow"])
        self.transition   = 0.0

        speeds = {
            "sleeping": 0.003, "listening": 0.02,
            "thinking": 0.01,  "speaking":  0.018,
            "error":    0.015, "completed": 0.008
        }
        self.breath_speed = speeds.get(state, 0.006)

        if state in ("listening", "speaking"):
            self.ripples.append({"r": 0.0, "alpha": 0.8})

    @staticmethod
    def _lerp_color(c1, c2, t):
        t = max(0.0, min(1.0, t))
        return QColor(
            int(c1.red()   + (c2.red()   - c1.red())   * t),
            int(c1.green() + (c2.green() - c1.green()) * t),
            int(c1.blue()  + (c2.blue()  - c1.blue())  * t),
        )

    def _tick(self):
        self.breath += self.breath_speed * self.breath_dir
        if self.breath >= 1.0:
            self.breath = 1.0; self.breath_dir = -1
        elif self.breath <= 0.0:
            self.breath = 0.0; self.breath_dir = 1

        if self.transition < 1.0:
            self.transition   += 0.02
            self.cur_color     = self._lerp_color(self.cur_color, self.target_color, 0.05)
            self.cur_glow      = self._lerp_color(self.cur_glow,  self.target_glow,  0.05)

        if self.state == "thinking":
            self.rotation = (self.rotation + 0.8) % 360
            for p in self.particles:
                p["angle"] += p["speed"]
                p["alpha"]  = min(1.0, p["alpha"] + 0.04)
        else:
            for p in self.particles:
                p["alpha"] = max(0.0, p["alpha"] - 0.03)

        new_ripples = []
        for r in self.ripples:
            r["r"]     += 2.0
            r["alpha"] -= 0.008
            if r["alpha"] > 0:
                new_ripples.append(r)
        self.ripples = new_ripples

        if self.state in ("listening", "speaking") and len(self.ripples) < 3:
            if int(self.breath * 100) % 40 == 0:
                self.ripples.append({"r": 0.0, "alpha": 0.5})

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        cx = self.width()  // 2
        cy = self.height() // 2
        c  = self.cur_color
        g  = self.cur_glow
        bs = 0.93 + self.breath * 0.07
        cr = int(self.orb_size // 2 * bs)

        # Ripples
        for rip in self.ripples:
            rr = int(cr + rip["r"] * 3)
            rc = QColor(c.red(), c.green(), c.blue(), int(rip["alpha"] * 50))
            p.setPen(QPen(rc, 1))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(cx - rr, cy - rr, rr*2, rr*2)

        # Outer ambient glow layers
        for i in range(6):
            alpha  = max(0, int((18 - i*2) * (0.5 + self.breath * 0.5)))
            grad_r = cr + 60 + i * 20
            grad   = QRadialGradient(cx, cy, grad_r)
            grad.setColorAt(0.0, QColor(g.red(), g.green(), g.blue(), alpha))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(grad))
            p.drawEllipse(cx - grad_r, cy - grad_r, grad_r*2, grad_r*2)

        # Elliptical orbital rings
        p.save()
        p.translate(cx, cy)
        for i, (rx, ry, alpha) in enumerate([
            (cr + 30, int((cr+30)*0.35), 60),
            (cr + 55, int((cr+55)*0.35), 40),
            (cr + 85, int((cr+85)*0.30), 25),
        ]):
            ring_c = QColor(c.red(), c.green(), c.blue(), alpha)
            p.setPen(QPen(ring_c, 1.0))
            p.setBrush(Qt.NoBrush)
            if self.state == "thinking":
                p.save()
                p.rotate(self.rotation * (0.5 + i * 0.3))
            p.drawEllipse(-rx, -ry, rx*2, ry*2)
            if self.state == "thinking":
                p.restore()
        p.restore()

        # Core orb
        core_grad = QRadialGradient(cx - cr//4, cy - cr//4, cr * 1.3)
        lighter   = QColor(min(255, c.red()+80), min(255, c.green()+80), min(255, c.blue()+80))
        darker    = QColor(max(0, c.red()-60),   max(0, c.green()-60),   max(0, c.blue()-60))
        core_grad.setColorAt(0.0, lighter)
        core_grad.setColorAt(0.5, c)
        core_grad.setColorAt(1.0, darker)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(core_grad))
        p.drawEllipse(cx - cr, cy - cr, cr*2, cr*2)

        # Specular highlight
        hl_r  = cr // 3
        hl_cx = cx - cr // 3
        hl_cy = cy - cr // 3
        hl    = QRadialGradient(hl_cx, hl_cy, hl_r)
        hl.setColorAt(0.0, QColor(255, 255, 255, 130))
        hl.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(QBrush(hl))
        p.drawEllipse(hl_cx - hl_r, hl_cy - hl_r, hl_r*2, hl_r*2)

        # Thinking particles
        for part in self.particles:
            if part["alpha"] < 0.01:
                continue
            px = cx + int(math.cos(part["angle"]) * part["radius"])
            py = cy + int(math.sin(part["angle"]) * part["radius"] * 0.4)
            pc = QColor(c.red(), c.green(), c.blue(), int(part["alpha"] * 200))
            p.setBrush(pc)
            p.setPen(Qt.NoPen)
            r  = int(part["size"])
            p.drawEllipse(px - r, py - r, r*2, r*2)

        p.end()

# ─── Animated Background ─────────────────────────────────
class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.phase = 0.0
        self._t = QTimer()
        self._t.timeout.connect(self._tick)
        self._t.start(50)

    def _tick(self):
        self.phase = (self.phase + 0.002) % (math.pi * 2)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor(10, 10, 26))
        pulse = 0.28 + math.sin(self.phase) * 0.06
        for cx_, cy_, r_factor, col, alpha in [
            (0.5,  0.4,  pulse,  QColor(80, 60, 160), 14),
            (0.15, 0.5,  0.25,   QColor(40, 30, 100),  8),
            (0.85, 0.5,  0.25,   QColor(40, 30, 100),  8),
        ]:
            grad = QRadialGradient(w*cx_, h*cy_, h*r_factor)
            grad.setColorAt(0.0, QColor(col.red(), col.green(), col.blue(), alpha))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.fillRect(0, 0, w, h, QBrush(grad))

# ─── Clock Card ───────────────────────────────────────────
class ClockCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.time_lbl = QLabel("00:00")
        self.time_lbl.setStyleSheet("""
            color: #E8DFC8;
            font-family: 'Segoe UI Light', Arial;
            font-size: 52px;
            font-weight: 200;
            letter-spacing: 2px;
            background: transparent;
        """)

        self.date_lbl = QLabel("")
        self.date_lbl.setStyleSheet("""
            color: #5A5A72;
            font-family: 'Segoe UI', Arial;
            font-size: 11px;
            letter-spacing: 3px;
            background: transparent;
        """)

        layout.addWidget(self.time_lbl)
        layout.addWidget(self.date_lbl)

        self._t = QTimer()
        self._t.timeout.connect(self._update)
        self._t.start(1000)
        self._update()

    def _update(self):
        n = datetime.now()
        self.time_lbl.setText(n.strftime("%H:%M"))
        self.date_lbl.setText(n.strftime("%A, %B %d").upper())

# ─── Weather Card ─────────────────────────────────────────
class WeatherCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignRight)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.setAlignment(Qt.AlignRight)

        self.icon_lbl = QLabel("☀️")
        self.icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")

        right_col = QVBoxLayout()
        right_col.setSpacing(2)

        self.temp_lbl = QLabel("--°C")
        self.temp_lbl.setStyleSheet("""
            color: #E8DFC8;
            font-family: 'Segoe UI Light', Arial;
            font-size: 28px;
            font-weight: 200;
            background: transparent;
        """)

        self.desc_lbl = QLabel("Loading...")
        self.desc_lbl.setStyleSheet("""
            color: #5A5A72;
            font-family: 'Segoe UI', Arial;
            font-size: 11px;
            background: transparent;
        """)

        right_col.addWidget(self.temp_lbl)
        right_col.addWidget(self.desc_lbl)
        row.addLayout(right_col)
        row.addWidget(self.icon_lbl)
        layout.addLayout(row)

        self.city_lbl = QLabel("BENGALURU, IN")
        self.city_lbl.setAlignment(Qt.AlignRight)
        self.city_lbl.setStyleSheet("""
            color: #3A3A52;
            font-family: 'Segoe UI', Arial;
            font-size: 10px;
            letter-spacing: 2px;
            background: transparent;
        """)
        layout.addWidget(self.city_lbl)

        self._fetch()
        self._t = QTimer()
        self._t.timeout.connect(self._fetch)
        self._t.start(600000)

    def _fetch(self):
        try:
            r = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q":"Bengaluru","appid":"3873c793fa5cf1c8e21eabc34e171eef","units":"metric"},
                timeout=5
            )
            d = r.json()
            temp = d["main"]["temp"]
            desc = d["weather"][0]["description"].title()
            main = d["weather"][0]["main"].lower()
            icons = {
                "clear":"☀️","clouds":"☁️","rain":"🌧️",
                "drizzle":"🌦️","thunderstorm":"⛈️","snow":"❄️",
                "mist":"🌫️","fog":"🌫️"
            }
            self.icon_lbl.setText(icons.get(main, "🌤️"))
            self.temp_lbl.setText(f"{temp:.0f}°C")
            self.desc_lbl.setText(desc)
        except:
            self.desc_lbl.setText("Unavailable")

# ─── System Status Card ───────────────────────────────────
class SystemCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,6);
                border: 1px solid rgba(255,255,255,10);
                border-radius: 16px;
            }
            QLabel { background: transparent; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title = QLabel("SYSTEM STATUS")
        title.setStyleSheet("color: #5A5A72; font-family: 'Segoe UI', Arial; font-size: 9px; letter-spacing: 4px;")
        layout.addWidget(title)

        self._bars = {}
        for name, color in [("CPU", "#7B6FD4"), ("RAM", "#7B6FD4"), ("Network", "#C9A84C")]:
            row = QVBoxLayout()
            row.setSpacing(4)
            top = QHBoxLayout()
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("color: #E8DFC8; font-family: 'Segoe UI', Arial; font-size: 11px;")
            val_lbl = QLabel("0%")
            val_lbl.setStyleSheet("color: #E8DFC8; font-family: 'Segoe UI', Arial; font-size: 11px;")
            top.addWidget(name_lbl)
            top.addStretch()
            top.addWidget(val_lbl)
            row.addLayout(top)

            track = QFrame()
            track.setFixedHeight(3)
            track.setStyleSheet("background: rgba(255,255,255,15); border-radius: 2px;")
            fill = QFrame(track)
            fill.setFixedHeight(3)
            fill.setFixedWidth(0)
            fill.setStyleSheet(f"background: {color}; border-radius: 2px;")
            row.addWidget(track)
            layout.addLayout(row)
            self._bars[name] = (val_lbl, fill, track)

        # Microphone row
        mic_row = QHBoxLayout()
        mic_lbl = QLabel("● Microphone")
        mic_lbl.setStyleSheet("color: #5A5A72; font-family: 'Segoe UI', Arial; font-size: 11px;")
        self.mic_status = QLabel("Standby")
        self.mic_status.setStyleSheet("color: #5A5A72; font-family: 'Segoe UI', Arial; font-size: 11px;")
        mic_row.addWidget(mic_lbl)
        mic_row.addStretch()
        mic_row.addWidget(self.mic_status)
        layout.addLayout(mic_row)

        self._t = QTimer()
        self._t.timeout.connect(self._update)
        self._t.start(1000)
        self._update()

    def _update(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        net = psutil.net_io_counters()
        net_mb = (net.bytes_sent + net.bytes_recv) / 1024 / 1024

        for key, val, pct in [("CPU", f"{cpu:.0f}%", cpu),
                               ("RAM", f"{ram:.0f}%", ram),
                               ("Network", f"{net_mb:.1f} MB/s", min(100, net_mb))]:
            val_lbl, fill, track = self._bars[key]
            val_lbl.setText(val)
            w = max(2, int(track.width() * pct / 100))
            fill.setFixedWidth(w)

    def set_mic(self, status, color):
        self.mic_status.setText(status)
        self.mic_status.setStyleSheet(f"color: {color}; font-family: 'Segoe UI', Arial; font-size: 11px;")

# ─── Chat Bubble ─────────────────────────────────────────
class ChatBubble(QFrame):
    def __init__(self, role, text, time_str=""):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(2)

        bubble = QFrame()
        if role == "user":
            bubble.setStyleSheet("""
                QFrame {
                    background: rgba(255,255,255,8);
                    border: 1px solid rgba(255,255,255,12);
                    border-radius: 12px;
                    border-bottom-right-radius: 4px;
                }
                QLabel { background: transparent; }
            """)
        else:
            bubble.setStyleSheet("""
                QFrame {
                    background: rgba(123,111,212,20);
                    border: 1px solid rgba(123,111,212,40);
                    border-radius: 12px;
                    border-bottom-left-radius: 4px;
                }
                QLabel { background: transparent; }
            """)

        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(12, 10, 12, 10)
        text_lbl = QLabel(text)
        text_lbl.setWordWrap(True)
        text_lbl.setStyleSheet("color: #E8DFC8; font-family: 'Segoe UI', Arial; font-size: 12px; background: transparent;")
        b_layout.addWidget(text_lbl)

        row = QHBoxLayout()
        dot = QLabel("●")
        if role == "user":
            dot.setStyleSheet(f"color: {GOLD_HEX}; font-size: 8px; background: transparent;")
            row.addStretch()
            row.addWidget(bubble)
            row.addWidget(dot)
        else:
            dot.setStyleSheet(f"color: {PURPLE_HEX}; font-size: 8px; background: transparent;")
            row.addWidget(dot)
            row.addWidget(bubble)
            row.addStretch()
        outer.addLayout(row)

        if time_str:
            time_lbl = QLabel(f"{'You' if role == 'user' else 'Athena'} · {time_str}")
            align = Qt.AlignRight if role == "user" else Qt.AlignLeft
            margin = "margin-right: 16px;" if role == "user" else "margin-left: 16px;"
            time_lbl.setStyleSheet(f"color: #3A3A52; font-size: 9px; background: transparent; {margin}")
            time_lbl.setAlignment(align)
            outer.addWidget(time_lbl)

        # Fade in
        eff  = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(eff)
        eff.setOpacity(0)
        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.start()
        self._anim = anim

# ─── History Panel ────────────────────────────────────────
class HistoryPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,6);
                border: 1px solid rgba(255,255,255,10);
                border-radius: 16px;
            }
            QLabel { background: transparent; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        tab_row = QHBoxLayout()
        hist = QLabel("HISTORY")
        hist.setStyleSheet(f"color: {GOLD_HEX}; font-size: 10px; letter-spacing: 3px;")
        sep = QLabel("|")
        sep.setStyleSheet("color: #3A3A52; font-size: 10px;")
        mem = QLabel("MEMORY")
        mem.setStyleSheet("color: #3A3A52; font-size: 10px; letter-spacing: 3px;")
        tab_row.addWidget(hist)
        tab_row.addWidget(sep)
        tab_row.addWidget(mem)
        tab_row.addStretch()
        layout.addLayout(tab_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QWidget     { background: transparent; }
            QScrollBar:vertical { width: 3px; background: transparent; }
            QScrollBar::handle:vertical { background: rgba(201,168,76,50); border-radius: 1px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        self.inner = QWidget()
        self.inner.setStyleSheet("background: transparent;")
        self.inner_layout = QVBoxLayout(self.inner)
        self.inner_layout.setSpacing(8)
        self.inner_layout.setContentsMargins(0, 0, 4, 0)
        self.inner_layout.addStretch()
        self.scroll.setWidget(self.inner)
        layout.addWidget(self.scroll)

    def add_message(self, role, text):
        time_str = datetime.now().strftime("%H:%M")
        bubble   = ChatBubble(role, text, time_str)
        self.inner_layout.insertWidget(self.inner_layout.count() - 1, bubble)
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

# ─── Startup Overlay ─────────────────────────────────────
class StartupOverlay(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(14)

        title = QLabel("A T H E N A")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {GOLD_HEX};
            font-family: 'Segoe UI Light', Georgia, Arial;
            font-size: 42px;
            font-weight: 200;
            letter-spacing: 16px;
            background: transparent;
        """)
        sub = QLabel("Wisdom  ·  Strategy  ·  Intelligence")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"""
            color: rgba(201,168,76,100);
            font-family: 'Segoe UI', Georgia, Arial;
            font-size: 12px;
            letter-spacing: 5px;
            font-style: italic;
            background: transparent;
        """)
        layout.addWidget(title)
        layout.addWidget(sub)

        self._eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._eff)
        self._eff.setOpacity(0.0)

        self._in = QPropertyAnimation(self._eff, b"opacity")
        self._in.setDuration(1400)
        self._in.setStartValue(0.0)
        self._in.setEndValue(1.0)
        self._in.setEasingCurve(QEasingCurve.InOutCubic)
        self._in.finished.connect(lambda: QTimer.singleShot(1000, self._fadeout))
        self._in.start()

    def _fadeout(self):
        self._out = QPropertyAnimation(self._eff, b"opacity")
        self._out.setDuration(900)
        self._out.setStartValue(1.0)
        self._out.setEndValue(0.0)
        self._out.setEasingCurve(QEasingCurve.InOutCubic)
        self._out.finished.connect(self._done)
        self._out.start()

    def _done(self):
        self.hide()
        self.finished.emit()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(10, 10, 26, 240))

# ─── Main HUD ─────────────────────────────────────────────
class AthenaHUD(QWidget):
    update_state_signal    = pyqtSignal(str)
    update_response_signal = pyqtSignal(str)
    update_user_signal     = pyqtSignal(str)

    MODE_FULL    = "full"
    MODE_COMPACT = "compact"
    MODE_MINIMAL = "minimal"

    def __init__(self):
        super().__init__()
        self.mode          = self.MODE_FULL
        self.screen        = QApplication.primaryScreen().geometry()
        self._drag         = None
        self.history_panel = None
        self.system_card   = None
        self.orb           = None
        self.state_lbl     = None
        self.subtitle_lbl  = None
        self.state_dot     = None
        self.cur_state     = "sleeping"
        self._switching    = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.update_state_signal.connect(self._set_state)
        self.update_response_signal.connect(self._on_response)
        self.update_user_signal.connect(self._on_user)

        self._build()

    # ── Mode switching — safe version ─────────────────────
    def switch_mode(self, mode):
        if self._switching:
            return
        self._switching = True
        self.mode = mode
        # Step 1: hide everything immediately
        for child in self.findChildren(QWidget):
            try:
                child.hide()
            except:
                pass
        # Step 2: rebuild after click event fully completes
        QTimer.singleShot(200, self._do_rebuild)

    def _do_rebuild(self):
        # Step 3: safely delete all children
        for child in self.findChildren(QWidget):
            try:
                child.deleteLater()
            except:
                pass
        self.history_panel = None
        self.system_card   = None
        self.orb           = None
        self.state_lbl     = None
        self.subtitle_lbl  = None
        self.state_dot     = None
        # Step 4: rebuild and show
        QTimer.singleShot(100, self._finish_rebuild)

    def _finish_rebuild(self):
        self._build()
        self.show()
        self.raise_()
        self.activateWindow()
        self._switching = False

    # ── Build ──────────────────────────────────────────────
    def _build(self):
        if self.mode == self.MODE_FULL:
            self._build_full()
        elif self.mode == self.MODE_COMPACT:
            self._build_compact()
        else:
            self._build_minimal()

    def _make_btn(self, symbol, mode, parent=None):
        btn = QLabel(symbol, parent)
        btn.setStyleSheet(f"color: rgba(201,168,76,80); font-size: 16px; background: transparent;")
        btn.setCursor(Qt.PointingHandCursor)
        def _enter(e): btn.setStyleSheet(f"color: {GOLD_HEX}; font-size: 16px; background: transparent;")
        def _leave(e): btn.setStyleSheet(f"color: rgba(201,168,76,80); font-size: 16px; background: transparent;")
        btn.enterEvent      = _enter
        btn.leaveEvent      = _leave
        btn.mousePressEvent = lambda e, m=mode: self.switch_mode(m)
        return btn

    def _build_full(self):
        sw, sh = self.screen.width(), self.screen.height()
        self.setGeometry(0, 0, sw, sh)

        self.bg = BackgroundWidget(self)
        self.bg.setGeometry(0, 0, sw, sh)
        self.bg.lower()

        pad = 30

        self.clock = ClockCard()
        self.clock.setParent(self)
        self.clock.setGeometry(pad, pad, 280, 90)

        self.weather_card = WeatherCard()
        self.weather_card.setParent(self)
        self.weather_card.setGeometry(sw - 220 - pad, pad, 220, 90)

        self.system_card = SystemCard()
        self.system_card.setParent(self)
        self.system_card.setGeometry(pad, sh - 240 - pad, 280, 240)

        self.history_panel = HistoryPanel()
        self.history_panel.setParent(self)
        self.history_panel.setGeometry(sw - 340 - pad, sh//2 - 50, 340, sh//2 + 20)

        self.orb = OrbWidget(size=280)
        self.orb.setParent(self)
        orb_w = self.orb.width()
        orb_h = self.orb.height()
        self.orb.move(sw//2 - orb_w//2, sh//2 - orb_h//2 - 40)
        self.orb.set_state(self.cur_state)

        athena_lbl = QLabel("A T H E N A", self)
        athena_lbl.setAlignment(Qt.AlignCenter)
        athena_lbl.setStyleSheet(f"""
            color: rgba(201,168,76,180);
            font-family: 'Segoe UI Light', Georgia, Arial;
            font-size: 13px;
            letter-spacing: 10px;
            background: transparent;
        """)
        athena_lbl.setGeometry(sw//2 - 160, sh//2 - orb_h//2 - 80, 320, 28)

        state_row_y = sh//2 + orb_h//2 - 60

        self.state_dot = QLabel("●", self)
        self.state_dot.setStyleSheet(f"color: {PURPLE_HEX}; font-size: 8px; background: transparent;")
        self.state_dot.setGeometry(sw//2 - 70, state_row_y, 16, 20)

        self.state_lbl = QLabel("SLEEPING", self)
        self.state_lbl.setStyleSheet(f"""
            color: {PURPLE_HEX};
            font-family: 'Segoe UI', Arial;
            font-size: 11px;
            letter-spacing: 5px;
            background: transparent;
        """)
        self.state_lbl.setGeometry(sw//2 - 50, state_row_y, 200, 20)

        self.subtitle_lbl = QLabel("Awaiting your command...", self)
        self.subtitle_lbl.setAlignment(Qt.AlignCenter)
        self.subtitle_lbl.setStyleSheet(f"""
            color: #5A5A72;
            font-family: 'Segoe UI', Arial;
            font-size: 12px;
            font-style: italic;
            background: transparent;
        """)
        self.subtitle_lbl.setGeometry(sw//2 - 250, state_row_y + 28, 500, 24)

        # Mode buttons — created last so they're on top
        b1 = self._make_btn("⊟", self.MODE_COMPACT, self)
        b2 = self._make_btn("◎", self.MODE_MINIMAL, self)
        b1.setGeometry(sw - 60, 16, 24, 24)
        b2.setGeometry(sw - 34, 16, 24, 24)
        b1.show()
        b2.show()
        b1.raise_()
        b2.raise_()

        # Show all children
        for child in self.findChildren(QWidget):
            child.show()

        # Startup overlay on top
        self.startup = StartupOverlay(self)
        self.startup.setGeometry(0, 0, sw, sh)
        self.startup.raise_()
        self.startup.show()

        # Re-raise buttons after startup finishes
        self.startup.finished.connect(lambda: [b1.raise_(), b2.raise_()])

        # Apply current state
        self._set_state(self.cur_state)

    def _build_compact(self):
        w, h = 320, 600
        self.setGeometry(20, 20, w, h)

        cont = QFrame(self)
        cont.setGeometry(0, 0, w, h)
        cont.setStyleSheet("""
            QFrame {
                background: rgba(10,10,26,235);
                border: 1px solid rgba(255,255,255,12);
                border-radius: 20px;
            }
            QLabel { background: transparent; }
        """)

        layout = QVBoxLayout(cont)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        hdr = QHBoxLayout()
        self.orb = OrbWidget(size=50)
        self.orb.set_state(self.cur_state)

        self.state_lbl = QLabel("SLEEPING")
        self.state_lbl.setStyleSheet(f"color: {PURPLE_HEX}; font-size: 9px; letter-spacing: 2px;")
        name = QLabel("ATHENA")
        name.setStyleSheet(f"color: {GOLD_HEX}; font-size: 18px; letter-spacing: 5px;")
        col = QVBoxLayout()
        col.addWidget(name)
        col.addWidget(self.state_lbl)

        btns = QHBoxLayout()
        btns.addWidget(self._make_btn("⊞", self.MODE_FULL))
        btns.addWidget(self._make_btn("◎", self.MODE_MINIMAL))
        hdr.addWidget(self.orb)
        hdr.addLayout(col)
        hdr.addStretch()
        hdr.addLayout(btns)
        layout.addLayout(hdr)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color: rgba(255,255,255,10);")
        layout.addWidget(div)

        self.clock        = ClockCard()
        self.weather_card = WeatherCard()
        self.system_card  = SystemCard()
        self.history_panel = HistoryPanel()
        self.history_panel.setMinimumHeight(180)

        for widget in (self.clock, self.weather_card, self.system_card, self.history_panel):
            layout.addWidget(widget)

        self.subtitle_lbl = None
        self.state_dot    = None
        self._set_state(self.cur_state)

    def _build_minimal(self):
        w, h = 220, 64
        self.setGeometry(20, 20, w, h)

        cont = QFrame(self)
        cont.setGeometry(0, 0, w, h)
        cont.setStyleSheet("""
            QFrame {
                background: rgba(10,10,26,235);
                border: 1px solid rgba(255,255,255,12);
                border-radius: 32px;
            }
            QLabel { background: transparent; }
        """)

        layout = QHBoxLayout(cont)
        layout.setContentsMargins(10, 8, 14, 8)
        layout.setSpacing(10)

        self.orb = OrbWidget(size=44)
        self.orb.set_state(self.cur_state)

        self.state_lbl = QLabel("SLEEPING")
        self.state_lbl.setStyleSheet(f"color: {PURPLE_HEX}; font-size: 8px; letter-spacing: 2px;")
        name = QLabel("ATHENA")
        name.setStyleSheet(f"color: {GOLD_HEX}; font-size: 13px; letter-spacing: 3px;")
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(name)
        col.addWidget(self.state_lbl)

        expand = self._make_btn("⊟", self.MODE_COMPACT)
        layout.addWidget(self.orb)
        layout.addLayout(col)
        layout.addStretch()
        layout.addWidget(expand)

        self.history_panel = None
        self.system_card   = None
        self.subtitle_lbl  = None
        self.state_dot     = None
        self._set_state(self.cur_state)

    # ── State ─────────────────────────────────────────────
    def _set_state(self, state):
        self.cur_state = state
        cfg = STATES.get(state, STATES["sleeping"])

        if self.orb:
            self.orb.set_state(state)

        colors = {
            "sleeping":  PURPLE_HEX,
            "listening": GOLD_HEX,
            "thinking":  "#D07828",
            "speaking":  "#A0B4E6",
            "error":     "#C83232",
            "completed": "#32C864",
        }
        color = colors.get(state, PURPLE_HEX)
        bg    = "background: transparent;" if self.mode == self.MODE_FULL else ""

        if self.state_lbl:
            self.state_lbl.setText(cfg["label"])
            self.state_lbl.setStyleSheet(
                f"color: {color}; font-family: 'Segoe UI', Arial; font-size: 11px; letter-spacing: 5px; {bg}"
            )

        if self.state_dot:
            self.state_dot.setStyleSheet(f"color: {color}; font-size: 8px; background: transparent;")

        if self.subtitle_lbl:
            self.subtitle_lbl.setText(cfg["subtitle"])

        if self.system_card:
            self.system_card.set_mic(cfg["mic"], cfg["mic_color"])

    def _on_user(self, text):
        if self.history_panel:
            self.history_panel.add_message("user", text)

    def _on_response(self, text):
        if self.history_panel:
            self.history_panel.add_message("athena", text)
        if self.subtitle_lbl and self.cur_state == "speaking":
            short = text[:80] + "..." if len(text) > 80 else text
            self.subtitle_lbl.setText(short)

    # ── Drag ──────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.mode != self.MODE_FULL:
            self._drag = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag and self.mode != self.MODE_FULL:
            self.move(event.globalPos() - self._drag)

# ─── Runner ───────────────────────────────────────────────
_hud = None

def start_hud():
    global _hud
    app = QApplication.instance() or QApplication(sys.argv)
    _hud = AthenaHUD()
    _hud.show()
    return app, _hud

def get_hud():
    return _hud