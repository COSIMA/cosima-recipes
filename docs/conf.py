# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

from pathlib import Path


# -- Project information -----------------------------------------------------

project = 'COSIMA Cookbook'
copyright = '2025, COSIMA'
author = 'COSIMA'


# -- General configuration ---------------------------------------------------

master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'nbsphinx',
    'sphinx_reredirects',
    'sphinx_gallery.load_style',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

html_static_path = ['_static']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build', 'Thumbs.db', '.DS_Store',
    '01-Cooking-Tutorials/README.rst',
    '01-Cooking-Tutorials/01-Basics/README.rst',
    '01-Cooking-Tutorials/02-Advanced/README.rst',
    'Recipes/README.rst',
    '02-Easy-Recipes/README.rst',
    '03-Advanced-Recipes/README.rst',
    '04-Regional-Specialties/README.rst',
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'default'
html_theme_options = {
    "sidebar_collapse": False,
    "sidebar_includehidden": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

nbsphinx_execute = "never"
nbsphinx_thumbnails = {
    "01-Cooking-Tutorials/01-Basics/01-Loading-Slicing-Dicing-Output": "_static/thumbnails/cookbook.png",
    "01-Cooking-Tutorials/01-Basics/02-ACCESS-NRI_Intake_Catalog": "_static/thumbnails/intake.png",
    "01-Cooking-Tutorials/02-Advanced/Make_Your_Own_Intake_Datastore": "_static/thumbnails/database.png",
    "01-Cooking-Tutorials/02-Advanced/Submitting_analysis_jobs_to_gadi": "_static/thumbnails/gadi.png",
    "01-Cooking-Tutorials/02-Advanced/Spatial_selection": "_static/thumbnails/explore.png",
    "01-Cooking-Tutorials/02-Advanced/intake_to_dask_efficiently_chunking": "_static/thumbnails/dask.png",
}

redirects = {
    "appetisers": "easy-recipes.html",
    "mains": "advanced-recipes.html",
    "local-dishes": "regional-specialties.html",
    "recipes/index": "/index.html",
    "recipes/appetisers": "/easy-recipes.html",
    "recipes/mains": "/advanced-recipes.html",
    "recipes/local-dishes": "/regional-specialties.html",
    "cooking-lessons-101": "/tutorials.html",
    "cooking-lessons-101/index": "/tutorials.html",
    "cooking-lessons-101/basics": "/cooking-tutorials/basics.html",
    "cooking-lessons-101/advanced": "/cooking-tutorials/advanced.html",
    "Cooking-Lessons-101-Tutorials": "/tutorials.html",
    "coocking-tutorials/basics": "/cooking-tutorials/basics.html",
    "coocking-tutorials/advanced": "/cooking-tutorials/advanced.html",
}

_renamed_doc_prefixes = [
    ("01-Cooking-Lessons-101", "01-Cooking-Tutorials"),
    ("02-Appetisers", "02-Easy-Recipes"),
    ("03-Mains", "03-Advanced-Recipes"),
    ("04-Local-Dishes", "04-Regional-Specialties"),
]

_docs_root = Path(__file__).resolve().parent
for old_prefix, new_prefix in _renamed_doc_prefixes:
    new_dir = _docs_root / new_prefix
    if not new_dir.exists():
        continue
    for notebook in new_dir.rglob("*.ipynb"):
        docname = notebook.relative_to(_docs_root).with_suffix("").as_posix()
        redirects[docname.replace(new_prefix, old_prefix, 1)] = f"/{docname}.html"

_historical_redirects = {
    "Cooking-Lessons-101-Tutorials/COSIMA_CookBook_Tutorial": "/01-Cooking-Tutorials/01-Basics/01-Loading-Slicing-Dicing-Output.html",
    "Cooking-Lessons-101-Tutorials/ACCESS-NRI_Intake_Catalog": "/01-Cooking-Tutorials/01-Basics/02-ACCESS-NRI_Intake_Catalog.html",
    "Cooking-Lessons-101-Tutorials/Making_Maps_with_Cartopy": "/01-Cooking-Tutorials/01-Basics/03-Maps_with_Cartopy.html",
    "Cooking-Lessons-101-Tutorials/Animations_with_xmovie": "/01-Cooking-Tutorials/02-Advanced/Animations_with_xmovie.html",
    "Cooking-Lessons-101-Tutorials/Apply_function_to_every_gridpoint": "/01-Cooking-Tutorials/02-Advanced/Apply_function_to_every_gridpoint.html",
    "Cooking-Lessons-101-Tutorials/Make_Your_Own_Intake_Datastore": "/01-Cooking-Tutorials/02-Advanced/Make_Your_Own_Intake_Datastore.html",
    "Cooking-Lessons-101-Tutorials/Model_Agnostic_Analysis": "/01-Cooking-Tutorials/02-Advanced/Model_Agnostic_Analysis.html",
    "Cooking-Lessons-101-Tutorials/Spatial_selection": "/01-Cooking-Tutorials/02-Advanced/Spatial_selection.html",
    "Cooking-Lessons-101-Tutorials/Submitting_analysis_jobs_to_gadi": "/01-Cooking-Tutorials/02-Advanced/Submitting_analysis_jobs_to_gadi.html",
    "Cooking-Lessons-101-Tutorials/intake_to_dask_efficiently_chunking": "/01-Cooking-Tutorials/02-Advanced/intake_to_dask_efficiently_chunking.html",
    "Recipes/Appetisers-Easy/Barotropic_Streamfunction": "/02-Easy-Recipes/Barotropic_Streamfunction.html",
    "Recipes/Appetisers-Easy/Compare_SSH_model_obs": "/02-Easy-Recipes/Compare_SSH_model_obs.html",
    "Recipes/Appetisers-Easy/Compare_SST_SSS_TemperatureSalinity_to_WOA13": "/02-Easy-Recipes/Compare_SST_SSS_TemperatureSalinity_to_WOA13.html",
    "Recipes/Appetisers-Easy/Hovmoller_Temperature_Depth": "/02-Easy-Recipes/Hovmoller_Temperature_Depth.html",
    "Recipes/Appetisers-Easy/True_Zonal_Mean": "/02-Easy-Recipes/True_Zonal_Mean.html",
    "Recipes/Appetisers-Easy/Overturning_Circulation": "/03-Advanced-Recipes/Overturning_Circulation.html",
    "Recipes/Appetisers-Easy/Relative_Vorticity": "/03-Advanced-Recipes/Relative_Vorticity.html",
    "Recipes/Mains-Advanced/Extract_Variables_at_Ocean_Bottom": "/02-Easy-Recipes/Extract_Variables_at_Ocean_Bottom.html",
    "Recipes/Mains-Advanced/Sea_Ice_Coordinates": "/02-Easy-Recipes/Sea_Ice_Coordinates.html",
    "Recipes/Mains-Advanced/Along-slope-velocities": "/03-Advanced-Recipes/Along-slope-velocities.html",
    "Recipes/Mains-Advanced/Along_Isobath_Average": "/03-Advanced-Recipes/Along_Isobath_Average.html",
    "Recipes/Mains-Advanced/Cross-contour_transport": "/03-Advanced-Recipes/Cross-contour_transport.html",
    "Recipes/Mains-Advanced/Cross-slope_section": "/03-Advanced-Recipes/Cross-slope_section.html",
    "Recipes/Mains-Advanced/Eddy-Mean_Kinetic_Energy_Decomposition": "/03-Advanced-Recipes/Eddy-Mean_Kinetic_Energy_Decomposition.html",
    "Recipes/Mains-Advanced/Geostrophic_Velocities_from_Sea_Level": "/03-Advanced-Recipes/Geostrophic_Velocities_from_Sea_Level.html",
    "Recipes/Mains-Advanced/Horizontal_Regridding": "/03-Advanced-Recipes/Horizontal_Regridding.html",
    "Recipes/Mains-Advanced/Meridional_heat_transport": "/03-Advanced-Recipes/Meridional_heat_transport.html",
    "Recipes/Mains-Advanced/Nearest_Neighbour_Distance": "/03-Advanced-Recipes/Nearest_Neighbour_Distance.html",
    "Recipes/Mains-Advanced/Neutral_density": "/03-Advanced-Recipes/Neutral_density.html",
    "Recipes/Mains-Advanced/Particle_tracking_with_Parcels": "/03-Advanced-Recipes/Particle_tracking_with_Parcels.html",
    "Recipes/Mains-Advanced/Sea_Ice_Area_Concentration_Volume_with_Obs": "/03-Advanced-Recipes/Sea_Ice_Area_Concentration_Volume_with_Obs.html",
    "Recipes/Mains-Advanced/Sea_Ice_Seasonality_Statistics": "/03-Advanced-Recipes/Sea_Ice_Seasonality_Statistics.html",
    "Recipes/Mains-Advanced/Surface_Water_Mass_Transformation": "/03-Advanced-Recipes/Surface_Water_Mass_Transformation.html",
    "Recipes/Mains-Advanced/Temperature_Salinity_Diagram": "/03-Advanced-Recipes/Temperature_Salinity_Diagram.html",
    "Recipes/Mains-Advanced/Transformation_from_Depth_to_Potential_Density": "/03-Advanced-Recipes/Transformation_from_Depth_to_Potential_Density.html",
    "Recipes/Local-Dishes-regional/regional-mom6-forced-by-access-om2": "/04-Regional-Specialties/regional-mom6-forced-by-access-om2.html",
}

redirects.update(_historical_redirects)
from pathlib import Path
