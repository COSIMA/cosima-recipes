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
    # Sea Ice Coordinates & Plotting Examples
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This recipe shows how to load and plot sea ice concentration from sea ice models (CICE5, and SIS2) output, while also indicating how to get around some of the pitfalls and foibles in CICE temporal and spatial gridding.

    Requirements: The `conda/analysis3` module from `/g/data/xp65/public/modules`.

    - This recipe directly searches the intake catalog for coordinates, and so will require `conda/analysis3-25.02` or later.
    - This recipe was run on a large ARE instance, and may not work if run with fewer resources.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Firstly, load modules:
    """)
    return


@app.cell
def _():
    import intake
    from dask.distributed import Client
    from datetime import timedelta

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import matplotlib.path as mpath
    import cmocean.cm as cmo

    return Client, ccrs, cfeature, cmo, intake, mpath, np, plt, timedelta


@app.cell
def _(Client):
    client = Client(threads_per_worker=1)
    client.dashboard_link
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Open the catalog
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next we will select an experiment which uses the `cice5` sea ice model. Experiment `01deg_jra55v13_ryf9091` is a 0.1-degree repeat-year forcing run using MOM5. In CICE, areal sea ice concentration is called `aice_m`, where the `m` refers to the variable being averaged on a monthly basis.

    If you want a different experiment change the necessary values.
    """)
    return


@app.cell
def _():
    model = "cice5"
    experiment = "01deg_jra55v13_ryf9091" 
    variable = "aice_m"
    area_variable = "area_t"
    geo_variables = ["geolon_t", "geolat_t"]
    return area_variable, experiment, variable


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Note**: We could adapt these variables to instead select another experiment or even one using SIS2 and MOM6 by specifying:

    ```python
    experiment = "OM4_025.JRA_RYF"
    variable = "siconc"
    area_variable = "areacello"
    geo_variables = ["geolon", "geolat"]
    ```
    Since the SIS2 model is smaller than the CICE5 model, it may be easier to use if you have limited computing power.
    """)
    return


@app.cell
def _(catalog, experiment):
    cat_subset = catalog[experiment]
    cat_subset
    return (cat_subset,)


@app.cell
def _(cat_subset, variable):
    var_search = cat_subset.search(
                    variable = variable, 
                    frequency = "1mon"
                 )
    var_search
    return (var_search,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next we open the dataset as an xarray dataset. We use the `decode_coords=False` flag, to get around some messy issues with the way xarray decides to load CICE grids. To speed up opening data, we also set xarray [combine by coords](https://docs.xarray.dev/en/latest/generated/xarray.combine_by_coords.html) arguments here, as the data are spread across many files. These arguments can always be used to speed up opening data from CICE4 and CICE5 models, or any case where it is safe to assume the coordinates (other than time) in the first file opened are identical for the whole dataset.
    """)
    return


@app.cell
def _(var_search):
    dset = var_search.to_dask( 
        xarray_open_kwargs=dict(
            decode_coords = False,
            chunks = -1 # Read each file as a whole
        ) , 
        xarray_combine_by_coords_kwargs=dict(
            compat="override", # Speeds up performance (see Issue #460 on the Github repo for discussion on this)
            data_vars="minimal",
            coords="minimal"
        )
    )
    return (dset,)


@app.cell
def _(dset, variable):
    sic = dset[variable]
    sic
    return (sic,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Another messy thing about CICE5 is that it thinks that monthly data for, say, January occurs at midnight on Jan 31 -- while xarray interprets this as the first milllisecond of February.**

    To get around this, note that we loaded data from February above, and we now subtract 12 hours from the time dimension. This means that, at least data is sitting in the correct month, and really helps to compute monthly climatologies correctly.
    """)
    return


@app.cell
def _(sic, timedelta):
    sic['time'] = sic.time.to_pandas() - timedelta(hours = 12)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We increase the chunk size in time to speed up reading of data, and choose ten years of interest.
    """)
    return


