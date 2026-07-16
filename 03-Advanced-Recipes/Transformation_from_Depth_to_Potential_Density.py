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
    # Coordinate transformation from z levels to density levels

    ## Rebinning `ty_trans` to `ty_trans_rho` density levels in MOM5

    This transformation is commonly used for the purpose of decomposing the residual meridional overturning streamfunction into mean and eddy components. The mean is taken to be the time-mean Eulerian transport (time-mean in z coordinates), whilst the residual transport is the time-mean in density coordinates (density surface move in time). The eddy transport is the difference between the residual overturning streamfunction, and the Eulerian transport **transformed from depth to density coordinates** via the time-mean density.

    Binning is the discrete version of this transformation from depth to density coordinates. We define target density bins, and for each bin we add the quantity to be binned from all cells with a density that satisfies that bin. In its simplest form, binning is creating a histogram.

    We use three different binning methods:
    1. `xhistogram`, which performs binning in exactly the way MOM5 does and is thus most appropriate for calculating eddy quantities (define edge of bins)
    2. `xgcm` conservative binning (define edge of bins, but vertically interpolates so looks smoother than `xhistogram`)
    3. Using density coordinate binning method of Lee et al. (2007) (define isopycnals to bin onto i.e. centre)

    Compute times were calculated using the XXLargeMem (28 cpus, 252 Gb mem) Jupyter Lab on NCI's ARE, using conda environment analysis3-26.06.

    This notebook performs direct coordinate searches using the access-nri intake catalog, and so will __require conda environment analysis3-25.02 or later__.

    #### A starting point for conversion to MOM6

    This notebook uses MOM5 variables. To convert this notebook to MOM6, the following variables are required. However, note that MOM6 pan-Antarctic and ACCESS-OM3 models currently do not output 3D volume transports in both z and density coordinates so this particular example won't be able to be replicated without additional model runs.

    **Important note** In MOM6, online density-binned output diagnostics may have the same variable name as the z-coordinate binned output. In this case, they should have different filenames to distinguish them.

    | MOM5 variable | MOM6 variable and file |
    | :---: | :---: |
    |   `ty_trans`    |  `vmo` (no COSIMA MOM6 models output this yet)    |
    |   `ty_trans_rho`    |  `vmo`, `filename = '*.ocean_month_rho2.nc'` for panan and  `filename = 'access-om3.mom6.3d.vmo+rho2.1mon.mean.*.nc'` for ACCESS-OM3   |
    |   `pot_rho_2`    |  `rhopot2`     |
    | `yu_ocean`      | `yq` |
    | `xt_ocean`      | `xh` |
    | `yt_ocean`      | `yh` |
    | `st_ocean`      | `z_l` |
    | `st_edges_ocean` | `z_i` |
    | `potrho` | `rho2_l` |
    | `potrho_edges` | `rho2_i` |
    """)
    return


@app.cell
def _():
    import intake

    import matplotlib.pyplot as plt
    import numpy as np
    import xarray as xr
    import glob
    import cmocean.cm as cmocean
    import xgcm
    from xhistogram.xarray import histogram

    from dask.distributed import Client

    return Client, histogram, intake, np, plt, xgcm, xr


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    return


@app.cell
def _(intake):
    experiment = '01deg_jra55v13_ryf9091'

    catalog = intake.cat.access_nri
    expt_datastore = catalog[experiment]

    rho_0 = 1035.0 # kg/m^3 reference density
    g = 9.81

    # reduce computation by choosing only Southern Ocean latitudes
    lat_range = slice(-70, -34.99)
    return expt_datastore, lat_range, rho_0


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 1: Load density and quantity being binned
    (you can choose any other quantity instead of `ty_trans`, e.g. `dzt`. Interpolate density to whatever grid that variable is on)

    For the simplicity of the demonstrations here, we will **only load two months** of monthly `ty_trans`, `ty_trans_rho` and `pot_rho_2`, then take the time average after we weight with the number of days in each month.

    ### Notes on searching for data
    - We can search for multiple variables at once: `variable=['ty_trans','ty_trans_rho','pot_rho_2']` will get all three in the same search, which is faster than searching multiple times
    - The access-nri intake catalog doesn't support start and end dates yet. To work around this, we use 'regex' (regular expression) to search for dates. This regex: `start_date='2170-0[1-3].*'` says "find me all strings that start with either '1970-01', '1970-02', or '1970-03'". For more info on regex's, see [here](https://docs.python.org/3/library/re.html).
    """)
    return


