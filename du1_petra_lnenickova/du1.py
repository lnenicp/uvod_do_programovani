'''
ZOBRAZENI
Pro zvolene zobrazeni a meritko vypiste souradnice rovnobezek a poledniku. Pro tento ukol budeme uvazovat pouze valcova
tecna zobrazena, a to Marinovo, Lambertovo, Braunovo a Mercatorovo. Vasimm ukolem bude vypsat, na jakych souradnicich
na papire byste kreslili rovnobezky a poledniky, kdybyste chteli vykreslit souradnicovou sit pro dana zobrazeni.
Protoze poledniky a rovnobezky jsou svisle, respektive vodorovne, budete vypisovat pouze vzdalenost po vodorovne,
repsektive svisle ose. Rovnobezky i poledniky chcete vypisovat po 10 stupnich. Polomer Zeme budiz pro tento
ukol 6371,11 km.
'''

import math
import sys

def get_proj():
    '''slouží pro zadání zobrazení'''
    proj = input('Zadejte zobrazení:')
    proj = proj.upper()
    if proj not in ('A', 'L', 'B', 'M'):
        sys.exit('Zadejte jednu z naslednujících možností: A - Marinovo zobrazení, L -  Lambertovo zobrazení, B - Braunovo zobrazení, M - Mercatorovo zobrazeni')
    return proj

def get_scale():
    '''slouží pro zadnání vstupbí hodnoty měřítka'''
    scale = input('Zadejte měřítko:')
    if scale.isdigit():
        scale = int(scale)
        if scale == 0:
            sys.exit('Zadejte číslo větší než nula.')
    else:
        sys.exit('Zadejte kladné číslo.')
    return scale

def get_R():
    '''slouží pro zadání vtupní hodnoty poloměru Země, pokud je zadána nula, použije se pomoleěr 6371,11 km'''
    R_def = 637111000
    R_in = input('Zadejte poloměr Země(km):')
    if R_in.isdigit():
        R = int(R_in)
        if R > 0:
            R = int(R) * 100000
        if R == 0:
            R = R_def
        if R < 0:
            sys.exit('Zadejte kladné číslo')
    else:
        sys.exit('Zadejte kladné číslo')
    return R

def generate_net_points_u():
    '''generuje body na ose y po 10 stupních - rovnobezky'''
    u_net = []
    for u in range(-90,100, 10):
        u = u * math.pi / 180
        u_net.append(u)
    return u_net

def generate_net_points_v():
    '''generuje body na ose x po 10 stupních - poledníky'''
    v_net = []
    for v in range(-180,190, 10):
        v = v * math.pi / 180
        v_net.append(v)
    return v_net

def parallels_point(v, R):
    '''Počítá souřadnici bodu na ose x.
    Vstupní hodnotou  je zeměpisná délka bodu.
    Výstupem je souřadnice na ose x v cm.'''
    x = R * v
    cm = round(x / scale, 1)
    # pokud je vzdálenost větší než 100 cm, vypíše se pomlčka
    if -100 < cm and cm > 100:
        cm = '-'
    return cm

def parallels_net(v_net):
    '''Počítá souřadnice bodů na ose x.
    Vstupními hodnotami jsou zeměpisné délky bodů.
    Výstupem jsou souřadnice na ose x v cm.'''
    v_cm = []
    for v in v_net:
        v_cm.append(parallels_point(v, R))
    return v_cm

def meridians_point(u, R):
    '''Počítá souřadnici bodu na ose y.
    Vstupní hodnotou je zeměpisná šířka bodu.
    Výstupem je souřadnice na ose y v cm.'''
    if proj == 'A':
        y = R * u
        cm = round(y / scale, 1)
    if proj == 'L':
        y = R * math.sin(u)
        cm = round(y / scale, 1)
    if proj == 'B':
        y = 2 * R * math.tan(u / 2)
        cm = round(y / scale, 1)
    if proj == 'M':
        if abs(u) == math.pi/2: # poly se zobrazuji v nekonecnu
            cm = math.inf
        elif u == 0:
            cm = 0
        else:
            y = R * math.log(1 / math.tan((math.pi/2 - u) / 2))
            cm = round(y / scale, 1)
    # pokud je vzdálenost větší než 100 cm, vypíše se pomlčka
    if -100 < cm and cm > 100:
        cm = '-'
    return cm

def meridians_net(u_net):
    '''Počítá souřadnice bodů na ose y.
    Vstupními hodnotami jsou zeměpisné šířky bodů.
    Výstupem jsou souřadnice na ose y v cm.'''
    u_cm = []
    for u in u_net:
        u_cm.append(meridians_point(u, R))
    return u_cm

proj = get_proj()
scale = get_scale()
R = get_R()
u_net = generate_net_points_u()
v_net = generate_net_points_v()

print('poledniky:',parallels_net(v_net))
print('rovnobezky:',meridians_net(u_net))


## DOTAZOVANÍ NA SOUŘADNICE KONKRÉTNÍHO BODU
u = None
v = None
while not (u == 0 and v == 0):
    u_point = input('Zadejte zeměpisnou šířku:')
    if u_point.isdigit():
        u = float(u_point)* math.pi / 180
    if not u_point.isdigit():
        sys.exit('Zadejte číslo.')

    v_point = input('Zadejte zeměpisnou délku:')
    if v_point.isdigit():
        v = float(v_point)* math.pi / 180
    if not v_point.isdigit():
        sys.exit('Zadejte číslo.')

    print('rovnoběžka:', meridians_point(u, R))
    print('poledník:', parallels_point(v, R))
