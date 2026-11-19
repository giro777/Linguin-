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
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import platform

if platform != "android":
    Window.size = (420, 720)
Window.clearcolor = (0.07, 0.07, 0.07, 1)

BASIS = os.path.dirname(os.path.abspath(__file__))

# --- EXAKTER LOGO-BLAUTON ---
BLAU = (0.125, 0.639, 0.996, 1)
BLAU_DUNKEL = (0.09, 0.48, 0.78, 1)
GRAU = (0.35, 0.35, 0.35, 1)
ROT = (0.85, 0.25, 0.25, 1)
GRUEN = (0.18, 0.72, 0.38, 1)

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

# --- GRAMMATIK-LEKTIONEN ---
GRAMMATIK_LEKTIONEN = {
    "Fiiller 1. Bölüm": {
        "karten": [
            "İlk dil bilgisi dersine hoş geldin!",
            "Bu derste fiillerin (eylem kelimelerinin) Almancada nasıl kullanıldığına birlikte bakacağız.",
            "Uygulamada fiil kartları çoğunlukla mastar halindedir, yani:\n\nögrenmek = lernen\noynamak = spielen\nçalışmak = arbeiten",
            "Şimdi bu kelimeleri aktif forma nasıl dönüştüreceğimizi birlikte öğreneceğiz:\n\nöğreniyorum\noynuyorum\nçalışıyorum",
            "Bunun için bir zamire ihtiyacımız var. Senin için kolay kalması adına, zaten bildiğin bir zamirde kalacağız.",
            "ICH (BEN)",
            "Şimdi fiillere tekrar bakalım:\n\nlernen = öğrenmek\nspielen = oynamak\narbeiten = çalışmak",
            "Onları aktif forma dönüştürmek için önce fiil kökünü oluşturmalıyız:\n\nlernen = öğrenmek\nspielen = oynamak\narbeiten = çalışmak",
            "Bunun için son heceyi, yani -en takısını çıkarıyoruz:\n\nlern = öğrenmek\nspiel = oynamak\narbeit = çalışmak",
            "Ardından zamirimizi ekliyoruz:\n\nIch lern = öğrenmek\nIch spiel = oynamak\nIch arbeit = çalışmak",
            "Son olarak bir kelime sonu eklemeliyiz. Kelime sonu eki her zaman zamire bağlıdır. Ich için bu her zaman bir -e ekidir:\n\nIch lerne = Ben öğreniyorum\nIch spiele = Ben oynuyorum\nIch arbeite = Ben çalışıyorum",
            "Bu neredeyse tüm fiillerde bu şekilde çalışır. Bunlara düzenli fiiller denir.\n\nİşte birkaç örnek daha:\nyapmak | Ich mache = Ben yapıyorum\nduymak / dinlemek | Ich höre = Ben duyuyorum\nsatın almak | Ich kaufe = Ben satın alıyorum",
            "Şimdi işleri biraz daha karmaşık hale getiriyoruz. Yanımıza ikinci bir zamir alıyoruz:",
            "Du (Sen)",
            "Tıpkı önceki gibi fiil kökünü oluşturuyoruz:\n\nDu lern\nDu spiel\nDu arbeit",
            "Tıpkı Ich gibi, Du zamirinin de kendine ait bir eki vardır: -st.\n\nDu lernst\nDu spielst",
            "T veya D ile biten fiil kökleri ve birden fazla sessiz harfle biten fiil köklerini bu şekilde telaffuz etmek zor olurdu, bu yüzden buradaki ek -est olur:\n\nDu arbeitest\nDu öffnest\nDu atmest",
            "İşte birkaç örnek daha:\n\nDu kochst\nDu startest\nDu landest\nDu lachst",
            "Hiç de karmaşık değil, değil mi? O halde küçük bir test deneyelim.\n\nSana Mastar halinde 15 fiil veriyorum ve senin bunları çekimlemen gerekiyor!"
        ],
        "quiz": [
            {"anzeige": "Ich + fehlen = Ich fehl___", "antwort": "-e", "vollstaendig": "Ich fehle"},
            {"anzeige": "Du + duschen = Du dusch___", "antwort": "-st", "vollstaendig": "Du duschst"},
            {"anzeige": "Ich + frühstücken = Ich frühstück___", "antwort": "-e", "vollstaendig": "Ich frühstücke"},
            {"anzeige": "Du + planen = Du plan___", "antwort": "-st", "vollstaendig": "Du planst"},
            {"anzeige": "Ich + duschen = Ich dusch___", "antwort": "-e", "vollstaendig": "Ich dusche"},
            {"anzeige": "Du + trinken = Du trink___", "antwort": "-st", "vollstaendig": "Du trinkst"},
            {"anzeige": "Ich + feiern = Ich feier___", "antwort": "-e", "vollstaendig": "Ich feiere"},
            {"anzeige": "Du + heben = Du heb___", "antwort": "-st", "vollstaendig": "Du hebst"},
            {"anzeige": "Ich + kaufen = Ich kauf___", "antwort": "-e", "vollstaendig": "Ich kaufe"},
            {"anzeige": "Du + reden = Du red___", "antwort": "-est", "vollstaendig": "Du redest"},
            {"anzeige": "Ich + antworten = Ich antwort___", "antwort": "-e", "vollstaendig": "Ich antworte"},
            {"anzeige": "Ich + baden = Ich bad___", "antwort": "-e", "vollstaendig": "Ich bade"},
            {"anzeige": "Ich + senden = Ich send___", "antwort": "-e", "vollstaendig": "Ich sende"},
            {"anzeige": "Du + glauben = Du glaub___", "antwort": "-st", "vollstaendig": "Du glaubst"},
            {"anzeige": "Ich + hoffen = Ich hoff___", "antwort": "-e", "vollstaendig": "Ich hoffe"}
        ]
    }
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


# --- ÄSTHETISCHER, ABGERUNDETER KNOPF (PILL BUTTON) ---
class AbgerundeterButton(Button):
    def __init__(self, farbe=BLAU, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.custom_farbe = farbe

        with self.canvas.before:
            Color(*self.custom_farbe)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.height / 2.0])

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
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


class VokabelRootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(10)

        self.sound = None
        self.lektionen = lade_json_datei("vokabeln.json")
        self.phrasen_daten = lade_json_datei("phrasen.json")
        self.fortschritt = lade_json_datei("fortschritt.json")

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
        self.quiz_index = 0
        self.quiz_leben = 3
        self.quiz_punkte = 0

        self.zeige_hauptmenue()

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

        container = BoxLayout(orientation='vertical', size_hint=(1, 1))
        container.add_widget(Widget(size_hint_y=1))

        quadrat_block = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        quadrat_block.bind(minimum_height=quadrat_block.setter('height'))

        self.logo_hinzufuegen(quadrat_block, hoehe=150)

        quadrat_block.add_widget(label("Merhaba! Hoş geldin!", 24, 44, bold=True, color=BLAU))
        quadrat_block.add_widget(label("Ne yapmak istiyorsun?", 15, 26, color=(0.70, 0.70, 0.70, 1)))

        btn_lernen = knopf("Öğren (Lernen)", groesse=18, hoehe=58)
        btn_lernen.bind(on_release=self.zeige_lernen_menue)
        quadrat_block.add_widget(btn_lernen)

        btn_wiederholen = knopf("Tekrar (Wiederholung)", groesse=18, hoehe=58, farbe=BLAU_DUNKEL)
        btn_wiederholen.bind(on_release=self.starte_wiederholung_stapel)
        quadrat_block.add_widget(btn_wiederholen)

        container.add_widget(quadrat_block)
        container.add_widget(Widget(size_hint_y=1))
        self.add_widget(container)

    # ---------- 2. Untermenü: Lernen ----------
    def zeige_lernen_menue(self, *args):
        self.bildschirm_leeren()

        container = BoxLayout(orientation='vertical', size_hint=(1, 1))

        zurueck = knopf("< Ana Menü", groesse=15, hoehe=44, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_hauptmenue)
        container.add_widget(zurueck)

        container.add_widget(Widget(size_hint_y=1))

        mitte_block = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        mitte_block.bind(minimum_height=mitte_block.setter('height'))

        self.logo_hinzufuegen(mitte_block, hoehe=150)

        mitte_block.add_widget(label("Öğrenme Alanı", 20, 38, bold=True, color=BLAU))
        mitte_block.add_widget(label("Lütfen bir kategori seç:", 14, 24, color=(0.70, 0.70, 0.70, 1)))

        btn_vokabeln = knopf("Kelime Kartları (Vokabeln)", groesse=16, hoehe=50)
        btn_vokabeln.bind(on_release=self.zeige_lektionen_menue)
        mitte_block.add_widget(btn_vokabeln)

        btn_phrasen = knopf("Günlük İfadeler (Alltagsphrasen)", groesse=16, hoehe=50, farbe=BLAU_DUNKEL)
        btn_phrasen.bind(on_release=self.zeige_phrasen_kategorien_menue)
        mitte_block.add_widget(btn_phrasen)

        btn_grammatik = knopf("Gramer (Grammatik)", groesse=16, hoehe=50, farbe=BLAU_DUNKEL)
        btn_grammatik.bind(on_release=self.zeige_grammatik_menue)
        mitte_block.add_widget(btn_grammatik)

        container.add_widget(mitte_block)
        container.add_widget(Widget(size_hint_y=1))
        self.add_widget(container)

    def zeige_platzhalter_info(self, nachricht):
        self.bildschirm_leeren()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        layout.add_widget(label(nachricht, 20, 60, bold=True, color=BLAU))
        layout.add_widget(label("Bu özellik yakında eklenecektir.", 16, 40, color=(0.7, 0.7, 0.7, 1)))

        zurueck = knopf("Geri Dön", groesse=16, hoehe=56)
        zurueck.bind(on_release=self.zeige_lernen_menue)
        layout.add_widget(zurueck)
        self.add_widget(layout)

    # ---------- 3C. Grammatik-Lektionen-Menü ----------
    def zeige_grammatik_menue(self, *args):
        self.bildschirm_leeren()
        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12), padding=[0, 0, 0, dp(20)])
        layout.bind(minimum_height=layout.setter('height'))

        zurueck = knopf("< Öğrenme Menüsü", groesse=16, hoehe=48, farbe=GRAU)
        zurueck.bind(on_release=self.zeige_lernen_menue)
        layout.add_widget(zurueck)

        layout.add_widget(label("Gramer Dersleri", 22, 50, bold=True, color=BLAU))
        layout.add_widget(label("Lütfen bir ders seç:", 16, 30, color=(0.70, 0.70, 0.70, 1)))

        abgeschlossen = self.fortschritt.get("grammatik_abgeschlossen", [])

        for lektions_name in GRAMMATIK_LEKTIONEN.keys():
            status = "  (Tamamlandı)" if lektions_name in abgeschlossen else ""
            farbe = GRUEN if lektions_name in abgeschlossen else BLAU
            btn = knopf(f"{lektions_name}{status}", groesse=16, hoehe=58, farbe=farbe)
            btn.bind(on_release=lambda b, ln=lektions_name: self.starte_grammatik_lektion(ln))
            layout.add_widget(btn)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def starte_grammatik_lektion(self, lektions_name):
        self.aktuelle_grammatik_lektion = lektions_name
        lektion = GRAMMATIK_LEKTIONEN[lektions_name]
        self.grammatik_karten = list(lektion["karten"])
        self.grammatik_index = 0
        self.zeige_grammatik_karte()

    def zeige_grammatik_karte(self):
        self.bildschirm_leeren()

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        zurueck = knopf("< Dersler", groesse=15, hoehe=52, farbe=GRAU, size_hint_x=None, width=dp(105))
        zurueck.bind(on_release=self.zeige_grammatik_menue)
        top.add_widget(zurueck)
        top.add_widget(label(self.aktuelle_grammatik_lektion, 14, bold=True, color=BLAU))
        self.add_widget(top)

        gesamt = len(self.grammatik_karten)
        self.add_widget(label(f"Kart {self.grammatik_index + 1} / {gesamt}", 15, 36, color=(0.70, 0.70, 0.70, 1)))

        text = self.grammatik_karten[self.grammatik_index]
        schriftgroesse = 26 if len(text) < 25 else 20

        karte = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        karte.add_widget(label(text, schriftgroesse, bold=True, color=(1, 1, 1, 1)))
        self.add_widget(karte)

        aktion = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(64), spacing=dp(12))

        if self.grammatik_index > 0:
            prev_btn = knopf("< Önceki", groesse=16, hoehe=56, farbe=GRAU)
            prev_btn.bind(on_release=lambda x: self.grammatik_karte_wechseln(-1))
            aktion.add_widget(prev_btn)

        ist_letzte_karte = (self.grammatik_index == gesamt - 1)
        weiter_text = "Teste Başla (Quiz)" if ist_letzte_karte else "Sonraki Kart >"
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
        lektion = GRAMMATIK_LEKTIONEN[self.aktuelle_grammatik_lektion]
        self.quiz_fragen = list(lektion["quiz"])
        self.quiz_index = 0
        self.quiz_leben = 3
        self.quiz_punkte = 0
        self.zeige_grammatik_quiz_frage()

    def zeige_grammatik_quiz_frage(self, feedback_text="", feedback_farbe=BLAU):
        self.bildschirm_leeren()

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        zurueck = knopf("< Çık", groesse=15, hoehe=52, farbe=GRAU, size_hint_x=None, width=dp(90))
        zurueck.bind(on_release=self.zeige_grammatik_menue)
        top.add_widget(zurueck)
        top.add_widget(label(f"Soru {self.quiz_index + 1} / {len(self.quiz_fragen)}", 15, bold=True, color=BLAU))
        top.add_widget(label(f"Can: {self.quiz_leben} / 3", 15, bold=True, color=ROT if self.quiz_leben == 1 else GRUEN))
        self.add_widget(top)

        if feedback_text:
            self.add_widget(label(feedback_text, 17, 42, bold=True, color=feedback_farbe))
        else:
            self.add_widget(label("Doğru fiil sonunu seç:", 15, 36, color=(0.70, 0.70, 0.70, 1)))

        frage = self.quiz_fragen[self.quiz_index]

        karte = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(12))
        karte.add_widget(label("Fiili Çekimle", 16, 34, bold=True, color=BLAU_DUNKEL))
        karte.add_widget(label(frage["anzeige"], 28, bold=True, color=(1, 1, 1, 1)))
        self.add_widget(karte)

        # 3 Antwort-Buttons nebeneinander: -e, -st, -est
        antwort_reihe = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(72), spacing=dp(12), padding=[0, dp(6), 0, dp(6)])
        for option in ["-e", "-st", "-est"]:
            btn = knopf(option, groesse=20, hoehe=60, farbe=BLAU)
            btn.bind(on_release=lambda b, opt=option: self.pruefe_quiz_antwort(opt))
            antwort_reihe.add_widget(btn)

        self.add_widget(antwort_reihe)

    def pruefe_quiz_antwort(self, gewaehlte_endung):
        frage = self.quiz_fragen[self.quiz_index]
        richtig = (gewaehlte_endung == frage["antwort"])

        if richtig:
            self.quiz_punkte += 1
            self.sprache_abspielen(frage["vollstaendig"])
            self.quiz_index += 1
            if self.quiz_index >= len(self.quiz_fragen):
                self.zeige_grammatik_quiz_erfolg()
            else:
                self.zeige_grammatik_quiz_frage(
                    feedback_text=f"Doğru! ({frage['vollstaendig']})",
                    feedback_farbe=GRUEN
                )
        else:
            self.quiz_leben -= 1
            if self.quiz_leben <= 0:
                self.zeige_grammatik_quiz_verloren()
            else:
                self.zeige_grammatik_quiz_frage(
                    feedback_text=f"Yanlış! '{gewaehlte_endung}' değil. Tekrar dene!",
                    feedback_farbe=ROT
                )

    def zeige_grammatik_quiz_verloren(self):
        self.bildschirm_leeren()
        self.add_widget(Widget(size_hint_y=1))
        self.add_widget(label("Canların Bitti!", 26, 50, bold=True, color=ROT))
        self.add_widget(label("3 kez yanlış cevap verdin. Dersi tamamlamak için testi baştan yapmalısın.", 16, 70, color=(0.80, 0.80, 0.80, 1)))

        nochmal_btn = knopf("Testi Tekrar Başlat", groesse=18, hoehe=60, farbe=BLAU)
        nochmal_btn.bind(on_release=lambda x: self.starte_grammatik_quiz())
        self.add_widget(nochmal_btn)

        zurueck_btn = knopf("Derslere Dön", groesse=16, hoehe=54, farbe=GRAU)
        zurueck_btn.bind(on_release=self.zeige_grammatik_menue)
        self.add_widget(zurueck_btn)
        self.add_widget(Widget(size_hint_y=1))

    def zeige_grammatik_quiz_erfolg(self):
        abgeschlossen = self.fortschritt.get("grammatik_abgeschlossen", [])
        if self.aktuelle_grammatik_lektion not in abgeschlossen:
            abgeschlossen.append(self.aktuelle_grammatik_lektion)
            self.fortschritt["grammatik_abgeschlossen"] = abgeschlossen
            speichere_json_datei("fortschritt.json", self.fortschritt)

        gesamt = len(self.quiz_fragen)
        self.bildschirm_leeren()
        self.add_widget(Widget(size_hint_y=1))
        self.add_widget(label("Çok iyi! Başardın!", 26, 50, bold=True, color=GRUEN))
        self.add_widget(label(f"İlk ders bu kadardı!\n{gesamt} üzerinden {self.quiz_punkte} Puan", 18, 70, bold=True, color=BLAU))

        fertig_btn = knopf("Gramer Menüsüne Dön", groesse=18, hoehe=60, farbe=BLAU)
        fertig_btn.bind(on_release=self.zeige_grammatik_menue)
        self.add_widget(fertig_btn)
        self.add_widget(Widget(size_hint_y=1))

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

        gelernte = self.fortschritt.get(titel, [])
        gelernte_tupel = {(k["de"], k["tr"]) for k in gelernte}

        offene_karten = [k for k in alle_karten if (k["de"], k["tr"]) not in gelernte_tupel]

        if not offene_karten:
            offene_karten = list(alle_karten)
            self.fortschritt[titel] = []
            speichere_json_datei("fortschritt.json", self.fortschritt)

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
            self.zeige_platzhalter_info("Henüz öğrenilmiş kart yok!\nÖnce biraz kelime veya ifade öğrenin.")
            return

        self.aktive_lektion_key = ""
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
            if self.aktive_lektion_key:
                if self.aktive_lektion_key not in self.fortschritt:
                    self.fortschritt[self.aktive_lektion_key] = []

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
