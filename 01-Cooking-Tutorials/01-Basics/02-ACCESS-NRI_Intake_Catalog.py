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
    # ACCESS-NRI Intake catalog for loading model output
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This tutorial demonstrates how to use the ACCESS-NRI Intake catalog to load model or other output.

    ⚠️ **Membership to project `xp65` is required to access the ACCESS-NRI Intake catalog** ⚠️

    This is a concise version of the longer [ACCESS-NRI Intake catalog documentation](https://access-nri-intake-catalog.readthedocs.io/) and related [COSIMA training workshop](https://github.com/ACCESS-Hive/cosima-training-workshop-2023/blob/main/Intake.ipynb). Users are encouraged to refer to these for more detail and demonstrations.

    Requirements: The `conda/analysis3` module from `/g/data/xp65/public/modules`.
    ___
    ### There is also an interactive, web based view into the intake catalog, which will let you click through the catalog and generate the code for you.

    https://access-nri.github.io/interactive-data-catalogue/
    __For beginners, or troubleshooting, or just finding a dataset you aren't familiar with, this is a great place to start!__ It will:
    - Show you all the catalog entries, their metadata, and the experiments they encode
    - Generate quickstart code you can copy and paste into an ARE session in order to load data
    - Allow you to share searches via URLs
    - Disambiguate between dataset dictionaries and a single dataset (more on that later!) for you.

    __The Interactive Data Catalogue was built as a tool to address, avoid, or make trivial many of the common difficulties and questions that this notebook tries to train people in using.__
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Start a dask Client

    This is not specific to using the ACCESS-NRI Intake catalog, but it's useful!
    """)
    return


@app.cell
def _():
    from dask.distributed import Client

    client = Client(threads_per_worker=1)
    client
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Opening and searching the catalog
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To use the ACCESS-NRI Intake catalog, we need to import `intake`
    """)
    return


@app.cell
def _():
    import intake

    return (intake,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can open the catalog as follows
    """)
    return


@app.cell
def _(intake):
    catalog = intake.cat.access_nri
    return (catalog,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The returned object `catalog` is an instance of the ACCESS-NRI Intake catalog that we can use to find and load data.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Printing the `catalog` object will return a dataframe of experiments that you can browse:
    """)
    return


@app.cell
def _(catalog):
    catalog
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You can also search based on the columns in this dataframe to find experiments that are relevant to you. For example, you might be interested in all ACCESS-OM2 experiments that have the variable `"surface_salt"` at daily frequency. There are 6 such experiments currently available through the catalog:
    """)
    return


@app.cell
def _(catalog):
    catalog.search(model="ACCESS-OM2", variable="surface_salt", frequency="1day")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Opening data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There are [multiple ways](https://access-nri-intake-catalog.readthedocs.io/en/latest/usage/quickstart.html#loading-intake-sources) to open data from the experiments in `catalog`. Here we'll demonstrate how to do this when you know the name of the experiment you are interested in, since this typical for COSIMA users.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For example, we can open monthly data for the `surface_salt` variable in the `01deg_jra55v13_ryf9091` experiment as follows:
    """)
    return


@app.cell
def _():
    experiment = "01deg_jra55v13_ryf9091"
    variable = "surface_salt"
    return experiment, variable


@app.cell
def _(catalog, experiment, variable):
    data_ic = catalog[experiment].search(
        variable=variable, 
        frequency="1mon"
    ).to_dask()
    return (data_ic,)


@app.cell
def _(data_ic):
    data_ic["surface_salt"]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Some important facts

    There are a few important facts in the ACCESS-NRI Intake catalog that users should be aware of.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The catalog returns `Datasets` (not `Dataarray`s)

    This is because with the catalog you can load multiple variables into a single dataset with a single call (when these variables are in the same file). For example,
    """)
    return


@app.cell
def _(catalog, experiment):
    data_ic_multivar = catalog[experiment].search(
        variable=["surface_salt", "surface_temp"], 
        frequency="1mon"
    ).to_dask()
    return (data_ic_multivar,)


@app.cell
def _(data_ic_multivar):
    data_ic_multivar
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. The catalog knows which files make up distinct datasets
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The catalog knows which files make up distinct datasets and provides methods to open multiple datasets from a single query. We can run the equivalent to the cell above using the catalog, using `to_dataset_dict()` rather than `to_dask()`. Doing so returns a dictionary containing Datasets of the variable at all the available frequencies (daily and monthly in this case).
    """)
    return