@app.cell
def _(expt_datastore):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    start_time = '2170-01-01'
    end_time = '2170-03-01'
    time_slice = slice(start_time, end_time)
    _ds = expt_datastore.search(variable=['ty_trans', 'ty_trans_rho', 'pot_rho_2'], start_date='2170-0[1-3].*').to_dask(xarray_open_kwargs={'chunks': 'auto'})
    ty_trans, ty_trans_rho, pot_rho_2 = (_ds['ty_trans'], _ds['ty_trans_rho'], _ds['pot_rho_2'])
    return pot_rho_2, time_slice, ty_trans, ty_trans_rho


@app.cell
def _(lat_range, time_slice, ty_trans):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    ty_trans_1 = ty_trans.sel(time=time_slice).sel(yu_ocean=lat_range)
    days_in_month = ty_trans_1.time.dt.days_in_month
    # weighted time-mean by month length
    total_days = days_in_month.sum()
    ty_trans_1 = (ty_trans_1 * days_in_month).sum('time') / total_days
    return days_in_month, total_days, ty_trans_1


@app.cell
def _(days_in_month, lat_range, pot_rho_2, time_slice, total_days):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    pot_rho_2_1 = pot_rho_2.sel(time=time_slice).sel(yt_ocean=lat_range)
    pot_rho_2_1 = (pot_rho_2_1 * days_in_month).sum('time') / total_days
    return (pot_rho_2_1,)


@app.cell
def _(days_in_month, lat_range, time_slice, total_days, ty_trans_rho):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    ty_trans_rho_1 = ty_trans_rho.sel(time=time_slice).sel(grid_yu_ocean=lat_range)
    ty_trans_rho_1 = (ty_trans_rho_1 * days_in_month).sum('time') / total_days
    return (ty_trans_rho_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create an `xgcm` grid for interpolation, and then interpolate density onto the meridional transport grid
    """)
    return


@app.cell
def _(pot_rho_2_1, ty_trans_1, xgcm, xr):
    _ds = xr.Dataset({'ty_trans': ty_trans_1, 'pot_rho_2': pot_rho_2_1})
    _grid = xgcm.Grid(_ds, coords={'Y': {'center': 'yt_ocean', 'right': 'yu_ocean'}}, periodic=False, autoparse_metadata=False)
    pot_rho_2_2 = _grid.interp(pot_rho_2_1, 'Y', boundary='extend')
    return (pot_rho_2_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Method 1: `xhistogram`

    We use `xhistogram` which is an xarray-aware method for computing histograms; see its [documentation](https://xhistogram.readthedocs.io/en/latest/).

    Computation in xhistogram occurs via the same method as in MOM5 online binning. It is thus most appropriate for an comparisons between offline and online binned quantities.

    ### First, we define the edges of the target bins
    Output will be an array with coordinate density the linear centre of these bins. If we choose `potrho_edges`, the end result will have coordinates potrho, which is the same as online binned `ty_trans_rho`.
    """)
    return


@app.cell
def _(expt_datastore):
    potrho_edges = expt_datastore.search(
        variable='potrho_edges',
        start_date='2170-0[1-3].*', 
        frequency='1mon'
    ).to_dask(
        xarray_open_kwargs= {
            'chunks' : 'auto',
            'decode_timedelta': False,
        }
    )['potrho_edges']

    targetbins = potrho_edges.values
    return (targetbins,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Now apply the histogram over the vertical dimension `st_ocean` inside the target bins.
    We include the variable we want to bin in `weights`. This quantity should be extensive, since grid cells vary in sizes, which is true because `ty_trans` is multiplied by the cell size in x and z directions.
    """)
    return


@app.cell
def _(histogram, pot_rho_2_2, targetbins, ty_trans_1):
    # Make sure the variables have a name, otherwise xhistogram doesn't know what to call the bins
    ty_trans_2 = ty_trans_1.rename('ty_trans')
    pot_rho_2_3 = pot_rho_2_2.rename('pot_rho_2')
    ty_trans_mean = histogram(pot_rho_2_3, bins=[targetbins], dim=['st_ocean'], weights=ty_trans_2).rename({pot_rho_2_3.name + '_bin': 'potrho', 'xt_ocean': 'grid_xt_ocean', 'yu_ocean': 'grid_yu_ocean'})
    return pot_rho_2_3, ty_trans_2, ty_trans_mean


@app.cell
def _(ty_trans_mean):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    ty_trans_mean_1 = ty_trans_mean.load()
    return (ty_trans_mean_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Now define meridional overturning streamfunctions as a cumulative sum of transport from the bottom of the ocean.
    """)
    return


