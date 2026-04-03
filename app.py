import streamlit as st
import pandas as pd
import math
from vegg_modul import beregn_vegg_pakke
from tak_modul import beregn_tak_pakke
from gulv_modul import beregn_gulv_pakke
from data_manager import last_materialer, lagre_materialer

st.set_page_config(page_title="ByggKalkulator v1.0", layout="wide", page_icon="🏗️")

# Laster database i oppstarten
if 'db' not in st.session_state: 
    st.session_state.db = last_materialer()

if 'apninger' not in st.session_state: st.session_state.apninger = []
if 'manuelle_varer' not in st.session_state: st.session_state.manuelle_varer = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏗️  ByggKalkulator")
    
    # 1. Hent ut alle unike butikknavn fra databasen
    alle_butikker = set()
    for vare in st.session_state.db.values():
        if "butikker" in vare:
            alle_butikker.update(vare["butikker"].keys())
    
    # Lag en sortert liste, eller bruk ["Standard"] hvis databasen er tom
    list_butikker = sorted(list(alle_butikker)) if alle_butikker else ["Standard"]

    # 2. Butikkvelger - denne styrer prisene i hele appen
    st.subheader("🛒 Prisvalg")
    valgt_butikk = st.selectbox(
        "Velg butikk for beregning:", 
        list_butikker,
        help="Appen henter priser fra denne butikken. Finnes ikke prisen, brukes 0 kr."
    )

    st.divider()

    # 3. Totaloversikt
    st.subheader("💰 Totaloversikt")
    container_pris = st.empty()
    
    st.divider()

    # 4. Nullstill-knapp
    if st.button("🗑️ Nullstill alt"):
        st.session_state.apninger = []
        st.session_state.manuelle_varer = []
        st.rerun()

# --- HOVEDINNHOLD ---
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Konstruksjon", "➕ Ekstra utstyr", "🛒 Handleliste", "⚙️ Database"])

with tab1:
    with st.expander("📐 1. Hovedmål", expanded=True):
        c1, c2, c3 = st.columns(3)
        L = c1.number_input("Lengde (cm)", value=0, step=10)
        B = c2.number_input("Bredde (cm)", value=0, step=10)
        H = c3.number_input("Høyde (cm)", value=0, step=10)

    with st.expander("🖼️ 2. Åpninger", expanded=False):
        ca1, ca2, ca3 = st.columns([2, 2, 1])
        nb = ca1.number_input("Bredde (cm)", value=100)
        nh = ca2.number_input("Høyde (cm)", value=210)
        if ca3.button("➕ Legg til"):
            st.session_state.apninger.append({'b': nb, 'h': nh})
            st.rerun()
        for i, apn in enumerate(st.session_state.apninger):
            col_txt, col_btn = st.columns([4, 1])
            col_txt.write(f"• {apn['b']}x{apn['h']} cm")
            if col_btn.button("Slett", key=f"del_{i}"):
                st.session_state.apninger.pop(i)
                st.rerun()

    st.header("⚙️ Konfigurasjon")
    cv, cg, ct = st.columns(3)

    db_keys = st.session_state.db.keys()

    with cv:
        st.subheader("🧱 Vegg")
        v_er_ytter = st.toggle("Yttervegg-pakke", value=True)
        v_sider = st.radio("Plater på sider:", [0, 1, 2], index=1, horizontal=True)
        v_cc = st.selectbox("CC-avstand", [30, 40, 60], index=2)
        v_std = st.selectbox("Stender", [k for k in db_keys if "48x" in k])
        v_iso = st.selectbox("Isolasjon Vegg", [k for k in db_keys if "ursa" in k] + ["Ingen"])
        v_plt = st.selectbox("Plate", [k for k in db_keys if any(x in k for x in ["gips", "spon_vegg", "osb"])])
        v_kld = st.selectbox("Kledning", [k for k in db_keys if "kledning" in k]) if v_er_ytter else None

    with cg:
        st.subheader("🏠 Gulv")
        g_aktiv = st.checkbox("Beregn Gulv", value=True)
        g_std = st.selectbox("Bjelkelag", [k for k in db_keys if "48x" in k], disabled=not g_aktiv)
        g_plt = st.selectbox("Gulvplate", [k for k in db_keys if "spon_gulv" in k or "osb" in k], disabled=not g_aktiv)
        g_cc = st.selectbox("CC Gulv", [30, 60], index=1, disabled=not g_aktiv)
        g_iso = st.selectbox("Isolasjon Gulv", [k for k in db_keys if "ursa" in k] + ["Ingen"], disabled=not g_aktiv)

    with ct:
        st.subheader("📐 Tak")
        t_aktiv = st.checkbox("Beregn Tak", value=True)
        t_type = st.selectbox("Type taktekking", ["Takstein", "Taksteinsplater", "Shingel"], disabled=not t_aktiv)
        t_v = st.slider("Takvinkel (°)", 0, 45, 15, disabled=not t_aktiv)
        t_std = st.selectbox("Sperre", [k for k in db_keys if any(x in k for x in ["48x", "36x"])], disabled=not t_aktiv)
        
        if t_aktiv and t_type == "Takstein" and "48x98" in t_std:
            st.warning("⚠️ 48x98 er spinkelt for takstein! Vurder 48x148 eller mer.")

    # Legg til valgt_butikk til slutt i hvert kall:

