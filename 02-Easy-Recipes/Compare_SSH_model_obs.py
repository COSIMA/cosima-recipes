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
    # Compare sea surface height model output and observations

    Comparing the sea-surface height (ssh) from two different resolution runs. Specifically, we plot the time-mean and standard deviation of ssh and compare it to those obtained from observations from the CMEMS satellite altimetry dataset (former AVISO+ dataset).
    """)
    return


@app.cell
def _():
    import intake
    import numpy as np
    import xarray as xr
    import glob

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cmocean as cm

    from dask.distributed import Client

    return Client, ccrs, cm, glob, intake, plt, xr


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here we pick a `start_time` and `end_time`. We select *only* 5 years of daily data for computational speed in this example. But you can probably extend the `end_time` until the end of 2018 (for model outputs) and up to middle of 2020 for observations.
    """)
    return


@app.cell
def _():
    # SSH variable in ACCESS-OM2 models
    variable = 'sea_level'

    start_time = '1993-01-01'
    end_time = '1997-12-31'
    return end_time, start_time, variable


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## SSH from 1$^{\circ}$ model output
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell
def _(catalog, end_time, start_time, variable):
    _var_search = catalog['1deg_jra55_iaf_omip2_cycle6'].search(variable=variable, frequency='1day')
    _ds = _var_search.to_dask()
    ssh1 = _ds[variable].sel(time=slice(start_time, end_time))
    return (ssh1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## SSH from 0.25$^{\circ}$ model output
    """)
    return


@app.cell
def _(catalog, end_time, start_time, variable):
    _var_search = catalog['025deg_jra55_iaf_omip2_cycle6'].search(variable=variable, frequency='1day')
    _ds = _var_search.to_dask()
    ssh025 = _ds[variable].sel(time=slice(start_time, end_time))
    ssh025
    return (ssh025,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You can see we have a very large number of chunks, so lets rechunk.
    """)
    return


@app.cell
def _(ssh025):
    ssh025_1 = ssh025.chunk({'time': 'auto'})
    return (ssh025_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## CMEMS satellite observational data (former AVISO+ dataset)

    Load the CMEMS dataset and select `adt` the sea surface height variable name.

    **Note**: You **need** to join project `ua8` on NCI to access the CMEMS data!
    """)
    return


@app.cell
def _(end_time, glob, start_time, xr):
    filenames = glob.glob("/g/data/ua8/CMEMS_SeaLevel/timeseries/*.nc")
    cmems = xr.open_mfdataset(filenames, parallel=True)

    obs_ssh = cmems.adt
    obs_ssh = obs_ssh.sel(time=slice(start_time, end_time))
    obs_ssh = obs_ssh.rename('adt_cmems')
    return (obs_ssh,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Compute the mean and standard deviations to plot. We add `.load()` so to enforce computations. For the `std` calculations we provide `skipna=False` option to tell xarray to ignore the points on land that have `NaN` values. This way it doesn't try to divide by a zero-length series while computing the standard deviation. (If we didn't provide`skipna=False` we'd get the same answer but with a bunch of `RuntimeWarnings`.)

    **Note**: The following cells might take a while, depending how much data you loaded. (For 5 years of daily data ~3min for 0.25 model output using 28 cpus).
    """)
    return


@app.cell
def _(ssh1):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    ssh1_mean = ssh1.mean(dim='time').load()
    ssh1_std  = ssh1.std(dim='time', skipna=False).load()
    return ssh1_mean, ssh1_std


@app.cell
def _(ssh025_1):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    ssh025_mean = ssh025_1.mean(dim='time').load()
    ssh025_std = ssh025_1.std(dim='time', skipna=False).load()
    return ssh025_mean, ssh025_std


