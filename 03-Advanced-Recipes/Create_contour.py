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
    # Create a contour

    This notebook calculates a bathymetry contour but should be applicable to an arbitrary variable, such as sea surface height. There are two different approaches presented in this notebook to select a contour:
    - Approach 1: Extracting the coordinates using `matplotlib`'s `Path` class
        - assumes the contour you want to select is continuous
        - gives you the cells closest to the selected contour, can be deeper or shallower
    - Approach 2: Custom method for selecting and tracing a specific contour
        - no cells deeper than selected contour value (unless manually added which might be necessary)

    We then create some masks to indicate which direction is across the contour at each position along the contour. This step is useful in case you want to calculate cross-contour transport (the mask will work for both a B-grid and a C-grid). Both approaches ensure that the contour is (i) continuous and (ii) there all points are connected adjacently (not just diagonally) which is required for correct transport calculations.

    This notebook goes through selecting the 1000 m isobath around Antarctica which we often use to separate the Antarctic continental shelf from the offshore Southern Ocean. We use the OM2-01 grid for approach 1 and the OM3-25km grid for approach 2.

    Known locations of the Antarctic 1000 m bathymetry contour for commonly used models:
    - OM2-01: '/g/data/ik11/Antarctic_slope_contour_1000m.npz'
    - PanAnt-01: '/g/data/ik11/Antarctic_slope_contour_1000m_MOM6_01deg.nc'
    - PanAnt-005: '/g/data/ik11/Antarctic_slope_contour_1000m_MOM6_005deg.nc'
    - OM3-25km: '/g/data/ol01/Antarctic_slope_contour_1000m_OM3_25km.nc'

    Computation times shown used conda environment `analysis3-26.06` on 28 broadwell cpus.

    **Alert:** After including the additional cases the contour number doesn't always monotonically increase along the contour. At the moment, the two indices that are set at the same time are adjacent numbers, whereas if you were following the contour you'd expect their numbers to be 2 apart with the other coordinate in between. See  https://github.com/COSIMA/cosima-recipes/issues/383.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
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
    import cv2 # need to install opencv-python for this, used in approach 2

    from dask.distributed import Client

    catalog = intake.cat.access_nri
    return Client, cmocean, cv2, intake, np, plt, xr


@app.cell
def _(Client):
    client = Client(threads_per_worker=1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Approach 1

    Extracting the coordinates using `matplotlib`'s `Path` class
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Choose experiment
    """)
    return


@app.cell
def _(intake):
    catalog_1 = intake.cat.access_nri
    experiment = '01deg_jra55v13_ryf9091'  # the RYF90-91 experiment
    return catalog_1, experiment


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Load quantity we want a contour of, e.g. bathymetry
    """)
    return


@app.cell
def _(catalog_1, experiment):
    ht = catalog_1[experiment].search(variable='ht', frequency='fx').to_dask().ht
    hu = catalog_1[experiment].search(variable='hu', frequency='fx').to_dask().hu
    return ht, hu


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Choose a latitude range

    Make sure the contour fits in the range, but there is not too much extra space. Extra space slows down the computation.

    We must make sure that this latitude range is so that the t-cells are always south and west of the u-cells.

    This is important because the meridional and zonal transports occur on different grids to each other. We can check this by loading the `u`-cell and `t`-cell coordinates.

    We choose this convention so that later on when we create `numpy` grids of where the contour is and in what direction the contour goes.
    """)
    return


@app.cell
def _():
    lat_range = slice(-82, -59)
    return (lat_range,)


@app.cell
def _(ht, hu, lat_range):
    hu_1 = hu.sel(yu_ocean=lat_range)
    ht_1 = ht.sel(yt_ocean=lat_range)
    return ht_1, hu_1


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
def _(contour_depth, ht_1, plt):
    _fig = plt.figure(figsize=(10, 4))
    ht_1.plot(extend='both', cbar_kwargs={'label': 'ocean depth [m]'})
    ht_1.plot.contour(levels=[contour_depth], colors='r', linestyles='-')
    plt.title('Ocean depth (m)')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Fill in land with zeros and load:
    """)
    return


@app.cell
def _(ht_1):
    ht_2 = ht_1.fillna(0).load()
    return (ht_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Contour is on t-grid (we assume ACCESS-OM2 B-grid transports)
    """)
    return


@app.cell
def _(ht_2):
    grid_sel = 't'
    x_var = ht_2['xt_ocean']
    y_var = ht_2['yt_ocean']
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Select the contour
    We need to isolate out the single contour along the slope and get rid of the contours on the little isolated sea mounts and depressions.
    """)
    return


