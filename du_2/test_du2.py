import subprocess
import sys

import geojson

import du2


def get_return_code(input_list):
    subproc = subprocess.Popen(input_list)
    subproc.communicate()
    return subproc.returncode


def test_no_argument():
    returncode = get_return_code([sys.executable, 'du2.py'])
    assert returncode == 2


def test_nonexisting_input():
    returncode = get_return_code([sys.executable, 'du2.py', 'foo.bar'])
    assert returncode == 2


def test_missing_output():
    returncode = get_return_code([sys.executable, 'du2.py', 'valid_input.geojson'])
    assert returncode == 2


def test_success():
    returncode = get_return_code([sys.executable, 'du2.py', 'valid_input.geojson', 'test_output.geojson'])
    assert returncode == 0


def test_invalid_mp():
    returncode = get_return_code([sys.executable, 'du2.py', 'valid_input.geojson', 'test_output.geojson', '-mp', '0'])
    assert returncode == 2


def test_valid_mp():
    returncode = get_return_code([sys.executable, 'du2.py', 'valid_input.geojson', 'test_output.geojson', '-mp', '1'])
    assert returncode == 0


def test_valid_output_geojson():
    output_filename = 'test_valid_output.geojson'

    with open(output_filename, encoding='utf-8') as output_geojson:
        output_json = geojson.load(output_geojson)

    for key in ('type', 'features'):
        assert key in output_json.keys()


def test_quadtree():
    with open('valid_input.geojson', encoding='utf-8') as input_geojson:
        input_json = geojson.load(input_geojson)

    input_features = input_json.pop('features')

    output_json = {'features': []}

    min_x, min_y, max_x, max_y = du2.calculate_bbox(input_features)

    max_points = 50
    du2.quadtree(input_features, output_json, max_points, min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

    cluster_id_dict = {}
    for feature in output_json['features']:
        cluster_id = feature['properties']['cluster_id']
        if cluster_id not in cluster_id_dict:
            cluster_id_dict[cluster_id] = 0
        cluster_id_dict[cluster_id] += 1

    for cluster_id, amount in cluster_id_dict.items():
        assert amount < max_points, f'amount of point for cluster_id "{cluster_id}" >= {max_points}'
