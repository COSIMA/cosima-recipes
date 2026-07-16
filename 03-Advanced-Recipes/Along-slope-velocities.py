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
    # Along-slope velocity

    This recipe uses the horizontal surface velocity fields and projects them onto the bathymetry to calculate the along-topography component. The recipe works with MOM5, but the diagnostics and information needed to adapt to MOM6 are given below.

    #### Adapting for MOM6

    |Variable | MOM5 diagnostic | Equivalent MOM6 diagnostic |
    |:--------|-----|------|
    | Zonal velocity (m/s) | `u` | `uo` |
    | Meridional velocity (m/s) | `v` | `vo` |
    |Depth (m) | `ht` | `deptho` |

    In MOM5 velocities are calculated in the (north-east) corner of the cells, where the dimension names are `xu_ocean` and `yu_ocean`. In MOM6, velocities are calculated in the eastern face of the cell for `uo` and northern face of the cell for `vo`. To adapt this recipe, an option would be to interpolate first `uo` and `vo` to be in the (north-east) corner, where the dimensions are (`xq`, `yq`).

    There are a few different options for the zonal and meridional lengths of the cells as well, which we can use depending on how we perform the `xgcm` interpolation and differentiation. For more information on grids and `xgcm`, refer to the [xgcm documentation](https://xgcm.readthedocs.io/en/latest/index.html).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MOM5

    Load modules
    """)
    return


@app.cell
def _():
    from dask.distributed import Client
    import numpy as np
    import xarray as xr
    import dask

    import xgcm
    import intake

    # For plotting
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import matplotlib.path as mpath
    import cmocean as cm

    return Client, ccrs, cm, intake, mpath, np, plt, xgcm, xr


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    By default retain metadata after operations. This can retain out-of-date metadata, so some caution is required.
    """)
    return


@app.cell
def _(xr):
    xr.set_options(keep_attrs=True);
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start a cluster with multiple cores
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
    ### Load data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load the ACCESS-NRI Intake Catalog and get the velocity fields and bathymetry information from the selected experiment.

    We will only load one random year within that experiment and from that we'll select the velocities that correspond to the Southern Ocean.
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    experiment = '01deg_jra55v13_ryf9091'

    # Define latitude slices and year to open
    lat_slice  = slice(-80, -59)
    dates_2086 = '2086.*'
    return catalog, dates_2086, experiment, lat_slice


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First load bathymetry
    """)
    return


@app.cell
def _(catalog, experiment, lat_slice):
    hu_ds = catalog[experiment].search(variable='hu', frequency='fx').to_dask()

    # Select latitude slice 
    hu_ds = hu_ds.sel(yu_ocean=lat_slice)
    hu_ds
    return (hu_ds,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we want to load the velocity fields (we will be working with surface velocities only). We load monthly averages with chunks set to automatic, which is a good way to go unless we are sure how we want to chunk things.
    """)
    return


@app.cell
def _(catalog, dates_2086, experiment, lat_slice):
    ds = catalog[experiment].search(variable=['u', 'v'], 
                                    frequency='1mon',
                                    start_date=dates_2086).to_dask(xarray_open_kwargs={ "chunks": "auto",})

    # Select the slice we wanted and the surface level
    ds = ds.sel(yu_ocean=lat_slice).sel(st_ocean=0, method='nearest')
    uv_ds = ds.mean(dim='time')
    uv_ds
    return (uv_ds,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load grid information (zonal and meridional cell lengths). There's information for the t-cells and the u-cells.
    """)
    return


@app.cell
def _(catalog, experiment, lat_slice):
    grid_ds = catalog[experiment].search(variable=['dxt', 'dyt', 'dxu', 'dyu'], frequency='fx').to_dask()
    grid_ds = grid_ds.sel(yt_ocean=lat_slice, yu_ocean=lat_slice)
    grid_ds
    return (grid_ds,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Along-slope velocity

    We calculate the along-slope velocity component by projecting the velocity field to the tangent vector, $u_{\rm along} = \boldsymbol{u \cdot \hat{t}}$, and the cross-slope component by projecting to the normal vector, $v_{\rm cross} = \boldsymbol{u \cdot \hat{n}}$. The schematic below defines the unit normal normal and tangent vectors for a given bathymetric contour, $\boldsymbol{n}$ and $\boldsymbol{t}$ respectively.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <img src="images/topographic_gradient_sketch.png" alt="schematic" width="850"/>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Accordingly, the code below calculates the along-slope velocity component as

    $$ u_{\rm along} = (u,v) \boldsymbol{\cdot} \left(\frac{h_y}{|\boldsymbol{\nabla} h|} , -\frac{h_x}{|\boldsymbol{\nabla} h|}\right) =
    u \frac{h_y}{|\boldsymbol{\nabla} h|} - v \frac{h_x}{|\boldsymbol{\nabla} h|}, $$

    and similarly the cross-slope velocity component as

    $$ v_{\rm cross} = (u,v) \boldsymbol{\cdot} \left(\frac{h_x}{|\boldsymbol{\nabla} h|} , \frac{h_y}{|\boldsymbol{\nabla} h|}\right)  =
    u \frac{h_x}{|\boldsymbol{\nabla} h|} + v \frac{h_y}{|\boldsymbol{\nabla} h|}.$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We need the derivatives of the bathymetry which we compute using the `xgcm`.
    """)
    return


