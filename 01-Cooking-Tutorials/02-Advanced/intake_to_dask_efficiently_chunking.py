import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import subprocess

    return (subprocess,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Speeding up loading a dataset with the intake

    This Tutorial covers speeding up dataset loading with the intake catalog. It covers:
    1. Chunking.
    2. Combining coordinates
    3. Dask Graphs

    Slides with an abridged version of the information in this tutorial can be found over at a [post in the ACCESS-Hive forum](https://forum.access-hive.org.au/t/7th-march-2025-introduction-to-cosima-cookbook-cosima-recipes-how-to-make-it-go-loading-data-fast/4263/1).

    **Note 1**: Needs a large (or larger) ARE instance. If run using a smaller ARE instance, some things may not work due to lack of computational resources.

    **Note 2**: Changing ARE instance size will also affect timings - although changes in speedup/timings should be proportionate to the resources used.

    **Note 3**: Depending on the version of the catalog you are using, you may get different warnings. These warning should not affect execution, but may fill up your output, and make the notebook look quite different when you execute it.

    ___

    Because we'll be dealing with chunking, we'll also be using the `validate_chunkspec` tool from `access_intake_utils` - this will let us quickly and easily check that our chunks shouldn't degrade performance.
    """)
    return


@app.cell
def _():
    import intake # For the catalog
    import dask
    from dask.distributed import Client # Dask client config
    import datetime # We'll use this to time some slow operations
    from access_intake_utils.chunking import validate_chunkspec
    catalog = intake.cat.access_nri
    catalog
    return Client, catalog, dask, datetime, validate_chunkspec


@app.cell
def _(Client):
    client = Client(threads_per_worker = 1)
    client
    # Open up the dashboard by clicking the launch button below - it'll help you to see what dask is doing when it runs expensive operations. 
    # Knowing that Dask is doing something - even if it's slow - can sometimes be worth more than speeding an operation up. 
    # You're less likely to cancel it if you don't think it's broken!
    return


@app.cell
def _(catalog):
    datastore = catalog['01deg_jra55v13_ryf9091'].search(frequency='1mon',variable='u')
    datastore
    return (datastore,)


@app.cell
def _(datastore):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit -n 3 -r 3
    # This should take a couple of minutes to run on a large ARE instance - but be careful, without the -n and -r flags, it can 
    # blow out extremely quickly, as %%timeit calls code repeatedly to get an estimate of the runtime.
    datastore.to_dask(xarray_open_kwargs = {'decode_timedelta' : False}) # We need to set `xarray_open_kwargs = {'decode_timedelta' : False}` to avoid
    # a bunch of annoying warnings. When the next version of intake-esm is released, it won't be necessary any more as the default will change.
    return


@app.cell
def _(datastore):
    ds = datastore.to_dask(xarray_open_kwargs = {'decode_timedelta' : False}) 

    ds['u']
    return (ds,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ___
    # Part 1: Chunking

    ## This is a pretty big dataset, but it would be nice if we could open it in less than 17-18 seconds. Lets see if we can do better.

    - Step 1: Inspecting chunking.

    __Chunking__

    Chunking is core to how Dask, and by extension Xarray work. If we choose good chunks, we can often reduce the amount of work needed to do load an array.

    Further Reading:
    - [Xarray Documentation](https://docs.xarray.dev/en/stable/user-guide/dask.html#dask-chunks)
    - [Choosing good chunk sizes in Dask](https://blog.dask.org/2021/11/02/choosing-dask-chunk-sizes?utm_source=xarray-docs)
    """)
    return


@app.cell
def _(ds):
    ds['u']
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ___
    ### We can see from the output above that we have _lots_ (2459160) chunks, each of which are _very_ small (3.20 MiB).
    ### What this means is that when we do our computations, dask is almost certainly going to be spending lots of time concatenating very small chunks together, for no good reason.
    **As a rule of thumb, chunks of ~300MiB are a good starting place. So what happens if we tell dask to make each file into a single chunk?**

    - Since our xarray dataarray is 7.32TiB in total, and we have ~32GiB available, there is no way we can load the datasets without chunks.
    - However, our dataarray is probably stored over a number of files. As a first pass, lets check how our dataset is structured on disk, and then try to load each file into a single chunk.
    - We can see above we have 2760 timestamps. If we look at our dataset again, we see that it has 920 files - so one file for every 3 timestamps. This probably means we have 4 files per year of model output.

    ___

    ### How can we tell dask to load a single chunk per file?

    [`xr.open_dataset`](https://docs.xarray.dev/en/stable/generated/xarray.open_dataset.html) has a `chunks` argument, which lets us tell dask what chunking scheme to use for loading files.
    `intake-esm` lets us access this with `xaray_open_kwargs`

    - In this instance, we want to specify chunks *on a dimension by dimension basis* - so we'll need the dimension names.
    """)
    return


@app.cell
def _(ds):
    ds['u'].dims
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As an easy benchmark, lets time how long it takes us to get a single mean value over all spatial dimensions, selecting the first time time step (this is just to make things manageable - if you're really patient, you could do the full dataset). This will force xarray to do a lot with our chunks - so we'll get a good understanding of how they affect things. If we just open the dataset, they're less important (although we will still see some effects).
    """)
    return


@app.cell
def _(datastore):
    ds_1 = datastore.to_dask(xarray_open_kwargs={'decode_timedelta': False})
    ds_1.isel(time=0).mean().compute()
    return


@app.cell
def _(datastore):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit -n 3 -r 3
    # This should take a couple of minutes to run on a large ARE instance - but be careful, without the -n and -r flags, it can 
    # blow out extremely quickly, as %%timeit calls code repeatedly to get an estimate of the runtime.
    datastore.to_dask(xarray_open_kwargs = {'decode_timedelta' : False}).isel(time=0).mean().compute()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - We know we want one chunk per time slice, and we have 920 files and 2760 time steps, so we must have 3 time steps per file. So we'll specify chunks of 3 for time. Why do we do this?
    -  If we specify more chunks than each file contains, we will just get chunks the size of each file. So we could specify 3, 4, or 1000 for our time chunks, and we'll still get 3.

    How do we know how to set the chunk size for all the other dimensions, if we want one chunk per file?

    It turns out it's not necessary - we can use `-1` to represent 'the entire dimension'. So our chunking dict will look like this:
    """)
    return


@app.cell
def _(datastore):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit -n 3 -r 3
    chunks_dict = {
        'time' : 3,
        'st_ocean' : -1,
        'yu_ocean' : -1,
        'xu_ocean' : -1,
    }

    datastore.to_dask(xarray_open_kwargs={'chunks' : chunks_dict, 'decode_timedelta' : False})
    # This is how long it takes just to open the dataset
    return


@app.cell
def _(datastore):
    chunks_dict_1 = {'time': 3, 'st_ocean': -1, 'yu_ocean': -1, 'xu_ocean': -1}
    ds_chunked = datastore.to_dask(xarray_open_kwargs={'chunks': chunks_dict_1, 'decode_timedelta': False})
    ds_chunked['u']
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    What we did above - with `chunks_dict = {'time' : 3, 'st_ocean' : -1, 'yu_ocean' : -1,'xu_ocean' : -1}` - sped up opening the dataset a bit, from ~18 to ~14 seconds. However, the chunks are so big now that if we tried to calculate the mean, we would crash a large ARE instance - our workers only have about 4GB of memory each, and our chunks are bigger than that. So we need smaller chunks. Lets split up on `xu_ocean` too.
    """)
    return


