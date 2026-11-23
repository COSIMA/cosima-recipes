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
    # True Zonal Mean

    Calculate the *true zonal mean* of a scalar quantity regardless of the horizontal mesh.

    Specifically, we calculate the volume weighted mean along all grid cells whose centres fall within finite latitude intervals rather than the arithmetic mean of cells along the model's curvilinear grid. The method presented can also be used to re-grid models onto the same latitudinal grid and the general principles can be used to define any multidimensional sum or average using the `xhistogram` package.

    **Requirements:**
    Select the `conda/analysis3-25.09` (or later) kernel.
    This code should work for just about any MOM5 configuration since all we are grabbing is temeprature and standard grid information. We can swap temperature with any other scalar variable. We can also, in principle, swap latitude with another scalar.

    #### Adapting for MOM6

    |Variable | MOM5 diagnostic | Equivalent MOM6 diagnostic |
    |:--------|-----|------|
    | Temperature | `temp` (conservative temperature) | `thetao` (potential temperature) |
    | Cell volume (m3) | `area_t * dzt` | `volcello` |
    | Lat, lon | `geolon_t`, `geolat_t` | `geolon_t`, `geolat_t` |

    Note that the available MOM6 experiments from the COSIMA community are from a PanAntarctic model and thus limited to the Southern Ocean.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MOM5
    """)
    return


@app.cell
def _():
    import intake
    import matplotlib.pyplot as plt
    import cmocean as cm
    import xarray as xr
    import numpy as np
    from dask.distributed import Client
    from xhistogram.xarray import histogram

    return Client, histogram, intake, np, plt


@app.cell
def _(Client):
    client = Client(threads_per_worker=1)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Open ACCESS-NRI's default catalog:
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Choose the experiment and the variable we want to average. This example uses temperature but you can choose any scalar, 3D variable. The variables `dzt` and `area_t` are also required so we can only use experiments that save those:
    """)
    return


@app.cell
def _(catalog):
    catalog.search(name='.*025deg_jra55.*', variable=["temp", "dzt", "area_t"])
    return


@app.cell
def _():
    experiment = '025deg_jra55_ryf9091_gadi' # any experiment that includes the required variables
    variable = 'temp' # any scalar variable for which volume-weighted average makes sense

    xarray_open_kwargs = dict(use_cftime=True, chunks={"time": -1}, decode_timedelta=False)
    return experiment, variable, xarray_open_kwargs