@app.function
def cumsum_from_bottom(residual):
    cumsum = residual.cumsum('potrho') - residual.sum('potrho')
    return cumsum


@app.cell
def _(rho_0, ty_trans_mean_1, ty_trans_rho_1):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    psi_avg = cumsum_from_bottom(ty_trans_rho_1.sum('grid_xt_ocean') / (1000000.0 * rho_0)).load()  # .load() since we'll use it a few times in this notebook
    psi_avg_mean = cumsum_from_bottom(ty_trans_mean_1.sum('grid_xt_ocean') / (1000000.0 * rho_0))
    return psi_avg, psi_avg_mean


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plot streamfunctions of the residual, mean (what we just computed) and eddy (the difference) streamfunctions
    """)
    return


@app.cell
def _(np, plt, psi_avg, psi_avg_mean):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    _fig, _axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 4))
    _levels = np.linspace(-25, 25, 26)
    psi_avg.plot.contourf(ax=_axes[0], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    psi_avg_mean.plot.contourf(ax=_axes[1], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    _p = (psi_avg - psi_avg_mean).plot.contourf(ax=_axes[2], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    _cbar_ax = _fig.add_axes([0.92, 0.15, 0.01, 0.7])
    _fig.colorbar(_p, cax=_cbar_ax, label='Transport (Sv)')
    _axes[0].set_title('Residual')
    _axes[1].set_title('Mean')
    _axes[2].set_title('Eddy')
    for _ax in _axes:
        _ax.set_ylim(1037.5, 1032)
        _ax.set_xlim(-70, -35)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Method 2: `xgcm`

    Use `xgcm`'s conservative binning, described in the [tutorial](https://xgcm.readthedocs.io/en/stable/transform.html) available in the `xgcm` [documentation](https://xgcm.readthedocs.io/en/stable).

    This method results in a smoother vertical distribution than `xhistogram`, as it is not quite a histogram but does some interpolation to the top and bottom of each vertical cell. We have found that the computation currently has issues with interior land boundaries: `xgcm` isn't able to compute partial cells at the bottom of the ocean in MOM5. We thus add a correction after the computation to ensure that vertical integrals are preserved and thus that streamfunctions calculated are closed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Load vertical grid bin centres and edges
    """)
    return


@app.cell
def _(expt_datastore):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    _ds = expt_datastore.search(variable=['st_ocean', 'st_edges_ocean'], frequency='1mon', start_date='2170-0[1-3].*').to_dask(xarray_open_kwargs={'chunks': 'auto'})
    st_ocean = _ds['st_ocean']
    st_edges_ocean = _ds['st_edges_ocean']  # and `frequency` gets us down to a single dataset  # This is the easiest way to get a dataset to open relatively quickly
    return (st_edges_ocean,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Define edge of target density bins
    """)
    return


@app.cell
def _(expt_datastore):
    _ds = expt_datastore.search(variable='potrho_edges', frequency='1mon', start_date='2170-0[1-3].*').to_dask(xarray_open_kwargs={'chunks': 'auto'})
    pot_rho_2_target = _ds['potrho_edges'].values  # This is the easiest way to get a dataset to open relatively quickly
    return (pot_rho_2_target,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Calculate vertical regridding into density coordinates
    """)
    return