@app.cell
def _(datastore):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit 
    # Just opening the dataset
    chunks_dict_2 = {'time': 3, 'st_ocean': -1, 'yu_ocean': -1, 'xu_ocean': 120}
    datastore.to_dask(xarray_open_kwargs={'chunks': chunks_dict_2, 'decode_timedelta': False})
    return


@app.cell
def _(datastore):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit 
    # Opening the dataset & computing the mean
    chunks_dict_3 = {'time': 3, 'st_ocean': -1, 'yu_ocean': -1, 'xu_ocean': 120}
    datastore.to_dask(xarray_open_kwargs={'chunks': chunks_dict_3, 'decode_timedelta': False}).isel(time=0).mean().compute()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Two things to note:
    1. We've improved our performance (opening the dataset) by about a third from the default! Not bad.
    2. When we compute the mean, our performance has slipped significantly - from 29s to 48s - despite following the ~300MiB chunks rule. This isn't good!
    3. We've also got a warning that our chunks could degrade performance! What's gone wrong?
    # Disk Chunks - A huge (and badly documented) stumbling block

    `xarray` lets us specify chunks when we load a dataset. However, there is another kind of chunk we need to contend with: __disk chunks__.

    - netCDF files are actually chunked on disk - and if we don't pick chunks that respect those, it can massively slow things down.
    - What does 'picking chunks that respect disk chunks' mean? *We need to pick our chunks to be integer multiples of the disk chunks*. If we don't, then we have to open each disk chunk multiple times in order to load the dataset. This can really degrade performance - as shown above - and it's why xarray gave us that warning.

    Unfortunately, xarray doesn't make easy to validate that we chose to open our dataset with respect the disk chunking (without trying & waiting for warnings), so we've built a tool to help.

    __NOTE__: `access_intake_utils` is only available in the `conda/analysis3-25.05` or later environments.

    __Credit__: `access_intake_utils` was forked from [ACDtools](https://github.com/Thomas-Moore-Creative/ACDtools) & builds on the tooling there.
    """)
    return


@app.cell
def _(mo, validate_chunkspec):
    # In marimo, mo.doc($FUNCTION_NAME) will show you it's signature & documentation
    mo.doc(validate_chunkspec)
    return


@app.cell
def _(datastore, validate_chunkspec):
    validate_chunkspec(
        datastore,
        chunkspec={
            'time' : 3,
            'st_ocean' : -1,
            'yu_ocean' : -1,
            'xu_ocean' : 120,
        },
        varnames = 'u'
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    What does this mean?

    - In the above example, we specified chunks over `xu_ocean` of 120 elements, and the whole dimension in the other spatial dimensions. For time, we opened all 3 timesteps in each file as a single chunk.
    - This *vastly* reduced the number of chunks - and this is what improved our performance *opening the file*, as we had less communication overhead, and a smaller dask graph to build.
    - However, `validate_chunkspec` has shown that we actually didn't read the files in an optimal fashion, as we had to open and read each `xu_ocean` chunk multiple times in order to load the data.
    - This is what caused the performance degradation when we tried to compute the mean - we had to open each disk chunk multiple times.

    __Takeaway__: Even though we didn't read the chunks in the file optimally, by picking a sensible number of chunks, we've opened the file about a third faster. However, this has come at the (much larger) expense of slowing down subsequent computations a lot.

    So what happens if we read the file chunks optimally, too? Luckily, validate chunkspec has returned an optimised chunk specification dictionary - so let's use that.
    """)
    return


