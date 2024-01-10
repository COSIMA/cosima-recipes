import pytest
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError


def run_notebook(notebook_filename):
    '''
    Reads a notebook from a file, executes it, then writes the result back to a
    new file. If an error occurs while executing a cell, it stops and outputs a
    traceback.
    '''
    with open(notebook_filename) as f:
        nb = nbformat.read(f, as_version=4)
    path = Path(notebook_filename)
    notebook_filename_out = str(path.with_name(f"{path.stem}_converted{path.suffix}"))

    ep = ExecutePreprocessor(timeout=2400, kernel_name='python3')
    try:
        out = ep.preprocess(nb)
    except CellExecutionError:
        out = None
        msg = 'Error executing the notebook "%s".\n\n' % notebook_filename
        msg += 'See notebook "%s" for the traceback.' % notebook_filename_out
        print(msg)
        raise
    finally:
        with open(notebook_filename_out, mode='w', encoding='utf-8') as f:
            nbformat.write(nb, f)


@pytest.mark.parametrize(
    ("notebook_filename"),
    [
        ("COSIMA_CookBook_Tutorial.ipynb"),
        ("Make_Your_Own_Database.ipynb"),
        ("Making_Maps_with_Cartopy.ipynb"),
        ("Model_Agnostic_Analysis.ipynb"), 
        ("Spatial_selection.ipynb"),
        ("Submitting_analysis_jobs_to_gadi.ipynb"),
        ("Template_For_Notebooks.ipynb"),
        ("Using_Intake_Catalog.ipynb"),
        ("Using_Explorer_tools.ipynb"), 
    ])
def test_Tutorials(notebook_filename):
    run_notebook("Tutorials/" + notebook_filename)


@pytest.mark.parametrize(
    ("notebook_filename"),
    [
        ("Age_at_the_Bottom.ipynb"),
        ("Atlantic_IndoPacific_Basin_Overturning_Circulation.ipynb"),
        ("Barotropic_Streamfunction_model_agnostic.ipynb"),
        ("Bathymetry.ipynb"),
        ("Binning_transformation_from_depth_to_potential_density.ipynb"),
        ("Compare_SSH_model_obs.ipynb"),
        ("Compare_SST_SSS_TemperatureSalinity_to_WOA13.ipynb"),
        ("Cross-contour_transport.ipynb"),
        ("Cross-slope_section.ipynb"),
        #("Decomposing_kinetic_energy_into_mean_and_transient.ipynb"), # Takes a long time (not sure if it runs till the end)
        ("Equatorial_thermal_and_zonal_velocity_structure.ipynb"),
        ("Meridional_heat_transport.ipynb"),
        ("Model_Resolution_Comparison.ipynb"),
        ("Particle_tracking_with_Parcels.ipynb"),
        ("Querying_Scalar_Quantities_and_Annually_Averaged_Timeseries.ipynb"),
        ("Regridding.ipynb"),
        ("RelativeVorticity.ipynb"),
        ("SeaIce_Obs_Model_Compare.ipynb"),
        ("SeaIce_Plot_Example.ipynb"),
        #("SeaIceSeasonality_DFA.ipynb"), # Does not run
        ("Surface_Water_Mass_Transformation.ipynb"),
        ("TemperatureSalinityDiagrams_mom5_mom6.ipynb"),
        ("Transport_Through_Straits.ipynb"),
        ("True_Zonal_Mean.ipynb"),
        ("Zonally_Averaged_Global_Meridional_Overturning_Circulation.ipynb"),
        ("NearestNeighbourDistance.ipynb"),
    ])
def test_DocumentedExamples(notebook_filename):
    run_notebook("DocumentedExamples/" + notebook_filename)
