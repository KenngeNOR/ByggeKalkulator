# 🏗️ ByggeKalkulator v1.0
**👉 Prøv appen her: [byggekalkulator.streamlit.app](https://byggekalkulator.streamlit.app/)**

En interaktiv web-applikasjon bygget med **Streamlit**, med god hjelp av Gemini for nøyaktig beregning av materialbehov og kostnader ved oppføring av enkle trekonstruksjoner (vegg, gulv og tak).

## 🚀 Funksjoner
* **Dynamisk Konstruksjon:** Beregn mengder for vegger, bjelkelag og takflater basert på dine egne mål.
* **Smart Materialvalg:** Velg dimensjoner og isolasjonstype direkte fra en database.
* **Prissammenligning:** Bytt mellom ulike butikker (f.eks. Byggmax vs. Standard) for å se hvor du får det billigst.
* **Handleliste:** Genererer en komplett liste over alle materialer som kan lastes ned som CSV.
* **Database-editor:** Innebygd verktøy for å legge til nye varer eller oppdatere priser uten å røre JSON-filen manuelt.

## 🛠️ Installasjon og oppstart

For å kjøre denne applikasjonen lokalt, må du ha Python installert.

1. **Klone repoet:**
   ```bash
   git clone https://github.com/KenngeNOR/ByggeKalkulator.git
   cd ByggeKalkulator
   
2. **Installer avhengigheter:**
   ```bash
   pip install -r requirements.txt
   
3. **Kjør appen:**
   ```bash
   streamlit run app.py
   
   

**Prosjektstruktur**

app.py: Hovedfilen som styrer brukergrensesnittet.
vegg_modul.py, tak_modul.py, gulv_modul.py: Logikk for materialberegning.
data_manager.py: Håndterer lesing/skriving til materialdatabasen.
materialer.json: JSON-databasen som inneholder alle dimensjoner og butikkpriser.


## 📝 Merk for testere
Appen er under utvikling. Hvis du setter mål til 0, vil kalkulatoren nullstilles. Ved bytte av butikk vil prisene oppdateres automatisk basert på data i materialer.json. 
Om en vare mangler pris i valgt butikk, vil den vises med 0,- kr i listen.
   
