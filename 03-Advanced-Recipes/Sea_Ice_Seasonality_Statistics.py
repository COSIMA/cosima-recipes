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
    # Sea ice seasonality statistics: an example in the Southern Ocean

    ### Background

    This recipe calculates number of days of sea ice advance, retreat, and sea ice duration over the sea ice season (February 15 to February 14) in the Southern Ocean using output from ACCESS-OM2-01.

    The annual sea ice advance, retreat and total sea ice season duration as defined by [Massom et al 2013](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0064756).

    ---

    ### Requirements

    This notebook was generated using a large ARE session, and may not work if run in a session with fewer resources.

    For adaptation to `SIS`, which is the sea ice model of some of the PanAntarctic configurations, the following table will help you find equivalent diagnostics:

    | CICE diagnostic (x-coord, y-coord) | SIS diagnostic (x-coord, y-coord)|
    |---|---|
    `aice(ni,nj)` | `siconc(xT, yT)`|

    You will **not** need to correct time stamps, and the x, y-coords have longitude, latitude information. Loading of the data will be easier!
    """)
    return


@app.cell
def _():
    import cartopy.crs as ccrs                       
    import cmocean.cm as cm                              
    import datetime as dt
    import intake
    import matplotlib.path as mpath
    import matplotlib.pyplot as plt
    import numpy as np
    import xarray as xr
    from dask.distributed import Client

    return Client, ccrs, cm, dt, intake, mpath, np, plt, xr


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start a dask client:
    """)
    return


