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
    # Meridional Heat Transport

    ## (MOM5)

    This recipe calculates the model's meridional heat transport (MHT) using two methods based on distinct MOM5 diagnostics. The methods and the caveats associated with them are listed below:

    ### Method 1: Using online diagnostics

    This is the recommended method. In MOM5 the meridional heat transported associated to resolved advection is given by the `temp_yflux_adv_int_z`. The heat fluxes associated to parametrised processes are provided in separate diagnostics (like `temp_yflux_gm` and `temp_yflux_ndiffuse` for the mesoscale parametrisations and `temp_yflux_submeso` for the submesoscale parametrisations).

    This recipe uses ACCESS-OM2-01, which does not have mesoscale parametrisations (and therefore no `temp_yflux_gm` or `temp_yflux_ndiffuse`). We further assume the heat flux due to submesoscale parametrisation (`temp_yflux_submeso`) is small and that the bulk of the meridional heat flux is due to resolved advection `temp_yflux_adv_int_z`.

    ### Method 2: Using surface and frazil heat fluxes

    This is an alternative method that approximates the meridional heat transport from surface heat fluxes for the simulations in which the online diagnostics needed in Method 1 are not available. Note that this method relies on a steady state assumption. We use two diagnostics: `net_sfc_heating` (net surface heat flux) and `frazil_3d_int_z` which is the heat flux due to frazil formation at higher latitudes.

    The recipe calculates the total (all basins) MHT, and it also includes comparisons to a few observational products. Basin-specific MHT can be calculated by defining relevant masks.

    ## Information needed to adapt to MOM6

    The diagnostics for meridional heat transports are called `T_ady_2d` (from resolved advection), `T_diffy_2d` (from diffusion) and `hfds` for the surface heat flux (includes frazil contribution).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MOM5 recipe
    """)
    return


@app.cell
def _():
    import intake

    import numpy as np
    import xarray as xr

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cmocean

    from dask.distributed import Client
    import warnings
    warnings.filterwarnings("ignore", category = FutureWarning)
    warnings.filterwarnings("ignore", category = UserWarning)
    warnings.filterwarnings("ignore", category = RuntimeWarning)
    return Client, intake, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start dask cluster.
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
    Load ACCESS-NRI default catalog
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define experiment of interest
    """)
    return


@app.cell
def _():
    experiment = '01deg_jra55v140_iaf_cycle3'
    start_time = '2000-01-01'
    end_time = '2005-12-31'
    return end_time, experiment, start_time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We are now ready to load the data to start our analysis. We load `temp_yflux_adv_int_z`. For this example, we have chosen to use 6 years of output.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Method 1: Using online diagnostics
    """)
    return


@app.cell
def _(catalog, end_time, experiment, start_time):
    ds_adv = catalog[experiment].search(variable = ['temp_yflux_adv_int_z'], frequency='1mon').to_dask(xarray_open_kwargs={"decode_timedelta": True})
    ds_adv = ds_adv['temp_yflux_adv_int_z'].sel(time=slice(start_time, end_time))
    ds_adv
    return (ds_adv,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We convert the dataset from Watts (W) to PetaWatts (PW).
    """)
    return


@app.cell
def _(ds_adv):
    ds_adv_1 = ds_adv * 1e-15
    ds_adv_1.attrs['units'] = 'PetaWatts'
    ds_adv_1
    return (ds_adv_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    and then we compute the mean across `time` and sum over all longitudes.
    """)
    return


@app.cell
def _(ds_adv_1):
    MHT_method_1 = ds_adv_1.mean('time').sum('xt_ocean')
    return (MHT_method_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Method 2: Using surface and frazil heat fluxes
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First, we load the surface heat flux and grid metrics:
    """)
    return


@app.cell
def _(catalog, end_time, experiment, start_time):
    ds_sfc = catalog[experiment].search(variable = ['net_sfc_heating'], frequency='1mon').to_dask(xarray_open_kwargs={"decode_timedelta": True})
    ds_sfc = ds_sfc['net_sfc_heating'].sel(time=slice(start_time, end_time))
    ds_sfc
    return (ds_sfc,)


