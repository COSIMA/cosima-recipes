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
    # Cross-contour transport

    <div style="padding: 15px; background-color: #fff3cd; color: #856404; border-left: 6px solid #ffc107;">
        <strong>WARNING:</strong> This notebook is currently being improved. The current method of defining the contour and creating the x and y transport masks has issues (see https://github.com/COSIMA/cosima-recipes/issues/669) and can generate contours that are not closed. Also see the Alert below. We are working on an improved notebook, please follow https://github.com/COSIMA/cosima-recipes/pull/690 if you wish to stay up to date. In the meantime, if you are computing cross-contour transports, please ensure you understand the code and check for the known issues in your contour and masks.
    </div>

    This notebook calculates the transport across an arbitrary contour. We do this by first creating the contour, such as sea surface height, and extracting the coordinates using `matplotlib`'s `Path` class. We then create some masks to indicate which direction is across the contour at each position along the contour. We then load the transport data and compute the transport, resulting in data with dimensions depth and along contour index.

    Computation times shown used conda environment `analysis3-25.05` on 28 broadwell cpus.

    **Alert:** After including the additional cases the contour number doesn't always monotonically increase along the contour. At the moment, the two indices that are set at the same time are adjacent numbers, whereas if you were following the contour you'd expect their numbers to be 2 apart with the other coordinate in between. See  https://github.com/COSIMA/cosima-recipes/issues/383.

    First, we load useful packages:
    """)
    return


@app.cell
def _():
    import pandas as pd
    import intake
    import dask
    import matplotlib.pyplot as plt
    import netCDF4 as nc
    import xarray as xr
    import numpy as np
    import cmocean

    from dask.distributed import Client

    catalog = intake.cat.access_nri
    return Client, catalog, cmocean, np, plt, xr


@app.cell
def _(Client):
    client = Client(threads_per_worker=1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Choose experiment
    """)
    return


@app.cell
def _():
    experiment = '01deg_jra55v13_ryf9091'

    start_time = '2170-01-01'
    end_time = '2170-12-31'
    time_slice = slice(start_time, end_time)
    return end_time, experiment, start_time, time_slice


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Choose a latitude range so the contour fits in the range, but there is not too much extra space. Extra space slows down the computation.
    """)
    return


@app.cell
def _():
    lat_range = slice(-82, -59)
    return (lat_range,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### We must make sure that this latitude range is so that the t-cells are always south and west of the u-cells.

    This is important because the meridional and zonal transports occur on different grids to each other. We can check this by loading the `u`-cell and `t`-cell coordinates.

    We choose this convention so that later on when we create `numpy` grids of where the contour is and in what direction the contour goes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Load quantity we want a contour of, e.g. bathymetry
    """)
    return


@app.cell
def _(catalog, experiment, lat_range):
    _cat_subset = catalog[experiment]
    _var_search = _cat_subset.search(variable=['ht', 'hu'], start_date='2170-04-01, 00:00:00')
    _darray = _var_search.to_dask()
    ht = _darray['ht'].sel(yt_ocean=lat_range)  # Load this to access the xt_ocean, yt_ocean coordinates
    hu = _darray['hu'].sel(yu_ocean=lat_range)  # Load this to access the xu_ocean, yu_ocean coordinates
    ht  # 'xt_ocean', # We could also directly search for the coordinates we're after,  # 'yt_ocean', # but it's not necessary in this instance  # 'xu_ocean', # hence, they're commented out.  # 'yu_ocean',
    return ht, hu


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Choose your desired contour value
    """)
    return


@app.cell
def _():
    contour_depth = 1000 # metres
    return (contour_depth,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot your data (always good idea `:)`)
    """)
    return


@app.cell
def _(contour_depth, ht, plt):
    _fig = plt.figure(figsize=(10, 4))
    ht.plot(extend='both', cbar_kwargs={'label': 'ocean depth [m]'})
    ht.plot.contour(levels=[contour_depth], colors='r', linestyles='-')
    plt.title('Ocean depth (m)')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Fill in land with zeros and load:
    """)
    return


@app.cell
def _(ht):
    ht_1 = ht.fillna(0).load()
    return (ht_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Contour is on t-grid (we assume ACCESS-OM2 B-grid transports)
    """)
    return