@app.cell
def _(Client):
    client = Client(threads_per_worker=1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Open sea ice concentration

    Open the intake datastore:
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    experiment = "01deg_jra55v140_iaf_cycle2"
    return catalog, experiment


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Open sea ice concentration from `CICE`, called `aice` - we can use the `start_date` argument to select just one year.

    There are some recommended kwargs for `xarray` in order to open sea ice data which are described [here](https://github.com/COSIMA/cosima-recipes/blob/main/02-Easy-Recipes/Sea_Ice_Coordinates.ipynb) - lets use those:
    """)
    return


@app.cell
def _(catalog, experiment):
    xarray_kwargs = {"use_cftime" : True,
                     "decode_coords": False,
                     "decode_timedelta" : False,
                    }
    
    aice = catalog[experiment].search(variable="aice",
                                               start_date="200[0,1].*"
                                               ).to_dask(xarray_open_kwargs=xarray_kwargs)
    # Select only february
    aice = aice['aice'].sel(time=slice('2000-02-01','2001-03-01'))
    return (aice,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we need to apply the correction to the time stamps and longitude/latitude coordinates. `CICE` has an incorrect time stamp and does not come with lat/lon. Again, this is fully described [here](https://github.com/COSIMA/cosima-recipes/blob/main/02-Easy-Recipes/Sea_Ice_Coordinates.ipynb)
    """)
    return


@app.cell
def _(aice, catalog, dt, experiment):
    # Applying time correction 
    aice['time'] = aice.time - dt.timedelta(hours=12)
    geolon_t = catalog[experiment].search(variable='geolon_t').to_dask()
    # Overwrite coordinates used by CICE output:
    geolat_t = catalog[experiment].search(variable='geolat_t').to_dask()
    aice.coords['ni'] = geolon_t['xt_ocean'].values
    aice.coords['nj'] = geolon_t['yt_ocean'].values
    aice_1 = aice.rename({'ni': 'xt_ocean', 'nj': 'yt_ocean'})
    return (aice_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can subset the Southern Ocean:
    """)
    return


@app.cell
def _(aice_1):
    aice_2 = aice_1.sel(yt_ocean=slice(-80, -50))
    return (aice_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Select the specific days we are interested in - a sea ice year is defined to be between February 15 and February 14 the following year:
    """)
    return


@app.cell
def _(aice_2):
    aice_3 = aice_2.sel(time=slice('2000-02-15', '2001-02-14'))
    return (aice_3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sea ice seasonality calculations

    According to the definitions in [Massom et al 2013](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0064756):

     - If sea ice concentration in any grid cell is at least 15% over five consecutive days, sea ice is considered to be *advancing*.
     - Sea ice is defined to be *retreating* when its concentration is below 15% in any pixel until the end of the sea ice year.
     - Sea ice *season duration* is the period between day of advance and retreat.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First, lets find how many days in a year sea ice concentration is above the 15% threshold. Note that `aice` goes from 0 to 1, so the threshold will be 0.15:
    """)
    return


@app.cell
def _(aice_3, xr):
    min_threshold = 0.15
    days_in_year = len(aice_3.time.values)
    # Calculate total number of days in year (365 or 366 depending on whether it is a leap year or not):
    conc_above_threshold = xr.where(aice_3 >= min_threshold, True, False)
    # Identify grid cells where sea ice concentration values are equal or above min_threshold.
    # Resulting data array is boolean. If concentration > 0.15, then set to True, otherwise set to False:
    # Add values through time to get total number of days with ice cover of at least 15% within a grid cell:
    days_above_threshold = conc_above_threshold.sum('time').compute()
    return conc_above_threshold, days_above_threshold, days_in_year


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Make a land mask from the bathymetry diagnostic for plotting:
    """)
    return


@app.cell
def _(catalog, experiment, np, xr):
    ht = catalog[experiment].search(variable="ht",
                                    frequency="fx"
                                    ).to_dask()['ht']
    ht = ht.sel(yt_ocean=slice(-80,-50))
    land = xr.where(np.isnan(ht.rename('land')), 1, np.nan)
    # Adjust latitude on land, so it goes to south pole. Needed for prettier plotting:
    land_lat = land.yt_ocean.values
    land_lat[0] = -90
    land['yt_ocean'] = land_lat
    return (land,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot `days_above_threshold`:
    """)
    return


@app.cell
def _(ccrs, cm, days_above_threshold, land, mpath, np, plt):
    plt.figure(figsize=(7, 7))
    _ax = plt.axes(projection=ccrs.SouthPolarStereo())
    _ax.set_extent([-280, 80, -80, -50], crs=ccrs.PlateCarree())
    _theta = np.linspace(0, 2 * np.pi, 100)
    _center, _radius = ([0.5, 0.5], 0.5)
    _verts = np.vstack([np.sin(_theta), np.cos(_theta)]).T
    _circle = mpath.Path(_verts * _radius + _center)
    _ax.set_boundary(_circle, transform=_ax.transAxes)
    land.plot.contourf(ax=_ax, colors='darkgrey', zorder=2, transform=ccrs.PlateCarree(), add_colorbar=False)
    days_above_threshold.plot(ax=_ax, cmap=cm.ice, transform=ccrs.PlateCarree(), cbar_kwargs={'orientation': 'vertical', 'shrink': 0.6, 'extend': 'both', 'label': 'Number of days'})
    _ax.set_title('Number of days with concentration > 0.15')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create some masks that will be useful for the advance, retreat and duration metrics:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. Mask of cells where sea ice never exceeded the minimum threshold:
    """)
    return


@app.cell
def _(days_above_threshold, xr):
    noIce = xr.where(days_above_threshold == 0, True, False)
    return (noIce,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    2. Mask of cells where sea ice did not advance - define as not exceeding the threshold for at least 5 consecutive days:
    """)
    return


@app.cell
def _(days_above_threshold, xr):
    min_days_threshold = 5
    noIceAdvance = xr.where(days_above_threshold < min_days_threshold, True, False)
    return min_days_threshold, noIceAdvance


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    3. Mask of cells where sea ice concentration was *always* above the threshold:
    """)
    return


@app.cell
def _(days_above_threshold, days_in_year, xr):
    alwaysIce = xr.where(days_above_threshold == days_in_year, True, False)
    return (alwaysIce,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we are ready to calculate advance, retreat and duration.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Sea ice advance
    """)
    return


@app.cell
def _(
    alwaysIce,
    conc_above_threshold,
    min_days_threshold,
    noIceAdvance,
    np,
    xr,
):
    # Use cumulative sums based on time. If grid cell has sea ice cover below min_threshold, then cumulative sum is reset to zero:
    advance = conc_above_threshold.cumsum(dim='time') - conc_above_threshold.cumsum(dim='time').where(conc_above_threshold.values==0).ffill(dim = 'time').fillna(0)
    # Note: ffill adds nan values forward over a specific dimension

    # Find time index where the minimum consecutive sea ice concentration was first detected for each grid cell
    # Change all grid cells that do not meet the minimum consecutive sea ice concentration to False. Otherwise maintain their value.
    advanceDate = xr.where(advance==min_days_threshold, advance, False)

    # Find the time index where condition above was met:
    advanceDate = advanceDate.argmax(dim='time')

    # Apply masks of no sea ice advance (noIceAdvance) and sea ice always present (alwaysIce).
    advanceDate = advanceDate.where(noIceAdvance==False, np.nan).where(alwaysIce==False, 1).compute()
    return (advanceDate,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot day of year of sea ice advance. Note that this is defined relative to February 15th.
    """)
    return


@app.cell
def _(advanceDate, ccrs, cm, land, mpath, np, plt):
    plt.figure(figsize=(7, 7))
    _ax = plt.axes(projection=ccrs.SouthPolarStereo())
    _ax.set_extent([-280, 80, -80, -50], crs=ccrs.PlateCarree())
    _theta = np.linspace(0, 2 * np.pi, 100)
    _center, _radius = ([0.5, 0.5], 0.5)
    _verts = np.vstack([np.sin(_theta), np.cos(_theta)]).T
    _circle = mpath.Path(_verts * _radius + _center)
    _ax.set_boundary(_circle, transform=_ax.transAxes)
    land.plot.contourf(ax=_ax, colors='darkgrey', zorder=2, transform=ccrs.PlateCarree(), add_colorbar=False)
    advanceDate.plot(ax=_ax, cmap=cm.phase, transform=ccrs.PlateCarree(), cbar_kwargs={'orientation': 'vertical', 'shrink': 0.6, 'extend': 'both', 'label': 'Day of year'})
    # Filled land 
    _ax.set_title('Sea ice advance day')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Sea ice retreat
    """)
    return


@app.cell
def _(alwaysIce, conc_above_threshold, days_in_year, noIce, np, xr):
    # Reverse conc_above_threshold in time dimension, so end date is now the start date and calculate cumulative sum over time:
    retreat = conc_above_threshold[::-1].cumsum('time')

    # Change zero values to 9999 so they are ignored in the next step of our calculation:
    retreat = xr.where(retreat == 0, 9999, retreat)

    # Find the time index where sea ice concentration changes to above threshold:
    retreatDate = retreat.argmin(dim = 'time')

    # Substract index from total time length:
    retreatDate = days_in_year - retreatDate

    # Apply masks of no sea ice over min_threshold (noIce) and sea ice always present (alwaysIce):
    retreatDate = retreatDate.where(noIce==False, np.nan).where(alwaysIce==False, days_in_year).compute()
    return (retreatDate,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot day of year of sea ice retreat. Note that this is defined relative to February 15th.
    """)
    return


