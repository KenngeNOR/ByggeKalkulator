import math

def optimal_kjop(trengt_l_mm, antall, tilgjengelige_l):
    """
    Finner den kjøpelengden som gir minst totalt svinn for et gitt antall stykker,
    inkludert beregning for sagbladets tykkelse (kerf).
    """
    if antall <= 0 or trengt_l_mm <= 0 or not tilgjengelige_l:
        return 0, 0, 0
    
    # Standard sagblad-tykkelse (kerf) i mm. 
    # Vi legger til 5mm for å være på den sikre siden.
    sag_svinn = 5 
    
    beste_l = 0
    min_svinn = float('inf')
    totalt_antall_planker = 0
    
    for butikk_lengde in tilgjengelige_l:
        if butikk_lengde < trengt_l_mm:
            continue
            
        # Logikken her er: (Plankelengde + sag_svinn) / (Trengt lengde + sag_svinn)
        # Dette skyldes at du trenger n-1 kutt for n biter. 
        # Ved å legge til sag_svinn på begge sider av brøken, 
        # nøytraliserer vi det faktum at den siste biten ikke trenger et kutt etter seg.
        biter_per_planke = math.floor((butikk_lengde + sag_svinn) / (trengt_l_mm + sag_svinn))
        
        # Hvis biter_per_planke blir 0 (pga sag_svinn), må vi hoppe over
        if biter_per_planke == 0:
            continue
            
        trengte_planker = math.ceil(antall / biter_per_planke)
        
        # Totalt svinn inkluderer nå både restbiter og treverket som ble til sagflis
        totalt_forbruk = trengte_planker * butikk_lengde
        faktisk_nytte = antall * trengt_l_mm
        totalt_svinn = totalt_forbruk - faktisk_nytte
        
        if totalt_svinn < min_svinn:
            min_svinn = totalt_svinn
            beste_l = butikk_lengde
            totalt_antall_planker = trengte_planker
            
    return beste_l, totalt_antall_planker, min_svinn