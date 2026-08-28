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
    # Spatial selection with tripolar ACCESS-OM2 grid

    The ACCESS-OM2 model collection utilises a tripolar grid north of 65N to avoid a point of convergence over the ocean at the north pole.

    This means any plotting or analysis in this region needs to use 2D curvilinear latitude and longitude coordinates.

    This notebook will cover how to use the curvilinear coordinates to select data within latitude and longitude limits, and how to plot data in the tripole region correctly. There is also a [full tutorial on plotting with projections](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/01-Basics/03-Maps_with_Cartopy.html).

    Below the tripole area it is sufficient to use 1D latitude and longitude coordinates, which are much more convenient to use as they can use the [xarray](http://xarray.pydata.org/en/stable/index.html)'s [sel](http://xarray.pydata.org/en/stable/generated/xarray.DataArray.sel.html) method with `slice` notation.

    This notebook will also demonstrate how to do this.

    The data output from the CICE model component do not have a convenient to use 1D latitude and longitude coordinates. As the ice and ocean models share a grid the coordinates from each model can be used interchangeably with the other. A method to add 1D latitude and longitude coordinates to an ice [`xarray.DataArray`](http://xarray.pydata.org/en/stable/generated/xarray.DataArray.html) is also demonstrated.
    """)
    return


@app.cell
def _():
    import intake
    import matplotlib.pyplot as plt
    import xarray as xr
    import numpy as np
    import cartopy.crs as ccrs

    from dask.distributed import Client

    return Client, ccrs, intake, np, plt, xr


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start dask client
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
    ## Load data
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The specific experiment does not matter a great deal. This is the main IAF control run with JRA55 v1.4 forcing
    """)
    return


@app.cell
def _():
    experiment = '01deg_jra55v140_iaf'
    return (experiment,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load the 1D latitude/longitude variables from some ocean data to use them with ice data. The dimensions are renamed to match the required dimension in the ice data
    """)
    return


@app.cell
def _(catalog, experiment):
    _var_search = catalog[experiment].search(variable='area_t')  #area_t is arbitrary, we are only interested in the lat/lon dimension
    _var_search = _var_search.search(path=_var_search.df['path'][0])  #workaround to only load from one file
    ds = _var_search.to_dask()
    return (ds,)


@app.cell
def _(ds):
    yt_ocean = ds['yt_ocean'].rename({'yt_ocean': 'latitude'})
    xt_ocean = ds['xt_ocean'].rename({'xt_ocean': 'longitude'})
    return xt_ocean, yt_ocean


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Both the ocean and the ice output variables have masked curvilinear coordinates, which means there are missing values for the coordinates over land. These variables are not suitable for plotting with [cartopy](https://scitools.org.uk/cartopy/docs/latest/). A full curvilinear grid is available from the CICE model input grid:
    """)
    return


@app.cell
def _(xr):
    ice_grid = xr.open_dataset('/g/data/ik11/inputs/access-om2/input_eee21b65/cice_01deg/grid.nc')
    return (ice_grid,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Extract the full curvilinear coordinates, from the ice grid. Note that these grid coordinates are in radians we need to convert them to degrees. Again, the dimensions are renamed to match the dataset to which they will be added:
    """)
    return


@app.cell
def _(ice_grid, np):
    geolon_t = np.degrees(ice_grid.tlon.rename({'nx': 'longitude', 'ny': 'latitude'}))
    geolat_t = np.degrees(ice_grid.tlat.rename({'nx': 'longitude', 'ny': 'latitude'}))
    return geolat_t, geolon_t


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load an ice variable to use as an example dataset. In this case only the first 12 months for purposes of illustration.
    """)
    return


@app.cell
def _(catalog, experiment):
    _var_search = catalog[experiment].search(variable='aice_m')
    ds_1 = _var_search.to_dask(xarray_combine_by_coords_kwargs=dict(compat='override', data_vars='minimal', coords='minimal'))
    aice_m = ds_1['aice_m'].isel(time=slice(0, 12))
    return (aice_m,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Printing the variable shows it has non-informative dimension names and no CF coordinate variables. As a result when the first time slice is plotted there is no useful units automatically added to the plot.
    """)
    return


@app.cell
def _(aice_m):
    aice_m
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define colormap for plotting. We define the `ice_cmap` method which accepts two options:
    1. `'ice'`: Standard `ice` colormap from cmocean
    2. `'blues'`: Colormap from dark blue (open ocean) to white (100% sea ice cover)
    """)
    return


@app.function
def ice_cmap(colormap):
    """Returns a colormap appropriate for sea ice. Accepts either 'ice' or 'blues'."""

    from palettable.colorbrewer.sequential import Blues_9_r
    import cmocean

    if colormap == 'ice':
        cmap = cmocean.cm.ice
    elif colormap == 'blues':
        cmap = Blues_9_r.mpl_colormap
    else:
        raise ValueError("colormap must be 'ice' or 'blues'")

    cmap.set_bad('lightgrey') # set color for land

    return cmap


@app.cell
def _():
    cmap = ice_cmap('blues')
    cmap
    return (cmap,)


@app.cell
def _(aice_m, cmap):
    aice_m.isel(time=0).plot(aspect=2, size=10, cmap=cmap);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Add spatial coordinates
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To improve usability CF compatible spatial coordinates from the ocean data loaded above can be added to the ice data.

    The unintuitive dimensions are renamed, and importantly match the dimension names chosen for the coordinates. The coordinates loaded above are added to the `DataArray`, and saved in a new variable, `aice_m_coords`.
    """)
    return


@app.cell
def _(aice_m, geolat_t, geolon_t, xt_ocean, yt_ocean):
    aice_m_coords = aice_m.rename({'nj': 'latitude', 
                                   'ni': 'longitude'}).assign_coords({'latitude': yt_ocean, 
                                                                      'longitude': xt_ocean, 
                                                                      'geolat_t': geolat_t, 
                                                                      'geolon_t': geolon_t})
    aice_m_coords
    return (aice_m_coords,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now when the first time slice is plotted there are informative axes as there are now CF compliant dimensions `latitude` and `longitude`.
    """)
    return