@app.cell
def _(ht_1):
    grid_sel = 't'
    x_var = ht_1['xt_ocean']
    y_var = ht_1['yt_ocean']
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Select the contour
    We need to isolate out the single contour along the slope and get rid of the contours on the little isolated sea mounts and depressions.
    """)
    return


@app.cell
def _(contour_depth, ht_1, plt):
    _fig = plt.figure(figsize=(10, 4))
    sc = plt.contour(ht_1, levels=[contour_depth])
    path_vertices = sc.get_paths()[0].vertices
    x_vertices = path_vertices[:, 0]
    y_vertices = path_vertices[:, 1]
    return x_vertices, y_vertices


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This list of path_vertices includes all of the paths in the above figure. But we want to only select the longest contour. The contours are all stacked in `x_vertices` and `y_vertices`, with the longest contour listed first. We need to find the end of the longest contour and cut `x_vertices`/`y_vertices` at that point.

    Along our desired contour, `x_vertices`/`y_vertices` should increase/decrease by max 1, so we can use the location where `diff(x_vertices) > 1` to find the end of our desired contour.

    When we call `np.diff`, we wind up with floating point numbers. To get a mask where the difference is greater than 1, we can just turn the result of `np.diff(x_vertices)` back into an array of integers using `.astype(int)` on it - so we can cleanly check if the result is greater than 1.
    """)
    return


@app.cell
def _(np, plt, x_vertices, y_vertices):
    last_contour_index = np.where(np.abs(np.diff(x_vertices).astype(int)) > 1)[0][0]
    x_contour = x_vertices[:last_contour_index + 1]
    y_contour = y_vertices[:last_contour_index + 1]
    _fig = plt.figure(figsize=(10, 4))
    # Check desired contour looks right:
    plt.scatter(x_contour, y_contour, s=5, alpha=0.5, color='tomato')
    return x_contour, y_contour


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `x_contour` and `y_contour` are not integers with this updated contour method.
    We need to convert them to integers so we can use them as indices for selecting data on the contour.
    """)
    return


@app.cell
def _(np, x_contour, y_contour):
    x_contour_1 = np.round(x_contour).astype(int)
    y_contour_1 = np.round(y_contour).astype(int)
    if np.max(np.abs(np.diff(x_contour_1))) != 1:
    # check that the difference between coords of contour never increase by more than 1:
        print('help! x_contour increases by more than 1 between coords.')
    if np.max(np.abs(np.diff(y_contour_1))) != 1:
        print('help! y_contour increases by more than 1 between coords.')
    return x_contour_1, y_contour_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Processing
    Now process these coordinates to make sure there are no double ups.

    N.B: It can be tempting to use numpy's `unique` functionality to do this sort of task - be careful, as it won't preserve order!
    """)
    return


@app.cell
def _(np, x_contour_1, y_contour_1):
    diff_x_contour = np.diff(x_contour_1)
    diff_y_contour = np.diff(y_contour_1)
    diff_ind = []
    for _ii in range(len(diff_x_contour)):
        if diff_x_contour[_ii] == 0 and diff_y_contour[_ii] == 0:
            diff_ind.append(_ii)
    return (diff_ind,)


@app.cell
def _(diff_ind, np, x_contour_1, y_contour_1):
    for _ii in range(len(diff_ind)):
        index = diff_ind[::-1][_ii]
        x_contour_2 = np.delete(x_contour_1, index)
        y_contour_2 = np.delete(y_contour_1, index)
    return x_contour_2, y_contour_2


@app.cell
def _(ht_1, np, x_contour_2, y_contour_2):
    ht_contour = np.zeros(len(x_contour_2))
    for _ii in range(len(ht_contour)):
        ht_contour[_ii] = ht_1[y_contour_2[_ii], x_contour_2[_ii]]
    return (ht_contour,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Due to the discrete grid, the values on our contour are not exactly the same. We check this makes sense -- if this plot is blank, then something has gone wrong.
    """)
    return


@app.cell
def _(contour_depth, ht_contour, plt):
    _fig = plt.figure(figsize=(10, 4))
    plt.plot(ht_contour, 'o', markersize=1)
    plt.axhline(contour_depth, color='k', linewidth=0.5)
    return


@app.cell
def _(x_contour_2):
    # Number of grid points on the contour
    num_points = len(x_contour_2)
    return (num_points,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Now we number the points along the contour
    """)
    return


@app.cell
def _(np, x_contour_2):
    # start numbering from 1 not 0:
    contour_mask_numbered = np.arange(1, len(x_contour_2) + 1)
    return (contour_mask_numbered,)


