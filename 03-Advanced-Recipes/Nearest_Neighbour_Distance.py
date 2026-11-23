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
    # Calculate pairwise distances between a contour and grid cells

    In this notebook, we will demonstrate how to calculate the distance from every grid cell to the nearest grid cell along a contour. We will demonstrate this by computing the distance from each grid cell in a data array to the sea ice edge. We will use monthly sea ice concentration from ACCESS-OM2-01 over the Southern Ocean to perform these calculations.

    *Useful definitions*
    **Nearest neighbour**: Refers to the search of the point within a predetermined set of points that is located closest (spatially) to a given point. In order words, what grid cell along the sea ice edge is closest to a grid cell with coordinates `i`, `j`.
    **Sea ice edge**: Refers to the northernmost grid cell where sea ice concentration is $10\%$ or above.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Loading modules
    """)
    return


@app.cell
def _():
    import intake

    import xarray as xr
    import numpy as np
    import datetime as dt

    from sklearn.neighbors import BallTree
    import matplotlib.pyplot as plt

    return BallTree, dt, intake, np, xr


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Creating a session in the COSIMA cookbook
    """)
    return


@app.cell
def _():
    from dask.distributed import Client
    client = Client(threads_per_worker = 1)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Accessing ACCESS-OM2-01 data

    First we load the ACCESS-NRI default intake catalog.
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We use monthly sea ice outputs. Here, we load only two months of sea ice data.
    """)
    return


@app.cell
def _(catalog):
    cat_subset = catalog['01deg_jra55v140_iaf_cycle4']
    _ds = cat_subset.search(variable='aice_m', file_id='seaIce.1mon.d2:2.nc:5.ni:3600.nj:2700').to_dask(xarray_combine_by_coords_kwargs=dict(compat='override', data_vars='minimal', coords='minimal'), xarray_open_kwargs={'chunks': 'auto'})
    var_ice = _ds['aice_m']
    var_ice = var_ice.sel(time=slice('1978-01', '1978-03'))
    var_ice
    return (var_ice,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The sea ice outputs need some processing before we can start our calculations. You can check this [example](../02-Easy-Recipes/Sea_Ice_Coordinates.ipynb) for a guide on how to load and plot sea ice data.

    We will follow these processing steps:
    1. Correct time dimension values by subtracting 12 hours,
    2. Attach the ocean model grid so we can calculate distances.
    """)
    return


@app.cell
def _(catalog, dt, var_ice):
    var_search = catalog['01deg_jra55v140_iaf_cycle4'].search(variable='area_t')
    var_search = var_search.search(path=var_search.df['path'][0])
    _ds = var_search.to_dask(xarray_open_kwargs={'chunks': 'auto'})
    area_t = _ds['area_t']
    var_ice['time'] = var_ice.time.to_pandas() - dt.timedelta(hours=12)
    var_ice.coords['ni'] = area_t['xt_ocean'].values
    var_ice.coords['nj'] = area_t['yt_ocean'].values
    var_ice_1 = var_ice.rename({'ni': 'xt_ocean', 'nj': 'yt_ocean'})
    var_ice_1 = var_ice_1.sel(yt_ocean=slice(-80, -45))
    var_ice_1
    return (var_ice_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Finding sea ice edge
    The sea ice edge is the defined as the northernmost areas where sea ice concentration (SIC) is over $10\%$. This is a multistep process:

    1. Identify cells where $\text{SIC} >= 0.1$, classifying them with a value of 1;
    2. Calculate the cumulative sum along latitude;
    3. Apply mask to constrain to only cells with $\text{SIC} >= 0.1$;
    4. Choose the maximum for each longitude.

    We'll demonstrate this process over the first timestep of data.
    """)
    return


@app.cell
def _(var_ice_1):
    is_ice = var_ice_1.isel(time=0) >= 0.1
    cumulative_ice = is_ice.cumsum(dim='yt_ocean')
    ice_edge = (cumulative_ice == cumulative_ice.max('yt_ocean')) * is_ice
    ice_edge.plot()
    return ice_edge, is_ice


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Checking results in relation to SIC data
    """)
    return


