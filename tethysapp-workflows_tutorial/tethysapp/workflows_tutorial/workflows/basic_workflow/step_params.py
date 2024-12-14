import logging

import param

log = logging.getLogger(f'tethys.{__name__}')


class DatasetsParam(param.Parameterized):
    """
    Param form that defines the form in the Routing Options step
    """
    def __init__(self, *args, **kwargs):
        # Pop these to avoid warning messages.
        self._request = kwargs.pop('request', None)
        self._session = kwargs.pop('session', None)
        self._resource = kwargs.pop('resource', None)
        super().__init__(*args, **kwargs)
        self.set_data_options()

    def set_data_options(self):
        options = [
            'Increasing Data', 'Decreasing Data', 'Random Data'
        ]
        default = []
        self.param.add_parameter(
            'datasets',
            param.ListSelector(
                label='Datasets for Plotting',
                doc='Select one dataset to plot in your final results.',
                default=default,
                objects=options,
                allow_None=False
            )
        )