@app.cell
def _(contour_mask_numbered, ht_1, num_points, x_contour_2, xr, y_contour_2):
    contour_mask = xr.zeros_like(ht_1)
    for _ii in range(num_points):
        contour_mask[y_contour_2[_ii], x_contour_2[_ii]] = contour_mask_numbered[_ii]
    return (contour_mask,)


@app.cell
def _(cmocean, contour_mask, plt):
    contour_mask.attrs['long_name'] = 'Contour index'
    plt.figure(1, figsize=(10, 4))
    contour_mask.plot(extend='both', cmap = cmocean.cm.amp);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Create mask
    Now we create a mask below contour so that the direction of the contour can be determined
    """)
    return


@app.cell
def _(contour_mask, np):
    mask_value = -1000
    contour_mask_numbered_1 = contour_mask
    contour_masked_above = np.copy(contour_mask_numbered_1)
    contour_masked_above[-1, 0] = mask_value
    for _ii in range(len(contour_mask.xt_ocean) - 1):
        for jj in range(len(contour_mask.yt_ocean))[::-1][:-1]:
            if contour_masked_above[jj, _ii] == mask_value:
                if contour_masked_above[jj - 1, _ii] == 0:
                    contour_masked_above[jj - 1, _ii] = mask_value
                if contour_masked_above[jj, _ii + 1] == 0:
                    contour_masked_above[jj, _ii + 1] = mask_value
    for _ii in range(len(contour_mask.xt_ocean))[::-1][:-1]:
        for jj in range(len(contour_mask.yt_ocean))[::-1][:-1]:
            if contour_masked_above[jj, _ii] == mask_value:
                if contour_masked_above[jj - 1, _ii] == 0:
                    contour_masked_above[jj - 1, _ii] = mask_value
                if contour_masked_above[jj, _ii - 1] == 0:
                    contour_masked_above[jj, _ii - 1] = mask_value
    for _ii in range(len(contour_mask.xt_ocean))[::-1][:-1]:
        for jj in range(len(contour_mask.yt_ocean) - 1):
            if contour_masked_above[jj, _ii] == mask_value:
                if contour_masked_above[jj + 1, _ii] == 0:
                    contour_masked_above[jj + 1, _ii] = mask_value
                if contour_masked_above[jj, _ii - 1] == 0:
                    contour_masked_above[jj, _ii - 1] = mask_value
    for _ii in range(len(contour_mask.xt_ocean) - 1):
        for jj in range(len(contour_mask.yt_ocean) - 1):
            if contour_masked_above[jj, _ii] == mask_value:
                if contour_masked_above[jj + 1, _ii] == 0:
                    contour_masked_above[jj + 1, _ii] = mask_value
                if contour_masked_above[jj, _ii + 1] == 0:
                    contour_masked_above[jj, _ii + 1] = mask_value
    return contour_mask_numbered_1, contour_masked_above


@app.cell
def _(contour_mask, contour_masked_above, plt):
    plt.figure(1, figsize=(10, 4))

    plt.pcolormesh(contour_mask.xt_ocean, contour_mask.yt_ocean, contour_masked_above)
    plt.colorbar()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    North of the contour, values have been filled in to be -1000, and it is thus a different colour in the plot.

    #### Direction of cross-contour transport
    Now we can use the mask to determine whether the transport across the contour should be north, east, south or west (the grid is made of discrete square(ish) shaped cells). This is done by looping through the contour points and determining in which directions there are zeros (i.e. below contour) and -1000 (i.e. above contour). This means the orientation of the contour can be determined. This is saved as `mask_x_transport`, which has -1 and +1 in a 2D (x and y) array where the contour has eastward transport, and `mask_y_transport` which as -1 and +1 for coordinates with northward transport. All other positions in the array are 0. This means that multiplying the northward transport `ty_trans` by the `mask_y_transport` gives all the northward transport across the contour, and zeros everywhere else (e.g. where contour goes upwards and cross-contour transport is thus eastward).
    """)
    return


