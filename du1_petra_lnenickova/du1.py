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

# vstupní hodnota zobrazeni
proj = input('Zadejte zobrazení:')
proj = proj.upper()
if len(proj) != 1 \
    or proj not in ('A', 'L', 'B', 'M'):
    sys.exit('Zadejte jednu z naslednujících možností: A - Marinovo zobrazení, L -  Lambertovo zobrazení, B - Braunovo zobrazení, M - Mercatorovo zobrazení')

# vstupní hodnota měřítka
scale = input('Zadejte měřítko:')
if scale.isdigit():
    scale = int(scale)
    if scale == 0:
        sys.exit('Zadejte číslo větší než nula.')
else:
    sys.exit('Zadejte kladné číslo.')

# vstupní hodnota poloměru Země
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

## urceni pruseciku (po 10s) s osami x a y
# rovnobezky
u_net = []
for u in range(-90,100, 10):
    u = u * math.pi / 180
    u_net.append(u)

# poledniky
v_net = []
for v in range(-180,190, 10):
    v = v * math.pi / 180
    v_net.append(v)

## VÝPOČET SOUŘADNIC POLEDNÍKŮ
# výpočet pro jednotlivý bod
def parallels_point(v):
    x = R * v
    cm = round(x / scale, 1)
    return cm

# výpočet souřadnic sítě
def parallels_net():
    v_cm = []
    for v in v_net:
        v_cm.append(parallels_point(v))
    return v_cm

## VÝPOČET SOUŘADNIC ROVNOBĚŽEK
# výpočet pro jednotlivý bod
def meridians_point(u):
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
        # do ln() mohou vstupovat pouze kladna cisla, proto rozdeleni do intervalu a "hra s minusem"
        if u > 0:
            y = R * math.log(math.tan(u / 2 + math.pi / 4), math.e)
            cm = round(y / scale, 1)
        if u < 0:
            u = - u
            y = R * math.log(math.tan(u / 2 + math.pi / 4), math.e)
            cm = - round(y / scale, 1)
        if u == 0:
            cm = 0
    return cm

# výpočet souřadnic sítě
def meridians_net():
    u_cm = []
    if proj in ('A', 'L', 'B'):
        for u in u_net:
            u_cm.append(meridians_point(u))
    if proj == 'M':
        merid_M = u_net[1:-1] # poly se nezobrazi, proto odebrany hodnoty -90, 90
        for u in merid_M:
            u_cm.append(meridians_point(u))
    return u_cm

# tisk výsledku
print('rovnobežky:',meridians_net())
print('poledníky:', parallels_net())


## DOTAZOVANÍ NA SOUŘADNICE KONKRÉTNÍHO BODU
u = None
v = None
while u != 0 and v != 0:
    u_point = input('Zadejte zeměpisnou šířku:')
    if u_point.isdigit():
        u = int(u_point)* math.pi / 180
    if not u_point.isdigit():
        sys.exit('Zadejte číslo.')

    v_point = input('Zadejte zeměpisnou délku:')
    if v_point.isdigit():
        v = int(v_point)* math.pi / 180
    if not v_point.isdigit():
        sys.exit('Zadejte číslo.')

    print('rovnoběžka:', meridians_point(u))
    print('poledník:', parallels_point(v))




