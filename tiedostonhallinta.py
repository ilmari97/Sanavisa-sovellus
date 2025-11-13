# Tuodaan json-, os-, sys-moduulit ja datetime-funktio.
import json
import os
import sys
from datetime import datetime

# Palautaa absoluuttisen polun resurssitiedostoon, riippuen ajetaanko ohjelmaa PyInstaller-paketista vai suoraan Pythonilla
def resurssi_polku(suhteellinen_polku):

    if hasattr(sys, "_MEIPASS"):    # Pakotetaan polku exe-tiedoston sijaintiin, jotta kirjoitetut tiedot säilyvät
        perus_polku = os.path.abspath(os.path.dirname(sys.executable))
    else:   # Perus ajotapa (kehitys)
        perus_polku = os.path.abspath(".")

    return os.path.join(perus_polku, suhteellinen_polku)

# Funktio, jonka tehtävänä on lukea "sanalista.json" tiedoston sisältö sanakirja muuttujaan
def tiedoston_luku():

    sanakirja = {}  # Alustetaan tyhjä sanakirja, jos tiedoston lukeminen epäonnistuu
    tiedoston_nimi = resurssi_polku("sanalista.json")
    try:
        with open(tiedoston_nimi, "r", encoding="utf-8") as tiedosto:
            sanakirja = json.load(tiedosto) # Ladataan tiedosto sanakirja muuttujaan
    except (json.JSONDecodeError, IOError):
        pass

    return sanakirja

# Funktio, jonka tehtävänä on kirjata käyttäjän antamat sanat sanakirjaan ja järjestellä sanat aakkosjärjestykseen       
def tiedostoon_kirjaus(sana_suomi: str, sana_englanti: str):

    sanakirja = tiedoston_luku()
    sanakirja[sana_suomi] = sana_englanti
    jarjestetty = dict(sorted(sanakirja.items()))   # Järjestellään sanakirja aakkosjärjestykseen
    tiedoston_nimi = resurssi_polku("sanalista.json")
    try:    # Avataan tiedosto ja kirjataan siihen sanakirjan päivitetty versio, joka sisältää käyttäjän antamat syötteet
        with open(tiedoston_nimi, "w", encoding="utf-8") as tiedosto:
            json.dump(jarjestetty, tiedosto, indent=4, ensure_ascii=False)
    except IOError:
        pass

# Funktio tilastojen lukemiseen
def lue_tilastot():

    tiedoston_nimi = resurssi_polku("tilastot.json")

    # Lukee tilastot tiedostosta tai palauttaa tyhjän listan
    if not os.path.exists(tiedoston_nimi):
        return []
    try:
        with open(tiedoston_nimi, "r", encoding = "utf-8") as tiedosto:
            return json.load(tiedosto)
    except (json.JSONDecodeError, IOError):
        return []
    
# Funktio tilastojen lisäämiseen
def lisaa_tilasto(nimi, pisteet, yhteensa, oikein_prosentti):

    tilastot = lue_tilastot()
    uusi_merkinta = {
        "nimi": nimi, 
        "paivamaara": datetime.now().strftime("%d.%m.%Y - %H.%M"), 
        "pisteet": pisteet, 
        "yhteensa": yhteensa, 
        "prosentti": oikein_prosentti
    }
    tilastot.append(uusi_merkinta)
    tiedoston_nimi = resurssi_polku("tilastot.json")
    try:
        with open(tiedoston_nimi, "w", encoding = "utf-8") as tiedosto:
            json.dump(tilastot, tiedosto, indent = 4, ensure_ascii = False)
    except IOError:
        print(f"Virhe tilastojen kirjoittamisessa tiedostoon {tiedoston_nimi}")