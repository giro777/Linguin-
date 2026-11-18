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
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.utils import platform

if platform != "android":
    Window.size = (420, 720)
Window.clearcolor = (0.07, 0.07, 0.07, 1)

BASIS = os.path.dirname(os.path.abspath(__file__))

# --- EXAKTER LOGO-BLAUTON ---
BLAU = (0.125, 0.639, 0.996, 1)     
BLAU_DUNKEL = (0.09, 0.48, 0.78, 1) 
GRAU = (0.35, 0.35, 0.35, 1)

# --- VOKABEL-LEKTIONEN (18 Lektionen) ---
LEKTIONS_UEBERSETZUNG = {
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
    "Lektion 11: Stadt, Orte & Reisen": "Seyahat ve Coğrafya",
    "Lektion 12: Arbeit, Bildung & Wissenschaft": "Eşyalar ve Malzemeler",
    "Lektion 13: Sprache, Musik & Kunst": "İş ve Meslek",
    "Lektion 14: Gefühle, Eigenschaften & Zustände": "Duygular ve Durum",
    "Lektion 15: Verben: Bewegung & Alltag": "Bilim ve Teknoloji",
    "Lektion 16: Verben: Denken, Kommunikation & Wahrnehmung": "Kültür ve Sanat",
    "Lektion 17: Pronomen & Artikel": "Spor ve Boş Zaman",
    "Lektion 18: Präpositionen, Konjunktionen & Adverbien": "Genel Fiiller ve Sıfatlar"
}


def lade_json_datei(dateiname):
    for pfad in (os.path.join(BASIS, "Data", dateiname),
                 os.path.join(BASIS, "data", dateiname),
                 os.path.join(BASIS, dateiname)):
        if os.path.exists(pfad):
            with open(pfad, encoding="utf-8") as f:
                return json.load(f)
    return {}


def speichere_json_datei(dateiname, daten):
    try:
        pfad = os.path.join(BASIS, "data", dateiname)
        if not os.path.exists(os.path.dirname(pfad)):
            os.makedirs(os.path.dirname(pfad), exist_ok=True)
        with open(pfad, "w", encoding="utf-8") as f:
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


