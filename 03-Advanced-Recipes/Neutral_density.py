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
    # Neutral density
    ## (MOM6)

    This notebook calculates neutral density ($\gamma$) in MOM6 using the algorithm developed by [Jackett and McDougall 1997](https://doi.org/10.1175/1520-0485(1997)027<0237:ANDVFT>2.0.CO;2).

    Before using neutral density, be aware that this is a calculation that uses as a reference a climatology from the World Atlas, Levitus 1980. Therefore, **it shouldn't be used for simulations or datasets with climates/ocean states different to the 1980s (i.e. future projection simulations)**.

    We use a python wrapper called `pygamma_n`, developed by Eric Firing and Filipe Fernandes; see https://currents.soest.hawaii.edu/hgstage/pygamma/ .

    `pygamma_n` is available from `conda/analysis3-25.06`

    ## Information needed to adapt to MOM5:

    Diagnostics needed:
     - `temp`: conservative temperature
     - `salt`: salinity
     - `ht`: depth at t-cells

    Note that temperature in MOM5 is given as a conservative temperature in Kelvin, so you will need to (a) convert to Celsius and (b) go straight into calculating insitu temperature. All these diagnostics are in the t-cells, with `xt_ocean` and `yt_ocean` as longitude and latitude.
    """)
    return


@app.cell
def _():
    import intake

    import numpy as np
    import xarray as xr
    from joblib import Parallel, delayed

    import gsw
    import pygamma_n

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cmocean

    import dask.distributed as dask
    import warnings
    warnings.filterwarnings("ignore", category = FutureWarning)
    warnings.filterwarnings("ignore", category = UserWarning)
    warnings.filterwarnings("ignore", category = RuntimeWarning)
    return (
        Parallel,
        ccrs,
        cmocean,
        dask,
        delayed,
        gsw,
        intake,
        np,
        plt,
        pygamma_n,
        xr,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Initialize a dask client.
    """)
    return


@app.cell
def _(dask):
    client = dask.Client(threads_per_worker=1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load ACCESS-NRI default catalog:
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define arguments needed to load data from a MOM6 experiment:
    """)
    return


@app.cell
def _():
    experiment = 'panant-01-zstar-ACCESSyr2'
    start_time = '2000-01-01'
    end_time = '2001-01-01'
    frequency = '1mon'
    return end_time, experiment, start_time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the region to work with:
    """)
    return


@app.cell
def _(end_time, start_time):
    latitude_slice = slice(-70, -60)
    longitude_slice = slice(-70, -40)
    time_slice = slice(start_time, end_time)
    return latitude_slice, longitude_slice, time_slice


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's load the data - we will need temperature, salinity and depth - and select our region of interest. This recipe the `pygamma` function that only takes in 2D fields, so there is a parallelisation involved in calculating it for a time-varying 3D field. Be mindful of not making your region too big.
    """)
    return


@app.cell
def _(catalog, experiment):
    potential_temperature = catalog[experiment].search(variable = 'thetao', frequency = '1mon').to_dask(xarray_open_kwargs={"decode_timedelta": True})
    practical_salinity = catalog[experiment].search(variable = 'so', frequency = '1mon').to_dask(xarray_open_kwargs={"decode_timedelta": True})
    depth = catalog[experiment].search(variable = 'deptho', frequency = 'fx').to_dask()
    return depth, potential_temperature, practical_salinity


@app.cell
def _(
    depth,
    latitude_slice,
    longitude_slice,
    potential_temperature,
    practical_salinity,
    time_slice,
):
    potential_temperature_1 = potential_temperature['thetao'].sel(time=time_slice, xh=longitude_slice, yh=latitude_slice)
    practical_salinity_1 = practical_salinity['so'].sel(time=time_slice, xh=longitude_slice, yh=latitude_slice)
    depth_1 = depth['deptho'].sel(xh=longitude_slice, yh=latitude_slice)
    return depth_1, potential_temperature_1, practical_salinity_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load the data before doing any calculations. We are opening potential temperature (`thetao`) and practical salinity (`so`).
    """)
    return


@app.cell
def _(potential_temperature_1, practical_salinity_1):
    potential_temperature_2 = potential_temperature_1.load()
    practical_salinity_2 = practical_salinity_1.load()
    return potential_temperature_2, practical_salinity_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `pygamma_n` takes in in-situ temperature and absolute salinity, so we will use `gsw` to convert. This involves calculating pressure as well! And annoyingly to go from MOM6's potential temperature to in situ temperature, we have to calculate conservative temperature as an intermediate step.
    """)
    return


@app.cell
def _(gsw, potential_temperature_2, practical_salinity_2):
    # Get values of coordinates
    depth_coordinate = potential_temperature_2['z_l']
    longitudes = potential_temperature_2['xh']
    latitudes = potential_temperature_2['yh']
    pressure_coordinate = gsw.p_from_z(-depth_coordinate, latitudes)
    # Calculate pressure to use as a coordinate
    absolute_salinity = gsw.SA_from_SP(practical_salinity_2, pressure_coordinate, longitudes, latitudes).rename('SA')
    conservative_temperature = gsw.CT_from_pt(absolute_salinity, potential_temperature_2)
    # Calculate absolute salinity
    # Calculate conservative temperature (needed to calculate in situ temperatures)
    # Calculate insitu temperature 
    insitu_temperature = gsw.t_from_CT(absolute_salinity, conservative_temperature, pressure_coordinate).rename('t')
    return (insitu_temperature,)


@app.cell
def _(insitu_temperature):
    insitu_temperature_1 = insitu_temperature.load()
    return (insitu_temperature_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `pygamma_n` function to calculate neutral densities takes 2D fields (cross sections with depth and lat/lon). So for our time-varying, 3D fields we are going to need to "iterate" twice, once through time and once through longitudes. We will define a function that calculates $\gamma$ for a certain time step and longitude, and then use the Parallel function from `joblib` to calculate each cross section in parallel.
    """)
    return


