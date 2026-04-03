import math
from logikk import optimal_kjop

def beregn_vegg_pakke(L_tot_cm, H_cm, cc_cm, apninger, er_yttervegg, kled_valg, plat_valg, plate_sider, stender_valg, iso_valg, db, valgt_butikk):
    if L_tot_cm <= 0 or H_cm <= 0:
        return {"varer": [], "sum": 0.0}

    H_mm, L_mm = H_cm * 10, L_tot_cm * 10
    varer = []
    
    def hent_pris(vare_nøkkel):
        butikker = db[vare_nøkkel].get("butikker", {})
        return butikker.get(valgt_butikk, butikker.get("Standard", 0))

    # 1. Rammeverk - kun hvis L > 0
    stendere_ant = math.ceil(L_mm / (cc_cm * 10)) + 1 + (len(apninger) * 2)
    s_info = db[stender_valg]
    l_st, n_st, _ = optimal_kjop(H_mm, stendere_ant, s_info["tilgjengelige_l"])
    
    varer.append({"Vare": f"Stender {stender_valg}", "Mengde": n_st, "Enhet": f"stk à {l_st/1000}m", "Pris": (n_st * l_st/1000 * hent_pris(stender_valg))})
    
    svill_m = (L_mm * 2) / 1000
    varer.append({"Vare": f"Svill {stender_valg}", "Mengde": svill_m, "Enhet": "m", "Pris": svill_m * hent_pris(stender_valg)})

    # Arealberegning
    brutto_m2 = (L_mm * H_mm) / 1000000
    apning_m2 = sum([(a['b'] * a['h']) / 10000 for a in apninger])
    netto_m2 = max(0, brutto_m2 - apning_m2)

    if netto_m2 > 0:
        if er_yttervegg:
            # Kledning osv
            k = db[kled_valg]
            eff_b = (k["b"] - k["overlapp"]) / 1000
            m_kled = math.ceil(netto_m2 / eff_b)
            varer.append({"Vare": f"Utv. Kledning {kled_valg}", "Mengde": m_kled, "Enhet": "m", "Pris": m_kled * hent_pris(kled_valg)})
            varer.append({"Vare": "Vindpapp (rull)", "Mengde": 1, "Enhet": "stk", "Pris": hent_pris("vindpapp_rull")})
            
            n_asfalt = math.ceil(netto_m2 / ((db["asfaltplate"]["l"] * db["asfaltplate"]["b"])/1000000))
            varer.append({"Vare": "Asfaltplater (Vindtett)", "Mengde": n_asfalt, "Enhet": "stk", "Pris": n_asfalt * hent_pris("asfaltplate")})

        if plate_sider > 0:
            p = db[plat_valg]
            p_areal = (p["l"] * p["b"]) / 1000000
            n_p = math.ceil((netto_m2 / p_areal) * plate_sider)
            varer.append({"Vare": f"Veggplate {plat_valg}", "Mengde": n_p, "Enhet": "stk", "Pris": n_p * hent_pris(plat_valg)})
            if er_yttervegg:
                varer.append({"Vare": "Dampsperre (Fuktsperre)", "Mengde": 1, "Enhet": "rull", "Pris": hent_pris("fuktspere_015_15m")})

        if iso_valg != "Ingen":
            i = db[iso_valg]
            n_pakker = math.ceil(netto_m2 / i["m2_pakke"])
            if n_pakker > 0:
                varer.append({"Vare": f"Isolasjon {iso_valg}", "Mengde": n_pakker, "Enhet": "pakker", "Pris": n_pakker * hent_pris(iso_valg)})

    return {"varer": varer, "sum": sum(v["Pris"] for v in varer)}