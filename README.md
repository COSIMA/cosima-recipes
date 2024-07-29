<img src="https://github.com/COSIMA/logo/blob/master/png/logo_word.png" width="800"/>
<br/> <br/>

<a href="https://cosima-recipes.readthedocs.io/en/latest">
    <img alt="latest docs" src="https://img.shields.io/badge/docs-latest-blue.svg">
</a>

# cosima-recipes
A collection of example recipes and tutorials on analysing ocean and sea ice model output produced by the [Consortium for Ocean-Sea Ice Modelling in Australia (COSIMA)](http://cosima.org.au/).

Most examples use output from the [ACCESS-OM2 model](https://doi.org/10.5194/gmd-13-401-2020), while some also use results from configurations of the [Modular Ocean Model 6 (MOM6)](https://github.com/mom-ocean/MOM6) and remote sensing observations.

To access the data used in these recipes you need an account with the Australian-based [National Computational Infrastructure (NCI)](https://nci.org.au/).

To **get started** with `cosima-recipes`, clone this repository in your local space on one of the NCI HPC machines so you can have access to model output. You should then be able to run these recipes through an [Australian Research Environment (ARE)](https://are.nci.org.au/) JupyterLab session running python. You need to join projects _hh5_, _xp65_, _ik11_, _cj50_ and _ol01_ to run the recipes and acccess the data analysed.

When starting ARE, include the projects in the _Storage_ line: `gdata/xp65+gdata/ik11+gdata/cj50+gdata/hh5+gdata/oi10` as well as your own project. In _Module directories_, set `/g/data/hh5/public/modules` and in _Modules_ set `conda/analysis3`. Use a _Compute Size_ of `large` or greater.

If you have never used the NCI see these [first steps instructions](https://access-hive.org.au/getting_started/first_steps/) and [getting started with ARE](https://access-hive.org.au/getting_started/are/).

### Contributing

If you made a notebook for analysing something that is not already included in the recipes, then please consider **contributing back to the repository**.

To make a contribution follow the steps laid out in the [beginner's guide on how to contribute](
https://cosima-recipes.readthedocs.io/en/latest/contributing.html). If they sound intimidating then don't worry!
Just raise [an issue](https://github.com/COSIMA/cosima-recipes/issues) explaining briefly what the contribution you want to make is and we'll help out with the process!

## Contents

We are in the process of transitioning these recipes from using [cosima-cookbook](https://github.com/COSIMA/cosima-cookbook) infrastructure to an _intake catalogue_, so you will find recipes may use either method to access model data. If you are halfway through a project using the cosima-cookbook and looking for resources, this [tag](https://github.com/COSIMA/cosima-recipes/tree/cosima_cookbook) marks the repository before most recipes were transitioned.

### [Tutorials](https://cosima-recipes.readthedocs.io/en/latest/tutorials.html)

The notebook [ACCESS-NRI_Intake_Catalog](https://cosima-recipes.readthedocs.io/en/latest/Tutorials/ACCESS-NRI_Intake_Catalog.html) outlines the basic philosophy of the Intake catalog and how to transition from using the cosima-cookbook to the Intake catalogue. This is the best place to start if you are not familiar with the Intake catalog. Also included here are some other tutorials, related to techniques (e.g. [Making_Maps_with_Cartopy.ipynb](https://cosima-recipes.readthedocs.io/en/latest/Tutorials/Making_Maps_with_Cartopy.html)) or tools (e.g. [Model Agnostic Analysis](https://cosima-recipes.readthedocs.io/en/latest/Tutorials/Model_Agnostic_Analysis.html))

### [Examples](https://cosima-recipes.readthedocs.io/en/latest/examples.html)
Νotebooks for simple and not-so-simple diagnostics which are well-documented and explained. If you can find an example that suits your purpose, this is the best place to start.

## Conditions of use for ACCESS-OM2 data

We request that users of ACCESS-OM2 model [code](https://github.com/access-nri/access-om2) or output data:
1. consider citing Kiss et al. (2020) ([http://doi.org/10.5194/gmd-13-401-2020](http://doi.org/10.5194/gmd-13-401-2020))
2. include an acknowledgement such as the following:

   *The authors thank the Consortium for Ocean-Sea Ice Modelling in Australia (COSIMA; [http://www.cosima.org.au](http://www.cosima.org.au)) for making the ACCESS-OM2 suite of models available at [https://github.com/COSIMA/access-om2](https://github.com/access-nri/access-om2).*
3. let us know of any publications which use these models or data so we can add them to [our list](https://scholar.google.com/citations?hl=en&user=inVqu_4AAAAJ).