@app.cell
def _(catalog, end_time, experiment, start_time):
    ds_frz = catalog[experiment].search(variable = ['frazil_3d_int_z'], frequency='1mon').to_dask(xarray_open_kwargs={"decode_timedelta": True})
    ds_frz = ds_frz['frazil_3d_int_z'].sel(time=slice(start_time, end_time))
    ds_frz
    return (ds_frz,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Add the heat fluxes and take the `time` mean:
    """)
    return


@app.cell
def _(ds_frz, ds_sfc):
    shflux = (ds_sfc + ds_frz).mean('time').load()
    return (shflux,)


@app.cell
def _(catalog, experiment):
    # Get the relevant grid_info
    area = catalog[experiment].search(variable='area_t', frequency='fx').to_dask()['area_t']
    geolat_t = catalog[experiment].search(variable='geolat_t', frequency='fx').to_dask()['geolat_t']
    geolon_t = catalog[experiment].search(variable='geolon_t', frequency='fx').to_dask()['geolon_t']
    return area, geolat_t, geolon_t


@app.cell
def _(area, geolat_t, geolon_t, shflux):
    # Add geolat_t and geolon_t coords
    area_1 = area.assign_coords({'geolon_t': geolon_t, 'geolat_t': geolat_t})
    shflux_1 = shflux.assign_coords({'geolon_t': geolon_t, 'geolat_t': geolat_t})
    return area_1, shflux_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now calculate Meridional Heat Flux (MHF). This is done by calculating the total heat flux as the heat flux times the area, and then integrating in latitude space such that for each latitude:

    $$
    \mathrm{MHF}(y) = \int_{y_{0}}^{y} (\mathrm{SHFLUX} \times \mathrm{AREA}) \, \mathrm{d}y
    $$
    """)
    return


@app.cell
def _(area_1, np, shflux_1):
    # Create left edge for bottom bin
    latv_bins = np.hstack(([-90], area_1['yt_ocean'].values))
    MHT = shflux_1 * area_1
    MHT = MHT.groupby_bins('geolat_t', latv_bins)
    MHT = MHT.sum()
    MHT = MHT.cumsum()
    MHT = MHT.rename(geolat_t_bins='yt_ocean')
    MHT.coords['yt_ocean'] = area_1['yt_ocean']
    MHT_method_2 = MHT + (MHT.isel(yt_ocean=0) - MHT.isel(yt_ocean=-1)) / 2
    MHT_method_2 = MHT_method_2 * 1e-15
    # Convert to petawatt
    MHT_method_2.attrs['units'] = 'PetaWatts'
    return (MHT_method_2,)


@app.cell
def _(MHT_method_1, MHT_method_2, plt):
    _fig = plt.figure(figsize=(9, 6))
    _ax = _fig.add_subplot()
    MHT_method_1.plot(ax=_ax, color='blue', label='Method 1')
    MHT_method_2.plot(ax=_ax, color='green', label='Method 2')
    plt.legend(frameon=False, fontsize=12)
    plt.axhline(y=0, linewidth=1, color='black')
    # add legend
    plt.ylim(-2.25, 2.75)
    plt.title('Global Ocean Meridional Heat Transport', fontsize=18)
    plt.xlabel('Latitude')
    # limits along the y axis
    # add titles and labels
    plt.ylabel('$10^{15}$ Watts')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Comparison between model output and observations

    The following section compares the model's heat transport to observations. These observations are derived using various methods, in particular using surface flux observations a la method 2 (which assumes a steady state).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Read ERBE Period Ocean and Atmospheric Heat Transport

    This data comes (annoyingly) in a text file. The cell below opens and saves latitudes and heat transport into two separate lists:
    """)
    return


@app.cell
def _():
    # Path to the file containing observations
    _filename = '/g/data3/ik11/from_hh5_tmp/cosima/observations/original/MHT/obs_vq_am_estimates.txt'
    erbe_MHT = []
    # Create empty variables to store our observations
    erbe_lat = []
    with open(_filename) as _f:
        for _line in _f.readlines()[1:96]:
    # Open data and save it to empty variables above
            _line = _line.strip()
            _sline = _line.split()  #Open each line from rows 1 to 96
            erbe_lat.append(float(_sline[0]))
            erbe_MHT.append(float(_sline[3]))  #Separating each line to extract data  #Extracting latitude and MHT and saving to empty variables
    return erbe_MHT, erbe_lat


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Read NCEP and ECMWF Oceanic and Atmospheric Transport Products

    These datasets are available at https://climatedataguide.ucar.edu/climate-data. We use a climatological mean of surface fluxes or vertically integrated total energy divergence for oceanic and atmospheric transports respectively for the period between February 1985 - April 1989.

    This also comes as a text file and again, we will save it into lists. There is also an estimate of the observational error:
    """)
    return


