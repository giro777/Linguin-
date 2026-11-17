"""Deutsch – Türkisch Lern-App (Kivy-Version, läuft auf Linux und Android).

Die Vokabeln kommen aus data/vokabeln.json und die deutschen Sprachaufnahmen
aus data/audio/<id>.mp3. Beides erzeugt prepare_data.py vorab am PC.
"""
import json
import math
import os
import random
import struct
import wave

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex as hexc
from kivy.utils import platform

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
EMOJI_FONT = os.path.join(BASE, "fonts", "NotoEmoji-Regular.ttf")
HAS_EMOJI_FONT = os.path.exists(EMOJI_FONT)

Window.clearcolor = hexc("#17202A")
if platform not in ("android", "ios"):
    Window.size = (420, 780)  # Handy-ähnliches Fenster am PC

# ---------------------------------------------------------------- Emojis
EMOJI_MAP = {
    "Tier": "🐾", "Fisch": "🐟", "Pferd": "🐎", "Vogel": "🐦", "Hund": "🐕", "Katze": "🐈", "Kuh": "🐄", "Insekt": "🐛", "Fledermaus": "🦇",
    "Wasser": "💧", "Lebensmittel": "🛒", "Essen": "🍽", "Ei": "🥚", "Öl": "🛢", "Milch": "🥛", "Koch": "🍳", "Obst": "🍎", "Mais": "🌽", "Fleisch": "🥩", "Salz": "🧂", "Zucker": "🍬", "Apfel": "🍏", "Getränk": "🥤",
    "Luft": "💨", "Sonne": "☀", "Baum": "🌳", "Meer": "🌊", "Stein": "🪨", "Feuer": "🔥", "Mond": "🌙", "Insel": "🏝", "Schnee": "❄", "Stern": "⭐", "Ozean": "🌊", "Regen": "🌧", "Kälte": "🥶", "Eis": "🧊", "Wald": "🌲", "Himmel": "☁", "Gras": "🌱", "Wetter": "🌤", "Blume": "🌸", "See": "🏞", "Wolke": "☁", "Sand": "🏖", "Tal": "⛰",
    "Mutter": "👩", "Vater": "👨", "Mann": "👨", "Junge": "👦", "Mädchen": "👧", "Freund": "🤝", "Kinder": "👶", "König": "👑", "Bruder": "👦", "Soldat": "💂", "Mensch": "🧍", "Frau": "👩", "Kapitän": "⚓", "Nachbar": "🏠", "Chef": "👔", "Elternteil": "👪", "Papa": "🧔", "Schwester": "👧",
    "Hand": "✋", "Kopf": "🗣", "Auge": "👁", "Gesicht": "😊", "Füße": "🦶", "Körper": "👤", "Fuß": "👣", "Herz": "❤", "Arm": "💪", "Schlaf": "😴", "Bein": "🦵", "Mund": "👄", "Blut": "🩸", "Ohr": "👂", "Haut": "✋", "Haar": "💇", "Finger": "👆", "Arzt": "🩺", "Knochen": "🦴", "Zähne": "🦷", "Nase": "👃",
    "Zeit": "⏳", "Jahr": "📅", "Tag": "☀", "Nacht": "🌙", "Woche": "📆", "Minute": "⏱", "Stunde": "⏰", "Morgen": "🌅", "Sommer": "☀", "Winter": "❄", "Monat": "🗓", "Frühling": "🌷", "Abend": "🌆",
    "Zuhause": "🏠", "Haus": "🏡", "Buch": "📖", "Zimmer": "🚪", "Papier": "📄", "Tür": "🚪", "Bett": "🛏", "Fenster": "🪟", "Wand": "🧱", "Glas": "🥛", "Garten": "🌻", "Schlüssel": "🔑", "Stuhl": "🪑", "Uhr": "🕒", "Karte": "🗺",
    "Hafen": "⚓", "Land": "🌍", "Stadt": "🏙", "Auto": "🚗", "Schiff": "🚢", "Straße": "🛣", "Boot": "⛵", "Flugzeug": "✈", "Reise": "🧳", "Zug": "🚆", "Bank": "🏦",
}


def get_emoji_fuer_wort(de_wort):
    teile = de_wort.split()
    if not teile:
        return "💡"
    sauber = teile[0].strip(",.-")
    return EMOJI_MAP.get(sauber) or EMOJI_MAP.get(de_wort) or "💡"


# ---------------------------------------------------------------- Widgets
def make_label(text="", size=14, color="#ECF0F1", bold=False, height=None, **kw):
    """Label mit Zeilenumbruch und zentriertem Text."""
    kw.setdefault("halign", "center")
    lbl = Label(text=text, font_size=sp(size), color=hexc(color), bold=bold,
                valign="middle", **kw)
    if height is not None:
        lbl.size_hint_y = None
        lbl.height = dp(height)
    lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
    return lbl


