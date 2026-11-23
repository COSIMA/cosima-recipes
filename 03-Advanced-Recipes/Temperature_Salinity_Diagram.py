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
    # Temperature-Salinity diagram using MOM6 output
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This notebook shows how to plot a temperature-salinity diagram which is weighted by volume using xhistogram.

    The notebook is written using output from MOM6. If you want to use output from MOM5 the relevant diagnostics are as follows;
    - Temperature: `temp` which is conservative temperature (in MOM6 we use potential temperature `thetao`)
    - Salinity: `salt`    (in MOM6 this is `so`)

    In MOM6, there is a tracer cell volume diagnostic (`volcello`). There is no output diagnostic equivalent in MOM5, however you can calculate the tracer cell volume by multiplying the tracer cell area (`area_t`) by the tracer cell thickness (`dzt`).

    Note that the coordinate (lat and lon) names also differ between MOM6 and MOM5. In MOM6, the tracer longitude coordinate is labelled `xh`, the tracer latitude coordinate is labelled `yh`, and the tracer vertical coordinate is `z_l`. In MOM5, the tracer longitude coordinate is labelled `xt_ocean`, the tracer latitude coordinate is labelled `yt_ocean`, and the tracer vertical coordinate is `st_ocean`.

    **Requirements**: The conda/analysis3 (or later) module on ARE. A session with 4 cores is sufficient for this example but more cores will be needed for larger datasets.

    Firstly, we load all required modules and start a client.
    """)
    return


@app.cell
def _():
    # analysis libraries
    import xarray as xr
    import numpy as np
    import gsw
    from xhistogram.xarray import histogram as xhistogram

    # intake and Dask
    import intake
    catalog = intake.cat.access_nri
    from dask.distributed import Client

    # plotting libaries
    import matplotlib.pyplot as plt
    import cmocean.cm as cmo
    import matplotlib.colors as colors

    return Client, catalog, cmo, colors, gsw, np, plt, xhistogram


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Load data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Choose an experiment of any resolution. Here, only 1 year of the MOM6 `panant-01-zstar-v13` experiment is selected; if you want to use a longer time period, you might need more resources!
    """)
    return


@app.cell
def _():
    experiment = "panant-01-zstar-v13"
    start_time = "1991-01-01"
    end_time = "1991-12-31"
    return end_time, experiment, start_time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Load the data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We define a function below to load output (temperature or salinity) on which we will compute the histogram for the T-S diagram.
    """)
    return


@app.cell
def _(catalog, experiment):
    def load_data(variable, frequency='1mon', file_id=None, start_time=None, end_time=None):
    
        '''
        variable: string defining the variable to load (e.g. `thetao` or `so`)
        '''

        catalog_subset = catalog[experiment]
        variable_search = catalog_subset.search(variable=variable, frequency=frequency)
        if file_id is not None:
            variable_search = variable_search.search(file_id=file_id)
        
        darray = variable_search.to_dask(xarray_open_kwargs={"decode_timedelta": False})

        darray = darray.get(variable)
    
        if 'time' in darray.coords:
            darray = darray.sel(time=slice(start_time, end_time))
    
        return darray

    return (load_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now load the data using this function.
    """)
    return


@app.cell
def _(end_time, load_data, start_time):
    salt = load_data('so', start_time=start_time, end_time=end_time)
    temperature = load_data('thetao', start_time=start_time, end_time=end_time)
    cell_volume = load_data('volcello', start_time=start_time, end_time=end_time, file_id='ocean.1mon.nv:2.xh:3600.xq:3601.yh:845.yq:846.z_i:76.z_l:75')
    return cell_volume, salt, temperature


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Subset the data regionally
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Select the region and coordinates of meridional section for the temperature-salinity diagram.
    """)
    return


@app.cell
def _():
    longitude = -25  # longitude of meridional section
    latitude_range = slice(-90, -37)  # latitude range of section
    return latitude_range, longitude


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And we subset the previously loaded data using this function.
    """)
    return


