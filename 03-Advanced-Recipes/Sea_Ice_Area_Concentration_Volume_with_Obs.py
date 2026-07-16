import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import subprocess

    return (subprocess,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Sea Ice Comparisons to Observations

    This script shows how to load and plot sea ice concentration from CICE output and compare it to the NSIDC CDR (National Snow and Ice Data Centre, Climate Data Record) dataset

    This notebook uses the _ACCESS-NRI Intake Catalog_ following the examples in [Tutorials/Using the Intake Catalog](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/01-Basics/02-ACCESS-NRI_Intake_Catalog.html).

    Requirements: The runs analysed here are only in access-nri-intake-catalog version 0.3.1 or newer, and xarray.DataTree introduced in xarray version v2024.10.0. This was tested using `conda/analysis3-25.05` from `/g/data/xp65/public/modules` and a _medium_ instance on _normalsr_ queue (although we recommend a larger instance if making iterative changes).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **OM2 Experiments:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    These are the ACCESS-OM2 runs we are going to use, we can compare results from prototype runs forced with ERA5 against normal runs using JRA55do, as [described on the ACCESS_HIVE](https://forum.access-hive.org.au/t/era-5-forced-access-om2-simulations/1103/5). To compare against the observational datasets, we use IAF (Inter-Annual Forcing). _N.B._ The JRA55do runs used here a slightly different to the typical (e.g. _025deg_jra55_iaf_omip2_cycle6_) in the model version used and the timeframes evaluated.
    """)
    return


@app.cell
def _():
    RUNS = {
        "025deg_era5": ["025deg_era5_iaf"],  # (our name: run name(s))
        "025deg_jra55": ["025deg_jra55_iaf_era5comparison"],
        "1deg_era5": ["1deg_era5_iaf"],
        "1deg_jra55": ["1deg_jra55_iaf_era5comparison"],
    }
    return (RUNS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We are going to look at Sea Ice Concentration and Sea Ice Volume
    """)
    return


@app.cell
def _():
    VARS = ["aice_m", "hi_m" ]  # ice area fraction or sea ice concentration, ice thickness averaged by grid cell area
    VARS_2D = ["area_t", "geolat_t", "geolon_t"]
    return VARS, VARS_2D


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Observational Data:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sea Ice concentration is measured through passive microwave remote sensing. We are going to use the NSIDC CDR Dataset (described at [nsidc.org](https://nsidc.org/data/g02202/versions/4))
    """)
    return


@app.cell
def _():
    OBS_TIME_SLICE = slice("1979", "2022")
    sh_obs_url = "https://polarwatch.noaa.gov/erddap/griddap/nsidcG02202v4shmday"
    nh_obs_url = "https://polarwatch.noaa.gov/erddap/griddap/nsidcG02202v4nhmday"
    return OBS_TIME_SLICE, sh_obs_url


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Load depenencies:**
    """)
    return


@app.cell
def _():
    import intake
    from xarray import DataTree, map_over_datasets

    from dask.distributed import Client

    import xarray as xr
    import numpy as np
    from datetime import timedelta
    import cf_xarray as cfxr
    import xesmf

    # plotting
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cmocean.cm as cmo
    import matplotlib.lines as mlines

    return (
        Client,
        DataTree,
        ccrs,
        cmo,
        intake,
        mlines,
        np,
        plt,
        timedelta,
        xesmf,
        xr,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A standard way to calculate climatologies. (We start in 1991 as earlier decades are influenced by model spin-up for 0.25deg runs which only start in 1980.)
    """)
    return


@app.cell
def _():
    CLIMAT_TIME_SLICE = slice('1991', '2020')

    def climatology(ds):
        return _ds.sel(time=CLIMAT_TIME_SLICE).groupby('time.month').mean('time')

    return (climatology,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start a dask client
    """)
    return


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)

    client.dashboard_link
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Open the _ACCESS-NRI Intake Catalog_
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Load the ACCESS-OM2 results
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For CICE data in OM2, we need to do some wrangling to make it easier to deal with. This is described in more detail in [DocumentedExamples/SeaIce_Plot_Example](https://cosima-recipes.readthedocs.io/en/latest/02-Easy-Recipes/Sea_Ice_Coordinates.html). Its included in this function:
    """)
    return


@app.cell
def _(catalog):
    def open_by_name(name, vars):
        """Return a dataset for the requested name and vars"""

        return (
            catalog[name]
            .search(variable=vars)
            .to_dask(
                xarray_open_kwargs={
                    "chunks": -1 ,
                    "decode_coords": False,
                },
                xarray_combine_by_coords_kwargs={
                    "compat": "override",
                    "data_vars": "minimal",
                    "coords": "minimal",
                },
            )
        )

    return (open_by_name,)


@app.cell
def _(RUNS, VARS_2D, open_by_name, timedelta, xr):
    def open_by_experiment(exp_name, vars):
        """Concatenate any datasets provided for this experiment into one ds, and add area and geo coordinates"""

        # get the data for each run of this config
        cice_ds = xr.concat(
            [open_by_name(iName, vars) for iName in RUNS[exp_name]], dim="time"
        )

        # We also want the area/lat/lon fields, these are separate datasets, so lets merge them.
        area_ds = xr.merge(
            [open_by_name(RUNS[exp_name][0], iVar) for iVar in VARS_2D]
        ).load()

        # Label the lats and lons
        cice_ds.coords["ni"] = area_ds["xt_ocean"].values
        cice_ds.coords["nj"] = area_ds["yt_ocean"].values

        # Copy attributes for cf compliance
        cice_ds.ni.attrs = area_ds.xt_ocean.attrs
        cice_ds.nj.attrs = area_ds.yt_ocean.attrs

        cice_ds = cice_ds.rename(({"ni": "xt_ocean", "nj": "yt_ocean"}))

        # Add the geolon, geolat, and area as extra co-ordinates fields from area_t

        cice_ds = cice_ds.assign_coords(
            {
                "geolat_t": area_ds.geolat_t,
                "geolon_t": area_ds.geolon_t,
                "area_t": area_ds.area_t,
            }
        )

        # cice timestamps are also misleading:
        cice_ds["time"] = cice_ds.time.to_pandas() - timedelta(minutes=1)

        return cice_ds

    return (open_by_experiment,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Because the dimensions are different for different experiments, they would not fit in a Dataset, a DataTree is required. The DataTree has a group for each experiment, which contains a xarray dataset with the data for that experiment.
    """)
    return


@app.cell
def _(RUNS, VARS, open_by_experiment):
    # magic command not supported in marimo; please file an issue to add support
    # %%time

    si_name_ds_pairs = dict()
    for run in RUNS.keys():
        si_name_ds_pairs[run] = open_by_experiment(run, VARS)
    return (si_name_ds_pairs,)


@app.cell
def _(DataTree, si_name_ds_pairs):
    si_dt = DataTree.from_dict(si_name_ds_pairs)
    return (si_dt,)


@app.cell
def _(np):
    def match_timestamps_to_CDR(ds):
        if _ds is None or 'time' not in _ds:
            return _ds  # root dataset in datatree is not used
        cice_ds = _ds.copy()
        cice_ds['time'] = [np.datetime64(str(i)[0:7] + '-01T00:00:00.000000000') for i in _ds.time.values]
        return cice_ds  # make a copy, datatree doesn't allow manipulating in place  # we are going to use the same timestamps as NSIDC

    return (match_timestamps_to_CDR,)


@app.cell
def _(match_timestamps_to_CDR, si_dt):
    si_dt_1 = si_dt.map_over_datasets(match_timestamps_to_CDR)
    return (si_dt_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The result is a datatree, with a dataset for each experiment and timestamps which align with the observational timestamps
    """)
    return


@app.cell
def _(si_dt_1):
    si_dt_1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Load the observational dataset
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The CDR dataset has the area of each grid cell provided as a separate file, which we need to load
    """)
    return


@app.cell
def _(np, xr):
    def open_cdr_dataset(path, area_file):
        _ds = xr.open_dataset(path).rename({'cdr_seaice_conc_monthly': 'cdr_conc', 'xgrid': 'x', 'ygrid': 'y'})
        areasNd = np.fromfile(area_file, dtype=np.int32).reshape(_ds.cdr_conc.isel(time=0).shape)
        areasKmNd_sh = areasNd / 1000
        _ds['area'] = xr.DataArray(areasKmNd_sh, dims=['y', 'x'])
        _ds = _ds.set_coords('area')  # # we also need the area of each gridcell
        _ds['cdr_conc'] = _ds.cdr_conc.where(_ds.cdr_conc <= 1)
        return _ds  # # Divide by 1000 to get km2 (https://web.archive.org/web/20170817210544/http://nsidc.org/data/polar-stereo/tools_geo_pixel.html#pixel_area)  # convert error codes to Nan

    return (open_cdr_dataset,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can pull the datasets direct from the url, however the cell area needs to be downloaded separately:
    """)
    return


@app.cell
def _(subprocess):
    #! wget --ftp-user=anonymous -nc ftp://sidads.colorado.edu/DATASETS/seaice/polar-stereo/tools/pss25area_v3.dat ftp://sidads.colorado.edu/DATASETS/seaice/polar-stereo/tools/psn25area_v3.dat
    subprocess.call(['wget', '--ftp-user=anonymous', '-nc', 'ftp://sidads.colorado.edu/DATASETS/seaice/polar-stereo/tools/pss25area_v3.dat', 'ftp://sidads.colorado.edu/DATASETS/seaice/polar-stereo/tools/psn25area_v3.dat'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We are interested in the Antarctic, but the lines for the Arctic are below and commented out.
    """)
    return


@app.cell
def _(DataTree, open_cdr_dataset, sh_obs_url):
    sh_cdr_xr = open_cdr_dataset(sh_obs_url, "pss25area_v3.dat")

    # nh_cdr_xr = open_cdr_dataset(
    #     nh_obs_url,
    #     'psn25area_v3.dat'
    # )

    cdr_dt = DataTree.from_dict(
        {
            "cdr_sh": sh_cdr_xr,
            # 'cdr_nh':nh_cdr_xr
        }
    )
    return (cdr_dt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The result is a datatree, with a datasets for the relevant hemisphere
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Calculate Sea Ice Area
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sea ice area is the circumpolar sum of sea ice concentration multiplied by the area of each grid cell. By convention, and because lower concentrations are not accurate when measured through remote sensing, concentrations below 0.15 are not included
    """)
    return


@app.function
def sea_ice_area(sic, area, range=[0.15, 1]):
    return (sic * area).where((sic >= range[0]) * (sic <= range[1])).cf.sum(["X", "Y"])


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Calculate for observational data, and remove gaps with missing data
    """)
    return


@app.cell
def _(OBS_TIME_SLICE, np):
    def sea_ice_area_obs(ds):
        if _ds is None or 'time' not in _ds:
            return _ds  # root dataset in datatree is not used
        sic = _ds.cdr_conc
        result = sea_ice_area(sic, sic.area).to_dataset(name='cdr_area')
        result.loc[{'time': '1988-01-01'}] = np.nan
        result.loc[{'time': '1987-12'}] = np.nan
        return result.sel(time=OBS_TIME_SLICE)  # Theres a couple of data gaps which should be nan

    return (sea_ice_area_obs,)


@app.cell
def _(cdr_dt, sea_ice_area_obs):
    obs_area_dt = cdr_dt.map_over_datasets(sea_ice_area_obs)
    # Theres another gap which should be nan in the arctic only
    # obs_area_dt['cdr_nh'].to_dataset().loc[{'time':'1984-07'}]=np.nan
    return (obs_area_dt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Calculate for model data, limit to southern hemisphere / Antarctica
    """)
    return


@app.function
def sea_ice_area_model_sh(ds):
    if _ds is None or 'time' not in _ds:  # root dataset in datatree is not used
        return _ds
    sic = _ds.aice_m.cf.sel(Y=slice(-90, 0))
    area_km2 = _ds.area_t / 1000000.0
    return sea_ice_area(sic, area_km2).to_dataset(name='si_area').load()


@app.cell
def _(si_dt_1):
    model_area_dt = si_dt_1.map_over_datasets(sea_ice_area_model_sh)
    return (model_area_dt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Sea Ice Area Trends
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We are going to compare the trends in the minima and maxima over time, and the monthly climatology
    """)
    return


@app.cell
def _(model_area_dt, xr):
    def min_and_max_year(da):
        result = xr.Dataset()
        result['min'] = da.min()
        result['max'] = da.max()
        return result

    def _min_and_max(ds):
        if _ds is None or 'time' not in _ds:  # root dataset in datatree is not used
            return _ds
        annual_min_max_ds = _ds.si_area.groupby('time.year').apply(min_and_max_year)
        return annual_min_max_ds
    model_min_max_dt = model_area_dt.map_over_datasets(_min_and_max)
    return (model_min_max_dt,)


@app.cell
def _(model_min_max_dt, obs_area_dt, plt):
    for _group in model_min_max_dt.groups[1:]:
        _ds = model_min_max_dt[_group].ds
        _ds['min'].plot(label=_group[1:])
    obs_area_dt['cdr_sh'].ds.cdr_area.groupby('time.year').min().plot(label='CDR')
    plt.title('Trends in Sea-Ice Minima')
    plt.ylabel('Sea-Ice Area ($km^2$)')
    _ = plt.legend()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We see that all models have sea ice area which is too low in summer. Model runs forced by JRA have more variability than those forced by ERA5 and are slightly closer to the measured sea ice area from observations.
    """)
    return


@app.cell
def _(model_min_max_dt, obs_area_dt, plt):
    for _group in model_min_max_dt.groups[1:]:
        _ds = model_min_max_dt[_group].ds.sel(year=slice(1950, 2022))
        _ds['max'].plot(label=_group[1:])
    obs_area_dt['cdr_sh'].ds.cdr_area.groupby('time.year').max().plot(label='CDR')  # drop 2023 because its incomplete
    plt.title('Trends in Sea-Ice Maxima')
    plt.ylabel('Sea-Ice Area ($km^2$)')
    _ = plt.legend()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We see that the closest runs are those forced by ERA5, and the runs forced by JRA55 are under representing Winter sea ice.
    """)
    return