@app.cell
def _(gsw, pygamma_n):
    def neutral_density(t, s, time_index, longitude_index):
        """
        Calculates neutral density (gamma) for a given longitude and time 
        of in-situ temperature and practical salinity datasets.
        """
        pressure = gsw.p_from_z(-t['z_l'], t['yh'])
    
        gamma, dg_lo, dg_hi = pygamma_n.gamma_n(s.isel(time=time_index, xh=longitude_index).transpose(), 
                                                t.isel(time=time_index, xh=longitude_index).transpose(), 
                                                pressure.transpose(), 
                                                (t['xh'][longitude_index].item()*(t['yh']*0+1)), 
                                                (t['yh']))
        gamma  = gamma.T
    
        return gamma

    return (neutral_density,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now that we have our function, we need to make a list of arguments we want to feed it (every combination possible of time and longitude indexes):
    """)
    return


@app.cell
def _(insitu_temperature_1):
    # Create a list of pairs that have a unique time, lon index
    Nt = len(insitu_temperature_1['time'])
    Nx = len(insitu_temperature_1['xh'])
    args_list = [[i, j] for i in range(Nt) for j in range(Nx)]
    return Nx, args_list


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below uses `Parallel` to run the neutral density function for each cross section in parallel, where the results are arranged as a list:
    """)
    return


@app.cell
def _(
    Parallel,
    args_list,
    delayed,
    insitu_temperature_1,
    neutral_density,
    practical_salinity_2,
):
    # Run the neutral_density function in parallel
    results = Parallel(n_jobs=-1)((delayed(neutral_density)(insitu_temperature_1, practical_salinity_2, arg1, arg2) for arg1, arg2 in args_list))
    return (results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We need to reshape that list onto a DataArray with appropriate dimensions:
    """)
    return


@app.cell
def _(Nx, insitu_temperature_1, np, results):
    # Reshape into the original dataset shape
    gamma = np.nan * np.zeros(np.shape(insitu_temperature_1))
    for idx, result in enumerate(results):
        i, j = divmod(idx, Nx)
        gamma[i, :, :, j] = result
    return (gamma,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Convert `gamma` into a dataarray with dimensions and attributes.
    """)
    return


@app.cell
def _(gamma, insitu_temperature_1, xr):
    gamma_1 = xr.DataArray(gamma, dims=insitu_temperature_1.dims, coords=insitu_temperature_1.coords, name='gamma')
    gamma_1.attrs['long_name'] = 'neutral density'
    gamma_1.attrs['units'] = 'kg/m3'
    return (gamma_1,)


@app.cell
def _(gamma_1, insitu_temperature_1, np, xr):
    # Put the nans back in land (pygamma has a fillvalue of zero)
    gamma_2 = xr.where(np.isnan(insitu_temperature_1), np.nan, gamma_1)
    return (gamma_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Plotting
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's create a land mask and do a map of the time mean neutral density at the surface:
    """)
    return


@app.cell
def _(depth_1, np, xr):
    # Create a land mask
    land_mask = xr.where(np.isnan(depth_1), 1, np.nan)
    return (land_mask,)


@app.cell
def _(ccrs, cmocean, gamma_2, land_mask, plt):
    _fig = plt.figure(figsize=(15, 15))
    projection = ccrs.Mercator(central_longitude=-55)
    _axs = _fig.add_subplot(121, projection=projection)
    _axs.set_extent([-70, -40, -70, -60], crs=ccrs.PlateCarree())
    land_mask.plot.contourf(ax=_axs, colors='lightgrey', transform=ccrs.PlateCarree(), add_colorbar=False, zorder=2)
    land_mask.fillna(0).plot.contour(ax=_axs, colors='k', levels=[0, 1], transform=ccrs.PlateCarree(), add_colorbar=False, linewidths=0.5, zorder=3)
    gamma_2.mean('time').isel(z_l=0).plot.pcolormesh(ax=_axs, cmap=cmocean.cm.dense, transform=ccrs.PlateCarree(), vmin=26.5, vmax=28, levels=25, cbar_kwargs={'label': '$\\gamma$ (kg/m$^{3}$)', 'shrink': 0.3})
    _axs.set_title('Neutral density at the surface')
    return


@app.cell
def _(cmocean, gamma_2, plt):
    _fig, _axs = plt.subplots(figsize=(10, 5))
    gamma_2.mean('time').sel(xh=-45, method='nearest').plot.pcolormesh(ax=_axs, cmap=cmocean.cm.dense, vmin=27.4, vmax=28.4, levels=25, cbar_kwargs={'label': '$\\gamma$ (kg/m$^{3}$)'})
    _axs.invert_yaxis()
    _axs.set_ylabel('Depth (m)')
    _axs.set_xlabel('Latitude')
    _axs.set_title('Neutral density at 45$^{\\circ}$W')
    return


if __name__ == "__main__":
    app.run()
