import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Introduction: loading, slicing, dicing model output

    This tutorial is designed to help new users get to grips with the COSIMA Cookbook.

    The COSIMA Cookbook is collection of recipes for analysing ocean and sea ice model output, using a common method of loading the output.

    The tutorial requires:
     * Access to the ACCESS-NRI Intake Catalog (through project `xp65`).
     * Ability to open a Jupyter notebook on the NCI's Gadi HPC (e.g., via the ARE).
     * Access an appropriate set of `conda` packages to load the appropriate python libraries (such as through the `xp65` conda packages).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Before starting,** load in some standard libraries that you are likely to need:
    """)
    return


@app.cell
def _():
    # To start a dask cluster
    from dask.distributed import Client
    # For plotting
    import matplotlib.pyplot as plt
    # For oceanographic colormaps
    import cmocean as cm
    # For numerical operations
    import numpy as np

    return Client, cm, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start a cluster with multiple cores
    """)
    return


@app.cell
def _(Client):
    client = Client(threads_per_worker=1)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In addition, you **always** need to load the `intake` module.
    This provides functions that we use to load data via the ACCESS-NRI Intake Catalog:
    """)
    return


@app.cell
def _():
    import intake

    return (intake,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Cookbook Philosophy
    The COSIMA Cookbook is a framework for analysing ocean-sea ice model output.
    It is designed to:

    * Provide examples of commonly used analyses;
    * Write efficient, well-documented, openly accessible code;
    * Encourage community contributions to the code;
    * Ensure analyses results are reproducible;
    * Carry out analysis using directly the model output, minimising creation of intermediate files;
    * Find methods to deal with the memory limitations when analysing high-resolution model output.

    ### 1.1 A database of experiments
    The COSIMA Cookbook relies on a database of experiments (let's call it a datastore) in order to load model output. This datastore effectively holds metadata for each experiment, as well as variable names, data ranges and so on.

    **NCI Projects**: Access to COSIMA ocean-sea ice model output requires that you are a member of NCI projects `xp65`, `ik11`, `cj50`, and `ol01`.

    With that sorted out, there are three different ways for you to access the datastore:

    1. Use the default ACCESS-NRI catalog, which is periodically refreshed automatically. This datastore includes many experiments stored in the COSIMA data directories on NCI under the projects mentioned above. The examples in this tutorial use this datastore.

    2. Use another datastore that someone has made for you.

    3. Make your own catalog, which is stored in your own path and includes only the experiments you are interested in. Please refer to the [`Make_Your_Own_Intake_Datastore`](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/02-Advanced/Make_Your_Own_Intake_Datastore.html) tutorial for instructions on how to create this datastore.

    To access the default datastore, you need to load it each time you fire up a notebook:
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.2 Inbuilt Catalog Functions

    We have constructed a few functions to help you operate the cookbook and to access the datasets.  The following functions query and display the data available in the datastore, without loading the data itself.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `catalog` lists all of the experiments and variables that are included in the datastore. The format is mostly self-explanatory, but the list is huge (and noth particularly useful):
    """)
    return


@app.cell
def _(catalog):
    catalog
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Each line in the table above references a directory full of netCDF files with model output.

    **The COSIMA cookbook philosophy is that you don't need to know about the directories in which these files are stored to be able to interrogate them or to load the data**.

    However, with thousands of experiments in the datastore, the above table isn't so easy to understand. Luckily, we can refine our search to limit the experiments we see. For example, if we already know the name of the experiment we are after, we can specify it via:
    """)
    return


@app.cell
def _(catalog):
    catalog.search(name='025deg_jra55_ryf9091_gadi')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is more useful, because it focusses just on the experiment I'm interested in -- and provides a list of all the variables available that experiment. It also gives a short description which is a nice way to explore which experiments might be available.

    However, we may notice that the list of variables in the right-most column here is too long for this format. There are other ways to get hold of a list of all of these variables, such as:
    """)
    return


