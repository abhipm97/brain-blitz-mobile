from kivy.config import Config
Config.set("graphics", "width", "420")
Config.set("graphics", "height", "820")
Config.set("graphics", "resizable", "1")

import random
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line

# Premium dark palette
BG = (0.035, 0.043, 0.075, 1)
PANEL = (0.075, 0.087, 0.135, 1)
PANEL2 = (0.105, 0.118, 0.18, 1)
PURPLE = (0.49, 0.32, 1, 1)
PURPLE_DARK = (0.29, 0.19, 0.68, 1)
GREEN = (0.20, 0.88, 0.61, 1)
RED = (1, 0.31, 0.42, 1)
WHITE = (0.95, 0.96, 1, 1)
MUTED = (0.55, 0.60, 0.72, 1)
GOLD = (1, 0.75, 0.30, 1)

Window.clearcolor = BG


class RoundedButton(Button):
    def __init__(self, fill=PURPLE, text_color=WHITE, radius=16, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = text_color
        self.bold = True
        self.font_size = sp(15)
        self._fill = fill
        self._radius = radius
        with self.canvas.before:
            self._color_instruction = Color(*fill)
            self._rounded = RoundedRectangle(pos=self.pos, size=self.size,
                                               radius=[dp(radius)])
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *_):
        self._rounded.pos = self.pos
        self._rounded.size = self.size


class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(10)
        with self.canvas.before:
            Color(*PANEL)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size,
                                             radius=[dp(20)])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


