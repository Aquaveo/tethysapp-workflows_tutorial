"""
********************************************************************************
* Name: tribs_spatial_manager
* Author: glarsen
* Created On: December, 2023
* Copyright: (c) Aquaveo 2023
********************************************************************************
"""
import glob
import json
import logging
import mimetypes
import os
from rasterio import shutil as rio_shutil
import re
import requests
import tempfile
import zipfile

from tethysext.workflows.services.base_spatial_manager import BaseSpatialManager

from .dataset_types import DatasetTypes

log = logging.getLogger(__name__)


class SpatialManager(BaseSpatialManager):
    """
    Managers GeoServer Layers for tRIBS Projects.
    """
    WORKSPACE = 'tribs'
    URI = 'http://portal.aquaveo.com/tribs'
    SLD_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'sld_templates')
    S_RASTER_CONT = 'raster_continuous'
    S_RASTER_DISC = 'raster_discrete'
    S_FEATURES_SHP = 'features_shapefile'
    S_FEATURES_SHP_LABELS = 'features_shapefile_labels'
    S_NDVI = 'ndvi'
    S_NAIP = 'naip'
    S_VT = 'vegetation_types'
    DATASET_TYPE_TO_STYLE = {
        DatasetTypes.RASTER_CONT_ASCII: S_RASTER_CONT,
        DatasetTypes.RASTER_CONT_GEOTIFF: S_RASTER_CONT,
        DatasetTypes.RASTER_CONT_ASCII_TIMESERIES: S_RASTER_CONT,
        DatasetTypes.RASTER_CONT_GEOTIFF_TIMESERIES: S_RASTER_CONT,
        DatasetTypes.RASTER_DISC_ASCII: S_RASTER_DISC,
        DatasetTypes.RASTER_DISC_GEOTIFF: S_RASTER_DISC,
        DatasetTypes.RASTER_DISC_ASCII_TIMESERIES: S_RASTER_DISC,
        DatasetTypes.RASTER_DISC_GEOTIFF_TIMESERIES: S_RASTER_DISC,
    }

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