import os
import re
import json
import math
import random
import hashlib
import threading

from gtts import gTTS

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.utils import platform

if platform != "android":
    Window.size = (420, 720)
Window.clearcolor = (0.065, 0.068, 0.075, 1)

BASIS = os.path.dirname(os.path.abspath(__file__))

# --- FARBEN ---
BLAU = (0.125, 0.639, 0.996, 1)
BLAU_DUNKEL = (0.09, 0.48, 0.78, 1)
GRAU = (0.35, 0.35, 0.35, 1)
ROT = (0.85, 0.25, 0.25, 1)
GRUEN = (0.18, 0.72, 0.38, 1)

KARTE_FUELLUNG = (0.12, 0.13, 0.16, 1)
KARTE_RAND = (0.24, 0.27, 0.33, 1)
KARTE_RAND_BLAU = (0.125, 0.639, 0.996, 0.55)
TEXT_HELL = (0.96, 0.97, 0.98, 1)
TEXT_MUTED = (0.68, 0.71, 0.76, 1)

# =====================================================================
#  SPRACH-KONFIGURATION
# =====================================================================
# App-Sprache -> verfügbare Lernsprachen (= verfügbare Kurse)
KURSE = {
    "de": ["en"],
    "tr": ["de", "en"],
}
APP_SPRACHEN = ["de", "tr"]
STANDARD_APP_SPRACHE = "tr"
STANDARD_LERNSPRACHE = "de"

# Sprachnamen, je nach App-Sprache
SPRACHNAMEN = {
    "de": {"de": "Deutsch", "en": "Englisch", "tr": "Türkisch"},
    "tr": {"de": "Almanca", "en": "İngilizce", "tr": "Türkçe"},
}
# Eigennamen (für die Auswahl der App-Sprache)
EIGENNAMEN = {"de": "Deutsch", "tr": "Türkçe"}

# Sprachcode für die Sprachausgabe (gTTS)
TTS_CODES = {"de": "de", "en": "en", "tr": "tr"}

# --- Übersetzte Texte der Oberfläche ---
TEXTE = {
    "title": {"de": "Lern-App", "tr": "Öğrenme Uygulaması"},
    "hello": {"de": "Hallo! Willkommen!", "tr": "Merhaba! Hoş geldin!"},
    "what_do": {"de": "Was möchtest du tun?", "tr": "Ne yapmak istiyorsun?"},
    "learn": {"de": "Lernen", "tr": "Öğren"},
    "review": {"de": "Wiederholung", "tr": "Tekrar"},
    "learn_area": {"de": "Lernbereich", "tr": "Öğrenme Alanı"},
    "choose_cat": {"de": "Bitte wähle eine Kategorie:", "tr": "Lütfen bir kategori seç:"},
    "vocab": {"de": "Vokabelkarten", "tr": "Kelime Kartları"},
    "phrases": {"de": "Alltagsphrasen", "tr": "Günlük İfadeler"},
    "grammar": {"de": "Grammatik", "tr": "Gramer"},
    "back_main": {"de": "< Hauptmenü", "tr": "< Ana Menü"},
    "back_learn": {"de": "< Lernmenü", "tr": "< Öğrenme Menüsü"},
    "back": {"de": "Zurück", "tr": "Geri Dön"},
    "no_content": {"de": "Für diesen Kurs gibt es noch keine Inhalte.",
                   "tr": "Bu kurs için henüz içerik yok."},
    "vocab_lessons": {"de": "Vokabel-Lektionen", "tr": "Kelime Dersleri"},
    "choose_lesson": {"de": "Bitte wähle eine Lektion:", "tr": "Lütfen bir ders seç:"},
    "grammar_lessons": {"de": "Grammatik-Lektionen", "tr": "Gramer Dersleri"},
    "done_tag": {"de": "(Abgeschlossen)", "tr": "(Tamamlandı)"},
    "lessons_btn": {"de": "< Lektionen", "tr": "< Dersler"},
    "card_n": {"de": "Karte {n} / {m}", "tr": "Kart {n} / {m}"},
    "topic": {"de": "ERKLÄRUNG", "tr": "KONU ANLATIMI"},
    "prev": {"de": "< Zurück", "tr": "< Önceki"},
    "next": {"de": "Nächste Karte >", "tr": "Sonraki Kart >"},
    "start_quiz": {"de": "Quiz starten", "tr": "Teste Başla (Quiz)"},
    "exit": {"de": "< Beenden", "tr": "< Çık"},
    "question_n": {"de": "Frage {n} / {m}", "tr": "Soru {n} / {m}"},
    "correct": {"de": "Richtig!  →  {s}", "tr": "Doğru!  →  {s}"},
    "wrong": {"de": "Falsch! Nicht '{a}'. Versuch es nochmal!",
              "tr": "Yanlış! '{a}' değil. Tekrar dene!"},
    "no_lives": {"de": "Keine Leben mehr!", "tr": "Canların Bitti!"},
    "lives_msg": {
        "de": "Du hast 3-mal falsch geantwortet.\nUm die Lektion abzuschließen, musst du das Quiz neu starten.",
        "tr": "3 kez yanlış cevap verdin.\nDersi tamamlamak için testi baştan yapmalısın."},
    "progress": {"de": "Fortschritt: {n} / {m}", "tr": "İlerleme: {n} / {m}"},
    "restart_quiz": {"de": "Quiz neu starten", "tr": "Testi Tekrar Başlat"},
    "to_lessons": {"de": "Zurück zu den Lektionen", "tr": "Derslere Dön"},
    "success": {"de": "Sehr gut! Geschafft!", "tr": "Çok iyi! Başardın!"},
    "score": {"de": "Punkte: {p} / {m}   ·   Leben: {l}/3",
              "tr": "Puan: {p} / {m}   ·   Kalan Can: {l}/3"},
    "to_grammar_menu": {"de": "Zurück zum Grammatikmenü", "tr": "Gramer Menüsüne Dön"},
    "tap_flip": {"de": "(Tippe unten, um die Karte zu drehen)",
                 "tr": "(Çevirmek için alttaki butona tıkla)"},
    "listen_again": {"de": "Nochmal anhören ({lang})", "tr": "Tekrar Dinle ({lang})"},
    "flip": {"de": "Karte umdrehen", "tr": "Kartı Çevir"},
    "flip_back": {"de": "Zurückdrehen", "tr": "Geri Çevir"},
    "study_again": {"de": "Nochmal üben", "tr": "Tekrar Çalış"},
    "known": {"de": "Weiß ich!", "tr": "Biliyorum!"},
    "fb_again": {"de": "Das üben wir nochmal!", "tr": "Bunu tekrar çalışacağız!"},
    "fb_good": {"de": "Super! Weiter so!", "tr": "Harika! Süpersin!"},
    "back_short": {"de": "< Zurück", "tr": "< Geri"},
    "lesson_done": {"de": "Toll! Lektion beendet!", "tr": "Harika! Ders bitti!"},
    "lesson_done_msg": {"de": "Du hast alle Karten dieser Lektion geschafft!",
                        "tr": "Bu dersteki bütün ifadeleri başarıyla tamamladın!"},
    "to_menu": {"de": "Zum Menü", "tr": "Menüye Dön"},
    "nothing_learned": {
        "de": "Noch keine gelernten Karten!\nLerne zuerst ein paar Vokabeln oder Phrasen.",
        "tr": "Henüz öğrenilmiş kart yok!\nÖnce biraz kelime veya ifade öğrenin."},
    "review_title": {"de": "Wiederholung", "tr": "Tekrar"},
    "settings": {"de": "Einstellungen", "tr": "Ayarlar"},
    "app_language": {"de": "App-Sprache", "tr": "Uygulama Dili"},
    "learn_language": {"de": "Lernsprache", "tr": "Öğrenilen Dil"},
    "choose_answer": {"de": "Wähle die richtige Antwort:", "tr": "Doğru cevabı seç:"},
    "quiz_default_title": {"de": "QUIZ", "tr": "QUİZ"},
}

