from tethysext.workflows.models import TethysWorkflow


class BasicWorkflow(TethysWorkflow):
    """
    Run a basic workflow.
    """
    TYPE = 'basic_simulation_workflow'
    DISPLAY_TYPE_SINGULAR = 'Basic Simulation Workflow'
    DISPLAY_TYPE_PLURAL = 'Basic Simulation Workflows'
