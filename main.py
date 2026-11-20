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
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.utils import platform

if platform != "android":
    Window.size = (420, 720)
Window.clearcolor = (0.065, 0.068, 0.075, 1)

BASIS = os.path.dirname(os.path.abspath(__file__))

# --- EXAKTER LOGO-BLAUTON & AKZENTFARBEN ---
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

# --- FARBCODES FÜR MARKUP (BBCode) ---
C_ICH = "#20A3FE"       # Blau für "Ich" und "-e"
C_DU = "#FFB300"        # Gold-Orange für "Du" und "-st" / "-est"
C_ER = "#4CD964"        # Grün für "Er"
C_SIE_SG = "#FF6B8B"    # Rosa/Koralle für "Sie" (3. Pers. Singular - kadın)
C_ES = "#BF5AF2"        # Violett für "Es"
C_T_END = "#A29BFE"     # Helles Lila für "-t" / "-et" bei 3. Pers. Sg.
C_WIR = "#00D2D3"       # Türkis für "Wir" und "-en"
C_IHR = "#FF7675"       # Lachsrot für "Ihr" und "-t" / "-et"
C_SIE_PL = "#55EFC4"    # Mintgrün für "Sie" (3. Pers. Plural - onlar / nezaket) und "-en"

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

# --- GRAMMATIK-LEKTIONEN (MIT DURCHGÄNGIGER FARBMARKIERUNG) ---
GRAMMATIK_LEKTIONEN = {
    "Fiiller 1. Bölüm": {
        "karten": [
            "İlk dil bilgisi dersine hoş geldin!",
            "Bu derste fiillerin (eylem kelimelerinin) Almancada nasıl kullanıldığına birlikte bakacağız.",
            "Uygulamada fiil kartları çoğunlukla mastar halindedir, yani:\n\nögrenmek = lernen\noynamak = spielen\nçalışmak = arbeiten",
            "Şimdi bu kelimeleri aktif forma nasıl dönüştüreceğimizi birlikte öğreneceğiz:\n\nöğreniyorum\noynuyorum\nçalışıyorum",
            "Bunun için bir zamire ihtiyacımız var. Senin için kolay kalması adına, zaten bildiğin bir zamirde kalacağız.",
            f"[color={C_ICH}]ICH (BEN)[/color]",
            "Şimdi fiillere tekrar bakalım:\n\nlernen = öğrenmek\nspielen = oynamak\narbeiten = çalışmak",
            "Onları aktif forma dönüştürmek için önce fiil kökünü oluşturmalıyız:\n\nlernen = öğrenmek\nspielen = oynamak\narbeiten = çalışmak",
            "Bunun için son heceyi, yani -en takısını çıkarıyoruz:\n\nlern = öğrenmek\nspiel = oynamak\narbeit = çalışmak",
            f"Ardından zamirimizi ekliyoruz:\n\n[color={C_ICH}]Ich[/color] lern = öğrenmek\n[color={C_ICH}]Ich[/color] spiel = oynamak\n[color={C_ICH}]Ich[/color] arbeit = çalışmak",
            f"Son olarak bir kelime sonu eklemeliyiz. Kelime sonu eki her zaman zamire bağlıdır. [color={C_ICH}]Ich[/color] için bu her zaman bir [color={C_ICH}]-e[/color] ekidir:\n\n[color={C_ICH}]Ich[/color] lern[color={C_ICH}]e[/color] = Ben öğreniyorum\n[color={C_ICH}]Ich[/color] spiel[color={C_ICH}]e[/color] = Ben oynuyorum\n[color={C_ICH}]Ich[/color] arbeit[color={C_ICH}]e[/color] = Ben çalışıyorum",
            f"Bu neredeyse tüm fiillerde bu şekilde çalışır. Bunlara düzenli fiiller denir.\n\nİşte birkaç örnek daha:\nyapmak | [color={C_ICH}]Ich[/color] mach[color={C_ICH}]e[/color] = Ben yapıyorum\nduymak / dinlemek | [color={C_ICH}]Ich[/color] hör[color={C_ICH}]e[/color] = Ben duyuyorum\nsatın almak | [color={C_ICH}]Ich[/color] kauf[color={C_ICH}]e[/color] = Ben satın alıyorum",
            "Şimdi işleri biraz daha karmaşık hale getiriyoruz. Yanımıza ikinci bir zamir alıyoruz:",
            f"[color={C_DU}]Du (Sen)[/color]",
            f"Tıpkı önceki gibi fiil kökünü oluşturuyoruz:\n\n[color={C_DU}]Du[/color] lern\n[color={C_DU}]Du[/color] spiel\n[color={C_DU}]Du[/color] arbeit",
            f"Tıpkı [color={C_ICH}]Ich[/color] gibi, [color={C_DU}]Du[/color] zamirinin de kendine ait bir eki vardır: [color={C_DU}]-st[/color].\n\n[color={C_DU}]Du[/color] lern[color={C_DU}]st[/color]\n[color={C_DU}]Du[/color] spiel[color={C_DU}]st[/color]",
            f"T veya D ile biten fiil kökleri ve birden fazla sessiz harfle biten fiil köklerini bu şekilde telaffuz etmek zor olurdu, bu yüzden buradaki ek [color={C_DU}]-est[/color] olur:\n\n[color={C_DU}]Du[/color] arbeit[color={C_DU}]est[/color]\n[color={C_DU}]Du[/color] öffn[color={C_DU}]est[/color]\n[color={C_DU}]Du[/color] atm[color={C_DU}]est[/color]",
            f"İşte birkaç örnek daha:\n\n[color={C_DU}]Du[/color] koch[color={C_DU}]st[/color]\n[color={C_DU}]Du[/color] start[color={C_DU}]est[/color]\n[color={C_DU}]Du[/color] land[color={C_DU}]est[/color]\n[color={C_DU}]Du[/color] lach[color={C_DU}]st[/color]",
            "Hiç de karmaşık değil, değil mi? O halde küçük bir test deneyelim.\n\nSana Mastar halinde 15 fiil veriyorum ve senin bunları çekimlemen gerekiyor!"
        ],
        "quiz_hinweis": "Doğru fiil sonunu seç:",
        "quiz_titel": "FİİLİ ÇEKİMLE",
        "optionen": ["-e", "-st", "-est"],
        "quiz": [
            {"anzeige": f"[color={C_ICH}]Ich[/color] + fehlen = [color={C_ICH}]Ich[/color] fehl___", "antwort": "-e", "vollstaendig": "Ich fehle"},
            {"anzeige": f"[color={C_DU}]Du[/color] + duschen = [color={C_DU}]Du[/color] dusch___", "antwort": "-st", "vollstaendig": "Du duschst"},
            {"anzeige": f"[color={C_ICH}]Ich[/color] + frühstücken = [color={C_ICH}]Ich[/color] frühstück___", "antwort": "-e", "vollstaendig": "Ich frühstücke"},
            {"anzeige": f"[color={C_DU}]Du[/color] + planen = [color={C_DU}]Du[/color] plan___", "antwort": "-st", "vollstaendig": "Du planst"},
            {"anzeige": f"[color={C_ICH}]Ich[/color] + duschen = [color={C_ICH}]Ich[/color] dusch___", "antwort": "-e", "vollstaendig": "Ich dusche"},
            {"anzeige": f"[color={C_DU}]Du[/color] + trinken = [color={C_DU}]Du[/color] trink___", "antwort": "-st", "vollstaendig": "Du trinkst"},
            {"anzeige": f"[color={C_ICH}]Ich[/color] + feiern = [color={C_ICH}]Ich[/color] feier___", "antwort": "-e", "vollstaendig": "Ich feiere"},
            {"anzeige": f"[color={C_DU}]Du[/color] + heben = [color={C_DU}]Du[/color] heb___", "antwort": "-st", "vollstaendig": "Du hebst"},
            {"anzeige": f"[color={C_ICH}]Ich[/color] + kaufen = [color={C_ICH}]Ich[/color] kauf___", "antwort": "-e", "vollstaendig": "Ich kaufe"},
            {"anzeige": f"[color={C_DU}]Du[/color] + reden = [color={C_DU}]Du[/color] red___", "antwort": "-est", "vollstaendig": "Du redest"},
            {"anzeige": f"[color={C_ICH}]Ich[/color] + antworten = [color={C_ICH}]Ich[/color] antwort___", "antwort": "-e", "vollstaendig": "Ich antworte"},
            {"anzeige": f"[color={C_ICH}]Ich[/color] + baden = [color={C_ICH}]Ich[/color] bad___", "antwort": "-e", "vollstaendig": "Ich bade"},
            {"anzeige": f"[color={C_ICH}]Ich[/color] + senden = [color={C_ICH}]Ich[/color] send___", "antwort": "-e", "vollstaendig": "Ich sende"},
            {"anzeige": f"[color={C_DU}]Du[/color] + glauben = [color={C_DU}]Du[/color] glaub___", "antwort": "-st", "vollstaendig": "Du glaubst"},
            {"anzeige": f"[color={C_ICH}]Ich[/color] + hoffen = [color={C_ICH}]Ich[/color] hoff___", "antwort": "-e", "vollstaendig": "Ich hoffe"}
        ]
    },
    "Fiiller 2. Bölüm": {
        "karten": [
            f"Artık [color={C_ICH}]Ich[/color] ve [color={C_DU}]Du[/color] zamirlerine hakim olduğuna göre, tam da oradan devam ediyoruz.",
            "Üçüncü tekil şahıs Almancada Türkçeye göre biraz daha karmaşıktır. Türkçede hakkında konuşulan kişi kim olursa olsun her zaman “O” kullanılırken, Almancada cinsiyete göre ayrım yapılır.",
            f"[color={C_ER}]Er[/color] (eril), [color={C_SIE_SG}]Sie[/color] (dişil) ve [color={C_ES}]Es[/color] (nötr)",
            f"Yani O demek yerine bir erkek hakkında konuşurken [color={C_ER}]Er[/color] dersin:\n\n[color={C_ER}]Er[/color] ist mein Verlobter = O benim nişanlım\n\n[color={C_ER}]Er[/color] zamirinde aklına Türkçe Erkek kelimesi gelirse, kolayca hatırlayabilirsin.",
            f"Ve bir kadın hakkında konuştuğunda O yerine [color={C_SIE_SG}]Sie[/color] dersin.\n[color={C_SIE_SG}]Sie[/color] kelimesindeki S harfi yumuşak okunur, Türkçe Kız kelimesindeki Z harfine benzer:\n\n[color={C_SIE_SG}]Sie[/color] ist meine Tochter = O benim kız çocuğum",
            "Böylece hangi zamirin hangi cinsiyete ait olduğunu kolayca hatırlayabilirsin.",
            f"“[color={C_ES}]Es[/color]”, hava durumu gibi nötr bir şeyden bahsettiğinde kullanılır:\n\nDışarısı güzel, hava iyi.\n[color={C_ES}]Es[/color] ist schön draußen, das Wetter ist gut",
            "Bu karmaşık görünebilir ama anlayana kadar yavaş yavaş ilerleyeceğiz.",
            "Yine mastar haliyle başlayalım:\n\nspielen = oynamak\nlernen = öğrenmek\narbeiten = çalışmak",
            "Zaten bildiğin gibi, son heceyi çıkararak fiil kökünü elde etmeliyiz:\n\nspiel = oynamak\nlern = öğrenmek\narbeit = çalışmak",
            f"Ardından 3 zamirimizi ekliyoruz:\n\n[color={C_ER}]Er[/color] spiel = O (erkek) oynuyor\n[color={C_SIE_SG}]Sie[/color] lern = O (kadın) öğreniyor\n[color={C_ES}]Es[/color] arbeit = O (nötr) çalışıyor",
            f"Ve sonra ek gelir. Bu ek her üç zamir için de aynıdır: [color={C_T_END}]-t[/color]\n\n[color={C_ER}]Er[/color] spiel[color={C_T_END}]t[/color] = O (erkek) oynuyor\n[color={C_SIE_SG}]Sie[/color] lern[color={C_T_END}]t[/color] = O (kadın) öğreniyor\n[color={C_ES}]Es[/color] arbeit[color={C_T_END}]et[/color] = O (nötr) çalışıyor",
            "Farklı zamirlerin ne zaman kullanıldığını açıklamak için işte birkaç cümle daha:",
            f"Das ist Daniel. [color={C_ER}]Er[/color] arbeit[color={C_T_END}]et[/color] im Supermarkt.\nBu Daniel. O süpermarkette çalışıyor.",
            f"Das ist meine Oma. [color={C_SIE_SG}]Sie[/color] back[color={C_T_END}]t[/color] Kekse.\nBu benim büyükannem. O kurabiye pişiriyor.",
            f"Das Wetter ist schlecht. [color={C_ES}]Es[/color] regn[color={C_T_END}]et[/color].\nHava kötü. Yağmur yağıyor.",
            f"[color={C_DU}]Du[/color] zamirinde [color={C_DU}]-est[/color] ile biten kelimeler, burada [color={C_T_END}]-et[/color] ile biter:\n\n[color={C_ER}]Er[/color] arbeit[color={C_T_END}]et[/color], [color={C_SIE_SG}]Sie[/color] land[color={C_T_END}]et[/color], [color={C_ES}]Es[/color] start[color={C_T_END}]et[/color]",
            "Becerilerini test edelim.\n\nBurada 9 cümlen var ve doğru zamiri yerleştirmen gerekiyor!"
        ],
        "quiz_hinweis": "Doğru zamiri seç (Er / Sie / Es):",
        "quiz_titel": "DOĞRU ZAMİRİ SEÇ",
        "optionen": ["Er", "Sie", "Es"],
        "quiz": [
            {
                "anzeige": f"[color={C_ICH}]Ich[/color] kauf[color={C_ICH}]e[/color] ein Handy. ___ ist teuer.\n[size=15sp][color=#A0A6B2]Bir cep telefonu satın alıyorum; pahalı.[/color][/size]",
                "antwort": "Es",
                "vollstaendig": "Ich kaufe ein Handy. Es ist teuer."
            },
            {
                "anzeige": f"Das ist meine Tochter. ___ spiel[color={C_T_END}]t[/color] Klavier.\n[size=15sp][color=#A0A6B2]Bu benim kızım. O piyano çalıyor.[/color][/size]",
                "antwort": "Sie",
                "vollstaendig": "Das ist meine Tochter. Sie spielt Klavier."
            },
            {
                "anzeige": f"Mein Onkel ist sauer. ___ fluch[color={C_T_END}]t[/color].\n[size=15sp][color=#A0A6B2]Amcam kızgın. O küfrediyor.[/color][/size]",
                "antwort": "Er",
                "vollstaendig": "Mein Onkel ist sauer. Er flucht."
            },
            {
                "anzeige": f"Meine Schwester hat 5 Euro. ___ kauf[color={C_T_END}]t[/color] eine Wassermelone.\n[size=15sp][color=#A0A6B2]Kız kardeşimin 5 eurosu var. O bir karpuz satın alıyor.[/color][/size]",
                "antwort": "Sie",
                "vollstaendig": "Meine Schwester hat 5 Euro. Sie kauft eine Wassermelone."
            },
            {
                "anzeige": f"Heute kann man Papierdrachen fliegen. ___ ist windig.\n[size=15sp][color=#A0A6B2]Bugün uçurtma uçurulabilir. Hava rüzgârlı.[/color][/size]",
                "antwort": "Es",
                "vollstaendig": "Heute kann man Papierdrachen fliegen. Es ist windig."
            },
            {
                "anzeige": f"Mein Sohn heißt Leon, ___ ist 5 Jahre alt.\n[size=15sp][color=#A0A6B2]Oğlumun adı Leon. O 5 yaşında.[/color][/size]",
                "antwort": "Er",
                "vollstaendig": "Mein Sohn heißt Leon, er ist 5 Jahre alt."
            },
            {
                "anzeige": f"Mein Mathelehrer heißt Herr Müller. ___ ist sehr streng.\n[size=15sp][color=#A0A6B2]Matematik öğretmenimin adı Bay Müller. Kendisi çok serttir.[/color][/size]",
                "antwort": "Er",
                "vollstaendig": "Mein Mathelehrer heißt Herr Müller. Er ist sehr streng."
            },
            {
                "anzeige": f"Meine Mutter wartet auf mich. ___ ist genervt.\n[size=15sp][color=#A0A6B2]Annem beni bekliyor. O sinirli.[/color][/size]",
                "antwort": "Sie",
                "vollstaendig": "Meine Mutter wartet auf mich. Sie ist genervt."
            },
            {
                "anzeige": f"Da ist ein Baby. ___ schau[color={C_T_END}]t[/color] mich an.\n[size=15sp][color=#A0A6B2]Orada bir bebek var. O bana bakıyor.[/color][/size]",
                "antwort": "Es",
                "vollstaendig": "Da ist ein Baby. Es schaut mich an."
            }
        ]
    },
    "Fiiller 3. Bölüm": {
        "karten": [
            "Harika, başardın! Artık tekil şahısların hepsine hakimsin.\n\nŞimdi çoğul şahısları deneyelim (Biz, Siz, Onlar).",
            f"Biz = [color={C_WIR}]Wir[/color]",
            "Her zamanki gibi üç fiilimizin mastar halini alıyoruz:\n\nspielen = oynamak\nlernen = öğrenmek\narbeiten = çalışmak",
            f"Ve şimdi gerçekten kolaylaşıyor. Çünkü birinci çoğul şahıs mastar haliyle birebir aynı yazılır. Yani tek yapman gereken zamiri eklemek ([color={C_WIR}]Wir[/color] + [color={C_WIR}]-en[/color]):\n\n[color={C_WIR}]Wir[/color] spiel[color={C_WIR}]en[/color] = Biz oynuyoruz\n[color={C_WIR}]Wir[/color] lern[color={C_WIR}]en[/color] = Biz öğreniyoruz\n[color={C_WIR}]Wir[/color] arbeit[color={C_WIR}]en[/color] = Biz çalışıyoruz",
            f"Birkaç örnek daha:\n\n[color={C_WIR}]Wir[/color] heirat[color={C_WIR}]en[/color] = Biz evleniyoruz\n[color={C_WIR}]Wir[/color] putz[color={C_WIR}]en[/color] = Biz temizliyoruz\n[color={C_WIR}]Wir[/color] wein[color={C_WIR}]en[/color] = Biz ağlıyoruz",
            "Bu kolaydı, değil mi? O halde bir sonraki kişiyle devam edelim!",
            f"Siz = [color={C_IHR}]Ihr[/color]",
            "Her zamanki gibi fiillerimizin mastar halini alıyoruz:\n\nspielen = oynamak\nlernen = öğrenmek\narbeiten = çalışmak",
            "Tabii ki önce fiil kökünü oluşturmalıyız:\n\nspiel = oynamak\nlern = öğrenmek\narbeit = çalışmak",
            f"İki veya daha fazla kişiden bahsettiğinde [color={C_IHR}]Ihr[/color] (Siz) zamirini kullanırsın:\n\n[color={C_IHR}]Ihr[/color] spiel = oynamak\n[color={C_IHR}]Ihr[/color] lern = öğrenmek\n[color={C_IHR}]Ihr[/color] arbeit = çalışmak",
            f"[color={C_IHR}]Ihr[/color] (Siz) için kelime sonu eki [color={C_IHR}]-t[/color]'dir (veya [color={C_IHR}]-et[/color]), tıpkı geçen dersteki [color={C_ER}]Er[/color]/[color={C_SIE_SG}]Sie[/color]/[color={C_ES}]Es[/color] (O) gibi:\n\n[color={C_IHR}]Ihr[/color] spiel[color={C_IHR}]t[/color] = siz oynuyorsunuz\n[color={C_IHR}]Ihr[/color] lern[color={C_IHR}]t[/color] = siz öğreniyorsunuz\n[color={C_IHR}]Ihr[/color] arbeit[color={C_IHR}]et[/color] = siz çalışıyorsunuz",
            "Birkaç örnek cümle daha:",
            f"[color={C_WIR}]Wir[/color] arbeit[color={C_WIR}]en[/color] im Supermarkt, [color={C_IHR}]Ihr[/color] arbeit[color={C_IHR}]et[/color] im Baumarkt.\nBiz süpermarkette çalışıyoruz, siz yapı markette çalışıyorsunuz.",
            f"[color={C_WIR}]Wir[/color] lern[color={C_WIR}]en[/color] Deutsch, [color={C_IHR}]ihr[/color] lern[color={C_IHR}]t[/color] Türkisch.\nBiz Almanca öğreniyoruz, siz Türkçe öğreniyorsunuz.",
            f"[color={C_WIR}]Wir[/color] guck[color={C_WIR}]en[/color] einen Film, [color={C_IHR}]Ihr[/color] guck[color={C_IHR}]t[/color] eine Serie.\nBiz bir film izliyoruz, siz bir dizi izliyorsunuz.",
            f"[color={C_WIR}]Wir[/color] hör[color={C_WIR}]en[/color] Musik, [color={C_IHR}]Ihr[/color] hör[color={C_IHR}]t[/color] ein Hörbuch.\nBiz müzik dinliyoruz, siz sesli kitap dinliyorsunuz.",
            f"[color={C_WIR}]Wir[/color] trainier[color={C_WIR}]en[/color] die Arme, [color={C_IHR}]Ihr[/color] trainier[color={C_IHR}]t[/color] den Bauch.\nBiz kolları çalıştırıyoruz, siz karın bölgesini çalıştırıyorsunuz.",
            "O halde becerilerini bir kez daha test edelim. Verilen zamirle bu 7 fiili çekimle!"
        ],
        "quiz_hinweis": "Doğru fiil sonunu seç:",
        "quiz_titel": "FİİLİ ÇEKİMLE",
        "optionen": ["-en", "-t", "-et"],
        "quiz": [
            {"anzeige": f"[color={C_IHR}]Ihr[/color] + arbeiten = [color={C_IHR}]Ihr[/color] arbeit___", "antwort": "-et", "vollstaendig": "Ihr arbeitet"},
            {"anzeige": f"[color={C_IHR}]Ihr[/color] + kaufen = [color={C_IHR}]Ihr[/color] kauf___", "antwort": "-t", "vollstaendig": "Ihr kauft"},
            {"anzeige": f"[color={C_WIR}]Wir[/color] + schlafen = [color={C_WIR}]Wir[/color] schlaf___", "antwort": "-en", "vollstaendig": "Wir schlafen"},
            {"anzeige": f"[color={C_IHR}]Ihr[/color] + tanzen = [color={C_IHR}]Ihr[/color] tanz___", "antwort": "-t", "vollstaendig": "Ihr tanzt"},
            {"anzeige": f"[color={C_WIR}]Wir[/color] + lernen = [color={C_WIR}]Wir[/color] lern___", "antwort": "-en", "vollstaendig": "Wir lernen"},
            {"anzeige": f"[color={C_IHR}]Ihr[/color] + fragen = [color={C_IHR}]Ihr[/color] frag___", "antwort": "-t", "vollstaendig": "Ihr fragt"},
            {"anzeige": f"[color={C_WIR}]Wir[/color] + laufen = [color={C_WIR}]Wir[/color] lauf___", "antwort": "-en", "vollstaendig": "Wir laufen"}
        ]
    },
    "Fiiller 4. Bölüm": {
        "karten": [
            f"Artık neredeyse başardın. Usta olamadığın sadece tek bir kişi kaldı.\n\nÜçüncü çoğul şahıs \"[color={C_SIE_PL}]Sie[/color]\" (Onlar)",
            f"Kafan karışmış olabilir çünkü iki tane \"[color={C_SIE_PL}]Sie[/color]\" versiyonu var. Ama hızlıca alışana kadar pratik yapacağız.",
            "Yine mastar halindeki fiillerimizle başlayalım:\n\nspielen = oynamak\nlernen = öğrenmek\narbeiten = çalışmak",
            f"Biz ([color={C_WIR}]Wir[/color]) şahsında olduğu gibi takı mastar haliyle aynıdır, yani işimizi kolaylaştırıp sadece zamiri eklememiz yeterlidir ([color={C_SIE_PL}]Sie[/color] + [color={C_SIE_PL}]-en[/color]):\n\n[color={C_SIE_PL}]Sie[/color] spiel[color={C_SIE_PL}]en[/color] = Onlar oynuyorlar\n[color={C_SIE_PL}]Sie[/color] lern[color={C_SIE_PL}]en[/color] = Onlar öğreniyorlar\n[color={C_SIE_PL}]Sie[/color] arbeit[color={C_SIE_PL}]en[/color] = Onlar çalışıyorlar",
            "İşte birkaç örnek cümle:",
            f"Das sind die Schüler der Goethe Realschule. [color={C_SIE_PL}]Sie[/color] schreib[color={C_SIE_PL}]en[/color] einen Test.\nBunlar, Goethe Ortaokulu'nun öğrencileri. Onlar bir sınav yazıyorlar.",
            f"Die Firma Audi hat viele Angestellte. [color={C_SIE_PL}]Sie[/color] verdien[color={C_SIE_PL}]en[/color] viel Geld.\nAudi firmasının birçok çalışanı var. Onlar çok para kazanıyorlar.",
            f"Die Familie Müller ist spät dran. [color={C_SIE_PL}]Sie[/color] steh[color={C_SIE_PL}]en[/color] im Stau.\nMüller ailesi gecikti. Trafikteler.",
            "O kadar da zor değil, değil mi? Ancak bu derste özel bir durum var.",
            f"Üçüncü çoğul şahıs [color={C_SIE_PL}]Sie[/color] (Onlar) aynı zamanda nezaket şekli (kibar ifade) olarak da kullanılır.",
            f"Kibar olmanız gereken biriyle konuşurken [color={C_DU}]Du[/color] yerine [color={C_SIE_PL}]Sie[/color] kullanırsınız.",
            f"Bunun birkaç örnekle nasıl çalıştığını sana göstereyim:\n\nArkadaşına iltifat ediyorsun = [color={C_DU}]Du[/color] sieh[color={C_DU}]st[/color] gut aus (İyi görünüyorsun)\nPatronuna iltifat ediyorsun = [color={C_SIE_PL}]Sie[/color] seh[color={C_SIE_PL}]en[/color] gut aus (İyi görünüyorsunuz)",
            f"Arkadaşın seninle konuşuyor = [color={C_DU}]Du[/color] ha[color={C_DU}]st[/color] das gut gemacht!\nPatronun seni övüyor = [color={C_SIE_PL}]Sie[/color] hab[color={C_SIE_PL}]en[/color] das gut gemacht!",
            f"Annenden bir içecek istiyorsun = Ha[color={C_DU}]st[/color] [color={C_DU}]du[/color] Cola? (Kola var mı)\nRestoranda bir içecek istiyorsun = Hab[color={C_SIE_PL}]en[/color] [color={C_SIE_PL}]Sie[/color] Cola? (Kola var mı)",
            "Şimdi bir test yapalım.\n\nDoğru zamiri cümleye yerleştirin!"
        ],
        "quiz_hinweis": "Doğru zamiri cümleye yerleştirin (Du / Sie):",
        "quiz_titel": "DOĞRU ZAMİRİ SEÇ",
        "optionen": ["Du", "Sie"],
        "quiz": [
            {
                "anzeige": f"Das sind meine Mitschüler. ___ sind nett.\n[size=15sp][color=#A0A6B2]Bunlar benim sınıf arkadaşlarım. Onlar iyi insanlar.[/color][/size]",
                "antwort": "Sie",
                "vollstaendig": "Das sind meine Mitschüler. Sie sind nett."
            },
            {
                "anzeige": f"Guten Tag Herr Müller, ___ seh[color={C_SIE_PL}]en[/color] heute gut aus.\n[size=15sp][color=#A0A6B2]İyi günler Bay Müller, bugün iyi görünüyorsunuz.[/color][/size]",
                "antwort": "Sie",
                "vollstaendig": "Guten Tag Herr Müller, Sie sehen heute gut aus."
            },
            {
                "anzeige": f"___ arbeit[color={C_DU}]est[/color] sehr hart!\n[size=15sp][color=#A0A6B2]Çok sıkı çalışıyorsun![/color][/size]",
                "antwort": "Du",
                "vollstaendig": "Du arbeitest sehr hart!"
            },
            {
                "anzeige": f"Ich gehe zu meiner Familie. ___ hab[color={C_SIE_PL}]en[/color] mich eingeladen.\n[size=15sp][color=#A0A6B2]Ailemin yanına gidiyorum; beni davet ettiler.[/color][/size]",
                "antwort": "Sie",
                "vollstaendig": "Ich gehe zu meiner Familie. Sie haben mich eingeladen."
            },
            {
                "anzeige": f"___ sieh[color={C_DU}]st[/color] lustig aus.\n[size=15sp][color=#A0A6B2]Komik görünüyorsun.[/color][/size]",
                "antwort": "Du",
                "vollstaendig": "Du siehst lustig aus."
            },
            {
                "anzeige": f"Guten Tag, hab[color={C_SIE_PL}]en[/color] ___ einen Tisch frei?\n[size=15sp][color=#A0A6B2]İyi günler, boş bir masanız var mı?[/color][/size]",
                "antwort": "Sie",
                "vollstaendig": "Guten Tag, haben Sie einen Tisch frei?"
            }
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
        self.quiz_optionen = []
        self.quiz_hinweis = "Doğru fiil sonunu seç:"
        self.quiz_titel = "FİİLİ ÇEKİMLE"
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

    def _anzahl_wiederholungs_karten(self):
        gesamt = 0
        for kat, karten in self.fortschritt.items():
            if isinstance(karten, list) and kat != "grammatik_abgeschlossen":
                gesamt += len(karten)
        return gesamt

    # ---------- 1. Hauptmenü (Start) ----------
    def zeige_hauptmenue(self, *args):
        self.bildschirm_leeren()

        container = BoxLayout(orientation='vertical', size_hint=(1, 1))
        container.add_widget(Widget(size_hint_y=1))

        quadrat_block = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12))
        quadrat_block.bind(minimum_height=quadrat_block.setter('height'))

        self.logo_hinzufuegen(quadrat_block, hoehe=150)

        quadrat_block.add_widget(label("Merhaba! Hoş geldin!", 24, 44, bold=True, color=BLAU))
        quadrat_block.add_widget(label("Ne yapmak istiyorsun?", 15, 26, color=TEXT_MUTED))

        btn_lernen = knopf("Öğren (Lernen)", groesse=18, hoehe=58, farbe=BLAU)
        btn_lernen.bind(on_release=self.zeige_lernen_menue)
        quadrat_block.add_widget(btn_lernen)

        wiederhol_anzahl = self._anzahl_wiederholungs_karten()
        wiederhol_text = f"Tekrar (Wiederholung) · {wiederhol_anzahl}" if wiederhol_anzahl > 0 else "Tekrar (Wiederholung)"
        btn_wiederholen = knopf(wiederhol_text, groesse=18, hoehe=58, farbe=BLAU)
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
        mitte_block.add_widget(label("Lütfen bir kategori seç:", 14, 24, color=TEXT_MUTED))

        btn_vokabeln = knopf("Kelime Kartları (Vokabeln)", groesse=16, hoehe=50, farbe=BLAU)
        btn_vokabeln.bind(on_release=self.zeige_lektionen_menue)
        mitte_block.add_widget(btn_vokabeln)

        btn_phrasen = knopf("Günlük İfadeler (Alltagsphrasen)", groesse=16, hoehe=50, farbe=BLAU)
        btn_phrasen.bind(on_release=self.zeige_phrasen_kategorien_menue)
        mitte_block.add_widget(btn_phrasen)

        btn_grammatik = knopf("Gramer (Grammatik)", groesse=16, hoehe=50, farbe=BLAU)
        btn_grammatik.bind(on_release=self.zeige_grammatik_menue)
        mitte_block.add_widget(btn_grammatik)

        container.add_widget(mitte_block)
        container.add_widget(Widget(size_hint_y=1))
        self.add_widget(container)

    def zeige_platzhalter_info(self, nachricht):
        self.bildschirm_leeren()
        self.add_widget(Widget(size_hint_y=1))
        karte = KarteBox(rand_farbe=KARTE_RAND_BLAU, size_hint_y=None, height=dp(190))
        karte.add_widget(label(nachricht, 19, 80, bold=True, color=BLAU))
        karte.add_widget(label("Bu özellik yakında eklenecektir.", 15, 36, color=TEXT_MUTED))
        self.add_widget(karte)

        zurueck = knopf("Geri Dön", groesse=16, hoehe=56, farbe=BLAU)
        zurueck.bind(on_release=self.zeige_lernen_menue)
        self.add_widget(zurueck)
        self.add_widget(Widget(size_hint_y=1))

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
        layout.add_widget(label("Lütfen bir ders seç:", 16, 30, color=TEXT_MUTED))

        abgeschlossen = self.fortschritt.get("grammatik_abgeschlossen", [])

        for lektions_name in GRAMMATIK_LEKTIONEN.keys():
            ist_fertig = lektions_name in abgeschlossen
            status = "  ✓ (Tamamlandı)" if ist_fertig else ""
            farbe = GRUEN if ist_fertig else BLAU
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

    def _text_ohne_markup(self, text):
        reiner = text.replace("[/color]", "").replace("[/size]", "")
        for code in (C_ICH, C_DU, C_ER, C_SIE_SG, C_ES, C_T_END, C_WIR, C_IHR, C_SIE_PL, "#A0A6B2"):
            reiner = reiner.replace(f"[color={code}]", "")
        reiner = reiner.replace("[size=15sp]", "")
        return reiner

    def zeige_grammatik_karte(self):
        self.bildschirm_leeren()

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        zurueck = knopf("< Dersler", groesse=15, hoehe=52, farbe=GRAU, size_hint_x=None, width=dp(105))
        zurueck.bind(on_release=self.zeige_grammatik_menue)
        top.add_widget(zurueck)
        top.add_widget(label(self.aktuelle_grammatik_lektion, 14, bold=True, color=BLAU))
        self.add_widget(top)

        gesamt = len(self.grammatik_karten)
        fortschritt_quote = (self.grammatik_index + 1) / max(1, gesamt)
        self.add_widget(FortschrittsBalken(fortschritt_wert=fortschritt_quote, fuell_farbe=BLAU))
        self.add_widget(label(f"Kart {self.grammatik_index + 1} / {gesamt}", 14, 28, color=TEXT_MUTED))

        text = self.grammatik_karten[self.grammatik_index]
        reiner_text = self._text_ohne_markup(text)
        schriftgroesse = 25 if len(reiner_text) < 25 else 18

        karte = KarteBox(rand_farbe=KARTE_RAND_BLAU)
        karte.add_widget(label("KONU ANLATIMI", 11, 22, bold=True, color=BLAU))
        karte.add_widget(label(text, schriftgroesse, bold=True, markup=True, color=TEXT_HELL))
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
        self.quiz_optionen = list(lektion.get("optionen", ["-e", "-st", "-est"]))
        self.quiz_hinweis = lektion.get("quiz_hinweis", "Doğru fiil sonunu seç:")
        self.quiz_titel = lektion.get("quiz_titel", "FİİLİ ÇEKİMLE")
        self.quiz_index = 0
        self.quiz_leben = 3
        self.quiz_punkte = 0
        self.zeige_grammatik_quiz_frage()

    def zeige_grammatik_quiz_frage(self, feedback_text="", feedback_farbe=BLAU):
        self.bildschirm_leeren()

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        zurueck = knopf("< Çık", groesse=15, hoehe=52, farbe=GRAU, size_hint_x=None, width=dp(86))
        zurueck.bind(on_release=self.zeige_grammatik_menue)
        top.add_widget(zurueck)
        top.add_widget(label(f"Soru {self.quiz_index + 1} / {len(self.quiz_fragen)}", 15, bold=True, color=BLAU))

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
            self.sprache_abspielen(frage["vollstaendig"])
            self.quiz_index += 1
            if self.quiz_index >= len(self.quiz_fragen):
                self.zeige_grammatik_quiz_erfolg()
            else:
                self.zeige_grammatik_quiz_frage(
                    feedback_text=f"Doğru!  →  {frage['vollstaendig']}",
                    feedback_farbe=GRUEN
                )
        else:
            self.quiz_leben -= 1
            if self.quiz_leben <= 0:
                self.zeige_grammatik_quiz_verloren()
            else:
                self.zeige_grammatik_quiz_frage(
                    feedback_text=f"Yanlış! '{gewaehlte_antwort}' değil. Tekrar dene!",
                    feedback_farbe=ROT
                )

    def zeige_grammatik_quiz_verloren(self):
        self.bildschirm_leeren()
        self.add_widget(Widget(size_hint_y=1))

        karte = KarteBox(rand_farbe=ROT, size_hint_y=None, height=dp(210))
        karte.add_widget(label("Canların Bitti!", 25, 44, bold=True, color=ROT))
        karte.add_widget(label("3 kez yanlış cevap verdin.\nDersi tamamlamak için testi baştan yapmalısın.", 15, 76, color=TEXT_MUTED))
        karte.add_widget(label(f"İlerleme: {self.quiz_index} / {len(self.quiz_fragen)}", 15, 32, bold=True, color=TEXT_HELL))
        self.add_widget(karte)

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

        karte = KarteBox(rand_farbe=GRUEN, size_hint_y=None, height=dp(220))
        karte.add_widget(label("Çok iyi! Başardın!", 25, 44, bold=True, color=GRUEN))
        karte.add_widget(label(self.aktuelle_grammatik_lektion, 16, 32, bold=True, color=BLAU))
        karte.add_widget(label(f"Puan: {self.quiz_punkte} / {gesamt}   ·   Kalan Can: {self.quiz_leben}/3", 16, 42, bold=True, color=TEXT_HELL))
        self.add_widget(karte)

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
        layout.add_widget(label("Lütfen bir ders seç:", 16, 30, color=TEXT_MUTED))

        for lektions_titel, vokabel_liste in self.lektionen.items():
            tuerkisch_titel = LEKTIONS_UEBERSETZUNG.get(lektions_titel, lektions_titel)

            gelernte_liste = self.fortschritt.get(lektions_titel, [])
            anzahl_gelernt = len(gelernte_liste)
            gesamt = len(vokabel_liste)

            ist_komplett = (gesamt > 0 and anzahl_gelernt >= gesamt)
            farbe = GRUEN if ist_komplett else BLAU
            status_text = f"  ✓ ({anzahl_gelernt}/{gesamt})" if ist_komplett else f"  ({anzahl_gelernt}/{gesamt})"
            btn = knopf(f"{tuerkisch_titel}{status_text}", groesse=15, hoehe=56, farbe=farbe)
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
        layout.add_widget(label("Lütfen bir kategori seç:", 16, 30, color=TEXT_MUTED))

        for kat_titel, phrasen_liste in self.phrasen_daten.items():
            gelernte_liste = self.fortschritt.get(kat_titel, [])
            anzahl_gelernt = len(gelernte_liste)
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

        gesamt = len(self.aktuelle_vokabeln)
        quote = (self.karten_index + 1) / max(1, gesamt)
        self.add_widget(FortschrittsBalken(fortschritt_wert=quote, fuell_farbe=BLAU))

        if feedback_text:
            self.add_widget(label(feedback_text, 17, 36, bold=True, color=(0.94, 0.76, 0.06, 1)))

        self.add_widget(label(f"Kart {self.karten_index + 1} / {gesamt}", 14, 28, color=TEXT_MUTED))

        vokabel = self.aktuelle_vokabeln[self.karten_index]

        if not self.ist_umgedreht and vorlesen:
            self.sprache_abspielen(vokabel["de"])

        karte = KarteBox(rand_farbe=KARTE_RAND_BLAU if not self.ist_umgedreht else KARTE_RAND)
        karte.add_widget(label("ALMANCA" if not self.ist_umgedreht else "TÜRKÇE", 13, 30, bold=True, color=BLAU))
        karte.add_widget(label(vokabel["de"] if not self.ist_umgedreht else vokabel["tr"], 31, bold=True, color=TEXT_HELL))
        karte.add_widget(label("(Çevirmek için alttaki butona tıkla)", 13, 28, color=TEXT_MUTED))
        self.add_widget(karte)

        aktion = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140), spacing=dp(10), padding=[0, dp(8), 0, dp(8)])

        if not self.ist_umgedreht:
            hoeren = knopf("Tekrar Dinle (Almanca)", groesse=16, hoehe=56, farbe=BLAU_DUNKEL)
            hoeren.bind(on_release=lambda x: self.sprache_abspielen(vokabel["de"]))
            drehen = knopf("Kartı Çevir", groesse=18, hoehe=56, farbe=BLAU)
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
            gewusst = knopf("Biliyorum!", groesse=16, hoehe=56, farbe=BLAU)
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
        self.add_widget(Widget(size_hint_y=1))

        karte = KarteBox(rand_farbe=GRUEN, size_hint_y=None, height=dp(200))
        karte.add_widget(label("Harika! Ders bitti!", 25, 44, bold=True, color=GRUEN))
        karte.add_widget(label(self.aktiver_titel, 16, 32, bold=True, color=BLAU))
        karte.add_widget(label("Bu dersteki bütün ifadeleri başarıyla tamamladın!", 15, 50, color=TEXT_MUTED))
        self.add_widget(karte)

        neu = knopf("Menüye Dön", groesse=18, hoehe=60, farbe=BLAU)
        neu.bind(on_release=lambda x: self.ruecksprung_funktion())
        self.add_widget(neu)
        self.add_widget(Widget(size_hint_y=1))


class VokabelApp(App):
    def build(self):
        self.title = "Deutsch – Türkisch Lern-App"
        return VokabelRootLayout()


if __name__ == '__main__':
    VokabelApp().run()
