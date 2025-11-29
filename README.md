# Volební scraper - výsledky voleb do Poslanecké sněmovny 2017

Tento projekt je scraper, který automaticky stahuje výsledky voleb do
Poslanecké sněmovny Parlamentu ČR (2017) z webu volby.cz.\
Uživatel do skriptu zadá **URL vybraného okresu** (územního celku) z
hlavní tabulky a skript stáhne výsledky hlasování **pro všechny obce v
daném okrese**.

------------------------------------------------------------------------

## Jak získat URL okresu (územního celku)

1.  Otevřeme hlavní stránku voleb:\
    https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ

2.  Uvidíme tabulku se seznamem okresů.

3.  U vybraného okresu klikneme na odkaz ve sloupci **„X"** (nebo na
    číselný odkaz okresu).\
    Otevře se stránka obsahující výsledky pro daný okres, např.:

        https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3203

4.  Tuto URL použijeme jako **první argument** při spuštění skriptu.

------------------------------------------------------------------------

## Jak skript funguje

1.  Načte HTML stránku okresu.
2.  Najde všechny obce z tabulek na stránce.
3.  U každé obce získá odkaz na detail (sloupec **Číslo** nebo **X**).
4.  Z detailu každé obce vytáhne:
    -   počet voličů v seznamu,
    -   počet vydaných obálek,
    -   počet platných hlasů,
    -   počty hlasů pro jednotlivé politické strany.
5.  Výsledky uloží do jednoho CSV souboru.

------------------------------------------------------------------------

## Jak skript spustit

Skript se spouští z příkazové řádky a vyžaduje dva argumenty:

1.  **URL okresu** z hlavní tabulky\
2.  **Název výstupního CSV souboru**

### Ukázka spuštění:

``` bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3203" vysledky_plzen.csv
```

Po dokončení se zobrazí:

    Data uložena do souboru: vysledky_plzen.csv

------------------------------------------------------------------------

## Formát výstupního CSV

CSV soubor má následující strukturu:

  -----------------------------------------------------------------------
  Sloupec                             Popis
  ----------------------------------- -----------------------------------
  `kod_obce`                              číselný kód obce

  `nazev_obce`                              název obce

  `volici`                        počet voličů v seznamu

  `vydane_obalky`                         vydané obálky

  `platne_hlasy`                             platné hlasy

  `…`                                 následuje jeden sloupec pro každou
                                      politickou stranu (hodnota = počet
                                      hlasů)
  -----------------------------------------------------------------------

## Použité knihovny

Projekt využívá tyto knihovny:

-   `requests`\
-   `beautifulsoup4`

Instalace všech požadovaných knihoven:

``` bash
pip install -r requirements.txt
```

Soubor `requirements.txt` byl automaticky vygenerován pomocí:

    pip freeze > requirements.txt

------------------------------------------------------------------------

## Poznámky

-   Skript funguje pro libovolný okres - stačí předat jinou URL.
-   Počet politických stran není pevně daný - skript jej dynamicky
    detekuje z HTML.
-   Výstupní CSV je v kódování UTF-8.
-   Kód je v českém jazyce včetně komentářů.

------------------------------------------------------------------------

## Autor

Projekt vytvořila Michaela Lindauerová jako závěrečný úkol v rámci Python Akademie -- Engeto.
