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
    # Depth-time Hovmoller plot

    This recipe shows how to calculate a depth-time Hovmoller plot of 1-year anomaly of annual, globally-averaged anomalies of conservative temperature from ACCESS-OM2 between Jan 1989 and Dec 2018.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Converting to MOM6

    This notebook is written using MOM5 output. To convert to MOM6 you will need to change the following variables:

    | MOM5 | MOM6 |
    |---|---|
    | xt_ocean | xh |
    | yt_ocean | yh |
    | st_ocean | z_l |
    | temp$\text{*}$ | thetao$\text{*}$ |
    | area_t | areacello |

    $\text{*}$Note that in MOM5 `temp` describes conservative temperature, and in MOM6 `thetao` describes potential temperature.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recipe for MOM5
    """)
    return


@app.cell
def _():
    import numpy as np
    import xarray as xr
    import intake

    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.gridspec import GridSpec
    from matplotlib import ticker
    import cmocean.cm as cm

    from dask.distributed import Client

    return Client, GridSpec, cm, intake, mdates, np, plt, ticker


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    return


@app.cell
def _(intake):
    # Import your experiment from the catalog
    catalog = intake.cat.access_nri
    experiment = '1deg_jra55_iaf_omip2_cycle1'  # 1-deg experiment
    return catalog, experiment


@app.cell
def _(catalog):
    def load_var(experiment, variable, frequency, start_time=None, end_time=None):

        cat_subset = catalog.search(name = experiment)

        var = cat_subset[experiment].search(
            variable = variable, frequency = frequency, variable_cell_methods='time: mean'
            ).to_dask(xarray_open_kwargs = dict(use_cftime=True,chunks={}),
                      xarray_combine_by_coords_kwargs = dict(compat="override", data_vars="minimal", coords="minimal")
                     )[variable]

        var = var.sel(time=slice(start_time, end_time))

        return var

    return (load_var,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Loading the variables
    """)
    return


@app.cell
def _(experiment, load_var):
    temperature = load_var(experiment, 'temp', '1mon')
    return (temperature,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Compute anomalies relative to the first year (assuming monthly output here). This approach shows model drift/evolution over time.
    """)
    return


@app.cell
def _(temperature):
    temperature_anomaly = temperature - temperature.isel(time=slice(0, 12)).mean('time')
    return (temperature_anomaly,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next, we load cell area (denoted as $a(x,y,z)$) to construct the total ocean area as a function of depth, $A$, namely
    $$ A(z) = \sum_x \sum_y a(x,y,z)$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We load `dxt` and `dyt` and compute a masked version of cell area; we also use a slight hack to divide temperature by itself and thereby get a 3-dimensional cell area mask that is needed to create $A(z)$. Note that we need the correct area sum at each depth that accounts for the depth-varying land mask.
    """)
    return


@app.cell
def _(catalog, experiment, temperature):
    cat_subset = catalog.search(name = experiment)

    cell_area = cat_subset[experiment].search(variable = 'area_t', frequency = 'fx', path=".*output000.*").to_dask()['area_t']

    ## Make a mask to get vertical variation of area
    temp1 = temperature.isel(time=0)
    cell_mask = temp1 / temp1

    total_area = (cell_area * cell_mask).sum({'xt_ocean', 'yt_ocean'}).load()
    return cell_area, total_area


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, the mean temperature at each time level can then be computed as
    $$T(z,t) = \frac{\sum_x \sum_y a(x,y,z) \, \tilde{\theta}(x,y,z,t)}{A(z)}$$
    where $T$ is the globally average temperature anomaly and $\tilde{\theta}$ is  conservative temperature.
    """)
    return


@app.cell
def _(cell_area, temperature_anomaly, total_area):
    ### Temperature hovmoller
    temperature_hov = (cell_area * temperature_anomaly).sum({'xt_ocean', 'yt_ocean'}) / total_area
    temperature_hov = temperature_hov.compute()
    return (temperature_hov,)


@app.cell
def _(GridSpec, mdates, plt):
    def plot_hovmoller(fsize = 14, date_format = mdates.DateFormatter('%Y')):
    
        # Set figures properties
        plt.rcParams['font.size'] = fsize
        plt.rcParams['xtick.labelsize'] = fsize-2
        plt.rcParams['ytick.labelsize'] = fsize-2
    
        fig = plt.figure(figsize = (10, 6))
        grid = GridSpec(100, 100)
    
        ax = [fig.add_subplot(grid[:30, :]),
              fig.add_subplot(grid[32:, :])]
    
        for i in range(len(ax)):
            ax[i].xaxis.set_major_formatter(date_format)
            ax[i].tick_params(axis='x', labelrotation=45)
    
        return fig, ax

    return (plot_hovmoller,)


@app.cell
def _(cm, np, plot_hovmoller, plt, temperature_hov, ticker):
    fig, ax = plot_hovmoller(fsize = 14)

    levels_temperature = np.arange(-0.3, 0.31, 0.01)

    shelf_temp = temperature_hov.plot(ax = ax[0],
                                      levels = levels_temperature,
                                      x = 'time',
                                      y = 'st_ocean',
                                      add_colorbar = False,
                                      label = None,
                                      cmap = cm.balance)

    temperature_hov.plot(ax = ax[1],
                            levels = levels_temperature,
                            x = 'time',
                            y = 'st_ocean',
                            add_colorbar = False,
                            label = None,
                            cmap = cm.balance)

    ## Beautification details
    ax[0].set_ylim(500, 0)
    ax[0].set_ylabel("")
    ax[0].set_xlabel("")
    ax[0].set_xticklabels([])
    ax[1].set_ylabel("Depth [m]",loc="top")
    ax[1].set_ylim(5000, 500)
    ax[1].set_xlabel("") # or ax[1].set_xlabel("Time")

    # Colorbars
    bar = plt.axes([0.13, 0.99, 0.77, 0.03])
    cbar_1 = plt.colorbar(shelf_temp, cax = bar, orientation = 'horizontal', extend='both', format= '%.2f')  
    cbar_1.set_label(r"Temperature [$\degree$C]")


    for cbar in [cbar_1]:
        tick_locator = ticker.MaxNLocator(nbins=5) ## The ticker needs to called within the loop
        cbar.locator = tick_locator
        cbar.update_ticks()
    return


if __name__ == "__main__":
    app.run()
