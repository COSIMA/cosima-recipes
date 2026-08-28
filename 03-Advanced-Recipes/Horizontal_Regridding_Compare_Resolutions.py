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
    # Horizontal regridding and comparing different resolutions

    This notebook demonstrates regridding the ACCESS-OM2 output onto a different grid. In this example, regridding model output from all three ACCESS-OM2 resolutions on to a 1-degree longitude-latitude grid with regular spacing.

    **Requirements:** This notebook has been tested using the `conda/analysis3-26.06` module on ARE/gadi

    **Conversion to MOM6:**

    MOM6 uses a different grid to MOM5/ACCESS-OM2, so be aware of the differences when doing regridding of velocity or transport variables which are positioned differently on the grid to MOM5. However, sea surface height also lives on the `h` or tracer grid, so this recipe could be converted to MOM6 with the following variable changes.

    | MOM5 variable | MOM6 variable |
    | ---- | ---- |
    | `geolat_t` | `geolat`|
    | `geolon_t` | `geolon`|
    | `geolat_c` | `geolat_c`|
    | `geolon_c` | `geolon_c`|
    | `xt_ocean` | `xh` |
    | `yt_ocean` | `yh` |
    | `sea_level`| `zos` |

    **Firstly,** load in the requisite libraries:
    """)
    return


@app.cell
def _():
    import intake

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs

    import xarray as xr

    xr.set_options(keep_attrs=True)

    from dask.distributed import Client

    import xesmf

    return Client, ccrs, intake, plt, xesmf, xr


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load a `dask` client. This is not required for small regridding jobs, and does not affect the speed of generating the regridding weights, but may improve speed, or reduce memory overhead, when regridding large datasets with, for example, large time dimensions.
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
    Load a catalog; here we load the default ACCESS-NRI catalog.
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Load raw data

    We load some raw data from ACCESS-OM2 models. In particular, we load here the 2 years of monthly sea-surface height from the inter-annually forced ocean model runs at three different resolutions. These experiments are part of the default database and are called:

    - `1deg_jra55_iaf_omip2_cycle6` for ACCESS-OM2 1$^\circ$ degree,
    - `025deg_jra55_iaf_omip2_cycle6` for ACCESS-OM2 0.25$^\circ$ degree,
    - `01deg_jra55v140_iaf_cycle4` for ACCESS-OM2 0.1$^\circ$ degree.

    We use the `intake` catalog to load our variables.

    We make sure to assign the correct tripolar coordinates as `coords`. Since sea-surface height is lives on `t`-cells, we add `geolon_t` and `geolat_t`. We also rename them to `longitude` and `latitude` to ease our life further down (`xesmf` package that we will use for regridding automatically searches for coordinates named `longitude` and `latitude`.)

    After we load the data we rechunk them according to how the regridder's needs; read further down for more details on this.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First, we load the grid parameters for each resolution.
    """)
    return


