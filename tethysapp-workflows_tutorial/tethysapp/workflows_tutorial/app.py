from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import PersistentStoreDatabaseSetting, SpatialDatasetServiceSetting, SchedulerSetting


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

    DATABASE_NAME='workflows_tutorial_db'

    SCHEDULER_NAME='primary_condor_scheduler'
    GEOSERVER_NAME='primary_geoserver'

    def persistent_store_settings(self):
        """
        Define persistent store settings.
        """
        ps_settings = (
            PersistentStoreDatabaseSetting(
                name=self.DATABASE_NAME,
                description='database for app to use.',
                initializer='workflows_tutorial.model.init_db',
                required=True,
                spatial=True
            ),
        )

        return ps_settings
    
    def spatial_dataset_service_settings(self):
        """
        Define spatial dataset service settings.
        """
        sds_settings = (
            SpatialDatasetServiceSetting(
                name=self.GEOSERVER_NAME,
                description='GeoServer service for app to use.',
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=True,
            ),
        )

        return sds_settings
    

    def scheduler_settings(self):
        """
        Define scheduler settings
        """
        scheduler_settings = (
            SchedulerSetting(
                name=self.SCHEDULER_NAME,
                description='Scheduler for HTCondor cluster.',
                engine=SchedulerSetting.HTCONDOR,
                required=False,
            ),
        )

        return scheduler_settings

    def register_url_maps(self):
        """
        Add controllers
        """
        from tethysext.workflows.controllers.workflows.workflow_router import WorkflowRouter
        from tethysext.workflows.urls import workflows
        from .workflows import BasicWorkflow

        UrlMap = url_map_maker(self.root_url)
        url_maps = super().register_url_maps(set_index=False)

        url_maps.extend(
            workflows.urls(
                url_map_maker=UrlMap, 
                app=self,
                persistent_store_name=self.DATABASE_NAME,
                workflow_pairs=(
                    (BasicWorkflow, WorkflowRouter),
                ),
                base_template='workflows_tutorial/base.html',
            )
        )
        return url_maps    