@app.cell
def _(obs_ssh):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    obs_ssh_mean = obs_ssh.mean(dim='time').load()
    obs_ssh_std  = obs_ssh.std(dim='time', skipna=False).load()
    return obs_ssh_mean, obs_ssh_std


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Plot and compare
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot the time-mean and standard deviation of both of the model outputs and the CMEMS observational dataset (former AVISO+).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First we load `geolon_t`/`geolat_t` coordinates, so we can plot the Arctic region correctly for the model output.
    """)
    return


@app.cell
def _(catalog, ssh025_mean, ssh025_std, ssh1_mean, ssh1_std):
    _var_search = catalog['1deg_jra55_iaf_omip2_cycle6'].search(variable='area_t')
    _ds = _var_search.search(path=_var_search.df['path'][0]).to_dask()
    geolon_t_1 = _ds.geolon_t
    geolat_t_1 = _ds.geolat_t
    ssh1_mean_1 = ssh1_mean.assign_coords({'geolon_t': geolon_t_1, 'geolat_t': geolat_t_1})
    ssh1_std_1 = ssh1_std.assign_coords({'geolon_t': geolon_t_1, 'geolat_t': geolat_t_1})
    _var_search = catalog['025deg_jra55_iaf_omip2_cycle6'].search(variable='area_t')
    _ds = _var_search.search(path=_var_search.df['path'][0]).to_dask()
    geolon_t_025 = _ds.geolon_t
    geolat_t_025 = _ds.geolat_t
    ssh025_mean_1 = ssh025_mean.assign_coords({'geolon_t': geolon_t_025, 'geolat_t': geolat_t_025})
    ssh025_std_1 = ssh025_std.assign_coords({'geolon_t': geolon_t_025, 'geolat_t': geolat_t_025})
    return ssh025_mean_1, ssh025_std_1, ssh1_mean_1, ssh1_std_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This plotting is a little slow, takes ~1 minute:
    """)
    return


@app.cell
def _(
    ccrs,
    cm,
    obs_ssh_mean,
    obs_ssh_std,
    plt,
    ssh025_mean_1,
    ssh025_std_1,
    ssh1_mean_1,
    ssh1_std_1,
):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    projection = ccrs.Robinson(central_longitude=-100)
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(14, 10), subplot_kw={'projection': projection})
    plt.subplots_adjust(wspace=-0.15)
    max_std = 0.3
    max_mean = 1.65
    ax = axes[0, 0]
    p1 = ssh1_mean_1.plot.contourf(ax=ax, x='geolon_t', y='geolat_t', levels=100, vmin=-max_mean, vmax=+max_mean, add_colorbar=False, cmap=cm.cm.balance, transform=ccrs.PlateCarree())
    ax.set_title('mean SSH ACCESS-OM2 1$^{\\circ}$')
    ax = axes[1, 0]
    p1 = ssh025_mean_1.plot.contourf(ax=ax, x='geolon_t', y='geolat_t', levels=100, vmin=-max_mean, vmax=+max_mean, add_colorbar=False, cmap=cm.cm.balance, transform=ccrs.PlateCarree())
    # mean SSH plots
    ax.set_title('mean SSH ACCESS-OM2 0.25$^{\\circ}$')
    ax = axes[2, 0]
    p1 = obs_ssh_mean.plot(ax=ax, transform=ccrs.PlateCarree(), cmap=cm.cm.balance, vmin=-max_mean, vmax=max_mean, add_colorbar=False)
    ax.set_title('mean SSH CMEMS obs')
    ax = axes[0, 1]
    p2 = ssh1_std_1.plot.contourf(ax=ax, x='geolon_t', y='geolat_t', levels=100, vmin=0, vmax=max_std, add_colorbar=False, cmap=cm.cm.deep, transform=ccrs.PlateCarree())
    ax.set_title('SSH standard deviation ACCESS-OM2 1$^{\\circ}$')
    ax = axes[1, 1]
    p2 = ssh025_std_1.plot.contourf(ax=ax, x='geolon_t', y='geolat_t', levels=100, vmin=0, vmax=max_std, add_colorbar=False, cmap=cm.cm.deep, transform=ccrs.PlateCarree())
    ax.set_title('SSH standard deviation ACCESS-OM2 0.25$^{\\circ}$')
    ax = axes[2, 1]
    p2 = obs_ssh_std.plot(ax=ax, transform=ccrs.PlateCarree(), cmap=cm.cm.deep, vmin=0, vmax=max_std, add_colorbar=False)
    ax.set_title('SSH standard deviation CMEMS obs')
    ax_cb1 = plt.axes([0.13, 0.3, 0.015, 0.4])
    cb = plt.colorbar(p1, cax=ax_cb1, extend='both', label='Mean SSH (m)')
    ax_cb1.yaxis.set_ticks_position('left')
    ax_cb1.yaxis.set_label_position('left')
    ax_cb2 = plt.axes([0.88, 0.3, 0.015, 0.4])
    # std SSH plots
    # Colorbars
    cb = plt.colorbar(p2, cax=ax_cb2, extend='max', label='SSH standard deviation (m)')
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
