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
    # Lagrangian particle tracking with ACCESS-OM2-01
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lagrangian particle tracking is widely used in a range of physical and biological oceanography applications. This [review paper](https://www.sciencedirect.com/science/article/pii/S1463500317301853) on Lagrangian fundamentals covers many of the basics and provides an overview of the different particle tracking software programs available to the oceanography community. In this notebook we'll use [Parcels](https://github.com/OceanParcels/parcels) which has the advantage of a large user community and an active development team. The [Parcels website](https://oceanparcels.org) is well documented and has some great general tutorials to get you started. In this tutorial, we'll focus on how to get a simple particle tracking experiment running with output from the ACCESS-OM2-01 model.

    **Requirements:** `conda/analysis3-25.05` up to `conda/analysis3-25.08`(not later - see the issue in [this Hive post](https://forum.access-hive.org.au/t/issue-using-parcels-in-analysis3/5491)). This notebook was run on an xx-large ARE instance on the normal queue (**NOTE: `normal`, not `normalbw`.** An xx-large instance on normal has 48 cpus & 190gb memory, whereas an xx-large on normalbw has 28 cpus & 126gb memory)

    <div class="alert alert-block alert-warning">
    <b>Warning:</b>

    - Parcels now uses [`Zarr`](https://zarr.dev) for its output. This creates very large numbers of files, which may overwhelm the inode quota for your project. When running particle tracking experiments, you should closely monitor you inode usage and should postprocess the output into either NetCDF format or use zipped `Zarr` storage. You may find [this post on the ACCESS Hive](https://forum.access-hive.org.au/t/zarr-inodes/5496?u=edoddridge) and [this post on Stack Overflow](https://stackoverflow.com/questions/67635491/transform-zarr-directory-storage-to-zip-storage) helpful.

    - You should use `rm` on the command line to delete files when you have finished with them. **Do not use the ARE interface** to delete files - it doesn't actually delete them. Instead, those files are moved to a `.Trash*` folder in the project directory, where they still count towards the quotas for the project.
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Firstly, load in the required modules.
    """)
    return


@app.cell
def _():
    import numpy as np
    import xarray as xr
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from pathlib import Path
    import pandas as pd

    from glob import glob
    from datetime import timedelta
    from cftime import DatetimeNoLeap
    import warnings, dask
    from dask.distributed import Client
    from parcels import FieldSet, ParticleSet, Variable, JITParticle, ScipyParticle, AdvectionRK4, AdvectionRK4_3D

    import intake
    cat = intake.cat.access_nri
    return (
        AdvectionRK4,
        AdvectionRK4_3D,
        Client,
        FieldSet,
        JITParticle,
        ParticleSet,
        Variable,
        cat,
        dask,
        glob,
        mpl,
        np,
        plt,
        timedelta,
        warnings,
        xr,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    It's a good idea to start a cluster with multiple cores for you to work with.
    """)
    return


@app.cell
def _(Client):
    client = Client(threads_per_worker=1)
    client
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the output trajectory for storing the particle tracking data.
    """)
    return


@app.cell
def _(Path):
    import os

    _output_dir = os.path.expandvars("/scratch/$PROJECT/$USER/particle_tracking")

    print(f"WARNING: Output is being saved in this directory: {_output_dir} \nChange to any directory you like [except your home directory].")
    output_directory = Path(_output_dir)
    output_directory.mkdir(exist_ok=True)
    output_directory
    return (output_directory,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Define the velocity fields (and any other model data) we want Parcels to read
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We're now going to run some simple offline Lagrangian particle tracking experiments. This means we need to read in some velocity fields that have been output from an ocean model and feed these to Parcels. Generally speaking, you want to run Lagrangian particle tracking experiments with the highest temporal resolution available. We have several periods of daily output from ACCESS-OM2-01 available on Gadi. These are listed below.

    - 21 years of daily `u`, `v`, `wt` from the **RYF** simulation corresponding to model years 50-71. This is stored in folders `output196-output279` here: `/g/data/ik11/outputs/access-om2-01/01deg_jra55v13_ryf9091/`
    - 15 years of daily `u`, `v`, `wt` from the **RYF** simulation corresponding to model years 186-200. This is stored in folders `output740-output799` here: `/g/data/ik11/outputs/access-om2-01/01deg_jra55v13_ryf9091/`
    - 31 years of daily `u`, `v`, `wt` from cycle 1 of the **IAF** simulation from 1987 to 2018. This is stored in folders `output116 - output243` here: `/g/data/cj50/access-om2/raw-output/access-om2-01/01deg_jra55v140_iaf`

    We'll use the first year of the daily RYF data for this experiment. We'll also start with a simple 2D advection example, and then run a 3D particle advection experiment with temperature and salinity.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2D Advection
    """)
    return


@app.cell
def _():
    experiment = "01deg_jra55v13_ryf9091"
    return (experiment,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Note:** The `from_mom5` method that we use [see cells below for explanation as to why] expects to be fed a list of file paths defining where the model data is stored. For this reason, we do not use intake to load the velocity data in this notebook.
    """)
    return


@app.cell
def _(glob):
    # define the file paths containing the daily U and V velocity data
    data_path = '/g/data/ik11/outputs/access-om2-01/01deg_jra55v13_ryf9091/'
    ufiles = sorted(glob(data_path+'output19*/ocean/ocean_daily_3d_u_*.nc'))
    vfiles = sorted(glob(data_path+'output19*/ocean/ocean_daily_3d_v_*.nc'))
    return ufiles, vfiles


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define a mesh mask which contains the model grid and coordinates that Parcels needs.
    **Note:** this step may take some time... Once you have created the mesh_mask file, you can simply define it's file path in subsequent examples, without needing to recalculate it.
    """)
    return


@app.cell
def _(output_directory, xr):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    orig_mesh_mask = '/g/data/ik11/outputs/access-om2-01/01deg_jra55v13_ryf9091/output196/ocean/ocean.nc'
    mesh_mask = str(output_directory) + '/ocean.nc'
    variables = ['v', 'wt']
    lat_slice = slice(None, -32.58) 
    ds_mesh_mask = xr.open_dataset(orig_mesh_mask, decode_timedelta=True).get(variables).sel(yu_ocean=lat_slice, yt_ocean=lat_slice) 
    ds_mesh_mask.to_netcdf(mesh_mask)
    return (mesh_mask,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we'll define a set of dictionaries that tells Parcels where the velocity data is stored, the variable names, where to access the grid information, the dimensions of the data and the chunksizes.

    **Note 1:** We need use the `from_mom5` method when running particle tracking with ACCESS-OM2-01 for several reasons:
    - MOM5 is defined on an Arakawa B-grid, but with vertical velocities at the bottom faces of the cells, not the top. This distinguishes it from some other B-grid models.
    - At the time the `from_mom5` method was developed, Parcels expected depth to be positive upwards, but in ACCESS-OM2, depth is positive downwards. The `from_mom5` method corrects this.

    **Note 2:** Technically, in 2D dimensional particle tracking when the vertical velocity is ignored, the ACCESS-OM2-01 B-grid collapses to the equivalent of an Arakawa A-grid, but for 3D particle tracking the `from_mom5` method is required when using ACCESS-OM2 outputs. For consistency, we'll use it for both 2D and 3D particle tracking examples in this notebook.
    """)
    return


@app.cell
def _(FieldSet, mesh_mask, ufiles, vfiles):
    # Define a dictionary that tells Parcels where the U and V velocity data is,
    # and where to find the coordinates. 
    filenames = {'U': {'lon': mesh_mask, 'lat': mesh_mask, 'depth': mesh_mask, 'data': ufiles}, 'V': {'lon': mesh_mask, 'lat': mesh_mask, 'depth': mesh_mask, 'data': vfiles}}
    variables_1 = {'U': 'u', 'V': 'v'}
    dimensions = {'U': {'lon': 'xu_ocean', 'lat': 'yu_ocean', 'depth': 'sw_ocean', 'time': 'time'}, 'V': {'lon': 'xu_ocean', 'lat': 'yu_ocean', 'depth': 'sw_ocean', 'time': 'time'}}
    # Now define a dictionary that specifies the `U, V` variable names as given in the netCDF files  
    cs = {'U': {'lon': ('xu_ocean', 400), 'lat': ('yu_ocean', 300), 'depth': ('st_ocean', 75), 'time': ('time', 1)}, 'V': {'lon': ('xu_ocean', 400), 'lat': ('yu_ocean', 300), 'depth': ('st_ocean', 75), 'time': ('time', 1)}}
    # Define a dictionary to specify the U,V dimentions.
    # See the description under the 3D advection section for why we specify sw_ocean as the depth here. 
    # For further reading, also see this tutorial on the Ocean Parcels website: https://nbviewer.org/github/OceanParcels/parcels/blob/master/parcels/examples/documentation_indexing.ipynb
    # Define the chunksizes
    # Read in the fieldset using the Parcels `FieldSet.from_mom5` function. 
    fieldset = FieldSet.from_mom5(filenames, variables_1, dimensions, mesh='spherical', chunksize=cs, tracer_interp_method='bgrid_tracer')
    return (fieldset,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Check that the grid indexing type is correct for our model output. It should be **mom5**, not nemo or any other type, unless you're running 2D advection on a single layer in which case Arakawa-A grid indexing will also work (this will not be correct for 3D advection).
    """)
    return


@app.cell
def _(fieldset):
    print(fieldset.U.gridindexingtype)
    print(fieldset.V.gridindexingtype)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We need to tell Parcels that this fieldset is periodic in the zonal (east-west) direction. This is because, if the particle is close to the edge of the fieldset (but still in it), the advection scheme will need to interpolate velocities that may lay outside the fieldset domain. With the halo, we make sure the advection kernel can access these values.
    """)
    return


@app.cell
def _(fieldset):
    fieldset.add_constant('halo_west', fieldset.U.grid.lon[0])
    fieldset.add_constant('halo_east', fieldset.U.grid.lon[-1])
    fieldset.add_periodic_halo(zonal=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We now need a custom kernel that can move the particle from one side of the domain to the other.
    """)
    return


@app.cell
def _(particle_dlon):
    def periodicBC(particle, fieldset, time):
        if particle.lon < fieldset.halo_west:
            particle_dlon = particle_dlon + (fieldset.halo_east - fieldset.halo_west)
        elif particle.lon > fieldset.halo_east:
            particle_dlon = particle_dlon - (fieldset.halo_east - fieldset.halo_west)

    return (periodicBC,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We'll also add a recovery kernel to delete particles if they encounter the `ErrorOutOfBounds` signal from Parcels.
    """)
    return


@app.cell
def _(StatusCode):
    def checkOutOfBounds(particle, fieldset, time):
        if particle.state == StatusCode.ErrorOutOfBounds:
            particle.delete()

    return (checkOutOfBounds,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can create the **Particle Set**. This contains the particle starting locations and defines the type of particle that is simulated. We'll read in the `ht` field from the model and initialise particles in a small section across the ACC.
    """)
    return


@app.cell
def _(cat, experiment):
    datastore = cat[experiment].search(variable='ht')
    datastore = datastore.search(path=datastore.df.loc[0,'path'])
    ht = datastore.to_dask(xarray_open_kwargs={'chunks':'auto'}).ht
    return (ht,)


@app.cell
def _(JITParticle, ParticleSet, fieldset, ht, np):
    x1, x2 = -100.5, -100
    y1, y2 = -60, -65

    lons = ht.where((ht.yt_ocean<y1) & (ht.yt_ocean>y2) & (ht.xt_ocean<x2) & (ht.xt_ocean>x1), 
                    drop=True).geolon_t.values.ravel()
    lats = ht.where((ht.yt_ocean<y1) & (ht.yt_ocean>y2) & (ht.xt_ocean<x2) & (ht.xt_ocean>x1), 
                    drop=True).geolat_t.values.ravel()

    depths = np.full(len(lats), 1.)

    pset = ParticleSet.from_list(fieldset=fieldset,   # the fields on which the particles are advected
                                 pclass=JITParticle,  # the type of particles (JITParticle or ScipyParticle)
                                 lon=lons,            # a vector of release longitudes 
                                 lat=lats,            # a vector of release latitudes
                                 depth=depths,        # a vector of release depths 
                                 time=0.)             # set time to start start time of daily velocity fields
    pset
    return lats, lons, pset


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot these particles.
    """)
    return


@app.cell
def _(ht, lats, lons, plt):
    fig = plt.figure(figsize=(12, 4))

    ht.plot(cmap='Blues')
    plt.scatter(lons, lats, s=5, c='r')
    plt.ylim([-80, -35]);

    ax = plt.gca()
    ax.set_facecolor('gray')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can now advect these particles with Parcels. We'll do this using 4th order Runge-Kutta in 2D. In this example, we'll integrate the particle positions for only 50 days to keep it simple. This may take a few minutes depending on the resources you're using. Feel free to change the total length of the run as you like.
    """)
    return


