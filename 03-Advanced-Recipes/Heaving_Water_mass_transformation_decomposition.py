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
    # Isopycnal heaving and along isopycnal change decomposition

    This notebook is to show how we can decompose temperature (or other scalar, e.g., salinity, age tracer) anomalies into isopycnal heaving and changes along isopycnals (water mass transformation)

    To perform this decomposition, we regrid the temperature data from its depth coordinate output to density coordinate to determine the temperature anomaly on isopycnals. Then, we regrid the temperature anomaly back to depth coordinates. Finally, we calculate the difference between the original temperature anomaly and the temperature anomaly on isopycnals. Such residual part is regarded as the temperature anomaly due to isopycnal heaving.

    We recommend using the XXLarge (28 cpus, 128 Gb mem) Jupyter Lab on NCI's ARE, using conda environment analysis3-26.06.

    ## Model output requirements
    Here are essential model outputs required for this notebook.

    | Variables | in ACCESS-OM2 | in MOM6 |
    |----------|----------|----------|
    | temperature  |  `temp`  |  `thetao` |
    | salinity  |  `salt`  |  `so` |

    Note that this notebook is set up to work with ACCESS-OM2 simulations. Therefore, `temp` is conservative temperature and `salt` is practical salinity in ACCESS-OM2. In MOM6, `thetao` is potential temperature and `so` is practical salinity. Be careful when you use `gsw` to calculate the density fields in different simulations, since this example uses the function that assumes your temperature variable is conservative temperature.
    """)
    return


@app.cell
def _():
    # load modules
    import matplotlib.pyplot as plt
    import numpy as np
    import xarray as xr
    import cf_xarray
    import cartopy.crs as ccrs
    import cmocean as cm
    import logging
    from dask.distributed import Client
    import matplotlib.path as mpath
    import cartopy.feature as cft
    import xgcm
    from xgcm import Grid
    import gsw
    from xhistogram.xarray import histogram
    import intake

    return Client, Grid, cm, gsw, intake, np, plt, xr


@app.cell
def _(Client):
    #Start a cluster with multiple cores
    client = Client(threads_per_worker = 1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1: Load dataset
    To calculate the temperature change along the isopycnal, we will need both temperature(x,y,depth) and density(x,y,depth), to get tempertaure(x,y,density).
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    experiment_control = '01deg_jra55v13_ryf9091' # Control experiment
    experiment_pertubation = '01deg_jra55v13_ryf9091_qian_wthp' # Perturbation experiment
    return catalog, experiment_control, experiment_pertubation


@app.cell
def _(catalog, experiment_control):
    # Load Control conservative temperature and practical salinity
    temp_ctrl = catalog[experiment_control].search(variable="temp",frequency='1mon').to_dask() 
    temp_ctrl = temp_ctrl.temp

    salt_ctrl = catalog[experiment_control].search(variable="salt",frequency='1mon').to_dask() 
    salt_ctrl = salt_ctrl.salt
    return salt_ctrl, temp_ctrl


@app.cell
def _(catalog, experiment_pertubation):
    # Load Perturbation conservative temperature and practical salinity
    temp_pert = catalog[experiment_pertubation].search(variable="temp",frequency='1mon').to_dask() 
    temp_pert = temp_pert.temp

    salt_pert = catalog[experiment_pertubation].search(variable="salt",frequency='1mon').to_dask() 
    salt_pert = salt_pert.salt
    return salt_pert, temp_pert


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: Get the potential density by using gsw
    """)
    return


@app.cell
def _():
    # The time period you want to look at
    start_time = '2150-01-01'
    end_time = '2150-12-31'

    # the domain you want to look at
    lat_slice = slice(-90,-50)
    lon = -130
    return


@app.function
# function to select the time period and domain you want for your variables
def subset_by_time_and_space(var,lon,lat_slice,start_time,end_time):
    var_domain = var.sel(time = slice(start_time,end_time)).sel(xt_ocean = lon, method = 'nearest').sel(yt_ocean = lat_slice).mean('time').load()

    return var_domain


