# whiteboxgui


[![image](https://img.shields.io/pypi/v/whiteboxgui.svg)](https://pypi.python.org/pypi/whiteboxgui)
[![image](https://img.shields.io/conda/vn/conda-forge/whiteboxgui.svg)](https://anaconda.org/conda-forge/whiteboxgui)
[![image](https://pepy.tech/badge/whiteboxgui)](https://pepy.tech/project/whiteboxgui)
[![image](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/giswqs/whiteboxgui/blob/master/examples/examples.ipynb)
[![image](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/giswqs/whiteboxgui/master)
[![image](https://binder.pangeo.io/badge_logo.svg)](https://binder.pangeo.io/v2/gh/giswqs/whiteboxgui/master)
[![image](https://img.shields.io/twitter/follow/giswqs?style=social)](https://twitter.com/giswqs)


**An interactive GUI for WhiteboxTools in a Jupyter-based environment**

-   GitHub repo: <https://github.com/giswqs/whiteboxgui>
-   Documentation: <https://giswqs.github.io/whiteboxgui>
-   PyPI: <https://pypi.org/project/whiteboxgui>
-   conda-forge: <https://anaconda.org/conda-forge/whiteboxgui>
-   WhiteboxTools: <https://github.com/jblindsay/whitebox-tools>
-   User Manual: <https://jblindsay.github.io/wbt_book>
-   whitebox-python: <https://github.com/giswqs/whitebox-python>
-   whiteboxR: <https://github.com/giswqs/whiteboxR>
-   whitebox-ArcGIS: <https://github.com/giswqs/WhiteboxTools-ArcGIS>
-   Free software: MIT license

## Description

The whiteboxgui Python package is a Jupyter frontend for WhiteboxTools, an advanced geospatial data analysis platform developed by Prof. John Lindsay ([webpage](https://jblindsay.github.io/ghrg/index.html); [jblindsay](https://github.com/jblindsay)) at the University of Guelph's [Geomorphometry and Hydrogeomatics Research Group](https://jblindsay.github.io/ghrg/index.html). WhiteboxTools can be used to perform common geographical information systems (GIS) analysis operations, such as cost-distance analysis, distance buffering, and raster reclassification. Remote sensing and image processing tasks include image enhancement (e.g. panchromatic sharpening, contrast adjustments), image mosaicing, numerous filtering operations, simple classification (k-means), and common image transformations. WhiteboxTools also contains advanced tooling for spatial hydrological analysis (e.g. flow-accumulation, watershed delineation, stream network analysis, sink removal), terrain analysis (e.g. common terrain indices such as slope, curvatures, wetness index, hillshading; hypsometric analysis; multi-scale topographic position analysis), and LiDAR data processing. LiDAR point clouds can be interrogated (LidarInfo, LidarHistogram), segmented, tiled and joined, analyized for outliers, interpolated to rasters (DEMs, intensity images), and ground-points can be classified or filtered. WhiteboxTools is not a cartographic or spatial data visualization package; instead it is meant to serve as an analytical backend for other data visualization software, mainly GIS. 

The WhiteboxTools currently contains **447** tools, which are each grouped based on their main function into one of the following categories: Data Tools, GIS Analysis, Hydrological Analysis, Image Analysis, LiDAR Analysis, Mathematical and Statistical Analysis, Stream Network Analysis, and Terrain Analysis. For a listing of available tools, complete with documentation and usage details, please see the [WhiteboxTools User Manual](https://jblindsay.github.io/wbt_book/available_tools/index.html).


## Installation

The whiteboxgui Python package can be installed using the following command:

```
pip install whiteboxgui
```

## Usage

The whiteboxgui provides a Graphical User Interface (GUI) for WhiteboxTools in a Jupyter-based environment, which can be invoked using the following Python script:

```
import whiteboxgui
whiteboxgui.show(verbose=True)
```
![Imgur](https://i.imgur.com/z4Pm2Mt.png)

## Demo

![tutorial](https://i.imgur.com/girs2dr.gif)

## Credits

This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.