@app.cell
def _(contour_depth, ht_2, plt):
    _fig = plt.figure(figsize=(10, 4))
    sc = plt.contour(ht_2, levels=[contour_depth])
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
def _(ht_2, np, x_contour_2, y_contour_2):
    ht_contour = np.zeros(len(x_contour_2))
    for _ii in range(len(ht_contour)):
        ht_contour[_ii] = ht_2[y_contour_2[_ii], x_contour_2[_ii]]
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
def _(contour_mask_numbered, ht_2, num_points, x_contour_2, xr, y_contour_2):
    contour_mask = xr.zeros_like(ht_2)
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
        for _jj in range(len(contour_mask.yt_ocean))[::-1][:-1]:
            if contour_masked_above[_jj, _ii] == mask_value:
                if contour_masked_above[_jj - 1, _ii] == 0:
                    contour_masked_above[_jj - 1, _ii] = mask_value
                if contour_masked_above[_jj, _ii + 1] == 0:
                    contour_masked_above[_jj, _ii + 1] = mask_value
    for _ii in range(len(contour_mask.xt_ocean))[::-1][:-1]:
        for _jj in range(len(contour_mask.yt_ocean))[::-1][:-1]:
            if contour_masked_above[_jj, _ii] == mask_value:
                if contour_masked_above[_jj - 1, _ii] == 0:
                    contour_masked_above[_jj - 1, _ii] = mask_value
                if contour_masked_above[_jj, _ii - 1] == 0:
                    contour_masked_above[_jj, _ii - 1] = mask_value
    for _ii in range(len(contour_mask.xt_ocean))[::-1][:-1]:
        for _jj in range(len(contour_mask.yt_ocean) - 1):
            if contour_masked_above[_jj, _ii] == mask_value:
                if contour_masked_above[_jj + 1, _ii] == 0:
                    contour_masked_above[_jj + 1, _ii] = mask_value
                if contour_masked_above[_jj, _ii - 1] == 0:
                    contour_masked_above[_jj, _ii - 1] = mask_value
    for _ii in range(len(contour_mask.xt_ocean) - 1):
        for _jj in range(len(contour_mask.yt_ocean) - 1):
            if contour_masked_above[_jj, _ii] == mask_value:
                if contour_masked_above[_jj + 1, _ii] == 0:
                    contour_masked_above[_jj + 1, _ii] = mask_value
                if contour_masked_above[_jj, _ii + 1] == 0:
                    contour_masked_above[_jj, _ii + 1] = mask_value
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
    mask_x_transport = np.zeros_like(contour_mask_numbered_1)
    mask_y_transport = np.zeros_like(contour_mask_numbered_1)
    mask_y_transport_numbered = np.zeros_like(contour_mask_numbered_1)
    mask_x_transport_numbered = np.zeros_like(contour_mask_numbered_1)
    shape = contour_masked_above.shape
    _contour_masked_above_halo = np.zeros((shape[0], shape[1] + 2))
    _contour_masked_above_halo[:, 0] = contour_masked_above[:, -1]
    _contour_masked_above_halo[:, 1:-1] = contour_masked_above
    _contour_masked_above_halo[:, -1] = contour_masked_above[:, 0]
    _new_number_count = 1
    for _mask_loc in range(1, int(np.max(contour_mask_numbered_1)) + 1):
        _index_i = np.where(contour_mask_numbered_1 == _mask_loc)[1]
        _index_j = np.where(contour_mask_numbered_1 == _mask_loc)[0]
        if contour_masked_above[_index_j + 1, _index_i] == 0 and contour_masked_above[_index_j - 1, _index_i] != 0:
            mask_y_transport[_index_j, _index_i] = -1
            mask_y_transport_numbered[_index_j, _index_i] = _new_number_count
            _new_number_count = _new_number_count + 1
        elif contour_masked_above[_index_j - 1, _index_i] == 0 and contour_masked_above[_index_j + 1, _index_i] != 0:
            mask_y_transport[_index_j - 1, _index_i] = 1
            mask_y_transport_numbered[_index_j - 1, _index_i] = _new_number_count
            _new_number_count = _new_number_count + 1
        elif contour_masked_above[_index_j - 1, _index_i] == 0 and contour_masked_above[_index_j + 1, _index_i] == 0:
            mask_y_transport[_index_j - 1, _index_i] = 1
            mask_y_transport[_index_j, _index_i] = -1
            mask_y_transport_numbered[_index_j - 1, _index_i] = _new_number_count
            mask_y_transport_numbered[_index_j, _index_i] = _new_number_count + 1
            _new_number_count = _new_number_count + 2
        if _contour_masked_above_halo[_index_j, _index_i + 2] == 0 and _contour_masked_above_halo[_index_j, _index_i] != 0:
            mask_x_transport[_index_j, _index_i] = -1
            mask_x_transport_numbered[_index_j, _index_i] = _new_number_count
            _new_number_count = _new_number_count + 1
        elif _contour_masked_above_halo[_index_j, _index_i] == 0 and _contour_masked_above_halo[_index_j, _index_i + 2] != 0:
            mask_x_transport[_index_j, _index_i - 1] = 1
            mask_x_transport_numbered[_index_j, _index_i - 1] = _new_number_count
            _new_number_count = _new_number_count + 1
        elif _contour_masked_above_halo[_index_j, _index_i] == 0 and _contour_masked_above_halo[_index_j, _index_i + 2] == 0:
            mask_x_transport[_index_j, _index_i - 1] = 1
            mask_x_transport[_index_j, _index_i] = -1
            mask_x_transport_numbered[_index_j, _index_i - 1] = _new_number_count
            mask_x_transport_numbered[_index_j, _index_i] = _new_number_count + 1
            _new_number_count = _new_number_count + 2
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

    Here we convert the contour masks to a dataset (which could be saved and reloaded). We need to ensure the lat / lon coordinates correspond to the actual data location:
    - The y masks are used for `ty_trans`, so like `vhrho` this should have dimensions (`yu_ocean`, `xt_ocean`).
    - The x masks are used for `tx_trans`, so like `uhrho` this should have dimensions (`yt_ocean`, `xu_ocean`).

    Hint: You can set the actual name to always be simply latitude/longitude irrespective of the variable to make concatenation of transports in both direction and sorting possible. An example is given in [Cross_contour_transport.ipynb](https://github.com/COSIMA/cosima-recipes/blob/main/03-Advanced-Recipes/Cross-contour_transport.ipynb).
    """)
    return


@app.cell
def _(
    contour_mask_numbered_1,
    contour_masked_above,
    ht_2,
    hu_1,
    mask_x_transport,
    mask_x_transport_numbered,
    mask_y_transport,
    mask_y_transport_numbered,
    xr,
):
    # Create dataset
    ds_approach1 = xr.Dataset({'mask_x_transport': (('yt_ocean', 'xu_ocean'), mask_x_transport), 'mask_y_transport': (('yu_ocean', 'xt_ocean'), mask_y_transport), 'mask_x_transport_numbered': (('yt_ocean', 'xu_ocean'), mask_x_transport_numbered), 'mask_y_transport_numbered': (('yu_ocean', 'xt_ocean'), mask_y_transport_numbered), 'contour_masked_above': (('yt_ocean', 'xt_ocean'), contour_masked_above), 'contour_mask_numbered': (('yt_ocean', 'xt_ocean'), contour_mask_numbered_1.values)}, coords={'xt_ocean': ht_2.xt_ocean, 'yt_ocean': ht_2.yt_ocean, 'xu_ocean': hu_1.xu_ocean, 'yu_ocean': hu_1.yu_ocean})
    return (ds_approach1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And plot just to confirm that we didn't mess up anything.
    """)
    return


