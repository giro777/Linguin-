import os
import json
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
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

if platform != "android":
    Window.size = (420, 720)
Window.clearcolor = (0.07, 0.07, 0.07, 1)

BASIS = os.path.dirname(os.path.abspath(__file__))
ROT = (0.75, 0.15, 0.15, 1)
GRAU = (0.35, 0.35, 0.35, 1)


def lade_lektionen():
    for pfad in (os.path.join(BASIS, "Data", "vokabeln.json"),
                 os.path.join(BASIS, "data", "vokabeln.json"),
                 os.path.join(BASIS, "vokabeln.json")):
        if os.path.exists(pfad):
            with open(pfad, encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("vokabeln.json nicht gefunden")


def label(text, groesse, hoehe=None, **kw):
    """Label mit Zeilenumbruch, zentriert, skaliert mit sp/dp."""
    lbl = Label(text=text, font_size=sp(groesse), halign='center',
                valign='middle', **kw)
    if hoehe:
        lbl.size_hint_y = None
        lbl.height = dp(hoehe)
    lbl.bind(size=lambda w, s: setattr(w, 'text_size', (s[0], None)))
    return lbl


def knopf(text, groesse=16, hoehe=56, farbe=ROT, **kw):
    btn = Button(text=text, font_size=sp(groesse), bold=True,
                 halign='center', valign='middle',
                 background_normal='', background_color=farbe, **kw)
    btn.size_hint_y = None
    btn.height = dp(hoehe)
    btn.bind(size=lambda w, s: setattr(w, 'text_size', (s[0] - dp(16), s[1])))
    return btn


class VokabelRootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(10)

        self.sound = None
        self.fehler = ""
        try:
            self.lektionen = lade_lektionen()
        except Exception as e:
            print(f"Ladefehler: {e}")
            self.fehler = f"vokabeln.json nicht gefunden oder defekt:\n{e}"
            self.lektionen = {}

        self.aktuelle_vokabeln = []
        self.karten_index = 0
        self.ist_umgedreht = False
        self.aktiver_titel = ""

        self.zeige_hauptmenue()

    def bildschirm_leeren(self):
        self.clear_widgets()

    # ---------- Sprachausgabe ----------
    def sprache_abspielen(self, text):
        def lade():
            try:
                name = hashlib.md5(text.encode("utf-8")).hexdigest() + ".mp3"
                pfad = os.path.join(App.get_running_app().user_data_dir, name)
                if not os.path.exists(pfad):
                    gTTS(text=text, lang='de').save(pfad)
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

    # ---------- Hauptmenü ----------
    def zeige_hauptmenue(self, *args):
        self.bildschirm_leeren()

        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None,
                           spacing=dp(10), padding=[0, 0, 0, dp(20)])
        layout.bind(minimum_height=layout.setter('height'))

        for img_datei in ["logo.png", "logo.gif"]:
            pfad = os.path.join(BASIS, img_datei)
            if os.path.exists(pfad):
                try:
                    layout.add_widget(Image(source=pfad, size_hint_y=None,
                                            height=dp(160)))
                    break
                except Exception:
                    pass

        layout.add_widget(label("Merhaba! Ne öğrenmek istiyorsun?", 22, 60,
                                bold=True, color=(0.90, 0.22, 0.27, 1)))
        layout.add_widget(label("Lütfen bir ders seç:", 16, 36,
                                color=(0.70, 0.70, 0.70, 1)))

        if self.fehler:
            layout.add_widget(label(self.fehler, 14, 120,
                                    color=(1, 0.4, 0.4, 1)))

        for lektions_titel, vokabel_liste in self.lektionen.items():
            btn = knopf(f"{lektions_titel}  ({len(vokabel_liste)} kelime)",
                        groesse=16, hoehe=60)
            btn.bind(on_release=lambda b, lt=lektions_titel: self.starte_lektion(lt))
            layout.add_widget(btn)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    # ---------- Lektion ----------
    def starte_lektion(self, lektions_titel):
        self.aktuelle_vokabeln = list(self.lektionen[lektions_titel])
        random.shuffle(self.aktuelle_vokabeln)
        self.karten_index = 0
        self.ist_umgedreht = False
        self.aktiver_titel = lektions_titel
        self.zeige_lern_ansicht()

    def zeige_lern_ansicht(self, feedback_text=""):
        self.bildschirm_leeren()

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        zurueck = knopf("< Menü", groesse=16, hoehe=52, farbe=(0.25, 0.25, 0.25, 1),
                        size_hint_x=None, width=dp(100))
        zurueck.bind(on_release=self.zeige_hauptmenue)
        top.add_widget(zurueck)
        top.add_widget(label(self.aktiver_titel, 14, bold=True,
                             color=(0.90, 0.22, 0.27, 1)))
        self.add_widget(top)

        if feedback_text:
            self.add_widget(label(feedback_text, 18, 40, bold=True,
                                  color=(0.94, 0.76, 0.06, 1)))

        gesamt = len(self.aktuelle_vokabeln)
        self.add_widget(label(f"Kart {self.karten_index + 1} / {gesamt}", 15, 36,
                              color=(0.70, 0.70, 0.70, 1)))

        vokabel = self.aktuelle_vokabeln[self.karten_index]

        if not self.ist_umgedreht:
            self.sprache_abspielen(vokabel["de"])

        karte = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        karte.add_widget(label("Almanca" if not self.ist_umgedreht else "Türkçe",
                               16, 36, bold=True, color=(0.85, 0.35, 0.35, 1)))
        karte.add_widget(label(vokabel["de"] if not self.ist_umgedreht else vokabel["tr"],
                               36, bold=True, color=(1, 1, 1, 1)))
        karte.add_widget(label("(Çevirmek için alttaki butona tıkla)", 13, 32,
                               color=(0.55, 0.55, 0.55, 1)))
        self.add_widget(karte)

        aktion = BoxLayout(size_hint_y=None, height=dp(72), spacing=dp(12),
                           padding=[0, dp(8), 0, dp(8)])

        if not self.ist_umgedreht:
            b = knopf("Kartı Çevir", groesse=18, hoehe=56)
            b.bind(on_release=lambda x: self.karte_umdrehen())
            aktion.add_widget(b)
        else:
            nochmal = knopf("Tekrar Çalış", groesse=16, hoehe=56, farbe=GRAU)
            nochmal.bind(on_release=lambda x: self.naechste_karte(wiederholen=True))
            gewusst = knopf("Biliyorum!", groesse=16, hoehe=56)
            gewusst.bind(on_release=lambda x: self.naechste_karte(wiederholen=False))
            aktion.add_widget(nochmal)
            aktion.add_widget(gewusst)

        self.add_widget(aktion)

    def karte_umdrehen(self):
        self.ist_umgedreht = not self.ist_umgedreht
        self.zeige_lern_ansicht()

    def naechste_karte(self, wiederholen=False):
        if wiederholen:
            feedback = "Bunu tekrar çalışacağız!"
            wort = self.aktuelle_vokabeln.pop(self.karten_index)
            self.aktuelle_vokabeln.append(wort)
        else:
            feedback = "Harika! Süpersin!"
            self.karten_index += 1

        self.ist_umgedreht = False

        if self.karten_index >= len(self.aktuelle_vokabeln):
            self.zeige_fertig_bildschirm()
        else:
            self.zeige_lern_ansicht(feedback_text=feedback)

    def zeige_fertig_bildschirm(self):
        self.bildschirm_leeren()
        self.add_widget(label("Harika! Ders bitti!", 26, bold=True,
                              color=(0.90, 0.25, 0.25, 1)))
        self.add_widget(label("Bu dersteki bütün kelimeleri başarıyla tamamladın!", 16,
                              color=(0.70, 0.70, 0.70, 1)))
        neu = knopf("Ders Seçimine Dön", groesse=18, hoehe=60)
        neu.bind(on_release=self.zeige_hauptmenue)
        self.add_widget(neu)


class VokabelApp(App):
    def build(self):
        self.title = "Deutsch – Türkisch Lern-App"
        return VokabelRootLayout()


if __name__ == '__main__':
    VokabelApp().run()
