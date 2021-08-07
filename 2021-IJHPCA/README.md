# Setup

- Install the spack environment at spack-env.  This will add the required
  packages for running the tests and analyzing the results.
- If flux-sched@0.8.0 is still being used, then copy the `flux-tree` command
  into the spack-env view libexec

# Running

- Run `./testing/test_generation/make-all-tests.sh`
  - This generates all of the directories/files for our tests
- Run `./testing/submit_tests.py /path/to/testing-dirs/*`
  - This submits all of the tests to Slurm, run with `--help` to control which
    queue, the amount of parallelism, and how the jobs are dependent on one
    another (i.e., in a chain or all indepdendent).
- Run `./testing/find-failed-jobs.sh` to check for any hung or failed jobs.
  Delete their directories and restart from step 1 of this section.

# Analysis

- Run `cd ./analysis/data; ./run_full_pipeline.sh`
  - This runs `generate_all_dfs.sh` and `run_analysis_pipeline.sh`, which are
    described below.

## Analysis Pipeline

- `generate_all_dfs.sh`
  - Traverses the run directories, collects the relevant data from all runs,
    saves results out as pickled pandas dataframes.  These dataframes are much
    smaller than the full testing directories, easier to move around between
    machines, faster to start from when analyzing/plotting, and more condusive
    to version control (although still not great).
- `run_analysis_pipeline.sh`
  - Runs the full analysis pipeline, starting with the dataframes generated in
    the previous script and ending with figures and latex tables.
  - Splitting out from dataframe generation makes iterating on analysis scripts
    quicker.
  - This script calls many individual scripts, which are described below
- `generate_all_models.sh` (calls `generate_model.py` for each test application)
  - Generate a dataframe with the performance predicted by each model
- `generate_all_stats.sh` (calls `generate_model_stats.py` for each test application)
  - Generate a dataframe with the statistics of the model predictions
- `print_all_stats.sh` (calls `print_real_stats.py` and `print_model_stats.py` for each test application)
  - Print latex tables on real and model dataframes generated by the previous steps
- `plot_all_models.sh` (calls `plot_with_model.py` for each test application)
  - Plots the real performance curves with the model's predicted performance on
    same figure from dataframes generated by previous steps
- `scale_up_study.sh` (calls `model_scale_study.py`, `plot_model_scale_study.py`, and `print_scale_up_stats.py`)
  - Generates a model for a pre-exascale system, then plots the predicted
    performance in a figure and dump out relevant statistics in a latex table.

# Other Utilities
- `analysis/dump_df.py`
  - Will print out to terminal (or dump to a csv) any of the dataframes
    generated in the analysis pipeline
- `analysis/clear_analysis_cache.sh`
  - Clears out the `*.cache` files created in the test directories. Run this if
    `generate_all_dfs.sh` is returning stale data.
- `testing/find-unsubmitted-jobs.py`
  - Prints out any tests not already submitted.  Useful if you ran a
    test-generation script after running `submit_tests.py`
- `testing/poll-squeue.sh`
  - Script that leverages the interval feature of `squeue` to efficiently
    monitor the status of the experiments.
  - Also overrides the default output format to give more space to the test
    name.