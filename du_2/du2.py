import argparse
import os
import sys

import geojson


def int_gt_1(string_value):
    int_value = int(string_value)
    if int_value < 1:
        raise argparse.ArgumentTypeError("must be integer greater than 0")
    return int_value


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_geojson',
        metavar='INPUT',
        type=argparse.FileType('r', encoding='utf-8'),
        help='input GeoJSON'
    )
    parser.add_argument(
        'output_geojson',
        metavar='OUTPUT',
        type=argparse.FileType('w'),
        help='output GeoJSON'
    )
    parser.add_argument(
        '-mp', '--max-points',
        metavar='MAX_POINTS',
        type=int_gt_1,
        dest='max_points',
        default=50,
        required=False,
        help='maximum amount of points in cluster'
    )
    return parser.parse_args()


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


def quadtree(input_features, output_json, max_features, min_x, min_y, max_x, max_y):
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
    if len(input_features) > max_features:

        # vypocte osy, podle kterych se bude delit
        half_x = get_half_value(min_x, max_x)
        half_y = get_half_value(min_y, max_y)

        # body rozradi do skupin podle kvadrantu
        features1, features2, features3, features4 = sort_features(
            input_features, half_x, half_y)

        # funkce se vola opakovane pro vsechny kvadranty a body se dale/opakovane deli
        # minima a maxima se predefinuji pro kazdy kvadrant
        quadtree(
            features1, output_json, max_features,
            min_x=min_x, min_y=half_y, max_x=half_x, max_y=max_y
        )
        quadtree(
            features2, output_json, max_features,
            min_x=half_x, min_y=half_y, max_x=max_x, max_y=max_y
        )
        quadtree(
            features3, output_json, max_features,
            min_x=min_x, min_y=min_y, max_x=half_x, max_y=half_y
        )
        quadtree(
            features4, output_json, max_features,
            min_x=half_x, min_y=min_y, max_x=max_x, max_y=half_y
        )
    else:
        # v kvadrantu je mene nez zvoleny pocet prvku, dalsi deleni neprobiha
        output_json['features'] += input_features


# fce pro spravne spusteni
def run():
    args = get_args()
    # nacte data
    input_json = geojson.load(args.input_geojson)
    args.input_geojson.close()

    for key in ('type', 'features'):
        if key not in input_json.keys():
            print('not valid GeoJSON', file=sys.stderr)
            sys.exit(2)

    # vyjme "část" s fetaures
    input_features = input_json.pop('features')

    # předpřipravení výstupního souboru - ostatní klíče a hodnoty krome features
    output_json = input_json
    # připravení prázdného listu "feautures" pro výstupní soubor
    output_json['features'] = []

    # výpočet ohraničujícího obdélníku
    min_x, min_y, max_x, max_y = calculate_bbox(input_features)

    # trideni bodu dle kvadratu, zapis hodnot cluster_id
    quadtree(input_features, output_json, args.max_points, min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

    # finální zápis dat
    geojson.dump(output_json, args.output_geojson, indent=2)
    args.output_geojson.close()

    print('ok')


if __name__ == '__main__':
    run()
