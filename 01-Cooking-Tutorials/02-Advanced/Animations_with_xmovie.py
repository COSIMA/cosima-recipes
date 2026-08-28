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
    # Animations with xmovie

    This tutorial demonstrates how to make an animation with Cartopy and xmovie. See https://github.com/jbusecke/xmovie for more details on xmovie package.
    """)
    return


@app.cell
def _():
    import intake
    import xarray as xr
    import cmocean as cm
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    from xmovie import Movie

    import warnings
    warnings.filterwarnings(
        action="ignore",
        category=UserWarning,
        message=r"No `(vmin|vmax)` provided. Data limits are calculated from input. Depending on the input this can take long. Pass `\1` to avoid this step"
    )

    # '%matplotlib inline' command supported automatically in marimo
    return Movie, ccrs, cm, intake, plt, xr


@app.cell
def _():
    from dask.distributed import Client
    client = Client(threads_per_worker = 1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Load the ACCESS-NRI catalog
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We use the sea-surface temperature (SST) from a 0.25°-resolution experiment as our sample data. These maps should work with any 2D data.
    """)
    return


@app.cell
def _(catalog):
    experiment = "025deg_jra55_iaf_omip2_cycle6"
    ds = catalog[experiment].search(variable="sst", frequency="1mon").to_dask()

    # convert from degrees K to degrees C
    sst = ds.sst - 273.15

    # slice just few months for the tutorial
    sst = sst.isel(time=slice(0, 11))
    sst
    return (sst,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We load the unmasked coordinates and assign them to the dataset; see the tutorial on maps with Cartopy for more details.
    """)
    return


@app.cell
def _(sst, xr):
    # these lon/lat arrays are NOT masked.
    # NB. This is a hack. We would like to improve this.
    geolon_t = xr.open_dataset('/g/data/ik11/grids/ocean_grid_025.nc').geolon_t
    geolat_t = xr.open_dataset('/g/data/ik11/grids/ocean_grid_025.nc').geolat_t
    sst_1 = sst.assign_coords({'geolat_t': geolat_t, 'geolon_t': geolon_t})
    return (sst_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We create a custom function that plots every frame. See https://xmovie.readthedocs.io/en/latest/examples/quickstart.html#Modifying-plots for more details on the argument structure requirements of this plotting function that we will provide to `xmovie.Movie` method.
    """)
    return


@app.cell
def _(ccrs, cm):
    def plot_sst(da, fig, timestamp, *args, **kwargs):

        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson(central_longitude=-100))

        da.isel(time=timestamp).plot.contourf(
            ax=ax,
            x="geolon_t",
            y="geolat_t",
            levels=33,
            vmin=-2,
            vmax=30,
            extend="both",
            cmap=cm.cm.thermal,
            transform=ccrs.PlateCarree(),
            cbar_kwargs={"label": "SST (°C)", "fraction": 0.03, "aspect": 15, "shrink": 0.7},
        )

        ax.coastlines()
        ax.set_title(da['time'].dt.strftime('%d-%m-%Y')[timestamp].item())

        return ax, None

    return (plot_sst,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we create a figure and the movie using `xmovie.Movie` method.
    """)
    return


@app.cell
def _(Movie, plot_sst, plt, sst_1):
    fig = plt.figure(figsize=(8, 6))
    mov = Movie(sst_1, plot_sst)
    return (mov,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's preview how one of the frames look; choose here frame 2.
    """)
    return


@app.cell
def _(mov):
    mov.preview(2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And now make the movie. We can save as `.gif` or `.mp4`.
    """)
    return


@app.cell
def _(mov):
    mov.save('movie_sst.gif', progress=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ![movie_sst.gif](movie_sst.gif)
    """)
    return


if __name__ == "__main__":
    app.run()