@app.cell
def _(warnings):
    warnings.filterwarnings("ignore", category=FutureWarning, message=".*xarray will not decode timedelta values.*")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Note**: This cell might take ~5 minutes.
    """)
    return


@app.cell
def _(
    AdvectionRK4,
    checkOutOfBounds,
    output_directory,
    periodicBC,
    pset,
    timedelta,
):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    # Set your output location: 
    output_filename = 'TestParticles_2D.zarr'

    # Set the file name and the time step of the outputs 
    # (particle locations will be saved every 2 days in this example). 
    # If you're running long simulations, consider reducing this output timestep to 5 or 10 days to save storage and file space.  
    output_file = pset.ParticleFile(name=output_directory / output_filename, 
                                    outputdt=timedelta(days=2)
                                   ) 

    kernels = [AdvectionRK4, # the 2D advection kernel (which defines how particles move) 
               periodicBC,
               checkOutOfBounds ]

    pset.execute(kernels, 
                 runtime=timedelta(days=50),   # the total length of the run
                 dt=timedelta(hours=2),        # the integration timestep of the kernels (generally, the smaller the better but this comes with a computational/time cost)
                 output_file=output_file,      # the output file
                )
    return (output_filename,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Open the output file and plot the first 100 of these trajectories.
    """)
    return


