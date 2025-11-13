# Tuodaan os-moduuli tiedostonkäsittelyä varten, datetime ja ascii_lowercase funktiot, sekä random-moduuli visaa varten.
# Tuodaan myös omatekoinen tiedostonhallinta-moduuli, sekä flask-moduulista halutut funktiot.
from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import datetime   # Tilastointia ja päivän sanaa varten
from string import ascii_lowercase  # Lisätyn sanan tarkastamista varten
import tiedostonhallinta
import random
import copy
import os

# Flaskin alustus ja salaisuusavain
app = Flask(__name__)
app.secret_key = "kissa123koira987"

sanakirja = tiedostonhallinta.tiedoston_luku()  # Luetaan tiedosto kerran muistiin globaaliin muuttujaan

# Etusivu/valikko, joka näyttää valinnat ja sanakirjan koon
@app.route("/")
def valikko():

    sanat = sanakirja
    session["tulos_kasitelty"] = False
    paivan_sana = hae_paivan_sana(sanat)

    # Renderöi valikon HTML-mallin
    return render_template("valikko.html", 
                           sanakirjan_koko = len(sanat), 
                           paivan_sana = paivan_sana)

# Lisää sana
@app.route("/lisaa_sana", methods = ["GET", "POST"])
def lisaa_sana():

    global sanakirja

    # Luodaan sallittujen merkkien joukko (set)
    kirjaimet = {"å", "ä", "ö", " ", "-"} | set(ascii_lowercase) # Vain lowercase, koska käytämme lower() funktiota merkkijonoon

    if request.method == "POST":
        sana_suomi = request.form.get("suomi").lower().strip()  # Pienet kirjaimet, poistetaan välilyönnit alusta ja lopusta
        sana_englanti = request.form.get("englanti").lower().strip()
        if sana_suomi in sanakirja: # Tarkistetaan ettei sanoja ole jo lisätty
            flash(f"Virhe: Sana {sana_suomi} löytyy jo sanalistasta.")
            return redirect(url_for("lisaa_sana"))
        if sana_englanti in sanakirja:
            flash(f"Virhe: Sana {sana_englanti} löytyy jo sanalistasta.")
            return redirect(url_for("lisaa_sana"))
        if not set(sana_suomi).issubset(kirjaimet) or not set(sana_englanti).issubset(kirjaimet):   # Tarkistetaan merkit
            flash("Virhe: Sanat eivät voi sisältää numeroita tai erikoismerkkejä.")
            return redirect(url_for("lisaa_sana"))
        if len(sana_suomi) <= 1 or len(sana_englanti) <= 1: # Tarkistetaan sanojen pituudet
            flash("Virhe: Sanojen on oltava pidempiä kuin yksi merkki.")
            return redirect(url_for("lisaa_sana"))
        if (sana_suomi.count(" ") > 1 or sana_englanti.count(" ") > 1 or
             "  " in sana_suomi or "  " in sana_englanti or
            sana_suomi.count("-") > 1 or sana_englanti.count("-") > 1 or
            "--" in sana_suomi or "--" in sana_englanti):
            flash("Virhe: Sana voi sisältää enintään yhden välilyönnin tai välimerkin.")
            return redirect(url_for("lisaa_sana"))
        tiedostonhallinta.tiedostoon_kirjaus(sana_suomi, sana_englanti) # Kirjoitetaan tiedostoon ja järjestellään se
        sanakirja = tiedostonhallinta.tiedoston_luku()

        return redirect(url_for("valikko")) # Palataan valikkoon    

    return render_template("lisaa_sana.html")   # Näytetään syöttölomake GET-pyynnöllä

# Pelin aloitus
@app.route("/aloita_peli", methods=["POST"])
def aloita_peli():

    sanat = sanakirja
    if len(sanat) < 5:  # Tarkistetaan että sanapareja on vähintään viisi
        return redirect(url_for("valikko"))
    session["koko_sanakirja"] = sanat   # Asetetaan alustavat tiedot sessioon
    session["pisteet"] = 0

    return render_template("asetukset.html", max_kierrokset = len(sanat))

