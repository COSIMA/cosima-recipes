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
    # Regional Tasmanian domain forced by JRA55-do reanalysis and ACCESS-OM2-01 model output

    ## What does this recipe do?
    This recipe uses `regional-mom6` package to set up a regional ocean configuration with MOM6. The recipe uses input from:

    Input Type | Source | Location on NCI
    ---|---|---
    Surface | [JRA55-do surface forcing](https://climate.mri-jma.go.jp/pub/ocean/JRA55-do/) | `/g/data/ik11`
    Ocean | [ACCESS-OM2-01](https://github.com/COSIMA/access-om2) |  `/g/data/ik11`
    Bathymetry | [GEBCO](https://www.gebco.net/data_and_products/gridded_bathymetry_data/) | `/g/data/ik11`

    Additionally to access to project `ik11`, we also need access to `/g/data/x77` if we want to use the same executable using the latest FMS build (which is a good idea for troubleshooting).
    """)
    return


@app.cell
def _():
    import intake
    import xarray as xr
    import os
    import subprocess
    import matplotlib.pyplot as plt
    from pathlib import Path
    from dask.distributed import Client

    import regional_mom6 as rmom6
    print("using regional-mom6 version " + rmom6.__version__)
    return Client, Path, intake, os, plt, rmom6, subprocess, xr


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start a dask client.
    """)
    return


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What does the `regional-mom6` package do?

    Setting up a regional model in MOM6 can be a pain. The `regional-mom6` package enables users to spend their debugging time fixing a model that's running and doing weird things, rather than puzzling over a model that won't even start.

    This recipe provides a guide to configure a running MOM6 regional model. There will still be some fiddling to do with the `MOM_input` file to make sure that the parameters are set up right for our domain, and we might want to manually edit some of the input files. *But*, `regional-mom6` package should help us bypass most of the woes of regridding, encoding, and understanding the arcane arts of the MOM6 boundary segment files.

    Wanna find out more about `regional-mom6` package? Go to the [package's documentation](https://regional-mom6.readthedocs.io/en/latest/).

    ### Citing

    If you use regional-mom6 package in research, teaching, or other activities, we would be grateful if you could mention regional-mom6 and cite the paper in JOSS:

    > Barnes et al. (2024). regional-mom6: A Python package for automatic generation of regional configurations for the Modular Ocean Model 6. _Journal of Open Source Software_, **9(100)**, 6857, doi:[10.21105/joss.06857](https://doi.org/0.21105/joss.06857).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What does this recipe do?

    This recipe demonstrates how to set up a regional domain using the package. By the end we should have a running MOM6 experiment on the domain of your choice. To make a stable test case:

    * Avoid any regions with ice
    * Avoid regions near the North pole

    Also note, that although the default configuration is meant to be repeat-year forced (RYF), the calendar and encoding will need fixing to run longer than a year.

    Input Type | Source
    ---|---
    Surface | JRA55-do
    Ocean | ACCESS-OM2-01
    Bathymetry | Gebco
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 0: Your personal environment variables
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Some user-custom directories are automatically sourced from the user's environment variables below.
    """)
    return


@app.cell
def _(subprocess):
    scratch = subprocess.run("echo /scratch/$PROJECT/$USER", shell=True, capture_output=True, text=True).stdout.strip()
    home = subprocess.run("echo ~", shell=True, capture_output=True, text=True).stdout.strip()

    for (dir_name, dir) in zip(("scratch", "home"), (scratch, home)):
        print(dir_name, "directory:", dir)
    return home, scratch


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Users can override the paths that were sourced above from their enviroment variables by redefining a directory as a string. For example:

    ```python
    scratch = "/scratch/ab12/xz1234/my_custom_directory_for_this_experiment"
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1: Choose our domain, define workspace paths

    To make sure that things are working we recommend starting with the default example defined below.

    If this runs ok, then we can change to a domain of our choice and hopefully it runs ok too! If not, check the [README](https://github.com/COSIMA/regional-mom6/blob/main/README.md) and [documentation](https://regional-mom6.readthedocs.io/) for troubleshooting tips.

    We can log in and use [Copernicus GUI](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/download) to find the latitude-longitude ranges of the domain of choice and then paste below.
    """)
    return


@app.cell
def _(home, os, scratch):
    expt_name = "tassie-access-om2-forced"

    latitude_extent = [-48, -38.95]
    longitude_extent = [143, 150]

    date_range = ["2013-01-01", "2013-01-05"]

    ## Place where all the input files go
    input_dir = f"{scratch}/regional_mom6_configs/{expt_name}/"

    ## Directory where we'll be running the experiment from
    run_dir = f"{home}/mom6_rundirs/{expt_name}/"

    ## Directory where the compiled FRE tools are located (needed to construct mask tables)
    fre_tools_dir = "/g/data/ik11/mom6_tools/tools"

    ## Directory where ocean model cut-outs go before processing
    tmp_dir = f"{scratch}/{expt_name}"

    ## if directories don't exist, create them
    for path in (run_dir, tmp_dir, input_dir):
        os.makedirs(str(path), exist_ok=True)
    return (
        date_range,
        fre_tools_dir,
        input_dir,
        latitude_extent,
        longitude_extent,
        run_dir,
        tmp_dir,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: Prepare ocean forcing data

    We need to cut out our ocean forcing. The pipeline expects an initial condition and one time-dependent segment per non-land boundary. Naming convention is `"east_unprocessed"` and `"ic_unprocessed"` for initial condition. The following provides an example for cutting out the necessary forcing files from an ocean model. We use data from a Repeat-Year Forced ACCESS-OM2-01 experiment, but we should be able to recycle parts of the code to cut out data from any dataset of our choice.

    We load the ACCESS-OM2-01 output using the Intake catalog. Note that load a slightly bigger region than our indented regional configuration (see `buffer` parameter below). This buffer-region enables proper interpolation of the ACCESS-OM2-01 output to the grid required by MOM6 near the regional domain's boundary.

    First we load the default ACCESS-NRI intake catalog:
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And now we can load the desired ACCESS-OM2-01 model output that we'll use as boundary forcing and initial condition.
    """)
    return


@app.cell
def _(catalog, date_range, latitude_extent, xr):
    buffer = 0.2 # degrees; buffer around the regional domain used for interpolation -- try 2x the input's resolution

    print('Open dataset...')
    experiment = catalog["01deg_jra55v150_iaf_cycle1"]

    ds_dict = experiment.search(
        variable=["u", "v", "salt", "temp", "eta_t"],
        frequency='1day',
        start_date=date_range[0]+", 00:00:00",
    
    ).to_dataset_dict()

    access_om2_input = xr.merge(ds_dict.values(), join="inner")

    access_om2_input = access_om2_input.sel(
            yu_ocean = slice(latitude_extent[0] - buffer, latitude_extent[1] + buffer),
            yt_ocean = slice(latitude_extent[0] - buffer, latitude_extent[1] + buffer))

    access_om2_input = access_om2_input.sel(time=slice(date_range[0], date_range[1]))
    access_om2_input
    return access_om2_input, buffer


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    And now slice the initial conditions and the boundary forings.
    """)
    return


@app.cell
def _(
    access_om2_input,
    buffer,
    latitude_extent,
    longitude_extent,
    rmom6,
    tmp_dir,
):
    print('Initial condition...')

    ## Cut out initial condition and save to netCDF
    ic = access_om2_input.isel(time = 0)

    ## `longitude_slicer` handles seams in longitude and different grid and ensures that the output matches our 'longitude_extent'
    ic = rmom6.longitude_slicer(ic,
                                [longitude_extent[0] - buffer, longitude_extent[1] + buffer],
                                ["xu_ocean", "xt_ocean"])
    ic.drop_encoding().to_netcdf(tmp_dir + "/ic_unprocessed.nc")

    ## Cut out East & West boundary conditions and save to netCDF
    print('East & West boundary conditions...')

    rmom6.longitude_slicer(access_om2_input,
                           [longitude_extent[1] - buffer, longitude_extent[1] + buffer],
                           ["xu_ocean", "xt_ocean"]).to_netcdf(tmp_dir + "/east_unprocessed.nc")

    rmom6.longitude_slicer(access_om2_input,
                           [longitude_extent[0] - buffer, longitude_extent[0] + buffer],
                           ["xu_ocean", "xt_ocean"]).to_netcdf(tmp_dir + "/west_unprocessed.nc")

    ## Cut out North & South boundary conditions and save to netCDF
    print('North & South boundary conditions...')

    northsouth = rmom6.longitude_slicer(access_om2_input,
                                        [longitude_extent[0] - buffer, longitude_extent[1] + buffer],
                                        ["xu_ocean", "xt_ocean"])

    northsouth.sel(
        yu_ocean = slice(latitude_extent[1] - buffer, latitude_extent[1] + buffer),
        yt_ocean = slice(latitude_extent[1] - buffer, latitude_extent[1] + buffer)
    ).to_netcdf(tmp_dir + "/north_unprocessed.nc")

    northsouth.sel(
        yu_ocean = slice(latitude_extent[0] - buffer, latitude_extent[0] + buffer),
        yt_ocean = slice(latitude_extent[0] - buffer, latitude_extent[0] + buffer)
    ).to_netcdf(tmp_dir + "/south_unprocessed.nc")

    print('Finished initial and boundary conditions.')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3: Construct the experiment object
    The `regional_mom6.experiment` returns an object that contains the regional domain basics and also generates the horizontal and vertical grids, `hgrid` and `vgrid` respectively, and sets up the required directory structures as expected by MOM6.
    """)
    return


@app.cell
def _(
    date_range,
    fre_tools_dir,
    input_dir,
    latitude_extent,
    longitude_extent,
    rmom6,
    run_dir,
):
    expt = rmom6.experiment(
        longitude_extent = longitude_extent,
        latitude_extent = latitude_extent,
        date_range = [date_range[0]+" 00:00:00", date_range[1]+" 00:00:00"],
        resolution = 0.05,
        number_vertical_layers = 75,
        layer_thickness_ratio = 10,
        depth = 4500,
        mom_run_dir = run_dir,
        mom_input_dir = input_dir,
        fre_tools_dir = fre_tools_dir,
        boundaries=["north", "south", "east", "west"]
    )
    return (expt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can now access the horizontal and vertical grid of the regional configuration via `expt.hgrid` and `expt.vgrid` respectively.

    Plotting the vertical grid with `marker = '.'` lets us see the spacing.
    """)
    return


@app.cell
def _(expt):
    expt.vgrid.zl.plot(marker='.',
                       y='zl',
                       yincrease=False,
                       figsize=(4, 8))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Modular workflow!

    After constructing our `expt` object, if we are not happy with the default horizontal and vertical grids, `hgrid` and `vgrid`, we can simply modify and then save them back into the `expt` object. However, we'll then also need to save them to disk again. For example:

    ```python
    new_hgrid = xr.open_dataset(input_dir + "/hgrid.nc")
    ```

    Modify `new_hgrid`, ensuring that _all metadata_ is retained to keep MOM6 happy. Then, save our changes:

    ```python
    expt.hgrid = new_hgrid

    expt.hgrid.to_netcdf(input_dir + "/hgrid.nc")
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 4: Set up bathymetry

    Similarly to ocean forcing, we point the experiment's `setup_bathymetry` method at the location of the file of choice and also provide the variable names. We don't need to preprocess the bathymetry since it is simply a two-dimensional field and is easier to deal with. Afterwards we can inspect `expt.bathymetry` to see our regional domain.

    After running this cell, our input directory will contain other bathymetry-related things like the ocean mosaic and mask table too. The mask table defaults to a 10x10 layout and can be modified later.
    """)
    return


@app.cell
def _(expt):
    expt.setup_bathymetry(
        bathymetry_path='/g/data/ik11/inputs/GEBCO_2022/GEBCO_2022.nc',
        longitude_coordinate_name='lon',
        latitude_coordinate_name='lat',
        vertical_coordinate_name='elevation',
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Check out our domain:
    """)
    return


@app.cell
def _(expt):
    expt.bathymetry.depth.plot()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can can add geographical coordinates to the plot above, e.g.,
    """)
    return


@app.cell
def _(expt, plt):
    plt.pcolormesh(expt.bathymetry.lon, expt.bathymetry.lat, expt.bathymetry.depth[0, :, :], shading='auto')
    plt.colorbar(label = 'depth [m]')
    plt.xlabel('Longitude [degrees E]')
    plt.ylabel('Latitude [degrees N]');
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##  Step 5: Handle the ocean forcing - where the magic happens

    This cuts out and interpolates the initial condition as well as all boundaries (unless we don't pass it boundaries).

    The dictionary maps the MOM6 variable names to what they're called in our ocean input file. Notice how the horizontal dimensions are `xt_ocean`, `yt_ocean`, `xu_ocean`, `yu_ocean` in ACCESS-OM2-01 versus `xh`, `yh`, `xq`, and `yq` in MOM6. This is because ACCESS-OM2-01 is on a B grid, so we need to differentiate between `q` and `t` points.

    If one of our segments is land, we can delete its string from the 'boundaries' list. We need to update `MOM_input` to reflect this though so that MOM6 knows how many segments to look for, and their orientations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define a mapping from the MOM5 B-grid variables and dimensions to the MOM6 C-grid ones.
    """)
    return


@app.cell
def _():
    ocean_varnames = {"time": "time",
                      "yh": "yt_ocean",
                      "xh": "xt_ocean",
                      "xq": "xu_ocean",
                      "yq": "yu_ocean",
                      "zl": "st_ocean",
                      "eta": "eta_t",
                      "u": "u",
                      "v": "v",
                      "tracers": {"salt": "salt", "temp": "temp"}
                      }
    return (ocean_varnames,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Set up the initial condition
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    No `xu_ocean` and `xt_ocean` in **west_unprocessed.nc** and **east_unprocessed.nc**

    `xu_ocean = UNLIMITED ; // (0 currently)`
    """)
    return


@app.cell
def _(Path, expt, ocean_varnames, tmp_dir):
    # Set up the initial condition.
    expt.setup_initial_condition(
        tmp_dir + "/ic_unprocessed.nc", # directory where the unprocessed initial condition is stored, as defined earlier
        ocean_varnames,
        arakawa_grid = "B"
        )

    # Set up the four boundary conditions.
    expt.setup_ocean_state_boundaries(
        Path(tmp_dir),
        ocean_varnames,
        arakawa_grid = "B"
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can inspect all variable in the experiment by calling
    """)
    return


@app.cell
def _(expt):
    vars(expt)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Furthermore, we can plot our the interpolated initial condition. It's a good idea to check and ensure things look reasonble, especially near the region's boundaries.
    """)
    return


@app.cell
def _(expt, plt):
    _fig, _axes = plt.subplots(ncols=3, figsize=(16, 4))
    expt.ic_eta.plot(ax=_axes[0])
    expt.ic_vels.u.sel(zl=0, method='nearest').plot(ax=_axes[1])
    expt.ic_vels.v.sel(zl=0, method='nearest').plot(ax=_axes[2])
    _axes[0].set_title('sea surface height')
    _axes[1].set_title('u velocity @ surface')
    _axes[2].set_title('v velocity @ surface')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To ensure that no spurious gradients have emerged at the boundaries (e.g., during the interpolation) we plot a few slices, e.g.,
    """)
    return


