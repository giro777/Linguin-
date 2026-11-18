import math
import os
import random
import docx
from gtts import gTTS

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image

# Fenstergröße für den PC-Test im Handy-Format einstellen
Window.size = (420, 720)
Window.clearcolor = (0.07, 0.07, 0.07, 1)  # Edles Tiefschwarz für den Hintergrund

# Kleines Hilfs-Wörterbuch für passende Emojis neben deutschen Wörtern
EMOJI_MAP = {
    "Tier": "🐾", "Fisch": "🐟", "Pferd": "🐎", "Vogel": "🐦", "Hund": "🐕", "Katze": "🐈", "Kuh": "🐄", "Insekt": "🐛", "Fledermaus": "🦇",
    "Wasser": "💧", "Lebensmittel": "🛒", "Essen": "🍽️", "Ei": "🥚", "Öl": "🛢️", "Milch": "🥛", "Koch": "👨‍🍳", "Obst": "🍎", "Mais": "🌽", "Fleisch": "🥩", "Salz": "🧂", "Zucker": "🍬", "Apfel": "🍏", "Getränk": "🥤",
    "Luft": "💨", "Sonne": "☀️", "Baum": "🌳", "Meer": "🌊", "Stein": "🪨", "Feuer": "🔥", "Mond": "🌙", "Insel": "🏝️", "Schnee": "❄️", "Stern": "⭐", "Ozean": "🌊", "Regen": "🌧️", "Kälte": "🥶", "Eis": "🧊", "Wald": "🌲", "Himmel": "☁️", "Gras": "🌱", "Wetter": "🌤️", "Blume": "🌸", "See": "🏞️", "Wolke": "☁️", "Sand": "🏖️", "Tal": "⛰️",
    "Mutter": "👩", "Vater": "👨", "Mann": "👨", "Junge": "👦", "Mädchen": "👧", "Freund": "🤝", "Kinder": "👶", "König": "👑", "Bruder": "👦", "Soldat": "🖴", "Mensch": "🧍", "Frau": "👩", "Kapitän": "⚓", "Nachbar": "🏠", "Chef": "👔", "Elternteil": "👪", "Papa": "🧔", "Schwester": "👧",
    "Hand": "✋", "Kopf": "🗣️", "Auge": "👁️", "Gesicht": "😊", "Füße": "🦶", "Körper": "👤", "Fuß": "👣", "Herz": "❤️", "Arm": "💪", "Schlaf": "😴", "Bein": "🦵", "Mund": "👄", "Blut": "🩸", "Ohr": "👂", "Haut": "✋", "Haar": "💇", "Finger": "👆", "Arzt": "🩺", "Knochen": "🦴", "Zähne": "🦷", "Nase": "👃",
    "Zeit": "⏳", "Jahr": "📅", "Tag": "☀️", "Nacht": "🌙", "Woche": "📆", "Minute": "⏱️", "Stunde": "⏰", "Morgen": "🌅", "Sommer": "☀️", "Winter": "❄️", "Monat": "🗓️", "Frühling": "🌷", "Abend": "🌆",
    "Zuhause": "🏠", "Haus": "🏡", "Buch": "📖", "Zimmer": "🚪", "Papier": "📄", "Tür": "🚪", "Bett": "🛏️", "Fenster": "🪟", "Wand": "🧱", "Glas": "🥛", "Garten": "🌻", "Schlüssel": "🔑", "Stuhl": "🪑", "Uhr": "🕒", "Karte": "🗺️",
    "Hafen": "⚓", "Land": "🌍", "Stadt": "🏙️", "Auto": "🚗", "Schiff": "🚢", "Straße": "🛣️", "Boot": "⛵", "Flugzeug": "✈️", "Reise": "🧳", "Zug": "🚆", "Bank": "🏦"
}

# Feste, saubere Zuordnung aller 18 Lektionen direkt auf Türkisch nach Nummer
TURKISCHE_LEKTIONEN = {
    1: "Sayılar ve Miktarlar",
    2: "Renkler ve Optik",
    3: "Hayvanlar ve Bitkiler",
    4: "Aile ve İnsanlar",
    5: "Vücut und Sağlık",
    6: "Yemek und İçecek",
    7: "Ev ve Yaşam",
    8: "Doğa und Çevre",
    9: "Hava ve Zaman",
    10: "Şehir ve Ulaşım",
    11: "Seyahat und Coğrafya",
    12: "Eşyalar ve Malzemeler",
    13: "İş und Meslek",
    14: "Duygular ve Durum",
    15: "Bilim und Teknoloji",
    16: "Kültür ve Sanat",
    17: "Spor ve Boş Zaman",
    18: "Genel Fiiller und Sıfatlar"
}

