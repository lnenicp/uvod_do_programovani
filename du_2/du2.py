import geojson

# vtup/vystup
INPUT_FILENAME = 'input.geojson'
OUTPUT_FILENAME = 'output.geojson'
MAX_FEATURES = 50

PROPERTY_NAME = 'cluster_id'

def calculate_bbox(features):
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
    return (min_value + max_value) / 2

def sort_features(features, half_x, half_y):
    '''
    Rozdeli vstupni data do skupin dle kvadrantu, do kterych prislusi.
    (Pomoci prideleni hodnoty do cluster_id)
    :param features: vstupni data
    :param half_x: hodnota osy x, podle ktere se bude delit
    :param half_y: hodnota osy y, podle ktere se bude delit
    :return: množiny/listy bodu podle kvadrantu
    '''
    features1 = []
    features2 = []
    features3 = []
    features4 = []
    for feature in features:
        # vlozeni "cluster_id", vytvoreni prazdneho str
        if PROPERTY_NAME not in feature['properties']:
            feature['properties'][PROPERTY_NAME] = ''
        coordinates = feature['geometry']['coordinates']
        x = coordinates[0]
        y = coordinates[1]
        if x < half_x and y > half_y:
            feature['properties'][PROPERTY_NAME] += '1'
            features1.append(feature)
        elif x > half_x and y > half_y:
            feature['properties'][PROPERTY_NAME] += '2'
            features2.append(feature)
        elif x < half_x and y < half_y:
            feature['properties'][PROPERTY_NAME] += '3'
            features3.append(feature)
        elif x > half_x and y < half_y:
            feature['properties'][PROPERTY_NAME] += '4'
            features4.append(feature)
    return features1, features2, features3, features4

def quadtree(input_features, output_json, min_x, min_y, max_x, max_y):
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
            features1, output_json,
            min_x=min_x, min_y=half_y, max_x=half_x, max_y=max_y
        )
        quadtree(
            features2, output_json,
            min_x=half_x, min_y=half_y, max_x=max_x, max_y=max_y
        )
        quadtree(
            features3, output_json,
            min_x=min_x, min_y=min_y, max_x=half_x, max_y=half_y
        )
        quadtree(
            features4, output_json,
            min_x=half_x, min_y=min_y, max_x=max_x, max_y=half_y
        )
    else:
        print(f'less than "{MAX_FEATURES}" features, saving to output')
        output_json['features'] += input_features


# fce pro spravne spusteni
def run():
    # nacte data
    with open(INPUT_FILENAME, encoding='utf-8') as input_geojson:
        input_json = geojson.load(input_geojson)

    # vyjme "část" s fetaures
    input_features = input_json.pop('features')

    # přepřipravení výstupního souboru - ostatní klíče a hodnoty krome features
    output_json = input_json
    # připravení prázdného listu "feautures" pro výstupní soubor
    output_json['features'] = []

    # výpočet ohraničujícího obdélníku
    min_x, min_y, max_x, max_y = calculate_bbox(input_features)

    # trideni bodu do kvadratu (soucasne tvorba "cluster_id"
    quadtree(input_features, output_json,min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

    # finální zápis dat
    with open(OUTPUT_FILENAME, 'w') as output_geojson:
        geojson.dump(output_json, output_geojson)


run()