@app.cell
def _(catalog, experiment, variable):
    data_ic_multifreq = catalog[experiment].search(variable=variable).to_dataset_dict()
    return (data_ic_multifreq,)


@app.cell
def _(data_ic_multifreq):
    data_ic_multifreq
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Alternatively, multiple datasets can be opened directly into an [xarray datatree](https://docs.xarray.dev/en/stable/generated/xarray.DataTree.html) by calling `to_datatree` rather than `to_dataset_dict`. For example:
    """)
    return


@app.cell
def _(catalog, experiment, variable):
    data_ic_datatree = catalog[experiment].search(variable=variable).to_datatree()
    return (data_ic_datatree,)


@app.cell
def _(data_ic_datatree):
    data_ic_datatree
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## If you have multiple datasets, you can use the interactive catalog to guide you down to a single dataset:
    https://access-nri.github.io/interactive-data-catalogue/#/datastore/01deg_jra55v13_ryf9091?variable_filter=surface_salt

    - The link above takes us to the same search in the interactive catalog, which tells us our search contains 3 datasets.
    - We can see if we open the frequency selector on this page that __both monthly and daily data are available__.
    - Selecting daily data gives us two datasets, and the quickstart code still tells us to load a dataset dict.
    - Selecting monthly data gives us a single dataset, and the quickstart code changes to load a dataset!
        - So if we want a single dataset, we can either filter for monthly data too (https://access-nri.github.io/interactive-data-catalogue/#/datastore/01deg_jra55v13_ryf9091?variable_filter=surface_salt&frequency_filter=1mon), or
        -  Daily and do some further filtering, eg. (https://access-nri.github.io/interactive-data-catalogue/#/datastore/01deg_jra55v13_ryf9091?variable_filter=surface_salt&frequency_filter=1day&file_id_filter=ocean.1day.nv:2.xt_ocean:3600.yt_ocean:2700)
        - The further filtering reveals we have both 2D (ocean surface) and 3D (full depth) fields for daily data.

    __In general, you will find it quicker to use the interactive catalog to search for what you need - you won't need to learn intake syntax to get what you're after, just click through by hand. Once you've got what you need, you can copy the code and open an ARE session.__
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. The frequency vocabulary:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In the catalog, frequency follows a standard vocabulary that is very similar to CMIP6:

    ```python
    "fx" # fixed
    "subhr" # subhourly
    "<int>hr" # hourly
    "<int>day" # daily
    "<int>mon" # monthly
    "<int>yr" # yearly
    "<int>dec" # decadal
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Method for passing keyword arguments
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    With the catalog, keyword argments for xarray's `open_dataset` and `combine_by_coords` functions are passed separately to `to_dask` (or `to_dataset_dict`). For example:
    """)
    return


