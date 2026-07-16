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
    # Extract variables at bottom of ocean: an example with Age

    This notebook shows a simple example of plotting ocean Ideal Age. Ideal Age is a fictitious tracer which is set to zero in the surface grid-cell every timestep, and is aged by 1 year per year otherwise. It is a useful proxy for nutrients, such as carbon or oxygen (but not an exact analogue).

    One of the interesting aspects of age is that we can use it to show pathways of the densest water in the ocean by plotting a map of age in the lowest grid cell. This plot requires a couple of tricks to extract information from the lowest cell.

    Compute times were calculated using the (24 cpus, 95 Gb mem) Jupyter Lab on NCI's Gadi with conda environment analysis3-25.07 or above.

    **Conversion for MOM6:** This notebook uses ACCESS-OM2 (MOM5) data. To convert this notebook for extracting tracer variables at the bottom of the ocean with ACCESS-OM3 or other MOM6 models, there are some variable names that would need to be changed: \
        - we would replace ``st_ocean`` with the vertical coordinate of MOM6 data which is usually ``z_l`` \
        - we would replace ``ht`` with the depth variable ``deptho`` \
        - the ideal age variable in MOM6 is ``agessc``
    """)
    return


@app.cell
def _():
    import intake
    import matplotlib.pyplot as plt
    import xarray as xr
    import numpy as np

    import cartopy.crs as ccrs
    import cmocean as cm

    from dask.distributed import Client

    return Client, ccrs, cm, intake, np, plt, xr


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Add a database session. No database file has been specified so it will use the default database that indexes a number of COSIMA datasets
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, let's set the experiment and time interval, and average ideal age over a year.
    """)
    return


@app.cell
def _(catalog):
    experiment = '01deg_jra55v13_ryf9091'
    variable = 'age_global'
    start_time = '2099-01-01'
    end_time   = '2099-12-31'

    ds_age = catalog[experiment].search(variable=variable, frequency='1mon').to_dask()
    age = ds_age[variable].sel(time=slice(start_time, end_time))
    age
    return age, experiment


@app.cell
def _(age):
    # Perhaps, there's a better way to chunk the variable but this works fine, too
    chunks_dict = {'xt_ocean': 360, 'yt_ocean': 300, 'st_ocean': 75, 'time': '250Mb'}
    age_1 = age.chunk(chunks_dict)
    age_1
    return (age_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The age variable is a 4D variable. There are a number of ways to extract the value at the bottom of the ocean. This notebook outlines two ways this can be achieved: *(i)* using masking and using *(ii)* indexing.

    In this case masking is much slower than indexing, but for some use cases this has been the opposite. The masking approach has the benefit of not requiring the depth grid information.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## I. Masking approach
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create a mask of all the bottom cells. Can achieve this by taking the data, shift it up one cell in the vertical grid, find all non-NAN cells, and then negate this mask. Then mask the same data with with this mask, which will select out only the lowest level of non-NAN values in the data.

    In a second step turn it into a boolean array for neatness.
    """)
    return


@app.cell
def _(age_1, np):
    bottom_mask = age_1.isel(time=1).where(~np.isfinite(age_1.isel(time=1).shift({'st_ocean': -1})))
    bottom_mask = ~np.isnan(bottom_mask)
    bottom_mask
    return (bottom_mask,)


@app.cell
def _(age_1, bottom_mask):
    _bottom_age = age_1.where(bottom_mask).sum(dim='st_ocean', skipna=True, min_count=1)
    bottom_age_mean = _bottom_age.mean('time').compute()
    bottom_age_mean
    return (bottom_age_mean,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load some things we need for plotting. Bathymetry for plotting the land mask, and lat/lon:
    """)
    return


@app.cell
def _(catalog, experiment, np, xr):
    bathymetry = catalog[experiment].search(variable='ht',
                                            frequency='fx').to_dask()['ht']

    land = xr.where(np.isnan(bathymetry.rename('land')), 1, np.nan)
    land
    return (land,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Although, ``ht`` loaded from ``intake`` already has ``geolon_t`` and ``geolat_t`` coordinates, we can't not use them for plotting because they contain NaN values over the continents. So we still have to load geolon_t & geolat_t from the grid file and assign them to ``land`` and ``bottom_age_mean`` prior to producing a figure.
    """)
    return


@app.cell
def _(xr):
    ds = xr.open_dataset("/g/data/ik11/grids/ocean_grid_01.nc")
    ds = ds.rename(
        {
            "grid_x_C": "xu_ocean",
            "grid_y_C": "yu_ocean",
            "grid_x_T": "xt_ocean",
            "grid_y_T": "yt_ocean",
        }
    )
    geolon_t = ds.geolon_t
    geolat_t = ds.geolat_t
    return geolat_t, geolon_t


@app.cell
def _(bottom_age_mean, geolat_t, geolon_t, land):
    land_1 = land.drop_vars(['geolon_t', 'geolat_t'])
    land_1 = land_1.assign_coords({'geolon_t': geolon_t, 'geolat_t': geolat_t})
    bottom_age_mean_1 = bottom_age_mean.assign_coords({'geolon_t': geolon_t, 'geolat_t': geolat_t})
    return bottom_age_mean_1, land_1


@app.cell
def _(bottom_age_mean_1, ccrs, cm, land_1, plt):
    _fig = plt.figure(figsize=(10, 6))
    _ax = plt.axes(projection=ccrs.Robinson(central_longitude=-100))
    _gl = _ax.gridlines(draw_labels=True, linestyle='--', color='grey', x_inline=False, y_inline=False)
    _ax.spines['geo'].set_visible(True)
    _gl.xlabel_style = {'size': 8}
    _gl.ylabel_style = {'size': 8}
    land_1.plot.contourf(ax=_ax, x='geolon_t', y='geolat_t', colors='grey', zorder=2, transform=ccrs.PlateCarree(), add_colorbar=False)
    land_1.fillna(0).plot.contour(ax=_ax, x='geolon_t', y='geolat_t', colors='k', levels=[0, 1], transform=ccrs.PlateCarree(), add_colorbar=False, linewidths=0.5)
    bottom_age_mean_1.plot.contourf(ax=_ax, x='geolon_t', y='geolat_t', cmap=cm.cm.matter, vmin=60, vmax=200, transform=ccrs.PlateCarree(), levels=8, cbar_kwargs={'label': 'Age (yrs)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    plt.title('Ocean Bottom Age')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## II. Indexing approach
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here we grab the `kmt` variable out of `ocean_grid.nc`. The `kmt` variable tells us the lowest cell which is active at each $(x, y)$ location.
    """)
    return


