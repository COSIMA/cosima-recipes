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


# -- Project information -----------------------------------------------------

project = 'COSIMA Recipes'
copyright = '2023, COSIMA'
author = 'COSIMA'


# -- General configuration ---------------------------------------------------

master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'nbsphinx',
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
    'DocumentedExamples/README.rst', 'Tutorials/README.rst',
    'Tutorials/Template_For_Notebooks.ipynb'
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'default'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

nbsphinx_execute = "never"
nbsphinx_thumbnails = {
    "Tutorials/Make_Your_Own_Database": "_static/thumbnails/database.png",
    "Tutorials/Submitting_analysis_jobs_to_gadi": "_static/thumbnails/gadi.png",
    "Tutorials/Using_Explorer_tools": "_static/thumbnails/explore.png",
    "Tutorials/COSIMA_CookBook_Tutorial": "_static/thumbnails/cookbook.png",
}