@app.cell
def _(ice_edge, var_ice_1):
    var_ice_1.where(var_ice_1 >= 0.1).isel(time=0).plot()
    ice_edge.plot.contour(colors=['red'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Above we plotted only cells with SIC greater or equal to 0.1. The red line represents the sea ice edge we identified in the previous step. We can be satisfied that we identified the sea ice edge correctly.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Getting coordinate pairs for our entire grid
    We will use the latitude and longitude values in our data to create coordinate pairs. We only need to get this information once if we are calculating distances from the same grid.
    """)
    return


@app.cell
def _(np, var_ice_1):
    grid_x, grid_y = np.meshgrid(var_ice_1.xt_ocean.values, var_ice_1.yt_ocean.values)
    grid_coords = np.vstack([grid_y.flat, grid_x.flat]).T
    # Changing shape so there are two values per row
    grid_coords
    return (grid_coords,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Getting coordinate pairs for sea ice edge
    We will find the index for the sea ice edge so we can identify the latitude at which the sea ice edge occurs. This will be combined with all longitude values to create the coordinate pairs for the sea ice edge.

    Note that this step has to be done once for every time step as the sea ice edge changes over time.
    """)
    return


@app.cell
def _(ice_edge, np):
    # Getting the indices for cell with maximum value along yt_ocean dimension
    ice_yt = ice_edge.yt_ocean[ice_edge.argmax(dim='yt_ocean')]
    ice_coords = np.vstack([ice_yt, ice_edge.xt_ocean]).T
    ice_coords
    return (ice_coords,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Using Nearest Neighbours algorithm to calculate distance to closest sea ice edge cell

    We will build a data structure called [BallTree](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.BallTree.html#sklearn.neighbors.BallTree) for our calculations, from the points comprising the sea ice edge. This structure allows us to efficiently query the nearest point within the sea ice edge set to any arbitrary point, according to some kind of metric. Because we're on a sphere, we use the [haversine (great circle) distance](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.haversine_distances.html), which also requires that we transform coordinates from degrees to radians. `scikit-learn` also offers a [KDTree](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KDTree.html) for a similar purpose, but this doesn't support the haversine distance as a metric, so we opt for the ball tree instead.

    The advantage of using a data structure like a ball tree is that we trade off slightly more time and memory to construct the tree for more efficient querying. This makes it feasible to query the closest sea ice edge cell to every point on the grid, which may otherwise have excessive time and/or memory requirements for a brute force approach.
    """)
    return


@app.cell
def _(BallTree, ice_coords, np):
    # magic command not supported in marimo; please file an issue to add support
    # %%time

    # First we set up our Ball Tree. Coordinates must be given in radians.
    ball_tree = BallTree(np.deg2rad(ice_coords), metric='haversine')
    return (ball_tree,)


@app.cell
def _(ball_tree, grid_coords, np):
    # magic command not supported in marimo; please file an issue to add support
    # %%time

    # The nearest neighbour calculation will give two outputs: distances and indices
    # We only need the distances for now, so ignore the second output
    distances_radians, _ = ball_tree.query(np.deg2rad(grid_coords), return_distance=True)
    return (distances_radians,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Transforming distance from radians to kilometers

    Because the haversine distance operates in terms of radians only, we will need to multiply by the resulting distances by Earth's radius to get distances in radians. We will also reshape the results so it matches our original grid.
    """)
    return


@app.cell
def _(distances_radians, var_ice_1, xr):
    distances_km = distances_radians * 6371
    distances_t0 = xr.DataArray(data=distances_km.reshape(var_ice_1.yt_ocean.size, -1), dims=['yt_ocean', 'xt_ocean'], coords={'yt_ocean': var_ice_1.yt_ocean, 'xt_ocean': var_ice_1.xt_ocean})
    distances_t0
    return (distances_t0,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Turning results into data array
    We will also apply a mask to our results, so we will only keep values for cells where SIC was greater or equal to 0.1.
    """)
    return


@app.cell
def _(distances_t0, is_ice):
    distances_t0.where(is_ice).plot()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Calculating results for other time steps

    We can wrap this up into a function to calculate distances for a given timestep. This function returns the ice mask as a second value, so that we can make the plots in the same format as demonstrated so far.
    """)
    return


@app.cell
def _(BallTree, np, var_ice_1, xr):
    def ice_edge_distances(ice_ds):
        x, y = np.meshgrid(np.deg2rad(var_ice_1.xt_ocean.values), np.deg2rad(var_ice_1.yt_ocean.values))
        grid_coords = np.vstack([y.flat, x.flat]).T
        is_ice = ice_ds >= 0.1
        cumulative_ice = is_ice.cumsum(dim='yt_ocean')
        ice_edge = (cumulative_ice == cumulative_ice.max('yt_ocean')) * is_ice
        ice_yt = ice_edge.yt_ocean[ice_edge.argmax(dim='yt_ocean')]
        ice_coords = np.vstack([ice_yt, ice_edge.xt_ocean]).T
        ball_tree = BallTree(np.deg2rad(ice_coords), metric='haversine')
        distances_radians, _ = ball_tree.query(grid_coords, return_distance=True)
        distances_km = distances_radians * 6371
        distances = xr.DataArray(data=distances_km.reshape(ice_ds.yt_ocean.size, -1), dims=['yt_ocean', 'xt_ocean'], coords={'yt_ocean': ice_ds.yt_ocean, 'xt_ocean': ice_ds.xt_ocean}, name='ice_edge_distance')
        return (distances, is_ice)

    return (ice_edge_distances,)


@app.cell
def _(ice_edge_distances, var_ice_1):
    distances_t1, mask = ice_edge_distances(var_ice_1.isel(time=1))
    distances_t1.where(mask).plot()
    return distances_t1, mask


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Stacking results into one data array
    """)
    return


@app.cell
def _(distances_t0, distances_t1, is_ice, mask, xr):
    dist_ice = xr.concat([distances_t0.where(is_ice), distances_t1.where(mask)], dim='time')
    dist_ice
    return (dist_ice,)


@app.cell
def _(dist_ice):
    dist_ice.plot(col='time')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We are done! We should be able to follow the same workflow to calculate distances to any line/point of your interest.
    """)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
