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
    # Compare Temperature and Salinity from ACCESS-OM2 to WOA13

    This notebook shows examples of comparing ACCESS-OM2 Temperature and Salinity structure to the WOA13 climatology (that is used as initial conditions for most runs). We describe the location and setup of the WOA13 data interpolated onto the model grids, as well as plot SST and SSS anomalies along with equatorial slices of temperature and salinity anomalies.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First, lets load in some modules, call some workers and load a database
    """)
    return


@app.cell
def _():
    import matplotlib.pyplot as plt
    import xarray as xr
    import numpy as np
    import cftime
    import datetime
    import cmocean as cm
    import cartopy.crs as ccrs
    import cartopy.feature as cft
    import sys, os, warnings
    warnings.filterwarnings('ignore')
    import intake
    catalog = intake.cat.access_nri
    from dask.distributed import Client

    return Client, catalog, ccrs, cft, cm, datetime, np, plt


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## WOA13 data

    The WOA13 data has already been interpolated onto the various model grids (as it is used for initial conditions). This makes it easy to plot biases.

    The WOA13 data is located in the `/g/data/ik11/observations/woa13/` folder, with various subfolders for the different resolutions (including the different vertical grids such as KDS50, KDS75 etc.). The available interpolated versions are (see `/g/data/ik11/observations/woa13/README/`:

    - `woa13/10` - 1-degree, GFDL50 vertical levels scheme
    - `woa13/025` - 1/4-degree, GFDL50 vertical levels scheme
    - `woa13/01` - 1/10-degree, KDS75 vertical levels scheme
    - `woa13/10_KDS50` - 1-degree, KDS50 vertical levels scheme
    - `woa13/025_KDS50` - 1/4-degree, KDS50 vertical levels scheme

    Note that the new ACCESS-OM2 runs all use the KDS vertical levels schemes (KDS50 at 1-degree and 1/4-degree, KDS75 at 1/10-degree).

    Let's first explore some of this data by looking at the 1-degree KDS50 experiment. First the netcdf files. Note that currently, because of the folder structure of the WOA13 data, the experiment names can be a bit opaque as they do not contain the woa13 string. Here we examine the 1-degree KDS50 data
    """)
    return


@app.cell
def _(catalog):
    cat_subset = catalog.search(name="WOA-13")
    return (cat_subset,)


@app.cell
def _(cat_subset):
    woa13_01 = cat_subset["WOA-13"].search(file_id='ocean.fx.GRID_X_T:3600.GRID_Y_T:2700.ZT:75.3074755ecbbb1caf').to_dask(xarray_open_kwargs={"use_cftime": True})

    woa13_025 = cat_subset["WOA-13"].search(file_id='ocean.fx.GRID_X_T:1440.GRID_Y_T:1080.ZT:50.1a63c55cfeecc896').to_dask(xarray_open_kwargs={"use_cftime": True})
    woa13_025_KDS50 = cat_subset["WOA-13"].search(file_id='ocean.fx.GRID_X_T:1440.GRID_Y_T:1080.ZT:50.32020de7a4439aa0').to_dask(xarray_open_kwargs={"use_cftime": True})

    woa13_10 = cat_subset["WOA-13"].search(file_id='ocean.fx.GRID_X_T:360.GRID_Y_T:300.ZT:50.dddcd86326896f91').to_dask(xarray_open_kwargs={"use_cftime": True})
    woa13_10_KDS50 = cat_subset["WOA-13"].search(file_id='ocean.fx.GRID_X_T:360.GRID_Y_T:300.ZT:50.34b05ef0b2b8ac49').to_dask(xarray_open_kwargs={"use_cftime": True})

    woa13_10_KDS75 = cat_subset["WOA-13"].search(file_id='ocean.fx.GRID_X_T:360.GRID_Y_T:300.ZT:75.4f9b6169e024b84e').to_dask(xarray_open_kwargs={"use_cftime": True})
    return woa13_01, woa13_025_KDS50, woa13_10_KDS50


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Comparing to ACCESS-OM2 simulations

    Now lets plot some biases against the WOA13 data set. We will use the original ACCESS-OM2 IAF runs, so first define a dictionary with information on those runs
    """)
    return


@app.cell
def _():
    from collections import OrderedDict
    exptdict = OrderedDict([
        ('1degIAF', # 1deg IAF run from Kiss et al. 2020
         {'model': 'ACCESS-OM2 IAF', 'expt': '1deg_jra55_iaf_omip2_cycle5',
          'n_files': -12, 'itime': '1998-01-01', 'ftime': None}),
        ('025degIAF', # 025deg IAF run from Kiss et al. 2020
         {'model': 'ACCESS-OM2-025 IAF', 'expt': '025deg_jra55_iaf_omip2_cycle5',
          'n_files': -34, 'itime': '1998-01-01', 'ftime': None}),
        ('01degIAF', # 01deg IAF run from Kiss et al. 2020
         {'model': 'ACCESS-OM2-01 IAF',  'expt': '01deg_jra55v140_iaf_cycle4',
          'n_files': None, 'itime': '1998-01-01','ftime': None})
    ])
    return (exptdict,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For each of these runs we then attach information to these dictionaries containing the matched WOA13 interpolated data sets. Note that we include a file name (with wildcards) so that we only use the monthly files and not the additional `ocean_temp_salt.res.nc` initial condition file.
    """)
    return