@app.cell
def _(expt, plt):
    _fig, _axes = plt.subplots(ncols=3, figsize=(16, 4))
    expt.ic_eta.isel(nx=0).plot(ax=_axes[0])
    expt.ic_vels.u.isel(ny=0, zl=0).plot(ax=_axes[1])
    expt.ic_vels.v.isel(nyp=0, zl=0).plot(ax=_axes[2])
    _axes[0].set_title('sea surface height')
    _axes[1].set_title('u velocity @ surface')
    _axes[2].set_title('v velocity @ surface')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 6: Run the FRE tools

    This is just a wrapper for the FRE tools needed to make the mosaics and masks for the experiment. The only thing we need to tell it is the processor layout. In this case we're asking for a 10 by 10 grid of 100 processors.
    """)
    return


@app.cell
def _(expt):
    expt.run_FRE_tools(layout = (10, 10)) ## tuple defines the processor layout
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 7: Modify the default input directory to make a runnable configuration out of the box

    This step copies the default directory, and modifies the `MOM_layout` files to match your experiment by inserting the right number of x, y points and the CPU layout. If we use `payu` to run MOM6, then we set the `using_payu` flag to `True`. This way, an example `config.yaml` file is copied to our run directory. This `config.yaml` still needs to be modified manually to add our NCI projets, locations of  executable, etc.
    """)
    return


@app.cell
def _(expt):
    expt.setup_run_directory(surface_forcing = "jra", using_payu = True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 8: Run your model!

    To do this, we navigate to our run directory in terminal. If we are working on NCI, we can run our model via:

    ```
    module load conda/analysis3
    payu setup -f
    payu run -f
    ```

    By default `input.nml` is set to only run for 5 days as a test. If this is successful, then we can modify this file to run for longer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 9 and beyond: Fiddling, troubleshooting, and fine tuning

    Hopefully our model is running. If not, the first thing we should do is reduce the timestep. We can do this by adding `#override DT=XXXX` to your `MOM_override` file.

    If there's strange behaviour on our boundaries, we can play around with the `nudging timescale` (an example is already included in the `MOM_override` file). Sometimes, if a boundary has a lot going on (like all of the eddies spinning off the western boundary currents or off the Antarctic Circumpolar current), it can be hard to avoid these edge effects. This is because the chaotic, submesoscale structures developed within the regional domain won't match those at the boundary.

    Another thing that can go wrong is little bays creating non-advective cells at your boundaries. Keep an eye out for tiny bays where one side is taken up by a boundary segment. We can either fill them in manually, or move your boundary slightly to avoid them.
    """)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
