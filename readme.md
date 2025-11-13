--- SANAVISA-SOVELLUKSEN ASENNUS- JA KÄYTTÖOHJE ---

SOVELLUKSEN KUVAUS:
	Sanavisa on suomi-englanti sanaharjoittelu-sovellus, joka pyörii selaimessa.

---

**Valmis käyttöversio (Windows)**

Valmis sovelluksen asennuspaketti löytyy tästä GitHub-arkistosta.
[Lataa valmis ZIP-tiedosto tästä](https://github.com/ilmari97/Sanavisa-sovellus/releases/latest)

---

**Kehittäjän Setup (Projektin Ajaminen Koodista)**

**Nämä ohjeet on tarkoitettu niille, jotka haluavat ajaa sovellusta kehitystilassa tai muokata lähdekoodia.**

1.  **Kloonaa arkisto:**
    ```bash
    git clone https://github.com/ilmari97/Sanavisa-sovellus.git
    cd Sanavisa-sovellus
    ```
2.  **Virtuaaliympäristö ja Riippuvuudet:**
    Luo ja aktivoi virtuaaliympäristö, ja asenna riippuvuudet:
    ```bash
    # (Aktivoi venv)
    pip install -r requirements.txt
    ```
3.  **Aja sovellus:**
    ```bash
    python sovellus.py
    ```

---

Asennus ja käyttö:

1. **Purkaminen:**
	Pura zip-tiedosto haluamaasi kansioon, johon sinulla on kirjoitusoikeudet. Älä pura työpöydän juureen tai järjestelmäkansioihin.

2. **Tarkistus:**
	Varmista että kansiossa on seuraavat kolme tiedostoa:
	- sovellus.exe
	- sanalista.json (Tallennetut sanaparit)
	- tilastot.json (Tallennetut pelitulokset)

3. **Käynnistys:**
	- Käynnistä sovellus.exe
	- Musta konsoli-ikkuna (palvelin) avautuu. **Älä sulje tätä ikkunaa!**
   	- Kun näet konsolissa viestin "Running on...", avaa selain ja siirry osoitteeseen:

      		http://127.0.0.1:5000

	Käyttäjä voi sulkea sovelluksen sulkemalla ensin selainikkunan ja sitten konsoli-ikkunan.

---
