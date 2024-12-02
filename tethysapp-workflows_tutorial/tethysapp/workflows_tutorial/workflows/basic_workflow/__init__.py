from ..workflow_base import WorkflowBase
from tethysext.workflows.steps import SpatialInputStep
from .attributes import PointAttributes

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
            geoserver_name="primary_geoserver",
            map_manager=map_manager,
            spatial_manager=spatial_manager,
        )
        workflow.steps.append(generic_spatial_input_step)


        return workflow