def get_emoji_fuer_wort(de_wort):
    sauber_wort = de_wort.split()[0].strip(",.-")
    if sauber_wort in EMOJI_MAP:
        return EMOJI_MAP[sauber_wort]
    if de_wort in EMOJI_MAP:
        return EMOJI_MAP[de_wort]
    return "💡"

def lade_lektionen_aus_docx(dateipfad):
    doc = docx.Document(dateipfad)
    lektionen = {}
    uebersicht_tabelle = doc.tables[0]
    
    for index, zeile in enumerate(uebersicht_tabelle.rows[1:], start=1):
        thema_tr = TURKISCHE_LEKTIONEN.get(index, f"Ders {index}")
        titel = f"Ders {index}: {thema_tr}"

        if index < len(doc.tables):
            vokabel_tabelle = doc.tables[index]
            vokabeln = []
            for v_zeile in vokabel_tabelle.rows[1:]:
                nr = v_zeile.cells[0].text.strip()
                deutsch = v_zeile.cells[1].text.strip()
                tuerkisch = v_zeile.cells[2].text.strip()
                vokabeln.append({"nr": nr, "de": deutsch, "tr": tuerkisch})
            lektionen[titel] = vokabeln

    return lektionen


class VokabelRootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15

        try:
            self.lektionen = lade_lektionen_aus_docx("Frequenzliste_Deutsch_Tuerkisch_Kategorisiert.docx")
        except Exception as e:
            self.lektionen = {}

        self.aktuelle_vokabeln = []
        self.karten_index = 0
        self.ist_umgedreht = False
        self.aktiver_titel = ""

        self.zeige_hauptmenue()

    def bildschirm_leeren(self):
        self.clear_widgets()

    def sprache_abspielen(self, text):
        try:
            tts = gTTS(text=text, lang='de', slow=False)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_filename = temp_file.name
            temp_file.close()
            tts.save(temp_filename)
            os.system(f"mpg123 -q {temp_filename} &>/dev/null || ffplay -nodisp -autoexit {temp_filename} &>/dev/null || xdg-open {temp_filename} &")
        except Exception as e:
            print(f"Sprachausgabe-Fehler: {e}")

    def spiele_erfolgsglocke(self):
        try:
            print("\a")
        except Exception as e:
            print(f"Glocken-Sound-Fehler: {e}")

    def zeige_hauptmenue(self, *args):
        self.bildschirm_leeren()

        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12)
        layout.bind(minimum_height=layout.setter('height'))

        # Bevorzugt PNG nutzen (unter Linux absolut fehlerfrei für Transparenz)
        bild_geladen = False
        for img_datei in ["logo.png", "logo.gif"]:
            if os.path.exists(img_datei):
                try:
                    logo = Image(source=img_datei, size_hint_y=None, height=260)
                    layout.add_widget(logo)
                    bild_geladen = True
                    break
                except Exception:
                    pass

        if not bild_geladen:
            platzhalter_lbl = Label(text="✨ 🇩🇪 ❤️ 🇹🇷 ✨", font_size=32, size_hint_y=None, height=100, halign='center')
            layout.add_widget(platzhalter_lbl)

        titel = Label(text="Merhaba! Ne öğrenmek istiyorsun?", font_size=18, bold=True, color=(0.90, 0.22, 0.27, 1), size_hint_y=None, height=40)
        untertitel = Label(text="Lütfen bir ders seç:", font_size=13, color=(0.70, 0.70, 0.70, 1), size_hint_y=None, height=30)
        layout.add_widget(titel)
        layout.add_widget(untertitel)

        for lektions_titel, vokabel_liste in self.lektionen.items():
            anzahl = len(vokabel_liste)
            btn = Button(
                text=f"{lektions_titel}  ({anzahl} kelime)",
                font_size=14,
                bold=True,
                size_hint_y=None,
                height=50,
                background_normal='',
                background_color=(0.75, 0.15, 0.15, 1)
            )
            btn.bind(on_release=lambda b, lt=lektions_titel: self.starte_lektion(lt))
            layout.add_widget(btn)

        scroll.add_widget(layout)
        self.add_widget(scroll)

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
        zurueck_btn = Button(text="← Menü", size_hint_x=None, width=90, background_normal='', background_color=(0.25, 0.25, 0.25, 1))
        zurueck_btn.bind(on_release=self.zeige_hauptmenue)
        titel_lbl = Label(text=self.aktiver_titel, font_size=12, bold=True, color=(0.90, 0.22, 0.27, 1))
        top_layout.add_widget(zurueck_btn)
        top_layout.add_widget(titel_lbl)
        self.add_widget(top_layout)

        if feedback_text:
            fb_lbl = Label(text=feedback_text, font_size=16, bold=True, color=(0.94, 0.76, 0.06, 1), size_hint_y=None, height=35)
            self.add_widget(fb_lbl)

        gesamt = len(self.aktuelle_vokabeln)
        fortschritt = Label(text=f"Kart {self.karten_index + 1} / {gesamt}", font_size=12, color=(0.70, 0.70, 0.70, 1), size_hint_y=None, height=30)
        self.add_widget(fortschritt)

        aktuelle_vokabel = self.aktuelle_vokabeln[self.karten_index]
        emoji = get_emoji_fuer_wort(aktuelle_vokabel["de"])

        if not self.ist_umgedreht:
            self.sprache_abspielen(aktuelle_vokabel["de"])

        karten_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        sprache_text = f"🇩🇪 Almanca {emoji}" if not self.ist_umgedreht else "🇹🇷 Türkçe 🌟"
        wort_text = aktuelle_vokabel["de"] if not self.ist_umgedreht else aktuelle_vokabel["tr"]

        sprache_lbl = Label(text=sprache_text, font_size=13, bold=True, color=(0.80, 0.30, 0.30, 1), size_hint_y=None, height=30)
        wort_lbl = Label(text=wort_text, font_size=24, bold=True, color=(1, 1, 1, 1), halign='center', valign='middle')
        wort_lbl.bind(size=wort_lbl.setter('text_size'))
        
        hinweis_lbl = Label(text="(Çevirmek için alttaki butona tıkla)", font_size=10, color=(0.50, 0.50, 0.50, 1), size_hint_y=None, height=25)

        karten_layout.add_widget(sprache_lbl)
        karten_layout.add_widget(wort_lbl)
        karten_layout.add_widget(hinweis_lbl)
        
        self.add_widget(karten_layout)

        action_layout = BoxLayout(size_hint_y=None, height=55, spacing=15, padding=[0, 10, 0, 10])

        if not self.ist_umgedreht:
            umdreh_btn = Button(
                text="🔄 Kartı Çevir",
                font_size=15,
                bold=True,
                background_normal='',
                background_color=(0.75, 0.15, 0.15, 1)
            )
            umdreh_btn.bind(on_release=lambda x: self.karte_umdrehen())
            action_layout.add_widget(umdreh_btn)
        else:
            nochmal_btn = Button(
                text="🔄 Tekrar Çalış",
                font_size=14,
                bold=True,
                background_normal='',
                background_color=(0.35, 0.35, 0.35, 1)
            )
            nochmal_btn.bind(on_release=lambda x: self.naechste_karte(wiederholen=True))

            gewusst_btn = Button(
                text="✨ Biliyorum!",
                font_size=14,
                bold=True,
                background_normal='',
                background_color=(0.75, 0.15, 0.15, 1)
            )
            gewusst_btn.bind(on_release=lambda x: self.naechste_karte(wiederholen=False))

            action_layout.add_widget(nochmal_btn)
            action_layout.add_widget(gewusst_btn)

        self.add_widget(action_layout)

    def karte_umdrehen(self):
        self.ist_umgedreht = not self.ist_umgedreht
        self.zeige_lern_ansicht()

    def naechste_karte(self, wiederholen=False):
        if wiederholen:
            feedback = "📉 Bunu tekrar çalışacağız! 🥺💪"
            wort = self.aktuelle_vokabeln.pop(self.karten_index)
            self.aktuelle_vokabeln.append(wort)
        else:
            feedback = "🔥 Harika! Süpersin! 🎉🚀"
            self.spiele_erfolgsglocke()
            self.karten_index += 1

        self.ist_umgedreht = False

        if self.karten_index >= len(self.aktuelle_vokabeln):
            self.zeige_fertig_bildschirm()
        else:
            self.zeige_lern_ansicht(feedback_text=feedback)

    def zeige_fertig_bildschirm(self):
        self.bildschirm_leeren()
        
        feuer_lbl = Label(text="🎉 Harika! Ders bitti! ❤️", font_size=20, bold=True, color=(0.85, 0.20, 0.20, 1), size_hint_y=None, height=50)
        info_lbl = Label(text="Bu dersteki bütün kelimeleri başarıyla tamamladın!", font_size=13, color=(0.70, 0.70, 0.70, 1), size_hint_y=None, height=40)
        
        neu_btn = Button(
            text="Ders Seçimine Dön",
            font_size=15,
            bold=True,
            size_hint=(None, None),
            size=(280, 50),
            background_normal='',
            background_color=(0.75, 0.15, 0.15, 1)
        )
        neu_btn.bind(on_release=self.zeige_hauptmenue)

        self.add_widget(feuer_lbl)
        self.add_widget(info_lbl)
        self.add_widget(neu_btn)


class VokabelApp(App):
    def build(self):
        self.title = "Deutsch – Türkisch Lern-App ❤️"
        return VokabelRootLayout()


if __name__ == '__main__':
    VokabelApp().run()
        