@app.cell
def _(aice_m_coords, cmap):
    aice_m_coords.isel(time=0).plot(aspect=2, size=10, cmap=cmap);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Selection using `sel` and `slice`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Also selection using slices of latitude and longitude are easy using these new dimensions. e.g. selecting the Weddell Sea in Antarctica
    """)
    return


@app.cell
def _(aice_m_coords, cmap):
    aice_m_coords.isel(time=0).sel(longitude=slice(-80, 0), latitude=slice(None, -50)).plot(size=10, cmap=cmap);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The same data can also be plotted and projected using `cartopy` which works fine using the 1D `latitude` and `longitude` coordinates as these are correct for all values south of 65N, so all of the Southern Hemisphere.
    """)
    return


@app.cell
def _(aice_m_coords, ccrs, cmap, plt):
    _fig = plt.figure(figsize=(14, 8))
    _ax = plt.axes(projection=ccrs.Orthographic(-40, -90))
    _ax.coastlines()
    _ax.gridlines()
    aice_m_coords.isel(time=0).sel(longitude=slice(-80, 0), latitude=slice(None, -50)).plot(ax=_ax, transform=ccrs.PlateCarree(), cmap=cmap)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Simple `sel` with `slice` can also be used to select areas in the northern hemisphere, but they appear distorted  as this area is in the tripole, so the 1D latitude and longitude variables are not correct
    """)
    return


@app.cell
def _(aice_m_coords, cmap):
    aice_m_coords.isel(time=0).sel(longitude=slice(-80, 80), 
                                   latitude=slice(50, 85)).plot(size=8, aspect=2, cmap=cmap);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If the same selection is plotted in an Orthographic projection with `cartopy` it is obvious that land/sea boundaries are not correct, and artefacts from the tripole are visible
    """)
    return


@app.cell
def _(aice_m_coords, ccrs, cmap, plt):
    _fig = plt.figure(figsize=(18, 8))
    _ax = plt.axes(projection=ccrs.Orthographic(0, 90))
    _ax.coastlines()
    _ax.gridlines()
    aice_m_coords.isel(time=0).sel(longitude=slice(-80, 80), latitude=slice(50, 85)).plot(ax=_ax, cmap=cmap, transform=ccrs.PlateCarree())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Using the true curvilinear coordinates to plot, the artefacts are removed, and the land/sea registration is correct, but the simple `sel` using the 1D coordinates means there are not constant lines of latitude or longitude in the selected data.
    """)
    return


@app.cell
def _(aice_m_coords, ccrs, cmap, plt):
    _fig = plt.figure(figsize=(18, 8))
    _ax = plt.axes(projection=ccrs.Orthographic(0, 90))
    _ax.coastlines()
    _ax.gridlines()
    aice_m_coords.isel(time=0).sel(longitude=slice(-80, 80), latitude=slice(50, 85)).plot(ax=_ax, cmap=cmap, transform=ccrs.PlateCarree(), x='geolon_t', y='geolat_t')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Selection using `where`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To do proper spatial selection with 2D coordinates in the tripole area it is necessary to use the `xarray` [`where`](http://xarray.pydata.org/en/stable/generated/xarray.DataArray.where.html) method, which will mask out the data where the stipulated condition is not met. With `drop=True` coordinate labels with only `False` values are removed.
    """)
    return


@app.cell
def _(aice_m_coords, cmap, geolat_t, geolon_t, plt):
    aice_m_coords.isel(time=0).where((geolon_t >= -80) & 
                                     (geolon_t <= 80) & 
                                     (geolat_t >= 50) & 
                                     (geolat_t <= 85), drop=True).plot(size=8, aspect=2, 
                                                                       x='geolon_t',
                                                                       y='geolat_t', 
                                                                       cmap=cmap)
    plt.xlim([-80, 80])
    plt.ylim([50, 85]);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now when plotted in Orthographic projection with `cartopy` the selection is clearly along lines of constant latitude, and the left hand side selection is a constant longitude.
    """)
    return


@app.cell
def _(aice_m_coords, ccrs, cmap, plt):
    _fig = plt.figure(figsize=(18, 8))
    _ax = plt.axes(projection=ccrs.Orthographic(0, 90))
    _ax.coastlines()
    _ax.gridlines()
    aice_m_coords.isel(time=0).where((aice_m_coords.geolon_t >= -80) & (aice_m_coords.geolon_t <= 80) & (aice_m_coords.geolat_t >= 50) & (aice_m_coords.geolat_t <= 85), drop=True).plot(ax=_ax, transform=ccrs.PlateCarree(), x='geolon_t', y='geolat_t', cmap=cmap)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