def label(text, size=15, color=WHITE, bold=False, height=None, halign="center"):
    w = Label(text=text, font_size=sp(size), color=color, bold=bold, markup=True,
              halign=halign, valign="middle", size_hint_y=None,
              height=dp(height or max(26, size * 1.65)))
    w.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
    return w


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=[dp(22), dp(24)],
                         spacing=dp(13))
        root.add_widget(Widget(size_hint_y=0.12))
        root.add_widget(label("[b]BRAIN BLITZ[/b]", 31, WHITE, True, 52))
        root.add_widget(label("THINK FAST. PLAY SMART.", 11, PURPLE, True, 24))
        root.add_widget(Widget(size_hint_y=0.04))

        self.best = label("PERSONAL BEST   •   0", 12, MUTED, True, 30)
        root.add_widget(self.best)

        modes = [
            ("QUICK PLAY", "Mixed questions • 3 lives", "quick", PURPLE),
            ("60-SECOND RUSH", "Solve as many as you can", "timed", GREEN),
            ("SURVIVAL", "One mistake costs a life", "survival", GOLD),
        ]
        for title, subtitle, mode, color in modes:
            card = Card(size_hint_y=None, height=dp(104), padding=dp(13), spacing=dp(5))
            card.add_widget(label(title, 18, color, True, 30))
            card.add_widget(label(subtitle, 12, MUTED, False, 22))
            btn = RoundedButton(text="PLAY", fill=color, size_hint_y=None, height=dp(36))
            btn.bind(on_release=lambda _b, m=mode: self.start(m))
            card.add_widget(btn)
            root.add_widget(card)

        root.add_widget(Widget())
        root.add_widget(label("ADDITION  •  SUBTRACTION  •  MULTIPLICATION  •  DIVISION",
                              9, MUTED, False, 24))
        self.add_widget(root)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.best.text = f"PERSONAL BEST   •   {app.store.get('stats')['best'] if app.store.exists('stats') else 0}"

    def start(self, mode):
        app = App.get_running_app()
        app.mode = mode
        app.root.get_screen("game").prepare_game()
        app.root.current = "game"


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer = BoxLayout(orientation="vertical", padding=[dp(20), dp(18)],
                               spacing=dp(12))
        top = BoxLayout(size_hint_y=None, height=dp(42))
        back = RoundedButton(text="‹  MENU", fill=PANEL2, radius=12)
        back.bind(on_release=self.go_home)
        top.add_widget(back)
        top.add_widget(Widget())
        self.mode_title = label("QUICK PLAY", 12, PURPLE, True, 38)
        top.add_widget(self.mode_title)
        self.outer.add_widget(top)

        stats = GridLayout(cols=3, size_hint_y=None, height=dp(78), spacing=dp(8))
        self.score_text = self.stat_box(stats, "SCORE", "0")
        self.lives_text = self.stat_box(stats, "LIVES", "♥ ♥ ♥")
        self.streak_text = self.stat_box(stats, "STREAK", "0")
        self.outer.add_widget(stats)

        self.progress = label("LEVEL 1", 12, MUTED, True, 28)
        self.outer.add_widget(self.progress)
        self.timer = label("00:12", 18, GREEN, True, 34)
        self.outer.add_widget(self.timer)

        self.question_card = Card(size_hint_y=0.36, padding=dp(12), spacing=dp(8))
        self.question_card.add_widget(label("YOUR NEXT CHALLENGE", 10, MUTED, True, 22))
        self.question = label("12 × 8", 42, WHITE, True, 78)
        self.question_card.add_widget(self.question)
        self.outer.add_widget(self.question_card)

        self.answer = TextInput(
            hint_text="TYPE YOUR ANSWER", multiline=False, input_filter="int",
            halign="center", font_size=sp(25), foreground_color=WHITE,
            hint_text_color=MUTED, background_normal="", background_active="",
            background_color=PANEL2, cursor_color=PURPLE,
            size_hint_y=None, height=dp(58), padding=[dp(10), dp(12)]
        )
        self.answer.bind(on_text_validate=self.submit)
        self.outer.add_widget(self.answer)

        self.feedback = label("Ready when you are.", 13, MUTED, False, 34)
        self.outer.add_widget(self.feedback)

        self.submit_btn = RoundedButton(text="SUBMIT ANSWER", fill=PURPLE,
                                        size_hint_y=None, height=dp(56))
        self.submit_btn.bind(on_release=self.submit)
        self.outer.add_widget(self.submit_btn)
        self.outer.add_widget(Widget())
        self.add_widget(self.outer)

    def stat_box(self, parent, heading, value):
        box = Card(padding=dp(7), spacing=dp(2))
        box.add_widget(label(heading, 9, MUTED, True, 18))
        val = label(value, 16, WHITE, True, 30)
        box.add_widget(val)
        parent.add_widget(box)
        return val

    def prepare_game(self):
        app = App.get_running_app()
        self.mode = app.mode
        self.score = 0
        self.lives = 3
        self.streak = 0
        self.correct = 0
        self.total = 0
        self.seconds = 60 if self.mode == "timed" else 12
        self.running = True
        self.mode_title.text = {"quick": "QUICK PLAY", "timed": "60-SECOND RUSH",
                                "survival": "SURVIVAL"}[self.mode]
        self.update_stats()
        self.make_question()
        if hasattr(self, "tick_event") and self.tick_event:
            self.tick_event.cancel()
        self.tick_event = Clock.schedule_interval(self.tick, 1)

    def make_question(self):
        level = 1 + self.correct // 5
        upper = min(12 + level * 8, 100)
        a, b = random.randint(2, upper), random.randint(2, upper)
        op = random.choice(["+", "−", "×", "÷"])
        if op == "+":
            ans = a + b
        elif op == "−":
            if b > a:
                a, b = b, a
            ans = a - b
        elif op == "×":
            a, b = random.randint(2, min(15, level + 7)), random.randint(2, min(15, level + 7))
            ans = a * b
        else:
            ans = random.randint(2, upper)
            b = random.randint(2, min(15, level + 7))
            a = ans * b
        self.answer_value = ans
        self.question.text = f"{a} {op} {b}"
        self.progress.text = f"LEVEL {level}     •     QUESTION {self.total + 1}"
        self.answer.text = ""
        self.answer.focus = True

    def submit(self, *_):
        if not self.running:
            return
        raw = self.answer.text.strip()
        if not raw:
            self.feedback.text = "Enter an answer first."
            self.feedback.color = GOLD
            return
        self.total += 1
        if int(raw) == self.answer_value:
            self.score += 10
            self.correct += 1
            self.streak += 1
            self.feedback.text = "✓  NICE! +10 POINTS"
            self.feedback.color = GREEN
        else:
            self.streak = 0
            if self.mode != "timed":
                self.lives -= 1
            self.feedback.text = f"NOT QUITE — ANSWER: {self.answer_value}"
            self.feedback.color = RED
        self.update_stats()
        if self.mode != "timed" and self.lives <= 0:
            Clock.schedule_once(lambda _dt: self.finish(), 0.45)
        else:
            Clock.schedule_once(lambda _dt: self.make_question(), 0.35)

    def tick(self, _dt):
        if not self.running:
            return
        self.seconds -= 1
        if self.mode == "timed":
            self.timer.text = f"{self.seconds // 60:02d}:{self.seconds % 60:02d}"
            self.timer.color = RED if self.seconds <= 10 else GREEN
            if self.seconds <= 0:
                self.finish()
        else:
            self.timer.text = f"♥  {self.lives} LIVES"
            self.timer.color = RED if self.lives == 1 else GREEN

    def update_stats(self):
        self.score_text.text = str(self.score)
        self.lives_text.text = "♥ " * self.lives if self.mode != "timed" else "∞"
        self.streak_text.text = str(self.streak)

    def finish(self):
        if not self.running:
            return
        self.running = False
        if self.tick_event:
            self.tick_event.cancel()
        app = App.get_running_app()
        best = app.store.get("stats")["best"] if app.store.exists("stats") else 0
        new_best = max(best, self.score)
        app.store.put("stats", best=new_best)
        results = app.root.get_screen("results")
        results.set_results(self.score, self.correct, self.total, new_best)
        app.root.current = "results"

    def go_home(self, *_):
        if self.running:
            self.running = False
            if self.tick_event:
                self.tick_event.cancel()
        self.manager.current = "home"


