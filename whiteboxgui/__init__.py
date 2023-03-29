"""Top-level package for whiteboxgui."""

__author__ = """Qiusheng Wu"""
__email__ = 'giswqs@gmail.com'
__version__ = '2.3.0'

import sys

from .whiteboxgui import show, update_package

if "google.colab" in sys.modules:
    from google.colab import output
    output.enable_custom_widget_manager()