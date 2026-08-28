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
    # Cross-slope section

    ### Background

    This recipe computes a cross-section across the Antarctic continental slope, as defined by the 1000 m isobath. We will do the cross-section using an example field through the gridded data of ACCESS-OM2-01 using the  `metpy.interpolate.cross_section` function. For more information on how `metpy` works refer to their [documentation](https://unidata.github.io/MetPy/latest/examples/cross_section.html#sphx-glr-examples-cross-section-py). It is a very useful library!

    ---

    ### Requirements

    This recipe works with MOM5 diagnostics from ACCESS-OM2-01. For adaptation to MOM6 the following diagnostics will be useful:

    | MOM5 diagnostic (x-coord, y-coord) | MOM6 diagnostic (x-coord,y-coord)|
    |---|---|
    |`pot_rho_2 (xt_ocean,yt_ocean)` | `rhopot2(xh,yh)`|
    |`pot_temp (xt_ocean,yt_ocean)` | `thetao(xh,yh)`|
    |`ht (xt_ocean,yt_ocean)` | `deptho(xh,yh)`|
    |`hu (xu_ocean,yu_ocean)` | N/A |
    |`dxt (xt_ocean,yt_ocean)` | `dxt(xh,yh)`|

    When calculating the normal directions, take into account that the MOM6 diagnostics might not be in the same grid as this recipe.
    """)
    return


@app.cell
def _():
    import cartopy.crs as ccrs
    import cmocean as cm
    import intake
    import matplotlib.path as mpath
    import matplotlib.pyplot as plt
    import numpy as np
    import xarray as xr
    import xgcm
    from dask.distributed import Client
    from metpy.interpolate import cross_section

    from matplotlib.colors import BoundaryNorm
    from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

    return Client, cm, cross_section, intake, np, plt, xgcm, xr


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Open the intake catalog and select experiment:
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    experiment = '01deg_jra55v13_ryf9091'
    return catalog, experiment


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Load data

    We will do a cross section of potential temperature with potential density contours, we will open only 5 years of data (from 1950-1955). Let's also load bathymetry and grid distances data, which we will need to get the cross-slope direction
    """)
    return


