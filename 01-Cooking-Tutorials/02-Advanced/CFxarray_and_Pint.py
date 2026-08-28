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
    # Using `cf_xarray` and `pint` for Model Agnostic Analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Introduction

    In this Advanced tutorial, we learn how `cf_xarray` and `pint` can be used for *model-agnostic analysis*. This means writing your notebook so that it can easily be used with any CF-compliant data source.

    **Background:** COSIMA Recipes once included model-agnostic analysis in many of the example recipes to support both ACCESS-OM2/MOM5 and MOM6 analysis. However, this made some recipes difficult to read and understand because it obscured grid or variable information, which are important for users to learn. Most COSIMA Recipes now take a pedagogical approach and show an example of analysis for one model, with some additional information on how a user might modify the recipe for a different model, for example, the equivalent variable names. Users who wish to perform model-agnostic analysis may find this `cf_xarray` and `pint` tutorial helpful!

    ### What are the CF Conventions?

    From [CF Metadata conventions](https://cfconventions.org):

    > The CF metadata conventions are designed to promote the processing and sharing of files created with the NetCDF API. The conventions define metadata that provide a definitive description of what the data in each variable represents, and the spatial and temporal properties of the data. This enables users of data from different sources to decide which quantities are comparable, and facilitates building applications with powerful extraction, regridding, and display capabilities. The CF convention includes a standard name table, which defines strings that identify physical quantities.

    In most cases the model output data accessed through the ACCESS-NRI Intake Catalog complies with some version of the CF conventions; enough to be usable for model agnostic analysis.

    ### Why bother?

    Model agnostic means the same code can work for multiple models. This makes your code more usable by **you** and by others. You no longer need to have different versions of code for different models. It makes you and any one who uses your code more productive. It allows for common tasks to be abstracted into general methods that can be more easily reused, meaning less code needs to be written and maintained. This is an enormous productivity boost.

    ### How is model agnostic analysis achieved?

    This can be achieved by using packages that enable this:
    - [cf_xarray](https://cf-xarray.readthedocs.io/en/latest/index.html) for generalised coordinate naming
    - [xgcm](https://xgcm.readthedocs.io) to make grid operations generic across data
    - [pint](https://pint.readthedocs.io/) and [pint-xarray](https://pint-xarray.readthedocs.io/) for handling units easily and robustly
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Introduction
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This tutorial uses an example analysis, shows how the this might be done in a traditional, model specific, manner, and then implements the same analysis in a model agnostic way.

    This tutorial is intended to be run using the `conda/analysis3` or `conda/access-med` environment, available via the `xp65` project: https://access-nri-intake-catalog.readthedocs.io/en/latest/usage/how.html#using-the-catalog-on-the-are

    The first step is to import necessary packages.
    """)
    return


@app.cell
def _():
    import intake

    import numpy as np
    import xarray as xr
    import cf_xarray as cfxr
    import pint_xarray

    from pint import application_registry as ureg
    import cf_xarray.units
    import matplotlib.pyplot as plt
    import cmocean as cm
    import cartopy.crs as ccrs
    import cartopy.feature as cft

    return ccrs, cm, intake, plt, xr


@app.cell
def _():
    from dask.distributed import Client
    client = Client(threads_per_worker=1)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `cf_xarray` works best when `xarray` keeps attributes by default:
    """)
    return


@app.cell
def _(xr):
    xr.set_options(keep_attrs=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load the ACCESS-NRI Intake Catalog:
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Then, select one experiment from the catalog and load surface temperature data from a 0.25$^\circ$ global MOM5 model.
    """)
    return


@app.cell
def _(catalog):
    _experiment = '025deg_jra55_iaf_omip2_cycle6'
    _cat_subset = catalog[_experiment]
    _variable = 'sst'
    _var_search = _cat_subset.search(variable=_variable, frequency='1mon')
    _ds = _var_search.to_dask(xarray_open_kwargs={'decode_timedelta': False})
    SST = _ds[_variable]  # This option suppresses a warning due to an upcoming default alteration in xarray
    return (SST,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is a 3D dataset in latitude, longitude and time:
    """)
    return


@app.cell
def _(SST):
    SST
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Model specific
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First, do our analysis as it might usually be done, in a model-specific manner:

    1. Convert the temperature units from kelvin (K) to Celsius (C);
    2. Use the time coordinate name in the mean function.

    We use `pint` to ensure this is in degrees C. Note that if the data were originally in degrees Celcius, this would do nothing. This is a way of catering for any temperature units that are understood by pint in a transparent way. Note the call to quantify, which invokes pint's machinery to parse the units and allow unit conversions.
    """)
    return


@app.cell
def _(SST):
    SST.attrs['units'] = 'K'
    SST_1 = SST.pint.quantify().pint.to('C')
    SST_time_mean = SST_1.mean('time')
    SST_time_mean
    return SST_1, SST_time_mean


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, plot the result:
    """)
    return


@app.cell
def _(SST_time_mean, ccrs, cm, plt):
    plt.figure(figsize=(12, 6))
    _ax = plt.axes(projection=ccrs.Robinson())
    SST_time_mean_1 = SST_time_mean.pint.dequantify()
    SST_time_mean_1.plot(ax=_ax, x='xt_ocean', y='yt_ocean', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal)
    _ax.coastlines()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    (Note that the Arctic is not correctly respresented due to the 1D lat/lon coordinates not being correct in the tripole area. See the [Making Maps with cartopy Tutorial](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/01-Basics/03-Maps_with_Cartopy.html#fixing-the-tripole) for more information.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Model agnostic
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, do the same calculation, but in a model agnostic manner.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can use the `cf` accessor to automatically determine the name of the time dimension without knowledge of the exact model being used. `cf_xarray` checks the names of variables and coordinates, and associated metadata, to try and infer information about the data based on the CF conventions.

    To see what `cf_xarray` information is available just evaluate the accessor:
    """)
    return


@app.cell
def _(SST_1):
    SST_1.cf
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In this case it has found `X`, `Y` and `T` axes, and `longitude`, `latitude` and `time` coordinates. These are now accessible like a `dict` using the `cf` accessor. Note that this returns the actual coordinate, and many functions just want a simple string argument, which is the name of the coordinate.

    `cf_xarray` also wraps many standard xarray functions, allowing `cf` names to be used, which are [automatically converted to the name in the data](https://cf-xarray.readthedocs.io/en/latest/examples/introduction.html#feature-rewriting-arguments).

    The upshot: just use the `cf` accessor, append the required function, and use the standard CF coordinate name (in this case they are the same, `time`, but that is not guaranteed):
    """)
    return


@app.cell
def _(SST_1):
    SST_time_mean_2 = SST_1.cf.mean('time')
    SST_time_mean_2
    return (SST_time_mean_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Using the `cf_xarray`-wrapped function makes the code more legible and easier to write, i.e.
    ```python
    SST.cf.mean('time')
    ```
    compared to
    ```python
    SST.mean(SST.cf['time'].name)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `cf` accessor can be used in the same way in the plot, with the CF names for latitude and longitude used as `x` and `y` arguments:
    """)
    return


@app.cell
def _(SST_time_mean_2, ccrs, cm, plt):
    plt.figure(figsize=(12, 6))
    _ax = plt.axes(projection=ccrs.Robinson())
    SST_time_mean_3 = SST_time_mean_2.pint.dequantify()
    SST_time_mean_3.cf.plot(ax=_ax, x='longitude', y='latitude', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal)
    _ax.coastlines()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Putting this into practice
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Above a model agnostic version of some code was demonstrated, but that doesn't utilise the full power of what it is capable of. The model agnostic code can now be easily turned into a function that accepts an `xarray` `DataArray`:
    """)
    return


@app.cell
def _(ccrs, cm, plt):
    def map_mean_temp_in_degrees_celsius(da):
        da = da.pint.quantify().pint.to('C')  # Take the time mean of da and plot a global temperature field in a Robinson projection
        da_time_mean = da.cf.mean('time')  # 
        plt.figure(figsize=(12, 6))  # Input DataArray (da) should be a 3D array of latitude, longitude and time.
        _ax = plt.axes(projection=ccrs.Robinson())
        da_time_mean = da_time_mean.pint.dequantify()
        da_time_mean.cf.plot(ax=_ax, x='longitude', y='latitude', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal)
        _ax.coastlines()

    return (map_mean_temp_in_degrees_celsius,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Try this out with the SST data used above:
    """)
    return


@app.cell
def _(SST_1, map_mean_temp_in_degrees_celsius):
    map_mean_temp_in_degrees_celsius(SST_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now try on the output from a different experiment and model (MOM6):
    """)
    return


@app.cell
def _(catalog):
    _experiment = 'OM4_025.JRA_RYF'
    _variable = 'tos'
    _cat_subset = catalog[_experiment]
    _var_search = _cat_subset.search(variable=_variable, frequency='1mon')
    _ds = _var_search.to_dask(xarray_open_kwargs={'decode_timedelta': False})
    SST_mom6 = _ds[_variable]
    return (SST_mom6,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Check to see it has correctly parsed the CF information. It is not necessary to print this out, but interesting, and note it has quite different index and coordinate names
    """)
    return


@app.cell
def _(SST_mom6):
    SST_mom6.cf
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the function from above which also worked on MOM5 data with very different coordinates
    """)
    return


@app.cell
def _(SST_mom6, map_mean_temp_in_degrees_celsius):
    map_mean_temp_in_degrees_celsius(SST_mom6)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What to do when it goes wrong
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The model agnostic function worked flawlessly with two different ocean data sets, after the units were corrected in the MOM5 data. What about some ice data?

    Using the same experiment from which the first `SST` data was obtained, load the ice air temperature variable:
    """)
    return


@app.cell
def _(catalog):
    catalog.search(name=".*025deg", realm="seaIce", variable="Tair_m")
    return


@app.cell
def _(catalog):
    _experiment = '025deg_jra55_iaf_omip2_cycle6'
    _variable = 'Tair_m'
    _cat_subset = catalog[_experiment]
    _var_search = _cat_subset.search(variable=_variable, frequency='1mon')
    _ds = _var_search.to_dask(xarray_open_kwargs={'decode_timedelta': False}, xarray_combine_by_coords_kwargs=dict(compat='override', data_vars='minimal', coords='minimal'))
    ice_air_temp = _ds[_variable]
    ice_air_temp  # xarray_combine_by_coords_kwargs is required to get the  # data from this experiment loaded in a reasonable timeframe
    return (ice_air_temp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    When we try the generic routine:
    """)
    return


@app.cell
def _(ice_air_temp, map_mean_temp_in_degrees_celsius):
    map_mean_temp_in_degrees_celsius(ice_air_temp)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The error message is
    ```
    "Receive multiple variables for key 'longitude': ['TLON', 'ULON']. Expected only one. Please pass a list ['longitude'] instead to get all variables matching 'longitude'."
    ```
    This suggests that `cf_xarray` has found multiple longitude coordinates `TLON` and `ULON` and doesn't know how to resolve this automatically.

    Inspecting the `cf` information doesn't show multiple axes like it [does in the documentation](https://cf-xarray.readthedocs.io/en/latest/examples/introduction.html#what-attributes-have-been-discovered):
    """)
    return


@app.cell
def _(ice_air_temp):
    ice_air_temp.cf
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    [This is a bug](https://github.com/xarray-contrib/cf-xarray/issues/396), taking the mean alters the coordinates:
    """)
    return


@app.cell
def _(ice_air_temp):
    ice_air_temp.cf.mean('time').cf
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    So the solution is to drop the redundant velocity grid:
    """)
    return


@app.cell
def _(ice_air_temp):
    ice_air_temp_1 = ice_air_temp.drop_vars(['ULON', 'ULAT'])
    return (ice_air_temp_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now trying to plot again using the generic function and there is another error:
    """)
    return


@app.cell
def _(ice_air_temp_1, map_mean_temp_in_degrees_celsius):
    map_mean_temp_in_degrees_celsius(ice_air_temp_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This error:
    ```
    ValueError: x and y arguments to pcolormesh cannot have non-finite values or be of type numpy.ma.core.MaskedArray with masked values
    ```
    is because there are `NaN` values in the coordinate variables, as [explained in the plotting with cartopy tutorial](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/01-Basics/03-Maps_with_Cartopy.html#fixing-the-tripole).

    By following the instructions in that tutorial and the [Spatial selection with tripolar ACCESS-OM2 grid notebook](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/02-Advanced/Spatial_selection.html) the coordinates can be fixed by replacing them with coordinates from the ice grid input file. It requires some work, the dimensions must be renamed to match, and coordinates converted from radians to degrees.
    """)
    return


@app.cell
def _(ice_air_temp_1, xr):
    ice_grid = xr.open_dataset('/g/data/ik11/inputs/access-om2/input_eee21b65/cice_025deg/grid.nc').rename({'ny': 'nj', 'nx': 'ni'})
    ice_grid = ice_grid.pint.quantify()
    ice_air_temp_2 = ice_air_temp_1.assign_coords({'TLON': ice_grid.tlon.pint.to('degrees_E'), 'TLAT': ice_grid.tlat.pint.to('degrees_N')})
    ice_air_temp_2
    return (ice_air_temp_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Finally, the generic plotting routine works:
    """)
    return


@app.cell
def _(ice_air_temp_2, map_mean_temp_in_degrees_celsius):
    map_mean_temp_in_degrees_celsius(ice_air_temp_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One more step is to modify the original routine to take the vertical range as an argument, so it is more generally useful:
    """)
    return


@app.cell
def _(ccrs, cm, plt):
    def map_mean_temp_in_degrees_celsius_1(da, vmin=-2, vmax=30):
        da = da.pint.quantify().pint.to('C')
        da_time_mean = da.cf.mean('time')
        plt.figure(figsize=(12, 6))
        _ax = plt.axes(projection=ccrs.Robinson())
        da_time_mean = da_time_mean.pint.dequantify()
        da_time_mean.cf.plot(ax=_ax, x='longitude', y='latitude', transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax, extend='both', cmap=cm.cm.thermal)
        _ax.coastlines()

    return (map_mean_temp_in_degrees_celsius_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    By specifying default values for the arguments it is completely backwards compatible, we have lost no functionality, but the ice air temperature can now be plotted with a range that better suits the range of the data
    """)
    return


@app.cell
def _(ice_air_temp_2, map_mean_temp_in_degrees_celsius_1):
    map_mean_temp_in_degrees_celsius_1(ice_air_temp_2, vmin=-30)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Conclusion
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Model-specific code to take a time mean and plot the data was converted to a model agnostic function with no loss of functionality.

    The same function can be used with a wide range CF-compliant data.

    In some cases the input data will need to be modified if it is not sufficiently compliant, or non-conforming in some way (such as the ice data above with `NaN`'s in the coordinate). It is better to modify the data to be more compliant and higher quality, and use generic tools, than have multiple code versions to account for the vagaries or problems of individual datasets.

    Ideally, those improvements can be incorporated into future versions of the data at source, in post-processing, or in some utility functions for transforming a class of non-conforming data.
    """)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