@app.cell
def _(ht, mpl, output_directory, output_filename, plt, xr):
    ds = xr.open_zarr(output_directory / output_filename)
    fig_1 = plt.figure(figsize=(12, 8))
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['r', 'pink', 'violet', 'firebrick', 'orange', 'orangered'])
    ht.plot(cmap='Blues')
    plt.plot(ds.lon[:100, :].T, ds.lat[:100, :].T)
    plt.scatter(ds.lon[:100, :], ds.lat[:100, :], s=5, c='w')
    plt.ylim([-68, -60])
    plt.xlim([-108, -90])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3D Advection with temperature and salinity sampling

    Now we'll run an example in 3D and also sample and save temperature and salinity fields.
    """)
    return


@app.cell
def _(dask, warnings):
    warnings.simplefilter(action='ignore', category=dask.array.core.PerformanceWarning)
    return


@app.cell
def _():
    experiment_1 = '01deg_jra55v13_ryf9091'
    return (experiment_1,)


@app.cell
def _(glob, output_directory):
    # define the file paths containing the daily U, V, W, temperature and salinity data
    data_path_1 = '/g/data/ik11/outputs/access-om2-01/01deg_jra55v13_ryf9091/'
    ufiles_1 = sorted(glob(data_path_1 + 'output19*/ocean/ocean_daily_3d_u_*.nc'))
    vfiles_1 = sorted(glob(data_path_1 + 'output19*/ocean/ocean_daily_3d_v_*.nc'))
    wfiles = sorted(glob(data_path_1 + 'output19*/ocean/ocean_daily_3d_wt_*.nc'))
    tfiles = sorted(glob(data_path_1 + 'output19*/ocean/ocean_daily_3d_temp_*.nc'))
    sfiles = sorted(glob(data_path_1 + 'output19*/ocean/ocean_daily_3d_salt_*.nc'))
    # Define a file which contains the model grid and coordinates that Parcels needs
    # Note: We've already created this file under the 2D advection example, so here we're just defining a file path. 
    mesh_mask_1 = str(output_directory) + '/ocean.nc'
    return mesh_mask_1, sfiles, tfiles, ufiles_1, vfiles_1, wfiles


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We now need to set up the Parcels `FieldSet`. For 3D advection we also need a vertical velocity field (`W`), and in this example we'll add temperature and salinity as well.

    **Note:** Initialising the `FieldSet` can take some time depending on the domain and number of files you're feeding to Parcels. In this example, it should be quick.
    """)
    return


