import geojson

# vtup/vystup
input = 'vstup.geojson'
output ='vystup.geojson'

property_name = 'cluster_id'

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
        if property_name not in feature['properties']:
            feature['properties'][property_name] = ''
        coordinates = feature['geometry']['coordinates']
        x = coordinates[0]
        y = coordinates[1]
        if x < half_x and y > half_y:
            feature['properties'][property_name] += '1'
            features1.append(feature)
        elif x > half_x and y > half_y:
            feature['properties'][property_name] += '2'
            features2.append(feature)
        elif x < half_x and y < half_y:
            feature['properties'][property_name] += '3'
            features3.append(feature)
        elif x > half_x and y < half_y:
            feature['properties'][property_name] += '4'
            features4.append(feature)
    return features1, features2, features3, features4

# nacteni dat
with open(input, encoding="utf-8") as json_data:
    data = geojson.load(json_data)

features = input_json.pop('features')

'''
# pridani nove properties 'qt_index' a zapis jeji hodnoty do vystupniho souboru
for i in range(len(data['features'])):
    inx =  1
    data['features'][i]['properties']['qt_index'] = inx
'''
with open(output, mode="w") as f:
    geojson.dump(data, f)


