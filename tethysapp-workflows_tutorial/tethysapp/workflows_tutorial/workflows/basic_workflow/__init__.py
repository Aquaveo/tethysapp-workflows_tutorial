from ..workflow_base import WorkflowBase
from tethysext.workflows.steps import SpatialInputStep, SpatialDatasetStep, TableInputStep, FormInputStep, SetStatusStep
from .attributes import PointAttributes
import pandas as pd

class BasicWorkflow(WorkflowBase):
    """
    Run a basic workflow.
    """
    TYPE = 'basic_workflow'
    DISPLAY_TYPE_SINGULAR = 'Basic Workflow'
    DISPLAY_TYPE_PLURAL = 'Basic Workflows'

    __mapper_args__ = {'polymorphic_identity': TYPE}

    @classmethod
    def new(cls, app, name, creator_id, description, creator_name, geoserver_name, map_manager, spatial_manager, **kwargs):
        """
        Factor class method that creates a new workflow with steps
        Args:
            app(TethysApp): The TethysApp hosting this workflow (e.g. Agwa).
            name(str): Name for this instance of the workflow.
            creator_id(str): Username of the user that created the workflow.
            description(str): Description of the workflow.
            creator_name(str): Username of the creator of the workflow.
            geoserver_name(str): Name of the SpatialDatasetServiceSetting pointing at the GeoServer to use for steps with MapViews.
            map_manager(MapManagerBase): The MapManager to use for the steps with MapViews.
            spatial_manager(SpatialManager): The SpatialManager to use for the steps with MapViews.
            kwargs: additional arguments to use when configuring workflows.

        Returns:
            Workflow: the new workflow.
        """
        # Create new workflow instance
        workflow = cls(name=name, description=description, creator_id=creator_id, creator_name=creator_name)

        boundary_step = SpatialInputStep(
            name='Boundary Input Step',
            order=10,
            help="Use the Point tool to define a boundary.",
            options={
                'shapes': ['polygons', 'extents'],
                'singular_name': 'Example Boundary',
                'plural_name': 'Example Boundaries',
                'allow_shapefile': True,
                'allow_drawing': True
            },
            geoserver_name=geoserver_name,
            map_manager=map_manager,
            spatial_manager=spatial_manager,
        )

        workflow.steps.append(boundary_step)

        point_step = SpatialInputStep(
            name='Point In Boundary Step',
            order=20,
            help="Use the Point tool to define a location or locations in the boundary.",
            options={
                'shapes': ['points'],
                'singular_name': 'Location',
                'plural_name': 'Locations',
                'allow_shapefile': True,
                'allow_drawing': True,
                'attributes': PointAttributes()
            },
            geoserver_name=geoserver_name,
            map_manager=map_manager,
            spatial_manager=spatial_manager,
        )
        workflow.steps.append(point_step)
        

        spatial_dataset_step = SpatialDatasetStep(
            name='Spatial Dataset Step',
            order=30,
            help='This step will be used to select a spatial dataset.',
            options={
                 'geometry_source': {
                    SpatialDatasetStep.OPT_PARENT_STEP: {
                        'match_attr': 'name',
                        'match_value': point_step.name,
                        'parent_field': 'geometry'
                    }
                },
                'dataset_title': 'Transformations to Perform',
                'template_dataset': pd.DataFrame(columns=['X','Y']),
                'plot_columns': ('X', 'Y'),
            },
            geoserver_name=geoserver_name,
            map_manager=map_manager,
            spatial_manager=spatial_manager,
        )

        spatial_dataset_step.parents.append(point_step)
        workflow.steps.append(spatial_dataset_step)

        table_input_step = TableInputStep(
            name='Table Input Step',
            order=40,
            help="Enter the following parameters for each dataset.",
            options={
                'dataset_title': 'Table Input',
                'read_only_columns': ['Soil Texture'],
            }
        )
        workflow.steps.append(table_input_step)

        dataset_input_step = FormInputStep(
            name='Dataset Input Step',
            order=50,
            help="Select a dataset here",
            options={'param_class': 'tethysapp.workflows_tutorial.workflows.basic_workflow.step_params.DatasetsParam'},
        )
        workflow.steps.append(dataset_input_step)

        set_status_step = SetStatusStep(
            name='Set Status',
            order=60,
            help='Set the status of the workflow to ready to run.',
            options={'status': 'ready'},
        )
        workflow.steps.append(set_status_step)

        return workflow