@app.cell
def _(datastore, validate_chunkspec):
    optimised_chunks = validate_chunkspec(
        datastore,
        chunkspec={
            'time' : 3,
            'st_ocean' : -1,
            'yu_ocean' : -1,
            'xu_ocean' : 120,
        },
        varnames = 'u'
    )
    return (optimised_chunks,)


@app.cell
def _(datastore, optimised_chunks):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit -n 3 -r 3
    datastore.to_dask(xarray_open_kwargs={'chunks' : optimised_chunks, 'decode_timedelta' : False})
    # Just opening the dataset, it's similar to before.
    return


@app.cell
def _(datastore, optimised_chunks):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit -n 3 -r 3
    # Opening the dataset & computing the mean
    datastore.to_dask(xarray_open_kwargs={'chunks' : optimised_chunks, 'decode_timedelta' : False}).isel(time=0).mean().compute()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## So even with optimised chunks that are about the right size, we still didn't really improve things a great deal.

    **Sometimes, getting the chunks right can be more of an art than a science.**

    - We tried to follow the 300MiB chunk rule of thumb above, and slowed down loading our dataset by 50% - so the warnings about degrading performance were right. This is because the chunks we chose weren't integer multiples of the disk chunks. However, without `validate_chunkspec`, we would have had no (easy) way of knowing this!
    - If we wanted to throw away a large fraction of a dimension - for example, if we were only interested in data in the Southern Ocean, we could instead have tried to split our chunks up on latitude. That way, when we select a subset of data, we can throw away a lot of chunks - without having to extract a subset of their data first.

    - You can also try `'chunks' : 'auto'` to let xarray decide - there's also a chance this will speed things up. It should respect the disk chunking - but occasionally doesn't
    """)
    return


@app.cell
def _(datastore):
    datastore.to_dask(xarray_open_kwargs={'chunks' : 'auto', 'decode_timedelta' : False})['u']
    return


@app.cell
def _(datastore):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit -n 3 -r 3
    mean_chunks = datastore.to_dask(xarray_open_kwargs={'chunks' : 'auto', 'decode_timedelta' : False}).isel(time=0).mean().compute()
    return


@app.cell
def _(datastore):
    # Note the chunks that 'auto' gives us - what hapens if we manually specify those?
    ds_2 = datastore.to_dask(xarray_open_kwargs={'chunks': {'time': 2, 'st_ocean': 14, 'yu_ocean': 600, 'xu_ocean': 800}, 'decode_timedelta': False})
    return (ds_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    When we look at the two cells above & the cell below, we see that we have the exact same chunks, and the exact same dask graph as we would if we specified `'chunks' : 'auto'`.
    However, we now have a bucketload of warnings. This is because the chunks dask chose are not integer multiples of the disk chunks over time. In this instance, it doesn't matter - we're only selecting the first time anyway - but it's worth being aware of. `'chunks' : 'auto'` *should* choose integer multiples of the disk chunks, but it didn't quite work here. We'll explore why after the exercises below.
    """)
    return


