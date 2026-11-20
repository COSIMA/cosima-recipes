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
    # Relative Vorticity

    This notebook shows a simple example of calculation the vertical component of relative vorticity, but is applicable to any curl calculation as well.

    ## Background

    Relative vorticity is defined as the curl of the velocity field:

    $$\zeta = \partial_x v - \partial_y u.$$

    For demonstration purposes we will compute the vorticity at some arbitrary depth for a given month, but the method can be applied to any time-varying, 3D field.

    We will demonstrate two methods for computing relative vorticity:

    1. The recommended method, leveraging the functionality of `xgcm` to handle grid operations.
    2. A naïve method of simply converting degrees of longitude/latitude into metres and differentiating via `xarray`.

    We compare these two methods to the model's vorticity diagnostic. We show that Method 1 is accurate, and should be used over Method 2.

    ---

    This recipe is intended to work with output from ACCESS-OM2, where MOM5 uses an Arakawa B-grid and velocities are given at cell corners. For adaptation to MOM6, which uses an Arakawa C-grid, you should take into account that velocities are in cell faces. This means that:

    | MOM5 diagnostic (x-coord, y-coord) | MOM6 diagnostic (x-coord, y-coord) |
    | --- | --- |
    | `u (xu_ocean, yu_ocean)`  | `uo (xq, yh)` |
    | `v (xu_ocean, yu_ocean)`  | `vo (xh, yq)` |
    | `vorticity_z (xt_ocean, yt_ocean)`  | `RV (xq, yq)` |

    Most experiments will also have four different options of $\mathrm{d}x$ and $\mathrm{d}y$ to account for distances in different grids/faces. For MOM6, we recommend that you approach the calculation using Method 1 by adapting the interpolation steps to suit MOM6 diagnostics and where each flow field lives.
    """)
    return


@app.cell
def _():
    import intake
    import matplotlib.pyplot as plt
    import numpy as np
    import xarray as xr
    from dask.distributed import Client

    return Client, intake, np, plt, xr


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load a `dask` client.
    """)
    return


@app.cell
def _(Client):
    client = Client(threads_per_worker=1, memory_limit=0)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Open the ACCESS-NRI default catalog and the first cycle of the 0.1$^{\circ}$ IAF experiment. This recipe uses this experiment because it has velocity and vorticity diagnostics available at the same time step. This will allow us to compare methods.
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell
def _():
    experiment = "01deg_jra55v140_iaf"
    return (experiment,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load the diagnostics needed for this recipe - note that `intake` is not able, currently, to load `to_dask` datasets in different grids, so we will load them separately.

    We will load grid diagnostics (distances in meridional and zonal directions, as well as latitude, longitude), one day of velocities at a certain depth level, and MOM5's relative vorticity diagnostic, which we will use to compare the three methods.
    """)
    return


@app.cell
def _(catalog, experiment):
    geolon_c = catalog[experiment].search(variable=['geolon_c'],
                                          frequency="fx").to_dask()['geolon_c']
    geolon_c = geolon_c.sel(xu_ocean=slice(-90, -40), yu_ocean=slice(20, 60))

    geolat_c = catalog[experiment].search(variable=['geolat_c'],
                                          frequency="fx").to_dask()['geolat_c']
    geolat_c = geolat_c.sel(xu_ocean=slice(-90, -40), yu_ocean=slice(20, 60))
    return geolat_c, geolon_c


@app.cell
def _(catalog):
    # u-grid diagnostics
    dxu = catalog["01deg_jra55v140_iaf"].search(variable=["dxu"], 
                                                frequency="fx").to_dask().sel(xu_ocean=slice(-90, -40), yu_ocean=slice(20, 60))
    dyu = catalog["01deg_jra55v140_iaf"].search(variable=["dyu"], 
                                                frequency="fx").to_dask().sel(xu_ocean=slice(-90, -40), yu_ocean=slice(20, 60))
    return dxu, dyu


@app.cell
def _(catalog):
    # t-grid diagnostics
    dxt = catalog["01deg_jra55v140_iaf"].search(variable=["dxt"], 
                                                frequency="fx").to_dask().sel(xt_ocean=slice(-90, -40), yt_ocean=slice(20, 60))
    dyt = catalog["01deg_jra55v140_iaf"].search(variable=["dyt"], 
                                                frequency="fx").to_dask().sel(xt_ocean=slice(-90, -40), yt_ocean=slice(20, 60))
    return dxt, dyt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load velocity as monthly snapshots (indicated by the variable cell methods argument)
    """)
    return