@app.cell
def _(climatology, model_area_dt, obs_area_dt, plt):
    for _group in model_area_dt.groups[1:]:
        climatology(model_area_dt[_group].ds.si_area).plot(label=_group[1:])
    climatology(obs_area_dt['cdr_sh'].ds.cdr_area).plot(label='CDR')
    plt.title('Climatology of Sea-Ice Area')
    plt.ylabel('Sea-Ice Area ($km^2$)')
    plt.legend()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We see all model runs have too low sea ice in summer, and grow faster than observations in autumn and earlier that the observed maximum.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Sea Ice Concentration Anomalies
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To examine the differences between the model results and observations, we calculate difference in each grid cell between observations and each experiment

    As that data are on different grids, we need to regrid to compare the datasets

    Lets simplify a little to only look at 0.25 degree results
    """)
    return


@app.cell
def _():
    groups = ("/025deg_era5", "/025deg_jra55")
    return (groups,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The lat/lon of of each cell in the observational dataset are in a different file:
    """)
    return


@app.cell
def _(subprocess):
    #! wget -nc https://noaadata.apps.nsidc.org/NOAA/G02202_V5/ancillary/G02202-ancillary-pss25-v05r00.nc
    subprocess.call(['wget', '-nc', 'https://noaadata.apps.nsidc.org/NOAA/G02202_V5/ancillary/G02202-ancillary-pss25-v05r00.nc'])
    return


