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
    # Submitting analysis jobs to gadi

    This notebook goes through an example of how to convert your jupyter notebook code into a PBS job you can submit to Gadi, NCI.

    Sometimes, once you have your analysis working in a jupyter notebook and you are using a lot of data, it can be helpful to submit the job directly to Gadi. This uses the PBS queue (see NCI website for more details, https://opus.nci.org.au/display/Help/4.+PBS+Jobs). It means the job is not interactive, but it also means you can submit many jobs at the same time if say you want to break up your analysis and run one year/month at a time.

    One way to set up this analysis is to convert your `.ipynb` notebooks into `.py` files, and then run on gadi with a wrapping `.sh` bash script. Functions and packages that work in your `.ipynb` notebooks, such as `intake` also work on gadi. `dask`, however, requires some special treatment; see the CLEX CMS team's article on this for more information (https://coecms-training.github.io/parallel/dask-batch.html).

    This notebook shows how to
    1. set up your `.py` script to use `dask` stably
    2. set up your PBS script
    3. Optional: add an environment variable for easy submission of different months/years/variables
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1: `.py` script

    ```python
    \"\"\"
    Title - e.g. Computing EKE for one year
    \"\"\"

    # Load modules as normal

    import intake
    import numpy as np
    import cftime
    import xarray as xr

    import matplotlib.pyplot as plt
    import cmocean as cm
    import cartopy.crs as ccrs
    import cartopy.feature as cft

    import sys, os
    import warnings
    warnings.simplefilter("ignore")
    from dask.distributed import Client

    if __name__ == '__main__':

        client = Client(threads_per_worker = 1)
        catalog = intake.cat.access_nri

        ## Your jupyter notebook code goes here inside the `main` loop
    ```

    Add your python code from jupyter inside the main loop. **Be very careful of the indentation!**. Also note that at the end of the PBS script you need to explicitly save things, otherwise all the results of your analyses will get deleted. So, be sure to save any figures, data you need! For example, you could save out the variable EKE as a `netcdf` using the following code.

    ```python
        EKE.load() ## Loading first speeds up saving

        ##saving
        save_dir = '/path/...'
        ds = xr.Dataset({'EKE': EKE})
        ds.to_netcdf(save_dir+'EKE_expt0.nc',
                     encoding={'EKE': {'shuffle': True, 'zlib': True, 'complevel': 5}})

    ```
    The encoding line helps with compression. You can add extra attributes to the DataSet e.g. `long_name`, `units` etc. too.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: Make a PBS script
    The NCI website has information about all the different options you have for a PBS script. However, the following script should provide a starting point to modify the time, memory for your needs. If using dask make sure you set a value for `jobfs`, as the dask settings in the previous python script will set the dask to dump it computation in the `jobfs` local memory, which is very efficient compared to dumping in `/scratch` or `/g/data`.

    ```
    #!/bin/bash
    #PBS -P a01 #replace this with your NCI project, e.g., x77, e14, ...
    #PBS -q normalbw
    #PBS -l mem=120gb
    #PBS -l ncpus=8
    #PBS -l walltime=0:15:00
    #PBS -l storage=gdata/ik11+gdata/xp65+gdata/a01 # add all the storage flags you need
    #PBS -l jobfs=100gb
    #PBS -N save_EKE
    #PBS -j oe

    module use /g/data3/xp65/public/modules
    module load conda/analysis3

    cd /g/data/XXX/uu1234/analysis/scripts/  # replace here with directory that your .py script lives in

    # call python
    python3 save_EKE.py &>> output_save_EKE.txt ## This will output any python errors (e.g. dask output, print statements) into a .txt file for easy debugging.

    exit

    ```

    If you are satisfied with your code you can comment the `output_save_EKE.txt` out before the `&` symbol to avoid making unnecessary files. You will still always have a PBS error file with the walltime used and any errors in your PBS script (such as folders/files not being called correctly) - some of these `.txt` files can get very large with `dask` statements if it's a big job.

    #### *To submit this script (saved as `run_EKE.sh`) in gadi, use `qsub run_EKE.sh`.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## (Optional) Step 3: Loop

    Sometimes, you just want to run the same script for many months, variables or years. This is when the `-v` environment variables command is useful. For example, let's say our script calculates the EKE for 1 year, and we want to run it for 10 years. We make some small modifications to the PBS script:

    ```
    #!/bin/bash
    #PBS -P ### #(write your project here, e.g. x77,e14)
    #PBS -q normalbw
    #PBS -l mem=120gb
    #PBS -l ncpus=8
    #PBS -l walltime=0:15:00
    #PBS -l storage=gdata/ik11+gdata/xp65+gdata/x77+gdata/e14+scratch/e14
    #PBS -l jobfs=100gb
    #PBS -N save_EKE
    #PBS -j oe
    #PBS -v year

    module use /g/data3/xp65/public/modules
    module load conda/analysis3

    cd  /g/data/XXX/uu1234/analysis/scripts/ ## point to where your .py script is saved

    # call python
    python3 save_EKE.py $year &>> output_save_EKE_$year.txt

    exit

    ```

    Now, in order to run the script you need to specify a year, say 2000, using `qsub -v year=2000 run_EKE.sh`.

    You also need to tell python how to use this number, which you can do using `sys`. Inside the `'main'` loop, write

    ```python
        #### get run count argument that was passed to python script ####
        import sys
        year = int(sys.argv[1])

        start_time = str(year)+'-01-01'
        end_time = str(year)+'-12-31'
    ```

    And then you can go along with the python code/cosima recipes, selecting that time period using the cosima cookbook or `.sel(time =slice(start_time,end_time))`.

    Then, you can save the file out at the end of the code with a file name of a particular year
    ```python
        EKE.load() ## Loading first speeds up saving

        ##saving
        save_dir = '/path/...'
        ds = xr.Dataset({'EKE': EKE})
        ds.to_netcdf(save_dir+'EKE_year_'+str(year)+'.nc',
                     encoding={'EKE': {'shuffle': True, 'zlib': True, 'complevel': 5}})

    ```
    You can add more environment variables in the same way.

    Finally, for even faster command lines, you can write a small bash script to call the `qsub` command for each year. This will submit 10 of the same job with year argument 2000 to 2009 simulataneously (so be careful -- try not to submit hundreds of jobs at the same time which blocks up the NCI queues!)

    ```
    #!/bin/bash

    ## loop over count, submit job to gadi with count that gets communicated to python

    for i in {2000..2009}
    do
       echo "creating job for year $i"
       qsub -v year=i run_EKE.sh
    done

    ```

    ## A different looping strategy

    Rather than submitting 10 years at the same time, you could also add a counter in your PBS script so that when it gets to the end of the script it will resubmit but update the environment variable to be say the next year.

    ```
    #!/bin/bash
    #PBS -P a01 #replace this with your NCI project, e.g., x77, e14, ...
    #PBS -q normalbw
    #PBS -l mem=120gb
    #PBS -l ncpus=8
    #PBS -l walltime=0:15:00
    #PBS -l storage=gdata/ik11+gdata/xp65+gdata/a01 # add all the storage flags you need
    #PBS -l jobfs=100gb
    #PBS -N save_EKE
    #PBS -j oe
    #PBS -v year

    module use /g/data3/xp65/public/modules
    module load conda/analysis3

    cd /g/data/XXX/uu1234/analysis/scripts/  # replace here with directory that your .py script lives in

    # set max number of time loops to run:
    n_loops = 10

    # call python
    python3 save_EKE.py year &>> output_save_EKE_{year}.txt

    # increment count and resubmit:
    year = $((year+1))
    if [ $year -lt $n_loops ]; then
    cd $script_dir
    qsub -v year=$year run_EKE.sh
    fi

    exit
    ```

    Then running `qsub -v year=2000 run_EKE.sh` will run the code for year 2000, then once that has finished submit a job for year 2001 and so on for `n_loops = 10` iterations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Other links

    The CLEX wiki http://climate-cms.wikis.unsw.edu.au/Home is a great resource with lots of information!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


if __name__ == "__main__":
    app.run()