@app.cell
def _(sic):
    sic_1 = sic.chunk({'time': 12})
    sic_1 = sic_1.sel(time=slice('1981', '1990'))
    sic_1
    return (sic_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note that `aice_m` is the monthly average of fractional ice area in each grid cell aka the concentration. **To find the actual area of the ice we need to know the area of each cell. Unfortunately, CICE5 doesn't save this for us ... but the ocean model does.** So, let's load `area_t` from the ocean model, and rename the coordinates in our ice variable to match the ocean model. Then we can multiply the ice concentration with the cell area to get a total ice area.
    """)
    return


@app.cell
def _(area_variable, cat_subset):
    var_search_1 = cat_subset.search(variable=area_variable)
    ds = var_search_1.to_dask()
    area = ds[area_variable].load()
    area
    return (area,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Our CICE data is missing x- and y-coordinate values, so we can also get them from `area_t`
    """)
    return


@app.cell
def _(area, sic_1):
    sic_1.coords['ni'] = area['xt_ocean'].values
    sic_1.coords['nj'] = area['yt_ocean'].values
    sic_1['ni'].attrs = area['xt_ocean'].attrs
    sic_1['nj'].attrs = area['yt_ocean'].attrs
    sic_2 = sic_1.rename({'ni': 'xt_ocean', 'nj': 'yt_ocean'})
    sic_2
    return (sic_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Note:**
    Using the '1d' coordinates of `xt_ocean` and `yt_ocean` isn't strictly speaking correct due to the tripolar grid. However, because we will sum over the whole of each hemisphere, so it doesn't matter in practice.

    The real longitude and latitudes are the 2-dimensional `geolon_t` and `geolat_t`, respectively.

    Also, if you are looking at SIS2 output you will have to update the names of the indices (`xt_ocean` and `yt_ocean`) here and below.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Sea Ice Area
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's look at a timeseries of SH sea ice area. Area is defined (per convention) as the sum of sea ice concentration multiply by the area of each grid cell (and masked for sea ice concentration above 15%)

    By convention, sea-ice area for a region or basin is the sum of the area's where concentration is greater than 15%.
    We also need to drop `geolon` and `geolat` so we have unique longitude and latitude to reference.
    """)
    return


@app.cell
def _(area, sic_2):
    sic_3 = sic_2.where(sic_2 >= 0.15)
    si_area = sic_3 * area
    si_area = si_area.drop_vars({'geolon_t', 'geolat_t'})
    si_area
    return si_area, sic_3


@app.cell
def _(si_area):
    SH_area = si_area.sel(yt_ocean = slice(-90, -45)).sum(['xt_ocean', 'yt_ocean'])
    NH_area = si_area.sel(yt_ocean = slice(45, 90)).sum(['xt_ocean', 'yt_ocean'])

    SH_area
    return NH_area, SH_area


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As we are using a repeat year forcing experiemnt, the sea ice cycle is very regular:
    """)
    return


@app.cell
def _(NH_area, SH_area, plt):
    (SH_area / 1e12).plot(label = 'Antarctic')   # convert from m^2 -> 10^6 km^2
    (NH_area / 1e12).plot(label = 'Arctic')      # convert from m^2 -> 10^6 km^2

    plt.legend(loc='lower right')
    plt.ylabel('Sea Ice Area (10$^6$ km$^2$)');
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And the seasonal cycle of sea-ice area:
    """)
    return


@app.cell
def _(NH_area, SH_area, plt):
    (SH_area / 1e12).groupby('time.month').mean('time').plot(label = 'Antarctic')   # convert from m^2 -> 10^6 km^2
    (NH_area / 1e12).groupby('time.month').mean('time').plot(label = 'Arctic')      # convert from m^2 -> 10^6 km^2

    plt.legend()
    plt.ylabel('Sea Ice Area (10$^6$ km$^2$)');
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Making Maps
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If we just plot a selected month now, you see that everything North of 65$^\circ$ N is skewed.
    """)
    return