@app.cell
def _(ds_2):
    ds_2['u']
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Can you improve on what we've done here? Things to try:
    1. Select the data we want to open at the datastore stage, not after opening the dataset.
    2. Play around with chunking. What's the best you can do? For more info on chunking, see [here](https://docs.xarray.dev/en/stable/generated/xarray.open_dataset.html#xarray-open-dataset) and [here](https://docs.dask.org/en/latest/array-chunks.html). If you can beat 24 seconds, open a pull request and let us know!
    3. What about rechunking after you load the dataset? See [here](https://docs.xarray.dev/en/stable/generated/xarray.Dataset.chunk.html)
    """)
    return


@app.cell
def _(datastore):
    # Exercise 1.
    # magic command not supported in marimo; please file an issue to add support
    # %timeit 
    datastore.search(...).to_dask(xarray_open_kwargs={'chunks' : 'auto', 'decode_timedelta' : False}).isel(time=0).mean(dim=['st_ocean','yu_ocean','xu_ocean']).compute()
    return


@app.cell
def _(datastore):
    # Exercise 2.
    # magic command not supported in marimo; please file an issue to add support
    # %timeit
    datastore.to_dask(xarray_open_kwargs={'chunks' : ..., 'decode_timedelta' : False}).isel(time=0).mean(dim=['st_ocean','yu_ocean','xu_ocean']).compute()
    return


@app.cell
def _(datastore):
    # Exercise 3.
    # magic command not supported in marimo; please file an issue to add support
    # %timeit 
    ds_3 = datastore.to_dask(xarray_open_kwargs={'decode_timedelta': False, 'chunks': ...})
    ds_3.chunk(...).isel(time=0).mean(dim=['st_ocean', 'yu_ocean', 'xu_ocean']).compute()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Some extra notes on disk chunks & using `validate_chunkspec` to avoid slowing things down
    """)
    return


