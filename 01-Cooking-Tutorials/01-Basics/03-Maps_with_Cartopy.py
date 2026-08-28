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
    # Maps with Cartopy

    This tutorial runs through a series of examples that demonstrate how to make maps using data from the Intake Catalog using `cartopy`.

    Note that these examples are just to give you ideas of how you might be able to make nice maps, but you should expect to adjust and modify to your own use case.
    """)
    return


@app.cell
def _():
    from dask.distributed import Client
    import intake

    import matplotlib.pyplot as plt
    import xarray as xr
    import numpy as np

    import cmocean as cm
    import cartopy.crs as ccrs

    return Client, ccrs, cm, intake, np, plt, xr


@app.cell
def _(Client):
    client = Client(threads_per_worker=1)
    client
    return (client,)


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We will use the SST field from a 0.25° resolution ACCESS-OM2 experiment as our sample data. These maps should work with any 2D data.

    To use this recipe with ACCESS-OM3 (MOM6) experiments, you'll need to change the experiment and substitute the diagnostic `sst` for `tos`, noting that `tos` will be in $^{\circ} C$ rather than Kelvin.
    """)
    return


@app.cell
def _(catalog):
    experiment = '025deg_jra55_iaf_omip2_cycle6'
    _ds = catalog[experiment].search(variable='sst', frequency='1mon').to_dask()
    SST = _ds.sst.isel(time=0) - 273.15
    # convert from degrees K to degrees C
    SST
    return SST, experiment


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Vanilla `.plot()`

    You can always make a vanilla plot of this data using `xarray`...
    """)
    return


@app.cell
def _(SST):
    SST.plot();
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ..., but this doesn't look that appealing. Or, let's just make a subjective remark: it doesn't seem publication-worthy. `:)`

    Also, note that there is (objectively) *noticeable* distortion in the Arctic ocean, i.e., north of 65°N. For example, with the current plate-tectonics configuration, Canada does not touch the North Pole as the figure might imply.

    Why is that? The grid that ocean models use diverts from a regular latitude-longitude grid close to the poles, particularly in the Arctic ocean, to avoid the Pole singularity. MOM5 and MOM6 use a grid which replaces the North Pole with two displaced poles: one inside Russia and one inside Canada. That's why often this grid is referred to as "tripolar" grid (South Pole + the two ficticious Poles in Canada and Russia). The coordinates polewards of about 65 degrees become strongly 2D contrary to a latitude-longitude grid where they are not.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Using Cartopy
    Instead, let's plot the same data with cartopy. This example uses the `Robinson` global projection -- but note that key argument in the plot function: `transform=ccrs.PlateCarree()` -- which is needed every time you plot something with cartopy. (Confusingly, you could also use a `PlateCarree` projection, not to be confused with the transformation ...)
    """)
    return


@app.cell
def _(SST, ccrs, cm, plt):
    plt.figure(figsize=(8, 4))
    _ax = plt.axes(projection=ccrs.Robinson())
    SST.plot(ax=_ax, x='xt_ocean', y='yt_ocean', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal)
    _ax.coastlines()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You can see that this looks a little better.

    ## Colouring in the land
    Say, for example, we don't like such a huge colourbar. Also, say we'd prefer the land colour to be something other than white. These details can be dealt with by doing something like the following.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's first colour the land.
    """)
    return


@app.cell
def _():
    import cartopy.feature as cft

    land_50m = cft.NaturalEarthFeature(
        "physical", "land", "50m", edgecolor="black", facecolor="papayawhip", linewidth=0.5
    )
    return (land_50m,)


@app.cell
def _(SST, ccrs, cm, land_50m, plt):
    plt.figure(figsize=(8, 4))
    _ax = plt.axes(projection=ccrs.Robinson())
    SST.plot.pcolormesh(ax=_ax, x='xt_ocean', y='yt_ocean', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal)
    _ax.coastlines(resolution='50m')
    _ax.add_feature(land_50m)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    However, there is still a glitch in this plot -- because data in the region north of 65ᵒN (a.k.a. the "tripole region") is still distorted. This occurs because the 1D coordinates `xt_ocean` and `yt_ocean` are actually incorrect in the tripole region.

    ## Fixing the Arctic region
    Instead, we need to plot with the 2D arrays of (longitude, latitude) locations -- `geolon_t` and `geolat_t` which we save as static data from each run.

    We load `geolon_t` and `geolat_t` and assign these 2D-arrays as coordinates on our data array.
    """)
    return


@app.cell
def _(SST, catalog, experiment):
    _ds = catalog[experiment].search(variable=['geolon_t', 'geolat_t'], frequency='fx').to_dask()
    geolon_t = _ds.geolon_t
    geolat_t = _ds.geolat_t
    SST_1 = SST.assign_coords({'geolon_t': geolon_t, 'geolat_t': geolat_t})
    return (SST_1,)


