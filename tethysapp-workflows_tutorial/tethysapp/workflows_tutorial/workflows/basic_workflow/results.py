from tethysext.workflows.results import (
    SpatialWorkflowResult, DatasetWorkflowResult, PlotWorkflowResult, ReportWorkflowResult
)


def build_results_tabs(geoserver_name, map_manager, spatial_manager):
    """
    Define the tabs for the results step.

    Returns:
        list<ResourceWorkflowResult>: Results definitions.
    """
    map_result = SpatialWorkflowResult(
        name='Map',
        codename='map_result',
        description='Resulting transformations on original points displayed on a map.',
        order=10,
        options={
            'layer_group_title': 'Points',
            'layer_group_control': 'checkbox'
        },
        geoserver_name=geoserver_name,
        map_manager=map_manager,
        spatial_manager=spatial_manager
    )

    table_result = DatasetWorkflowResult(
        name='Table',
        codename='table_result',
        description='Table dataset result.',
        order=20,
        options={
            'data_table_kwargs': {
                'paging': True,
            },
            'no_dataset_message': 'No peak flows found.'
        },
    )

    plot_result = PlotWorkflowResult(
        name='Plot',
        codename='plot_result',
        description='Plot dataset result.',
        order=30,
        options={
            'renderer': 'plotly',
            'axes': [],
            'plot_type': 'lines',
            'axis_labels': ['x', 'y'],
            'line_shape': 'linear',
            'x_axis_type': 'datetime',
            'no_dataset_message': 'No dataset found.'
        },
    )

    report_result = ReportWorkflowResult(
        geoserver_name, 
        map_manager,
        spatial_manager,
        name='Report',
    )


    return [map_result, table_result, plot_result, report_result]