@app.cell
def _(cmocean, ds_approach1, plt):
    plt.figure(1, figsize=(10, 4))

    ds_approach1.mask_x_transport.plot(cmap=cmocean.cm.balance, vmin=-1.5, vmax=1.5);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Lets use the mask we created to plot surface temperature on the Antarctic contiental shelf.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load surface temperature
    """)
    return


@app.cell
def _(catalog_1, experiment, lat_range):
    # Define year to open
    dates_2086 = '2086.*'
    temp = catalog_1[experiment].search(variable='surface_temp', frequency='1mon', start_date=dates_2086).to_dask()
    temp = temp.sel(yt_ocean=lat_range).surface_temp.mean('time')
    return (temp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create the shelf mask
    """)
    return


@app.cell
def _(ds_approach1):
    shelf_mask = ds_approach1.contour_masked_above.where(ds_approach1.contour_masked_above==0, 1)
    shelf_mask = shelf_mask.where(shelf_mask==1)
    return (shelf_mask,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Select shelf
    """)
    return


@app.cell
def _(shelf_mask, temp):
    temp_masked = temp.where(shelf_mask.isnull())
    return (temp_masked,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's also select the 1000 m contour
    """)
    return


@app.cell
def _(ds_approach1):
    slope_contour = ds_approach1.contour_masked_above.where(ds_approach1.contour_masked_above>0)
    slope_contour = slope_contour/slope_contour
    return (slope_contour,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can now make the plot
    """)
    return


@app.cell
def _(plt, slope_contour, temp_masked):
    plt.figure(1, figsize=(10, 4))

    temp_masked.plot()
    slope_contour.fillna(2).plot.contour(levels=[0,1], colors='k', linewidths=1.5);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Approach 2

    Custom method for selecting and tracing a specific depth contour.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load data from the OM3-25km beta release.
    """)
    return


