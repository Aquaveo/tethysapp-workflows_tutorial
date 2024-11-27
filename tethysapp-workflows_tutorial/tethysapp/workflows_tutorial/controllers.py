from tethys_sdk.routing import controller
from tethysext.workflows.views.layouts import WorkflowLayout
from .app import App
from .map_manager import MapManager
from .spatial_manager import SpatialManager


@controller(name="home", url="home")
class WorkflowLayoutController(WorkflowLayout):
    app = App
    base_template = 'workflows_tutorial/base.html'
    
    def __init__(self):
        super().__init__(SpatialManager, MapManager, App.DATABASE_NAME)