@app.cell
def _(ccrs, cmo, plt, sic_3):
    _ax = plt.subplot(projection=ccrs.PlateCarree())
    sic_3.sel(time='1985-08').plot(cmap=cmo.ice)
    _ax.coastlines()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Most of our work is in the Southern Ocean, so maybe we don't care. But if you are interested in the Arctic, then we need to account for the tri-polar ocean grid that out models use. The easiest way out of that is using `contourf`, and the passing the x- and y-coordinates.

    See [Making Maps with Cartopy](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/01-Basics/03-Maps_with_Cartopy.html) tutorial for more help with plotting!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We need the `geolon` and `geolat` fields from the model output for the actual (two-pole) coordinates, instead of the model's (three-pole) coordinates.
    """)
    return


@app.cell
def _(area):
    area
    return


@app.cell
def _(area, sic_3):
    sic_4 = sic_3.assign_coords({'geolat': area.geolat_t, 'geolon': area.geolon_t})
    return (sic_4,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use `contourf`, and the `geolon` and `geolat` fields
    """)
    return


@app.cell
def _(ccrs, cmo, plt, sic_4):
    _ax = plt.subplot(projection=ccrs.PlateCarree())
    sic_4.sel(time='1985-08').squeeze('time').plot.contourf(transform=ccrs.PlateCarree(), x='geolon', y='geolat', levels=33, cmap=cmo.ice)
    _ax.coastlines()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Using Cartopy, we can make Polar Stereographic plots of sea ice concentration for a selected month, as follows:
    """)
    return


@app.cell
def _(ccrs, cfeature, cmo, mpath, np, plt):
    def plot_sic(data):
        """ 
        Plot sea ice concentration (SIC) on a polar stereographic map 
        with a circular boundary, where longitude and latitude are 
        given as `geolon` and `geolat`.

        Parameters
        ----------
        data : xarray.DataArray
            Sea ice concentration with coordinates 'geolon' and 'geolat'.
        """
        _ax = plt.gca()
        theta = np.linspace(0, 2 * np.pi, 100)
        center, radius = ([0.5, 0.5], 0.5)
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T  # Map the plot boundaries to a circle
        circle = mpath.Path(verts * radius + center)
        _ax.set_boundary(circle, transform=_ax.transAxes)
        _ax.add_feature(cfeature.NaturalEarthFeature('physical', 'land', '50m', edgecolor=None, facecolor='gainsboro'), zorder=2)
        data.plot.contourf(transform=ccrs.PlateCarree(), x='geolon', y='geolat', levels=np.arange(0.15, 1.05, 0.05), cmap=cmo.ice, cbar_kwargs={'label': 'Sea Ice Concentration'})
        gl = _ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.2, linestyle='--', ylocs=np.arange(-80, 81, 10))
        _ax.coastlines(zorder=2)  # Add land features and gridlines  # disabled since it can cause some spurious lines to appear

    return (plot_sic,)


@app.cell
def _(ccrs, plot_sic, plt, sic_4):
    def plot_sic_southern_hemisphere():
        _ax = plt.subplot(projection=ccrs.SouthPolarStereo())
        _ax.set_extent([-180, 180, -90, -50], crs=ccrs.PlateCarree())
        plot_sic(sic_4.sel(time='1985-08').squeeze('time'))
    plot_sic_southern_hemisphere()
    return


@app.cell
def _(ccrs, plot_sic, plt, sic_4):
    def plot_sic_northern_hemisphere():
        _ax = plt.subplot(projection=ccrs.NorthPolarStereo(central_longitude=-45))
        _ax.set_extent([-180, 180, 40, 90], crs=ccrs.PlateCarree())
        plot_sic(sic_4.sel(time='1985-02').squeeze('time'))
    plot_sic_northern_hemisphere()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Once we are happy with your plot, we can save the plot to disk using `plt.savefig('filepath/filename')` function at the end of the cell containing the plot we want to save, as shown below. Note that the filename must contain the extension (e.g., `.pdf`, `.jpeg`, `.png`, etc).

    For more information on the options available to save figures refer to [Matplotlib documentation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```python
    plot_sic_southern_hemisphere()
    plt.savefig('MyFirstSeaIcePlot.png', dpi = 300)
    ```
    """)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