@app.cell
def _(catalog, experiment):
    velocity_diagnostics = ["u", "v"]
    depth_level = 30
    def subset_ugrid(ds):
        ds = ds.sel(xu_ocean=slice(-90, -40), yu_ocean=slice(20, 60)).sel(st_ocean=depth_level, method='nearest')
        return ds

    ds_velocity = catalog[experiment].search(variable=velocity_diagnostics, 
                                             frequency="1mon", 
                                             variable_cell_methods='time: point'
                                             ).to_dask(preprocess=subset_ugrid)
    return depth_level, ds_velocity


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load vorticity as monthly snapshots (indicated by the variable cell methods argument)
    """)
    return


@app.cell
def _(catalog, depth_level, experiment):
    def subset_tgrid(ds):
        ds = ds.sel(xt_ocean=slice(-90, -40), yt_ocean=slice(20, 60)).sel(st_ocean=depth_level, method='nearest')
        return ds

    ds_vorticity = catalog[experiment].unwrap().search(variable="vorticity_z",
                                                       frequency="1mon",
                                                       variable_cell_methods='time: point'
                                                       ).to_dask(preprocess=subset_tgrid)
    return (ds_vorticity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Combine all we need in the same dataset and select a random time step
    """)
    return


@app.cell
def _(ds_velocity, ds_vorticity, dxt, dxu, dyt, dyu, xr):
    ds = xr.merge([ds_velocity, ds_vorticity, dxu, dyu, dxt, dyt], compat='override')
    ds = ds.isel(time=-1)
    return (ds,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Method 1: Using `xgcm`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    [`xgcm`](https://xgcm.readthedocs.io/en/stable/) is a package that deals with staggered grids that are typically used in ocean models. An excerpt from `xgcm`'s docs mentions:

    > "(in model output datasets), different variables are located at different positions with respect to a volume or area element (e.g. cell center, cell face, etc.) xgcm solves the problem of how to interpolate and difference these variables from one position to another."
    """)
    return


@app.cell
def _():
    import xgcm

    return (xgcm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We first need to create a `grid` object that has all the information regarding our staggered grid. For our case, `grid` needs to know the location of the `xt_ocean`, `xu_ocean` points (and same for $y$) and their relative orientation to one another, i.e., that `xu_ocean` is shifted to the right of `xt_ocean` by $\frac1{2}$ grid-cell.

    `xgcm` also expects you to pass on grid information in which `xt_ocean`, `xu_ocean` are of the same length and staggered in the correct direction (`u` to the right of `t`) - and same for the y-direction. Lets check that.
    """)
    return


@app.cell
def _(ds):
    ds
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The x-direction is correct, but in the y-direction we need to remove the last t-point:
    """)
    return


@app.cell
def _(ds):
    ds_1 = ds.isel(yt_ocean=slice(None, -1))
    return (ds_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Create a grid object that stores grid information (coordinate names, properties and dimensions):
    """)
    return


@app.cell
def _(ds_1, xgcm):
    metrics = {('X',): ['dxt', 'dxu'], ('Y',): ['dyt', 'dyu']}
    grid = xgcm.Grid(ds_1, metrics=metrics, coords={'X': {'center': 'xt_ocean', 'right': 'xu_ocean'}, 'Y': {'center': 'yt_ocean', 'right': 'yu_ocean'}}, autoparse_metadata=False)  # X distances  # Y distances
    return (grid,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can use this `grid` object to interpolate diagnostics across grids - for example, `grid.interp(v, 'Y')` will interpolate `v` in the y-direction, bringing `v` from `yu_ocean` to `yt_ocean`.

    We can also compute derivatives using the `.derivative` function. For example, $\partial_x v$ is obtained via `grid.derivative(v, 'X')` - note that the result will also shift `v` in the x-direction from corners (`xu_ocean`) to centres (`xt_ocean`).

    We want to calculate vorticity at the centres of tracer cells in order to compare to the `vorticity_z` diagnostic - so we will interpolate accordingly.
    """)
    return


@app.cell
def _(ds_1, grid):
    vx = grid.derivative(ds_1.v, 'X', boundary='extend')
    vx = grid.interp(vx, 'Y', boundary='extend')
    uy = grid.derivative(ds_1.u, 'Y', boundary='extend')
    uy = grid.interp(uy, 'X', boundary='extend')
    ζ_xgcm = vx - uy
    ζ_xgcm = ζ_xgcm.rename('Relative Vorticity')
    ζ_xgcm.attrs['long_name'] = 'Relative Vorticity, ∂v/∂x-∂u/∂y'
    ζ_xgcm.attrs['units'] = 's-1'
    return (ζ_xgcm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now, let's plot `ζ_xgcm`, as well as the difference with the vorticity diagnostic:
    """)
    return