@app.cell
def _(catalog, experiment, variable):
    xarray_open_kwargs=dict(
        chunks={"xt_ocean": -1, "yt_ocean": -1}
    )
    xarray_combine_by_coords_kwargs=dict(
        compat="override",
        data_vars="minimal",
        coords="minimal"
    )

    data_ic_kw = catalog[experiment].search(
        variable=variable, 
        frequency="1mon"
    ).to_dask(
        xarray_open_kwargs=xarray_open_kwargs,
        xarray_combine_by_coords_kwargs=xarray_combine_by_coords_kwargs,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Catalog does not allow search by start and end date (straightforwardly)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    It's not straightforwardly possible to query on a time range with the Intake catalog.

    We can always slice the time axis afterwards though. That is, with the catalog you'd just do:
    """)
    return


@app.cell
def _(catalog, experiment, variable):
    data_ic_1 = catalog[experiment].search(variable=variable, frequency='1mon').to_dask()
    start_time = '2000-01-01'
    end_time = '2180-01-01'
    data_ic_times = data_ic_1.sel(time=slice(start_time, end_time))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    which takes a few seconds longer than filtering before opening via regex (see below).

    This difference is acceptable because the opening of datasets is a parallelized task that is done [lazily](https://docs.xarray.dev/en/stable/user-guide/dask.html#parallel-computing-with-dask),  so opening all files and reducing the times using xarray's `sel` methods doesn't add too much overhead. In most cases where the overhead of opening the files seems large, this can be reduced through sensible choices of keyword arguments provided to `open_dataset` and `combine_by_coords` - see the xarray documentation on [Reading multi-file datasets](https://docs.xarray.dev/en/stable/user-guide/io.html#reading-multi-file-datasets) for details.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If you are brave, you can do the same thing via regular expressions (regex). This is a way of telling the computer to match a variety of text outputs, depending on their content and stucture.

    See [the Python regex documentation for more info](https://docs.python.org/3/library/re.html) - or ask an LLM, they're very good at regex.

    For the example above, we could match all start times up to 2180-01-01 and then end times up to that using:
    """)
    return


@app.cell
def _(catalog, experiment, variable):
    data_ic_regex_filtered = catalog[experiment].search(
        variable=variable, 
        frequency="1mon",
        start_date="2[0-1][0-9][0-9].*", # Match anything from 2000-... to 2199-...
        end_date="2...-..-.*",
    ).to_dask()
    data_ic_regex_filtered
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You might notice that this regex expression is very difficult to understand. For all but the simplest (things like `rm ./*` in your terminal to clear out a directory is a simple regex), they can be extremely difficult to read. Unless filtering on dates once you've already opened the dataset is taking an extremely long time, stick with that approach!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Applying a preprocessing function

    You can use `xarray`'s preprocess function to apply a function to each dataset prior to `intake`'s concatenation. In some cases, this can make the loading into memory fast.

    For example:
    """)
    return


@app.cell
def _(catalog):
    def select_region(ds):
        ds = ds.sel(xt_ocean=slice(-230, -180), yt_ocean=slice(-50, -20))
        return ds
    data_ic_2 = catalog['01deg_jra55v13_ryf9091'].search(variable='surface_temp', frequency='1mon').to_dask(preprocess=select_region)
    data_ic_2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Tips, gotchas and workarounds
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Speeding up opening your datasets
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Try passing the following argument to your `to_dask` or `to_dataset_dict` call:

    ```python
    xarray_combine_by_coords_kwargs=dict(
        compat="override",
        data_vars="minimal",
        coords="minimal"
    )
    ```

    See the xarray documentation on [Reading multi-file datasets](https://docs.xarray.dev/en/stable/user-guide/io.html#reading-multi-file-datasets) for more details about these arguments.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Choosing chunksizes

    Correctly choosing chunk sizes when you open datasets will greatly improve the speed of your analysis. Check out the [Chunking tutorial](https://access-nri-intake-catalog.readthedocs.io/en/latest/usage/chunking.html) in the ACCESS-NRI Intake catalog documentation.

    By default, intake will use `chunks='auto'` when it opens an xarray dataset. This typically chooses a good chunking scheme for most purposes, but you may be able to improve it with some manual tuning - in the case of advanced analyses.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Loading time-invariant variables
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Many COSIMA experiments include multiple repeated files containing the same fixed frequency data (e.g. grid information). You can use the option `fx` for the frequency argument, otherwise the catalog fails to concatenate these files since they don't contain a clear dimension to concatenate along.
    """)
    return


