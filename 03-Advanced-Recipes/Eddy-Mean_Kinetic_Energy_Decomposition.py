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
    # Kinetic Energy Mean-Transient Decomposition

    Decomposing the kinetic energy into time-mean and transient components.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Theory
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For a hydrostatic ocean model, like MOM5, the relevant kinetic energy per unit mass is

    $$ {\rm KE} = \frac{1}{2} (u^2 + v^2).$$

    The vertical velocity component, $w$, does not appear in the mechanical energy budget. It is very much subdominant. But more fundamentally, it simply does not appear in the mechanical energy buget for a hydrostatic ocean.

    For a non-steady fluid, we can define the time-averaged kinetic energy as the __total kinetic energy__, TKE

    $$ {\rm TKE} = \left< {\rm KE} \right > {\stackrel{\rm{def}}{=}} \frac{1}{T} \int_0^T \frac{1}{2} \left( u^2 + v^2 \right)\,\mathrm{d}t.$$

    It is useful to decompose the velocity into time-mean and time-varying components, e.g.,

    $$ u = \bar{u} + u'.$$

    The __mean kinetic energy__ is the energy associated with the mean flow

    $$ {\rm MKE} = \frac{1}{2} \left( \bar{u}^2 + \bar{v}^2 \right) $$

    The kinetic energy of the time varying component is the __eddy kinetic energy__, EKE. This quantity can be obtained by
    substracting the velocity means and calculating the kinetic energy of the
    perturbation velocity quantities.

    $$ {\rm EKE} =  \overline{ \frac{1}{2} \left[ \left(u - \overline{u}\right)^2 + \left(v - \overline{v}\right)^2 \right] } $$

    MKE and EKE partition the total kinetic energy

    $${\rm TKE} = {\rm MKE} + {\rm EKE}.$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Adapting for MOM6

    |Variable | MOM5 diagnostic | Equivalent MOM6 diagnostic |
    |:--------|-----|------|
    | Zonal velocity (m/s) | `u` | `uo` |
    | Meridional velocity (m/s) | `v` | `vo` |
    |Cell thickness (m) | `dzt` | Not available for most experiments, but can be calculated by `volcello / areacello` |

    In MOM5 velocities are calculated in the (north-east) corner of the cells, where the dimension names are `xu_ocean` and `yu_ocean`. In MOM6, velocities are calculated in the eastern face of the cell for `uo` and northern face of the cell for `vo`. To adapt this recipe, an option would be to interpolate first `uo` and `vo` to be in the (north-east) corner, where the dimensions are (`xq`, `yq`).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MOM5
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We start by importing some useful packages.
    """)
    return


@app.cell
def _():
    import cartopy.crs as ccrs
    import cartopy.feature as feature
    import cmocean as cm
    import intake
    import matplotlib.path as mpath
    import matplotlib.pyplot as plt
    import numpy as np
    import xarray as xr

    from dask.distributed import Client

    return Client, ccrs, cm, feature, intake, mpath, np, plt, xr


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Open ACCESS-NRI default catalog
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Choose an experiment which has daily velocities saved for the Southern Ocean (you can also perhaps choose an experiment with 5 day velocities).
    """)
    return


@app.cell
def _():
    expt = '01deg_jra55v13_ryf9091'
    return (expt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For this recipe we will just load 1 month of daily velocities, but if you want to do the decomposition with output longer than, e.g., 1 year then we suggest you either convert this to a `.py` script and submit through the queue via `qsub` or figure a way to scale `dask` up to larger `ncpus`.
    """)
    return


@app.cell
def _():
    dates = '2100-12.*'
    return (dates,)


@app.cell
def _(catalog, dates, expt):
    def select_region(ds):
        ds = ds.sel(yu_ocean=slice(None, -50))
        return ds

    darray = catalog[expt].search(
                    variable = 'u',
                    frequency = '1day',
                    start_date=dates).to_dask(chunks='auto', preprocess=select_region)
    u = darray['u']

    darray = catalog[expt].search(
                    variable = 'v',
                    frequency = '1day',
                    start_date=dates).to_dask(chunks='auto', preprocess=select_region)
    v = darray['v']
    return u, v


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Make model's land mask and define a plotting function:
    """)
    return