@app.cell
def _(catalog, experiment):
    kmt = catalog[experiment].search(variable='kmt',
                                     frequency='fx').to_dask()['kmt']
    kmt = kmt.fillna(1.0).astype(int) - 1
    kmt.load()
    return (kmt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Provided that `kmt` is loaded, `xarray` is smart enough to figure out what this line means, and extracts a 2-D field of bottom age for us.
    """)
    return


@app.cell
def _(age_1, kmt):
    _bottom_age = age_1.mean('time').isel(st_ocean=kmt)
    bottom_age_mean_2 = _bottom_age.compute()
    return (bottom_age_mean_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Assign ``geolon_t`` and ``geolat_t`` from the grid file to ``bottom_age_mean``
    """)
    return


@app.cell
def _(bottom_age_mean_2, geolat_t, geolon_t):
    bottom_age_mean_3 = bottom_age_mean_2.assign_coords({'geolon_t': geolon_t, 'geolat_t': geolat_t})
    return (bottom_age_mean_3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And here is the plot:
    """)
    return


@app.cell
def _(bottom_age_mean_3, ccrs, cm, land_1, plt):
    _fig = plt.figure(figsize=(10, 6))
    _ax = plt.axes(projection=ccrs.Robinson(central_longitude=-100))
    _gl = _ax.gridlines(draw_labels=True, linestyle='--', color='grey', x_inline=False, y_inline=False)
    _ax.spines['geo'].set_visible(True)
    _gl.xlabel_style = {'size': 8}
    _gl.ylabel_style = {'size': 8}
    land_1.plot.contourf(ax=_ax, x='geolon_t', y='geolat_t', colors='grey', zorder=2, transform=ccrs.PlateCarree(), add_colorbar=False)
    land_1.fillna(0).plot.contour(ax=_ax, x='geolon_t', y='geolat_t', colors='k', levels=[0, 1], transform=ccrs.PlateCarree(), add_colorbar=False, linewidths=0.5)
    bottom_age_mean_3.plot.contourf(ax=_ax, x='geolon_t', y='geolat_t', cmap=cm.cm.matter, vmin=60, vmax=200, levels=8, transform=ccrs.PlateCarree(), cbar_kwargs={'label': 'Age (yrs)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    plt.title('Ocean Bottom Age')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Some remarks
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A few things to note here:
    * The continental shelves are all young - this is just because they are shallow.
    * The North Atlantic is also relatively young, due to formation of NADW. Note that both the Deep Western Boundary Currents and the Mid-Atlantic Ridge both sustain southward transport of this young water.
    * A signal following AABW pathways (northwards at the western boundaries) shows slightly younger water in these regions, but it has mixed somewhat with older water above.
    * Even after 200 years, the water in the NE Pacific has not experienced any ventilation...
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Notes on performance
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The indexing method requires the data to be loaded into memory and appears faster than it actually is if this isn't factored in. Calculations with large datasets that do not fit within memory will struggle in this case.

    The indexing method does not perform well in a `dask` workflow where lazy loading is being used.

    The masking approach does not suffer from these limitations and when in doubt should be the preferred method. It also has the advantage of not requiring the grid data.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To illustrate this: a single month of bottom age from the original data using masking
    """)
    return


@app.cell
def _(age_1, bottom_mask):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    age_1.isel(time=1).where(bottom_mask).sum(dim='st_ocean').compute()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The same with indexing (different month to ensure no caching effects) is significantly slower
    """)
    return


@app.cell
def _(age_1, kmt):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    age_1.isel(time=3).isel(st_ocean=kmt).compute()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    It is much faster to preload the data and then index it, but this does rely on their being sufficient memory
    """)
    return


@app.cell
def _(age_1):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    myage = age_1.isel(time=4).load()
    return (myage,)


@app.cell
def _(kmt, myage):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    myage.isel(st_ocean=kmt).compute()
    return


if __name__ == "__main__":
    app.run()
