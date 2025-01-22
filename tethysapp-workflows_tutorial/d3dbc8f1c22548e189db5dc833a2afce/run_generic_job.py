#!/opt/tethys-python

import json
from pprint import pprint
from shapely.geometry import Point, Polygon

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

    boundary_points = params_json['Boundary Input Step']['parameters']['geometry']['features'][0]['geometry']['coordinates'][0]
    boundary_polygon = Polygon(boundary_points)
    print(f"\n\n\nBoundary Points: {boundary_points}\n\n\n")

    # Find the point id and original point coordinates from the Point In Boundary Step
    features = params_json['Point In Boundary Step']['parameters']['geometry']['features']
    for feature in features:
        if feature['properties']['point_name'] == point_name:
            print(f"\n\n\nFeature: {feature}\n\n\n")
            point_id = feature['properties']['id']
            original_point_coordinates = feature['geometry']['coordinates']

    # Get the transformations for the point from the Spatial Dataset Step
    transformations = params_json['Spatial Dataset Step']['parameters']['datasets'][point_id]
    print("Transformations: ", transformations)

    print(f'Running job for point: {point_name}')
    x = [original_point_coordinates[0]]
    y = [original_point_coordinates[1]]

    # Apply the transformations to the point and check if each new point is within the boundary
    for index in range(len(transformations['X'])):
        new_coords = [original_point_coordinates[0] + float(transformations['X'][index]), original_point_coordinates[1] + float(transformations['Y'][index])]
        if boundary_polygon.contains(Point(new_coords)):
            x.append(new_coords[0])
            y.append(new_coords[1])

    # Create the series data
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