@app.cell
def _(exptdict, woa13_01, woa13_025_KDS50, woa13_10_KDS50):
    # Add on pre-interpolated WOA13 directories for every run:
    for _ekey in exptdict.keys():
        _e = exptdict[_ekey]
        if _ekey.find('025deg') != -1:
            _e['WOA13expt'] = '025_KDS50'
            _e['WOA13array'] = woa13_025_KDS50
        elif _ekey.find('01deg') != -1:
            _e['WOA13expt'] = '01'
            _e['WOA13array'] = woa13_01
        else:
            _e['WOA13expt'] = '10_KDS50'
            _e['WOA13array'] = woa13_10_KDS50
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## SST and SSS biases

    We will start by plotting SST and SSS biases compared to WOA13. The following loop loads data from the model runs and the corresponding WOA13 data and saves them into the previous dictionary (as entries SST, SST_WOA13 and SST_anom and the same for SSS). This can take time...
    """)
    return


@app.cell
def _(catalog, datetime, exptdict):
    for _ekey in exptdict.keys():
        _e = exptdict[_ekey]
        cat_subset_1 = catalog[_e['expt']]
        _var_search = cat_subset_1.search(variable='temp')
        _darray = _var_search.to_dask(xarray_open_kwargs={'decode_timedelta': True})
        _darray = _darray['temp']
        _darray = _darray.sel(time=slice(_e['itime'], _e['ftime']))
        surface_temp = _darray.isel(st_ocean=0)
        _tstart = datetime.datetime.fromtimestamp(surface_temp.time.item(0) * 1e-09)
        _tend = datetime.datetime.fromtimestamp(surface_temp.time.item(-1) * 1e-09)
        _e['yearrange'] = '{} to {}'.format(_tstart.strftime('%Y-%m'), _tend.strftime('%Y-%m'))
        print(f"{_ekey}: {_e['yearrange']}")
        _e['SST'] = surface_temp.mean('time').load() - 273.15
        _darray = _e['WOA13array']
        _darray = _darray['temp']
        _e['SST_WOA13'] = _darray.isel(ZT=0).mean('time').load()
        SST_anom = _e['SST'] - _e['SST_WOA13'].values
        _e['SST_anom'] = SST_anom.load()
        cat_subset_1 = catalog[_e['expt']]
        _var_search = cat_subset_1.search(variable='salt')
        _darray = _var_search.to_dask(xarray_open_kwargs={'decode_timedelta': True})
        _darray = _darray['salt']
        _darray = _darray.sel(time=slice(_e['itime'], _e['ftime']))
        surface_salt = _darray.isel(st_ocean=0)
        _e['SSS'] = surface_salt.mean('time').load()
        _darray = _e['WOA13array']
        _darray = _darray['salt']
        _e['SSS_WOA13'] = _darray.isel(ZT=0).mean('time').load()
        SSS_anom = _e['SSS'] - _e['SSS_WOA13'].values
        _e['SSS_anom'] = SSS_anom.load()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now that all the data is loaded, all we have to do is plot it.

    We first define a function to plot the SST
    """)
    return