@app.cell
def _(catalog):
    variables = catalog.search(name='025deg_jra55_ryf9091_gadi').unique().variable
    print(variables)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    See the [`ACCESS-NRI_Intake_Catalog`](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/01-Basics/02-ACCESS-NRI_Intake_Catalog.html) for additional methods.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.3 Loading data from an experiment

    Python has many ways of reading data from a netCDF file... so we thought we would add another way. This is done via the `.to_dask()` function, which is the most commonly used function in the Cookbook. This function takes the output from a `catalog.search()` query to find a specific variable, and loads the files you need to create that variable.

    Let's take now a little while to get to know how to load output. Most times, we need just three arguments: `experiment`, `variable`, and (in most cases) the `frequency` of the variable.
    """)
    return


@app.cell
def _(catalog):
    _experiment = '025deg_jra55_ryf9091_gadi'
    variable = 'temp_global_ave'
    ds = catalog[_experiment].search(variable=variable).to_dask(xarray_open_kwargs=dict(use_cftime=True))
    return (ds,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The above command returns an `xarray` dataset `ds`.

    **Note 1**: it is possible to load several variables at once in this fashion and thus get a dataset with many variables (`variable=[variable_1, variable_2]`)

    **Note 2**: the `xarray_open_kwargs = dict(use_cftime=True)` argument is only needed to suppress warnings for experiments which go outside the range of "normal" dates used by `np.datetime`

    It's often easier to work with an `xarray` dataarray instead of a dataset. In that case, we can extract the dataarray that corresponds to the variable of our choice via:
    """)
    return


@app.cell
def _(ds):
    ds['temp_global_ave']
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can see that this operation loaded the globally averaged potential temperature from the model output. The time axis runs from year 1900 to year 2459. For some variables (particularly 3D variables that might use a loooot of memory), we may prefer to restrict ourselves to a smaller time window:
    """)
    return


@app.cell
def _(ds):
    ds['temp_global_ave'].sel(time=slice('2000-01-01', '2050-12-31'))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.4 Exercises
    OK, this is a tutorial, so now you have to do some work. Your tasks are to:
    * Find and load sea surface height (ssh) from an experiment (perhaps choose a 1° configuration for starters).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    * Load potential temperature from an experiment (again, 1° would be quickest). Can you chunk the data differently from the default?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. How to manipulate and plot variables with xarray
    We use the python package `xarray` (which is built on `dask`, `pandas`, `matplotlib` and `numpy`) for many of our diagnostics. `xarray` has a a lot of nice features, some of which we will try to demonstrate for you.

    ### 2.1 Plotting
    `xarray`'s `.plot()` method does its best to figure out what you are trying to plot, and plotting it for you. Let's start by loading a 1-dimensional variable and plotting.
    """)
    return


@app.cell
def _(catalog):
    _experiment = '025deg_jra55_ryf9091_gadi'
    variable_1 = 'temp_global_ave'
    ds_1 = catalog[_experiment].search(variable=variable_1).to_dask(xarray_open_kwargs=dict(use_cftime=True))
    ds_1[variable_1].plot()
    return ds_1, variable_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You can see that `xarray` has used the metada in its plot, correctly labeing the x-axis which time and that the y-axis is `temp_global_ave`. You can always modify aspects of your plot if you are unhappy with the default xarray behaviour:
    """)
    return


@app.cell
def _(ds_1, plt, variable_1):
    plt.figure(figsize=(10, 5))
    ds_1[variable_1].plot()
    plt.xlabel('Year')
    plt.ylabel('Temperature (°C)')
    plt.title('Globally Averaged Temperature')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Because `xarray` knows about dimensions, it has plotting routines which can figure out what it should plot. By way of example, let's load a single time slice of `surface_temp` and see how `.plot()` handles it:
    """)
    return


@app.cell
def _(catalog):
    _experiment = '01deg_jra55v13_ryf9091'
    variable_2 = 'surface_temp'
    ds_2 = catalog[_experiment].search(variable=variable_2, frequency='1mon').to_dask()
    temp = ds_2[variable_2].isel(time=-1).load()
    temp.plot()
    return (temp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A few things you might notice here. Firstly, we didn't need to pass any `xarray_open_kwargs` in the `.to_dask()` function - because this experiment has a smaller date range (1900-2179). Second, we needed to specify the `frequency` - this is because this field is saved at both daily and monthly frequency, and they need dismabiguation. Also, even though this is an experiment at a 0.1° horizontal resolution for 280 years -- we can still load `ds`, because it's lazily loading (that is, it only loads the metadata). But before we plot, we need to select a single time level to ensure we don't run out of memory!

    Again, we can customise this plot as we see fit:
    """)
    return


@app.cell
def _(cm, np, plt, temp):
    temp_C = temp - 273.15 # convert from Kelvin to Celsius
    temp_C.plot.contourf(levels=np.arange(-2, 32, 2), cmap=cm.cm.thermal)

    plt.ylabel('latitude')
    plt.xlabel('longitude')
    plt.title('Surface Temperature')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.2 Slicing and dicing

    There are two different ways of subselecting from a DataArray: `isel` and `sel`. The first of these two is selecting by index (the `i` stands for index). This means we specify the value of the index of the array. For the latter, we can specify the _value_ of the coordinate we want to select.

    These two methods are demonstrated in the following example:
    """)
    return