@app.cell
def _(cell_volume, latitude_range, longitude, salt, temperature):
    salt_1 = salt.sel(xh=longitude, method='nearest').sel(yh=latitude_range)
    temperature_1 = temperature.sel(xh=longitude, method='nearest').sel(yh=latitude_range)
    cell_volume_1 = cell_volume.sel(xh=longitude, method='nearest').sel(yh=latitude_range)
    return cell_volume_1, salt_1, temperature_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Convert Temperature and Salinity units
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we need to convert from potential temperature to conservative temperature and from practical salinity to absolute salinity. If adapting this to MOM5 output, make sure you check the temperature and salinity definitions/units - they may be different than for MOM6! To learn more about the different types of salinity and temperature measurements, and how to convert between them, visit the `GSW` toolbox: https://teos-10.github.io/GSW-Python/intro.html
    """)
    return


@app.cell
def _(gsw, salt_1, temperature_1):
    # Calculate ocean pressure (gsw assumes ocean depth is positive upwards, 
    # hence the negative applied here)
    pressure = gsw.p_from_z(-salt_1.z_l, salt_1.yh)
    SA = gsw.SA_from_SP(salt_1, pressure, salt_1.xh, salt_1.yh)
    # This converts pratical salinity (psu) to absolute salinity (g/kg)
    SA.attrs = {'units': 'Absolute Salinity (g/kg)'}
    CT = gsw.CT_from_pt(salt_1, temperature_1)
    CT = CT.rename('thetao')
    # This converts potential temperature (deg C) to conservative temperature (deg C)
    CT.attrs = {'units': 'Conservative temperature (°C)'}
    return CT, SA


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now load the converted data into memory. Note: You don't need to load the data into memory to run the rest of the script but it can make subsequent calculations faster. However, if you choose to load more data (e.g. a larger region or longer timeframe) then this step might cause the kernel to die.
    """)
    return


@app.cell
def _(CT, SA):
    CT_1 = CT.compute()
    SA_1 = SA.compute()
    return CT_1, SA_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Compute T-S histogram
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now define the function that computes the temperature and salinity bins for the T-S histogram.
    """)
    return


@app.cell
def _(gsw, np, xhistogram):
    def compute_TS_bins(salt, temperature, volume):
    
        temp_bins = np.arange(np.floor(temperature.min().values)-0.5, np.ceil(temperature.max().values)+0.6, 0.5)
        salt_bins = np.arange(np.floor(salt.min().values)-0.1, np.ceil(salt.max().values)+0.11, 0.1)
    
        # To create density contours in the T-S diagram
        temp_bins_mesh, salt_bins_mesh = np.meshgrid(temp_bins, salt_bins)
        TS_density = gsw.density.sigma2(salt_bins_mesh, temp_bins_mesh)
    
        # Create the 2D histogram array containing the temperature and salinity values, 
        # weighted by grid cell volume
        TS_histogram = xhistogram(temperature, salt, bins=(temp_bins, salt_bins), weights=volume)
        TS_histogram = TS_histogram.where(TS_histogram != 0).compute()
    
        return TS_histogram, TS_density, salt_bins_mesh, temp_bins_mesh

    return (compute_TS_bins,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Calculate the histogram.
    """)
    return


@app.cell
def _(CT_1, SA_1, cell_volume_1, compute_TS_bins):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    TS_histogram, TS_density, salt_bins_mesh, temp_bins_mesh = compute_TS_bins(SA_1, CT_1, cell_volume_1)
    return TS_density, TS_histogram, salt_bins_mesh, temp_bins_mesh


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plot the histogram
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can plot this T-S histogram!
    """)
    return


@app.cell
def _(
    CT_1,
    SA_1,
    TS_density,
    TS_histogram,
    cmo,
    colors,
    np,
    plt,
    salt_bins_mesh,
    temp_bins_mesh,
):
    plt.rcParams['font.size'] = 14
    plt.figure(figsize=(9, 8))
    norm = colors.LogNorm(vmin=TS_histogram.min().values, vmax=TS_histogram.max().values)
    # normalize the colorbar to the min and maximum values of the histogram 
    # using a LogNormal scale
    TS_histogram.plot(cmap=cmo.dense, norm=norm, cbar_kwargs=dict(label='volume (m$^{3}$)'))
    cs = plt.contour(salt_bins_mesh, temp_bins_mesh, TS_density, colors='silver', linewidths=1, levels=np.arange(np.floor(TS_density.min()), np.ceil(TS_density.max()), 0.5))
    # Plot (shade) the TS histogram data
    plt.clabel(cs, inline=True)
    plt.xlabel(SA_1.units)
    # Add the density contours
    plt.ylabel(CT_1.units)
    plt.title('T-S weighted histogram from MOM6')
    plt.xlim([32.9, 35.7])
    plt.yticks(np.arange(-2, 23, 2))
    plt.show()
    return


if __name__ == "__main__":
    app.run()
