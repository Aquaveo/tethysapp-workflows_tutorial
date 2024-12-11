#!/opt/tethys-python

import json
from pprint import pprint

from tethysext.workflows.services.workflows.decorators import workflow_step_job


@workflow_step_job
def main(
    db_session, workflow, step, gs_private_url, gs_public_url, workflow_class, 
    params_json, params_file, cmd_args, extra_args
):
    # Extract extra args
    point_name = extra_args[0]
    output_filename = extra_args[2]

    print("Params JSON: ", params_json)

    # Find the point in features that matches the point name
    features = params_json['Generic Spatial Input Step']['parameters']['geometry']['features']
    matching_feature = next((feature for feature in features if feature['properties']['point_name'] == point_name), None)
    
    if matching_feature:
        initial_coordinates = matching_feature['geometry']['coordinates']
    else:
        raise ValueError(f"No feature found with the name {point_name}")
    
    print(f"\n\n\nPoints here: {initial_coordinates}\n\n\n")

    table_data = params_json['Generic Table Input Step']['parameters']['dataset']
    print(f"\n\n\nTable Data: {table_data}\n\n\n")

    print(f'Running job for point: {point_name}')
    x = [initial_coordinates[0]]
    y = [initial_coordinates[1]]
    for x_change in table_data['X']:
        x.append(initial_coordinates[0] + float(x_change))
    for y_change in table_data['Y']:
        y.append(initial_coordinates[1] + float(y_change))

    series = {
        'name': point_name,
        'x': x,
        'y': y,
    }

    print('Results:')
    pprint(series, compact=True)

    # Save to file
    print('Saving File... ')
    with open(output_filename, 'w') as f:
        f.write(json.dumps(series))

    print('Saved file Successfully')