# --- BEREGNINGER ---
# Vi oppretter tomme resultater som fallback hvis boksene ikke er huket av
res_v = {'varer': [], 'sum': 0.0}
res_g = {'varer': [], 'sum': 0.0}
res_t = {'varer': [], 'sum': 0.0}

# Vegg beregnes alltid (eller legg til checkbox hvis ønskelig)
# Vegg beregnes kun hvis vi har lengde og høyde
if L > 0 and H > 0:
    res_v = beregn_vegg_pakke(
        (L*2)+(B*2)-10, H, v_cc, 
        st.session_state.apninger, 
        v_er_ytter, v_kld, v_plt, v_sider, v_std, v_iso, 
        st.session_state.db, 
        valgt_butikk
    )

# Gulv beregnes kun hvis boks er huket av OG vi har areal
if g_aktiv and L > 0 and B > 0:
    res_g = beregn_gulv_pakke(L, B, g_cc, g_iso, g_std, g_plt, st.session_state.db, valgt_butikk)

# Tak beregnes kun hvis boks er huket av OG vi har areal
if t_aktiv and L > 0 and B > 0:
    res_t = beregn_tak_pakke(L, B, t_v, 30, t_std, t_type, st.session_state.db, valgt_butikk)

# Samle alle varer
alle_varer = res_v['varer'] + res_g['varer'] + res_t['varer'] + st.session_state.manuelle_varer
total_sum = sum(v['Pris'] for v in alle_varer)

# Oppdater metric i sidebar med en gang
container_pris.metric("Totalpris", f"{total_sum:,.2f} kr")

with tab2:
    st.header("➕ Manuelt utstyr")
    m_c1, m_c2, m_c3, m_c4 = st.columns([3, 1, 1, 1])
    m_navn = m_c1.text_input("Varenavn")
    m_ant = m_c2.number_input("Antall", min_value=1, value=1)
    m_enh = m_c3.selectbox("Enhet", ["stk", "pk", "eske", "rull", "m"])
    m_pris = m_c4.number_input("Pris pr enhet", min_value=0.0, step=10.0)
    if st.button("Legg til"):
        if m_navn:
            st.session_state.manuelle_varer.append({"Vare": m_navn, "Mengde": m_ant, "Enhet": m_enh, "Pris": m_ant * m_pris})
            st.rerun()

    for i, m_vare in enumerate(st.session_state.manuelle_varer):
        mc1, mc2 = st.columns([4, 1])
        mc1.write(f"**{m_vare['Vare']}**: {m_vare['Mengde']} {m_vare['Enhet']} - {m_vare['Pris']:.2f} kr")
        if mc2.button("Fjern", key=f"man_del_{i}"):
            st.session_state.manuelle_varer.pop(i)
            st.rerun()

with tab3:
    st.header("🛒 Handleliste")
    
    # Samle alle varer fra beregningene
    alle_varer = res_v['varer'] + res_g['varer'] + res_t['varer'] + st.session_state.manuelle_varer
    
    if alle_varer:
        df = pd.DataFrame(alle_varer)
        
        # Sjekk etter varer med 0 kr (potensielle feil i databasen)
        mangler_pris = df[df['Pris'] == 0]
        if not mangler_pris.empty:
            st.warning(f"⚠️ {len(mangler_pris)} vare(r) mangler pris i valgt butikk ({valgt_butikk})!")
            st.caption("Sjekk databasen for: " + ", ".join(mangler_pris['Vare'].unique()))

        # Vis tabellen
        st.table(df.assign(Pris=df['Pris'].map('{:,.2f} kr'.format)))
        
        # Bruk den ferdigberegnede total_sum fra hovedløkka
        st.subheader(f"Total: {total_sum:,.2f} kr")
        
        st.download_button("📥 Last ned CSV", df.to_csv(index=False).encode('utf-8'), "handleliste.csv", "text/csv")
    else:
        st.warning("Ingen varer i listen ennå.")