class RoundButton(ButtonBehavior, Label):
    """Abgerundeter Button mit Farbe und Druck-Farbe."""

    def __init__(self, bg="#2980B9", bg_down="#1F618D", radius=12, **kw):
        kw.setdefault("bold", True)
        kw.setdefault("valign", "middle")
        kw.setdefault("halign", "center")
        kw["font_size"] = kw.get("font_size", sp(15))
        super().__init__(**kw)
        self._bg, self._bg_down = hexc(bg), hexc(bg_down)
        with self.canvas.before:
            self._col = Color(*self._bg)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._update, size=self._update, state=self._on_state)

    def _update(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self.text_size = (max(self.width - dp(24), 0), self.height)

    def _on_state(self, *_):
        self._col.rgba = self._bg_down if self.state == "down" else self._bg


class Card(ButtonBehavior, BoxLayout):
    """Antippbare Karteikarte mit abgerundeten Ecken."""

    def __init__(self, bg="#212F3D", radius=20, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*hexc(bg))
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


# ---------------------------------------------------------------- Audio
def erzeuge_glocke(pfad):
    """Schreibt einen kurzen C-Dur-Glockenklang als WAV-Datei."""
    sample_rate = 22050
    duration = 0.45
    frequenzen = [523.25, 659.25, 783.99, 1046.50]
    daten = bytearray()
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        huellkurve = math.exp(-3.5 * t)
        s = sum(math.sin(2 * math.pi * f * t) * huellkurve for f in frequenzen)
        s = int((s / len(frequenzen)) * 32767 * 0.6)
        daten.extend(struct.pack("<h", max(-32768, min(32767, s))))
    with wave.open(pfad, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(daten))


# ---------------------------------------------------------------- App
class VokabelApp(App):
    title = "Deutsch – Türkisch"

    def build(self):
        self.lektionen = {}
        self.fehler = ""
        try:
            with open(os.path.join(DATA, "vokabeln.json"), encoding="utf-8") as f:
                self.lektionen = json.load(f)
        except Exception as e:
            self.fehler = f"data/vokabeln.json nicht gefunden oder defekt:\n{e}"

        self.aktuelle_vokabeln = []
        self.karten_index = 0
        self.ist_umgedreht = False
        self.aktiver_titel = ""
        self.screen = "menu"
        self.wort_sound = None

        glocke_pfad = os.path.join(self.user_data_dir, "glocke.wav")
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            if not os.path.exists(glocke_pfad):
                erzeuge_glocke(glocke_pfad)
            self.glocke = SoundLoader.load(glocke_pfad)
        except Exception as e:
            print("Glocke:", e)
            self.glocke = None

        self.container = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))
        Window.bind(on_keyboard=self.on_key)
        self.zeige_hauptmenue()
        return self.container

    # -- Hilfen
    def on_key(self, window, key, *args):
        """Android-Zurück-Taste (und Esc am PC): erst zum Menü, dann beenden."""
        if key == 27 and self.screen != "menu":
            self.zeige_hauptmenue()
            return True
        return False

    def leeren(self):
        self.container.clear_widgets()

    def sprache_abspielen(self, vokabel):
        pfad = os.path.join(DATA, "audio", f"{vokabel.get('id', '')}.mp3")
        if not os.path.exists(pfad):
            return
        try:
            if self.wort_sound:
                self.wort_sound.stop()
            self.wort_sound = SoundLoader.load(pfad)
            if self.wort_sound:
                self.wort_sound.play()
        except Exception as e:
            print("Sprachausgabe-Fehler:", e)

    def erfolgsglocke(self):
        if self.glocke:
            self.glocke.stop()
            self.glocke.play()

    # -- Hauptmenü
    def zeige_hauptmenue(self, *_):
        self.screen = "menu"
        self.leeren()
        c = self.container
        c.add_widget(make_label("Merhaba! Was möchtest du lernen?", 22, "#5DADE2", True, height=56))
        c.add_widget(make_label("Wähle eine Lektion aus und starte deine Karteikarten:",
                                14, "#A6ACAF", height=44))

        if self.fehler:
            c.add_widget(make_label(self.fehler, 14, "#E74C3C"))
            return

        sv = ScrollView(do_scroll_x=False)
        grid = GridLayout(cols=1, spacing=dp(8), padding=dp(4), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for titel, vokabeln in self.lektionen.items():
            btn = RoundButton(text=f"{titel}   ({len(vokabeln)} Wörter)", halign="left",
                              size_hint_y=None, height=dp(56))
            btn.bind(on_release=lambda _b, t=titel: self.starte_lektion(t))
            grid.add_widget(btn)
        sv.add_widget(grid)
        c.add_widget(sv)

    # -- Lektion starten
    def starte_lektion(self, titel):
        self.aktuelle_vokabeln = list(self.lektionen[titel])
        random.shuffle(self.aktuelle_vokabeln)
        self.karten_index = 0
        self.ist_umgedreht = False
        self.aktiver_titel = titel
        self.zeige_lern_ansicht(spiele=True)

    # -- Lernansicht
    def zeige_lern_ansicht(self, feedback_text="", spiele=False):
        self.screen = "lern"
        self.leeren()
        c = self.container
        vokabel = self.aktuelle_vokabeln[self.karten_index]

        # obere Leiste
        top = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        zurueck = RoundButton(text="< Menü", bg="#566573", bg_down="#34495E",
                              size_hint_x=None, width=dp(90), font_size=sp(14))
        zurueck.bind(on_release=self.zeige_hauptmenue)
        top.add_widget(zurueck)
        top.add_widget(make_label(self.aktiver_titel, 13, "#5DADE2", True, halign="right"))
        c.add_widget(top)

        c.add_widget(make_label(feedback_text, 17, "#F1C40F", True, height=34))
        c.add_widget(make_label(
            f"Karte {self.karten_index + 1} von {len(self.aktuelle_vokabeln)}",
            13, "#A6ACAF", height=24))

        # Karte
        karte = Card(orientation="vertical", padding=dp(14), spacing=dp(4))
        karte.bind(on_release=lambda *_: self.karte_umdrehen())
        karte.add_widget(make_label("Deutsch" if not self.ist_umgedreht else "Türkisch",
                                    13, "#85929E", True, height=24))
        if not self.ist_umgedreht:
            emoji = get_emoji_fuer_wort(vokabel["de"]).replace("\ufe0f", "")
            if HAS_EMOJI_FONT:
                karte.add_widget(make_label(emoji, 44, height=64, font_name=EMOJI_FONT))
        karte.add_widget(make_label(
            vokabel["de"] if not self.ist_umgedreht else vokabel["tr"],
            28, "#ECF0F1", True))
        karte.add_widget(make_label("(Tippe auf die Karte zum Umdrehen)", 11, "#7F8C8D", height=22))
        c.add_widget(karte)

        # Buttons
        aktionen = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        if not self.ist_umgedreht:
            hoeren = RoundButton(text="Anhören", bg="#8E44AD", bg_down="#6C3483")
            hoeren.bind(on_release=lambda *_: self.sprache_abspielen(vokabel))
            umdrehen = RoundButton(text="Umdrehen")
            umdrehen.bind(on_release=lambda *_: self.karte_umdrehen())
            aktionen.add_widget(hoeren)
            aktionen.add_widget(umdrehen)
        else:
            nochmal = RoundButton(text="Nochmal üben", bg="#C0392B", bg_down="#962D22")
            nochmal.bind(on_release=lambda *_: self.naechste_karte(wiederholen=True))
            gewusst = RoundButton(text="Gewusst!", bg="#27AE60", bg_down="#1E8449")
            gewusst.bind(on_release=lambda *_: self.naechste_karte(wiederholen=False))
            aktionen.add_widget(nochmal)
            aktionen.add_widget(gewusst)
        c.add_widget(aktionen)

        if spiele:
            self.sprache_abspielen(vokabel)

    def karte_umdrehen(self):
        self.ist_umgedreht = not self.ist_umgedreht
        self.zeige_lern_ansicht()

    def naechste_karte(self, wiederholen=False):
        if wiederholen:
            feedback = "Ach, das üben wir noch mal!"
            wort = self.aktuelle_vokabeln.pop(self.karten_index)
            self.aktuelle_vokabeln.append(wort)
        else:
            feedback = "Genial! Super gemacht!"
            self.erfolgsglocke()
            self.karten_index += 1

        self.ist_umgedreht = False
        if self.karten_index >= len(self.aktuelle_vokabeln):
            self.zeige_fertig_bildschirm()
        else:
            self.zeige_lern_ansicht(feedback_text=feedback, spiele=True)

    def zeige_fertig_bildschirm(self):
        self.screen = "fertig"
        self.leeren()
        c = self.container
        c.add_widget(BoxLayout())  # Abstandhalter oben
        c.add_widget(make_label("Harika! Lektion beendet!", 24, "#2ECC71", True, height=60))
        c.add_widget(make_label("Du hast alle Vokabeln dieser Lektion erfolgreich gemeistert!",
                                14, "#A6ACAF", height=48))
        btn = RoundButton(text="Zurück zur Lektionsauswahl", size_hint_y=None, height=dp(56))
        btn.bind(on_release=self.zeige_hauptmenue)
        c.add_widget(btn)
        c.add_widget(BoxLayout())  # Abstandhalter unten


if __name__ == "__main__":
    VokabelApp().run()
