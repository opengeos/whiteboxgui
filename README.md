# whiteboxgui

[![image](https://img.shields.io/pypi/v/whiteboxgui.svg)](https://pypi.python.org/pypi/whiteboxgui)
[![image](https://img.shields.io/conda/vn/conda-forge/whiteboxgui.svg)](https://anaconda.org/conda-forge/whiteboxgui)
[![image](https://pepy.tech/badge/whiteboxgui)](https://pepy.tech/project/whiteboxgui)
[![image](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/opengeos/whiteboxgui/blob/master/examples/examples.ipynb)
[![image](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/opengeos/whiteboxgui/master)

**An interactive GUI for WhiteboxTools in a Jupyter-based environment**

-   GitHub repo: <https://github.com/opengeos/whiteboxgui>
-   Documentation: <https://opengeos.github.io/whiteboxgui>
-   PyPI: <https://pypi.org/project/whiteboxgui>
-   conda-forge: <https://anaconda.org/conda-forge/whiteboxgui>
-   WhiteboxTools: <https://github.com/jblindsay/whitebox-tools>
-   User Manual: <https://www.whiteboxgeo.com/manual/wbt_book>
-   whitebox-python: <https://github.com/opengeos/whitebox-python>
-   whiteboxR: <https://github.com/opengeos/whiteboxR>
-   whitebox-ArcGIS: <https://github.com/opengeos/WhiteboxTools-ArcGIS>
-   Free software: MIT license

## Description

The whiteboxgui Python package is a Jupyter frontend for WhiteboxTools, an advanced geospatial data analysis platform developed by Prof. John Lindsay ([webpage](https://jblindsay.github.io/ghrg/index.html); [jblindsay](https://github.com/jblindsay)) at the University of Guelph's [Geomorphometry and Hydrogeomatics Research Group](https://jblindsay.github.io/ghrg/index.html). WhiteboxTools can be used to perform common geographical information systems (GIS) analysis operations, such as cost-distance analysis, distance buffering, and raster reclassification. Remote sensing and image processing tasks include image enhancement (e.g. panchromatic sharpening, contrast adjustments), image mosaicing, numerous filtering operations, simple classification (k-means), and common image transformations. WhiteboxTools also contains advanced tooling for spatial hydrological analysis (e.g. flow-accumulation, watershed delineation, stream network analysis, sink removal), terrain analysis (e.g. common terrain indices such as slope, curvatures, wetness index, hillshading; hypsometric analysis; multi-scale topographic position analysis), and LiDAR data processing. LiDAR point clouds can be interrogated (LidarInfo, LidarHistogram), segmented, tiled and joined, analyized for outliers, interpolated to rasters (DEMs, intensity images), and ground-points can be classified or filtered. WhiteboxTools is not a cartographic or spatial data visualization package; instead it is meant to serve as an analytical backend for other data visualization software, mainly GIS.

The WhiteboxTools currently contains **518** tools, which are each grouped based on their main function into one of the following categories: Data Tools, GIS Analysis, Hydrological Analysis, Image Analysis, LiDAR Analysis, Mathematical and Statistical Analysis, Stream Network Analysis, and Terrain Analysis. For a listing of available tools, complete with documentation and usage details, please see the [WhiteboxTools User Manual](https://www.whiteboxgeo.com/manual/wbt_book/available_tools/index.html).

## Installation

**whiteboxgui** is available on [PyPI](https://pypi.org/project/whiteboxgui). To install **whiteboxgui**, run this command in your terminal:

```
pip install whiteboxgui
```

**whiteboxgui** is also available on [conda-forge](https://anaconda.org/conda-forge/whiteboxgui). If you have
[Anaconda](https://www.anaconda.com/distribution/#download-section) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your computer, you can create a conda Python environment to install whiteboxgui:

    conda create -n wbt python
    conda activate wbt
    conda install mamba -c conda-forge
    mamba install whiteboxgui -c conda-forge

## Usage

The whiteboxgui provides a Graphical User Interface (GUI) for WhiteboxTools in a Jupyter-based environment, which can be invoked using the following Python script. You can also try [![image](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/opengeos/whiteboxgui/blob/master/examples/examples.ipynb)

```
import whiteboxgui
whiteboxgui.show(tree=True)
```

![Imgur](https://i.imgur.com/z4Pm2Mt.png)

## Demo

![tutorial](https://i.imgur.com/girs2dr.gif)

## Credits

This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.