# Übersetzung der (deutschen) Lektionstitel, falls die App-Sprache Türkisch ist.
# Titel, die hier nicht vorkommen, werden unverändert angezeigt.
LEKTIONS_UEBERSETZUNG_TR = {
    "Lektion 1: Zahlen & Mengen": "Ders 1: Sayılar ve Miktarlar",
    "Lektion 2: Farben & Optik": "Ders 2: Renkler ve Optik",
    "Lektion 3: Tiere": "Ders 3: Hayvanlar",
    "Lektion 4: Familie & Menschen": "Ders 4: Aile ve İnsanlar",
    "Lektion 5: Körper & Gesundheit": "Ders 5: Vücut ve Sağlık",
    "Lektion 6: Essen & Trinken": "Ders 6: Yiyecek ve İçecek",
    "Lektion 7: Natur, Wetter & Geografie": "Ders 7: Doğa, Hava ve Coğrafya",
    "Lektion 8: Zeit, Kalender & Jahreszeiten": "Ders 8: Zaman, Takvim ve Mevsimler",
    "Lektion 9: Zuhause, Möbel & Alltagsobjekte": "Ders 9: Ev, Mobilya ve Günlük Eşyalar",
    "Lektion 10: Kleidung & Materialien": "Ders 10: Kıyafetler ve Malzemeler",
    "Lektion 11: Stadt, Orte & Reisen": "Ders 11: Şehir, Yerler ve Seyahat",
    "Lektion 12: Arbeit, Bildung & Wissenschaft": "Ders 12: İş, Eğitim ve Bilim",
    "Lektion 13: Sprache, Musik & Kunst": "Ders 13: Dil, Müzik ve Sanat",
    "Lektion 14: Gefühle, Eigenschaften & Zustände": "Ders 14: Duygular, Özellikler ve Durumlar",
    "Lektion 15: Verben: Bewegung & Alltag": "Ders 15: Fiiller: Hareket ve Günlük Yaşam",
    "Lektion 16: Verben: Denken, Kommunikation & Wahrnehmung": "Ders 16: Fiiller: Düşünme, İletişim ve Algı",
    "Lektion 17: Pronomen & Artikel": "Ders 17: Zamirler ve Artikeller",
    "Lektion 18: Präpositionen, Konjunktionen & Adverbien": "Ders 18: Edatlar, Bağlaçlar ve Zarflar",
}


# =====================================================================
#  DATEIEN LADEN / SPEICHERN
# =====================================================================
def schreib_ordner():
    """Ordner für veränderbare Dateien (Fortschritt, Einstellungen)."""
    if platform == "android":
        try:
            return App.get_running_app().user_data_dir
        except Exception:
            pass
    return os.path.join(BASIS, "data")


def lade_json_datei(dateiname, veraenderbar=False):
    pfade = []
    if veraenderbar:
        pfade.append(os.path.join(schreib_ordner(), dateiname))
    pfade += [os.path.join(BASIS, "Data", dateiname),
              os.path.join(BASIS, "data", dateiname),
              os.path.join(BASIS, dateiname)]
    for pfad in pfade:
        if os.path.exists(pfad):
            try:
                with open(pfad, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden von {pfad}: {e}")
    return {}


def speichere_json_datei(dateiname, daten):
    try:
        ordner = schreib_ordner()
        os.makedirs(ordner, exist_ok=True)
        with open(os.path.join(ordner, dateiname), "w", encoding="utf-8") as f:
            json.dump(daten, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Fehler beim Speichern von {dateiname}: {e}")


def label(text, groesse, hoehe=None, **kw):
    lbl = Label(text=text, font_size=sp(groesse), halign='center',
                valign='middle', **kw)
    if hoehe:
        lbl.size_hint_y = None
        lbl.height = dp(hoehe)
    lbl.bind(size=lambda w, s: setattr(w, 'text_size', (s[0], None)))
    return lbl


# --- ÄSTHETISCHER, ABGERUNDETER KNOPF (PILL BUTTON) MIT PRESS-EFFEKT ---
class AbgerundeterButton(Button):
    def __init__(self, farbe=BLAU, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.custom_farbe = farbe
        self.gedrueckt = False

        with self.canvas.before:
            self._color_instr = Color(*self.custom_farbe)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.height / 2.0])

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def _aktive_farbe(self):
        if not self.gedrueckt:
            return self.custom_farbe
        r, g, b, a = self.custom_farbe
        return (max(0.0, r * 0.78), max(0.0, g * 0.78), max(0.0, b * 0.78), a)

    def on_press(self):
        self.gedrueckt = True
        self._color_instr.rgba = self._aktive_farbe()
        return super().on_press()

    def on_release(self):
        self.gedrueckt = False
        self._color_instr.rgba = self._aktive_farbe()
        return super().on_release()

    def update_canvas(self, *args):
        self._color_instr.rgba = self._aktive_farbe()
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.rect.radius = [self.height / 2.0]


def knopf(text, groesse=16, hoehe=56, farbe=BLAU, **kw):
    btn = AbgerundeterButton(text=text, font_size=sp(groesse), bold=True,
                             halign='center', valign='middle',
                             farbe=farbe, **kw)
    btn.size_hint_y = None
    btn.height = dp(hoehe)
    btn.bind(size=lambda w, s: setattr(w, 'text_size', (s[0] - dp(16), s[1])))
    return btn


# --- ZAHNRAD-SYMBOL (selbst gezeichnet, unabhängig von Schriftarten) ---
class ZahnradButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.size_hint = (None, None)
        self.size = (dp(48), dp(48))

        with self.canvas.after:
            self._farbe = Color(*TEXT_MUTED)
            self._ring = Line(circle=(0, 0, 1), width=dp(2.2))
            self._nabe = Line(circle=(0, 0, 1), width=dp(1.8))
            self._zaehne = [Line(points=[0, 0, 0, 0], width=dp(3.2), cap='round')
                            for _ in range(8)]

        self.bind(pos=self._zeichne, size=self._zeichne, state=self._zeichne)
        self._zeichne()

    def _zeichne(self, *args):
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) * 0.25
        self._farbe.rgba = BLAU if self.state == 'down' else TEXT_MUTED
        self._ring.circle = (cx, cy, r)
        self._nabe.circle = (cx, cy, r * 0.4)
        for i, zahn in enumerate(self._zaehne):
            w = i * math.pi / 4
            c, s = math.cos(w), math.sin(w)
            zahn.points = [cx + c * r * 1.05, cy + s * r * 1.05,
                           cx + c * r * 1.5, cy + s * r * 1.5]


