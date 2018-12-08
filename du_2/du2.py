import geojson

# vtup/vystup
input = 'vstup.geojson'
output ='vystup.geojson'

# nacteni dat
with open(input, encoding="utf-8") as json_data:
    data = geojson.load(json_data)

# pridani nove properties 'qt_index' a zapis jeji hodnoty do vystupniho souboru
for i in range(len(data['features'])):
    inx =  1
    data['features'][i]['properties']['qt_index'] = inx
    with open(output, mode="w") as f:
        geojson.dump(data, f)