@app.cell
def _(intake, xr):
    grid1 = intake.cat.access_nri["1deg_jra55_iaf_omip2_cycle6"].search(
        variable = ["geolat_t", "geolon_t", "geolat_c", "geolon_c"], frequency = "fx").to_dask()
    grid025 = intake.cat.access_nri["025deg_jra55_iaf_omip2_cycle6"].search(
        variable = ["geolat_t", "geolon_t", "geolat_c", "geolon_c"], frequency = "fx").to_dask()

    # for the 0.1deg model they are in different files
    geolat_t01 = intake.cat.access_nri["01deg_jra55v140_iaf_cycle4"].search(
        variable = "geolat_t", frequency = "fx").to_dask()
    geolon_t01 = intake.cat.access_nri["01deg_jra55v140_iaf_cycle4"].search(
        variable = "geolon_t", frequency = "fx").to_dask()
    geolat_c01 = intake.cat.access_nri["01deg_jra55v140_iaf_cycle4"].search(
        variable = "geolat_c", frequency = "fx").to_dask()
    geolon_c01 = intake.cat.access_nri["01deg_jra55v140_iaf_cycle4"].search(
        variable = "geolon_c", frequency = "fx").to_dask()
    grid010 = xr.merge([geolat_t01,geolon_t01,geolat_c01,geolon_c01])
    return grid010, grid025, grid1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, we load the sea level variable for each resolution.
    """)
    return


@app.cell
def _(catalog, grid1):
    _ds = catalog['1deg_jra55_iaf_omip2_cycle6'].search(variable='sea_level', frequency='1mon').to_dask()
    ssh_1 = _ds['sea_level'].sel(time=slice('2000-01-01', '2001-12-31')).chunk({'time': 'auto', 'xt_ocean': -1, 'yt_ocean': -1})
    ssh_1 = ssh_1.assign_coords({'geolat_t': grid1.geolat_t, 'geolon_t': grid1.geolon_t})
    ssh_1 = ssh_1.rename({'xt_ocean': 'x', 'yt_ocean': 'y'})
    ssh_1
    return (ssh_1,)


@app.cell
def _(catalog, grid025):
    _ds = catalog['025deg_jra55_iaf_omip2_cycle6'].search(variable='sea_level', frequency='1mon').to_dask()
    ssh_025 = _ds['sea_level'].sel(time=slice('2000-01-01', '2001-12-31')).chunk({'time': 'auto', 'xt_ocean': -1, 'yt_ocean': -1})
    ssh_025 = ssh_025.assign_coords({'geolat_t': grid025.geolat_t, 'geolon_t': grid025.geolon_t})
    ssh_025 = ssh_025.rename({'xt_ocean': 'x', 'yt_ocean': 'y'})
    ssh_025
    return (ssh_025,)


@app.cell
def _(catalog, grid010):
    _ds = catalog['01deg_jra55v140_iaf_cycle4'].search(variable='sea_level', frequency='1mon').to_dask()
    ssh_010 = _ds['sea_level'].sel(time=slice('2000-01-01', '2001-12-31')).chunk({'time': 'auto', 'xt_ocean': -1, 'yt_ocean': -1})
    ssh_010 = ssh_010.assign_coords({'geolat_t': grid010.geolat_t, 'geolon_t': grid010.geolon_t})
    ssh_010 = ssh_010.rename({'xt_ocean': 'x', 'yt_ocean': 'y'})
    ssh_010
    return (ssh_010,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Regrid using `xesmf`

    We regrid all output onto a regular lat-lon grid with 1 degree lateral resolution. First we construct the `dataset` with the coordinates that we want to regrid onto.
    """)
    return


@app.cell
def _(xesmf):
    ds_out = xesmf.util.grid_global(1, 1)

    # lon_b and lat_b are generated by xesmf and represent the edges of the
    # target grid, but is not needed in this recipe

    ds_out = ds_out.drop_vars({"lon_b", "lat_b"})

    # we shift our longitude grid range from [-180, 180] to [-280, 80]
    # this is only for visualisation purposes so that the grid's seam falls in
    # the middle of the Indian Ocean rather than in the middle of the Pacific Ocean
    ds_out = ds_out.assign_coords({"lon": ds_out.lon - 100.0})

    ds_out = ds_out.rename({"lon": "longitude", "lat": "latitude"})
    ds_out
    return (ds_out,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's have a look how the original ACCESS-OM2 1$^\circ$ grid (with the two poles in the Arctic region, north of 65$^\circ$N) compares with the "sane" latitude-longitude 1$^\circ$ grid.
    """)
    return


@app.cell
def _(ccrs, ds_out, plt, ssh_1):
    _projection = ccrs.cartopy.crs.Orthographic(central_longitude=0.0, central_latitude=90)
    _fig, _axes = plt.subplots(ncols=2, subplot_kw={'projection': _projection}, figsize=(14, 8))
    _axes[0].scatter(ssh_1.geolon_t, ssh_1.geolat_t, s=0.1, transform=ccrs.PlateCarree())
    _axes[0].set_title('original ACCESS-OM2 1deg grid', fontsize=18)
    _axes[1].scatter(ds_out['longitude'], ds_out['latitude'], s=0.1, transform=ccrs.PlateCarree())
    # plot grid locations
    _axes[1].set_title('1deg lat-lon grid', fontsize=18)
    for _ax in _axes:
        _ax.coastlines()
        _ax.set_extent([-180, 180, 55, 90], crs=ccrs.PlateCarree())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To regrid our fields we need to construct the three regridders for the three different resolutions using `xesmf.Regridder()`. The `xesmf.Regridder()` function takes as input two datasets, one that includes the original grid and one that includes the grids we need to regrid on. (Type `?xesmf.Regridder` for the function's docstring.)

    The names of the coordinates need to follow CF-convetions.
    We also make sure to drop the 1D coords `x` and `y` to **force** the regridder to use the 2D arrays `geolon_c` and `geolat_c`.

    **Note**: The 0.10 degree `regridder_010degACCESSOM2_1deg` below should take ~3-4 minutes to compute.
    """)
    return