@app.cell
def _(ccrs, cft, cm, exptdict, np, plt):
    def plot_SST(ekeys):
        clev = np.arange(-3, 3.25, 0.25)
        land_50m = cft.NaturalEarthFeature('physical', 'land', '50m', edgecolor='black', facecolor='gray', linewidth=0.5)
        for i, _ekey in enumerate(_ekeys):
            _e = exptdict[_ekey]
            ax1 = plt.subplot(1 + len(_ekeys) // 2, 2, i + 1, projection=ccrs.Robinson(central_longitude=-100))
            ax1.coastlines(resolution='50m')
            ax1.add_feature(land_50m)
            pn = _e['SST_anom'].plot.contourf(cmap=cm.cm.balance, levels=clev, add_colorbar=False, transform=ccrs.PlateCarree())
            plt.title('({}) {}, {}'.format(chr(ord('a') + i), _e['model'], _e['yearrange']))
            if i == 0:
                p0 = pn
        i = i + 1
        _e = exptdict['01degIAF']
        ax1 = plt.subplot(1 + len(_ekeys) // 2, 2, i + 1, projection=ccrs.Robinson(central_longitude=-100))
        ax1.coastlines(resolution='50m')
        ax1.add_feature(land_50m)  #1:
        pn = _e['SST_WOA13'].plot.contourf(cmap=cm.cm.thermal, levels=np.arange(-2.0, 32.0, 1.0), add_colorbar=False, transform=ccrs.PlateCarree())  # save plot for colourbar
        plt.title('({}) WOA13'.format(chr(ord('a') + i)))
        ax5 = plt.axes([0.92, 0.52, 0.01, 0.33])
        cb = plt.colorbar(p0, cax=ax5, orientation='vertical')
        cb.ax.set_ylabel('SST anomaly (°C)')
        ax6 = plt.axes([0.92, 0.13, 0.01, 0.33])
        cb = plt.colorbar(pn, cax=ax6, orientation='vertical')
        cb.ax.set_ylabel('SST (°C)')

    return (plot_SST,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We now plot IAF and RYF SST biases at 3 resolutions:
    """)
    return


@app.cell
def _(plot_SST, plt):
    _fig = plt.figure(figsize=(14, 10))
    _ekeys = ['01degIAF', '025degIAF', '1degIAF']
    plot_SST(_ekeys)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Then we do the same for sea surface salinity biases
    """)
    return


@app.cell
def _(ccrs, cft, cm, exptdict, np, plt):
    def plot_SSS(ekeys):
        clev = np.arange(-1.5, 1.6, 0.1)
        land_50m = cft.NaturalEarthFeature('physical', 'land', '50m', edgecolor='black', facecolor='gray', linewidth=0.5)
        for i, _ekey in enumerate(_ekeys):
            _e = exptdict[_ekey]
            ax1 = plt.subplot(1 + len(_ekeys) // 2, 2, i + 1, projection=ccrs.Robinson(central_longitude=-100))
            ax1.coastlines(resolution='50m')
            ax1.add_feature(land_50m)
            pn = _e['SSS_anom'].plot.contourf(cmap=cm.cm.balance, levels=clev, add_colorbar=False, transform=ccrs.PlateCarree())
            plt.title('({}) {}, {}'.format(chr(ord('a') + i), _e['model'], _e['yearrange']))
            if i == 1:
                p0 = pn
        i = i + 1
        _e = exptdict['01degIAF']
        ax1 = plt.subplot(1 + len(_ekeys) // 2, 2, i + 1, projection=ccrs.Robinson(central_longitude=-100))
        ax1.coastlines(resolution='50m')
        ax1.add_feature(land_50m)
        pn = _e['SSS_WOA13'].plot.contourf(cmap=cm.cm.thermal, levels=np.arange(31.0, 36.2, 0.2), add_colorbar=False, transform=ccrs.PlateCarree())  # save plot for colourbar
        plt.title('({}) WOA13'.format(chr(ord('a') + i)))
        ax5 = plt.axes([0.92, 0.52, 0.01, 0.33])
        cb = plt.colorbar(p0, cax=ax5, orientation='vertical')
        cb.ax.set_ylabel('SSS anomaly (psu)')
        ax6 = plt.axes([0.92, 0.13, 0.01, 0.33])
        cb = plt.colorbar(pn, cax=ax6, orientation='vertical')
        cb.ax.set_ylabel('SSS (psu)')

    return (plot_SSS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot IAF and RYF SSS biases at 3 resolutions:
    """)
    return


@app.cell
def _(plot_SSS, plt):
    _fig = plt.figure(figsize=(14, 10))
    _ekeys = ['01degIAF', '025degIAF', '1degIAF']
    plot_SSS(_ekeys)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Equatorial Pacific Temperature and Salinity Longitude-depth biases

    Our final example compares temperature and salinity biases in the tropical Pacific (note, this overlaps somewhat with the `Equatorial_thermal_and_zonal_velocity_structure.ipynb` documented example).

    We follow the same procedure as before, first loading the data.
    """)
    return


@app.cell
def _(catalog, datetime, exptdict):
    for _ekey in exptdict.keys():
        _e = exptdict[_ekey]
        cat_subset_2 = catalog[_e['expt']]
        _var_search = cat_subset_2.search(variable='temp')
        _darray = _var_search.to_dask(xarray_open_kwargs={'decode_timedelta': True})
        _darray = _darray['temp']
        _darray = _darray.sel(time=slice(_e['itime'], _e['ftime']))
        eq_temp = _darray.sel(yt_ocean=0, method='nearest')
        _tstart = datetime.datetime.fromtimestamp(eq_temp.time.item(0) * 1e-09)
        _tend = datetime.datetime.fromtimestamp(eq_temp.time.item(-1) * 1e-09)
        _e['yearrange'] = '{} to {}'.format(_tstart.strftime('%Y-%m'), _tend.strftime('%Y-%m'))
        print(f"{_ekey}: {_e['yearrange']}")
        _darray = _e['WOA13array']
        _darray = _darray['temp']
        _e['eq_temp_WOA13'] = _darray.sel(GRID_Y_T=0.0, method='nearest').mean('time')
        eq_temp_anom = eq_temp.mean('time') - 273.15 - _e['eq_temp_WOA13'].values
        eq_temp_anom.attrs['units'] = 'degrees Celsius'
        _e['eq_temp_anom'] = eq_temp_anom.load()
        cat_subset_2 = catalog[_e['expt']]
        _var_search = cat_subset_2.search(variable='salt')
        _darray = _var_search.to_dask(xarray_open_kwargs={'decode_timedelta': True})
        _darray = _darray['salt']
        _darray = _darray.sel(time=slice(_e['itime'], _e['ftime']))
        eq_salt = _darray.sel(yt_ocean=0, method='nearest')
        _darray = _e['WOA13array']
        _darray = _darray['salt']
        _e['eq_salt_WOA13'] = _darray.sel(GRID_Y_T=0.0, method='nearest').mean('time')
        eq_salt_anom = eq_salt.mean('time') - _e['eq_salt_WOA13'].values
        _e['eq_salt_anom'] = eq_salt_anom.load()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Then plotting equatorial plots of temperature biases
    """)
    return


@app.cell
def _(exptdict, np, plt):
    # Define a function to plot Equatorial Slices of temperature:
    def plot_eqtemp(ekeys):
        clev = np.arange(-3.0, 3.25, 0.25)
        for i, _ekey in enumerate(_ekeys):  # Define contour levels
            _e = exptdict[_ekey]
            ax1 = plt.subplot(int(np.ceil(len(_ekeys) / 2)), 2, i + 1)
            pn = _e['eq_temp_anom'].plot.contourf(cmap='bwr', levels=clev, add_colorbar=False, yincrease=False)  # Loop through models
            CS = _e['eq_temp_WOA13'].plot.contour(levels=np.arange(0, 32, 2), colors='k')
            ax1.clabel(CS, inline=False, fmt='%d', fontsize=15)
            _e['eq_temp_WOA13'].plot.contour(levels=[20.0], colors='k', linewidths=3.0)
            (_e['eq_temp_anom'] + _e['eq_temp_WOA13'].values).plot.contour(levels=[20.0], colors='k', linewidths=3.0, linestyles='--')
            plt.title('({}) {}, {}'.format(chr(ord('a') + i), _e['model'], _e['yearrange']))  # Plot bias as color
            ax1.set_ylim([300.0, 0.0])
            ax1.set_xlim([-220.0, -80.0])
            ax1.set_ylabel('Depth (m)')  # Plot WOA13 isotherms (and 20C bold)
            ax1.set_xlabel('Longitude ($^\\circ$E)')
            if i == 0:
                ax1.text(-210.0, 275.0, 'WOA13 Isotherms', fontsize=15)
                p0 = pn
        ax5 = plt.axes([0.92, 0.2, 0.01, 0.5])
        cb = plt.colorbar(p0, cax=ax5, orientation='vertical')
        cb.ax.set_ylabel('Temperature anomaly (°C)')  # Add annotations

    return (plot_eqtemp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot temperature comparison of IAF simulations.
    """)
    return


@app.cell
def _(plot_eqtemp, plt):
    _fig = plt.figure(figsize=(14, 12))
    _ekeys = ['1degIAF', '025degIAF', '01degIAF']
    plot_eqtemp(_ekeys)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And finally, repeat the same for salinity.
    """)
    return


@app.cell
def _(exptdict, np, plt):
    # Define a function to plot Equatorial Slices of salinity
    def plot_eqsalt(ekeys):
        clev = np.arange(-1.0, 1.1, 0.1)
        for i, _ekey in enumerate(_ekeys):  # Define contour levels
            _e = exptdict[_ekey]
            ax1 = plt.subplot(int(np.ceil(len(_ekeys) / 2)), 2, i + 1)
            pn = _e['eq_salt_anom'].plot.contourf(cmap='bwr', levels=clev, add_colorbar=False, yincrease=False)  # Loop through models
            CS = _e['eq_salt_WOA13'].plot.contour(levels=np.arange(30.0, 36.1, 0.1), colors='k')
            ax1.clabel(CS, inline=False, fmt='%3.2f', fontsize=15)
            plt.title('({}) {}, {}'.format(chr(ord('a') + i), _e['model'], _e['yearrange']))
            ax1.set_ylim([300.0, 0.0])
            ax1.set_xlim([-220.0, -80.0])  # Plot bias as color
            ax1.set_ylabel('Depth (m)')
            ax1.set_xlabel('Longitude ($^\\circ$E)')
            if i == 0:  # Plot WOA13 salinity (and 20C bold)
                ax1.text(-210.0, 275.0, 'WOA13 Isohalines', fontsize=15)
                p0 = pn
        ax5 = plt.axes([0.92, 0.2, 0.01, 0.5])
        cb = plt.colorbar(p0, cax=ax5, orientation='vertical')  # Add annotations
        cb.ax.set_ylabel('Salinity anomaly (psu)')

    return (plot_eqsalt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot salinity comparisson for IAF simulations.
    """)
    return


@app.cell
def _(plot_eqsalt, plt):
    _fig = plt.figure(figsize=(14, 12))
    _ekeys = ['1degIAF', '025degIAF', '01degIAF']
    plot_eqsalt(_ekeys)
    return


if __name__ == "__main__":
    app.run()