with tab4:
    st.header("⚙️ Materialdatabase")
    st.info("Endringer du gjør her lagres permanent i materialer.json.")

    vareliste = list(st.session_state.db.keys())
    valgt_vare = st.selectbox("Velg vare å redigere", vareliste)

    if valgt_vare:
        data = st.session_state.db[valgt_vare]
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏢 Butikker & Priser")
            
            # Liste over eksisterende butikkpriser for denne varen
            oppdaterte_butikker = data.get("butikker", {}).copy()
            
            for butikk_navn, pris in list(oppdaterte_butikker.items()):
                col_b, col_p, col_del = st.columns([2, 2, 1])
                ny_p = col_p.number_input(f"Pris {butikk_navn}", value=float(pris), step=0.5, key=f"p_{valgt_vare}_{butikk_navn}")
                oppdaterte_butikker[butikk_navn] = ny_p
                
                col_b.markdown(f"**{butikk_navn}**")
                if col_del.button("🗑️", key=f"del_{valgt_vare}_{butikk_navn}"):
                    del oppdaterte_butikker[butikk_navn]
                    st.session_state.db[valgt_vare]["butikker"] = oppdaterte_butikker
                    lagre_materialer(st.session_state.db)
                    st.rerun()

            st.divider()
            st.write("➕ **Legg til ny butikkpris**")
            ny_b_navn = st.text_input("Butikknavn (f.eks. Byggmax)")
            ny_b_pris = st.number_input("Pris", min_value=0.0, step=0.5)
            
            if st.button(f"Legg til {ny_b_navn}"):
                if ny_b_navn:
                    oppdaterte_butikker[ny_b_navn] = ny_b_pris
                    st.session_state.db[valgt_vare]["butikker"] = oppdaterte_butikker
                    lagre_materialer(st.session_state.db)
                    st.success(f"Lagt til {ny_b_navn}")
                    st.rerun()
            
        with c2:
            st.subheader("📐 Dimensjoner & Egenskaper")
            oppdaterte_egenskaper = {}
            for key, val in data.items():
                # Vi hopper over 'butikker' her siden det styres i c1
                if key not in ["butikker", "pris"]: 
                    if isinstance(val, (int, float)):
                        oppdaterte_egenskaper[key] = st.number_input(f"{key.capitalize()}", value=val)
                    elif isinstance(val, list):
                        str_val = ", ".join(map(str, val))
                        ny_str = st.text_input(f"{key} (kommaseparert)", value=str_val)
                        try:
                            oppdaterte_egenskaper[key] = [int(x.strip()) for x in ny_str.split(",") if x.strip()]
                        except ValueError:
                            st.error(f"Ugyldig format for {key}. Bruk kun tall og komma.")
                            oppdaterte_egenskaper[key] = val
                    else:
                        oppdaterte_egenskaper[key] = st.text_input(f"{key}", value=str(val))

        st.divider()
        if st.button(f"💾 Lagre alle endringer for {valgt_vare}", use_container_width=True):
            # Oppdater både butikker og tekniske data
            st.session_state.db[valgt_vare]["butikker"] = oppdaterte_butikker
            for k, v in oppdaterte_egenskaper.items():
                st.session_state.db[valgt_vare][k] = v
            
            lagre_materialer(st.session_state.db)
            st.success(f"Alt lagret for {valgt_vare}!")
            st.rerun()

    st.divider()
    st.subheader("➕ Opprett helt ny vare")
    ny_nøkkel = st.text_input("Varens ID (f.eks '48x48_lekter_impr')")
    start_butikk = st.text_input("Første butikk", value="Byggmax")
    start_pris = st.number_input("Startpris", min_value=0.0, step=1.0)
    
    if st.button("Opprett vare i databasen"):
        if ny_nøkkel and ny_nøkkel not in st.session_state.db:
            st.session_state.db[ny_nøkkel] = {
                "butikker": {start_butikk: start_pris}
            }
            lagre_materialer(st.session_state.db)
            st.success(f"Opprettet {ny_nøkkel}!")
            st.rerun()
        else:
            st.error("Varen finnes allerede eller ID mangler.")