@app.cell
def _(ds_out, ssh_1, xesmf):
    # magic command not supported in marimo; please file an issue to add support
    # %%time

    regridder_1degACCESSOM2_1deg = xesmf.Regridder(
        ssh_1.drop_vars({"x", "y"}),
        ds_out,
        "bilinear",
        periodic=True,
        filename="bilinear_tracer_weights_in1degACCESSOM2_out1deg.nc",
    )
    regridder_1degACCESSOM2_1deg
    return (regridder_1degACCESSOM2_1deg,)


@app.cell
def _(ds_out, ssh_025, xesmf):
    # magic command not supported in marimo; please file an issue to add support
    # %%time

    regridder_025degACCESSOM2_1deg = xesmf.Regridder(
        ssh_025.drop_vars({"x", "y"}),
        ds_out,
        "bilinear",
        periodic=True,
        filename="bilinear_tracer_weights_in025degACCESSOM2_out1deg.nc",
    )
    regridder_025degACCESSOM2_1deg
    return (regridder_025degACCESSOM2_1deg,)


@app.cell
def _(ds_out, ssh_010, xesmf):
    # magic command not supported in marimo; please file an issue to add support
    # %%time

    regridder_010degACCESSOM2_1deg = xesmf.Regridder(
        ssh_010.drop_vars({"x", "y"}),
        ds_out,
        "bilinear",
        periodic=True,
        filename="bilinear_tracer_weights_in010degACCESSOM2_out1deg.nc",
    )
    regridder_010degACCESSOM2_1deg
    return (regridder_010degACCESSOM2_1deg,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Note

    For large grids (e.g., to regrid from a 0.10$^\circ$ grid to a 0.20$^\circ$), it might take a while to compute the re-grid weights. But, once you compute the weights, you can construct a regridder using the already-computed weights from a netCDF file by providing with the `reuse_weights = True` argument, e.g.,

    ```python
    regridder = xesmf.Regridder(dataset_in, dataset_out, 'bilinear', periodic=True,
                                filename='weights_file.nc', reuse_weights=True)
    ```
    or to automatically recalculate the weights file only in case it doesn't already exist, do
    ```python
    import os

    regridder = xesmf.Regridder(dataset_in, dataset_out, 'bilinear', periodic=True,
                                filename='weights_file.nc',
                                reuse_weights=os.path.exists('weights_file.nc'))
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Let's regrid our output

    Now we use the regridders we constructed above to regrid our output. Note that the dimensions we are applying the re-gridding can't be chunked, so when we opened the dataset, we set the chunks sizes to be the full size of x and y. The `time` axis can be chunked --- for big datasets make sure that you rechunk `time` if needed so you don't end up with *huge* chunk sizes. That is precisely why we used:

    ```python
    .chunk({'time': 'auto', 'longitude': -1, 'latitude': -1})
    ```

    to ensure this.

    Note also that for the regridded data arrays, we add back the longitude/latitude values on coords `x`/`y` respectively to make our lives easier with plotting later on.
    """)
    return


@app.cell
def _(ds_out, regridder_1degACCESSOM2_1deg, ssh_1):
    ssh_1_regridded = regridder_1degACCESSOM2_1deg(ssh_1)
    ssh_1_regridded = ssh_1_regridded.drop_vars(["longitude", "latitude"])
    ssh_1_regridded = ssh_1_regridded.assign_coords(
        {"x": ds_out.longitude.isel(y=0), "y": ds_out.latitude.isel(x=0)}
    )
    ssh_1_regridded = ssh_1_regridded.rename({"x": "longitude", "y": "latitude"})

    ssh_1_regridded
    return (ssh_1_regridded,)


@app.cell
def _(ds_out, regridder_025degACCESSOM2_1deg, ssh_025):
    ssh_025_regridded = regridder_025degACCESSOM2_1deg(ssh_025)
    ssh_025_regridded = ssh_025_regridded.drop_vars(["longitude", "latitude"])
    ssh_025_regridded = ssh_025_regridded.assign_coords(
        {"x": ds_out.longitude.isel(y=0), "y": ds_out.latitude.isel(x=0)}
    )
    ssh_025_regridded = ssh_025_regridded.rename({"x": "longitude", "y": "latitude"})
    ssh_025_regridded
    return (ssh_025_regridded,)


@app.cell
def _(ds_out, regridder_010degACCESSOM2_1deg, ssh_010):
    ssh_010_regridded = regridder_010degACCESSOM2_1deg(ssh_010)
    ssh_010_regridded = ssh_010_regridded.drop_vars(["longitude", "latitude"])
    ssh_010_regridded = ssh_010_regridded.assign_coords(
        {"x": ds_out.longitude.isel(y=0), "y": ds_out.latitude.isel(x=0)}
    )
    ssh_010_regridded = ssh_010_regridded.rename({"x": "longitude", "y": "latitude"})
    ssh_010_regridded
    return (ssh_010_regridded,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Plotting time
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can plot the regridded fields, slicing as we like using `longitude` and `latitude` coordinates. Here's a comparisson of monthly-mean snapshots for sea-surface height in the North Pacific. Notice how things look "normal" north of 65$^\circ$N where the model's grid has the tripolar complications!
    """)
    return


@app.cell
def _(ccrs, plt, ssh_010_regridded, ssh_025_regridded, ssh_1_regridded):
    _projection = ccrs.cartopy.crs.EqualEarth(central_longitude=180.0)
    _fig, _axes = plt.subplots(nrows=3, subplot_kw={'projection': _projection}, figsize=(12, 15))
    for _ax in _axes:
        _ax.coastlines()
    ssh_1_regridded.isel(time=0).sel({'longitude': slice(-250, -80), 'latitude': slice(10, 90)}).plot(ax=_axes[0], transform=ccrs.PlateCarree(), extend='both', vmin=-1, vmax=1, cmap='RdBu_r')
    _axes[0].set_title('ACCESS-OM2-1 regridded on 1deg lat-lon', fontsize=18)
    ssh_025_regridded.isel(time=0).sel({'longitude': slice(-250, -80), 'latitude': slice(10, 90)}).plot(ax=_axes[1], transform=ccrs.PlateCarree(), extend='both', vmin=-1, vmax=1, cmap='RdBu_r')
    _axes[1].set_title('ACCESS-OM2-025 regridded on 1deg lat-lon', fontsize=18)
    ssh_010_regridded.isel(time=0).sel({'longitude': slice(-250, -80), 'latitude': slice(10, 90)}).plot(ax=_axes[2], transform=ccrs.PlateCarree(), extend='both', vmin=-1, vmax=1, cmap='RdBu_r')
    _axes[2].set_title('ACCESS-OM2-010 regridded on 1deg lat-lon', fontsize=18)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Another thing we can do now that we have everything on the same grid is to compute difference between fields from different model resolutions.
    """)
    return


@app.cell
def _(ccrs, plt, ssh_010_regridded, ssh_1_regridded):
    plt.figure(figsize=(12, 4))
    _ax = plt.axes(projection=ccrs.cartopy.crs.EqualEarth(central_longitude=180.0))
    (ssh_010_regridded.isel(time=0) - ssh_1_regridded.isel(time=0)).sel({'longitude': slice(-250, -80), 'latitude': slice(10, 90)}).plot(ax=_ax, transform=ccrs.PlateCarree(), extend='both', vmin=-1, vmax=1, cmap='RdBu_r')
    _ax.coastlines()
    plt.title('sea surface height difference: 0.10deg - 1deg', fontsize=18)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Further examples

    The example that [compares sea ice observations with model outputs](https://cosima-recipes.readthedocs.io/en/latest/03-Advanced-Recipes/Sea_Ice_Area_Concentration_Volume_with_Obs.html) and also the "Regridders" section of the ["Ice maps analysis" notebook](https://nbviewer.jupyter.org/github/aekiss/ice_analysis/blob/main/ice_maps.ipynb#Regridders) include examples of functions that generate functions to regrid between ACCESS-OM2 resolutions and from various other datasets (JRA55, GIOMAS, and NSIDC) to the three ACCESS-OM2 resolutions. These regridder functions automatically save and reuse weights.
    """)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