@app.cell
def _(grid_ds, hu_ds, xr):
    # We need to merge the two datasets. They're on the same coordinates, so this should be straightforward.
    ds_1 = xr.merge([hu_ds, grid_ds])
    ds_1.coords['xt_ocean'].attrs.update(axis='X')
    # Give information on the grid: location of u (momentum) and t (tracer) points on B-grid 
    ds_1.coords['xu_ocean'].attrs.update(axis='X', c_grid_axis_shift=0.5)
    ds_1.coords['yt_ocean'].attrs.update(axis='Y')
    ds_1.coords['yu_ocean'].attrs.update(axis='Y', c_grid_axis_shift=0.5)
    ds_1
    return (ds_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For `xgcm` to work correctly, there center and corner (t-cells and u-cells) dimensions must have the same size and be staggered in the correct way (u-cells to the north-east of the t-cells). As we can see in the above `ds` the meridional dimensions are not of the same size. We need to remove the first point in `yu_ocean`.
    """)
    return


@app.cell
def _(ds_1, np, xgcm):
    ds_2 = ds_1.isel(yu_ocean=slice(1, None))
    grid = xgcm.Grid(ds_2, periodic=['X'])
    # Create grid object
    dhu_dx = grid.interp(grid.diff(ds_2.hu, 'X') / grid.interp(ds_2.dxu, 'X'), 'X')
    dhu_dy = grid.interp(grid.diff(ds_2.hu, 'Y', boundary='extend') / grid.interp(ds_2.dyt, 'X'), 'Y', boundary='extend')
    # Take topographic gradient (simple gradient over one grid cell) and move back to u-grid
    # In meridional direction, we need to specify what happens at the boundary
    # Magnitude of the topographic slope (to normalise the topographic gradient)
    topographic_slope_magnitude = np.sqrt(dhu_dx ** 2 + dhu_dy ** 2)
    return dhu_dx, dhu_dy, topographic_slope_magnitude


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Calculate along-slope velocity component
    """)
    return


@app.cell
def _(dhu_dx, dhu_dy, topographic_slope_magnitude, uv_ds):
    # Get the u and v data arrays out of our dataset
    uv_ds_1 = uv_ds.isel(yu_ocean=slice(1, None))
    u, v = (uv_ds_1['u'], uv_ds_1['v'])
    topographic_slope_magnitude_1 = topographic_slope_magnitude.where(topographic_slope_magnitude != 0)
    # Mask zeros to avoid error warnings when dividing
    alongslope_velocity = u * dhu_dy / topographic_slope_magnitude_1 - v * dhu_dx / topographic_slope_magnitude_1
    # Along-slope velocity
    alongslope_velocity
    return (alongslope_velocity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plotting
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create a land mask for plotting, set land cells to 1 and rest to zeros
    """)
    return


@app.cell
def _(hu_ds, np, xr):
    land = xr.where(np.isnan(hu_ds['hu'].rename('land')), 1, 0)
    return (land,)


@app.cell
def _(alongslope_velocity, ccrs, cm, land, mpath, np, plt):
    projection = ccrs.SouthPolarStereo()

    plt.figure(figsize=(12, 12))
    ax = plt.axes(projection=projection, facecolor='gainsboro')

    ax.set_extent([-280, 80, -80, -59], crs=ccrs.PlateCarree())

    theta = np.linspace(0, 2 * np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)

    # Plot land mask
    land.where(land==1).plot.contourf(ax=ax, 
                                      colors=['gainsboro'], 
                                      add_colorbar=False,
                                      transform=ccrs.PlateCarree())
    land.plot.contour(ax=ax, 
                      levels=[0.99], 
                      colors=['grey'], 
                      linewidths=[0.5],
                      transform=ccrs.PlateCarree())

    # Plot along slope surface velocities
    alongslope_velocity.plot(ax=ax, 
                             cmap=cm.cm.curl,
                             vmin=-0.35, vmax=0.35, extend='both',
                             cbar_kwargs={'shrink': 0.7,
                                          'label': 'm/s'},
                             transform=ccrs.PlateCarree())

    ax.set_title('Along-bathymetry surface velocity');
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
