import math
from logikk import optimal_kjop

def beregn_tak_pakke(L_bygg_cm, B_bygg_cm, vinkel, utstikk_cm, sperre_dim, tak_type, db, valgt_butikk):
    if L_bygg_cm <= 0 or B_bygg_cm <= 0:
        return {"varer": [], "sum": 0.0}

    L_mm, B_mm = L_bygg_cm * 10, B_bygg_cm * 10
    U_mm = utstikk_cm * 10
    varer = []
    
    def hent_pris(vare_nøkkel):
        butikker = db[vare_nøkkel].get("butikker", {})
        return butikker.get(valgt_butikk, butikker.get("Standard", 0))
    
    # 1. Sperrer
    grunnlinje_sperre = (B_mm / 2) + U_mm
    rad = math.radians(vinkel)
    # Hindre division by zero hvis vinkel er 90 (umulig her, men god praksis)
    sperre_l_faktisk = grunnlinje_sperre / math.cos(rad) if math.cos(rad) != 0 else grunnlinje_sperre
    
    antall_sperre_par = math.ceil(L_mm / 600) + 1
    tot_sperrer = antall_sperre_par * 2
    
    s_info = db[sperre_dim]
    l_valgt, n_stk, _ = optimal_kjop(sperre_l_faktisk, tot_sperrer, s_info["tilgjengelige_l"])
    
    varer.append({"Vare": f"Taksperre {sperre_dim}", "Mengde": n_stk, "Enhet": f"stk à {l_valgt/1000}m", "Pris": (n_stk * l_stk/1000 * hent_pris(sperre_dim)) if 'l_stk' in locals() else (n_stk * l_valgt/1000 * hent_pris(sperre_dim))})

    # 2. Areal-baserte varer
    takflate_m2 = (2 * sperre_l_faktisk * (L_mm + (2 * U_mm))) / 1000000
    
    if takflate_m2 > 0:
        # Vindpapp
        r_papp = math.ceil(takflate_m2 / (db["vindpapp_rull"]["l"] * (db["vindpapp_rull"]["b"]/1000)))
        varer.append({"Vare": "Undertak / Vindpapp", "Mengde": r_papp, "Enhet": "rull", "Pris": r_papp * hent_pris("vindpapp_rull")})

        # Tekking
        if tak_type in ["Takstein", "Taksteinsplater"]:
            m_sløyfer = math.ceil((tot_sperrer * sperre_l_faktisk) / 1000)
            varer.append({"Vare": "Sløyfer 23x48 mm", "Mengde": m_sløyfer, "Enhet": "m", "Pris": m_sløyfer * hent_pris("sløyfer_23x48")})
            # ... resten av tekking-logikken din her (Lekter, stein etc)
            
    return {"varer": varer, "sum": sum(v["Pris"] for v in varer)}