@app.cell
def _(intake):
    datastore_path = "/g/data/ol01/access-om3-output/access-om3-025/MC_25km_jra_ryf-1.0-beta/experiment_datastore.json"

    datastore = intake.open_esm_datastore(
        datastore_path,
        columns_with_iterables=[
            "variable",
            "variable_long_name",
            "variable_standard_name",
            "variable_cell_methods",
            "variable_units"
        ]
    )
    return (datastore,)


@app.cell
def _(datastore):
    # Load bathymetry 
    var_search = datastore.search(variable="deptho")
    ds     = var_search.search(path=var_search.df.path[0]).to_dask() # we only need one file as bathymetry doesn't change
    deptho = ds["deptho"].sel(yh=slice(-82,-55)).load() # select lat_range and load data
    return (deptho,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Select desired contour value
    """)
    return


@app.cell
def _():
    contour_depth_1 = 1000
    return (contour_depth_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot the contour, note there are actually a bunch of locations near the prime meridian where the 1000 m contour is not continuous. We will add cells manually next to land below.
    """)
    return


@app.cell
def _(contour_depth_1, deptho, plt):
    _fig = plt.figure(figsize=(10, 4))
    deptho.plot(extend='both', cbar_kwargs={'label': 'ocean depth [m]'})
    deptho.plot.contour(levels=[contour_depth_1], colors='r', linestyles='-')
    plt.title('Ocean depth (m)')
    (plt.xlim(-30, 30), plt.ylim(-78, -65))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create a binary mask
    """)
    return


@app.cell
def _(contour_depth_1, deptho, np):
    # Temporary mask with 0 bathymetry is deeper than the contour depth and 1 elsewhere
    tmp_mask = np.copy(deptho)
    tmp_mask[np.where(deptho > contour_depth_1)] = 0  # locations where the bathymetry is deeper than contour_depth
    tmp_mask[np.where(deptho <= contour_depth_1)] = 1  # locations where the bathymetry is shallower or equal to contour_depth
    return (tmp_mask,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Spread the isobath contour so all points are connected adjacently (not just diagonally).
    """)
    return


@app.cell
def _(cv2, np, tmp_mask):
    # Spread the 1s in tmp_mask to their neighboring pixels (using a 3x3 kernel). 
    # This ensures that the contour is connected horizontally and vertically, not just diagonally.
    kernel = np.ones((3,3),np.uint8) 

    # isolate the edges of the contour -> only the pixels at the boundary of the contour are marked with 1
    contour_mask0 = cv2.dilate(tmp_mask,kernel,iterations=1) - tmp_mask
    return (contour_mask0,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Select a starting point for tracing the contour along the western edge of the domain.
    """)
    return


@app.cell
def _(contour_mask0, deptho, np):
    # start at western edge of domain, at y point closest to correct depth contour:
    contour_mask_1 = np.zeros_like(deptho)
    contour_lat_index_start = np.where(contour_mask0[:, 0] > 0)[0][-1]
    # pick most northerly contour:
    # pick most southerly contour: 
    # contour_lat_index_start = np.where(contour_mask0[:,0]>0)[0][0]
    # starting point is marked with 1 in contour_mask, which can then be used as a seed for further contour tracing or region-growing algorithms
    contour_mask_1[contour_lat_index_start, 0] = 1
    return contour_lat_index_start, contour_mask_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot to make sure contour_lat_index_start (yellow dot) is on the correct contour.
    """)
    return