@app.cell
def _(datastore, validate_chunkspec):
    # Let's try validating our the chunks provided by `'chunks' : 'auto'` from earlier - are they optimal?

    validate_chunkspec(datastore, chunkspec={
            'time' : 2,
            'st_ocean' : 14,
            'yu_ocean' : 600,
            'xu_ocean' : 800,
        },
        varnames = 'u'
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Xarray's automatically determined chunks should be optimal in the sense that they don't read disk chunks multiple times.

    This can also be validated with ncdump, if we use the -hs flags. So why did we get those warnings?
    """)
    return


@app.cell
def _(datastore):
    fname = datastore.df.path.head(1).tolist()[0]
    print(f"{fname=}")
    return


@app.cell
def _(subprocess):
    #! ncdump -hs /g/data/ik11/outputs/access-om2-01/01deg_jra55v13_ryf9091/output1000/ocean/ocean.nc
    subprocess.call(['ncdump', '-hs', '/g/data/ik11/outputs/access-om2-01/01deg_jra55v13_ryf9091/output1000/ocean/ocean.nc'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - So `u` has disk chunks `{'time' : 1, 'st_ocean' : 7, 'yu_ocean' : 300,'xu_ocean' : 400}`
    - Note that different variables have different chunking - if we don't specify the variable we want to know the chunking of in `validate_chunkspec`, we might get a wrong answer!
    - When we ask for just 'u' above, we also load all `xu_ocean`, `yu_ocean`, `st_ocean` and `time` - let's add those variables in and see if our chunking is optimal for those too (spoiler - it isn't).

    This is why the chunk specification dictionary that we got from `'chunks' : 'auto'` caused all those warnings - because different variables in a dataset can be chunked differently!
    """)
    return


@app.cell
def _(datastore, validate_chunkspec):
    validate_chunkspec(datastore, chunkspec={
            'time' : 2,
            'st_ocean' : 14,
            'yu_ocean' : 600,
            'xu_ocean' : 800,
        },
        varnames = ['u', 'xu_ocean', 'yu_ocean', 'st_ocean', 'time']
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### It turns out our coordinates aren't chunked at all (these are the sizes of the netcdf files).
    - Since coordinates are often just 1D arrays, it doesn't make sense to chunk them a lot of the time.
    - This example here mostly serves to show how `validate_chunkspec` will suggest (hopefully) better chunks if the chunks you pick aren't optimal.
    - Note that the chunking dictionary returned by `validate_chunkspec` is *as close as possible* to the original chunking specification, whilst being an integer multiple of the disk chunks of the variables we're validating. It just happens that in this instance, that's the full file size.
    """)
    return


@app.cell
def _(datastore, validate_chunkspec):
    validate_chunkspec(datastore, chunkspec={
            'time' : 2,
            'st_ocean' : 15, # We've now changed our 'st_ocean' chunk to 15: which isn't an integer multiple of the disk chunks
            'yu_ocean' : 600,
            'xu_ocean' : 800,
        },
        varnames = ['u']
    )
    # In this instance, validate chunkspec tells us to change our chunk in 'st_ocean' from 15 to 14 to speed things up. This takes us back to what 'auto' gave us!
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What about a dataset where chunking isn't really the problem?
    """)
    return


@app.cell
def _(catalog):
    datastore_1 = catalog['025deg_era5_ryf'].search(frequency='1mon', file_id='iceh_XXXX_XX', variable='aicen_m')
    datastore_1
    return (datastore_1,)


@app.cell
def _(datastore_1, datetime):
    # Please don't run this - it can be super slow!
    # I've used the datetime module rather than %time or %%timeit as they take even longer!
    # However, profiling like this can be very inaccurate: see eg. https://github.com/Kai-Striega/EuroSciPy-2023-Speech/blob/main/EuroSciPy_Speech.pdf
    # for a detailed discussion on profiling.
    t0 = datetime.datetime.utcnow()
    ds_4 = datastore_1.to_dask()
    t1 = datetime.datetime.utcnow()
    dt = t1 - t0
    print(f'took ~= {dt.seconds // 60} minutes, {dt.seconds % 60} seconds to load')
    ds_4
    return


