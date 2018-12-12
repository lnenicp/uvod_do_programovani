import geojson
import sys
import os

def check_count_argument():
    if (len(sys.argv) < 4):
        sys.exit("Nedostatečný počet parametrů.")

def get_input_filename():
    ''' Slouží pro zadání vstupního souboru'''
    INPUT_FILENAME = sys.argv[1]
    if not INPUT_FILENAME[-8:] == '.geojson':
        sys.exit('Vstupní soubor musí být ve formátu ".geojson"')
    return INPUT_FILENAME

def get_output_filename():
    ''' Slouží pro zadání výstupního souboru'''
    OUTPUT_FILENAME = sys.argv[2]
    if not OUTPUT_FILENAME[-8:] == '.geojson':
        sys.exit('Výstupní soubor musí být ve formátu ".geojson"')
    return OUTPUT_FILENAME

def get_max_features():
    '''Slouží k zadání maximálního počtu bodů v jednom clusteru'''
    MAX_FEATURES = sys.argv[3]
    if MAX_FEATURES.lstrip("-").isdigit():
        MAX_FEATURES=int(MAX_FEATURES)
        if MAX_FEATURES <= 0:
            sys.exit('Zadejte kladné číslo.')
    else:
        sys.exit('Zadejte maximální počet prvků v clusteru(int).')
    return MAX_FEATURES

def check_input_file(INPUT_FILENAME):
    '''Slouží ke kontrole, zda vstupní soubor existuje a lze otevřít.'''
    if os.path.isfile(INPUT_FILENAME):
        try:
            with open(INPUT_FILENAME, encoding='utf-8') as input_data:
                input = geojson.load(input_data)
        except:
            sys.exit('Vstupní soubor nelze otevřít.')
    else:
        sys.exit('Vstupní soubor neexistuje')

def check_correct_geojson(OUTPUT_FILENAME):
    '''Sloouží ke kontrole konektnosti formatu GeoJsonu'''
    with open(OUTPUT_FILENAME, encoding='utf-8') as output_geojson:
        data = geojson.load(output_geojson)

    k_list = []
    for key in data:
        k_list.append(key)

    if ('type' not in k_list) or ('features' not in k_list):
        sys.exit('GeoJson není ve správném formátu.')

def calculate_bbox(features):
    '''
    Vypočítá ohraničující obdélník pro vstupní bodová data.
    :param features: vstupní data (features vstupního GeoJsonu)
    :return: souřanice: min_x, min_y, max_x, max_y
    '''
    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    for feature in features:
        coordinates = feature['geometry']['coordinates']
        point_x = coordinates[0]
        point_y = coordinates[1]
        if point_x < min_x:
            min_x = point_x
        if point_x > max_x:
            max_x = point_x
        if point_y < min_y:
            min_y = point_y
        if point_y > max_y:
            max_y = point_y
    return min_x, min_y, max_x, max_y

def get_half_value(min_value, max_value):
    '''
    Určí střed mezi minimální a maximalní hodnotou.
    (Využito pro hledání os, podle kterých probíhá dělení do kvadrantů.)
    :param min_value: minimální hodnota/souřadnice na dané ose
    :param max_value: maximální hodnota/souřadnice na dané ose
    :return: "průměr" ze zadaných hodnot
    '''
    return (min_value + max_value) / 2

def sort_features(features, half_x, half_y):
    '''
    Rozdělí vstupní data do skupin dle kvadrantu, do kterých přísluší. Přidá se nové properties - 'cluster_id'.
    Zároveň se při tom načte/přidá hodnota příslušného kvadrantu do properties - cluster_id.
    :param features: vstupní data (features vstupního GeoJsonu)
    :param half_x: hodnota osy x, podle které se budou dělit body do kvadrantů
    :param half_y: hodnota osy y, podle které se budou dělit body do kvadrantů
    :return: množiny/listy bodu podle kvadrantu: features1, features2, features3, features4
    '''
    features1 = []
    features2 = []
    features3 = []
    features4 = []
    for feature in features:
        if 'cluster_id' not in feature['properties']:
            feature['properties']['cluster_id'] = ''
        coordinates = feature['geometry']['coordinates']
        x = coordinates[0]
        y = coordinates[1]
        if x < half_x and y > half_y:
            feature['properties']['cluster_id'] += '1'
            features1.append(feature)
        elif x > half_x and y > half_y:
            feature['properties']['cluster_id'] += '2'
            features2.append(feature)
        elif x < half_x and y < half_y:
            feature['properties']['cluster_id'] += '3'
            features3.append(feature)
        elif x > half_x and y < half_y:
            feature['properties']['cluster_id'] += '4'
            features4.append(feature)
    return features1, features2, features3, features4