@app.cell
def _(contour_mask_numbered_1, contour_masked_above, np):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    mask_x_transport = np.zeros_like(contour_mask_numbered_1)
    mask_y_transport = np.zeros_like(contour_mask_numbered_1)
    mask_y_transport_numbered = np.zeros_like(contour_mask_numbered_1)
    mask_x_transport_numbered = np.zeros_like(contour_mask_numbered_1)
    shape = contour_masked_above.shape
    contour_masked_above_halo = np.zeros((shape[0], shape[1] + 2))
    # make halos:
    contour_masked_above_halo[:, 0] = contour_masked_above[:, -1]
    contour_masked_above_halo[:, 1:-1] = contour_masked_above
    contour_masked_above_halo[:, -1] = contour_masked_above[:, 0]
    new_number_count = 1
    for mask_loc in range(1, int(np.max(contour_mask_numbered_1)) + 1):
        index_i = np.where(contour_mask_numbered_1 == mask_loc)[1]
        index_j = np.where(contour_mask_numbered_1 == mask_loc)[0]
        if contour_masked_above[index_j + 1, index_i] == 0 and contour_masked_above[index_j - 1, index_i] != 0:
            mask_y_transport[index_j, index_i] = -1
            mask_y_transport_numbered[index_j, index_i] = new_number_count
            new_number_count = new_number_count + 1  # if point above is towards Antarctica and point below is away from Antarctica:
        elif contour_masked_above[index_j - 1, index_i] == 0 and contour_masked_above[index_j + 1, index_i] != 0:  # take transport grid point to north of t grid:
            mask_y_transport[index_j - 1, index_i] = 1
            mask_y_transport_numbered[index_j - 1, index_i] = new_number_count
            new_number_count = new_number_count + 1  # important to do 
        elif contour_masked_above[index_j - 1, index_i] == 0 and contour_masked_above[index_j + 1, index_i] == 0:
            mask_y_transport[index_j - 1, index_i] = 1
            mask_y_transport[index_j, index_i] = -1  # if point below is towards Antarctica and point above is away from Antarctica:
            mask_y_transport_numbered[index_j - 1, index_i] = new_number_count  # take transport grid point to south of t grid:
            mask_y_transport_numbered[index_j, index_i] = new_number_count + 1
            new_number_count = new_number_count + 2
        if contour_masked_above_halo[index_j, index_i + 2] == 0 and contour_masked_above_halo[index_j, index_i] != 0:
            mask_x_transport[index_j, index_i] = -1
            mask_x_transport_numbered[index_j, index_i] = new_number_count  # if point below and point above are BOTH towards Antarctica:
            new_number_count = new_number_count + 1  # take transport grid point to south of t grid:
        elif contour_masked_above_halo[index_j, index_i] == 0 and contour_masked_above_halo[index_j, index_i + 2] != 0:
            mask_x_transport[index_j, index_i - 1] = 1
            mask_x_transport_numbered[index_j, index_i - 1] = new_number_count
            new_number_count = new_number_count + 1
        elif contour_masked_above_halo[index_j, index_i] == 0 and contour_masked_above_halo[index_j, index_i + 2] == 0:
            mask_x_transport[index_j, index_i - 1] = 1
            mask_x_transport[index_j, index_i] = -1  # if point to right is towards Antarctica and point to left is away from Antarctica:
            mask_x_transport_numbered[index_j, index_i - 1] = new_number_count  # zonal indices increased by 1 due to halos
            mask_x_transport_numbered[index_j, index_i] = new_number_count + 1  # take transport grid point on right of t grid:
            new_number_count = new_number_count + 2  # if point to left is towards Antarctica and point to right is away from Antarctica:  # take transport grid point on left of t grid:  # if point to left and right BOTH toward Antarctica
    return (
        mask_x_transport,
        mask_x_transport_numbered,
        mask_y_transport,
        mask_y_transport_numbered,
    )