@app.cell
def _(catalog, experiment, variable, xarray_open_kwargs):
    cat_subset = catalog[experiment]
    _var_search = cat_subset.search(variable=variable, frequency='1yr')
    variable_to_average = _var_search.to_dask(xarray_open_kwargs=xarray_open_kwargs)[variable]
    variable_to_average
    return cat_subset, variable_to_average


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First we show the standard approach, which is to take the arithmetic mean of all grid cells along the quasi-longitudinal coordinate. For MOM5's tri-polar grid this approach is in principle "okay" for the southern hemisphere, where grid cell areas are constant at fixed latitude. It doesn't though, take into account partial cells.

    The `xarray`'s method `.mean(dim='dimension')` applies `numpy.mean()` across that dimension. This is simply the arithmetic mean.

    For some scalar $T$ the arithmetic mean, e.g., across dimension `i`, is given by

    $$ \left<T\right>_{j,k} = \frac{1}{I}\sum_{i=1}^{I} T_{i,j,k},$$

    where $i$, $j$ and $k$ are the indicies in the $x$, $y$ and $z$ directions respectively of the curvilinear grid and $I$ is the number of indicies along the $x$ axis.
    """)
    return


@app.cell
def _(plt, variable_to_average):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    x_arith_mean = variable_to_average.groupby('time.year').mean(dim='time').mean(dim='xt_ocean')

    plt.figure(figsize=(10, 5))
    x_arith_mean.sel(year=2000).plot(yincrease=False, vmin=273, vmax=300, cmap='Oranges')
    plt.title('x-coordinate arithmetic mean');
    return (x_arith_mean,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The main issue with this average is that the 'latitude' coordinate may be meaningless near the north pole, particularly when comparing to observational analyses or other models which can have either a regular grid or a different curvilinear grid. Even different versions of MOM might have different grids!

    Let us consider what the true zonal average looks like. That is consider a set of latitude 'edges' $\{\phi'_{1/2},\phi'_{1+1/2},...,\phi'_{\ell-1/2},\phi'_{\ell+1/2},...,\phi'_{L+1/2}\}$ between which we want to compute an average of $T$ at $\{\phi'_{1},\phi'_{2},...,\phi'_{\ell},...,\phi'_{L}\}$ such that

    $$ \overline{T}(\phi'_\ell,\sigma) = \dfrac{\iint_{\phi'_{\ell-1/2} < \phi \leq \phi'_{\ell+1/2}} T(\phi,\lambda,\sigma)\frac{\partial z}{\partial \sigma}(\phi,\lambda,\sigma)\,\mathrm{d}A}{\iint_{\phi'_{\ell-1/2} < \phi \leq \phi'_{\ell+1/2}}\frac{\partial z}{\partial \sigma}(\phi,\lambda,\sigma)\,\mathrm{d}A},$$

    where $\lambda$ is longitude and $\sigma$ is an arbitrary vertical coordinate.

    In discrete form this average is

    $$\overline{T}_{\ell,k} = \frac{\sum_{i=1}^{I}\sum_{j=1}^{J}\delta_{i,j}T_{i,j,k}\Delta Z_{i,j,k}\Delta \mathrm{Area}_{i,j}}{\sum_{i=1}^{I}\sum_{j=1}^{J}\delta_{i,j,k}\Delta Z_{i,j,k}\Delta \mathrm{Area}_{i,j}},$$

    where $\delta_{i,j} = 1$ if $\phi'_{\ell-1/2}<\phi_{i,j}\leq \phi'_{\ell+1/2}$ and $\delta_{i,j} = 0$ elsewhere, $\Delta Z$ is the grid cell vertical thickness and $\Delta \mathrm{Area}$ is the grid cell horizontal area.

    For our purposes we will use the edges of the models `xt_ocean` coordinate to define $\phi'_{\ell+1/2}$ so the number of 'bins' $L$ will be the same as the length of the quasi-latitude coordinate ($J$).

    Fortunately, as you can see below, the two sums are weighted histograms (one for $T$ times volume and the other for just volume) and these can be rapidly computed using `xhistogram`.

    First let's load the scalar variable (latitude) we want to use as our coordinate then define the bin edges.
    """)
    return


@app.cell
def _(cat_subset):
    coord = 'geolat_t'  # can be any scalar (2D, 3D, eulerian, lagrangian etc)
    _var_search = cat_subset.search(variable=coord, frequency='fx')
    variable_as_coord = _var_search.to_dask(xarray_open_kwargs=dict(use_cftime=True))[coord]
    variable_as_coord
    return (variable_as_coord,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we want to define the coordinate bins as the latitude edges of the t-cells, adding the first edge (0) at latitude -90:
    """)
    return


@app.cell
def _(cat_subset, np):
    # Define the coordinate bins as the latitude edges of the T-cells
    _var_search = cat_subset.search(variable='geolat_c', frequency='fx')
    yu_ocean = _var_search.to_dask(xarray_open_kwargs=dict(use_cftime=True))['yu_ocean']
    # make numpy array (using .values) and add 1st edge at -90
    # Alternatively we could just use some regular grid like this 
    # bins =  np.linspace(-80, 90, 50)
    # or use a grid from a different (coarser) model.
    bins = np.insert(yu_ocean.values, 0, np.array(-90), axis=0)
    return (bins,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now load the thickness and the area of the t-cells and from those compute the volume of each t-cell.
    """)
    return


