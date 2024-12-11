import logging
from tethys_gizmos.gizmo_options import MapView, MVView
from tethysext.workflows.services.map_manager import MapManagerBase


log = logging.getLogger(__name__)

class MapManager(MapManagerBase):
    """
    Map manager for the workflows_tutorial app.
    """
    MAP_VIEW_VERSION = '4.6.5'
    MAX_ZOOM = 28
    MIN_ZOOM = 4
    DEFAULT_ZOOM = 13   

    def get_map_preview_url(self):
        """
        Get url for map preview image.

        Returns:
            str: preview image url.
        """
        # Default image url
        layer_preview_url = None

        try:
            extent = self.map_extent

            # Calculate preview layer height and width ratios
            if extent:
                # Calculate image dimensions
                long_dif = abs(extent[0] - extent[2])
                lat_dif = abs(extent[1] - extent[3])
                hw_ratio = float(long_dif) / float(lat_dif)
                max_dim = 300

                if hw_ratio < 1:
                    width_resolution = int(hw_ratio * max_dim)
                    height_resolution = max_dim
                else:
                    height_resolution = int(max_dim / hw_ratio)
                    width_resolution = max_dim

                wms_endpoint = self.spatial_manager.get_wms_endpoint()

                layer_preview_url = (
                    '{}?'
                    'service=WMS&'
                    'version=1.1.0&'
                    'request=GetMap&'
                    'bbox={},{},{},{}&'
                    'width={}&'
                    'height={}&'
                    'srs=EPSG:4326&'
                    'format=image%2Fpng'
                ).format(
                    wms_endpoint,
                    extent[0],
                    extent[1],
                    extent[2],
                    extent[3],
                    width_resolution,
                    height_resolution
                )
        except Exception:
            log.exception('An error occurred while trying to generate the preview image.')

        return layer_preview_url
    
    def compose_map(self, request, *args, **kwargs):
        """
        Compose the MapView object.

        Args:
            scenario_id (int): ID of the scenario.

        Returns:
            MapView, 4-list, list: The MapView, map extent, and layer groups.
        """
        # Get endpoint
        _ = self.get_wms_endpoint()

        # Get default view and extent for model
        view, model_extent = self.get_map_extent()

        map_layers = []
        layer_groups = []
        map_view = MapView(
            height='600px',
            width='100%',
            controls=['ZoomSlider', 'Rotate', 'FullScreen'],
            layers=[],
            view=MVView(
                projection='EPSG:4326',
                center=self.DEFAULT_CENTER,
                zoom=13,
                maxZoom=28,
                minZoom=4,
            ),
            basemap=[
                'ESRI',
                'OpenStreetMap',
            ],
            legend=True
        )

        boundary_layers = []
        map_view.layers.extend(map_layers)

        # model_extent = boundary_layer.legend_extent
        return map_view, model_extent, layer_groups