@app.cell
def _(ccrs, cm, land, mpath, np, plt, retreatDate):
    plt.figure(figsize=(7, 7))
    _ax = plt.axes(projection=ccrs.SouthPolarStereo())
    _ax.set_extent([-280, 80, -80, -50], crs=ccrs.PlateCarree())
    _theta = np.linspace(0, 2 * np.pi, 100)
    _center, _radius = ([0.5, 0.5], 0.5)
    _verts = np.vstack([np.sin(_theta), np.cos(_theta)]).T
    _circle = mpath.Path(_verts * _radius + _center)
    _ax.set_boundary(_circle, transform=_ax.transAxes)
    land.plot.contourf(ax=_ax, colors='darkgrey', zorder=2, transform=ccrs.PlateCarree(), add_colorbar=False)
    retreatDate.plot(ax=_ax, cmap=cm.phase, transform=ccrs.PlateCarree(), cbar_kwargs={'orientation': 'vertical', 'shrink': 0.6, 'extend': 'both', 'label': 'Day of year'})
    # Filled land 
    _ax.set_title('Sea ice retreat day')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Sea ice duration
    """)
    return


@app.cell
def _(advanceDate, ccrs, cm, land, mpath, np, plt, retreatDate):
    durationDays = retreatDate - advanceDate
    plt.figure(figsize=(7, 7))
    _ax = plt.axes(projection=ccrs.SouthPolarStereo())
    _ax.set_extent([-280, 80, -80, -50], crs=ccrs.PlateCarree())
    _theta = np.linspace(0, 2 * np.pi, 100)
    _center, _radius = ([0.5, 0.5], 0.5)
    _verts = np.vstack([np.sin(_theta), np.cos(_theta)]).T
    _circle = mpath.Path(_verts * _radius + _center)
    _ax.set_boundary(_circle, transform=_ax.transAxes)
    land.plot.contourf(ax=_ax, colors='darkgrey', zorder=2, transform=ccrs.PlateCarree(), add_colorbar=False)
    durationDays.plot(ax=_ax, cmap=cm.ice, transform=ccrs.PlateCarree(), cbar_kwargs={'orientation': 'vertical', 'shrink': 0.6, 'extend': 'both', 'label': 'Number of days'})
    # Filled land 
    _ax.set_title('Sea ice season duration')
    return


if __name__ == "__main__":
    app.run()