@app.cell
def _(cat_subset, xarray_open_kwargs):
    _var_search = cat_subset.search(variable='dzt', frequency='1yr')
    dzt = _var_search.to_dask(xarray_open_kwargs=xarray_open_kwargs)['dzt']  # thickness of t-cells
    _var_search = cat_subset.search(variable='area_t', frequency='fx')
    area_t = _var_search.to_dask(xarray_open_kwargs=dict(use_cftime=True))['area_t']
    dVt = dzt * area_t  # area of t-cells  # volume of t-cells
    return (dVt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now let's compute the numerator and denominator of the equation above using `xhistogram`, then the time mean and then the zonal mean.
    """)
    return


@app.cell
def _(bins, dVt, histogram, np, variable_as_coord, variable_to_average):
    histVolCoordDepth = histogram(variable_as_coord.broadcast_like(dVt).where(~np.isnan(dVt)), bins=[bins], weights=dVt, dim=['yt_ocean', 'xt_ocean'])
    histTVolCoordDepth = histogram(variable_as_coord.broadcast_like(dVt).where(~np.isnan(dVt)), bins=[bins], weights=dVt * variable_to_average, dim=['yt_ocean', 'xt_ocean'])
    coord_mean = (histTVolCoordDepth/histVolCoordDepth).groupby('time.year').mean(dim='time')
    return (coord_mean,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can plot the results which, thankfully, retain all the data-array info on variables and axis etc.
    """)
    return


@app.cell
def _(coord_mean, plt):
    # magic command not supported in marimo; please file an issue to add support
    # %%time

    plt.figure(figsize=(10, 5))
    coord_mean.sel(year=2000).plot(yincrease=False, vmin=273, vmax=300, cmap='Oranges')
    plt.title('True zonal mean');
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Since we used the same bin edges as the standard `yt_ocean` coordinate we can take a difference between the arithmetic mean along the model's x-axis and our mean along grid cells within latitude bands. The main differences are near the North Pole where the grid is furthest for being regular. There are also differences near the Antacrtic Shelf suggesting partial cells also matter.
    """)
    return


@app.cell
def _(coord_mean, plt, x_arith_mean):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    _zonal_minus_x_mean = coord_mean.sel(year=2000) - x_arith_mean.sel(year=2000).values
    plt.figure(figsize=(10, 5))
    _zonal_minus_x_mean.plot(yincrease=False, vmin=-0.8, vmax=0.8, cmap='RdBu_r', extend='both')
    plt.title('True zonal minus $x$-coordinate arithmetic mean')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `xarray` has a new `weighted` functionality which allows it to do weighted means instead of arithmetic mean.

    Let's see how that works out... We chose `dVt` as the weights and we only do the comparison for year 2000.
    """)
    return


@app.cell
def _(dVt, variable_to_average):
    variable_to_weighted_average = variable_to_average.copy().sel(time='2000').mean(dim='time')
    variable_to_weighted_average = variable_to_weighted_average.weighted(dVt.sel(time='2000').fillna(0))
    meanweighted_y2000 = variable_to_weighted_average.mean(dim='xt_ocean').groupby('time.year').mean(dim='time').sel(year=2000)
    return (meanweighted_y2000,)


@app.cell
def _(coord_mean, meanweighted_y2000, plt):
    _zonal_minus_x_mean = coord_mean.sel(year=2000) - meanweighted_y2000.values
    plt.figure(figsize=(10, 5))
    _zonal_minus_x_mean.plot(yincrease=False, vmin=-0.8, vmax=0.8, cmap='RdBu_r')
    plt.title("True zonal minus xarray's $x$-coordinate weighted mean")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    South of 65N, where complications of the tripolar grid don't matter, `xarray`'s weighted mean does the job! But in the region of the tripolar we need to be more careful.
    """)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