@app.cell
def _(contour_depth_1, contour_lat_index_start, deptho, plt):
    plt.figure(1, figsize=(16, 8))
    plt.pcolormesh(deptho)
    plt.contour(deptho, [contour_depth_1], colors='r')
    plt.xlim((-1, 10))
    plt.ylim((100, 250))
    plt.plot(0, contour_lat_index_start, 'yo', markersize=10)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Manually change a few grid cells (ensure continuous contour and no loops) - this is specific to the grid and the contour selected!

    Set cells to 0 to remove them from the contour and set to 1 to add cells to contour.

    This is laborious, see next cell to find out which grid cells need to be changed for the OM3-25km example.
    """)
    return


@app.cell
def _(contour_mask0):
    # Below is true for the OM3-25km grid with contour_depth = 1000
    contour_mask0[230,868] = 0
    contour_mask0[247:254,914:921] = 0
    contour_mask0[253,913] = 0
    contour_mask0[249,909] = 0
    contour_mask0[245:249,908] = 0
    contour_mask0[244:249,916] = 0
    contour_mask0[225:230,914] = 0
    contour_mask0[102,1017] = 0
    contour_mask0[102:106,1016] = 1
    contour_mask0[105:107,1017] = 1
    contour_mask0[106:108,1018] = 1
    contour_mask0[107:109,1019] = 1
    contour_mask0[108,1019:1023] = 1
    contour_mask0[125,1042:1044] = 1
    contour_mask0[126,1043:1046] = 1

    contour_mask0[161:163,1113] = 1
    contour_mask0[162,1113:1115] = 1
    contour_mask0[162:165,1115] = 1
    contour_mask0[164,1115:1120] = 1
    contour_mask0[162:165,1120] = 1
    contour_mask0[162,1121] = 1
    contour_mask0[160,1127] = 1
    contour_mask0[159,1128] = 0

    contour_mask0[160:163,1194] = 1
    contour_mask0[160,1194:1199] = 1
    contour_mask0[160:163,1199] = 1
    contour_mask0[162,1199:1207] = 1
    contour_mask0[160:163,1206] = 1

    contour_mask0[123:125,401] = 0
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot `contour_mask0` to check which cells need to be changed.
    """)
    return


@app.cell
def _(contour_mask0, plt):
    # Check how contour_mask0 looks like 
    # - is the contour continuous around Antarctica?
    # - are there loops that would not contribute to any cross-slope transport anyway?
    # Change the xlim, ylim to zoom into different regions

    plt.figure(1,figsize=(16,8))
    plt.pcolormesh(contour_mask0)
    plt.colorbar()
    plt.clim((0,2))
    plt.scatter(401,123, c='r') # adjust to select grid cells that need to be changed
    plt.xlim((370,420))
    plt.ylim((50,160));
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Select out only the contour we want: We can now finally trace the connected contour from our starting point to the right edge of the grid, marking each point along the contour with a unique label (`count`). The algorithm checks the 4-connected neighbours (east, west, south, north) of the current point and checks each neighbour to see if it is (i) within the grid bounds and (ii) part of the contour and unvisited. The first valid neighbour found is selected as the next point (`new_loc`). If no valid neighbours are found, the contour has reached a dead end, and the loop terminates - if this happens before we reach the eastern boundary we need to go back and amend `contour_mask0`.
    """)
    return


@app.cell
def _(contour_lat_index_start, contour_mask0, contour_mask_1, deptho):
    # set up indices
    last_index_i = 0
    last_index_j = contour_lat_index_start
    count = 1  # start labeling from 1
    contour_mask_1[last_index_j, last_index_i] = count
    # mark starting point
    contour_mask0[last_index_j, last_index_i] = 0
    while last_index_i < deptho.shape[1] - 1:  # mark as visited
        if last_index_i == 0:
    # loop until the right edge or dead end
            neighbours = [(last_index_j, last_index_i + 1), (last_index_j + 1, last_index_i), (last_index_j - 1, last_index_i)]
        else:
            neighbours = [(last_index_j, last_index_i + 1), (last_index_j, last_index_i - 1), (last_index_j + 1, last_index_i), (last_index_j - 1, last_index_i)]  # define neighbours
        new_loc = None
        for nj, ni in neighbours:  # first step: don't go backwards
            if 0 <= nj < contour_mask0.shape[0] and 0 <= ni < contour_mask0.shape[1]:
                if contour_mask0[nj, ni] == 1:  # east
                    new_loc = (nj, ni)  # south
                    break  # north
        if new_loc is None:
            print('Dead end reached at step', count)
            break  # after first step: include west
        else:
            last_index_j, last_index_i = new_loc  # east
            count = count + 1  # west
            contour_mask_1[last_index_j, last_index_i] = count  # south
            contour_mask0[last_index_j, last_index_i] = 0  # north  # find valid neighbours  # unvisited contour  # dead end → stop  # move to next point  # mark visited
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can now check what `contour_mask` looks like - is it continuous around Antarctica? Are there still any loops or duplicate cells that are not needed?
    """)
    return