@app.cell
def _(FieldSet, mesh_mask_1, sfiles, tfiles, ufiles_1, vfiles_1, wfiles):
    # Define a dictionary that tells Parcels where the U and V velocity data is,
    # and where to find the coordinates. 
    filenames_1 = {'U': {'lon': mesh_mask_1, 'lat': mesh_mask_1, 'depth': mesh_mask_1, 'data': ufiles_1}, 'V': {'lon': mesh_mask_1, 'lat': mesh_mask_1, 'depth': mesh_mask_1, 'data': vfiles_1}, 'W': {'lon': mesh_mask_1, 'lat': mesh_mask_1, 'depth': mesh_mask_1, 'data': wfiles}, 'T': {'lon': mesh_mask_1, 'lat': mesh_mask_1, 'depth': mesh_mask_1, 'data': tfiles}, 'S': {'lon': mesh_mask_1, 'lat': mesh_mask_1, 'depth': mesh_mask_1, 'data': sfiles}}
    variables_2 = {'U': 'u', 'V': 'v', 'W': 'wt', 'T': 'temp', 'S': 'salt'}
    dimensions_1 = {'U': {'lon': 'xu_ocean', 'lat': 'yu_ocean', 'depth': 'sw_ocean', 'time': 'time'}, 'V': {'lon': 'xu_ocean', 'lat': 'yu_ocean', 'depth': 'sw_ocean', 'time': 'time'}, 'W': {'lon': 'xu_ocean', 'lat': 'yu_ocean', 'depth': 'sw_ocean', 'time': 'time'}, 'T': {'lon': 'xu_ocean', 'lat': 'yu_ocean', 'depth': 'sw_ocean', 'time': 'time'}, 'S': {'lon': 'xu_ocean', 'lat': 'yu_ocean', 'depth': 'sw_ocean', 'time': 'time'}}
    cs_1 = {'U': {'lon': ('xu_ocean', 400), 'lat': ('yu_ocean', 300), 'depth': ('st_ocean', 75), 'time': ('time', 1)}, 'V': {'lon': ('xu_ocean', 400), 'lat': ('yu_ocean', 300), 'depth': ('st_ocean', 75), 'time': ('time', 1)}, 'W': {'lon': ('xt_ocean', 400), 'lat': ('yt_ocean', 300), 'depth': ('sw_ocean', 75), 'time': ('time', 1)}, 'T': {'lon': ('xt_ocean', 400), 'lat': ('yt_ocean', 300), 'depth': ('st_ocean', 75), 'time': ('time', 1)}, 'S': {'lon': ('xt_ocean', 400), 'lat': ('yt_ocean', 300), 'depth': ('st_ocean', 75), 'time': ('time', 1)}}
    # Now define a dictionary that specifies the `U, V` variable names as given in the netCDF files  
    # Define a dictionary to specify the U,V, W, T and S dimentions.
    # All variables must have the same lat/lon/depth dimensions (even though the data doesn't).
    # We can check that Parcels is using the right type of grid indexing and interpolation once we've created the fieldset
    # For further reading, also see this tutorial on the Ocean Parcels website: 
    # https://nbviewer.org/github/OceanParcels/parcels/blob/master/parcels/examples/documentation_indexing.ipynb
    # Define the chunksizes
    # Read in the fieldset using the Parcels `FieldSet.from_mom5` function. 
    fieldset_1 = FieldSet.from_mom5(filenames_1, variables_2, dimensions_1, mesh='spherical', chunksize=cs_1, tracer_interp_method='bgrid_tracer')
    return (fieldset_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Check that the grid indexing and the interpolation methods have been correctly set by Parcels. MOM5 is a **B-grid** model. Anything other than **bgrid_velocity** and **bgrid_tracer** interpolation methods will give you incorrect results for this particular model/experiment.
    """)
    return


@app.cell
def _(fieldset_1):
    # check that the grid indexing type is correct for our model outpu (should be mom5, not nemo or any other type)
    print(fieldset_1.U.gridindexingtype)
    print(fieldset_1.V.gridindexingtype)
    print(fieldset_1.W.gridindexingtype)
    print(fieldset_1.T.gridindexingtype)
    print(fieldset_1.S.gridindexingtype)
    print(fieldset_1.U.interp_method)
    print(fieldset_1.V.interp_method)
    print(fieldset_1.W.interp_method)
    print(fieldset_1.T.interp_method)
    print(fieldset_1.S.interp_method)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As for the 2D advection case, we need to tell Parcels that this fieldset is periodic in the zonal (east-west) direction. This is because, if the particle is close to the edge of the fieldset (but still in it), the advection scheme will need to interpolate velocities that may lay outside the fieldset domain. With the halo, we make sure the advection kernel can access these values.
    """)
    return