@app.cell
def _(catalog, ccrs, expt, feature, mpath, np, plt, xr):
    datastore = catalog[expt].search(variable='ht')
    ht = datastore.search(path=datastore.df.loc[0, 'path']).to_dask(xarray_open_kwargs={'chunks': 'auto'})
    land_mask = xr.where(np.isnan(ht['ht']), 1, np.nan)
    land_mask = land_mask.rename('land_mask').sel(yt_ocean=slice(None, -49))
    land_50m = feature.NaturalEarthFeature('physical', 'land', '50m', edgecolor='black', facecolor='gray', linewidth=0.2)

    def circumpolar_map():
        _fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.SouthPolarStereo())
        ax.set_extent([-180, 180, -80, -50], crs=ccrs.PlateCarree())
        ax.set_facecolor('lightgrey')
        theta = np.linspace(0, 2 * np.pi, 100)
        center, radius = ([0.5, 0.5], 0.5)
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = mpath.Path(verts * radius + center)
        ax.set_boundary(circle, transform=ax.transAxes)  # Map the plot boundaries to a circle
        land_mask.plot.contourf(ax=ax, colors='lightgrey', add_colorbar=False, zorder=2, transform=ccrs.PlateCarree())
        return (_fig, ax)

    return (circumpolar_map,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The kinetic energy is

    $$ {\rm KE} = \frac{1}{2} (u^2 + v^2).$$

    We construct the following expression:
    """)
    return


@app.cell
def _(u, v):
    KE = 0.5*(u**2 + v**2)
    return (KE,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You may notice that this line runs instantly. The calculation is not (yet) computed. Rather, `xarray` needs to broadcast the squares of the velocity fields together to determine the final shape of KE.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is too large to store locally.  We need to reduce the data in some way.

    The mean kinetic energy is calculated by this function, which returns the depth integrated KE:

    $$ \int_{z_0}^{z} \mathrm{KE}\,\mathrm{d}z.$$

    Let's load the cell thickness ($dz$), and interpolate to the u-grid. Cell thickness varies with time with stretching and squashing of the water column, but experiments don't usually save it at a daily time step. So we will use the monthly average:
    """)
    return


@app.cell
def _(catalog, expt, u):
    dzt = catalog[expt].search(
                variable='dzt',
                frequency='1mon', 
                start_date='2100.*').to_dask()
    dzt = dzt.sel(time='2100-12-16')
    # Interpolate to the u-grid (note that some experiments might have dzu available)
    dzu = dzt['dzt'].rename({'xt_ocean':'xu_ocean', 'yt_ocean':'yu_ocean'}).interp(xu_ocean = u['xu_ocean'], yu_ocean = u['yu_ocean']).squeeze()
    return (dzu,)


@app.cell
def _(KE, dzu):
    KE_dz = KE*dzu
    return (KE_dz,)


@app.cell
def _(KE_dz):
    TKE = KE_dz.mean('time').sum('st_ocean')
    return (TKE,)


@app.cell
def _(TKE):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    TKE_1 = TKE.load()
    return (TKE_1,)


@app.cell
def _(TKE_1, ccrs, circumpolar_map, cm):
    _fig, _axs = circumpolar_map()
    TKE_1.plot(ax=_axs, vmax=70, cmap=cm.cm.rain, transform=ccrs.PlateCarree(), cbar_kwargs={'label': 'm$^3$ s$^{-2}$', 'shrink': 0.6})
    _axs.set_title('TKE')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Snapshot plot of depth-integrated KE for a random time step:
    """)
    return


@app.cell
def _(KE_dz):
    KE_snapshot = KE_dz.isel(time = 0).sum('st_ocean')
    KE_snapshot = KE_snapshot.load()
    return (KE_snapshot,)


@app.cell
def _(KE_snapshot, ccrs, circumpolar_map, cm):
    _fig, _axs = circumpolar_map()
    KE_snapshot.plot(ax=_axs, vmax=70, cmap=cm.cm.rain, transform=ccrs.PlateCarree(), cbar_kwargs={'label': 'm$^3$ s$^{-2}$', 'shrink': 0.6})
    _axs.set_title('KE snapshot')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Mean Kinetic Energy
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For the mean kinetic energy, we need to average the velocities over time.

    $$ {\rm MKE} = \frac{1}{2} \left( \bar{u}^2 + \bar{v}^2 \right). $$
    """)
    return


@app.cell
def _(u, v):
    u_mean = u.mean('time')
    v_mean = v.mean('time')
    return u_mean, v_mean


@app.cell
def _(dzu, u_mean, v_mean):
    MKE = (0.5*(u_mean**2 + v_mean**2)*dzu).sum('st_ocean')
    return (MKE,)


@app.cell
def _(MKE):
    MKE_1 = MKE.load()
    return (MKE_1,)


@app.cell
def _(MKE_1, ccrs, circumpolar_map, cm):
    _fig, _axs = circumpolar_map()
    MKE_1.plot(ax=_axs, vmax=70, cmap=cm.cm.rain, transform=ccrs.PlateCarree(), cbar_kwargs={'label': 'm$^3$ s$^{-2}$', 'shrink': 0.6})
    _axs.set_title('MKE')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Eddy Kinetic Energy
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We calculate the transient component of the velocity field and then compute the EKE:

    $$ {\rm EKE} =  \overline{ \frac{1}{2} \left[ \left(u - \overline{u}\right)^2 + \left(v - \overline{v}\right)^2 \right] }. $$
    """)
    return


@app.cell
def _(u, u_mean, v, v_mean):
    u_transient = u - u_mean
    v_transient = v - v_mean
    return u_transient, v_transient


@app.cell
def _(dzu, u_transient, v_transient):
    EKE = (0.5*(u_transient**2 + v_transient**2)*dzu).sum('st_ocean').mean('time')
    return (EKE,)


@app.cell
def _(EKE):
    EKE_1 = EKE.load()
    return (EKE_1,)


@app.cell
def _(EKE_1, ccrs, circumpolar_map, cm):
    _fig, _axs = circumpolar_map()
    EKE_1.plot(ax=_axs, vmax=70, cmap=cm.cm.rain, transform=ccrs.PlateCarree(), cbar_kwargs={'label': 'm$^3$ s$^{-2}$', 'shrink': 0.6})
    _axs.set_title('EKE')
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