@app.cell
def _(datastore_1, datetime):
    # Like we did above, lets try to set one chunk per file to speed things up.
    t0_1 = datetime.datetime.utcnow()
    ds_5 = datastore_1.to_dask(xarray_open_kwargs={'chunks': {'time': 408, 'nc': -1, 'ni': 1440, 'nj': 1080}})
    t1_1 = datetime.datetime.utcnow()
    dt_1 = t1_1 - t0_1
    print(f'took ~= {dt_1.seconds // 60} minutes, {dt_1.seconds % 60} seconds to load')
    ds_5
    return (ds_5,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ___
    # Part 2: Combining coordinates

    **Unfortunately, that didn't seem to help much - it might have even made things a bit slower.**
    - So what is the issue?

    It turns our that xarray is checking that all our coordinates are consistent. Doing that with the 2D arrays `(ni,nj)` can be really quite slow. Fortunately, we have options to turn these checks off too, if we are confident we don't need them. In this instance, they come from a consistent model grid, so we know we can get rid of them.

    **We don't use** `xarray_open_kwargs` **for this: we use** `xarray_combine_by_kwargs`

    Lets see if we can beat four minutes...
    ___
    Step 1: Lets concatenate together the minimal set of variables
    """)
    return


@app.cell
def _(datastore_1, datetime, ds_5):
    t0_2 = datetime.datetime.utcnow()
    datastore_1.to_dask(xarray_combine_by_coords_kwargs={'data_vars': 'minimal', 'coords': 'minimal'})
    t1_2 = datetime.datetime.utcnow()
    dt_2 = t1_2 - t0_2
    print(f'took ~= {dt_2.seconds // 60} minutes, {dt_2.seconds % 60} seconds to load')
    ds_5
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **So this actually slowed things down pretty substantially - that's not ideal!**

    Step 2: Let's set the `compat` flag to `override`. This skips a bunch of checks that slow things down a bunch.
    Note however: if we don't set `'datavars' : 'minimal'` and `'coords' : 'minimal'`, this can throw an error.
    """)
    return


@app.cell
def _(datastore_1, datetime, ds_5):
    t0_3 = datetime.datetime.utcnow()
    datastore_1.to_dask(xarray_combine_by_coords_kwargs={'compat': 'override', 'data_vars': 'minimal', 'coords': 'minimal'})
    t1_3 = datetime.datetime.utcnow()
    dt_3 = t1_3 - t0_3
    print(f'took ~= {dt_3.seconds // 60} minutes, {dt_3.seconds % 60} seconds to load')
    ds_5
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## That made a huge difference - we've gone down from 4 minutes to 12 seconds. Can we do better by setting the chunking too now?
    """)
    return


@app.cell
def _(datastore_1):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit
    # Finally, lets combine it all, and see how fast we can get!
    chunks_dict_4 = {'time': 408, 'nc': -1, 'nj': -1, 'ni': -1}
    datastore_1.to_dask(xarray_open_kwargs={'chunks': chunks_dict_4}, xarray_combine_by_coords_kwargs={'compat': 'override', 'data_vars': 'minimal', 'coords': 'minimal'})
    return


@app.cell
def _(datastore_1):
    chunks_dict_5 = {'time': 408, 'nc': -1, 'nj': -1, 'ni': -1}
    ds_6 = datastore_1.to_dask(xarray_open_kwargs={'chunks': chunks_dict_5}, xarray_combine_by_coords_kwargs={'compat': 'override', 'data_vars': 'minimal', 'coords': 'minimal'})
    ds_6['aicen_m']
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### So, for this dataset, we can go from 4 minutes to ten seconds with some thought - or 4 minutes to 12 seconds using the `xarray_combine_by_coords_kwargs`.

    TLDR;
    - If your dataset is taking a long time to load, start by adding `xarray_combine_by_coords_kwargs={ 'compat' : 'override', 'data_vars': 'minimal', 'coords': 'minimal'}` to your `datastore.to_dask()` call.
    - Chunking may be able to improve things further - but it might also make it worse. It is more likely to be a source of issues once you start working with, rather than just loading, the data.
    - Subsetting to the minimal dataset you want to open, *before* you open it in xarray with `.to_dask()`, will make a massive difference to load times.
    - By using `xarray_combine_by_coords_kwargs` and `xarray_open_kwargs`, you can achieve a lot of control over how xarray opens your dataset - see [combine by coords](https://docs.xarray.dev/en/stable/generated/xarray.combine_by_coords.html#xarray.combine_by_coords) and [open dataset](https://docs.xarray.dev/en/stable/generated/xarray.open_dataset.html#xarray-open-dataset) for all the options.
    ___

    ## Exercises

    Lets go back to our original dataset, and try to efficiently load some data.

    1. Lets try loading the daily data for the first year: first by selecting only the data for the first year, and secondly by opening all the data as efficiently as possible. Which works better?
    2. Lets plot the average of top grid cell temperature over the whole dataset. Now, can we make it faster using chunks?
    """)
    return


