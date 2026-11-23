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
    # Barotropic Streamfunction

    This recipe demonstrates how to compute and plot the barotropic streamfunction ($\psi$).

    ---

    ## Background

    The barotropic streamfunction ($\psi$) is obtained from the integration of the depth-integrated transports starting from a physical boundary at which we know the transport is zero - therefore there are different ways to calculate it depending on your choice of boundary for the integration.

    This recipe calculates $\psi$ integrating the depth-integrated zonal transport, $U$ in the meridional direction, starting from the Antarctic continent:

    $$
    \psi = \int_{y_{\rm Antarctica}}^{y} U \, \mathrm{d}y ,
    $$

    You can see from this expression that the direction of the transport is then parallel to streamlines, and the intensity of that transport is given by the difference between streamlines. For this statement to be valid, the flow must be incompressible (or approximately so).

    ---

    ## Requirements

    This recipe uses MOM6 output.

    The workflow is,
    1. Load the MOM6 depth-integrated zonal mass transport (`umo_2d`).
    2. Convert it to volume transport in Sverdrups (`Sv`).
    3. Integrate meridionally (cumulative sum along latitude) to obtain the barotropic streamfunction ($\psi$).
    4. Plot a circumpolar map with a circular boundary and land mask.

    ## MOM5 adaptation

    To adapt this recipe for MOM5 output, the following diagnostic equivalences may be useful:

    | MOM6 diagnostic (x-coord,y-coord) | MOM5 diagnostic (x-coord,y-coord)|
    |---|---|
    |`umo_2d(xq, yh)` | `tx_trans_int_z(xu_ocean, xt_ocean)`|
    |`deptho(xh, yh)` | `ht(xt_ocean, xt_ocean)`|
    """)
    return


@app.cell
def _():
    import cartopy.crs as ccrs
    import cmocean
    import intake
    import matplotlib.path as mpath
    import matplotlib.pyplot as plt
    import numpy as np
    import xarray as xr
    import dask.distributed as dask

    return ccrs, cmocean, dask, intake, mpath, np, plt, xr


@app.cell
def _(dask):
    client = dask.Client(threads_per_worker=1)
    client
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    experiment = "panant-01-zstar-v13"
    return catalog, experiment


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load transports - use a preprocessing function to subselect a domain.
    """)
    return


@app.cell
def _(catalog, experiment):
    def subset_domain(ds):
        ds = ds.sel(yh=slice(None, -50))
        return ds

    umo = catalog[experiment].search(variable='umo_2d',
                                    start_date='200[0,1].*',
                                    frequency='1mon'
                                    ).to_dask(preprocess=subset_domain)
    deptho = catalog[experiment].search(variable='deptho',
                                        frequency='fx'
                                        ).to_dask(preprocess=subset_domain)
    return deptho, umo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Take the time mean of the transport:
    """)
    return


@app.cell
def _(umo):
    mass_transport = umo['umo_2d'].mean('time')
    mass_transport
    return (mass_transport,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Looking at the `mass_transport` attributes, we can confirm that it is a mass transport from its units.
    To convert to volume transoprt we need to divide by the reference density.
    """)
    return


@app.cell
def _(mass_transport):
    ρ0 = 1030  # reference seawater density, kg m⁻³
    volume_transport = mass_transport / ρ0   # convert kg s⁻¹ -> m³ s⁻¹
    return (volume_transport,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To integrate the transport in the meridional direction, we just need to sum cumulatively northwards - this is because the transport is the *total amount of water* through a grid face.

    We also divide by 1e6 to convert from m³ s⁻¹ to Sv (1 Sv = 10⁶ m³ s⁻¹)
    """)
    return


@app.cell
def _(volume_transport):
    psi = volume_transport.cumsum('yh') / 1e6 # convert m³ s⁻¹ -> Sv
    return (psi,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now lets create a land mask for plotting:
    """)
    return


@app.cell
def _(deptho, np, xr):
    land_mask = xr.where(np.isnan(deptho['deptho']), 1, np.nan)
    return (land_mask,)


@app.cell
def _(ccrs, cmocean, land_mask, mpath, np, plt, psi):
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.SouthPolarStereo())
    ax.set_extent([-180, 180, -80, -50], crs=ccrs.PlateCarree())
    ax.set_facecolor('lightgrey')

    # Map the plot boundaries to a circle
    theta = np.linspace(0, 2 * np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)

    psi.plot.contourf(ax=ax,
                      levels=np.arange(-50, 160, 10),
                      extend='both',
                      cmap=cmocean.cm.speed,
                      cbar_kwargs={'shrink':.7, 'label':'Sv'},
                      transform=ccrs.PlateCarree())

    land_mask.plot.contourf(ax=ax,
                            colors=['lightgrey'], 
                            add_colorbar=False,
                            transform=ccrs.PlateCarree())


    plt.title("Barotropic streamfunction (MOM6)")
    plt.tight_layout()
    return


if __name__ == "__main__":
    app.run()