@app.cell
def _(salt_ctrl, salt_pert, temp_ctrl, temp_pert):
    # output for temporal averaged variables in the Southern Ocean
    temp_SO_ctrl = subset_by_time_and_space(temp_ctrl)
    salt_SO_ctrl = subset_by_time_and_space(salt_ctrl)

    temp_SO_pert = subset_by_time_and_space(temp_pert)
    salt_SO_pert = subset_by_time_and_space(salt_pert)
    return salt_SO_ctrl, salt_SO_pert, temp_SO_ctrl, temp_SO_pert


@app.cell
def _(gsw):
    # Use temperature and salinity to get the potential density you want, here I use the potential density referenced to 1000 m depth.
    depth_rho = 1000 

    def pot_rho(temp,salt,depth_rho):
        # practical salinity to absolute salinity
        salt_ab = gsw.conversions.SA_from_SP(salt, salt.st_ocean, salt.xt_ocean, salt.yt_ocean)
    
        # transfer to potential density you want
        rho = gsw.density.rho(salt_ab, temp-273.15, depth_rho)
    

        return rho

    return depth_rho, pot_rho


@app.cell
def _(
    depth_rho,
    pot_rho,
    salt_SO_ctrl,
    salt_SO_pert,
    temp_SO_ctrl,
    temp_SO_pert,
):
    # get the density variables
    rho_SO_ctrl = pot_rho(temp_SO_ctrl,salt_SO_ctrl,depth_rho)
    rho_SO_pert = pot_rho(temp_SO_pert,salt_SO_pert,depth_rho)
    return rho_SO_ctrl, rho_SO_pert


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3: Calculate the temperature change along the isopycnal by using xgcm, and the residual is the temperature change due to isopycnal heaving.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First, we define isopycnal bins to convert vertical coordinates from `temp(y, depth)` to `temp(y, density)`
    """)
    return


@app.cell
def _(np):
    # Create your isopycnal bins, to reduce your computing time, they could be non-linear.
    bin1 = np.arange(1020, 1025, 0.1)
    bin2 = np.arange(1025, 1035, 0.02)
    # Concatenate the two non-linear bins
    isopycnal_bins = np.concatenate((bin1, bin2))
    return (isopycnal_bins,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Also, to transfer isopycnal temperature changes `temp_anomaly(y, density)` to `temp_anomaly(y,  depth)` , we define a grid depth `depth(x,y,z)`.
    """)
    return