@app.cell
def _(catalog, experiment):
    data_ic_fixed = catalog[experiment].search(
        variable='area_t',
        frequency='fx'
    ).to_dask()
    data_ic_fixed
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Determining what can be searched upon in an experiment

    You can see what can be `search`ed on within an experiment with:
    """)
    return


@app.cell
def _(catalog, experiment):
    catalog[experiment].df.columns.tolist()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    It can also be helpful sometimes to look at the `catalog[experiment].df` object itself, which is a dataframe of all of the files in the experiment and their metadata
    """)
    return


@app.cell
def _(catalog, experiment):
    catalog[experiment].df.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Finding all variables in a catalog

    You can get a list of all available variable names from an experiment with:
    """)
    return


@app.cell
def _(catalog, experiment):
    variables = catalog.search(name=experiment).unique().variable
    print(variables)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### We could similarly filter for any of the keys in our catalog - see the intake dataframe catalog below

    (N.B This is the top level catalog we search here - it works exactly the same way)
    """)
    return


@app.cell
def _(catalog, experiment):
    catalog.search(name=experiment)
    return


@app.cell
def _(catalog, experiment):
    catalog.search(name=experiment, realm = 'ocean')
    return


@app.cell
def _(catalog, experiment):
    # Lets pull out all the unique frequencies, just like we did for variable above
    catalog.search(name=experiment, realm='ocean').unique().frequency
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We could also open the experiment (using square brackets) to search for variables, frequencies, etc. - but this opens the datastore: see how the output of the cell below is displayed differently.

    If we open the datastore:
    1. It is slower - opening datastores requires extra work
    2. The items we can search on might change - the datastore below contains no model field, for example.

    The opened datastore can contain extra information, eg. `variable_long_name` below - so sometimes you might want to open it to search the datastore. In general, try to use `catalog.search(name='xyz',...)` before you use `catalog['xyz'].search(...)`, though.
    """)
    return


@app.cell
def _(catalog, experiment):
    catalog[experiment]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For more information about the available variables, you can use the following command function - just copy and paste it in where you need it:
    """)
    return


@app.function
def get_detailed_variable_info(intake_catalog, experiment_name: str, variable: str | None=None) -> 'pd.Dataframe':
    """
    Get detailed information about all the variables available in an experiment contained within the catalog.

    If a specific variable is passed, then the returned dataframe will be filtered to include only information
    about that variable

    Returns a pandas dataframe, reorganised to use the variable as the index.

    Parameters:
    -----------
    intake_catalog: 
        The variable holding the intake catalog. If you have opened the catalog using
        `cat = intake.cat.access_nri`, then `intake_catalog=cat`, etc.
    experiment_name: str
        The name of the experiment you are interested in. Eg. `experiment = "01deg_jra55v13_ryf9091"`
    variable: str | None
        If you want detailed information about just a single variable, then pass it here. For 
        example, if you only want information about potential temperature, pass `variable='pot_temp'`
    """
    from intake_esm.utils import MinimalExploder
    import polars as pl
    expt_ds = intake_catalog[experiment_name]
    _df = MinimalExploder(expt_ds.esmcat.pl_df)()
    _df = _df.unique('variable').sort('variable')
    if variable is not None:
        _df = _df.filter(pl.col('variable') == variable)
    _df = _df.to_pandas().set_index('variable')
    return _df


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To get detailed info about all variables:
    """)
    return


@app.cell
def _(catalog, experiment):
    _df = get_detailed_variable_info(catalog, experiment)
    _df.head(10)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Say we are only interested in zonal wind stress, `tau_x`:
    """)
    return


@app.cell
def _(catalog, experiment):
    _df = get_detailed_variable_info(catalog, experiment, 'Tsfc_m')
    _df.head(10)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If you have any further questions after reading this notebook and the documentation linked from this notebook, please open an issue in the [ACCESS-NRI Intake catalog Github repo](https://github.com/ACCESS-NRI/access-nri-intake-catalog) or open topic on the [ACCESS-Hive forum](https://forum.access-hive.org.au/).
    """)
    return


@app.cell
def _(client):
    client.close()
    return


if __name__ == "__main__":
    app.run()