@app.cell
def _(fieldset_1):
    fieldset_1.add_constant('halo_west', fieldset_1.U.grid.lon[0])
    fieldset_1.add_constant('halo_east', fieldset_1.U.grid.lon[-1])
    fieldset_1.add_periodic_halo(zonal=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We now need to define a particle class that tells Parcels each particle has a temperature and salinity value associated with it. We also need to define a kernel to tell Parcels to sample the temperature and salinity fields at each integration timestep.
    """)
    return


@app.cell
def _(JITParticle, Variable, np):
    # Parcels will automatically save the latitude, longitude, and depth to file at a timestep that 
    # you specify (see cells below). This kernel tells Parcels to also save the temperature and salinity fields
    # to file, along with the location data. 
    class SampleParticle(JITParticle):
        thermo = Variable('thermo', dtype=np.float32, initial = 0.0)
        psal = Variable('psal', dtype=np.float32, initial = 0.0)

    # Kernel to sample temperature and salinity (if you have fed them into your FieldSet above).
    def SampleFields(particle, fieldset, time):
        particle.thermo = fieldset.T[time, particle.depth, particle.lat, particle.lon]
        particle.psal =   fieldset.S[time, particle.depth, particle.lat, particle.lon]

    return SampleFields, SampleParticle


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can create the **Particle Set**. Well use the same particle set as in the 2D example but this time we'll initialise particles at 10m depth. This time you can see that `thermo` and `psal` have been added to the Particle Set.
    """)
    return