class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        box = BoxLayout(orientation="vertical", padding=[dp(25), dp(30)], spacing=dp(15))
        box.add_widget(Widget())
        box.add_widget(label("SESSION COMPLETE", 12, PURPLE, True, 28))
        box.add_widget(label("GAME OVER", 34, WHITE, True, 62))
        box.add_widget(label("✦", 34, GOLD, True, 50))
        self.score = label("0", 54, GREEN, True, 80)
        box.add_widget(self.score)
        box.add_widget(label("TOTAL SCORE", 11, MUTED, True, 24))
        self.summary = label("Correct: 0/0\nAccuracy: 0%", 16, WHITE, False, 70)
        box.add_widget(self.summary)
        self.best = label("PERSONAL BEST: 0", 13, GOLD, True, 30)
        box.add_widget(self.best)
        box.add_widget(Widget())
        again = RoundedButton(text="PLAY AGAIN", fill=PURPLE, size_hint_y=None, height=dp(58))
        again.bind(on_release=self.play_again)
        box.add_widget(again)
        menu = RoundedButton(text="BACK TO HOME", fill=PANEL2, size_hint_y=None, height=dp(52))
        menu.bind(on_release=lambda *_: setattr(self.manager, "current", "home"))
        box.add_widget(menu)
        box.add_widget(Widget())
        self.add_widget(box)

    def set_results(self, score, correct, total, best):
        accuracy = round(correct / total * 100) if total else 0
        self.score.text = str(score)
        self.summary.text = f"Correct answers: {correct}/{total}\nAccuracy: {accuracy}%"
        self.best.text = f"PERSONAL BEST: {best}"

    def play_again(self, *_):
        game = self.manager.get_screen("game")
        game.prepare_game()
        self.manager.current = "game"


class BrainBlitzApp(App):
    def build(self):
        self.title = "Brain Blitz"
        self.store = JsonStore("brainblitz_scores.json")
        self.mode = "quick"
        manager = ScreenManager(transition=FadeTransition(duration=0.18))
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(GameScreen(name="game"))
        manager.add_widget(ResultsScreen(name="results"))
        return manager


if __name__ == "__main__":
    BrainBlitzApp().run()