@app.cell
def _(cmocean, contour_mask, mask_x_transport, plt):
    # Plot the mask for the x-transport:
    plt.figure(1, figsize=(10, 4))

    plt.pcolormesh(contour_mask.xt_ocean, contour_mask.yt_ocean, mask_x_transport,
                   cmap=cmocean.cm.balance, vmin=-1.5, vmax=1.5)
    plt.colorbar();
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As can be seen, in `mask_x_transport` there is red (+1) where eastward transport crosses the contour, and blue (-1) where westward transport crosses the contour (in the net northward direction). There are zeros everywhere else.

    ### We now have the coordinates of the contours, and whether the x or y transport is needed to calculate cross-contour transport.

    We now proceed to calculate transports across the contour. Here we convert the contour masks to data arrays, so we can multiply them later. We need to ensure the lat / lon coordinates correspond to the actual data location:
    - The y masks are used for `ty_trans`, so like `vhrho` this should have dimensions (`yu_ocean`, `xt_ocean`).
    - The x masks are used for `tx_trans`, so like `uhrho` this should have dimensions (`yt_ocean`, `xu_ocean`).

    However we set the actual name to always be simply latitude/longitude irrespective of the variable to make concatenation of transports in both direction and sorting possible.
    """)
    return


@app.cell
def _(
    ht_1,
    hu,
    mask_x_transport,
    mask_x_transport_numbered,
    mask_y_transport,
    mask_y_transport_numbered,
    xr,
):
    mask_x_transport_1 = xr.DataArray(mask_x_transport, coords=[ht_1.yt_ocean, hu.xu_ocean], dims=['latitude', 'longitude'])
    mask_y_transport_1 = xr.DataArray(mask_y_transport, coords=[hu.yu_ocean, ht_1.xt_ocean], dims=['latitude', 'longitude'])
    mask_x_transport_numbered_1 = xr.DataArray(mask_x_transport_numbered, coords=[ht_1.yt_ocean, hu.xu_ocean], dims=['latitude', 'longitude'])
    mask_y_transport_numbered_1 = xr.DataArray(mask_y_transport_numbered, coords=[hu.yu_ocean, ht_1.xt_ocean], dims=['latitude', 'longitude'])
    return (
        mask_x_transport_1,
        mask_x_transport_numbered_1,
        mask_y_transport_1,
        mask_y_transport_numbered_1,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And plot just to confirm that we didn't mess up anything.
    """)
    return


@app.cell
def _(cmocean, mask_x_transport_1, plt):
    plt.figure(1, figsize=(10, 4))
    mask_x_transport_1.plot(cmap=cmocean.cm.balance, vmin=-1.5, vmax=1.5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Stack contour data into 1D
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create the contour order data-array. Note that in this procedure the x-grid counts have x-grid dimensions and the y-grid counts have y-grid dimensions, but these are implicit, the dimension  *names* are kept general across the counts, the generic latitude, longitude, so that concatening works but we dont double up with numerous counts for one lat/lon point.
    """)
    return


@app.cell
def _(mask_x_transport_numbered_1, mask_y_transport_numbered_1, np, xr):
    # stack contour data into 1d:
    mask_x_numbered_1d = mask_x_transport_numbered_1.stack(contour_index=['latitude', 'longitude'])
    mask_x_numbered_1d = mask_x_numbered_1d.where(mask_x_numbered_1d > 0, drop=True)
    mask_y_numbered_1d = mask_y_transport_numbered_1.stack(contour_index=['latitude', 'longitude'])
    mask_y_numbered_1d = mask_y_numbered_1d.where(mask_y_numbered_1d > 0, drop=True)
    contour_ordering = xr.concat((mask_x_numbered_1d, mask_y_numbered_1d), dim='contour_index')
    contour_ordering = contour_ordering.sortby(contour_ordering)
    contour_index_array = np.arange(1, len(contour_ordering) + 1)
    return (
        contour_index_array,
        contour_ordering,
        mask_x_numbered_1d,
        mask_y_numbered_1d,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Load transports `tx_trans` and `ty_trans`
    """)
    return


@app.cell
def _(catalog, end_time, experiment, lat_range, start_time, time_slice):
    _cat_subset = catalog[experiment]
    _var_search = _cat_subset.search(variable='ty_trans', frequency='1mon')  # Can get 1mon or 3mon data
    _dset = _var_search.to_dask(xarray_open_kwargs={'decode_timedelta': False})
    _darray = _dset['ty_trans']
    _darray = _darray.sel(time=slice(start_time, end_time))
    ty_trans = _darray
    ty_trans = ty_trans.sel(yu_ocean=lat_range, time=time_slice)
    ty_trans.chunk(chunks={'time': -1})
    ty_trans
    return (ty_trans,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    These data aren't enourmous (just over 6GB), but they're not chunked very intelligently - having lots of little chunks increases multiprocessing overhead costs. We want chunks in the 100MB - 1GB range (probably towards the lower end of that range). We want to make computations, such as averaging, along the time axis, so it makes sense to keep all the time data for any position together in a chunk. However, because the input files consist of one time-step per file, we couldn't do this at load time. However, now that the data are loaded, we can do it after the fact:
    """)
    return


@app.cell
def _(ty_trans):
    ty_trans_1 = ty_trans.chunk(chunks={'time': -1, 'st_ocean': -1, 'yu_ocean': 102, 'xt_ocean': 400})
    ty_trans_1
    return (ty_trans_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now that we've worked out our chunking schema, we'll apply it to `tx_trans` as well.
    """)
    return