@app.cell
def _(ParticleSet, SampleParticle, cat, experiment_1, fieldset_1, np):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    ht_1 = cat[experiment_1].search(variable='ht').to_dask()
    x1_1, x2_1 = (-100.5, -100)
    y1_1, y2_1 = (-60, -61)
    lons_1 = ht_1.where((ht_1.yt_ocean < y1_1) & (ht_1.yt_ocean > y2_1) & (ht_1.xt_ocean < x2_1) & (ht_1.xt_ocean > x1_1), drop=True).geolon_t.values.ravel()
    lats_1 = ht_1.where((ht_1.yt_ocean < y1_1) & (ht_1.yt_ocean > y2_1) & (ht_1.xt_ocean < x2_1) & (ht_1.xt_ocean > x1_1), drop=True).geolat_t.values.ravel()
    depths_1 = np.full(len(lats_1), 10.0)
    pset_1 = ParticleSet.from_list(fieldset=fieldset_1, pclass=SampleParticle, lon=lons_1, lat=lats_1, depth=depths_1, time=0.0)
    pset_1  # the fields on which the particles are advected  # the type of particles we specified above with temp and salt added  # a vector of release longitudes  # a vector of release latitudes  # a vector of release depths  # set time to start start time of daily velocity fields
    return ht_1, pset_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For the 3D advection we will integrate particles forward-in-time for 20 days to keep this example simple, but feel free to integrate longer! If you want really long integrations, or a large particle set, you will need to consider [submitting the analysis as a job on Gadi](https://cosima-recipes.readthedocs.io/en/latest/01-Cooking-Tutorials/02-Advanced/Submitting_analysis_jobs_to_gadi.html) or to some other HPC system of your liking.

    **Note 1**: Generally you want to use a small integration timestep (`dt`). This is because, the larger the `dt`, the further particles will move in a single timestep and the more likely you are to get particles crossing ocean-land boundaries and 'beaching'. For example, in some Lagrangian applications it is common to use `dt` <= 15 minutes. However the choice of `dt` has to be balanced against the computational resources and the available simulation time. In this example, we'll use a `dt` of 1 hour to speed up the integration. If you want to integrate particles backwards-in-time, simple feed Parcels a negative `dt` value.

    **Note 2**: This 3D example may take some time (several minutes) depending on the resources you're using.
    """)
    return


@app.cell
def _(
    AdvectionRK4_3D,
    SampleFields,
    checkOutOfBounds,
    output_directory,
    periodicBC,
    pset_1,
    timedelta,
):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    # Set your output location: 
    output_filename_1 = 'TestParticles_3D.zarr'
    output_file_1 = pset_1.ParticleFile(name=output_directory / output_filename_1, outputdt=timedelta(days=2))
    # the file name and the time step of the outputs 
    # (particle locations will be saved every 2 days in this example)
    kernels_1 = [AdvectionRK4_3D, periodicBC, SampleFields, checkOutOfBounds]
    pset_1.execute(kernels_1, runtime=timedelta(days=20), dt=timedelta(hours=1), output_file=output_file_1)  # the total length of the run  # the integration timestep of the kernel  # the output file
    return (output_filename_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Open output file and scatter plot the first 100 of these trajectories, coloured by depth.
    """)
    return


