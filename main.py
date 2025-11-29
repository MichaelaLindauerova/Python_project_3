import sys
import csv
import requests
from bs4 import BeautifulSoup

def nacti_soup(url):
    """
    Stáhne HTML stránku z dané URL a vrátí objekt BeautifulSoup.
    """
    response = requests.get(url)
    response.raise_for_status()  # pokud je chyba (404, 500, atd.), vyhodí výjimku
    return BeautifulSoup(response.text, "html.parser")

def ziskej_obce(soup):
    """
    Z HTML stránky okresu vytáhne seznam obcí. Funguje pro libovolný okres. Projde všechny tabulky a vybere řádky, 
    kde první buňka vypadá jako číselný kód obce. Vrací seznam slovníků.
    """
    obce = []

    tabulky = soup.find_all("table")

    for tabulka in tabulky:
        radky = tabulka.find_all("tr")

        for radek in radky:
            bunky = radek.find_all("td")
            if len(bunky) < 3:
                continue

            kod = bunky[0].get_text(strip=True)
            nazev = bunky[1].get_text(strip=True)

            # podmínka číselného kódu obce (jen číslice)
            if not kod.isdigit():
                continue

            # odkaz na detail 
            odkaz_tag = bunky[0].find("a") or bunky[2].find("a")
            if not odkaz_tag:
                continue

            odkaz = "https://www.volby.cz/pls/ps2017nss/" + odkaz_tag["href"]

            obce.append({
                "kod_obce": kod,
                "nazev_obce": nazev,
                "odkaz": odkaz,
            })
    return obce

def ziskej_zakladni_udaje(soup):
    """
    Z detailu obce vytáhne počet voličů v seznamu, vydané obálky, platné hlasy. Vrací slovník se stringy.
    """

    def ocisti_text(text):
        return text.replace("\xa0", " ").strip()

    def najdi_bunku(header_klic):
        # najdeme <td>, kde atribut headers obsahuje daný klíč (např. "sa2")
        bunka = soup.find("td", headers=lambda value: value and header_klic in value)
        if bunka is None:
            return ""
        return ocisti_text(bunka.text)

    volici = najdi_bunku("sa2")
    obalky = najdi_bunku("sa3")
    platne = najdi_bunku("sa6")
    return {
        "volici": volici,
        "vydane_obalky": obalky,
        "platne_hlasy": platne,
    }

def ziskej_hlasy_stran(soup):
    """
    Z detailu obce vytáhne počty hlasů pro všechny strany. Vrací slovník.
    """
    hlasy_stran = {}

    # projdeme všechny řádky všech tabulek na stránce
    radky = soup.find_all("tr")

    for radek in radky:
        bunky = radek.find_all("td")
        if len(bunky) < 3:
            continue

        # první buňka musí být číslo (pořadí strany) – tak poznáme řádky se stranami
        poradi_text = bunky[0].get_text(strip=True)
        if not poradi_text.isdigit():
            continue

        # druhá buňka = název strany
        nazev_strany = bunky[1].get_text(strip=True)

        # třetí buňka = počet hlasů
        hlasy = bunky[2].get_text(strip=True).replace("\xa0", " ")

        hlasy_stran[nazev_strany] = hlasy
    return hlasy_stran

def ziskej_vysledek_pro_obec(obec):
    """
    Vezme slovník s jednou obcí, stáhne detailní stránku a spojí základní čísla a hlasy stran
    Vrací jeden velký slovník se všemi daty pro danou obec.
    """
    detail_soup = nacti_soup(obec["odkaz"])

    zakladni_udaje = ziskej_zakladni_udaje(detail_soup)
    hlasy_stran = ziskej_hlasy_stran(detail_soup)

    vysledek = {
        "kod_obce": obec["kod_obce"],
        "nazev_obce": obec["nazev_obce"],
        **zakladni_udaje,
        **hlasy_stran,
    }
    return vysledek

def ziskej_vysledky_pro_vsechny_obce(obce):
    """
    Projde všechny obce v okrese a vrátí seznam výsledků. Každý prvek seznamu je jeden slovník dat pro obec.
    """
    vysledky = []

    for obec in obce:
        print(f"Zpracovávám obec: {obec['nazev_obce']}...")
        plna_data = ziskej_vysledek_pro_obec(obec)
        vysledky.append(plna_data)
    return vysledky

def uloz_do_csv(vysledky, nazev_souboru):
    """
    Uloží výsledky do CSV.
    vysledky = seznam slovníků (jeden slovník pro každou obec)
    nazev_souboru = název výstupního CSV
    """
    # základní klíče (první sloupce v CSV)
    zakladni_klice = {"kod_obce", "nazev_obce", "volici", "vydane_obalky", "platne_hlasy"}

    # 1. najdeme všechny názvy politických stran (vyřadíme čistě číselné klíče)
    strany = set()
    for r in vysledky:
        for klic in r:
            if klic in zakladni_klice:
                continue
            # vezmeme jen klíče, které obsahují aspoň jedno písmeno (tj. názvy stran)
            if not any(znak.isalpha() for znak in klic):
                continue
            strany.add(klic)

    strany = sorted(strany)

    # 2. hlavička CSV
    hlavicka = ["kod_obce", "nazev_obce", "volici", "vydane_obalky", "platne_hlasy"]
    hlavicka += strany

    # 3. zápis CSV souboru
    with open(nazev_souboru, mode="w", encoding="utf-8", newline="") as soubor:
        writer = csv.writer(soubor)
        writer.writerow(hlavicka)

        for r in vysledky:
            radek = [
                r["kod_obce"],
                r["nazev_obce"],
                r["volici"],
                r["vydane_obalky"],
                r["platne_hlasy"],
            ]

            # sloupce pro jednotlivé strany
            for strana in strany:
                radek.append(r.get(strana, "0"))

            writer.writerow(radek)

if __name__ == "__main__":

    # kontrola počtu argumentů
    if len(sys.argv) != 3:
        print("Použití: python main.py <URL_OKRESU> <VYSTUPNI_SOUBOR.csv>")
        sys.exit(1)

    url_okresu = sys.argv[1]
    vystupni_soubor = sys.argv[2]

    print("Stahuji data z:", url_okresu)
    soup_okresu = nacti_soup(url_okresu)

    obce = ziskej_obce(soup_okresu)
    print(f"Nalezeno obcí: {len(obce)}")

    vysledky = ziskej_vysledky_pro_vsechny_obce(obce)

    uloz_do_csv(vysledky, vystupni_soubor)
    print(f"Data uložena do souboru: {vystupni_soubor}")