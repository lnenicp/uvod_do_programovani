import geojson

# vtup/vystup
input = 'vstup.geojson'
output ='vystup.geojson'


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

# nacteni dat
with open(input, encoding="utf-8") as json_data:
    data = geojson.load(json_data)

# pridani nove properties 'qt_index' a zapis jeji hodnoty do vystupniho souboru
for i in range(len(data['features'])):
    inx =  1
    data['features'][i]['properties']['qt_index'] = inx
    with open(output, mode="w") as f:
        geojson.dump(data, f)


