#!/usr/bin/env python3
"""Bereitet die Daten für die App vor (einmalig am PC ausführen).

  1. liest die .docx-Frequenzliste und schreibt data/vokabeln.json
  2. mit --audio: erzeugt zu jedem deutschen Wort eine MP3 (gTTS, braucht Internet)

Benötigt nur am PC:  pip install python-docx gTTS
Auf dem Handy werden weder python-docx noch gTTS gebraucht – die App läuft
dadurch komplett offline und ist schneller.

Aufruf:
  python prepare_data.py                       # nur JSON
  python prepare_data.py --audio               # JSON + Audio (bereits vorhandene MP3s werden übersprungen)
  python prepare_data.py meine_liste.docx --audio
"""
import argparse
import json
import os
import time

import docx

HIER = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HIER, "data")
AUDIO = os.path.join(DATA, "audio")


def lade_lektionen_aus_docx(dateipfad):
    doc = docx.Document(dateipfad)
    lektionen = {}
    zaehler = 0
    uebersicht = doc.tables[0]
    for index, zeile in enumerate(uebersicht.rows[1:], start=1):
        lektion_nr = zeile.cells[0].text.strip()
        thema = zeile.cells[1].text.strip()
        titel = f"{lektion_nr}: {thema}"

        vokabeln = []
        for v_zeile in doc.tables[index].rows[1:]:
            zaehler += 1
            vokabeln.append({
                "id": f"{zaehler:05d}",  # eindeutig, wird als Audio-Dateiname genutzt
                "nr": v_zeile.cells[0].text.strip(),
                "de": v_zeile.cells[1].text.strip(),
                "tr": v_zeile.cells[2].text.strip(),
            })
        lektionen[titel] = vokabeln
    return lektionen


def erzeuge_audio(lektionen):
    from gtts import gTTS

    os.makedirs(AUDIO, exist_ok=True)
    alle = [v for vokabeln in lektionen.values() for v in vokabeln]
    for i, v in enumerate(alle, start=1):
        pfad = os.path.join(AUDIO, f"{v['id']}.mp3")
        if os.path.exists(pfad) or not v["de"]:
            continue
        for versuch in range(4):
            try:
                gTTS(text=v["de"], lang="de", slow=False).save(pfad)
                break
            except Exception as e:
                print(f"  Fehler bei '{v['de']}' ({e}), neuer Versuch ...")
                time.sleep(2 * (versuch + 1))
        else:
            print(f"  !! '{v['de']}' übersprungen")
        print(f"[{i}/{len(alle)}] {v['de']}")
        time.sleep(0.2)  # nicht zu schnell, sonst drosselt Google


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", nargs="?",
                    default=os.path.join(HIER, "Frequenzliste_Deutsch_Tuerkisch_Kategorisiert.docx"))
    ap.add_argument("--audio", action="store_true", help="MP3-Sprachaufnahmen erzeugen")
    args = ap.parse_args()

    lektionen = lade_lektionen_aus_docx(args.docx)
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "vokabeln.json"), "w", encoding="utf-8") as f:
        json.dump(lektionen, f, ensure_ascii=False, indent=1)
    gesamt = sum(len(v) for v in lektionen.values())
    print(f"{len(lektionen)} Lektionen, {gesamt} Wörter -> data/vokabeln.json")

    if args.audio:
        erzeuge_audio(lektionen)


if __name__ == "__main__":
    main()