def quadtree(input_features, output_json, MAX_FEATURES, min_x, min_y, max_x, max_y):
    '''
    Určuje příslušnost vstupních bodů do konkréních clusterů.
    Nejdříve vypočítá "souřadnice os", podle kterých body rozdělí dle kvadrantů. Rozdělí body do kvadrantů.
    Zároveň se id příslušného kvadrantu načte do properties-cluster_id. (Při dalším/opakovaném dělení se
    id "přidá" za již napsanou hodnotu).
    Pokud se v příslušném clusteru nachází více než maximální povolené množství bodů (MAX_FEATURES),
    cluster se bude dělit opakovaně znovu, dokud nebude tato podmínka splněna.
    :param input_features: vstupní data (features vstupního GeoJsonu)
    :param output_json: výstupní data (features výstupního GeoJsonu)
    :param min_x: minimální souřadnice na ose x
    :param min_y: minimální souřadnice na ose y
    :param max_x: maximální souřadnice na ose x
    :param max_y: maximální souřadnice na ose y
    :return: id příslušného kvadrantu se zapíše/připíše do properties-cluster_id
    '''
    if len(input_features) > MAX_FEATURES:

        # vypocte osy, podle kterych se bude delit
        half_x = get_half_value(min_x, max_x)
        half_y = get_half_value(min_y, max_y)

        # body rozradi do skupin podle kvadrantu
        features1, features2, features3, features4 = sort_features(
            input_features, half_x, half_y)

        # funkce se vola opakovane pro vsechny kvadranty a body se dale/opakovane deli
        # minima a maxima se predefinuji pro kazdy kvadrant
        quadtree(
            features1, output_json, MAX_FEATURES,
            min_x=min_x, min_y=half_y, max_x=half_x, max_y=max_y
        )
        quadtree(
            features2, output_json, MAX_FEATURES,
            min_x=half_x, min_y=half_y, max_x=max_x, max_y=max_y
        )
        quadtree(
            features3, output_json, MAX_FEATURES,
            min_x=min_x, min_y=min_y, max_x=half_x, max_y=half_y
        )
        quadtree(
            features4, output_json, MAX_FEATURES,
            min_x=half_x, min_y=min_y, max_x=max_x, max_y=half_y
        )
    else:
        # v kvadrantu je mene nez zvoleny pocet prvku, dalsi deleni neprobiha
        output_json['features'] += input_features


# fce pro spravne spusteni
def run():
    # nacte data
    with open(INPUT_FILENAME, encoding='utf-8') as input_geojson:
        input_json = geojson.load(input_geojson)

    # vyjme "část" s fetaures
    input_features = input_json.pop('features')

    # předpřipravení výstupního souboru - ostatní klíče a hodnoty krome features
    output_json = input_json
    # připravení prázdného listu "feautures" pro výstupní soubor
    output_json['features'] = []

    # výpočet ohraničujícího obdélníku
    min_x, min_y, max_x, max_y = calculate_bbox(input_features)

    # trideni bodu dle kvadratu, zapis hodnot cluster_id
    quadtree(input_features, output_json, MAX_FEATURES, min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

    # finální zápis dat
    with open(OUTPUT_FILENAME, 'w') as output_geojson:
        geojson.dump(output_json, output_geojson)

check_count_argument()
INPUT_FILENAME = get_input_filename()
check_input_file(INPUT_FILENAME)
OUTPUT_FILENAME = get_output_filename()
MAX_FEATURES = get_max_features()
run()
check_correct_geojson(OUTPUT_FILENAME)

print('ok')

