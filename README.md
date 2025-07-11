<img src="https://github.com/COSIMA/logo/blob/master/png/logo_word.png" width="800"/>
<br/> <br/>

<a href="https://cosima-recipes.readthedocs.io/en/latest">
    <img alt="latest docs" src="https://img.shields.io/badge/docs-latest-blue.svg">
</a>

<a href="https://doi.org/10.5281/zenodo.14353852">
    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.14353852.svg" alt="DOI">
</a>

# COSIMA Cookbook

This repository is a Cookbook of Recipes 👩🏽‍🍳 👨🏻‍🍳.
A collection of cooking lessons and recipes for analysing ocean and sea ice model output produced by the [Consortium for Ocean-Sea Ice Modelling in Australia (COSIMA)](http://cosima.org.au/).

We explain: a "cooking lesson" here is a tutorial that teaches you something generic (e.g. about plotting or loading data); a "recipe" is an example of an analysis of some ocean-sea ice model output or some ocean-related observational datasets.
Both "cooking lessons" and "recipes" come in self-contained and well-documented Jupyter notebooks.
All the lessons and the recipes combined form a cookbook 📒!

Most recipes use output from the [ACCESS-OM2 model](https://doi.org/10.5194/gmd-13-401-2020), while some also use results from configurations of the [Modular Ocean Model 6 (MOM6)](https://github.com/mom-ocean/MOM6) and remote sensing observations.

To access the data used in these recipes you need an account with the Australian-based [National Computational Infrastructure (NCI)](https://nci.org.au/).

To **get started**, clone this repository in your local space on one of the NCI HPC machines so you can have access to model output. You should then be able to run these recipes (i.e., example analyses) through an [Australian Research Environment (ARE)](https://are.nci.org.au/) JupyterLab session running python or via any other way you might want to run a Jupyter notebook on an NCI HPC machine. You need to join projects _hh5_, _xp65_, _ik11_, _cj50_ and _ol01_ to run the recipes and access the data analysed.

If you plan to use an ARE session, then remember to include the projects in the _Storage_ line: `gdata/xp65+gdata/ik11+gdata/cj50+gdata/hh5+gdata/ol01` as well as any of your own project you need access to. In _Module directories_, set `/g/data/xp65/public/modules` and in _Modules_ set `conda/analysis3`. Use a _Compute Size_ of `large` or greater.

If you have never used the NCI see these [first steps instructions](https://access-hive.org.au/getting_started/) and [getting started with ARE](https://access-hive.org.au/getting_started/are/).

### Contributing

Have you made a recipe for analysing something that is not already included in this cookbook?
You are more than welcome to share it and include it in the cookbook!
Consider **contributing your recipe back to the repository**.
We are always delighted to expand our cookbook with more recipes.
If the process of contributing to the repository sounds a bit intimidating to you, rest assured that we will guide you and help you with submitting your contribution.

To make a contribution follow the steps laid out in the [beginner's guide on how to contribute](
https://cosima-recipes.readthedocs.io/en/latest/contributing.html). If they sound intimidating then don't worry!
Just raise [an issue](https://github.com/COSIMA/cosima-recipes/issues) explaining briefly what the contribution you want to make is and we'll help out with the process!

Contributors to the COSIMA Cookbook are added to the [**citable DOI**](https://github.com/COSIMA/cosima-recipes?tab=readme-ov-file#citation) entry associated with the repository.
Hence, users who put together a pull request for a new contribution, should ensure that the pull request also modifies the `.zenodo.json` file to include their affiliation details.

## Contents

### [Cooking Lessons 101 (Tutorials)](https://cosima-recipes.readthedocs.io/en/latest/cooking-lessons-101.html)

The starting point should be the [COSIMA_CookBook_Tutorial](https://cosima-recipes.readthedocs.io/en/latest/Cooking-Lessons-101-Tutorials/COSIMA_CookBook_Tutorial.html) that showcases how we can use Intake catalog to interrogate about available output and load them. The [ACCESS-NRI_Intake_Catalog](https://cosima-recipes.readthedocs.io/en/latest/Cooking-Lessons-101-Tutorials/ACCESS-NRI_Intake_Catalog.html) tutorial outlines the basic philosophy of the Intake catalog and how to transition from using the deprecated `cosima_cookbook`-way of loading variables. (If this 👉 `cosima_cookbook.getvar` means nothing to you then don't worry, it's already deprecated and you are better off not learning what that is in the first place!)

Also included here are some other tutorials, related to techniques (e.g., [Making_Maps_with_Cartopy.ipynb](https://cosima-recipes.readthedocs.io/en/latest/Cooking-Lessons-101-Tutorials/Making_Maps_with_Cartopy.html)) or tools (e.g., [Model Agnostic Analysis](https://cosima-recipes.readthedocs.io/en/latest/Cooking-Lessons-101-Tutorials/Model_Agnostic_Analysis.html)).


### [Recipes](https://cosima-recipes.readthedocs.io/en/latest/recipes.html)
The main part of this cookbook: All the recipes! These are Jupyter notebooks for either simple or not-so-simple diagnostics and analyses. All notebooks are aimed to be self-contained and  well-documented and explained.
If you can find a recipe that suits your purposes, then this is the best place to start.


### ACCESS-OM2-GMD-Paper-Figs
Jupyter notebooks to reproduce (as far as possible) the figures from the [ACCESS-OM2 model announcement paper (*GMD*, 2020)](https://doi.org/10.5194/gmd-13-401-2020). These notebooks are mostly uncommented, but they should be functional. They are intended to demonstrate methods to undertake the calculations used in the paper.

## Loading model output: use _intake_

Recipes have been transitioned to load model output to using an [_intake catalogue_](https://cosima-recipes.readthedocs.io/en/latest/Tutorials/ACCESS-NRI_Intake_Catalog.html). The **deprecated** [cosima-cookbook](https://github.com/COSIMA/cosima-cookbook) infrastructure
is no longer in use, and is not available on `xp65` environments.

## Conditions of use for ACCESS-OM2 output

We request that users of ACCESS-OM2 model [code](https://github.com/access-nri/access-om2) or output consider:
1. citing Kiss et al. (2020) ([http://doi.org/10.5194/gmd-13-401-2020](http://doi.org/10.5194/gmd-13-401-2020))
2. including an acknowledgement such as the following:

   *The authors thank the vibrant community of the Consortium for Ocean-Sea Ice Modelling in Australia (COSIMA; [http://www.cosima.org.au](http://www.cosima.org.au)) for making the ACCESS-OM2 suite of models available at [https://github.com/COSIMA/access-om2](https://github.com/access-nri/access-om2).*

3. let us know of any publications which use these models or data so we can add them to [our list](https://scholar.google.com/citations?hl=en&user=inVqu_4AAAAJ).


## Citation

If you use a recipe from the Cookbook for your research or teaching, or have based your analysis on one of the recipes, we would be grateful if you could cite:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14353852.svg)](https://doi.org/10.5281/zenodo.14353852)