@app.cell
def _(pot_rho_2_3, pot_rho_2_target, st_edges_ocean, ty_trans_2, xgcm, xr):
    _ds = xr.Dataset({'ty_trans': ty_trans_2, 'pot_rho_2': pot_rho_2_3})
    _ds = _ds.assign_coords({'st_edges_ocean': st_edges_ocean})
    _ds = _ds.chunk({'st_edges_ocean': 76, 'st_ocean': 75})
    _grid = xgcm.Grid(_ds, coords={'Z': {'center': 'st_ocean', 'outer': 'st_edges_ocean'}}, periodic=False, autoparse_metadata=False)
    _ds['pot_rho_2_outer'] = _grid.interp(_ds.pot_rho_2, 'Z', boundary='extend')
    _ds['pot_rho_2_outer'] = _ds['pot_rho_2_outer'].chunk({'st_edges_ocean': 76})
    ty_trans_transformed_cons = _grid.transform(_ds.ty_trans, 'Z', pot_rho_2_target, method='conservative', target_data=_ds.pot_rho_2_outer)
    ty_trans_transformed_cons = ty_trans_transformed_cons.rename({'pot_rho_2_outer': 'potrho'})
    return (ty_trans_transformed_cons,)


@app.cell
def _(ty_trans_transformed_cons):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    ty_trans_transformed_cons_1 = ty_trans_transformed_cons.load()
    return (ty_trans_transformed_cons_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Now account for partial cell at bottom
    We do this by finding what is missing from the vertical integral (residual). This is what was in the partial cell. We then add that residual into the densest cell that currently exists in the transformed data. This is only an approximation, because the density of the partial cell may be denser than that of the cell above it. However, this correction means the vertical integral is preserved under the transformation.
    """)
    return


@app.cell
def _(ty_trans_2, ty_trans_transformed_cons_1):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    #find residual from vertical integral
    ty_trans_residual = ty_trans_2.sum('st_ocean') - ty_trans_transformed_cons_1.sum('potrho')  #this is positive definite
    return (ty_trans_residual,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Find bottom density of `ty_trans_transformed_cons`
    """)
    return


@app.cell
def _(ty_trans_transformed_cons_1):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    # select out bottom values:
    ty_trans_transformed_cons2 = ty_trans_transformed_cons_1.where(ty_trans_transformed_cons_1 != 0)
    dens_array = ty_trans_transformed_cons2 * 0 + ty_trans_transformed_cons2.potrho  # array of isopycnal value where it exists and nan elsewhere
    max_dens = dens_array.max(dim='potrho', skipna=True)
    return dens_array, max_dens


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Add residual to this bottom density in array
    """)
    return


@app.cell
def _(dens_array, max_dens, ty_trans_residual, ty_trans_transformed_cons_1):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    ty_trans_residual_array = (dens_array.where(dens_array == max_dens) * 0 + 1) * ty_trans_residual
    ty_trans_new = ty_trans_residual_array.fillna(0) + ty_trans_transformed_cons_1
    return (ty_trans_new,)


@app.cell
def _(ty_trans_new):
    # rename coords to match ty_trans_rho
    ty_trans_new_1 = ty_trans_new.rename({'yu_ocean': 'grid_yu_ocean', 'xt_ocean': 'grid_xt_ocean'})
    return (ty_trans_new_1,)


@app.cell
def _(ty_trans_new_1):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    # We need to rechunk here to make the chunks a bit smaller, otherwise the dask workers will die.
    # I've halved the chunk size on `grid_xt_ocean` and `potrho`. Sometimes, {'chunks' : 'auto'} can be
    # a bit too ambitious!
    ty_trans_new_2 = ty_trans_new_1.chunk(chunks={'grid_yu_ocean': 337, 'grid_xt_ocean': 200, 'potrho': 40})
    ty_trans_new_2 = ty_trans_new_2.load()  # was 400  # was 80
    return (ty_trans_new_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plot streamfunction of result
    """)
    return


@app.cell
def _(rho_0, ty_trans_new_2):
    psi_avg_mean_2 = cumsum_from_bottom(ty_trans_new_2.sum('grid_xt_ocean') / (1000000.0 * rho_0))
    return (psi_avg_mean_2,)


