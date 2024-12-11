"""
********************************************************************************
* Name: tribs_spatial_manager
* Author: glarsen
* Created On: December, 2023
* Copyright: (c) Aquaveo 2023
********************************************************************************
"""
import json
import logging
import os

from tethysext.workflows.services.base_spatial_manager import BaseSpatialManager


log = logging.getLogger(__name__)


class SpatialManager(BaseSpatialManager):
    """
    Basic Spatial Manager for the Workflows Tutorial App.
    """

    # Override parent class GEOSERVER_CLUSTER_PORTS attribute with local environment var
    try:
        GEOSERVER_CLUSTER_PORTS = json.loads(os.environ.get("GEOSERVER_CLUSTER_PORTS"))
    except (json.JSONDecodeError, TypeError):
        GEOSERVER_CLUSTER_PORTS = [8081, 8082, 8083, 8084]
    log.debug(f"GEOSERVER_CLUSTER_PORTS set to {GEOSERVER_CLUSTER_PORTS}")

    def __init__(self, geoserver_engine, reload_ports=GEOSERVER_CLUSTER_PORTS):
        """
        Constructor

        Args:
            workspace(str): The workspace to use when creating layers and styles.
            geoserver_engine(tethys_dataset_services.GeoServerEngine): Tethys geoserver engine.
        """
        super().__init__(geoserver_engine)
        if reload_ports is not None:
            # Overriding the GEOSERVER_CLUSTER_PORTS attribute above
            # is not sufficient, so we set it on the instance too
            self.GEOSERVER_CLUSTER_PORTS = reload_ports

    def get_extent_for_project(self, project=None, buffer=None):

        default_extent = [-124.67, 25.84, -66.95, 49.38]  # Default for continental USA
        if project is None:
            return default_extent

        project_extent = project.get_attribute('project_extent')
        if project_extent is None:
            corners = [(default_extent[0], default_extent[1]), (default_extent[2], default_extent[3])]
        else:
            corners = [(project_extent[0], project_extent[1]), (project_extent[2], project_extent[3])]
        # get min_x, min_y, max_x, max_y from corners
        min_x = min([corner[0] for corner in corners])
        min_y = min([corner[1] for corner in corners])
        max_x = max([corner[0] for corner in corners])
        max_y = max([corner[1] for corner in corners])

        if buffer is not None:
            x_dist = max_x - min_x
            y_dist = max_y - min_y
            x_buff = x_dist * buffer
            y_buff = y_dist * buffer

            min_x = min_x - x_buff
            min_y = min_y - y_buff
            max_x = max_x + x_buff
            max_y = max_y + y_buff

        return [min_x, min_y, max_x, max_y]