# --- ABGERUNDETE KARTENFLÄCHE MIT FEINEM RAHMEN ---
class KarteBox(BoxLayout):
    def __init__(self, rand_farbe=KARTE_RAND, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(10)
        self._rand_farbe = rand_farbe

        with self.canvas.before:
            Color(*KARTE_FUELLUNG)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            self._border_color = Color(*self._rand_farbe)
            self._border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(18)), width=dp(1.1))

        self.bind(pos=self._update_karte, size=self._update_karte)

    def _update_karte(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(18))


# --- VISUELLER FORTSCHRITTSBALKEN ---
class FortschrittsBalken(Widget):
    def __init__(self, fortschritt_wert=0.0, fuell_farbe=BLAU, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(8)
        self.fortschritt_wert = max(0.0, min(1.0, fortschritt_wert))
        self.fuell_farbe = fuell_farbe

        with self.canvas:
            Color(0.18, 0.20, 0.25, 1)
            self._track = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
            self._fill_color = Color(*self.fuell_farbe)
            self._fill = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[dp(4)])

        self.bind(pos=self._update_balken, size=self._update_balken)

    def _update_balken(self, *args):
        self._track.pos = self.pos
        self._track.size = self.size
        breite = self.width * self.fortschritt_wert if self.fortschritt_wert > 0 else 0
        self._fill.pos = self.pos
        self._fill.size = (breite, self.height)