# Pelin alustus asetusten jälkeen
@app.route("/peli_asetettu", methods = ["POST"])
def peli_asetettu():

    try:
        kierrokset = int(request.form.get("kierrokset"))
        pelimuoto = int(request.form.get("pelimuoto"))
    except (ValueError, TypeError): # Virhe syötteessä
        return redirect(url_for("valikko"))
    sanat = session.get("koko_sanakirja", {})
    if 5 <= kierrokset <= len(sanat) and pelimuoto in (1, 2):
        session["kierrokset_yhteensa"] = kierrokset
        session["kierroksia_jaljella"] = kierrokset
        session["pelimuoto"] = pelimuoto
        session["tyo_sanakirja"] = copy.deepcopy(sanat) # Kopio, josta poistetaan sanat pelin ajaksi
        session.pop("palaute", None)    # Poistetaan edellisen pelin palaute istunnosta

        return redirect(url_for("kysy_sana"))   # Ohjaa kysymysreitille
    
    return redirect(url_for("valikko"))

# Kysymysreitti
@app.route("/peli", methods = ["GET", "POST"])
def kysy_sana():

    # Estetään pääsy, jos peliä ei ole aloitettu
    if "tyo_sanakirja" not in session or session.get("kierroksia_jaljella", 0) <= 0:
        return redirect(url_for("tulos"))
    if "vaarat_vastaukset" not in session:
        session["vaarat_vastaukset"] = []   # Alustetaan lista väärille vastauksille
    if request.method == "POST":

        # Vastauksen käsittely
        vastaus = request.form.get("vastaus", "").lower().strip()
        oikea_vastaus = session.get("oikea_vastaus")
        kysymys_sana = session.get("kysymys_sana")
        if vastaus == oikea_vastaus:
            session["pisteet"] += 1
            session["palaute"] = "Oikea vastaus!"
            session["palaute_tyyppi"] = "oikein" # Tyyppi väritystä varten
        else:
            session["palaute"] = f"Väärä vastaus! Oikea vastaus oli {oikea_vastaus}."
            session["palaute_tyyppi"] = "vaarin"

            # Tallennetaan väärä vastaus istuntoon
            session["vaarat_vastaukset"].append({
                "kysymys": kysymys_sana,
                "oikea": oikea_vastaus,
                "kayttaja": vastaus
            })
        session["kierroksia_jaljella"] -= 1
        if session["kierroksia_jaljella"] <= 0: # Jos viimeinen kierros, siirrytään tulokseen
            return redirect(url_for("tulos"))
        
        # Siirrytään uuteen kysymykseen
        return redirect(url_for("kysy_sana"))
    
    tyo_sanakirja = session["tyo_sanakirja"]
    satunnainen_avain = random.choice(list(tyo_sanakirja.keys()))   # Uuden kysymyksen arpominen
    arvo = tyo_sanakirja.pop(satunnainen_avain) # Poistetaan toistumattomuuden takaamiseksi

    # Valmistellaan kysymys ja oikea vastaus
    if session["pelimuoto"] == 1: # Suomi/Englanti
        kysymys = satunnainen_avain
        oikea = arvo
    else: # Englanti/Suomi
        kysymys = arvo
        oikea = satunnainen_avain
    session["kysymys_sana"] = kysymys
    session["oikea_vastaus"] = oikea    # Tallennetaan tiedot sessioon
    session["tyo_sanakirja"] = tyo_sanakirja    # Tallennetaan päivitetty sanakirja takaisin sessioon

    # Renderöidään kysymyssivu
    return render_template("kysymys.html", 
                           kysymys = kysymys, 
                           pelimuoto = session["pelimuoto"], 
                           pisteet = session["pisteet"], 
                           kierros_nro = session["kierrokset_yhteensa"] - session["kierroksia_jaljella"] + 1, 
                           yhteensa = session["kierrokset_yhteensa"], 
                           edellinen_palaute = session.pop("palaute", ""),
                           palaute_tyyppi = session.pop("palaute_tyyppi", ""))

# Tulosreitti
@app.route("/tulos")
def tulos():

    pisteet = session.get("pisteet", 0)
    yhteensa = session.get("kierrokset_yhteensa", 0)
    vaarat = session.get("vaarat_vastaukset", [])
    if yhteensa == 0:   # Estetään ohjelman kaatuminen
        return redirect(url_for("valikko"))
    if yhteensa > 0 and not session.get("tulos_kasitelty", False):  # Tarkistetaan onko tulos jo käsitelty
        prosentti = (pisteet / yhteensa) * 100 if yhteensa > 0 else 0
        session["viime_pisteet"] = pisteet
        session["viime_yhteensa"] = yhteensa
        session["viime_prosentti"] = round(prosentti, 1)
        session.pop("pisteet", None)
        session.pop("kierrokset_yhteensa", None)
        session.pop("tyo_sanakirja", None)

        # Näytetään lomake nimen syöttämiseksi
        return render_template("tulos.html", 
                               pisteet = pisteet,
                               yhteensa = yhteensa, 
                               prosentti = round(prosentti, 1), 
                               kysy_nimi = True,
                               vaarat = vaarat)
    
    # Jos tuloksia ei ole tai ne ovat jo tallennettu, näytetään vain tilastosivu
    return redirect(url_for("nayta_tilastot"))

