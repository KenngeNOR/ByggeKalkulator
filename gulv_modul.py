import math
from logikk import optimal_kjop

def beregn_gulv_pakke(L_cm, B_cm, cc_cm, iso_valg, bjelke_dim, plate_valg, db, valgt_butikk):
    if L_cm <= 0 or B_cm <= 0:
        return {"varer": [], "sum": 0.0}

    L_mm, B_mm = L_cm * 10, B_cm * 10
    varer = []
    
    def hent_pris(vare_nøkkel):
        butikker = db[vare_nøkkel].get("butikker", {})
        return butikker.get(valgt_butikk, butikker.get("Standard", 0))

    antall_bjelker = math.ceil(L_mm / (cc_cm * 10)) + 1
    s_info = db[bjelke_dim]
    l_bj, n_bj, _ = optimal_kjop(B_mm, antall_bjelker, s_info["tilgjengelige_l"])
    
    varer.append({"Vare": f"Gulvbjelke {bjelke_dim}", "Mengde": n_bj, "Enhet": f"stk à {l_bj/1000}m", "Pris": (n_bj * l_bj/1000 * hent_pris(bjelke_dim))})
    
    areal_m2 = (L_mm * B_mm) / 1000000
    p = db[plate_valg]
    n_plat = math.ceil(areal_m2 / ((p["l"] * p["b"]) / 1000000))
    varer.append({"Vare": f"Gulvplate {plate_valg}", "Mengde": n_plat, "Enhet": "stk", "Pris": n_plat * hent_pris(plate_valg)})
    
    if iso_valg != "Ingen":
        i = db[iso_valg]
        n_pakker = math.ceil(areal_m2 / i["m2_pakke"])
        if n_pakker > 0:
            varer.append({"Vare": f"Gulvisolasjon {iso_valg}", "Mengde": n_pakker, "Enhet": "pakker", "Pris": n_pakker * hent_pris(iso_valg)})
            varer.append({"Vare": "Fuktsperre 0.20", "Mengde": 1, "Enhet": "rull", "Pris": hent_pris("fuktspere_020_25m")})

    return {"varer": varer, "sum": sum(v["Pris"] for v in varer)}