@app.cell
def _():
    #Path to the file containing observations
    _filename = '/g/data/ik11/observations/ANNUAL_TRANSPORTS_1985_1989.ascii'
    ncep_g_mht = []
    #Creating empty variables to store our observations
    ecwmf_g_mht = []
    ncep_g_err = []
    ecwmf_g_err = []
    ncep_a_mht = []
    ecwmf_a_mht = []
    ncep_a_err = []
    ecwmf_a_err = []
    ncep_p_mht = []
    ecwmf_p_mht = []
    ncep_p_err = []
    ecwmf_p_err = []
    ncep_i_mht = []
    ecwmf_i_mht = []
    ncep_i_err = []
    ecwmf_i_err = []
    ncep_ip_mht = []
    ecwmf_ip_mht = []
    ncep_ip_err = []
    ecwmf_ip_err = []
    o_lat = []
    with open(_filename) as _f:
        for _line in _f.readlines()[1:]:
    #Opening data and saving it to empty variables above
            _line = _line.strip()
    #Open each line in file (ignoring the first row)
            _sline = _line.split()
            o_lat.append(float(_sline[0]) * 0.01)  #Separating each line to extract data
            ncep_g_mht.append(float(_sline[4]) * 0.01)
            ecwmf_g_mht.append(float(_sline[5]) * 0.01)
            ncep_a_mht.append(float(_sline[7]) * 0.01)  #Extracting values and saving to correct variable defined above
            ncep_p_mht.append(float(_sline[8]) * 0.01)  # T42 latitudes (north to south)
            ncep_i_mht.append(float(_sline[9]) * 0.01)  # Residual Ocean Transport - NCEP
            ncep_g_err.append(float(_sline[10]) * 0.01)  # Residual Ocean Transport - ECWMF
            ncep_a_err.append(float(_sline[11]) * 0.01)  # Atlantic Ocean Basin Transport - NCEP
            ncep_p_err.append(float(_sline[12]) * 0.01)  # Pacific Ocean Basin Transport - NCEP
            ncep_i_err.append(float(_sline[13]) * 0.01)  # Indian Ocean Basin Transport - NCEP
            ecwmf_a_mht.append(float(_sline[15]) * 0.01)  # Error Bars for NCEP Total Transports
            ecwmf_p_mht.append(float(_sline[16]) * 0.01)  # Error Bars for NCEP Atlantic Transports 
            ecwmf_i_mht.append(float(_sline[17]) * 0.01)  # Error Bars for NCEP Pacific Transports 
            ecwmf_g_err.append(float(_sline[18]) * 0.01)  # Error Bars for NCEP Indian Transports 
            ecwmf_a_err.append(float(_sline[19]) * 0.01)  # Atlantic Ocean Basin Transport - ECWMF
            ecwmf_p_err.append(float(_sline[20]) * 0.01)  # Pacific Ocean Basin Transport - ECWMF
            ecwmf_i_err.append(float(_sline[21]) * 0.01)  # Indian Ocean Basin Transport - ECWMF
    ncep_ip_mht = [a + b for a, b in zip(ncep_p_mht, ncep_i_mht)]  # Error Bars for ECWMF Total Transports
    ecwmf_ip_mht = [a + b for a, b in zip(ecwmf_p_mht, ecwmf_i_mht)]  # Error Bars for NCEP Atlantic Transports
    ncep_ip_err = [max(a, b) for a, b in zip(ncep_p_err, ncep_i_err)]  # Error Bars for NCEP Pacific Transports
    #Calculating MHT
    ecwmf_ip_err = [max(a, b) for a, b in zip(ecwmf_p_err, ecwmf_i_err)]  # Error Bars for NCEP Indian Transports
    return ecwmf_g_err, ecwmf_g_mht, ncep_g_err, ncep_g_mht, o_lat


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Plotting model outputs against observations

    We plot the global meridional heat transport as calculated from model outputs (blue line) and observations.
    """)
    return


@app.cell
def _(
    MHT_method_1,
    MHT_method_2,
    ecwmf_g_err,
    ecwmf_g_mht,
    erbe_MHT,
    erbe_lat,
    ncep_g_err,
    ncep_g_mht,
    o_lat,
    plt,
):
    _fig = plt.figure(figsize=(9, 6))
    _ax = _fig.add_subplot(1, 1, 1)
    MHT_method_1.plot(ax=_ax, color='blue', label='ACCESS-OM2-025 (MHF diagnostic)')
    #Plotting MHT from model outputs
    MHT_method_2.plot(ax=_ax, color='green', label='ACCESS-OM2-025 (shflux)')
    _ax.plot(erbe_lat, erbe_MHT, 'k--', linewidth=1, label='ERBE, JRA-25, NCEP/NCAR, and ERA40')
    plt.errorbar(o_lat[::-1], ncep_g_mht[::-1], yerr=ncep_g_err[::-1], c='gray', fmt='s', markerfacecolor='k', markersize=3, capsize=2, linewidth=1, label='NCEP')
    #Adding observations and error bars for observations
    plt.errorbar(o_lat[::-1], ecwmf_g_mht[::-1], yerr=ecwmf_g_err[::-1], c='gray', fmt='D', markerfacecolor='white', markersize=3, capsize=2, linewidth=1, label='ECWMF')
    plt.errorbar(24, 1.5, yerr=0.3, fmt='o', c='black', markersize=3, capsize=2, linewidth=1, label='Macdonald and Wunsch 1996')
    plt.errorbar(-30, -0.9, yerr=0.3, fmt='o', c='black', markersize=3, capsize=2, linewidth=1)
    plt.errorbar(24, 2.0, yerr=0.3, fmt='x', c='green', markersize=3, capsize=2, linewidth=1, label='Lavin et al. and Bryden et al.')
    plt.errorbar(24, 1.83, yerr=0.28, fmt='^', c='red', markersize=4, capsize=2, linewidth=1, label='Ganachaud and Wunsch 2003')
    plt.errorbar(-30, -0.6, yerr=0.3, fmt='^', c='red', markersize=4, capsize=2, linewidth=1)
    plt.errorbar(-19, -0.8, yerr=0.3, fmt='^', c='red', markersize=4, capsize=2, linewidth=1)
    plt.errorbar(47, 0.6, yerr=0.1, fmt='^', c='red', markersize=4, capsize=2, linewidth=1)
    plt.legend(frameon=False, fontsize=10)
    plt.axhline(y=0, linewidth=1, color='black')
    plt.ylim(-2.25, 2.75)
    plt.title('Global Ocean Meridional Heat Transport', fontsize=18)
    plt.xlabel('Latitude')
    # add legend
    # limits along the y axis
    # add titles and labels
    plt.ylabel('$10^{15}$ Watts')
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
