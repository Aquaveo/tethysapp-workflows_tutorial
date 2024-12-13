#!/opt/tethys-python

import json
import math
from pprint import pprint

import pandas as pd

from tethysext.workflows.services.workflows.decorators import workflow_step_job


increasing_data = {"X": [0, 2, 4, 6, 8, 9, 10, 13, 15, 16, 17, 21, 22, 25, 26, 28, 30, 31],
                   "Y": [7, 11, 13, 10, 12, 8, 15, 17, 20, 16, 18, 24, 28, 25, 31, 23, 27, 35]}

decreasing_data = {"X": [1, 2, 4, 6, 8, 9, 10, 12, 17, 19, 20, 24, 26, 27, 28, 31, 32, 35],
                     "Y": [35, 27, 23, 31, 25, 28, 24, 18, 16, 20, 17, 15, 8, 12, 10, 13, 11, 7]}

random_data = {"X": [1, 3, 5, 6, 7, 8, 9, 11, 15, 18, 22, 23, 24, 27, 29, 34, 36, 38],
               "Y": [4, 25, 16, 31, 12, 17, 30, 11, 20, 15, 10, 8, 32, 24, 33, 22, 18, 29]}

dataset_choices = {"Increasing Data": increasing_data, "Decreasing Data": decreasing_data, "Random Data": random_data}

def form_point_feature(x, y, point_name):
    """Generate a GeoJSON feature for a point."""
    return {
        "type": "Feature",
        "properties": {
            "name": point_name,
        },
        "geometry": {
            "type": "Point",
            "coordinates": [x, y]
        }
    }

def form_connecting_line_feature(start_point, end_point, first_point_name, second_point_name):
    """Generate a GeoJSON feature for a connecting line between two points."""
    return {
        "type": "Feature",
        "properties": {
            "name": f"Connecting Line for {first_point_name} and {second_point_name}",
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [start_point[0], start_point[1]],
                [end_point[0], end_point[1]]
            ]
        }
    }

@workflow_step_job
def main(
    db_session, workflow, step, gs_private_url, gs_public_url,
    workflow_class, params_json, params_file, cmd_args, extra_args
):
    
    print("Params JSON: ", params_json)

    # Extract extra args
    input_files = extra_args[0].split(',')
    print(f'Input Files: {input_files}')

    # Get series data from input files
    series = {}
    for series_file in input_files:
        # Store the series data from each of the json files
        with open(series_file) as f:
            s = json.loads(f.read())
        series[s['name']] = s

    for s_name, s in series.items():
        print(s_name)
        print(s)

        geojson_features = []
        # Variable to use for connecting lines
        previous_point = None
        new_point_name = "Original Point"
        counter = 2
        for x, y in zip(s['x'], s['y']):
            # Create point feature
            geojson_features.append(form_point_feature(x, y, new_point_name))
            
            # If this is not the first point, create a connecting line to the previous point
            if previous_point:
                geojson_features.append(form_connecting_line_feature(previous_point, [x, y], previous_point_name, new_point_name))

            previous_point_name = new_point_name
            new_point_name = f"Point {counter}"
            counter += 1
            
            previous_point = [x, y]
            
        geojson = {
            "type": "FeatureCollection",
            "features": geojson_features
        }

        # Create Layer on Result Map with the new points and lines
        print('Create result map layers...')
        map_result = step.result.get_result_by_codename('map_result')
        map_result.add_geojson_layer(
            geojson=geojson,
            layer_id=f'{s_name}_point_locations',
            layer_name=f'{s_name}_point_locations',
            layer_title=f'{s_name} Point Locations',
            layer_variable=f'{s_name}_point_locations',
            popup_title=s_name,
            selectable=True,
            label_options={'label_property': 'point_name'},
        )
    
    # Add series to table result
    print('Create series tables...')
    table_result = step.result.get_result_by_codename('table_result')
    table_result.reset()

    # Retrieve the table data from the Table Input Step
    table_data = params_json['Table Input Step']['parameters']['dataset']

    # Multiply the values by 2
    table_data['X'] = [x * 2 for x in table_data['X']]
    table_data['Y'] = [y * 2 for y in table_data['Y']]
    
    df = pd.DataFrame({'x': table_data['X'], 'y': table_data['Y']})
    table_result.add_pandas_dataframe("Table Data", df, show_export_button=True)

    # Add series to plot result
    dataset_choice = params_json['Dataset Input Step']['parameters']['form-values']['datasets'][0]
    data = dataset_choices[dataset_choice]
    
    print('Adding series to plot...')
    plot_result = step.result.get_result_by_codename('plot_result')
    plot_result.reset()
    plot_result.add_series(dataset_choice, [data['X'], data['Y']])
