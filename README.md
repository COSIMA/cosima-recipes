<img src="https://github.com/COSIMA/logo/blob/master/png/logo_word.png" width="800"/>
<br/> <br/>

<a href="https://cosima-recipes.readthedocs.io/en/latest">
    <img alt="latest docs" src="https://img.shields.io/badge/docs-latest-blue.svg">
</a>

# cosima-recipes

This repository consists a Cookbook of Recipes 👩🏽‍🍳👨🏻‍🍳.

We explain: a "recipe" here is an example of a model output (or observational dataset) analysis that we can perform.
Each "recipe" consists of a self-contained, and self-documented Jupyter notebook.
All the recipes combined form a cookbook 📒!

To **Get Started**, clone this repository locally, probably best in your local space on one of the NCI HPC machines so you can have access to model output. The repository includes a bunch of recipes (=examples) with which you can begin to construct your own analysis code.

### Contributing

If you made a recipe that you want to share you are more than welcome to!

Do you have a recipe for analysing something that is not already included in this cookbook?
Please consider **contributing your recipe back to the repository**.
We'd be delighted to expand our cookbook with more recipes.
We will also guide you and help you through with submitting your contribution.

To make a contribution follow the steps laid out in the [beginner's guide on how to contribute](
https://cosima-recipes.readthedocs.io/en/latest/contributing.html). If they sound intimidating then don't worry!
Just raise [an issue](https://github.com/COSIMA/cosima-recipes/issues) explaining briefly what the contribution you want to make is and we'll help out with the process!

## Contents

### [Tutorials](https://cosima-recipes.readthedocs.io/en/latest/tutorials.html)

The notebook `ACCESS-NRI_Intake_Catalog.ipynb` outlines the basic philosophy of the Intake catalog, the tool with which we load model output. This is the best place to start if you are not familiar with the Intake catalog. Also included here are some other tutorials, either related to the deprecated Python package `cosima_cookbook`, which was the old tool we used to load model output with. **Note**: not to be confused with the Cookbook of recipes you are looking at!
There are some other general tutorials, e.g., `Making_Maps_with_Cartopy.ipynb`.

### [Recipes](https://cosima-recipes.readthedocs.io/en/latest/recipes.html)
The main part of this cookbook: All the recipes! These are Jupyter notebooks for either simple or not-so-simple diagnostics and analyses. All notebooks are aimed to be self-contained and  well-documented and explained.
If you can find a recipe that suits your purposes, then this is the best place to start.

### ACCESS-OM2-GMD-Paper-Figs
Jupyter notebooks to reproduce (as far as possible) the figures from the [ACCESS-OM2 model announcement paper (*GMD*, 2020)](https://doi.org/10.5194/gmd-13-401-2020). These notebooks are mostly uncommented, but they should be functional. They are intended to demonstrate methods to undertake the calculations used in the paper.
