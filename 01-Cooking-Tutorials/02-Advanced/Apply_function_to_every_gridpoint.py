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
    ## Apply a function to every gridpoint

    This tutorial demonstrates best practice to vectorise functions that want to be applied across all grid points.

    When you need to compute something separately at many gridpoints, especially if it is fast at a single gridpoint, putting this computation into a for loop can be very slow. Instead, it is prefereable to vectorise a function, so that the numpy and/or dask backend can distribute the work across multiple cores.

    That is, to find the mean at each location, with an xarray dataset with dimensions `lon`, `lat`, and `time` instead of

    ```python
    out = np.zeros(N, M)
    for i in range(N):
        for j in range(M):
            out[i, j] = data.isel(lon=i, lat=j).mean()
    ```
    we write:

    ```python
    out = data.mean(dim=('time'))
    ```
    which xarray inteprets as to take the mean in the time dimension for every gridpoint.

    Some functions, such as ```scipy.stats.linregress```, do not have in-build vectorisation, but you might want to apply a function like this to every gridpoint, and for loops would be slow.

    This tutorial **provides a few examples of how to apply functions which do not natively vectorise many times to an xarray dataset, vectorised so that a dask client can speed up the calculation**. We answer here a dummy question "What is sea-surface temperature trend at each gridpoint of an ocean model, and is it significant?". Scientifically, this question mostly applies to the forcing dataset and not the ocean model, but it's as good an example as any.

    To achieve this goal, we use ```xarray.apply_ufunc```, which is very versatile, but therefore takes many arguments that can be difficult to interpret at first glance. The aim of the example below is to give something that will work on a problem similar to what COSIMA users may encounter.

    For full documentation of ```xarray.apply_ufunc``` refer to: https://docs.xarray.dev/en/stable/generated/xarray.apply_ufunc.html
    """)
    return


@app.cell
def _():
    import matplotlib.pyplot as plt
    import xarray as xr
    import numpy as np
    import scipy.stats
    import cartopy.crs as ccrs
    import intake
    catalog = intake.cat.access_nri
    return catalog, ccrs, np, plt, scipy, xr


@app.cell
def _():
    from dask.distributed import Client
    client = Client(threads_per_worker=1, memory_limit=0)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Get some data
    """)
    return


@app.cell
def _(catalog):
    experiment = '025deg_jra55_iaf_omip2_cycle6'
    sst = catalog[experiment].search(frequency="1mon", variable="sst").to_dask(
        xarray_open_kwargs={'chunks':{'time':-1}}
    )
    sst
    return (sst,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Rechunk so that there is only one chunk in the time dimension that will be used the linear regression.
    """)
    return


@app.cell
def _(sst):
    sst_1 = sst.chunk({'time': -1})
    sst_1
    return (sst_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define a function that takes the data we have and returns what we want.
    """)
    return


@app.cell
def _(np, scipy):
    def get_trend(time, timeseries):
        '''Calculate the trend through a timeseries using scipy.stats.linregress, 
        and return just the slope and the p value as an array, for the purposes of 
        demonstrating xarray.apply_ufunc

        Inputs:
            time: np.ndarray
                the times or x values of whatever the slope will go through
            timeseries: np.ndarray
                the data to calculate the slope of

        Outputs:
            stats: np.ndarray
                1st element is the trend in timeseries
                2nd element is the p value of this trend, indicating the significance
                They're lumped together into one variable, a) so .load() can be called 
                on both at once, and b) to demonstrate some of the nuance in xr.apply_ufunc
                when using it for more complicated applications
        '''

        slope, intercept, r, p, se = scipy.stats.linregress(time, timeseries)
        return np.array((slope, p)) # Combine into one array because it's easier to load in one go

    return (get_trend,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define a timeseries for the linear regression to work (because scipy doesn't like datetimes).

    **Note**: This line is specific to the function being applied - in this instance, we want to apply `scipy.stats.linregress`, and it needs a timeseries of x values so we make it one.
    """)
    return


@app.cell
def _(get_trend, np, sst_1, xr):
    years_since_start = xr.DataArray(np.arange(sst_1.time.shape[0]) / 12, dims=('time',), coords={'time': sst_1.time})
    stats = xr.apply_ufunc(get_trend, years_since_start, sst_1['sst'], input_core_dims=(('time',), ('time',)), output_core_dims=(('stat_type',),), dask_gufunc_kwargs={'output_sizes': {'stat_type': 2}}, vectorize=True, dask='parallelized')
    # Pass data through to the `xarray.apply_ufunc`
    stats  # function being used  # Argument 1 for function  # Argument 2 for function  # Dimensions the function needs for each argument  # Dimensions of each output from the function  # The new dimension will have size 2  # The function needs to only have one lat and lon at a time  # Dask is fine, but the function can't handle it so apply_ufunc needs to
    return (stats,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This last function call is roughly equivalent to

    ```python
    stats = np.zeros(2, len(sst.xt_ocean), len(sst.yt_ocean))

    for i in range(len(sst.xt_ocean)):
        for j in range(len(sst.yt_ocean)):
            slope,intercept = get_trend(years_since_start, sst.isel(xt_ocean=i, yt_ocean=j)
            stats[0, i, j] = slope
            stats[1, i, j] = intercept
    ```
    But the loading step (next cell) should be faster than this computation in a for loop
    """)
    return


@app.cell
def _(stats):
    # magic command not supported in marimo; please file an issue to add support
    # %%time 
    stats.load()

    # Put data back into some more useful variable names
    sst_trend = stats.sel(stat_type=0)
    p_value = stats.sel(stat_type=1)

    sst_trend
    return p_value, sst_trend


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot the calculated slope, stippling all regions that are significant at $p<0.05$. Before we plot we need to load the unmasked coordinates of geographic latitude and longitude and attach them to the dataset. If we don't use these cooridings the regions near the poles are distorted (see the [Making_Maps_with_Cartopy](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/01-Basics/03-Maps_with_Cartopy.html#fixing-the-tripole) tutorial).
    """)
    return


@app.cell
def _(p_value, sst_trend, xr):
    geolon_t = xr.open_dataset('/g/data/ik11/grids/ocean_grid_025.nc').geolon_t
    geolat_t = xr.open_dataset('/g/data/ik11/grids/ocean_grid_025.nc').geolat_t
    sst_trend_1 = sst_trend.assign_coords({'geolon_t': geolon_t, 'geolat_t': geolat_t})
    p_value_1 = p_value.assign_coords({'geolon_t': geolon_t, 'geolat_t': geolat_t})
    return p_value_1, sst_trend_1


@app.cell
def _(ccrs, p_value_1, plt, sst_trend_1):
    fig = plt.figure(figsize=(8, 4))
    ax = plt.axes(projection=ccrs.Robinson())
    ax.coastlines(resolution='50m')
    ax.gridlines(draw_labels=False)
    sst_trend_1.plot(ax=ax, x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), cbar_kwargs={'label': '°C/yr', 'extend': 'both'})
    plt.contourf(p_value_1.geolon_t, p_value_1.geolat_t, p_value_1, levels=(0, 0.05), colors='None', hatches=('...',), transform=ccrs.PlateCarree())
    plt.title('ACCESS-OM2-025 SST trend')
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