@app.cell
def _(contour_mask_1, deptho, plt):
    plt.figure(1, figsize=(16, 8))
    plt.pcolormesh(deptho.xh, deptho.yh, contour_mask_1)
    plt.colorbar()
    plt.clim((0, 1000))
    plt.xlim((5, 80))  # adjust xlim and ylim to zoom in and tracer the contour
    plt.ylim((-71, -64))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Looking good! We can now proceed as for approach 1 and...

    #### Create mask to separate points above (offshelf) from points below (onshelf) contour
    """)
    return


@app.cell
def _(contour_mask_1, deptho, np):
    contour_mask_numbered_2 = contour_mask_1
    contour_masked_above_1 = np.copy(contour_mask_numbered_2)
    contour_masked_above_1[-1, 0] = -100
    for _ii in range(len(deptho.xh) - 1):
        for _jj in range(len(deptho.yh))[::-1][:-1]:
            if contour_masked_above_1[_jj, _ii] == -100:
                if contour_masked_above_1[_jj - 1, _ii] == 0:
                    contour_masked_above_1[_jj - 1, _ii] = -100
                if contour_masked_above_1[_jj, _ii + 1] == 0:
                    contour_masked_above_1[_jj, _ii + 1] = -100
                if contour_masked_above_1[_jj - 1, _ii + 1] == 0:
                    contour_masked_above_1[_jj - 1, _ii + 1] = -100
    for _ii in range(len(deptho.xh))[::-1][:-1]:
        for _jj in range(len(deptho.yh))[::-1][:-1]:
            if contour_masked_above_1[_jj, _ii] == -100:
                if contour_masked_above_1[_jj - 1, _ii] == 0:
                    contour_masked_above_1[_jj - 1, _ii] = -100
                if contour_masked_above_1[_jj, _ii - 1] == 0:
                    contour_masked_above_1[_jj, _ii - 1] = -100
                if contour_masked_above_1[_jj - 1, _ii - 1] == 0:
                    contour_masked_above_1[_jj - 1, _ii - 1] = -100
    for _ii in range(len(deptho.xh))[::-1][:-1]:
        for _jj in range(len(deptho.yh) - 1):
            if contour_masked_above_1[_jj, _ii] == -100:
                if contour_masked_above_1[_jj + 1, _ii] == 0:
                    contour_masked_above_1[_jj + 1, _ii] = -100
                if contour_masked_above_1[_jj, _ii - 1] == 0:
                    contour_masked_above_1[_jj, _ii - 1] = -100
                if contour_masked_above_1[_jj + 1, _ii - 1] == 0:
                    contour_masked_above_1[_jj + 1, _ii - 1] = -100
    for _ii in range(len(deptho.xh) - 1):
        for _jj in range(len(deptho.yh) - 1):
            if contour_masked_above_1[_jj, _ii] == -100:
                if contour_masked_above_1[_jj + 1, _ii] == 0:
                    contour_masked_above_1[_jj + 1, _ii] = -100
                if contour_masked_above_1[_jj, _ii + 1] == 0:
                    contour_masked_above_1[_jj, _ii + 1] = -100
                if contour_masked_above_1[_jj + 1, _ii + 1] == 0:
                    contour_masked_above_1[_jj + 1, _ii + 1] = -100
    return contour_mask_numbered_2, contour_masked_above_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Create masks for x and y transport calculations (i.e. determine if positive u and v will be into or out of contour)
    """)
    return


