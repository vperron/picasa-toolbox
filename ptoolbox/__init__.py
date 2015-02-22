# -*- coding: utf-8 -*-

"""Base source file for picasa-toolbox.
Contains higher-level functions that use API, models and utils.
WARNING: try and be as functional and without side effects as possible !
"""

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())  # TODO: use a real logging config