# Tilastojen tallennus
@app.route("/tallenna_tulos", methods = ["POST"])
def tallenna_tulos():

    nimi = request.form.get("nimi", "Nimetön pelaaja").strip()

    if not session.get("tulos_kasitelty"):
        pisteet = session.pop("viime_pisteet", 0)
        yhteensa = session.pop("viime_yhteensa", 0)
        prosentti = session.pop("viime_prosentti", 0)
        tiedostonhallinta.lisaa_tilasto(nimi, pisteet, yhteensa, prosentti) # Kirjataan tulos tiedostoon
        session["tulos_kasitelty"] = True   # Merkitään tulos käsitellyksi, että sitä ei tallenneta uudelleen päivittämällä sivu

        # Siivotaan pelin jälkeen
        session.pop("pisteet", None)
        session.pop("kierrokset_yhteensa", None)
        session.pop("tyo_sanakirja", None)

    return redirect(url_for("nayta_tilastot"))

# Tilastojen näyttäminen
@app.route("/tilastot")
def nayta_tilastot():

    tilastot = tiedostonhallinta.lue_tilastot()

    # Lajitellaan pistemäärän mukaan (paras tulos ensin)
    lajitellut_tilastot = sorted(tilastot, key = lambda merkinta: merkinta["pisteet"], reverse = True)

    # Nollataan "tulos_kasitelty", jotta uusi peli voi alkaa
    session["tulos_kasitelty"] = False

    return render_template("tilastot.html", tilastot = lajitellut_tilastot)

# Näytä kaikki sanat
@app.route("/kaikki_sanat")
def kaikki_sanat_web():

    sivu_koko = 25  # Kiinteä sivukoko
    try:
        sivu_nro = int(request.args.get("sivu", 1)) # Määritellään nykyinen sivu (oletus 1)
    except (ValueError, TypeError):
        sivu_nro = 1
    sanat = sanakirja
    sanat_lista = list(sanat.items())   # Muutetaan sanat listaksi, jotta Jinja2 käsittelee sen paremmin
    yhteensa_sanoja = len(sanat_lista)
    sivuja_yhteensa = (yhteensa_sanoja + sivu_koko - 1) // sivu_koko    # Lasketaan sivutus
    if sivuja_yhteensa == 0:    # Varmistetaan sivunumero
        sivu_nro = 1
    else:
        if sivu_nro < 1:
            sivu_nro = 1
        if sivu_nro > sivuja_yhteensa:
            sivu_nro = sivuja_yhteensa
    aloitus_indeksi = (sivu_nro - 1) * sivu_koko    # Rajataan sanat näytettävälle sivulle
    lopetus_indeksi = aloitus_indeksi + sivu_koko
    rajatut_sanat= sanat_lista[aloitus_indeksi:lopetus_indeksi]

    return render_template("kaikki_sanat.html", 
                           sanat = rajatut_sanat, 
                           sivu_nro = sivu_nro, 
                           sivuja_yhteensa = sivuja_yhteensa, 
                           yhteensa_sanoja = yhteensa_sanoja, 
                           sivu_koko = sivu_koko)

# Laskee ja palauttaa yhden satunnaisen sanaparin, joka on sama koko päivän ajan
def hae_paivan_sana(sanat: dict):

    if len(sanat) == 0:
        return None
    pv_nro = datetime.now().timetuple().tm_yday # Hae päivän numero (1-366)
    sanat_lista = list(sanat.items())
    indeksi = pv_nro % len(sanat_lista)
    suomi, englanti = sanat_lista[indeksi]

    return {"suomi": suomi.capitalize(), "englanti": englanti.capitalize()}

# Käynnistys
if __name__ == "__main__":

    tiedoston_nimi = tiedostonhallinta.resurssi_polku("sanalista.json")
    # Varmistetaan että "sanalista.json" on tyhjä, jos se puuttuu
    if not os.path.exists(tiedoston_nimi):
        with open(tiedoston_nimi, "w", encoding = "utf-8") as tiedosto:
            tiedosto.write("{}")

    app.run(debug = False)