# --- VISUELLE 3-LEBEN-ANZEIGE ---
class LebenAnzeige(BoxLayout):
    def __init__(self, leben=3, max_leben=3, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (dp(54), dp(20))
        self.spacing = dp(6)
        self.padding = [dp(4), dp(4), dp(4), dp(4)]
        self.leben = max(0, min(max_leben, leben))
        self.max_leben = max_leben
        self._punkte = []

        with self.canvas:
            for i in range(self.max_leben):
                aktiv = i < self.leben
                farbe = GRUEN if self.leben > 1 else (ROT if aktiv else (0.28, 0.30, 0.35, 1))
                if not aktiv:
                    farbe = (0.25, 0.27, 0.32, 1)
                c = Color(*farbe)
                e = Ellipse(pos=(0, 0), size=(dp(11), dp(11)))
                self._punkte.append((c, e))

        self.bind(pos=self._update_punkte, size=self._update_punkte)

    def _update_punkte(self, *args):
        punkt_groesse = dp(11)
        abstand = dp(5)
        y_pos = self.y + (self.height - punkt_groesse) / 2.0
        for idx, (_, ell) in enumerate(self._punkte):
            ell.pos = (self.x + dp(3) + idx * (punkt_groesse + abstand), y_pos)
            ell.size = (punkt_groesse, punkt_groesse)


class VokabelRootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(10)

        self.sound = None

        # Einstellungen laden
        einstellungen = lade_json_datei("einstellungen.json", veraenderbar=True)
        self.app_sprache = einstellungen.get("app_sprache", STANDARD_APP_SPRACHE)
        if self.app_sprache not in KURSE:
            self.app_sprache = STANDARD_APP_SPRACHE
        self.lern_sprache = einstellungen.get("lern_sprache", STANDARD_LERNSPRACHE)
        if self.lern_sprache not in KURSE[self.app_sprache]:
            self.lern_sprache = KURSE[self.app_sprache][0]

        self.lektionen = {}
        self.phrasen_daten = {}
        self.grammatik = {}
        self.fortschritt = {}
        self.lade_kurs()

        self.aktuelle_vokabeln = []
        self.karten_index = 0
        self.ist_umgedreht = False
        self.aktiver_titel = ""
        self.aktive_lektion_key = ""
        self.ruecksprung_funktion = self.zeige_hauptmenue

        # Grammatik-Status
        self.aktuelle_grammatik_lektion = ""
        self.grammatik_karten = []
        self.grammatik_index = 0
        self.quiz_fragen = []
        self.quiz_optionen = []
        self.quiz_hinweis = ""
        self.quiz_titel = ""
        self.quiz_index = 0
        self.quiz_leben = 3
        self.quiz_punkte = 0

        self.zeige_hauptmenue()

    # ---------- Sprache / Kurs ----------
    def t(self, key, **fmt):
        text = TEXTE[key][self.app_sprache]
        return text.format(**fmt) if fmt else text

    def sprachname(self, code):
        return SPRACHNAMEN[self.app_sprache].get(code, code)

    def kurs_kuerzel(self):
        return f"{self.app_sprache}_{self.lern_sprache}"

    def fortschritt_dateiname(self):
        return f"fortschritt_{self.kurs_kuerzel()}.json"

    def lade_kurs(self):
        """Lädt alle Daten des aktuell gewählten Kurses (z. B. _tr_de)."""
        k = self.kurs_kuerzel()
        self.lektionen = lade_json_datei(f"vokabeln_{k}.json")
        self.phrasen_daten = lade_json_datei(f"phrasen_{k}.json")
        self.grammatik = lade_json_datei(f"grammatik_{k}.json")

        fortschritt = lade_json_datei(self.fortschritt_dateiname(), veraenderbar=True)
        # Alten Fortschritt (vor der Mehrsprachigkeit) für Türkisch -> Deutsch übernehmen
        if not fortschritt and k == "tr_de":
            fortschritt = lade_json_datei("fortschritt.json", veraenderbar=True)
        self.fortschritt = fortschritt
        self.sound = None

    def speichere_einstellungen(self):
        speichere_json_datei("einstellungen.json", {
            "app_sprache": self.app_sprache,
            "lern_sprache": self.lern_sprache,
        })

    def speichere_fortschritt(self):
        speichere_json_datei(self.fortschritt_dateiname(), self.fortschritt)

    def setze_app_sprache(self, code):
        self.app_sprache = code
        if self.lern_sprache not in KURSE[code]:
            self.lern_sprache = KURSE[code][0]
        self.speichere_einstellungen()
        self.lade_kurs()
        self.zeige_einstellungen()

    def setze_lern_sprache(self, code):
        self.lern_sprache = code
        self.speichere_einstellungen()
        self.lade_kurs()
        self.zeige_einstellungen()

    def lektions_titel(self, key):
        if self.app_sprache == "tr":
            return LEKTIONS_UEBERSETZUNG_TR.get(key, key)
        return key

    def karten_texte(self, karte):
        """Gibt (Lernsprache, App-Sprache) einer Karte zurück."""
        vorne = karte.get(self.lern_sprache)
        hinten = karte.get(self.app_sprache)
        if vorne is None or hinten is None:
            werte = [v for v in karte.values() if isinstance(v, str)]
            vorne = vorne if vorne is not None else (werte[0] if werte else "")
            hinten = hinten if hinten is not None else (werte[1] if len(werte) > 1 else "")
        return vorne, hinten

    @staticmethod
    def karten_schluessel(karte):
        return json.dumps(karte, sort_keys=True, ensure_ascii=False)

    def bildschirm_leeren(self):
        self.clear_widgets()

    def logo_hinzufuegen(self, layout, hoehe=150):
        for img_datei in ["logo.png", "logo.gif"]:
            pfad = os.path.join(BASIS, img_datei)
            if os.path.exists(pfad):
                try:
                    layout.add_widget(Image(source=pfad, size_hint_y=None,
                                            height=dp(hoehe)))
                    break
                except Exception:
                    pass

    # ---------- Sprachausgabe (gTTS) ----------
    def sprache_abspielen(self, text):
        sprache = TTS_CODES.get(self.lern_sprache, self.lern_sprache)

        def lade():
            try:
                name = hashlib.md5(f"{sprache}:{text}".encode("utf-8")).hexdigest() + ".mp3"
                pfad = os.path.join(App.get_running_app().user_data_dir, name)
                if not os.path.exists(pfad):
                    tts = gTTS(text=text, lang=sprache)
                    tts.save(pfad)
                Clock.schedule_once(lambda dt: self._spiele(pfad))
            except Exception as e:
                print(f"Sprachausgabe-Fehler: {e}")

        threading.Thread(target=lade, daemon=True).start()

    def _spiele(self, pfad):
        try:
            if self.sound:
                self.sound.stop()
            self.sound = SoundLoader.load(pfad)
            if self.sound:
                self.sound.play()
        except Exception as e:
            print(f"Abspiel-Fehler: {e}")

    def _anzahl_wiederholungs_karten(self):
        gesamt = 0
        for kat, karten in self.fortschritt.items():
            if isinstance(karten, list) and kat != "grammatik_abgeschlossen":
                gesamt += len(karten)
        return gesamt

    @staticmethod
    def _text_ohne_markup(text):
        return re.sub(r"\[/?(?:color|size)(?:=[^\]]*)?\]", "", text)

    # ---------- 1. Hauptmenü (Start) ----------
    def zeige_hauptmenue(self, *args):
        self.bildschirm_leeren()

        container = BoxLayout(orientation='vertical', size_hint=(1, 1))

        leiste = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48))
        leiste.add_widget(Widget())
        zahnrad = ZahnradButton()
        zahnrad.bind(on_release=self.zeige_einstellungen)
        leiste.add_widget(zahnrad)
        container.add_widget(leiste)

        container.add_widget(Widget(size_hint_y=1))

        quadrat_block = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        quadrat_block.bind(minimum_height=quadrat_block.setter('height'))

        self.logo_hinzufuegen(quadrat_block, hoehe=150)

        quadrat_block.add_widget(label(self.t("hello"), 24, 44, bold=True, color=BLAU))
        quadrat_block.add_widget(label(self.t("what_do"), 15, 26, color=TEXT_MUTED))

        btn_lernen = knopf(self.t("learn"), groesse=18, hoehe=58, farbe=BLAU)
        btn_lernen.bind(on_release=self.zeige_lernen_menue)
        quadrat_block.add_widget(btn_lernen)

        anzahl = self._anzahl_wiederholungs_karten()
        wiederhol_text = f"{self.t('review')} · {anzahl}" if anzahl > 0 else self.t("review")
        btn_wiederholen = knopf(wiederhol_text, groesse=18, hoehe=58, farbe=BLAU)
        btn_wiederholen.bind(on_release=self.starte_wiederholung_stapel)
        quadrat_block.add_widget(btn_wiederholen)

        container.add_widget(quadrat_block)
        container.add_widget(Widget(size_hint_y=1))
        self.add_widget(container)

    # ---------- Einstellungen ----------
    def zeige_einstellungen(self, *args):
        self.bildschirm_leeren()

        zurueck = knopf(self.t("back_main"), groesse=15, hoehe=44, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_hauptmenue)
        self.add_widget(zurueck)

        self.add_widget(Widget(size_hint_y=1))

        block = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        block.bind(minimum_height=block.setter('height'))

        block.add_widget(label(self.t("settings"), 22, 44, bold=True, color=BLAU))

        # App-Sprache
        block.add_widget(label(self.t("app_language"), 15, 28, color=TEXT_MUTED))
        reihe_app = BoxLayout(orientation='horizontal', size_hint_y=None,
                              height=dp(54), spacing=dp(10))
        for code in APP_SPRACHEN:
            ist_aktiv = (code == self.app_sprache)
            btn = knopf(EIGENNAMEN[code], groesse=17, hoehe=54,
                        farbe=BLAU if ist_aktiv else GRAU)
            btn.bind(on_release=lambda b, c=code: self.setze_app_sprache(c))
            reihe_app.add_widget(btn)
        block.add_widget(reihe_app)

        block.add_widget(Widget(size_hint_y=None, height=dp(8)))

        # Lernsprache (abhängig von der App-Sprache)
        block.add_widget(label(self.t("learn_language"), 15, 28, color=TEXT_MUTED))
        reihe_lern = BoxLayout(orientation='horizontal', size_hint_y=None,
                               height=dp(54), spacing=dp(10))
        for code in KURSE[self.app_sprache]:
            ist_aktiv = (code == self.lern_sprache)
            btn = knopf(self.sprachname(code), groesse=17, hoehe=54,
                        farbe=BLAU if ist_aktiv else GRAU)
            btn.bind(on_release=lambda b, c=code: self.setze_lern_sprache(c))
            reihe_lern.add_widget(btn)
        block.add_widget(reihe_lern)

        self.add_widget(block)
        self.add_widget(Widget(size_hint_y=1))

    # ---------- 2. Untermenü: Lernen ----------
    def zeige_lernen_menue(self, *args):
        self.bildschirm_leeren()

        container = BoxLayout(orientation='vertical', size_hint=(1, 1))

        zurueck = knopf(self.t("back_main"), groesse=15, hoehe=44, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_hauptmenue)
        container.add_widget(zurueck)

        container.add_widget(Widget(size_hint_y=1))

        mitte_block = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        mitte_block.bind(minimum_height=mitte_block.setter('height'))

        self.logo_hinzufuegen(mitte_block, hoehe=150)

        mitte_block.add_widget(label(self.t("learn_area"), 20, 38, bold=True, color=BLAU))
        mitte_block.add_widget(label(self.t("choose_cat"), 14, 24, color=TEXT_MUTED))

        btn_vokabeln = knopf(self.t("vocab"), groesse=16, hoehe=50, farbe=BLAU)
        btn_vokabeln.bind(on_release=self.zeige_lektionen_menue)
        mitte_block.add_widget(btn_vokabeln)

        btn_phrasen = knopf(self.t("phrases"), groesse=16, hoehe=50, farbe=BLAU)
        btn_phrasen.bind(on_release=self.zeige_phrasen_kategorien_menue)
        mitte_block.add_widget(btn_phrasen)

        btn_grammatik = knopf(self.t("grammar"), groesse=16, hoehe=50, farbe=BLAU)
        btn_grammatik.bind(on_release=self.zeige_grammatik_menue)
        mitte_block.add_widget(btn_grammatik)

        container.add_widget(mitte_block)
        container.add_widget(Widget(size_hint_y=1))
        self.add_widget(container)

    def zeige_platzhalter_info(self, nachricht):
        self.bildschirm_leeren()
        self.add_widget(Widget(size_hint_y=1))
        karte = KarteBox(rand_farbe=KARTE_RAND_BLAU, size_hint_y=None, height=dp(150))
        karte.add_widget(label(nachricht, 19, 100, bold=True, color=BLAU))
        self.add_widget(karte)

        zurueck = knopf(self.t("back"), groesse=16, hoehe=56, farbe=BLAU)
        zurueck.bind(on_release=self.zeige_hauptmenue)
        self.add_widget(zurueck)
        self.add_widget(Widget(size_hint_y=1))

    # ---------- 3C. Grammatik-Lektionen-Menü ----------
    def zeige_grammatik_menue(self, *args):
        self.bildschirm_leeren()
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12), padding=[0, 0, 0, dp(20)])
        layout.bind(minimum_height=layout.setter('height'))

        zurueck = knopf(self.t("back_learn"), groesse=16, hoehe=48, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_lernen_menue)
        layout.add_widget(zurueck)

        layout.add_widget(label(self.t("grammar_lessons"), 22, 50, bold=True, color=BLAU))
        layout.add_widget(label(self.t("choose_lesson"), 16, 30, color=TEXT_MUTED))

        if not self.grammatik:
            layout.add_widget(label(self.t("no_content"), 15, 60, color=TEXT_MUTED))

        abgeschlossen = self.fortschritt.get("grammatik_abgeschlossen", [])

        for lektions_name in self.grammatik.keys():
            ist_fertig = lektions_name in abgeschlossen
            status = f"  ✓ {self.t('done_tag')}" if ist_fertig else ""
            farbe = GRUEN if ist_fertig else BLAU
            btn = knopf(f"{lektions_name}{status}", groesse=16, hoehe=58, farbe=farbe)
            btn.bind(on_release=lambda b, ln=lektions_name: self.starte_grammatik_lektion(ln))
            layout.add_widget(btn)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def starte_grammatik_lektion(self, lektions_name):
        self.aktuelle_grammatik_lektion = lektions_name
        lektion = self.grammatik[lektions_name]
        self.grammatik_karten = list(lektion["karten"])
        self.grammatik_index = 0
        self.zeige_grammatik_karte()

    def zeige_grammatik_karte(self):
        self.bildschirm_leeren()

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        zurueck = knopf(self.t("lessons_btn"), groesse=15, hoehe=52, farbe=GRAU, size_hint_x=None, width=dp(105))
        zurueck.bind(on_release=self.zeige_grammatik_menue)
        top.add_widget(zurueck)
        top.add_widget(label(self.aktuelle_grammatik_lektion, 14, bold=True, color=BLAU))
        self.add_widget(top)

        gesamt = len(self.grammatik_karten)
        fortschritt_quote = (self.grammatik_index + 1) / max(1, gesamt)
        self.add_widget(FortschrittsBalken(fortschritt_wert=fortschritt_quote, fuell_farbe=BLAU))
        self.add_widget(label(self.t("card_n", n=self.grammatik_index + 1, m=gesamt), 14, 28, color=TEXT_MUTED))

        text = self.grammatik_karten[self.grammatik_index]
        reiner_text = self._text_ohne_markup(text)
        schriftgroesse = 25 if len(reiner_text) < 25 else 18

        karte = KarteBox(rand_farbe=KARTE_RAND_BLAU)
        karte.add_widget(label(self.t("topic"), 11, 22, bold=True, color=BLAU))
        karte.add_widget(label(text, schriftgroesse, bold=True, markup=True, color=TEXT_HELL))
        self.add_widget(karte)

        aktion = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(64), spacing=dp(12))

        if self.grammatik_index > 0:
            prev_btn = knopf(self.t("prev"), groesse=16, hoehe=56, farbe=GRAU)
            prev_btn.bind(on_release=lambda x: self.grammatik_karte_wechseln(-1))
            aktion.add_widget(prev_btn)

        ist_letzte_karte = (self.grammatik_index == gesamt - 1)
        weiter_text = self.t("start_quiz") if ist_letzte_karte else self.t("next")
        next_btn = knopf(weiter_text, groesse=17, hoehe=56, farbe=BLAU)
        next_btn.bind(on_release=lambda x: self.grammatik_karte_wechseln(1))
        aktion.add_widget(next_btn)

        self.add_widget(aktion)

    def grammatik_karte_wechseln(self, schritt):
        neuer_index = self.grammatik_index + schritt
        if neuer_index < 0:
            return
        if neuer_index >= len(self.grammatik_karten):
            self.starte_grammatik_quiz()
        else:
            self.grammatik_index = neuer_index
            self.zeige_grammatik_karte()

    # ---------- Grammatik Multiple-Choice Quiz (3 Leben) ----------
    def starte_grammatik_quiz(self):
        lektion = self.grammatik[self.aktuelle_grammatik_lektion]
        self.quiz_fragen = list(lektion.get("quiz", []))
        if not self.quiz_fragen:
            self.zeige_grammatik_menue()
            return
        self.quiz_optionen = list(lektion.get("optionen", []))
        self.quiz_hinweis = lektion.get("quiz_hinweis", self.t("choose_answer"))
        self.quiz_titel = lektion.get("quiz_titel", self.t("quiz_default_title"))
        self.quiz_index = 0
        self.quiz_leben = 3
        self.quiz_punkte = 0
        self.zeige_grammatik_quiz_frage()

    def zeige_grammatik_quiz_frage(self, feedback_text="", feedback_farbe=BLAU):
        self.bildschirm_leeren()

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        zurueck = knopf(self.t("exit"), groesse=15, hoehe=52, farbe=GRAU, size_hint_x=None, width=dp(86))
        zurueck.bind(on_release=self.zeige_grammatik_menue)
        top.add_widget(zurueck)
        top.add_widget(label(self.t("question_n", n=self.quiz_index + 1, m=len(self.quiz_fragen)), 15, bold=True, color=BLAU))

        leben_box = BoxLayout(orientation='horizontal', size_hint_x=None, width=dp(116), spacing=dp(4))
        leben_box.add_widget(label(f"{self.quiz_leben}/3", 14, bold=True, color=ROT if self.quiz_leben == 1 else GRUEN))
        leben_box.add_widget(LebenAnzeige(leben=self.quiz_leben, max_leben=3))
        top.add_widget(leben_box)
        self.add_widget(top)

        quote = self.quiz_index / max(1, len(self.quiz_fragen))
        self.add_widget(FortschrittsBalken(fortschritt_wert=quote, fuell_farbe=GRUEN if feedback_farbe == GRUEN else BLAU))

        if feedback_text:
            self.add_widget(label(feedback_text, 15, 42, bold=True, color=feedback_farbe))
        else:
            self.add_widget(label(self.quiz_hinweis, 15, 32, color=TEXT_MUTED))

        frage = self.quiz_fragen[self.quiz_index]
        reiner_frage_text = self._text_ohne_markup(frage["anzeige"])
        frage_groesse = 21 if len(reiner_frage_text) > 35 else 26

        karte = KarteBox(rand_farbe=KARTE_RAND_BLAU)
        karte.add_widget(label(self.quiz_titel, 12, 24, bold=True, color=BLAU))
        karte.add_widget(label(frage["anzeige"], frage_groesse, bold=True, markup=True, color=TEXT_HELL))
        self.add_widget(karte)

        if len(self.quiz_optionen) <= 3:
            antwort_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(68), spacing=dp(10), padding=[0, dp(4), 0, dp(4)])
            for option in self.quiz_optionen:
                btn = knopf(option, groesse=19, hoehe=56, farbe=BLAU)
                btn.bind(on_release=lambda b, opt=option: self.pruefe_quiz_antwort(opt))
                antwort_container.add_widget(btn)
        else:
            antwort_container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(124), spacing=dp(8), padding=[0, dp(4), 0, dp(4)])
            mitte = (len(self.quiz_optionen) + 1) // 2
            zeilen = [self.quiz_optionen[:mitte], self.quiz_optionen[mitte:]]
            for zeile in zeilen:
                reihe = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(54), spacing=dp(10))
                for option in zeile:
                    btn = knopf(option, groesse=18, hoehe=52, farbe=BLAU)
                    btn.bind(on_release=lambda b, opt=option: self.pruefe_quiz_antwort(opt))
                    reihe.add_widget(btn)
                antwort_container.add_widget(reihe)

        self.add_widget(antwort_container)

    def pruefe_quiz_antwort(self, gewaehlte_antwort):
        frage = self.quiz_fragen[self.quiz_index]
        richtig = (gewaehlte_antwort == frage["antwort"])

        if richtig:
            self.quiz_punkte += 1
            if frage.get("vollstaendig"):
                self.sprache_abspielen(frage["vollstaendig"])
            self.quiz_index += 1
            if self.quiz_index >= len(self.quiz_fragen):
                self.zeige_grammatik_quiz_erfolg()
            else:
                self.zeige_grammatik_quiz_frage(
                    feedback_text=self.t("correct", s=frage.get("vollstaendig", "")),
                    feedback_farbe=GRUEN
                )
        else:
            self.quiz_leben -= 1
            if self.quiz_leben <= 0:
                self.zeige_grammatik_quiz_verloren()
            else:
                self.zeige_grammatik_quiz_frage(
                    feedback_text=self.t("wrong", a=gewaehlte_antwort),
                    feedback_farbe=ROT
                )

    def zeige_grammatik_quiz_verloren(self):
        self.bildschirm_leeren()
        self.add_widget(Widget(size_hint_y=1))

        karte = KarteBox(rand_farbe=ROT, size_hint_y=None, height=dp(210))
        karte.add_widget(label(self.t("no_lives"), 25, 44, bold=True, color=ROT))
        karte.add_widget(label(self.t("lives_msg"), 15, 76, color=TEXT_MUTED))
        karte.add_widget(label(self.t("progress", n=self.quiz_index, m=len(self.quiz_fragen)), 15, 32, bold=True, color=TEXT_HELL))
        self.add_widget(karte)

        nochmal_btn = knopf(self.t("restart_quiz"), groesse=18, hoehe=60, farbe=BLAU)
        nochmal_btn.bind(on_release=lambda x: self.starte_grammatik_quiz())
        self.add_widget(nochmal_btn)

        zurueck_btn = knopf(self.t("to_lessons"), groesse=16, hoehe=54, farbe=GRAU)
        zurueck_btn.bind(on_release=self.zeige_grammatik_menue)
        self.add_widget(zurueck_btn)
        self.add_widget(Widget(size_hint_y=1))

    def zeige_grammatik_quiz_erfolg(self):
        abgeschlossen = self.fortschritt.get("grammatik_abgeschlossen", [])
        if self.aktuelle_grammatik_lektion not in abgeschlossen:
            abgeschlossen.append(self.aktuelle_grammatik_lektion)
            self.fortschritt["grammatik_abgeschlossen"] = abgeschlossen
            self.speichere_fortschritt()

        gesamt = len(self.quiz_fragen)
        self.bildschirm_leeren()
        self.add_widget(Widget(size_hint_y=1))

        karte = KarteBox(rand_farbe=GRUEN, size_hint_y=None, height=dp(220))
        karte.add_widget(label(self.t("success"), 25, 44, bold=True, color=GRUEN))
        karte.add_widget(label(self.aktuelle_grammatik_lektion, 16, 32, bold=True, color=BLAU))
        karte.add_widget(label(self.t("score", p=self.quiz_punkte, m=gesamt, l=self.quiz_leben), 16, 42, bold=True, color=TEXT_HELL))
        self.add_widget(karte)

        fertig_btn = knopf(self.t("to_grammar_menu"), groesse=18, hoehe=60, farbe=BLAU)
        fertig_btn.bind(on_release=self.zeige_grammatik_menue)
        self.add_widget(fertig_btn)
        self.add_widget(Widget(size_hint_y=1))

    # ---------- 3A. Vokabel-Lektionen-Menü ----------
    def zeige_lektionen_menue(self, *args):
        self.bildschirm_leeren()
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=[0, 0, 0, dp(20)])
        layout.bind(minimum_height=layout.setter('height'))

        zurueck = knopf(self.t("back_learn"), groesse=16, hoehe=48, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_lernen_menue)
        layout.add_widget(zurueck)

        layout.add_widget(label(self.t("vocab_lessons"), 22, 50, bold=True, color=BLAU))
        layout.add_widget(label(self.t("choose_lesson"), 16, 30, color=TEXT_MUTED))

        if not self.lektionen:
            layout.add_widget(label(self.t("no_content"), 15, 60, color=TEXT_MUTED))

        for lektions_titel, vokabel_liste in self.lektionen.items():
            anzeige_titel = self.lektions_titel(lektions_titel)

            anzahl_gelernt = len(self.fortschritt.get(lektions_titel, []))
            gesamt = len(vokabel_liste)

            ist_komplett = (gesamt > 0 and anzahl_gelernt >= gesamt)
            farbe = GRUEN if ist_komplett else BLAU
            status_text = f"  ✓ ({anzahl_gelernt}/{gesamt})" if ist_komplett else f"  ({anzahl_gelernt}/{gesamt})"
            btn = knopf(f"{anzeige_titel}{status_text}", groesse=15, hoehe=56, farbe=farbe)
            btn.bind(on_release=lambda b, lt=lektions_titel: self.starte_lektion(lt, ist_phrasen=False))
            layout.add_widget(btn)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    # ---------- 3B. Alltagsphrasen-Kategorien-Menü ----------
    def zeige_phrasen_kategorien_menue(self, *args):
        self.bildschirm_leeren()
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=[0, 0, 0, dp(20)])
        layout.bind(minimum_height=layout.setter('height'))

        zurueck = knopf(self.t("back_learn"), groesse=16, hoehe=48, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_lernen_menue)
        layout.add_widget(zurueck)

        layout.add_widget(label(self.t("phrases"), 22, 50, bold=True, color=BLAU))
        layout.add_widget(label(self.t("choose_cat"), 16, 30, color=TEXT_MUTED))

        if not self.phrasen_daten:
            layout.add_widget(label(self.t("no_content"), 15, 60, color=TEXT_MUTED))

        for kat_titel, phrasen_liste in self.phrasen_daten.items():
            anzahl_gelernt = len(self.fortschritt.get(kat_titel, []))
            gesamt = len(phrasen_liste)

            ist_komplett = (gesamt > 0 and anzahl_gelernt >= gesamt)
            farbe = GRUEN if ist_komplett else BLAU
            status_text = f"  ✓ ({anzahl_gelernt}/{gesamt})" if ist_komplett else f"  ({anzahl_gelernt}/{gesamt})"
            btn = knopf(f"{kat_titel}{status_text}", groesse=15, hoehe=56, farbe=farbe)
            btn.bind(on_release=lambda b, kt=kat_titel: self.starte_lektion(kt, ist_phrasen=True))
            layout.add_widget(btn)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    # ---------- Lektion starten ----------
    def starte_lektion(self, titel, ist_phrasen=False):
        self.aktive_lektion_key = titel
        if ist_phrasen:
            alle_karten = self.phrasen_daten[titel]
            self.aktiver_titel = titel
            self.ruecksprung_funktion = self.zeige_phrasen_kategorien_menue
        else:
            alle_karten = self.lektionen[titel]
            self.aktiver_titel = self.lektions_titel(titel)
            self.ruecksprung_funktion = self.zeige_lektionen_menue

        gelernte = {self.karten_schluessel(k) for k in self.fortschritt.get(titel, [])}
        offene_karten = [k for k in alle_karten if self.karten_schluessel(k) not in gelernte]

        if not offene_karten:
            offene_karten = list(alle_karten)
            self.fortschritt[titel] = []
            self.speichere_fortschritt()

        if not offene_karten:
            return

        self.aktuelle_vokabeln = list(offene_karten)
        random.shuffle(self.aktuelle_vokabeln)
        self.karten_index = 0
        self.ist_umgedreht = False
        self.zeige_lern_ansicht()

    # ---------- Wiederholungs-Stapel starten ----------
    def starte_wiederholung_stapel(self, *args):
        alle_gelernten = []
        for kat, karten in self.fortschritt.items():
            if isinstance(karten, list) and kat != "grammatik_abgeschlossen":
                alle_gelernten.extend(karten)

        if not alle_gelernten:
            self.zeige_platzhalter_info(self.t("nothing_learned"))
            return

        self.aktive_lektion_key = ""
        self.aktuelle_vokabeln = list(alle_gelernten)
        random.shuffle(self.aktuelle_vokabeln)
        self.aktiver_titel = self.t("review_title")
        self.ruecksprung_funktion = self.zeige_hauptmenue
        self.karten_index = 0
        self.ist_umgedreht = False
        self.zeige_lern_ansicht()

    def zeige_lern_ansicht(self, feedback_text="", vorlesen=True):
        self.bildschirm_leeren()

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        zurueck = knopf(self.t("back_short"), groesse=16, hoehe=52, farbe=GRAU, size_hint_x=None, width=dp(90))
        zurueck.bind(on_release=lambda x: self.ruecksprung_funktion())
        top.add_widget(zurueck)
        top.add_widget(label(self.aktiver_titel, 13, bold=True, color=BLAU))
        self.add_widget(top)

        gesamt = len(self.aktuelle_vokabeln)
        quote = (self.karten_index + 1) / max(1, gesamt)
        self.add_widget(FortschrittsBalken(fortschritt_wert=quote, fuell_farbe=BLAU))

        if feedback_text:
            self.add_widget(label(feedback_text, 17, 36, bold=True, color=(0.94, 0.76, 0.06, 1)))

        self.add_widget(label(self.t("card_n", n=self.karten_index + 1, m=gesamt), 14, 28, color=TEXT_MUTED))

        vokabel = self.aktuelle_vokabeln[self.karten_index]
        vorne, hinten = self.karten_texte(vokabel)

        if not self.ist_umgedreht and vorlesen:
            self.sprache_abspielen(vorne)

        seitenname = self.sprachname(self.lern_sprache if not self.ist_umgedreht else self.app_sprache).upper()

        karte = KarteBox(rand_farbe=KARTE_RAND_BLAU if not self.ist_umgedreht else KARTE_RAND)
        karte.add_widget(label(seitenname, 13, 30, bold=True, color=BLAU))
        karte.add_widget(label(vorne if not self.ist_umgedreht else hinten, 31, bold=True, color=TEXT_HELL))
        karte.add_widget(label(self.t("tap_flip"), 13, 28, color=TEXT_MUTED))
        self.add_widget(karte)

        aktion = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140), spacing=dp(10), padding=[0, dp(8), 0, dp(8)])

        if not self.ist_umgedreht:
            hoeren = knopf(self.t("listen_again", lang=self.sprachname(self.lern_sprache)), groesse=16, hoehe=56, farbe=BLAU_DUNKEL)
            hoeren.bind(on_release=lambda x: self.sprache_abspielen(vorne))
            drehen = knopf(self.t("flip"), groesse=18, hoehe=56, farbe=BLAU)
            drehen.bind(on_release=lambda x: self.karte_umdrehen())
            aktion.add_widget(hoeren)
            aktion.add_widget(drehen)
        else:
            zurueck_dreh = knopf(self.t("flip_back"), groesse=16, hoehe=56, farbe=BLAU_DUNKEL)
            zurueck_dreh.bind(on_release=lambda x: self.karte_umdrehen())
            aktion.add_widget(zurueck_dreh)

            reihe = BoxLayout(spacing=dp(12))
            nochmal = knopf(self.t("study_again"), groesse=16, hoehe=56, farbe=GRAU)
            nochmal.bind(on_release=lambda x: self.naechste_karte(wiederholen=True))
            gewusst = knopf(self.t("known"), groesse=16, hoehe=56, farbe=BLAU)
            gewusst.bind(on_release=lambda x: self.naechste_karte(wiederholen=False))
            reihe.add_widget(nochmal)
            reihe.add_widget(gewusst)
            aktion.add_widget(reihe)

        self.add_widget(aktion)

    def karte_umdrehen(self):
        self.ist_umgedreht = not self.ist_umgedreht
        self.zeige_lern_ansicht(vorlesen=False)

    def naechste_karte(self, wiederholen=False):
        aktuelle_karte = self.aktuelle_vokabeln[self.karten_index]

        if wiederholen:
            feedback = self.t("fb_again")
            wort = self.aktuelle_vokabeln.pop(self.karten_index)
            self.aktuelle_vokabeln.append(wort)
        else:
            feedback = self.t("fb_good")
            if self.aktive_lektion_key:
                if self.aktive_lektion_key not in self.fortschritt:
                    self.fortschritt[self.aktive_lektion_key] = []

                if aktuelle_karte not in self.fortschritt[self.aktive_lektion_key]:
                    self.fortschritt[self.aktive_lektion_key].append(aktuelle_karte)
                    self.speichere_fortschritt()

            self.karten_index += 1

        self.ist_umgedreht = False

        if self.karten_index >= len(self.aktuelle_vokabeln):
            self.zeige_fertig_bildschirm()
        else:
            self.zeige_lern_ansicht(feedback_text=feedback)

    def zeige_fertig_bildschirm(self):
        self.bildschirm_leeren()
        self.add_widget(Widget(size_hint_y=1))

        karte = KarteBox(rand_farbe=GRUEN, size_hint_y=None, height=dp(200))
        karte.add_widget(label(self.t("lesson_done"), 25, 44, bold=True, color=GRUEN))
        karte.add_widget(label(self.aktiver_titel, 16, 32, bold=True, color=BLAU))
        karte.add_widget(label(self.t("lesson_done_msg"), 15, 50, color=TEXT_MUTED))
        self.add_widget(karte)

        neu = knopf(self.t("to_menu"), groesse=18, hoehe=60, farbe=BLAU)
        neu.bind(on_release=lambda x: self.ruecksprung_funktion())
        self.add_widget(neu)
        self.add_widget(Widget(size_hint_y=1))


class VokabelApp(App):
    def build(self):
        self.title = "Lern-App"
        return VokabelRootLayout()


if __name__ == '__main__':
    VokabelApp().run()
