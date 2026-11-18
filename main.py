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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

# Fenstergröße nur am PC im Handy-Format
if platform != "android":
    Window.size = (420, 720)
Window.clearcolor = (0.07, 0.07, 0.07, 1)

BASIS = os.path.dirname(os.path.abspath(__file__))


def lade_lektionen(dateipfad):
    with open(dateipfad, encoding="utf-8") as f:
        return json.load(f)


class VokabelRootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15

        self.sound = None
        self.fehler = ""
        try:
            self.lektionen = lade_lektionen(os.path.join(BASIS, "vokabeln.json"))
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
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12)
        layout.bind(minimum_height=layout.setter('height'))

        for img_datei in ["logo.png", "logo.gif"]:
            pfad = os.path.join(BASIS, img_datei)
            if os.path.exists(pfad):
                try:
                    layout.add_widget(Image(source=pfad, size_hint_y=None, height=260))
                    break
                except Exception:
                    pass

        titel = Label(text="Merhaba! Ne öğrenmek istiyorsun?", font_size=18, bold=True,
                      color=(0.90, 0.22, 0.27, 1), size_hint_y=None, height=40)
        untertitel = Label(text="Lütfen bir ders seç:", font_size=13,
                           color=(0.70, 0.70, 0.70, 1), size_hint_y=None, height=30)
        layout.add_widget(titel)
        layout.add_widget(untertitel)

        if self.fehler:
            fehler_lbl = Label(text=self.fehler, font_size=12, color=(1, 0.4, 0.4, 1),
                               size_hint_y=None, height=120, halign='center')
            fehler_lbl.bind(size=fehler_lbl.setter('text_size'))
            layout.add_widget(fehler_lbl)

        for lektions_titel, vokabel_liste in self.lektionen.items():
            btn = Button(
                text=f"{lektions_titel}  ({len(vokabel_liste)} kelime)",
                font_size=14, bold=True, size_hint_y=None, height=50,
                background_normal='', background_color=(0.75, 0.15, 0.15, 1)
            )
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

        top_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        zurueck_btn = Button(text="< Menü", size_hint_x=None, width=90,
                             background_normal='', background_color=(0.25, 0.25, 0.25, 1))
        zurueck_btn.bind(on_release=self.zeige_hauptmenue)
        titel_lbl = Label(text=self.aktiver_titel, font_size=12, bold=True,
                          color=(0.90, 0.22, 0.27, 1))
        top_layout.add_widget(zurueck_btn)
        top_layout.add_widget(titel_lbl)
        self.add_widget(top_layout)

        if feedback_text:
            self.add_widget(Label(text=feedback_text, font_size=16, bold=True,
                                  color=(0.94, 0.76, 0.06, 1), size_hint_y=None, height=35))

        gesamt = len(self.aktuelle_vokabeln)
        self.add_widget(Label(text=f"Kart {self.karten_index + 1} / {gesamt}", font_size=12,
                              color=(0.70, 0.70, 0.70, 1), size_hint_y=None, height=30))

        vokabel = self.aktuelle_vokabeln[self.karten_index]

        if not self.ist_umgedreht:
            self.sprache_abspielen(vokabel["de"])

        karten_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        sprache_text = "Almanca" if not self.ist_umgedreht else "Türkçe"
        wort_text = vokabel["de"] if not self.ist_umgedreht else vokabel["tr"]

        sprache_lbl = Label(text=sprache_text, font_size=13, bold=True,
                            color=(0.80, 0.30, 0.30, 1), size_hint_y=None, height=30)
        wort_lbl = Label(text=wort_text, font_size=24, bold=True, color=(1, 1, 1, 1),
                         halign='center', valign='middle')
        wort_lbl.bind(size=wort_lbl.setter('text_size'))
        hinweis_lbl = Label(text="(Çevirmek için alttaki butona tıkla)", font_size=10,
                            color=(0.50, 0.50, 0.50, 1), size_hint_y=None, height=25)

        karten_layout.add_widget(sprache_lbl)
        karten_layout.add_widget(wort_lbl)
        karten_layout.add_widget(hinweis_lbl)
        self.add_widget(karten_layout)

        action_layout = BoxLayout(size_hint_y=None, height=55, spacing=15, padding=[0, 10, 0, 10])

        if not self.ist_umgedreht:
            umdreh_btn = Button(text="Kartı Çevir", font_size=15, bold=True,
                                background_normal='', background_color=(0.75, 0.15, 0.15, 1))
            umdreh_btn.bind(on_release=lambda x: self.karte_umdrehen())
            action_layout.add_widget(umdreh_btn)
        else:
            nochmal_btn = Button(text="Tekrar Çalış", font_size=14, bold=True,
                                 background_normal='', background_color=(0.35, 0.35, 0.35, 1))
            nochmal_btn.bind(on_release=lambda x: self.naechste_karte(wiederholen=True))
            gewusst_btn = Button(text="Biliyorum!", font_size=14, bold=True,
                                 background_normal='', background_color=(0.75, 0.15, 0.15, 1))
            gewusst_btn.bind(on_release=lambda x: self.naechste_karte(wiederholen=False))
            action_layout.add_widget(nochmal_btn)
            action_layout.add_widget(gewusst_btn)

        self.add_widget(action_layout)

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

        feuer_lbl = Label(text="Harika! Ders bitti!", font_size=20, bold=True,
                          color=(0.85, 0.20, 0.20, 1), size_hint_y=None, height=50)
        info_lbl = Label(text="Bu dersteki bütün kelimeleri başarıyla tamamladın!", font_size=13,
                         color=(0.70, 0.70, 0.70, 1), size_hint_y=None, height=40)
        neu_btn = Button(text="Ders Seçimine Dön", font_size=15, bold=True,
                         size_hint=(None, None), size=(280, 50),
                         background_normal='', background_color=(0.75, 0.15, 0.15, 1))
        neu_btn.bind(on_release=self.zeige_hauptmenue)

        self.add_widget(feuer_lbl)
        self.add_widget(info_lbl)
        self.add_widget(neu_btn)


class VokabelApp(App):
    def build(self):
        self.title = "Deutsch – Türkisch Lern-App"
        return VokabelRootLayout()


if __name__ == '__main__':
    VokabelApp().run()
