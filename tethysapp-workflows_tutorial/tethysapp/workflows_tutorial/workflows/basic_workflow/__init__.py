from ..workflow_base import WorkflowBase
from tethysext.workflows.steps import SpatialInputStep, TableInputStep, JobStep, ResultsStep
from .attributes import PointAttributes
from .jobs import build_jobs_callback
from .results import build_results_tabs

class BasicWorkflow(WorkflowBase):
    """
    Run a basic workflow.
    """
    TYPE = 'basic_workflow'
    DISPLAY_TYPE_SINGULAR = 'Basic Workflow'
    DISPLAY_TYPE_PLURAL = 'Basic Workflows'

    __mapper_args__ = {'polymorphic_identity': TYPE}

    @classmethod
    def new(cls, app, name, creator_id, creator_name, geoserver_name, map_manager, spatial_manager, **kwargs):
        """
        Factor class method that creates a new workflow with steps
        Args:
            app(TethysApp): The TethysApp hosting this workflow (e.g. Agwa).
            name(str): Name for this instance of the workflow.
            resource_id(str|uuid): ID of the resource.
            creator_id(str): Username of the user that created the workflow.
            geoserver_name(str): Name of the SpatialDatasetServiceSetting pointing at the GeoServer to use for steps with MapViews.
            map_manager(MapManagerBase): The MapManager to use for the steps with MapViews.
            spatial_manager(SpatialManager): The SpatialManager to use for the steps with MapViews.
            kwargs: additional arguments to use when configuring workflows.

        Returns:
            Workflow: the new workflow.
        """
        # Create new workflow instance
        workflow = cls(name=name, creator_id=creator_id, creator_name=creator_name)

        generic_spatial_input_step = SpatialInputStep(
            name='Generic Spatial Input Step',
            order=10,
            help="Use the point tool to define a location. [CHANGE THIS HELP TEXT]",
            options={
                'shapes': ['points'],
                'singular_name': 'Point',
                'plural_name': 'Points',
                'allow_shapefile': True,
                'allow_drawing': True,
                'attributes': PointAttributes()
            },
            geoserver_name=geoserver_name,
            map_manager=map_manager,
            spatial_manager=spatial_manager,
        )
        workflow.steps.append(generic_spatial_input_step)

        generic_table_input_step = TableInputStep(
            name='Generic Table Input Step',
            order=20,
            help="Enter the following parameters for each dataset.",
            options={
                'dataset_title': 'Table Input',
                'read_only_columns': ['Soil Texture'],
            }
        )
        workflow.steps.append(generic_table_input_step)


        generic_execute_step = JobStep(
                name='Generic Run Step',
                order=30,
                help='Review input and then press the Run button to run the workflow. '
                'Press Next after the execution completes to continue. [CHANGE THIS HELP TEXT]',
                options={
                    'scheduler': app.SCHEDULER_NAME,
                    'jobs': build_jobs_callback,
                    'working_message': 'Please wait for the execution to finish running before proceeding.',
                    'error_message': 'An error occurred with the run. Please adjust your input and try running again.',
                    'pending_message': 'Please run the workflow to continue.'
                },
                geoserver_name=geoserver_name,
                map_manager=map_manager,
                spatial_manager=spatial_manager,
            )
        workflow.steps.append(generic_execute_step)

        generic_result_step = ResultsStep(
            name='Generic Review Results',
            order=40,
            help='Review the results from the run step. [CHANGE THIS HELP TEXT]',
            options={},
        )
        generic_execute_step.result = generic_result_step  # set as result step for condor step
        step = build_results_tabs(geoserver_name, map_manager, spatial_manager)
        generic_result_step.results.extend(step)
        workflow.steps.append(generic_result_step)
        
        return workflow