@app.cell
def _(ht_1, output_directory, output_filename_1, plt, xr):
    ds_1 = xr.open_zarr(output_directory / output_filename_1)
    fig_2 = plt.figure(figsize=(12, 8))
    ht_1['ht'].plot(cmap='Blues')
    plt.plot(ds_1.lon[:100, :].T, ds_1.lat[:100, :].T, c='w', zorder=2)
    cb = plt.scatter(ds_1.lon[:100, 1:], ds_1.lat[:100, 1:], c=ds_1.z[:100, 1:], s=20, vmin=3, vmax=18, cmap='Reds', zorder=3)
    plt.legend(*cb.legend_elements(num=10), loc='upper right', title='Depth (m)')
    plt.ylim([-62, -58])
    plt.xlim([-108, -95])
    return (ds_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For reference, this is how the output file is organised.
    """)
    return


@app.cell
def _(ds_1):
    ds_1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Convert the zarr data to netcdf [a crucial step!]
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Parcels now uses [`Zarr`](https://zarr.dev) for its output. This creates very large numbers of files, which may overwhelm the inode quota for your project. When running particle tracking experiments, you should closely monitor you inode usage and once the simulation is complete, you should postprocess the output into either NetCDF format or use zipped `Zarr` storage format. You may find [this post on the ACCESS Hive](https://forum.access-hive.org.au/t/zarr-inodes/5496?u=edoddridge) and [this post on Stack Overflow](https://stackoverflow.com/questions/67635491/transform-zarr-directory-storage-to-zip-storage) helpful.

    This example shows how to convert the zarr data to netcdf and how to delete the zarr files using the `rm` command. You should use `rm` on the command line to delete files when you have finished with them. **Do not use the ARE interface** to delete files - it doesn't actually delete them. Instead, those files are moved to a `.Trash*` folder in the project directory, where they still count towards the quotas for the project.
    """)
    return


@app.cell
def _(output_directory, output_filename_1, xr):
    # Open the Zarr datastore files
    ds_2 = xr.open_zarr(output_directory / output_filename_1)
    netcdf_output_filename = output_filename_1[:-4] + 'nc'
    # Define the netcdf output filename 
    print(netcdf_output_filename)
    # Save to NetCDF
    ds_2.to_netcdf(output_directory / netcdf_output_filename)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Remove original zarr files
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div class="alert alert-block alert-warning">
    <b>Caution:</b> Run this from the command line and be very careful about specifying the correct path
    </div>

    ```
    rm -r /path/to/zarr/files/TestParticles_2D.zarr
    rm -r /path/to/zarr/files/TestParticles_3D.zarr
    ```

    Files are currently stored in:
    """)
    return


@app.cell
def _():
    print(dir[0])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Modifying this example to work with ACCESS-OM3
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As a community, we are migrating to **ACCESS-OM3** which uses the **MOM6** ocean model. MOM6 uses an Arakawa C-grid (rather than the B-grid used in MOM5/ACCESS-OM2) and so requires code modifications from the examples given above, including:
    - A different `FieldSet` method
    - Updated variable names and dimensions
    - A new `mesh_mask`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For now, we will use output from a panAntarctic experiment (`panant-01-zstar-ACCESSyr2`) which is stored here:
    `/g/data/ol01/outputs/mom6-panan/panant-01-zstar-ACCESSyr2/`

    **! Warning !** In future, this data will be migrated to this location: `/g/data/cj50/access-nri/mom6-panant/panant-01-zstar-ACCESSyr2/`

    **Note:** MOM6 does not output a vertical velocity diagnostic. This means, at this stage, only 2D particle tracking can be run offline with MOM6/ACCESS-OM3 output.
    """)
    return


@app.cell
def _(warnings):
    warnings.filterwarnings("ignore", category=FutureWarning, message=".*xarray will not decode timedelta values.*")
    return


