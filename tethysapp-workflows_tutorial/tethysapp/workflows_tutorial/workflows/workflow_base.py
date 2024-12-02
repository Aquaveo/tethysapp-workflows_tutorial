from tethysext.workflows.models import TethysWorkflow


class WorkflowBase(TethysWorkflow):
    """
    Base class for workflows.
    """
    __abstract__ = True

    def get_url_name(self):
        from ..app import App as app
        return f'{app().url_namespace}:{self.TYPE}_workflow'