@app.cell
def _(catalog, experiment):
    bathymetry = catalog[experiment].search(variable=["ht","hu"],
                                            frequency="fx").to_dask()
    grid_distances = catalog[experiment].search(variable=["dxt", "dyt"],
                                                frequency="fx").to_dask()

    ds = catalog[experiment].search(variable=["pot_rho_2","pot_temp"],
                                    start_date='^195[0-5].*',
                                    frequency="1mon",
                                    variable_cell_methods="time: mean"
                                    ).to_dask()
    ds = ds.mean('time')
    return bathymetry, ds, grid_distances


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In order to do a cross-slope section, we need to find the direction that is normal to the slope (a detailed description can be found in the [Along-slope-velocities](https://github.com/COSIMA/cosima-recipes/blob/main/03-Advanced-Recipes/Along-slope-velocities.ipynb) notebook - in this recipe we take the direction normal to bathymetry, instead of the one along.

    We will use `xgcm` in order to calculate the necessary gradients. Remember that the direction normal $\hat{\eta}$ to topography, $h$, is given by:

    $$
    \hat{\eta} = \partial_x h \; \hat{x} \; , \;\; \partial_y h \; \hat{y}
    $$
    """)
    return


@app.cell
def _(bathymetry, grid_distances, np, xgcm):
    bathymetry.coords['xt_ocean'].attrs.update(axis='X')
    bathymetry.coords['xu_ocean'].attrs.update(axis='X', c_grid_axis_shift=0.5)
    bathymetry.coords['yt_ocean'].attrs.update(axis='Y')
    bathymetry.coords['yu_ocean'].attrs.update(axis='Y', c_grid_axis_shift=0.5)

    # Create grid object
    grid = xgcm.Grid(bathymetry, periodic=['X'])

    # Calculate the gradients
    dxht = grid.interp(grid.diff(bathymetry["hu"], 'X'), "Y") / grid_distances['dxt']
    dyht = grid.interp(grid.diff(bathymetry["hu"], 'Y'), "X") / grid_distances['dyt']

    # Normalise to get the direction
    n_x = dxht / np.sqrt(dxht**2 + dyht**2)
    n_y = dyht / np.sqrt(dxht**2 + dyht**2)
    return n_x, n_y


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's open the Antarctic slope file, which marks the grid-cells belonging to the slope (1000 m isobath):
    """)
    return


@app.cell
def _(xr):
    ant_slope = xr.open_dataset('/g/data/ik11/grids/Antarctic_slope_contour_1000m_MOM6_01deg.nc')['contour_masked_above']
    ant_slope = ant_slope.rename({'xh':'xt_ocean','yh':'yt_ocean'})

    ant_slope.plot(figsize=(10,3));
    return (ant_slope,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As you can see, everything in the open ocean is <0, and points along the slope are indexed from zero to 4475.

    Let's select a something on the Antarctic peninsula.
    """)
    return


@app.cell
def _(ant_slope, np):
    np.where(ant_slope==2422)
    return


@app.cell
def _(ant_slope, np):
    slope_lat_idx = np.where(ant_slope==2422)[0][0]
    slope_lon_idx = np.where(ant_slope==2422)[1][0]
    return slope_lat_idx, slope_lon_idx


@app.cell
def _(ant_slope, plt, slope_lat_idx, slope_lon_idx):
    ant_slope.plot(figsize=(5,3))
    plt.scatter(ant_slope['xt_ocean'][slope_lon_idx], ant_slope['yt_ocean'][slope_lat_idx], color='m');
    plt.xlim(-100,-50)
    plt.ylim(-70,-60);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's look at what the direction normal to the Antarctic slope at that point is:
    """)
    return


@app.cell
def _(n_x, slope_lat_idx, slope_lon_idx):
    n_x.isel(yt_ocean=slope_lat_idx, xt_ocean=slope_lon_idx).values
    return


@app.cell
def _(n_y, slope_lat_idx, slope_lon_idx):
    n_y.isel(yt_ocean=slope_lat_idx, xt_ocean=slope_lon_idx).values
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can use these directions to select our starting and ending latitude, longitude coordinates to feed `metpy` for the cross-section.
    """)
    return


@app.cell
def _(ant_slope, n_x, n_y, slope_lat_idx, slope_lon_idx):
    # Points at the slope
    slope_lon = ant_slope['xt_ocean'][slope_lon_idx].item()
    slope_lat = ant_slope['yt_ocean'][slope_lat_idx].item()

    # Points on the shelf
    shelf_lon = slope_lon - 3*n_x.isel(yt_ocean=slope_lat_idx, xt_ocean=slope_lon_idx).values
    shelf_lat = slope_lat - 3*n_y.isel(yt_ocean=slope_lat_idx, xt_ocean=slope_lon_idx).values

    # Points off the shelf
    offshelf_lon = slope_lon + 5*n_x.isel(yt_ocean=slope_lat_idx, xt_ocean=slope_lon_idx).values
    offshelf_lat = slope_lat + 5*n_y.isel(yt_ocean=slope_lat_idx, xt_ocean=slope_lon_idx).values
    return (
        offshelf_lat,
        offshelf_lon,
        shelf_lat,
        shelf_lon,
        slope_lat,
        slope_lon,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's check what it looks like:
    """)
    return