@app.cell
def _(catalog):
    catalog
    return


@app.cell
def _(catalog):
    datastore_2 = catalog['01deg_jra55v13_ryf9091'].search(frequency='1day', variable='u')
    return (datastore_2,)


@app.cell
def _(datastore_2, datetime):
    t0_4 = datetime.datetime.utcnow()
    datastore_2.search(...).to_dask()
    t1_4 = datetime.datetime.utcnow()  ### Make changes here
    dt_4 = t1_4 - t0_4
    print(f'took ~= {dt_4.seconds // 60} minutes, {dt_4.seconds % 60} seconds to load')
    return


@app.cell
def _(datastore_2, datetime):
    t0_5 = datetime.datetime.utcnow()
    datastore_2.to_dask(...)
    t1_5 = datetime.datetime.utcnow()  ### Make changes here
    dt_5 = t1_5 - t0_5
    print(f'took ~= {dt_5.seconds // 60} minutes, {dt_5.seconds % 60} seconds to load')
    return


@app.cell
def _(catalog):
    datastore_3 = catalog['01deg_jra55v13_ryf9091'].search(variable='temp', frequency='1mon')
    datastore_3
    # Now let's use chunking and combining cordinates to try to speed up our plot
    # datastore.to_dask(xarray_open_kwargs={'decode_timedelta' : False, 'chunks' :  ...}, xarray_combine_by_kwargs = { ...} ).mean(dim='time').isel(
    # ^ This will take forever, but by being clever about how we load the data and using the tricks above, we can make it quite a bit faster.
    datastore_3.to_dask(xarray_open_kwargs={'decode_timedelta': False})['temp'].mean(dim='time').isel(st_ocean=0).plot()
    return (datastore_3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ___
    # Part 3: Dask Graphs
    ## Dask Task Graphs

    - The `dask_graph` that an xarray dataset contains tells us some information about how data in the dataset is realised - and it can sometimes give us useful information.
    - The warning above tells us that we've sent Dask a large task graph. What exactly does this mean?

    __Note__: You probably won't want to probe into what this section explores too much - but it can be helpful if you're struggling to work out why a computation is slow
    """)
    return


@app.cell
def _(datastore_3):
    twelve_chunks = datastore_3.search(start_date='1950-01-01, 00:00:00', variable='temp').to_dask(xarray_open_kwargs={'chunks': {'time': 3, 'st_ocean': 75, 'xt_ocean': 900, 'yt_ocean': 900}, 'decode_timedelta': False})
    twelve_chunks
    return (twelve_chunks,)


@app.cell
def _(dask, twelve_chunks):
    dask.visualize(twelve_chunks)
    return


@app.cell
def _(datastore_3):
    three_chunks = datastore_3.search(start_date='1950-01-01, 00:00:00', variable='temp').to_dask(xarray_open_kwargs={'chunks': {'time': 3, 'st_ocean': 75, 'xt_ocean': 3600, 'yt_ocean': 900}, 'decode_timedelta': False})
    three_chunks
    return (three_chunks,)


@app.cell
def _(dask, three_chunks):
    dask.visualize(three_chunks)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Okay: So what does this actually show?

    When we have 12 chunks, Dask opens our dataset, and then splits it out into 12 subsets of the data. Similarly, when we have three, it splits it out into 3 subsets.

    This might seem obvious, but what happens now when we want to combine things back together? Let's look at the mean over the whole dataset
    """)
    return