@app.cell
def _(contour_mask_numbered_2, contour_masked_above_1, np):
    mask_x_transport_1 = np.zeros_like(contour_mask_numbered_2)
    mask_y_transport_1 = np.zeros_like(contour_mask_numbered_2)
    mask_y_transport_numbered_1 = np.zeros_like(contour_mask_numbered_2)
    mask_x_transport_numbered_1 = np.zeros_like(contour_mask_numbered_2)
    _contour_masked_above_halo = np.zeros((contour_masked_above_1.shape[0], contour_masked_above_1.shape[1] + 2))
    _contour_masked_above_halo[:, 0] = contour_masked_above_1[:, -1]
    _contour_masked_above_halo[:, 1:-1] = contour_masked_above_1
    _contour_masked_above_halo[:, -1] = contour_masked_above_1[:, 0]
    _new_number_count = 1
    for _mask_loc in range(1, int(np.max(contour_mask_numbered_2)) + 1):
        _index_i = np.where(contour_mask_numbered_2 == _mask_loc)[1]
        _index_j = np.where(contour_mask_numbered_2 == _mask_loc)[0]
        if contour_masked_above_1[_index_j + 1, _index_i] == 0 and contour_masked_above_1[_index_j - 1, _index_i] != 0:
            mask_y_transport_1[_index_j, _index_i] = -1
            mask_y_transport_numbered_1[_index_j, _index_i] = _new_number_count
            _new_number_count = _new_number_count + 1
        elif contour_masked_above_1[_index_j - 1, _index_i] == 0 and contour_masked_above_1[_index_j + 1, _index_i] != 0:
            mask_y_transport_1[_index_j - 1, _index_i] = 1
            mask_y_transport_numbered_1[_index_j - 1, _index_i] = _new_number_count
            _new_number_count = _new_number_count + 1
        if _contour_masked_above_halo[_index_j, _index_i + 2] == 0 and _contour_masked_above_halo[_index_j, _index_i] != 0:
            mask_x_transport_1[_index_j, _index_i] = -1
            mask_x_transport_numbered_1[_index_j, _index_i] = _new_number_count
            _new_number_count = _new_number_count + 1
        elif _contour_masked_above_halo[_index_j, _index_i] == 0 and _contour_masked_above_halo[_index_j, _index_i + 2] != 0:
            mask_x_transport_1[_index_j, _index_i - 1] = 1
            mask_x_transport_numbered_1[_index_j, _index_i - 1] = _new_number_count
            _new_number_count = _new_number_count + 1
    return (
        mask_x_transport_1,
        mask_x_transport_numbered_1,
        mask_y_transport_1,
        mask_y_transport_numbered_1,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Write as dataset
    """)
    return


@app.cell
def _(datastore):
    # Load umo and vmo to get correct coordinate information (info might also be in some grid file?)
    umo = datastore.search(variable='umo').to_dask().umo.sel(yh=slice(-82,-55))
    vmo = datastore.search(variable='vmo').to_dask().vmo.sel(yq=slice(-82,-54.9))
    return umo, vmo


@app.cell
def _(
    contour_mask_numbered_2,
    contour_masked_above_1,
    deptho,
    mask_x_transport_1,
    mask_x_transport_numbered_1,
    mask_y_transport_1,
    mask_y_transport_numbered_1,
    umo,
    vmo,
    xr,
):
    # Create dataset
    ds_approach2 = xr.Dataset({'mask_x_transport': (('yh', 'xq'), mask_x_transport_1), 'mask_y_transport': (('yq', 'xh'), mask_y_transport_1), 'mask_x_transport_numbered': (('yh', 'xq'), mask_x_transport_numbered_1), 'mask_y_transport_numbered': (('yq', 'xh'), mask_y_transport_numbered_1), 'contour_masked_above': (('yh', 'xh'), contour_masked_above_1), 'contour_mask_numbered': (('yh', 'xh'), contour_mask_numbered_2)}, coords={'xh': deptho.xh, 'yh': deptho.yh, 'xq': umo.xq, 'yq': vmo.yq})
    return (ds_approach2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And plot just to confirm that we didn't mess up anything.
    """)
    return


@app.cell
def _(cmocean, ds_approach2, plt):
    plt.figure(1, figsize=(10, 4))

    ds_approach2.mask_x_transport.plot(cmap=cmocean.cm.balance, vmin=-1.5, vmax=1.5);
    return


if __name__ == "__main__":
    app.run()