@app.cell
def _(np, plt, psi_avg, psi_avg_mean_2):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    _fig, _axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 4))
    _levels = np.linspace(-25, 25, 26)
    psi_avg.plot.contourf(ax=_axes[0], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    psi_avg_mean_2.plot.contourf(ax=_axes[1], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    _p = (psi_avg - psi_avg_mean_2).plot.contourf(ax=_axes[2], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    _cbar_ax = _fig.add_axes([0.92, 0.15, 0.01, 0.7])
    _fig.colorbar(_p, cax=_cbar_ax, label='Transport (Sv)')
    _axes[0].set_title('Residual')
    _axes[1].set_title('Mean')
    _axes[2].set_title('Eddy')
    for _ax in _axes:
        _ax.set_ylim(1037.5, 1032)
        _ax.set_xlim(-70, -35)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Method 3: Bin `ty_trans` (mean Eulerian overturning) into density bins

    This uses the method by Lee et al. (2007) and which is is described as follows. Firstly, cells in the model output with a density $\rho$ between two prescribed densities ($\rho_\text{heavy} >\rho> \rho_\text{light}$) are selected. Each cell is assigned a proximity to the lighter density $\rho_\text{light}$, which is the 'bin fraction' $$f_b = \frac{\rho_\text{heavy}-\rho}{\rho_\text{heavy}-\rho_\text{light}}.$$

    Here, a bin fraction of 1 means the cell density $\rho = \rho_\text{light}$ and $f_b=0$ means $\rho = \rho_\text{heavy}$. The quantity being binned, such as the meridional transport $vh$, is then multiplied by $f_b$ and added to the lighter density $\rho_\text{light}$ bin's meridional transport, followed by the $vh(1-f_b)$ being added to the heavier bin, $\rho_\text{heavy}$. This process is repeated for all sets of consecutive bins, meaning that density bins have input from model output cells with density slightly lower and higher than it.

    > Lee, M., Nurser, A., Coward, A., and De Cuevas, B. (2007). [Eddy advective and diffusive
    transports of heat and salt in the Southern Ocean.](https://doi.org/10.1175/JPO3057.1) _Journal of Physical Oceanography_, **37(5)**, 1376–1393.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### For this method, we need to get rid of NaNs
    """)
    return


@app.cell
def _(pot_rho_2_3, ty_trans_2):
    ty_trans_3 = ty_trans_2.fillna(0)
    pot_rho_2_4 = pot_rho_2_3.fillna(0)
    return pot_rho_2_4, ty_trans_3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Load first to reduce computation time
    """)
    return


@app.cell
def _(pot_rho_2_4, ty_trans_3):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    pot_rho_2_5 = pot_rho_2_4.load()
    ty_trans_4 = ty_trans_3.load()
    return pot_rho_2_5, ty_trans_4


@app.cell
def _(np, pot_rho_2_5, ty_trans_rho_1):
    # choose bins (in this case, default ty_trans_rho pot_rho_2 bins
    rho2_bins = ty_trans_rho_1.potrho.values
    # set up a zero array to be filled in by the algorithm
    ty_trans_binned = np.zeros((len(rho2_bins), len(pot_rho_2_5.yu_ocean), len(pot_rho_2_5.xt_ocean)))
    return rho2_bins, ty_trans_binned


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Note**: the following cell takes a while.
    """)
    return


@app.cell
def _(pot_rho_2_5, rho2_bins, ty_trans_4, ty_trans_binned):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    from tqdm.auto import tqdm
    for i in tqdm(range(len(rho2_bins) - 1)):
        bin_mask = pot_rho_2_5.where(pot_rho_2_5 <= rho2_bins[i + 1]).where(pot_rho_2_5 > rho2_bins[i]) * 0 + 1
    # loop over the bins, performing algorithm by Lee et al. (2007)
    # note that it takes time; faster if ty_trans and pot_rho_2 already loaded
        bin_fractions = (rho2_bins[i + 1] - pot_rho_2_5 * bin_mask) / (rho2_bins[i + 1] - rho2_bins[i])
        ty_trans_in_lower_bin = (ty_trans_4 * bin_mask * bin_fractions).sum(dim='st_ocean')
        ty_trans_binned[i, :, :] = ty_trans_binned[i, :, :] + ty_trans_in_lower_bin.fillna(0).values
        del ty_trans_in_lower_bin  ## bin ty_trans:
        ty_trans_in_upper_bin = (ty_trans_4 * bin_mask * (1 - bin_fractions)).sum(dim='st_ocean')
        ty_trans_binned[i + 1, :, :] = ty_trans_binned[i + 1, :, :] + ty_trans_in_upper_bin.fillna(0).values
        del ty_trans_in_upper_bin
    return


@app.cell
def _(pot_rho_2_5, rho2_bins, ty_trans_binned, xr):
    # convert numpy array into xarray dataarray
    ty_trans_binned_array = xr.DataArray(ty_trans_binned, coords=[rho2_bins, pot_rho_2_5.yu_ocean, pot_rho_2_5.xt_ocean], dims=['potrho', 'grid_yu_ocean', 'grid_xt_ocean'], name='ty_trans_binned')
    return (ty_trans_binned_array,)


@app.cell
def _(rho_0, ty_trans_binned_array):
    # find streamfunction
    psi_avg_mean_3 = cumsum_from_bottom(ty_trans_binned_array.sum('grid_xt_ocean')) / (1e6 * rho_0)
    return (psi_avg_mean_3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plot streamfunctions
    """)
    return


@app.cell
def _(np, plt, psi_avg, psi_avg_mean_3):
    _fig, _axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 4))
    _levels = np.linspace(-25, 25, 26)
    psi_avg.plot.contourf(ax=_axes[0], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    psi_avg_mean_3.plot.contourf(ax=_axes[1], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    _p = (psi_avg - psi_avg_mean_3).plot.contourf(ax=_axes[2], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    _cbar_ax = _fig.add_axes([0.92, 0.15, 0.01, 0.7])
    _fig.colorbar(_p, cax=_cbar_ax, label='Transport (Sv)')
    _axes[0].set_title('Residual')
    _axes[1].set_title('Mean')
    _axes[2].set_title('Eddy')
    for _ax in _axes:
        _ax.set_ylim(1037.5, 1032)
        _ax.set_xlim(-70, -35)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### All three methods yield similar plots of the decomposition of the meridional overturning streamfunction.

    The exact numbers resulting from the transformations differ, due to the different numerical methods. `xhistogram` is exact when compared to snapshots of MOM5 model output, and is hence most appropriate when comparing between online and offline binned quantities. `xgcm` and the Lee method can still be used to compare quantities binned offline. For example, if we were to instead bin the daily transports onto isopycnals and calculate eddy terms directly from the correlation of velocity and thickness fluctuations, `xgcm` and the Lee method may be better as the weighted binning onto isopycnals leaves less chance of 'gaps' between density layers. The Lee method has no issues with partial cells, but it is **much slower** than `xgcm`.

    The difference in the mean streamfunction between the three methods is presented below.
    """)
    return


@app.cell
def _(np, plt, psi_avg_mean, psi_avg_mean_2, psi_avg_mean_3):
    _fig, _axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 4))
    _levels = np.arange(-10, 10.1, 0.5)
    (psi_avg_mean - psi_avg_mean_2).plot.contourf(ax=_axes[0], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    (psi_avg_mean - psi_avg_mean_3).plot.contourf(ax=_axes[1], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    _p = (psi_avg_mean_2 - psi_avg_mean_3).plot.contourf(ax=_axes[2], x='grid_yu_ocean', levels=_levels, add_colorbar=False)
    _cbar_ax = _fig.add_axes([0.92, 0.15, 0.01, 0.7])
    _fig.colorbar(_p, cax=_cbar_ax, label='Transport (Sv)')
    _axes[0].set_title('Method 1 - Method 2')
    _axes[1].set_title('Method 1 - Method 3')
    _axes[2].set_title('Method 2 - Method 3')
    for _ax in _axes:
        _ax.set_ylim(1037.5, 1032)
        _ax.set_xlim(-70, -35)
    _fig.suptitle('Difference in Mean Streamfunction', fontsize=16)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    An alternative method to calculate the decomposition of the residual meridional overturning circulation into mean and eddy components is to bin `ty_trans` (or `vhrho_nt`) into density bins using daily data (both density and transport). Then the transport $\overline{vh}$ can be separated into a mean component $\overline{v}\overline{h}$ and an eddy component $\overline{v^\prime h^\prime}$, where the overline is a time average and primed quantities the deviation from the time average. Quantities are calculated within density layers, and $h$ is density layer thickness, calculated by binning `dzt` or `dzu`. This calculation, since it uses daily data, is computationally expensive and is difficult to do efficiently in a Jupyter notebook. The resulting streamfunctions are similar, but not identical, and may be more intuitive for isopycnal flows. An example of this method can be found at https://github.com/claireyung/Topographic_Hotspots_Upwelling-Paper_Code/blob/main/Figure_Code/Fig5-Overturning.ipynb.
    """)
    return


if __name__ == "__main__":
    app.run()