@app.cell
def _(catalog):
    _experiment = '025deg_jra55_ryf9091_gadi'
    variable_3 = 'pot_rho_0'
    ds_3 = catalog[_experiment].search(variable=variable_3, frequency='1yr').to_dask(xarray_open_kwargs=dict(use_cftime=True))
    ds_3
    return ds_3, variable_3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In the above example, a 600-year dataset is loaded. You can see that potential density is a four dimensional dataset, with time, latitude, longitude and depth coordinates. The depth coordinate is called `st_ocean`.

    We will use `isel` to select the 201st year (time index of 200) and then we can plot a certain depth level, like 1000, using `.sel`. Note that we add a `method='nearest'`, because `.sel` requires the *exact* value - specifying the method allows us to select the level that is closest to 1000.
    """)
    return


@app.cell
def _(ds_3, variable_3):
    _rho = ds_3[variable_3].isel(time=200).sel(st_ocean=1000, method='nearest')
    _rho.plot(vmin=1026, vmax=1028)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In addition, both `.sel` and `.isel` methods allow us to slice a range of values:
    """)
    return


@app.cell
def _(ds_3, variable_3):
    _rho = ds_3[variable_3].isel(time=200).sel(st_ocean=1000, method='nearest').sel(xt_ocean=slice(-230, -180), yt_ocean=slice(-50, -20))
    _rho.plot(vmin=1027, vmax=1027.5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Above, we have sliced out a small region of interest for our plot.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.3 Averaging along dimensions

    We often perform operations such as averaging on dataarrays. Again, knowledge of the coordinates can be a big help here, as you can instruct the `mean()` method to operate along given coordinates. The case below takes a temporal and zonal average of potential density.

    #### IMPORTANT
    To be precise, it is actually a numerical mean (in this case in the $i$-grid direction), which (a) doesn't account for the size of grid-cells and (b) is only zonal outside the tripolar region in the Arctic, i.e., *south of 65N* in the ACCESS-OM2 models.

    Issue (a) is not a problem for this particular case because the zonal length of cells is the same everywhere. However if you want to calculate a mean in the meridional dimension, or in depth, grid sizes are variable and you will need use these sizes as weights.

    To address (b) and compute the zonal mean correctly one needs to be a bit more careful; see [`02-Easy-Recipes/True_Zonal_Mean.ipynb`](https://cosima-recipes.readthedocs.io/en/latest/02-Easy-Recipes/True_Zonal_Mean.html).
    """)
    return


@app.cell
def _(catalog, cm, plt):
    _experiment = '1deg_jra55_iaf_omip2_cycle6'
    variable_4 = 'temp'
    ds_4 = catalog[_experiment].search(variable=variable_4, frequency='1mon').to_dask(xarray_open_kwargs=dict(use_cftime=True))
    ds_4[variable_4].mean(['time', 'xt_ocean']).plot(cmap=cm.cm.thermal)
    plt.gca().invert_yaxis()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.4 Resampling

    `xarray` uses `datetime` conventions to allow for operations such as resampling in time. This resampling is simple and powerful. Here is an example of re-plotting a monthly timeseries with annual averaging:
    """)
    return


@app.cell
def _(catalog, plt):
    _experiment = '1deg_jra55_iaf_omip2_cycle6'
    variable_5 = 'temp_global_ave'
    ds_5 = catalog[_experiment].search(variable=variable_5, frequency='1mon').to_dask(xarray_open_kwargs=dict(use_cftime=True))
    ds_5[variable_5].plot(color='c', label='monthly')
    meandata = ds_5[variable_5].resample(time='YE').mean(dim='time')
    meandata.plot(color='r', label='annual average')
    plt.legend()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.5 Exercises

     * Pick an experiment and plot a map of the temperature of the upper 100m of the ocean for one year.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    * Now, take the same experiment and construct a timeseries of spatially averaged (regional or global) upper 700m temperature, resampled every 3 years.
    """)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