@app.cell
def _(glob):
    # define the file paths containing the daily U and V velocity data
    data_path_2 = '/g/data/ol01/outputs/mom6-panan/panant-01-zstar-ACCESSyr2/'
    uvfiles = sorted(glob(data_path_2 + 'output*/*.ocean_daily_z_*.nc'))
    uvfiles = uvfiles[:31]
    # for the sake of simplicity, we'll only use the first month of daily data in this example
    # Define the mesh mask containing the grid coordinates
    mesh_mask_2 = uvfiles[0]
    return mesh_mask_2, uvfiles


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div class="alert alert-block alert-warning">
    <b>MOM6 FieldSet Warning: </b> In MOM6 the t-cell dimensions (h points) have length 845 in the y direction and 3600 in the x direction, while the u-cell (q nodes) have length 846 and 3601. Parcels will complain about this mis-match. A work around is to restrict the lat and lon range to 845 and 3600 as in the code below. However, this causes problems with the periodic Halo construction and might not be the correct approach. <b>Use with caution!</b>
    </div>
    """)
    return


@app.cell
def _(FieldSet, mesh_mask_2, uvfiles):
    filenames_2 = {'U': {'lon': mesh_mask_2, 'lat': mesh_mask_2, 'depth': mesh_mask_2, 'data': uvfiles}, 'V': {'lon': mesh_mask_2, 'lat': mesh_mask_2, 'depth': mesh_mask_2, 'data': uvfiles}}
    variables_3 = {'U': 'uo', 'V': 'vo'}
    c_grid_dimensions = {'lon': 'xq', 'lat': 'yq', 'depth': 'z_l_sub01', 'time': 'time'}
    dimensions_2 = {'U': c_grid_dimensions, 'V': c_grid_dimensions}
    indices = {'lat': range(0, 845), 'lon': range(0, 3600)}
    # Note that all variables should be defined on the same dimension for a C-grid
    # Parcels deals with the staggered velocities under the hood in it's interpolation.
    # see more here: https://docs.oceanparcels.org/en/latest/examples/documentation_indexing.html
    # or here: https://docs.parcels-code.org/en/latest/examples/tutorial_nemo_3D.html
    # NOTE: The t-cell dimensions (h points) have length 845 in the y and 3600 in x
    # while the u-cell (q nodes) have length 846 and 3601 
    # Parcels will complain about this mis-match. A work around is to restrict the 
    # lat and lon range to 845 and 3600 as below. However, this might not be the correct 
    # approach. Use with caution!
    # You could also use the from_nemo FieldSet method, since Nemo 
    # is a C-grid model with the same u/v indexing as MOM6 
    # (see https://docs.oceanparcels.org/en/latest/examples/documentation_indexing.html) 
    fieldset_2 = FieldSet.from_c_grid_dataset(filenames_2, variables_3, dimensions_2, indices)
    return (fieldset_2,)


@app.cell
def _(fieldset_2):
    print(fieldset_2.U.gridindexingtype)
    print(fieldset_2.V.gridindexingtype)
    print(fieldset_2.U.interp_method)
    print(fieldset_2.V.interp_method)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the Particle Set as for the MOM5 example.
    """)
    return


@app.cell
def _(JITParticle, ParticleSet, fieldset_2, np, xr):
    file = '/g/data/ol01/outputs/mom6-panan/panant-01-zstar-ACCESSyr2/output049/20050301.ocean_static.nc'
    bathymetry = xr.open_dataset(file)
    x1_2, x2_2 = (-100.5, -100)
    y1_2, y2_2 = (-60, -65)
    lons_2 = bathymetry.where((bathymetry.yh < y1_2) & (bathymetry.yh > y2_2) & (bathymetry.xh < x2_2) & (bathymetry.xh > x1_2), drop=True).geolon.values.ravel()
    lats_2 = bathymetry.where((bathymetry.yh < y1_2) & (bathymetry.yh > y2_2) & (bathymetry.xh < x2_2) & (bathymetry.xh > x1_2), drop=True).geolat.values.ravel()
    depths_2 = np.full(len(lats_2), 1.0)
    pset_2 = ParticleSet.from_list(fieldset=fieldset_2, pclass=JITParticle, lon=lons_2, lat=lats_2, depth=depths_2, time=0.0, lonlatdepth_dtype=np.float32)
    pset_2  # the fields on which the particles are advected  # the type of particles (JITParticle or ScipyParticle)  # a vector of release longitudes  # a vector of release latitudes  # a vector of release depths  # set time to start start time of daily velocity fields
    return (pset_2,)


@app.cell
def _(AdvectionRK4, output_directory, pset_2, timedelta):
    # magic command not supported in marimo; please file an issue to add support
    # %%time
    # Set your output location: 
    output_filename_2 = 'TestParticles_MOM6_2D.zarr'
    output_file_2 = pset_2.ParticleFile(name=output_directory / output_filename_2, outputdt=timedelta(days=1))
    # Set the file name and the time step of the outputs 
    # (particle locations will be saved every 2 days in this example). 
    # If you're running long simulations, reduce this output timestep to 5 or 10 days (or longer!) to save storage and file space.  
    kernels_2 = [AdvectionRK4]
    pset_2.execute(kernels_2, runtime=timedelta(days=4), dt=timedelta(hours=2), output_file=output_file_2)  # the 2D advection kernel (which defines how particles move)  # the total length of the run  # the integration timestep of the kernels (generally, the smaller the better but this comes with a computational/time cost)  # the output file
    return


if __name__ == "__main__":
    app.run()