def knopf(text, groesse=16, hoehe=56, farbe=BLAU, **kw):
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
        self.lektionen = lade_json_datei("vokabeln.json")
        self.phrasen_daten = lade_json_datei("phrasen.json")
        
        # Fortschritt laden: { "kategorie_oder_lektion": [ {"de": "...", "tr": "..."}, ... ] }
        self.fortschritt = lade_json_datei("fortschritt.json")

        self.aktuelle_vokabeln = []
        self.karten_index = 0
        self.ist_umgedreht = False
        self.aktiver_titel = ""
        self.aktive_lektion_key = ""
        self.ruecksprung_funktion = self.zeige_hauptmenue

        self.zeige_hauptmenue()

    def bildschirm_leeren(self):
        self.clear_widgets()

    def logo_hinzufuegen(self, layout):
        for img_datei in ["logo.png", "logo.gif"]:
            pfad = os.path.join(BASIS, img_datei)
            if os.path.exists(pfad):
                try:
                    layout.add_widget(Image(source=pfad, size_hint_y=None,
                                            height=dp(150)))
                    break
                except Exception:
                    pass

    # ---------- Sprachausgabe (gTTS) ----------
    def sprache_abspielen(self, text):
        def lade():
            try:
                name = hashlib.md5(text.encode("utf-8")).hexdigest() + ".mp3"
                pfad = os.path.join(App.get_running_app().user_data_dir, name)
                if not os.path.exists(pfad):
                    tts = gTTS(text=text, lang='de')
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

    # ---------- 1. Hauptmenü (Start) ----------
    def zeige_hauptmenue(self, *args):
        self.bildschirm_leeren()

        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None,
                           spacing=dp(15), padding=[0, dp(10), 0, dp(20)])
        layout.bind(minimum_height=layout.setter('height'))

        self.logo_hinzufuegen(layout)

        layout.add_widget(label("Merhaba! Hoş geldin!", 24, 50, bold=True, color=BLAU))
        layout.add_widget(label("Ne yapmak istiyorsun?", 16, 30, color=(0.70, 0.70, 0.70, 1)))

        btn_lernen = knopf("Öğren (Lernen)", groesse=18, hoehe=64)
        btn_lernen.bind(on_release=self.zeige_lernen_menue)
        layout.add_widget(btn_lernen)

        btn_wiederholen = knopf("Tekrar (Wiederholung)", groesse=18, hoehe=64, farbe=BLAU_DUNKEL)
        btn_wiederholen.bind(on_release=self.starte_wiederholung_stapel)
        layout.add_widget(btn_wiederholen)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    # ---------- 2. Untermenü: Lernen ----------
    def zeige_lernen_menue(self, *args):
        self.bildschirm_leeren()

        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None,
                           spacing=dp(15), padding=[0, dp(10), 0, dp(20)])
        layout.bind(minimum_height=layout.setter('height'))

        zurueck = knopf("< Ana Menü", groesse=16, hoehe=48, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_hauptmenue)
        layout.add_widget(zurueck)

        self.logo_hinzufuegen(layout)

        layout.add_widget(label("Öğrenme Alanı", 22, 50, bold=True, color=BLAU))
        layout.add_widget(label("Lütfen bir kategori seç:", 16, 30, color=(0.70, 0.70, 0.70, 1)))

        btn_vokabeln = knopf("Kelime Kartları (Vokabeln)", groesse=18, hoehe=60)
        btn_vokabeln.bind(on_release=self.zeige_lektionen_menue)
        layout.add_widget(btn_vokabeln)

        btn_phrasen = knopf("Günlük İfadeler (Alltagsphrasen)", groesse=18, hoehe=60, farbe=BLAU_DUNKEL)
        btn_phrasen.bind(on_release=self.zeige_phrasen_kategorien_menue)
        layout.add_widget(btn_phrasen)

        btn_grammatik = knopf("Gramer (Grammatik)", groesse=18, hoehe=60, farbe=BLAU_DUNKEL)
        btn_grammatik.bind(on_release=lambda x: self.zeige_platzhalter_info("Grammatik kommt bald!"))
        layout.add_widget(btn_grammatik)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def zeige_platzhalter_info(self, nachricht):
        self.bildschirm_leeren()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        layout.add_widget(label(nachricht, 20, 60, bold=True, color=BLAU))
        layout.add_widget(label("Bu özellik yakında eklenecektir.", 16, 40, color=(0.7, 0.7, 0.7, 1)))
        
        zurueck = knopf("Geri Dön", groesse=16, hoehe=56)
        zurueck.bind(on_release=self.zeige_lernen_menue)
        layout.add_widget(zurueck)
        self.add_widget(layout)

    # ---------- 3A. Vokabel-Lektionen-Menü ----------
    def zeige_lektionen_menue(self, *args):
        self.bildschirm_leeren()
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=[0, 0, 0, dp(20)])
        layout.bind(minimum_height=layout.setter('height'))

        zurueck = knopf("< Öğrenme Menüsü", groesse=16, hoehe=48, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_lernen_menue)
        layout.add_widget(zurueck)

        layout.add_widget(label("Kelime Dersleri", 22, 50, bold=True, color=BLAU))
        layout.add_widget(label("Lütfen bir ders seç:", 16, 30, color=(0.70, 0.70, 0.70, 1)))

        for lektions_titel, vokabel_liste in self.lektionen.items():
            tuerkisch_titel = LEKTIONS_UEBERSETZUNG.get(lektions_titel, lektions_titel)
            
            # Fortschritt berechnen (wie viele bereits gelernt)
            gelernte_liste = self.fortschritt.get(lektions_titel, [])
            anzahl_gelernt = len(gelernte_liste)
            gesamt = len(vokabel_liste)
            
            status_text = f"  ({anzahl_gelernt}/{gesamt})"
            btn = knopf(f"{tuerkisch_titel}{status_text}", groesse=15, hoehe=56)
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

        zurueck = knopf("< Öğrenme Menüsü", groesse=16, hoehe=48, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_lernen_menue)
        layout.add_widget(zurueck)

        layout.add_widget(label("Günlük İfadeler", 22, 50, bold=True, color=BLAU))
        layout.add_widget(label("Lütfen bir kategori seç:", 16, 30, color=(0.70, 0.70, 0.70, 1)))

        for kat_titel, phrasen_liste in self.phrasen_daten.items():
            gelernte_liste = self.fortschritt.get(kat_titel, [])
            anzahl_gelernt = len(gelernte_liste)
            gesamt = len(phrasen_liste)

            status_text = f"  ({anzahl_gelernt}/{gesamt})"
            btn = knopf(f"{kat_titel}{status_text}", groesse=15, hoehe=56, farbe=BLAU_DUNKEL)
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
            self.aktiver_titel = LEKTIONS_UEBERSETZUNG.get(titel, titel)
            self.ruecksprung_funktion = self.zeige_lektionen_menue

        # Nur jene Karten anzeigen, die NOCH NICHT als gelernt markiert wurden
        gelernte = self.fortschritt.get(titel, [])
        gelernte_tupel = {(k["de"], k["tr"]) for k in gelernte}

        # Restkarten filtern
        offene_karten = [k for k in alle_karten if (k["de"], k["tr"]) not in gelernte_tupel]

        if not offene_karten:
            # Falls bereits alle gelernt wurden, fragen ob man sie zurücksetzen oder wiederholen möchte
            offene_karten = list(alle_karten)
            # Fortschritt für diesen Bereich kurzzeitig leeren für den Durchlauf
            self.fortschritt[titel] = []
            speichere_json_datei("fortschritt.json", self.fortschritt)

        self.aktuelle_vokabeln = list(offene_karten)
        random.shuffle(self.aktuelle_vokabeln)
        self.karten_index = 0
        self.ist_umgedreht = False
        self.zeige_lern_ansicht()

    # ---------- Wiederholungs-Stapel starten ----------
    def starte_wiederholung_stapel(self, *args):
        # Alle gelernten Karten aus allen Kategorien sammeln
        alle_gelernten = []
        for kat, karten in self.fortschritt.items():
            if isinstance(karten, list):
                alle_gelernten.extend(karten)

        if not alle_gelernten:
            self.zeige_platzhalter_info("Henüz öğrenilmiş kart yok!\nÖnce biraz kelime veya ifade öğrenin.")
            return

        self.aktive_lektion_key = "" # Kein einzelner Schlüssel
        self.aktuelle_vokabeln = list(alle_gelernten)
        random.shuffle(self.aktuelle_vokabeln)
        self.aktiver_titel = "Tekrar (Wiederholung)"
        self.ruecksprung_funktion = self.zeige_hauptmenue
        self.karten_index = 0
        self.ist_umgedreht = False
        self.zeige_lern_ansicht()

    def zeige_lern_ansicht(self, feedback_text="", vorlesen=True):
        self.bildschirm_leeren()

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        zurueck = knopf("< Geri", groesse=16, hoehe=52, farbe=GRAU, size_hint_x=None, width=dp(90))
        zurueck.bind(on_release=lambda x: self.ruecksprung_funktion())
        top.add_widget(zurueck)
        top.add_widget(label(self.aktiver_titel, 13, bold=True, color=BLAU))
        self.add_widget(top)

        if feedback_text:
            self.add_widget(label(feedback_text, 18, 40, bold=True, color=(0.94, 0.76, 0.06, 1)))

        gesamt = len(self.aktuelle_vokabeln)
        self.add_widget(label(f"Kart {self.karten_index + 1} / {gesamt}", 15, 36, color=(0.70, 0.70, 0.70, 1)))

        vokabel = self.aktuelle_vokabeln[self.karten_index]

        if not self.ist_umgedreht and vorlesen:
            self.sprache_abspielen(vokabel["de"])

        karte = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        karte.add_widget(label("Almanca" if not self.ist_umgedreht else "Türkçe", 16, 36, bold=True, color=BLAU_DUNKEL))
        karte.add_widget(label(vokabel["de"] if not self.ist_umgedreht else vokabel["tr"], 32, bold=True, color=(1, 1, 1, 1)))
        karte.add_widget(label("(Çevirmek için alttaki butona tıkla)", 13, 32, color=(0.55, 0.55, 0.55, 1)))
        self.add_widget(karte)

        aktion = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140), spacing=dp(10), padding=[0, dp(8), 0, dp(8)])

        if not self.ist_umgedreht:
            hoeren = knopf("Tekrar Dinle (Almanca)", groesse=16, hoehe=56, farbe=BLAU_DUNKEL)
            hoeren.bind(on_release=lambda x: self.sprache_abspielen(vokabel["de"]))
            drehen = knopf("Kartı Çevir", groesse=18, hoehe=56)
            drehen.bind(on_release=lambda x: self.karte_umdrehen())
            aktion.add_widget(hoeren)
            aktion.add_widget(drehen)
        else:
            zurueck_dreh = knopf("Almanca'ya Dön", groesse=16, hoehe=56, farbe=BLAU_DUNKEL)
            zurueck_dreh.bind(on_release=lambda x: self.karte_umdrehen())
            aktion.add_widget(zurueck_dreh)

            reihe = BoxLayout(spacing=dp(12))
            nochmal = knopf("Tekrar Çalış", groesse=16, hoehe=56, farbe=GRAU)
            nochmal.bind(on_release=lambda x: self.naechste_karte(wiederholen=True))
            gewusst = knopf("Biliyorum!", groesse=16, hoehe=56)
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
            feedback = "Bunu tekrar çalışacağız!"
            wort = self.aktuelle_vokabeln.pop(self.karten_index)
            self.aktuelle_vokabeln.append(wort)
        else:
            feedback = "Harika! Süpersin!"
            # Wenn es eine normale Lektion ist (kein reiner Wiederholungs-Modus), als gelernt speichern
            if self.aktive_lektion_key:
                if self.aktive_lektion_key not in self.fortschritt:
                    self.fortschritt[self.aktive_lektion_key] = []
                
                # Prüfen ob Karte bereits im Fortschritt ist, falls nicht hinzufügen
                if aktuelle_karte not in self.fortschritt[self.aktive_lektion_key]:
                    self.fortschritt[self.aktive_lektion_key].append(aktuelle_karte)
                    speichere_json_datei("fortschritt.json", self.fortschritt)

            self.karten_index += 1

        self.ist_umgedreht = False

        if self.karten_index >= len(self.aktuelle_vokabeln):
            self.zeige_fertig_bildschirm()
        else:
            self.zeige_lern_ansicht(feedback_text=feedback)

    def zeige_fertig_bildschirm(self):
        self.bildschirm_leeren()
        self.add_widget(label("Harika! Ders bitti!", 26, bold=True, color=BLAU))
        self.add_widget(label("Bu dersteki bütün ifadeleri başarıyla tamamladın!", 16, color=(0.70, 0.70, 0.70, 1)))
        neu = knopf("Menüye Dön", groesse=18, hoehe=60)
        neu.bind(on_release=lambda x: self.ruecksprung_funktion())
        self.add_widget(neu)


class VokabelApp(App):
    def build(self):
        self.title = "Deutsch – Türkisch Lern-App"
        return VokabelRootLayout()


if __name__ == '__main__':
    VokabelApp().run()