@app.cell
def _(
    catalog,
    end_time,
    experiment,
    lat_range,
    start_time,
    time_slice,
    ty_trans_1,
):
    _cat_subset = catalog[experiment]
    _var_search = _cat_subset.search(variable='tx_trans', frequency='1mon')
    _dset = _var_search.to_dask(xarray_open_kwargs={'decode_timedelta': False})
    _darray = _dset['tx_trans']
    _darray = _darray.sel(time=slice(start_time, end_time))
    tx_trans = _darray
    tx_trans = tx_trans.sel(yt_ocean=lat_range, time=time_slice)
    tx_trans = tx_trans.chunk(chunks={'time': -1, 'st_ocean': -1, 'yt_ocean': 102, 'xu_ocean': 400})
    ty_trans_2 = ty_trans_1.rename({'yu_ocean': 'latitude', 'xt_ocean': 'longitude'})
    tx_trans = tx_trans.rename({'yt_ocean': 'latitude', 'xu_ocean': 'longitude'})
    tx_trans
    return tx_trans, ty_trans_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Take time average
    """)
    return


@app.cell
def _(tx_trans, ty_trans_2):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    days_in_month = ty_trans_2.time.dt.days_in_month
    # weighed time mean by month length
    days_in_year = 365
    tx_trans_1 = (tx_trans * days_in_month / days_in_year).sum('time')
    tx_trans_1 = tx_trans_1.load()
    ty_trans_3 = (ty_trans_2 * days_in_month / days_in_year).sum('time')
    ty_trans_3 = ty_trans_3.load()
    return tx_trans_1, ty_trans_3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Convert from mass transport to volume transport
    """)
    return


@app.cell
def _(mask_x_transport_1, mask_y_transport_1, tx_trans_1, ty_trans_3):
    ρ0 = 1035  # kg/m^3
    ty_trans_4 = ty_trans_3 * mask_y_transport_1 / ρ0
    tx_trans_2 = tx_trans_1 * mask_x_transport_1 / ρ0  # convert kg/s -> m^3/s
    return tx_trans_2, ty_trans_4


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Extract transport values along contour
    """)
    return


@app.cell
def _(
    contour_index_array,
    contour_ordering,
    mask_x_numbered_1d,
    mask_y_numbered_1d,
    tx_trans_2,
    ty_trans_4,
    xr,
):
    ## We could also loop in time if we didn't want the time average. 
    # In that case, initialise a data array and fill in data by looping in time.
    x_transport_1d = tx_trans_2.stack(contour_index=['latitude', 'longitude'])
    # stack transports into 1d and drop any points not on contour:
    x_transport_1d = x_transport_1d.where(mask_x_numbered_1d > 0, drop=True)
    y_transport_1d = ty_trans_4.stack(contour_index=['latitude', 'longitude'])
    y_transport_1d = y_transport_1d.where(mask_y_numbered_1d > 0, drop=True)
    vol_trans_across_contour = xr.concat((x_transport_1d, y_transport_1d), dim='contour_index')
    vol_trans_across_contour = vol_trans_across_contour.sortby(contour_ordering)
    # combine all points on contour:
    vol_trans_across_contour.coords['contour_index'] = contour_index_array
    vol_trans_across_contour = vol_trans_across_contour.load()
    return (vol_trans_across_contour,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot the cumulative transport along the contour, summed over the lower part of the water column.
    We can clearly see the northward dense water export in the Ross and Weddell Seas.
    """)
    return