@app.cell
def _(np, temp_SO_ctrl, xr):
    # the depth and lat coordinate in the model
    st_ocean = temp_SO_ctrl.st_ocean.values
    yt_ocean = temp_SO_ctrl.yt_ocean.values
    # get the depth(y,depth)
    depth = np.zeros((len(st_ocean),len(yt_ocean)))
    for j in range(len(yt_ocean)):
        depth[:,j] = st_ocean

    depth = xr.DataArray(depth, dims = ['st_ocean','yt_ocean'], coords = [temp_SO_ctrl.st_ocean, temp_SO_ctrl.yt_ocean])
    return depth, st_ocean


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now all good to go. Let's calculate the temperature change along the isopycnal by using `gsw`. And the residual (total temperature change minus temperature change along the isopycnal) is the isopycnal heaving part.
    """)
    return


@app.cell
def _(Grid, depth, isopycnal_bins, np, st_ocean, xr):
    # Function to calculate the temperature change along the isopycnal
    def isopycnal_temp_change(var_ctrl, var_pert, rho_ctrl, rho_pert):
        # get the grid dataset you want to transfer
        ds = xr.Dataset({'var_ctrl': var_ctrl, 'rho_ctrl': rho_ctrl,
                        'var_pert': var_pert, 'rho_pert': rho_pert})
        ds.coords['st_ocean'].attrs.update(axis='Z')
        ds.coords['yt_ocean'].attrs.update(axis='Y')
        grid = Grid(ds, periodic=False)
        # transfer vars from depth coord to isopycnal bins
        var_ctrl_rho = grid.transform(ds.var_ctrl, 'Z', isopycnal_bins, target_data=ds.rho_ctrl,method='linear')
        var_ctrl_rho = var_ctrl_rho.rename({'rho_ctrl': 'pot_rho_1'})
        var_pert_rho = grid.transform(ds.var_pert, 'Z', isopycnal_bins, target_data=ds.rho_pert,method='linear')
        var_pert_rho = var_pert_rho.rename({'rho_pert': 'pot_rho_1'})
        # Create depth(t,pot_rho,y), here we use the averaged density field between two experiments
        ds_depth = xr.Dataset({'pot_rho_1': (rho_ctrl+rho_pert)/2, 'depth': depth})
        ds_depth.coords['st_ocean'].attrs.update(axis='Z')
        ds_depth.coords['yt_ocean'].attrs.update(axis='Y')
        grid = Grid(ds_depth, periodic=False)
        depth_rho = grid.transform(ds_depth.depth, 'Z', isopycnal_bins, target_data=ds_depth.pot_rho_1,method='linear')
        # Compute the anomaly in density coords, then transfer anomaly back to depth coords
        var_ano_rho = var_pert_rho-var_ctrl_rho
        ds_ano = xr.Dataset({'depth': depth_rho, 'var_ano': var_ano_rho})
        ds_ano.coords['yt_ocean'].attrs.update(axis='Y')
        ds_ano.coords['pot_rho_1'].attrs.update(axis='Pot_rho_1')
        grid = Grid(ds_ano, periodic=False)
        depth_bin = np.concatenate((np.arange(0,200.,0.02), np.arange(200.,6000.,10.)))
        var_ano_depth = grid.transform(ds_ano.var_ano, 'Pot_rho_1', depth_bin, target_data=ds_ano.depth,method='linear')
        # Make the coordinates and dimensions in the new anomaly consistent to the total anomaly
        var_ano_depth = var_ano_depth.transpose('depth','yt_ocean')
        var_ano_depth = var_ano_depth.interp(depth = st_ocean, method = 'linear')
        var_ano_depth = var_ano_depth.rename({'depth':'st_ocean'})

        return [var_ctrl_rho,var_pert_rho,var_ano_rho,var_ano_depth,depth_rho]

    return (isopycnal_temp_change,)


@app.cell
def _(
    isopycnal_temp_change,
    rho_SO_ctrl,
    rho_SO_pert,
    temp_SO_ctrl,
    temp_SO_pert,
):
    # get the values
    temp_ctrl_rho, temp_pert_rho, temp_ano_rho, temp_ano_depth, depth_rho_1 = isopycnal_temp_change(temp_SO_ctrl, temp_SO_pert, rho_SO_ctrl, rho_SO_pert)
    return (temp_ano_depth,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 4: Plot the total temperature change, temperature change along the isopycnal and temperature change due to heaving.
    """)
    return


@app.cell
def _(cm, plt, temp_SO_ctrl, temp_SO_pert, temp_ano_depth):
    fig = plt.figure(figsize=(18,4),dpi = 300)

    ax1 = plt.subplot(1,3,1)

    p1 = (temp_SO_pert-temp_SO_ctrl).plot(vmin=-0.5,vmax=0.5, cmap = cm.cm.balance,add_colorbar = False)
    ax1.invert_yaxis()
    ax1.set_xlim(-75,-50)
    ax1.set_xlabel('Latitude ˚N')
    ax1.set_ylabel('Depth (m)')
    ax1.set_title('Total temperature anomaly')

    ax2 = plt.subplot(1,3,2)
    (temp_ano_depth).plot(vmin=-0.5,vmax=0.5, cmap = cm.cm.balance,add_colorbar = False)
    ax2.invert_yaxis()
    ax2.set_xlim(-75,-50)
    ax2.set_xlabel('Latitude ˚N')
    ax2.set_ylabel('Depth (m)')
    ax2.set_title('Isopycnal temperature change')

    ax3 = plt.subplot(1,3,3)
    (temp_SO_pert-temp_SO_ctrl-temp_ano_depth).plot(vmin=-0.5,vmax=0.5, cmap = cm.cm.balance,add_colorbar = False)
    ax3.invert_yaxis()
    ax3.set_xlim(-75,-50)
    ax3.set_xlabel('Latitude (˚N)')
    ax3.set_ylabel('Depth (m)')
    ax3.set_title('Temperature change by isopycnal heaving')

    ax_cb1 = plt.axes([0.93, 0.15, 0.01, 0.7])
    cb = plt.colorbar(p1, cax=ax_cb1,  orientation='vertical',extend='both')
    cb.ax.set_ylabel('Temperature anomaly (˚C)')
    cb.ax.yaxis.set_label_position('right')
    cb.ax.yaxis.set_ticks_position('right')
    return


if __name__ == "__main__":
    app.run()
