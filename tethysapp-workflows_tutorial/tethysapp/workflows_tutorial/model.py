from tethysext.workflows.models.base import WorkflowsBase

def init_db(engine, first_time):
    """
    An example persistent store initializer function
    """
    # Create tables
    WorkflowsBase.metadata.create_all(engine)