@app.cell
def _(plt, vol_trans_across_contour):
    plt.figure(1, figsize=(10, 4))

    (vol_trans_across_contour.sel(st_ocean=slice(800, 6000)).sum('st_ocean').cumsum('contour_index')/1e6).plot()
    plt.ylabel('Cumulative transport across contour (Sv)');
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Finally, we can extract the coordinates of the contour index, and the distance, for a more meaningful $x$ axis.
    """)
    return


@app.cell
def _(mask_x_numbered_1d, mask_y_numbered_1d, np, xr):
    contour_ordering_1 = xr.concat((mask_x_numbered_1d, mask_y_numbered_1d), dim='contour_index')
    contour_ordering_1 = contour_ordering_1.sortby(contour_ordering_1)
    lat_along_contour = contour_ordering_1.latitude.copy()
    # get lat and lon along contour, useful for plotting later:
    lon_along_contour = contour_ordering_1.longitude.copy()
    contour_index_array_1 = np.arange(1, len(contour_ordering_1) + 1)
    lat_along_contour.coords['contour_index'] = contour_index_array_1
    # don't need the multi-index anymore, replace with contour count and save
    lon_along_contour.coords['contour_index'] = contour_index_array_1
    return lat_along_contour, lon_along_contour


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Extract distance in between contour coordinates
    This is used to label the x-axis in the plots below. Note these distances don't exactly match the dxt / dyt variables in the model, but it's only used for plotting, so it's probably ok.
    """)
    return


@app.cell
def _(lat_along_contour, lon_along_contour, np):
    from geopy import distance
    num_points_1 = len(lat_along_contour)
    d_distance_along_contour = np.zeros(num_points_1)
    for i in range(num_points_1 - 1):
        d_distance_along_contour[i + 1] = distance.distance((lat_along_contour[i], lon_along_contour[i]), (lat_along_contour[i + 1], lon_along_contour[i + 1])).km
    distance_along_contour = np.cumsum(d_distance_along_contour)
    return (distance_along_contour,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Select the indices for axis labels of specific longitudes, so we can plot transport vs distance but have longitude labels instead of length
    """)
    return


@app.cell
def _(lon_along_contour, np):
    target_lons = [-280, -240, -180, -120, -60, 0, 6., 80]

    distance_indices = np.zeros_like(target_lons)

    for j, lon in enumerate(target_lons):
        distance_indices[j] = np.argmin(np.abs((lon_along_contour.values - lon)))
    return (distance_indices,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Plot cumulative transport against distance along the contour.
    """)
    return


@app.cell
def _():
    depth_to_integrate = 800 # m
    return (depth_to_integrate,)


@app.cell
def _(
    contour_depth,
    depth_to_integrate,
    distance_along_contour,
    distance_indices,
    plt,
    vol_trans_across_contour,
):
    _fig, axes = plt.subplots(nrows=2, figsize=(10, 8))
    axes[0].plot(distance_along_contour, 1e-06 * vol_trans_across_contour.sel(st_ocean=slice(depth_to_integrate, 6000)).sum('st_ocean').cumsum('contour_index'))
    # factor 1e-6 converts m^3/s -> Sv
    axes[0].set_ylabel('Cumulative transport (Sv)')
    axes[0].set_xlabel('Distance from 80$^\\circ$E (10$^3$ km)')
    axes[0].set_xlim(0, distance_along_contour[-1])
    axes[0].set_title(f'Cumulative transport across {contour_depth} m isobath below {depth_to_integrate} m depth')
    axes[1].plot(distance_along_contour, 1e-06 * vol_trans_across_contour.sel(st_ocean=slice(depth_to_integrate, 6000)).sum('st_ocean').cumsum('contour_index'))
    axes[1].set_xticks(distance_along_contour[distance_indices.astype(int)[:-1]])
    axes[1].set_xticklabels(('80$^\\circ$E', '120$^\\circ$E', '180$^\\circ$W', '120$^\\circ$W', '60$^\\circ$W', '0$^\\circ$', '60$^\\circ$E'))
    axes[1].set_xlim(0, distance_along_contour[-1])
    axes[1].set_xlabel('Longitude coordinates along contour')
    axes[1].set_ylabel('Cumulative transport (Sv)')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can see that there is a net northward transport across the 1000m isobath on the Antarctic continental slope. This is spatially localised near the Ross and Weddell Seas where dense water is formed and exported. We could then choose to extract the density (or salt and temperature) along this same path, do this by interpolating density to the north and eastern edge of t-cells. Then we could bin the transports in each depth level into the corresponding density, to determine the transport across the contour in density space. Note this density binning needs to be done online or using at least daily data. An example of this calculation can be found in https://github.com/claireyung/Topographic_Hotspots_Upwelling-Paper_Code/blob/main/Analysis_Code/Save_and_bin_along_contours.ipynb.
    """)
    return


if __name__ == "__main__":
    app.run()
