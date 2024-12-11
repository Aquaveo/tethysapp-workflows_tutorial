#!/opt/tethys-python

import json
import math
from pprint import pprint

import pandas as pd

from tethysext.workflows.services.workflows.decorators import workflow_step_job

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
        generic_map_result = step.result.get_result_by_codename('generic_map')
        generic_map_result.add_geojson_layer(
            geojson=geojson,
            layer_id=f'{s_name}_point_locations',
            layer_name=f'{s_name}_point_locations',
            layer_title=f'{s_name} Point Locations',
            layer_variable=f'{s_name}_point_locations',
            popup_title=s_name,
            selectable=True,
            label_options={'label_property': 'point_name'},
        )

    # Find max value on y-axis for output point plots
    max_y_value = 0
    for _, s in series.items():
        cur_y = max(s['y'])
        max_y_value = max(cur_y, max_y_value)

    max_y_value = math.floor(max_y_value * 1.1) + 1
    
    # Add series to table result
    print('Create series tables...')
    generic_table_result = step.result.get_result_by_codename('generic_table')
    generic_table_result.reset()

    for point_name, s in series.items():
        df = pd.DataFrame({'x': s['x'], 'y': s['y']})
        generic_table_result.add_pandas_dataframe(point_name, df, show_export_button=True)

    # Add series to plot
    print('Adding series to plot...')
    generic_plot_result = step.result.get_result_by_codename('generic_plot')
    generic_plot_result.reset()
    for s_name, s in series.items():
        generic_plot_result.add_series(s_name, [s['x'], s['y']])