@app.cell
def _(np):
    maxvalue = 5e-5
    levels = np.linspace(-maxvalue, maxvalue, 24)
    return (levels,)


@app.cell
def _(ds_1, geolat_c, geolon_c, levels, np, plt, ζ_xgcm):
    _fig, _axs = plt.subplots(1, 2, figsize=(12, 4))
    _c = _axs[0].contourf(geolon_c, geolat_c, ζ_xgcm, levels=levels, cmap='RdBu_r', extend='both')
    plt.colorbar(_c)
    _axs[1].set_title('$\\zeta_{xgcm}$')
    _c = _axs[1].contourf(geolon_c, geolat_c, np.abs(ζ_xgcm - ds_1['vorticity_z']), levels=np.linspace(0, 1e-10, 22), cmap='Oranges', extend='max')
    plt.colorbar(_c)
    _axs[1].set_title('$\\zeta_{xgcm}$ - vorticity_z')
    for _ax in _axs:
        _ax.set_xlabel('longitude')
        _ax.set_ylabel('latitude')
        _ax.set_xlim(-90, -40)
        _ax.set_ylim(20, 60)
    plt.tight_layout()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note that `xgcm` doesn't handle the edges of the domain quite well, and a similar issue could happen around coastlines - **you should be extra careful in those areas!**

    Another thing to consider is that the model uses double precision arithmetic - but these diagnostics are saved as `float32`. Therefore, the differences between our offline calculation and the diagnostics are not exactly zero - but they are around 5 orders of magnitude smaller which is pretty good!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Method 2 (naïve computation using `xarray`)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To compute relative vorticity $\zeta = \partial_x v - \partial_y u$ we simply differentiate the velocity components with respect of `lon` (here `xu_ocean` in degrees) and `lat` (here `yu_ocean` in degrees). We then convert the derivatives from units of degrees$^{-1}$ to m$^{-1}$. To do so, we use the value of the radius of the Earth `Rearth` and also take into account that as we go towards the poles the `lon`-grid spacing is scaled by $\cos($ `lat` $)$.

    (Note the unicode characters like `ζ` can be used in `python`.)
    """)
    return


@app.cell
def _():
    # values used by MOM5
    Ω = 7.292e-5  # Earth's rotation rate; in radians/s
    Rearth = 6371e3  # Earth's radius; in m
    return Rearth, Ω


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Calculate the Coriolis parameter $f = 2\Omega \sin(\texttt{lat})$.
    """)
    return


@app.cell
def _(geolat_c, np, Ω):
    f = 2 * Ω * np.sin(np.deg2rad(geolat_c))  # convert lat in radians
    f = f.rename("Coriolis")
    f.attrs["long_name"] = "Coriolis parameter"
    f.attrs["units"] = "s-1"
    f.attrs["coordinates"] = "geolon_c geolat_c"
    return (f,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can calculate relative vorticity:
    """)
    return


@app.cell
def _(Rearth, ds_1, geolat_c, np):
    scale_factor_x = np.deg2rad(Rearth * np.cos(np.deg2rad(geolat_c)))
    scale_factor_y = np.pi / 180 * Rearth
    ζ_naive = ds_1['v'].differentiate('xu_ocean') / scale_factor_x - ds_1['u'].differentiate('yu_ocean') / scale_factor_y
    ζ_naive = ζ_naive.rename('Relative Vorticity').drop_vars('geolat_c')
    ζ_naive.attrs['long_name'] = 'Relative Vorticity, ∂v/∂x-∂u/∂y'
    ζ_naive.attrs['units'] = 's-1'
    return (ζ_naive,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We now plot `ζ_naive` and the difference from the vorticity diagnostic - note that for this we actually need to bring `ζ_naive` to the t-cells.
    """)
    return