@app.cell
def _(dask, twelve_chunks):
    dask.visualize(twelve_chunks.max())
    return


@app.cell
def _(dask, three_chunks):
    dask.visualize(three_chunks.max())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can see that as we add more chunks, the task graph gets bigger (__very quickly__). This can be a potential source of issues - if you've chunked badly, then dask has to do a lot of operations to put the dataset back together. For example, if you pick miniscule chunks, a large part of the computation time will be dask stitching the chunks back together. Let's demonstrate that:
    """)
    return


@app.cell
def _(twelve_chunks):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit
    twelve_chunks.max()
    return


@app.cell
def _(datastore_3):
    badly_chunked = datastore_3.search(start_date='1950-01-01, 00:00:00', variable='temp').to_dask(xarray_open_kwargs={'chunks': {'time': 1, 'st_ocean': 25, 'xt_ocean': 10, 'yt_ocean': 25}, 'decode_timedelta': False})
    # This is a real mess - we've made our chunks far too small.
    badly_chunked
    return (badly_chunked,)


@app.cell
def _(badly_chunked):
    # magic command not supported in marimo; please file an issue to add support
    # %%timeit
    badly_chunked.max()
    return


@app.cell
def _(dask, datastore_3):
    # So we've managed to slow things down ~200 times, just by picking bad chunks. Why? Lets look at a dask graph for a slightly 
    # less complicated graph
    less_badly_chunked = datastore_3.search(start_date='1950-01-01, 00:00:00', variable='temp').to_dask(xarray_open_kwargs={'chunks': {'time': 1, 'st_ocean': 75, 'xt_ocean': 200, 'yt_ocean': 200}, 'decode_timedelta': False})
    dask.visualize(less_badly_chunked)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This graph is so big we can't even see it - it's the smudgy line above.

    ___

    ## A side note: rechunking after loading

    The warnings above suggest rechunking after loading.
    Now we know about task graphs, lets see what rechunking after loading *actually does*. We'll take our 12 chunk computation, and turn it into one big chunk.
    """)
    return


@app.cell
def _(dask, twelve_chunks):
    dask.visualize(twelve_chunks)
    return


@app.cell
def _(twelve_chunks):
    twelve_chunks.chunk(chunks={
                'time' : -1,
                'st_ocean' : -1,
                'xt_ocean' : -1,
                'yt_ocean' : -1,
            })
    return


@app.cell
def _(dask, twelve_chunks):
    dask.visualize(twelve_chunks.chunk(chunks={
                'time' : -1,
                'st_ocean' : -1,
                'xt_ocean' : -1,
                'yt_ocean' : -1,
            }))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We didn't actually make our computation any simpler - we just added another, explicit layer, where we merge our chunks back together.

    ___

    ### So setting bad chunks can make a big task graph - and this can make things slow.

    - So does a big task graph mean your computation is badly organised?

    Well - yes and no.

    - We need the task graph, because it splits jobs up into manageable chunks of memory.
    - The limit of making the task graph smaller is not using Dask - and then we know for sure we'll run out of memory.
    - So we want to make the task grapher smaller, but not so small that we run out of memory.

    If you can make the task graph smaller without running out of memory, then your computation is likely to go faster. With that said - some computations *are just complicated, or can't be worked out in small chunks* - and that means we can't avoid a big task graph.
    The computation below is a simple example of this
    """)
    return


@app.cell
def _(twelve_chunks):
    # I don't know why anyone would ever do this operation - but it very quickly blows 
    # up our task graph for 3 to 32 layers.
    twelve_chunks.rolling(yt_ocean=10, xt_ocean=10).mean()
    return


@app.cell
def _(dask, twelve_chunks):
    # This makes such a large graph that visualizing only produces the smudge below - and it takes 20 minutes!
    dask.visualize(twelve_chunks.rolling(yt_ocean=10, xt_ocean=10).mean())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Trying to speed up your computation using the dask task graph is probably the most powerful tool you have available, in theory - it contains *all* the information. However, in practice, it's generally too much information to really do much with.
    """)
    return


if __name__ == "__main__":
    app.run()