@app.cell
def _(SST_1, ccrs, cm, land_50m, plt):
    _fig = plt.figure(figsize=(8, 4))
    _ax = plt.axes(projection=ccrs.Robinson())
    _ax.coastlines(resolution='50m')
    _ax.add_feature(land_50m)
    _ax.gridlines(draw_labels={'bottom': True, 'left': True, 'top': False, 'right': False})
    SST_1.plot.contourf(ax=_ax, x='geolon_t', y='geolat_t', levels=33, vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, transform=ccrs.PlateCarree(), cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    plt.title('Sea Surface Temperature')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    OK, so that's a bit better. We also tweaked the colorbar using `cbar_kwargs`.

    But you may have noticed that we had to use `contourf` to make this map: we can't use just `.plot` (which fallsback to `pcolormesh`) in this instance, because `geolon_t` and `geolat_t` we loaded from the model output are masked arrays and `pcolormesh` can't cope with undefined coordinates.
    (To convince yourself try `SST.plot(x='geolon_t', y='geolat_t')`.) Our options here are:

    - Use `pcolor`, noting that this is sometimes very slow;
    - Read the unmasked 2D longitude/latitude coordinates from a premade netCDF file.

    (Note: the coordinates and all ocean variables are masked where there is land to reduce the computations done by the models. For example, we don't need to be computing and updating temperature and velocity values for places in the middle of continents.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    So to demonstrate the last option here we first drop the masked coordinates drom our data array:
    """)
    return


@app.cell
def _(SST_1):
    SST_2 = SST_1.drop_vars(['geolon_t', 'geolat_t'])
    return (SST_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And then load the unmasked ones.
    """)
    return


@app.cell
def _(SST_2, xr):
    # these lon/lat arrays are NOT masked.
    # NB. This is a hack. We would like to improve this.
    geolon_t_1 = xr.open_dataset('/g/data/ik11/grids/ocean_grid_025.nc').geolon_t
    geolat_t_1 = xr.open_dataset('/g/data/ik11/grids/ocean_grid_025.nc').geolat_t
    SST_3 = SST_2.assign_coords({'geolat_t': geolat_t_1, 'geolon_t': geolon_t_1})
    return SST_3, geolat_t_1, geolon_t_1


@app.cell
def _(SST_3, ccrs, cm, land_50m, plt):
    plt.figure(figsize=(8, 4))
    _ax = plt.axes(projection=ccrs.Robinson(central_longitude=-100))
    _ax.coastlines(resolution='50m')
    _ax.add_feature(land_50m)
    _ax.gridlines(draw_labels={'bottom': True, 'left': True, 'top': False, 'right': False})
    SST_3.plot(ax=_ax, x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    plt.title('Sea Surface Temperature')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is about as good as we can get. Note that there are some mismatches between the coastlines in the model and reality, principally around Antarctica and the Canadian Archipelago. Also, note that the `ocean_grid_025.nc` file used here will only work for 0.25° resolution cases - check to see if others are available.

    Now that we have a reliable way of using cartopy to plot this data with `cartopy`, the following examples provide some examples of how to configure and tailor your maps ...
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Mark a region

    Sometimes we want to mark a particular region that our analysis is foccused on. We can do that using `matplotlib.patches`.
    """)
    return


@app.cell
def _(SST_3, ccrs, cm, land_50m, plt):
    import matplotlib.patches as mpatches
    plt.figure(figsize=(8, 4))
    _ax = plt.axes(projection=ccrs.Robinson(central_longitude=-100))
    _ax.coastlines(resolution='50m')
    _ax.add_feature(land_50m)
    _ax.gridlines(draw_labels={'bottom': True, 'left': True, 'top': False, 'right': False})
    SST_3.plot(ax=_ax, x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    plt.title('Sea Surface Temperature')
    _ax.add_patch(mpatches.Rectangle(xy=[-130, -35], width=45, height=40, facecolor='green', edgecolor='black', linewidth=2, alpha=0.8, fill=True, zorder=3, transform=ccrs.PlateCarree()))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Subplots

    It can be a bit tricky to use Cartopy with subplots. Here's an example:
    """)
    return


@app.cell
def _(SST_3, ccrs, cm, land_50m, plt):
    _fig, axes = plt.subplots(ncols=2, subplot_kw={'projection': ccrs.Robinson(central_longitude=-100)}, figsize=(12, 8))
    cbar_kwargs = {'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7}
    SST_3.plot(ax=axes[0], x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, cbar_kwargs=cbar_kwargs)
    SST_3.plot(ax=axes[1], x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.deep, cbar_kwargs=cbar_kwargs)
    import string
    for n, _ax in enumerate(axes):
        _ax.coastlines(resolution='50m')
        _ax.add_feature(land_50m)
        _ax.gridlines(draw_labels={'bottom': True, 'left': True, 'top': False, 'right': False})
        _ax.text(0, 1.02, '(' + string.ascii_lowercase[n] + ')', transform=_ax.transAxes, size=16)
    axes[0].set_title('Sea Surface Temperature')
    axes[1].set_title('Another Sea Surface Temperature')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Projections
    Here are a few interesting projections you can use with `cartopy` that might be useful for other applications. Note that if you decide to use a map region which extends north of 65°N, you should use the 2D coordinte files as per above.
    """)
    return


@app.cell
def _(SST_3, ccrs, cm, plt):
    _projection = ccrs.Orthographic(central_latitude=80, central_longitude=50)
    plt.figure(figsize=(10, 8))
    _ax = plt.axes(projection=_projection)
    _ax.coastlines(resolution='50m')
    _ax.gridlines(draw_labels=True)
    SST_3.plot(x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), vmin=-2, vmax=35, extend='both', cmap=cm.cm.thermal, cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Near-Sided Perspective
    """)
    return


@app.cell
def _(SST_3, ccrs, cm, land_50m, plt):
    _projection = ccrs.NearsidePerspective(central_longitude=165.0, central_latitude=-40.0, satellite_height=2500000)
    plt.figure(figsize=(10, 9))
    _ax = plt.axes(projection=_projection)
    _ax.add_feature(land_50m)
    SST_3.plot(x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### South Polar Stereo
    Note that this plot, by default, shows the entire globe, which undermines the area of the South Pole region. So, to enhance our beloved Southern Ocean we have to cut an area of the figure to focus down on it.
    """)
    return


@app.cell
def _(SST_3, ccrs, cm, land_50m, np, plt):
    _projection = ccrs.SouthPolarStereo()
    plt.figure(figsize=(10, 9))
    _ax = plt.axes(projection=_projection)
    _ax.set_extent([-280, 80, -80, -35], crs=ccrs.PlateCarree())
    _ax.add_feature(land_50m, color=[0.8, 0.8, 0.8])
    _ax.coastlines(resolution='50m')
    _ax.gridlines(draw_labels=True)
    import matplotlib.path as mpath
    theta = np.linspace(0, 2 * np.pi, 100)
    center, radius = ([0.5, 0.5], 0.5)
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    _ax.set_boundary(circle, transform=_ax.transAxes)
    SST_3.plot(x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    return (mpath,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Mercator regional plot
    """)
    return


@app.cell
def _(SST_3, ccrs, cm, land_50m, plt):
    _projection = ccrs.Mercator(central_longitude=0.0, min_latitude=-70.0, max_latitude=-20.0)
    plt.figure(figsize=(10, 5))
    _ax = plt.axes(projection=_projection)
    _ax.set_extent([-100, 50, -70, -20], crs=ccrs.PlateCarree())
    _ax.add_feature(land_50m, color=[0.8, 0.8, 0.8])
    _ax.coastlines(resolution='50m')
    _ax.gridlines(draw_labels={'bottom': True, 'left': True, 'top': False, 'right': False})
    SST_3.plot(x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Sector map

    This map shows a sector of the Southern Ocean. It involves a Stereographic projection and a fairly complicated cutout to set the boundary of the map, but gives a nice result.
    """)
    return


@app.cell
def _(mpath, np):
    def make_boundary_path(longitudes, latitudes):
        """
        Return a path around boundary to create a sector map, then cut it out given
        longitudes and latitudes.
        """

        boundary_path = np.array([longitudes[-1, :], latitudes[-1, :]])
        boundary_path = np.append(
            boundary_path, np.array([longitudes[::-1, -1], latitudes[::-1, -1]]), axis=1
        )
        boundary_path = np.append(
            boundary_path, np.array([longitudes[1, ::-1], latitudes[1, ::-1]]), axis=1
        )
        boundary_path = np.append(
            boundary_path, np.array([longitudes[:, 1], latitudes[:, 1]]), axis=1
        )
        boundary_path = mpath.Path(np.swapaxes(boundary_path, 0, 1))

        return boundary_path

    return (make_boundary_path,)


@app.cell
def _(
    SST_3,
    ccrs,
    cm,
    geolat_t_1,
    geolon_t_1,
    land_50m,
    make_boundary_path,
    plt,
):
    midlon = -40
    maxlon = midlon + 60
    minlon = midlon - 60
    minlat = -75
    maxlat = -30
    midlat = (minlat + maxlat) / 2
    _projection = ccrs.Stereographic(central_longitude=midlon, central_latitude=midlat)
    _fig = plt.figure(figsize=(12, 6.5))
    _ax = plt.axes(projection=_projection)
    lons = geolon_t_1.sel({'xt_ocean': slice(minlon, maxlon), 'yt_ocean': slice(minlat, maxlat)})
    lats = geolat_t_1.sel({'xt_ocean': slice(minlon, maxlon), 'yt_ocean': slice(minlat, maxlat)})
    boundary_path = make_boundary_path(lons, lats)
    _ax.add_feature(land_50m)
    _ax.coastlines(resolution='50m')
    _ax.set_boundary(boundary_path, transform=ccrs.PlateCarree())
    _ax.set_extent([minlon, maxlon, minlat, maxlat], crs=ccrs.PlateCarree())
    _ax.gridlines(draw_labels=True)
    SST_3.plot(x='geolon_t', y='geolat_t', transform=ccrs.PlateCarree(), vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can browse the full range of cartopy's projections in the package's [documentation](https://scitools.org.uk/cartopy/docs/latest).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Use model's land mask

    Notice above, that near Antarctica (e.g., near the peninsula), there are some points where the model does not have sea-surface temperature values. This is particularly evident in the `SouthPolarStereo` projection above. The reason for that is that the coastline used by cartopy isn't exactly the same as the one used by the models. The model mask is very different from the cartopy's land mask, e.g., near Antarctica, due to the differences where the ice shelves are.

    To use the model-specific land mask, first load the bathymetry for your experiment. For MOM5 output, `ht` is the bathymetry on the t grid while `hu` is the bathymetry on the u grid.
    """)
    return


@app.cell
def _(catalog, geolat_t_1, geolon_t_1, np, xr):
    experiment_1 = '025deg_jra55_iaf_omip2_cycle6'
    _ds = catalog[experiment_1].search(variable='ht', frequency='fx').to_dask()
    bathymetry = _ds['ht'].load()
    land = xr.where(np.isnan(bathymetry.rename('land')), 1, np.nan)
    land = land.assign_coords({'geolon_t': geolon_t_1, 'geolat_t': geolat_t_1})
    return (land,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create a land mask for plotting, set land cells to 1 and rest to NaN. This is preferred over `cartopy.feature`, because the land that `cartopy.feature` provides differs from the land that the model uses.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And now plot!
    """)
    return


@app.cell
def _(SST_3, ccrs, cm, land, plt):
    _fig = plt.figure(figsize=(8, 4))
    _ax = plt.axes(projection=ccrs.Robinson(central_longitude=-100))
    _ax.gridlines(draw_labels={'bottom': True, 'left': True, 'top': False, 'right': False})
    land.plot.contourf(ax=_ax, x='geolon_t', y='geolat_t', colors='papayawhip', zorder=2, transform=ccrs.PlateCarree(), add_colorbar=False)
    land.fillna(0).plot.contour(ax=_ax, x='geolon_t', y='geolat_t', colors='k', levels=[0, 1], transform=ccrs.PlateCarree(), add_colorbar=False, linewidths=0.5)
    SST_3.plot.contourf(ax=_ax, x='geolon_t', y='geolat_t', levels=33, vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, transform=ccrs.PlateCarree(), cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    plt.title('Sea Surface Temperature')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### NASA's Blue Marble as Land

    NASA's Blue Marble is much better land compared to a dull plain colour. Let's see how we can add that!
    """)
    return


@app.cell
def _(plt):
    map_path = "/g/data/ik11/grids/BlueMarble.tiff"
    blue_marble = plt.imread(map_path)
    blue_marble_extent = (-180, 180, -90, 90)
    return blue_marble, blue_marble_extent


@app.cell
def _(SST_3, blue_marble, blue_marble_extent, ccrs, cm, plt):
    _fig = plt.figure(figsize=(8, 4))
    _ax = plt.axes(projection=ccrs.Robinson(central_longitude=-100))
    _ax.gridlines(draw_labels={'bottom': True, 'left': True, 'top': False, 'right': False})
    SST_3.plot.contourf(ax=_ax, x='geolon_t', y='geolat_t', levels=33, vmin=-2, vmax=30, extend='both', cmap=cm.cm.thermal, transform=ccrs.PlateCarree(), cbar_kwargs={'label': 'SST (°C)', 'fraction': 0.03, 'aspect': 15, 'shrink': 0.7})
    _ax.imshow(blue_marble, extent=blue_marble_extent, transform=ccrs.PlateCarree(), origin='upper')
    plt.title("Sea Surface Temperature + NASA's Blue Marble")
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