@app.cell
def _(
    ant_slope,
    offshelf_lat,
    offshelf_lon,
    plt,
    shelf_lat,
    shelf_lon,
    slope_lat,
    slope_lon,
):
    ant_slope.plot()
    plt.plot([shelf_lon, offshelf_lon], [shelf_lat,offshelf_lat], color='k')
    plt.scatter(slope_lon, slope_lat, color='m');
    plt.scatter(shelf_lon, shelf_lat, color='g')
    plt.scatter(offshelf_lon, offshelf_lat, color='orange')
    plt.xlim(-100,-50)
    plt.ylim(-70,-60);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The black line marks the cross-section that is normal to the slope at the magenta dot. Green and orange dots are the coordinates we will pass on to `metpy`.
    """)
    return


@app.cell
def _(cross_section, ds, offshelf_lat, offshelf_lon, shelf_lat, shelf_lon, xr):
    # Create datasets
    ds_1 = ds.sel(xt_ocean=slice(-100, -50), yt_ocean=slice(-70, -60))
    ds_pot_rho_2 = xr.Dataset({'pot_rho_2': ds_1['pot_rho_2'], 'lat': ds_1.yt_ocean, 'lon': ds_1.xt_ocean})
    ds_pot_temp = xr.Dataset({'pot_temp': ds_1['pot_temp'], 'lat': ds_1.yt_ocean, 'lon': ds_1.xt_ocean})
    ds_pot_rho_2 = ds_pot_rho_2.rename({'xt_ocean': 'x', 'yt_ocean': 'y'})
    # Rename coordinates for metpy
    ds_pot_temp = ds_pot_temp.rename({'xt_ocean': 'x', 'yt_ocean': 'y'})
    potrho2_parsed = ds_pot_rho_2.metpy.parse_cf('pot_rho_2', coordinates={'y': 'y', 'x': 'x'})
    pottemp_parsed = ds_pot_temp.metpy.parse_cf('pot_temp', coordinates={'y': 'y', 'x': 'x'})
    # Parse
    pot_rho_2_section = cross_section(potrho2_parsed, start=(shelf_lat, shelf_lon), end=(offshelf_lat, offshelf_lon), steps=400, interp_type='linear')
    # Do the cross section
    pottemp_section = cross_section(pottemp_parsed, start=(shelf_lat, shelf_lon), end=(offshelf_lat, offshelf_lon), steps=400, interp_type='linear')
    return pot_rho_2_section, pottemp_section


@app.cell
def _(cm, plt, pot_rho_2_section, pottemp_section):
    pottemp_section.plot.contourf(figsize=(8, 5), yincrease=False, levels=21, cmap=cm.cm.thermal)
    _cs = pot_rho_2_section.plot.contour(yincrease=False, levels=[1036.5, 1036.8, 1036.9, 1037, 1037.1], colors=['k'])
    plt.clabel(_cs, _cs.levels, colors='k', inline=True, use_clabeltext=True)
    plt.gca().set_facecolor('grey')
    plt.ylim(4500, None)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note that our x-axis is an "index" - we can replace this with a "distance from isobath" coordinate.
    """)
    return


@app.cell
def _(np, pottemp_section, slope_lat, slope_lon, xr):
    # Radius of the Earth
    Rearth = 6371 # km
    distance = np.empty(400)
    for i in range(400):
        # Difference between points in lat/lon space
        dlon = pottemp_section["x"][i] - slope_lon
        dlat = pottemp_section["y"][i] - slope_lat
    
        distance[i] = Rearth * np.deg2rad(np.sqrt(dlat**2 + (dlon * np.cos(np.deg2rad(np.mean([slope_lat]))))**2))

    distance = xr.DataArray(distance, dims=['index'], coords={'index':pottemp_section['index']})
    return (distance,)


@app.cell
def _(distance, np):
    # Make everything on shelf negative
    np.where(distance==np.min(distance))
    return


@app.cell
def _(distance, xr):
    distance_1 = xr.where(distance['index'] < 147, -distance, distance)
    return (distance_1,)


@app.cell
def _(cm, distance_1, plt, pot_rho_2_section, pottemp_section):
    plt.figure(figsize=(8, 5))
    plt.contourf(distance_1, pottemp_section['st_ocean'], pottemp_section, levels=21, cmap=cm.cm.thermal)
    plt.colorbar().set_label('$\\theta (K)$')
    _cs = plt.contour(distance_1, pot_rho_2_section['st_ocean'], pot_rho_2_section, levels=[1036.5, 1036.8, 1036.9, 1037, 1037.1], colors=['k'])
    plt.clabel(_cs, _cs.levels, colors='k', inline=True, use_clabeltext=True)
    plt.gca().set_facecolor('grey')
    plt.gca().invert_yaxis()
    plt.ylim(4500, None)
    plt.xlabel('Distance from 1000m isobath (km)')
    plt.ylabel('Depth (m)')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note that this interpolation does not account for partial cells at the bottom, which is why the bathymetry looks rough (jagged/large steps).
    """)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