@app.cell
def _(xr):
    cdr_sps_ds = xr.open_dataset("G02202-ancillary-pss25-v05r00.nc")
    return (cdr_sps_ds,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can now build the re-gridder. This is described in detail in [DocumentedExamples/Regridding](https://cosima-recipes.readthedocs.io/en/latest/03-Advanced-Recipes/Horizontal_Regridding.html)
    """)
    return


@app.cell
def _(cdr_sps_ds, si_dt_1, xesmf):
    regridder_ACCESSOM2_025deg_sh = xesmf.Regridder(si_dt_1['025deg_era5'].ds.isel(time=0).drop_vars(['xt_ocean', 'yt_ocean']), cdr_sps_ds, 'bilinear', periodic=True, unmapped_to_nan=True)
    return (regridder_ACCESSOM2_025deg_sh,)


@app.cell
def _(cdr_dt, groups, regridder_ACCESSOM2_025deg_sh, si_dt_1, xr):
    aice_sh_3976_ds = xr.Dataset()
    aice_sh_anom_ds = xr.Dataset()
    for iG in groups:
        aice_sh_3976_ds[iG] = regridder_ACCESSOM2_025deg_sh(si_dt_1[iG].ds.aice_m.copy())
        aice_sh_anom_ds[iG] = aice_sh_3976_ds[iG] - cdr_dt['cdr_sh'].ds.cdr_conc
    return aice_sh_3976_ds, aice_sh_anom_ds


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can now plot the difference between modelled and observed sea ice concentration
    """)
    return


@app.cell
def _(
    aice_sh_3976_ds,
    aice_sh_anom_ds,
    ccrs,
    cdr_dt,
    climatology,
    cmo,
    mlines,
    np,
    plt,
):
    months = [2, 9]  # february, september
    month_names = ['Feb', 'Sep']
    n_months = len(months)
    plt.figure(figsize=(9, n_months * 3))
    cdr = climatology(cdr_dt['cdr_sh'].ds.cdr_conc)
    for j, _group in enumerate(aice_sh_anom_ds.data_vars):
        anoms = climatology(aice_sh_anom_ds[_group])
        aice = climatology(aice_sh_3976_ds[_group])
        for i, iMonth in enumerate(months):
            plt.subplot(n_months, 3, j + 1 + i * 3, projection=ccrs.SouthPolarStereo(true_scale_latitude=-70))
            _ds = anoms.sel(month=iMonth).compute()
            plt.contourf(_ds.x, _ds.y, _ds, levels=np.arange(-0.85, 0.86, 0.1), cmap=cmo.balance_r)
            cs_cdr = cdr.sel(month=iMonth).plot.contour(levels=[0.15], colors=['yellow'])
            cs_mod = aice.sel(month=iMonth).plot.contour(levels=[0.15], colors=['black'])
            plt.title(month_names[i] + '_' + _group[1:])
    line_cdr = mlines.Line2D([], [], color='yellow', label='Observed Extent')
    line_mod = mlines.Line2D([], [], color='black', label='Modelled Extent')
    plt.legend(handles=[line_cdr, line_mod], loc='center left', bbox_to_anchor=(1.2, 0.5))
    cax = plt.axes([0.7, 0.6, 0.05, 0.2])
    # Messy legend creation
    # And colorbar
    _ = plt.colorbar(cax=cax, label='Difference in \nSea Ice Concentration')  # Filled contours with concentration anomalies in this month  # Lines at 15% concentration (approx ice edge)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We see that OM2 under-represents sea ice in Summer, particularly in the Weddell Sea. In Winter, trends are less clear, although ERA5 forced sea ice concentration is too high at the northern boundary.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Sea Ice Volume
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can calculate volume in much the same way as area, except _vicen_ is volume (per unit area) in each of 5 thickness classes, so we can sum this for the volume irrespective of thickness.
    """)
    return


@app.cell
def _(np):
    def sea_ice_vol_model_sh(ds):
        if _ds is None or 'time' not in _ds:  # root dataset in datatree is not used
            return _ds
        vice_m = _ds.hi_m.sel(yt_ocean=slice(-90, 0))
        siv_total_da = (vice_m * _ds.area_t).where(~np.isnan(_ds.area_t)).cf.sum(['longitude', 'latitude'])
        return siv_total_da.to_dataset(name='si_vol').load()

    return (sea_ice_vol_model_sh,)


@app.cell
def _(sea_ice_vol_model_sh, si_dt_1):
    si_vol_dt = si_dt_1.map_over_datasets(sea_ice_vol_model_sh)
    return (si_vol_dt,)


@app.cell
def _(si_vol_dt, xr):
    def _min_and_max(ds):
        if _ds is None or 'time' not in _ds:
            return _ds

        def min_and_max_year(da):
            result = xr.Dataset()
            result['min'] = da.min()
            result['max'] = da.max()
            return result
        annual_min_max_ds = _ds.si_vol.groupby('time.year').apply(min_and_max_year)
        return annual_min_max_ds
    model_min_max_dt_1 = si_vol_dt.map_over_datasets(_min_and_max)
    return (model_min_max_dt_1,)


@app.cell
def _(model_min_max_dt_1, plt):
    for _group in model_min_max_dt_1.groups[1:]:
        _ds = model_min_max_dt_1[_group].ds
        _ds['min'].plot(label=_group[1:])
    plt.title('Trends in Sea-Ice Minimum Volume')
    plt.ylabel('Sea-Ice Volume ($m^3$)')
    _ = plt.legend()
    return


@app.cell
def _(model_min_max_dt_1, plt):
    for _group in model_min_max_dt_1.groups[1:]:
        _ds = model_min_max_dt_1[_group].ds.sel(year=slice(1950, 2022))
        _ds['max'].plot(label=_group[1:])
    plt.title('Trends in Sea-Ice Maximum Volume')
    plt.ylabel('Sea-Ice Volume ($m^3$)')
    _ = plt.legend()
    return


@app.cell
def _(climatology, plt, si_vol_dt):
    for _group in si_vol_dt.groups[1:]:
        climatology(si_vol_dt[_group].ds.si_vol).plot(label=_group[1:])
    plt.title('Climatology of Sea-Ice Volume')
    plt.ylabel('Sea-Ice Volume ($m^3$)')
    _ = plt.legend()
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
