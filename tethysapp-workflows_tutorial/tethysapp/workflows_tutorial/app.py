from tethys_sdk.base import TethysAppBase


class App(TethysAppBase):
    """
    Tethys app class for Workflows Tutorial.
    """
    name = 'Workflows Tutorial'
    description = 'A simple tethys applications for learning how to use the Tethys Workflows Extension'
    package = 'workflows_tutorial'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/icon.gif'
    root_url = 'workflows-tutorial'
    color = '#f39c12'
    tags = ''
    enable_feedback = False
    feedback_emails = []
