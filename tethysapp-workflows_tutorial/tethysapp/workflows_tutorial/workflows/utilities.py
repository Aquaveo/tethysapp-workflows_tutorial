import os
from datetime import datetime

import osgeo
from pyproj import datadir
import pytz
import timezonefinder


def get_gmt_offset(lat, long):
    """Gets the GMT offset for a given latitude and longitude. 

    Args:
        lat (float): Lattitude.
        long (float): Longitude

    Returns:
        gmt (float): The GMT offset in hours.
    """
    tf = timezonefinder.TimezoneFinder()
    timezone_str = tf.certain_timezone_at(lat=lat, lng=long)
    timezone = pytz.timezone(timezone_str)
    dt = datetime.now(timezone)
    return dt.utcoffset().total_seconds() / 3600


def safe_str(s):
    s_safe = "".join([c for c in s if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    s_safe = s_safe.replace(' ', '_')
    return s_safe


def get_condor_fdb_root(debug=False):
    """This function should only be called in an app-available environment (don't call in job scripts)."""
    # Use CONDOR_FDB_ROOT_DIR if set, otherwise use FDB_ROOT_DIR
    dir = os.environ.get('CONDOR_FDB_ROOT_DIR', os.environ.get('FDB_ROOT_DIR', None))
    if not dir:
        raise RuntimeError('CONDOR_FDB_ROOT_DIR and FDB_ROOT_DIR environment variables not set.')
    return dir


def get_condor_proj_dir(debug=False):
    """This function should only be called in an app-available environment (don't call in job scripts)."""
    CONTAINER_PROJ_DIR = '/var/lib/condor/micromamba/envs/tethys/share/proj'

    # If in debug mode, use the local proj lib as fallback, otherwise use the container proj as fallback
    if debug:
        fallback = datadir.get_data_dir()
    else:
        fallback = CONTAINER_PROJ_DIR

    dir = os.environ.get('CONDOR_PROJ_LIB', fallback)
    return {'PROJ_DATA': dir, 'PROJ_DEBUG': '3'}


def get_gdal_data_dirs(debug=False):
    """This function should only be called in an app-available environment (don't call in job scripts)."""
    CONTAINER_CONDA_PREFIX = '/var/lib/condor/micromamba/envs/tethys'
    CONTAINER_GDAL_DIR = 'share/gdal'
    CONTAINER_GDAL_PLUGINS = 'lib/python3.1/site-packages/osgeo/gdalplugins'

    if debug:
        gdal_path = os.path.dirname(osgeo.__file__)
        conda_prefix = os.environ.get('CONDA_PREFIX')
        gdal_driver_path = os.path.join(gdal_path, 'gdalplugins')
        gdal_data_path = os.path.join(conda_prefix, 'share', 'gdal')
    else:
        conda_prefix = '/var/lib/condor/micromamba/envs/tethys'
        gdal_data_path = os.path.join(CONTAINER_CONDA_PREFIX, CONTAINER_GDAL_DIR)
        gdal_driver_path = os.path.join(CONTAINER_CONDA_PREFIX, CONTAINER_GDAL_PLUGINS)

    gdal_data_path = os.environ.get('CONDOR_GDAL_DATA', gdal_data_path)
    gdal_driver_path = os.environ.get('CONDOR_GDAL_DRIVER_PATH', gdal_driver_path)

    return {'GDAL_DATA': gdal_data_path, 'GDAL_DRIVER_PATH': gdal_driver_path}


def get_geoserver_ports(debug=False):
    return os.environ.get('GEOSERVER_CLUSTER_PORTS')


def get_condor_env():
    """Build the condor environment variables string. This function should only be called in an app-available environment (don't call in job scripts)."""  # noqa: E501
    from django.conf import settings
    debug = settings.DEBUG
    job_env = {
        'FDB_ROOT_DIR': get_condor_fdb_root(debug),
        'GEOSERVER_CLUSTER_PORTS': get_geoserver_ports(debug),
    }
    job_env.update(get_gdal_data_dirs(debug))
    job_env.update(get_condor_proj_dir(debug))
    job_env_str = ';'.join([f'{k}={v}' for k, v in job_env.items()])
    return job_env_str
