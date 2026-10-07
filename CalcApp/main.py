"""
NumberX — умный калькулятор под Android.
Сборка: GitHub Actions + buildozer.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.resources import resource_find
import math
import re
import os

# ============ ЦВЕТА ============
BG      = (0.09, 0.09, 0.13, 1)
CARD    = (0.15, 0.15, 0.22, 1)
ACCENT  = (0.55, 0.36, 0.96, 1)
ACCENT2 = (0.42, 0.25, 0.80, 1)
TEXT    = (1, 1, 1, 1)
MUTED   = (0.6, 0.6, 0.7, 1)

# ============ ПУТИ К КАРТИНКАМ ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DPS_PATH = os.path.join(BASE_DIR, "dps.png")

if not os.path.exists(DPS_PATH):
    found = resource_find("dps.png")
    if found:
        DPS_PATH = found


# ============ ВИДЖЕТЫ ============
class RoundButton(Button):
    def __init__(self, bg=ACCENT, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self._color = Color(*bg)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(14)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


def bg_rect(widget, color=BG):
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda *a: setattr(rect, "pos", widget.pos),
                size=lambda *a: setattr(rect, "size", widget.size))
    return rect


def make_button(text, bg=ACCENT, height=dp(55), on_press=None, font_size=dp(17)):
    b = RoundButton(text=text, bg=bg, size_hint=(1, None), height=height,
                    font_size=font_size, color=TEXT, bold=True)
    if on_press:
        b.bind(on_press=on_press)
    return b


# ============ МИНИ-НЕЙРОНКА ============
class MiniNeural:
    """NumberX AI — офлайн мини-ИИ на правилах."""
    def __init__(self):
        self.name = "NumberX AI v1.0"

    def respond(self, text):
        text = text.strip().lower()
        if not text:
            return "Напиши что-нибудь, брат 🙂"

        # Линейное уравнение: 2x+5=11
        compact = text.replace(" ", "")
        m = re.match(r"^(-?\d*)x([+-]\d+)?=(-?\d+)$", compact)
        if m:
            try:
                a = m.group(1)
                a = -1 if a == "-" else (1 if a in ("", "+") else float(a))
                b = float(m.group(2)) if m.group(2) else 0
                c = float(m.group(3))
                x = (c - b) / a
                return f"Уравнение: {a}x + {b} = {c}\nРешение: x = {x:.4f}"
            except Exception:
                pass

        # Разбор числа
        if text.replace(".", "").replace("-", "").isdigit():
            n = float(text)
            out = [f"Число: {n}"]
            if n == int(n):
                out.append(f"Целое: {int(n)}")
                out.append("Чётное" if int(n) % 2 == 0 else "Нечётное")
            out.append(f"Квадрат: {n ** 2}")
            if n >= 0:
                out.append(f"√: {math.sqrt(n):.4f}")
            return "\n".join(out)

        # Приветствия
        if any(w in text for w in ["привет", "хай", "hello", "здарова"]):
            return (f"Здарова! Я {self.name}.\n"
                    "Умею: 2x+5=11, разбор числа, любые выражения.")

        # Прямой расчёт
        try:
            allowed = {k: getattr(math, k) for k in dir(math)
                       if not k.startswith("_")}
            allowed.update({"abs": abs, "round": round})
            val = eval(text.replace("^", "**"), {"__builtins__": {}}, allowed)
            return f"{text} = {val}"
        except Exception:
            pass

        return (f"Я {self.name}. Примеры:\n"
                "• 2x+5=11\n• 144\n• привет\n• (2+3)*4")


neural = MiniNeural()


# ============ ЭКРАН МЕНЮ ============
class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        bg_rect(root, BG)

        root.add_widget(Label(text="[b]NumberX[/b]", markup=True,
                              font_size=dp(36), color=ACCENT,
                              size_hint_y=None, height=dp(70)))

        root.add_widget(Label(text="Умный калькулятор", font_size=dp(14),
                              color=MUTED, size_hint_y=None, height=dp(25)))

        root.add_widget(Label(size_hint_y=None, height=dp(10)))

        items = [
            ("🧮  Выражения (со скобками)", "expr"),
            ("🔢  Простой калькулятор", "simple"),
            ("📐  Задачи", "tasks"),
            ("🤖  Мини-нейронка", "neural"),
            ("ℹ️  О программе", "about"),
        ]
        for text, scr in items:
            root.add_widget(make_button(
                text, bg=CARD, font_size=dp(16),
                on_press=lambda x, s=scr: self.go(s)))

        root.add_widget(Label(size_hint_y=None, height=dp(5)))
        root.add_widget(Label(text="Powered by [b]NumberX Team[/b]",
                              markup=True, font_size=dp(13), color=MUTED,
                              size_hint_y=None, height=dp(25)))
        self.add_widget(root)

    def go(self, screen):
        self.manager.current = screen


# ============ БАЗОВЫЙ ЭКРАН ============
class BaseScreen(Screen):
    title = ""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.root = BoxLayout(orientation="vertical")
        bg_rect(self.root, BG)

        header = BoxLayout(size_hint_y=None, height=dp(55),
                           padding=[dp(10), dp(5)], spacing=dp(8))
        back = RoundButton(text="←", bg=CARD, size_hint=(None, 1),
                           width=dp(50), font_size=dp(24), color=TEXT)
        back.bind(on_press=lambda x: self.back())
        header.add_widget(back)
        header.add_widget(Label(text=f"[b]{self.title}[/b]", markup=True,
                                font_size=dp(20), color=TEXT))
        self.root.add_widget(header)

        self.body = BoxLayout(orientation="vertical",
                              padding=dp(15), spacing=dp(10))
        self.root.add_widget(self.body)
        self.add_widget(self.root)

    def back(self):
        self.manager.current = "menu"


# ============ ВЫРАЖЕНИЯ ============
class ExprScreen(BaseScreen):
    title = "Выражения"

    def __init__(self, **kw):
        super().__init__(**kw)

        self.field = TextInput(
            hint_text="(2+3)*4 - sin(0.5) + sqrt(16)",
            multiline=False, size_hint_y=None, height=dp(55),
            font_size=dp(17), background_color=CARD,
            foreground_color=TEXT, cursor_color=ACCENT,
            padding=[dp(12), dp(12)])
        self.body.add_widget(self.field)

        self.body.add_widget(make_button("Вычислить", bg=ACCENT,
                                         on_press=self.calc))

        self.result = Label(text="Результат появится здесь",
                            font_size=dp(16), color=MUTED, halign="center")
        self.result.bind(size=lambda *a: setattr(
            self.result, "text_size", self.result.size))
        self.body.add_widget(self.result)

    def calc(self, *_):
        expr = self.field.text.strip()
        if not expr:
            self.result.text = "Введи выражение"
            return
        try:
            allowed = {k: getattr(math, k) for k in dir(math)
                       if not k.startswith("_")}
            allowed.update({"abs": abs, "round": round, "min": min, "max": max})
            val = eval(expr.replace("^", "**"),
                       {"__builtins__": {}}, allowed)
            self.result.text = f"{expr} = {val}"
            self.result.color = TEXT
        except Exception as e:
            self.result.text = f"Ошибка: {e}"
            self.result.color = (1, 0.4, 0.4, 1)


# ============ КАЛЬКУЛЯТОР ============
class SimpleScreen(BaseScreen):
    title = "Калькулятор"

    def __init__(self, **kw):
        super().__init__(**kw)
        self.expr = ""

        self.display = Label(text="0", font_size=dp(36), color=TEXT,
                             halign="right", valign="middle",
                             size_hint_y=None, height=dp(85))
        self.display.bind(size=lambda *a: setattr(
            self.display, "text_size", self.display.size))
        self.body.add_widget(self.display)

        grid = GridLayout(cols=4, spacing=dp(6))
        keys = [
            ("C", ACCENT2), ("(", CARD), (")", CARD), ("÷", CARD),
            ("7", CARD), ("8", CARD), ("9", CARD), ("×", CARD),
            ("4", CARD), ("5", CARD), ("6", CARD), ("−", CARD),
            ("1", CARD), ("2", CARD), ("3", CARD), ("+", CARD),
            ("0", CARD), (".", CARD), ("=", ACCENT), ("⌫", ACCENT2),
        ]
        for k, c in keys:
            grid.add_widget(make_button(
                k, bg=c, font_size=dp(22),
                on_press=lambda x, key=k: self.press(key)))
        self.body.add_widget(grid)

    def press(self, k):
        if k == "C":
            self.expr = ""
        elif k == "⌫":
            self.expr = self.expr[:-1]
        elif k == "=":
            try:
                e = self.expr.replace("×", "*").replace("÷", "/").replace("−", "-")
                allowed = {n: getattr(math, n) for n in dir(math)
                           if not n.startswith("_")}
                self.expr = str(eval(e, {"__builtins__": {}}, allowed))
            except Exception:
                self.expr = "Ошибка"
        else:
            if self.expr == "Ошибка":
                self.expr = ""
            self.expr += k
        self.display.text = self.expr or "0"


# ============ ЗАДАЧИ ============
class TasksScreen(BaseScreen):
    title = "Задачи"

    TASKS = [
        ("Площадь круга  S = π·r²", "Радиус", "r",
         lambda d: f"S = {math.pi * float(d['r']) ** 2:.4f}"),
        ("Периметр прямоуг.  P = 2(a+b)", "a,b через запятую", "k",
         lambda d: f"P = {2 * sum(float(x) for x in d['k'].split(',')):.4f}"),
        ("Гипотенуза  c = √(a²+b²)", "a,b через запятую", "k",
         lambda d: f"c = {math.hypot(*map(float, d['k'].split(','))):.4f}"),
        ("Квадратное  ax²+bx+c=0", "a,b,c через запятую", "k",
         lambda d: TasksScreen._quad(d['k'])),
        ("Среднее  avg = Σ/n", "Числа через запятую", "k",
         lambda d: f"avg = {sum(map(float, d['k'].split(','))) / len(d['k'].split(',')):.4f}"),
    ]

    @staticmethod
    def _quad(s):
        a, b, c = map(float, s.split(","))
        d = b * b - 4 * a * c
        if d < 0:
            return f"D = {d}\nКорней нет"
        x1 = (-b + math.sqrt(d)) / (2 * a)
        x2 = (-b - math.sqrt(d)) / (2 * a)
        return f"D = {d}\nx₁ = {x1:.4f}\nx₂ = {x2:.4f}"

    def __init__(self, **kw):
        super().__init__(**kw)
        scroll = ScrollView()
        lst = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        lst.bind(minimum_height=lst.setter("height"))

        for name, hint, key, fn in self.TASKS:
            lst.add_widget(make_button(
                name, bg=CARD, height=dp(65), font_size=dp(15),
                on_press=lambda x, n=name, h=hint, k=key, f=fn:
                    self.open_task(n, h, k, f)))

        scroll.add_widget(lst)
        self.body.add_widget(scroll)

    def open_task(self, name, hint, key, fn):
        box = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        box.add_widget(Label(text=hint, font_size=dp(15), color=TEXT,
                             size_hint_y=None, height=dp(30)))
        field = TextInput(multiline=False, size_hint_y=None, height=dp(50),
                          font_size=dp(16), background_color=CARD,
                          foreground_color=TEXT, cursor_color=ACCENT,
                          padding=[dp(10), dp(10)])
        box.add_widget(field)

        popup = Popup(title=name, content=box, size_hint=(0.9, 0.5),
                      background_color=BG, title_color=TEXT,
                      separator_color=ACCENT)

        def solve(*_):
            try:
                res = fn({key: field.text})
                popup.dismiss()
                self.show_popup("Результат", res)
            except Exception as e:
                popup.dismiss()
                self.show_popup("Ошибка", str(e))

        box.add_widget(make_button("Решить", bg=ACCENT, on_press=solve))
        popup.open()

    def show_popup(self, title, text):
        box = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        lbl = Label(text=text, font_size=dp(16), color=TEXT, halign="center")
        lbl.bind(size=lambda *a: setattr(lbl, "text_size", lbl.size))
        box.add_widget(lbl)
        popup = Popup(title=title, content=box, size_hint=(0.85, 0.4),
                      background_color=BG, title_color=TEXT,
                      separator_color=ACCENT)
        box.add_widget(make_button("OK", bg=ACCENT,
                                   on_press=lambda x: popup.dismiss()))
        popup.open()


# ============ НЕЙРОНКА ЭКРАН ============
class NeuralScreen(BaseScreen):
    title = "Мини-нейронка"

    def __init__(self, **kw):
        super().__init__(**kw)

        scroll = ScrollView()
        self.chat = Label(
            text=f"[i]{neural.name} готов. Напиши запрос.[/i]\n",
            markup=True, font_size=dp(15), color=TEXT,
            halign="left", valign="top", size_hint_y=None)
        self.chat.bind(
            width=lambda *a: setattr(self.chat, "text_size",
                                     (self.chat.width - dp(20), None)),
            texture_size=lambda *a: setattr(self.chat, "height",
                                            self.chat.texture_size[1]))
        scroll.add_widget(self.chat)
        self._scroll = scroll
        self.body.add_widget(scroll)

        row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(6))
        self.field = TextInput(hint_text="Сообщение...", multiline=False,
                               font_size=dp(15), background_color=CARD,
                               foreground_color=TEXT, cursor_color=ACCENT,
                               padding=[dp(10), dp(12)])
        self.field.bind(on_text_validate=self.send)
        row.add_widget(self.field)

        send_btn = RoundButton(text="➤", bg=ACCENT, size_hint=(None, 1),
                               width=dp(55), font_size=dp(20), color=TEXT)
        send_btn.bind(on_press=self.send)
        row.add_widget(send_btn)
        self.body.add_widget(row)

    def send(self, *_):
        msg = self.field.text.strip()
        if not msg:
            return
        self.field.text = ""
        reply = neural.respond(msg)
        self.chat.text += f"\n[b]Ты:[/b] {msg}\n[b]AI:[/b] {reply}\n"
        Clock.schedule_once(lambda dt: setattr(self._scroll, "scroll_y", 0), 0.1)


# ============ О ПРОГРАММЕ ============
class AboutScreen(BaseScreen):
    title = "О программе"

    def __init__(self, **kw):
        super().__init__(**kw)
        lbl = Label(
            text="[b]NumberX[/b]\n\n"
                 "Версия: 1.0.0\n"
                 "Умный калькулятор с мини-ИИ\n\n"
                 "Движок: Kivy\n"
                 "Мини-ИИ: NumberX AI v1.0\n\n"
                 "[i]Powered by NumberX Team[/i]",
            markup=True, font_size=dp(17), color=TEXT, halign="center")
        lbl.bind(size=lambda *a: setattr(lbl, "text_size", lbl.size))
        self.body.add_widget(lbl)


# ============ ПРИЛОЖЕНИЕ ============
class CalcApp(App):
    def build(self):
        Window.clearcolor = BG
        self.title = "NumberX"

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(ExprScreen(name="expr"))
        sm.add_widget(SimpleScreen(name="simple"))
        sm.add_widget(TasksScreen(name="tasks"))
        sm.add_widget(NeuralScreen(name="neural"))
        sm.add_widget(AboutScreen(name="about"))

        Clock.schedule_once(self.show_splash, 0.4)
        return sm

    def show_splash(self, dt):
        box = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
        bg_rect(box, CARD)

        # Только dps.png — splash-картинка
        if os.path.exists(DPS_PATH):
            try:
                box.add_widget(Image(source=DPS_PATH, size_hint=(1, None),
                                     height=dp(120), allow_stretch=True,
                                     keep_ratio=True))
            except Exception:
                pass

        box.add_widget(Label(text="Powered by", font_size=dp(15),
                             color=MUTED, size_hint_y=None, height=dp(25)))
        box.add_widget(Label(text="[b]NumberX[/b]", markup=True,
                             font_size=dp(24), color=ACCENT,
                             size_hint_y=None, height=dp(35)))

        popup = Popup(title="", content=box, size_hint=(0.78, 0.55),
                      background_color=BG, separator_color=ACCENT,
                      title_size=0)
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2.3)


if __name__ == "__main__":
    CalcApp().run()