@app.cell
def _(grid, ζ_naive):
    ζ_naive_t = grid.interp(ζ_naive, ["X", "Y"], boundary="extend")
    return (ζ_naive_t,)


@app.cell
def _(ds_1, geolat_c, geolon_c, levels, np, plt, ζ_naive, ζ_naive_t):
    _fig, _axs = plt.subplots(1, 2, figsize=(12, 4))
    _c = _axs[0].contourf(geolon_c, geolat_c, ζ_naive, levels=levels, cmap='RdBu_r', extend='both')
    plt.colorbar(_c)
    _axs[1].set_title('$\\zeta_{xgcm}$')
    _c = _axs[1].contourf(geolon_c, geolat_c, np.abs(ζ_naive_t - ds_1['vorticity_z']), levels=np.linspace(0, 1e-05, 22), cmap='Oranges', extend='max')
    plt.colorbar(_c)
    _axs[1].set_title('$\\zeta_{xgcm}$ - vorticity_z')
    for _ax in _axs:
        _ax.set_xlabel('longitude')
        _ax.set_ylabel('latitude')
        _ax.set_xlim(-90, -40)
        _ax.set_ylim(20, 60)
    plt.tight_layout()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As you can see this method is **very** different from the `vorticity_z` diagnostic - the residual is of the same order of magnitude as the diagnostic.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Commentary on the two methods

    Below are some brief discussions/conclusions on the two methods showcased in this recipe.

    #### Note 1
    We have demonstrated that using `xgcm` is the most accurate way of calculating relative vorticity - and the simplest one. Using offline naive computations might lead to significantly different results - so you should be careful if you are interested in budget calculations.

    #### Note 2
    There are other ways of calculating derivatives with `xgcm` documented online, namely using `.diff()` to differentiate and then dividing by the appropriate grid metric. You should be aware that how you choose to do this will impact the end result - you can read a more extensive discussion in this [issue](https://github.com/COSIMA/cosima-recipes/issues/151#issuecomment-4910436540). As this recipe demonstrates, the recommendation is to use `.derivative()`.

    #### Note 3
    It is always useful to understand how the model actually calculates a diagnostic. In the case of `vorticity_z`, you can see [here](https://github.com/mom-ocean/MOM5/blob/64990e1de853a175335848b67b580363053a79b4/src/mom5/ocean_diag/ocean_velocity_diag.F90#L1172-L1183) that the vorticity of a tracer cell is given by the average of $\partial_x v$ at its northern and southern faces, and equivalently $\partial_y u$ is the average of the derivatives at the western and eastern faces. Taking this into account, it is possible to do a naive computation that matches the diagnostic, but **you must have understood the model's code** before doing it! Jumping in head first without knowledge of how the model computed the diagnostic did not yield correct results, as exemplified by Method 2.

    #### Note 4
    Remember to be careful around coastlines, the edges of your domain, and north of 65 North in the tripolar region!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example application - the Rossby number

    To conclude, let's visualize the Rossby number

    $$\mathrm{Ro} = \frac{\zeta }{f},$$

    where $f=2 \Omega \sin \theta$ is the Coriolis parameter.
    """)
    return


@app.cell
def _(f, grid, ζ_xgcm):
    f_1 = grid.interp(grid.interp(f, 'X'), 'Y', boundary='extend')
    Ro = ζ_xgcm / f_1
    Ro = Ro.rename('Rossby number ζ/f')
    return (Ro,)


@app.cell
def _(Ro, np, plt):
    plt.figure(figsize=(8, 5))

    Ro.plot.contourf(levels=np.linspace(-0.15, 0.15, 21),
                     cmap='RdBu_r',
                     extend='both')

    plt.title(
        r"Rossby number $\zeta/f$"
    )
    plt.xlabel("longitude")
    plt.ylabel("latitude")
    plt.xlim(-90, -40)
    plt.ylim(20, 60);
    return


if __name__ == "__main__":
    app.run()
