# Multi-UAV Edge Computing Research Replication

This repository preserves the existing Python project and generated outputs for
Guo et al., *Achieve Load Balancing in Multi-UAV Edge Computing IoT Networks:
A Dynamic Entry and Exit Mechanism* (IEEE Internet of Things Journal, 2022;
DOI: 10.1109/JIOT.2022.3161703).

**Scientific status:** this is a conditional implementation with documented
assumptions, not a verified reproduction of the paper's numerical results.
Read the [reproducibility report](multi_uav_replication/REPRODUCIBILITY_REPORT.md)
and [assumptions register](multi_uav_replication/docs/ASSUMPTIONS.md) before
interpreting the results. The existing project has been copied without changing
its source, tests, documentation, data, model, figures, or ZIP archive.

## Repository structure

```text
.
├── README.md                         # Repository installation and output guide
├── UPLOADED_FILES.md                 # Complete inventory of tracked files
├── TRANSFER_SHA256SUMS.sha256         # Checksums for all 80 original output files
├── multi_uav_replication.zip          # Complete original archive, unchanged
├── multi_uav_replication.zip.sha256   # Original archive checksum
└── multi_uav_replication/
    ├── README.md                     # Original detailed project guide
    ├── REPRODUCIBILITY_REPORT.md      # Findings, validation and limitations
    ├── MANIFEST.sha256               # Original project file checksums
    ├── requirements.txt
    ├── requirements-tested.txt       # Versions used for the existing outputs
    ├── *.py                          # Models, algorithms, experiments and plots
    ├── docs/                         # Paper extraction, equations and assumptions
    ├── experiments/                  # Scenario guide
    ├── tests/                        # Unit and integration tests
    ├── results/                      # CSVs, configuration, trained model and logs
    └── figures/                      # Ten figures in PDF and PNG formats
```

The full original mapping of paper equations and algorithms to Python modules
is in [PAPER_ANALYSIS.md](multi_uav_replication/docs/PAPER_ANALYSIS.md). Wireless,
computation and flight models, LS-FCM, BP prediction, MNEEA, load balancing and
baseline methods are implemented in separate modules.

## Installation

Use Python 3.10 or newer. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r multi_uav_replication/requirements.txt
```

For the versions used to generate the included outputs, install
`multi_uav_replication/requirements-tested.txt` instead. Runtime dependencies
are NumPy and Matplotlib; tests use the Python standard library's unittest.

## Execute and validate

```bash
cd multi_uav_replication
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 python main.py
python validate_results.py
```

On Windows, set `OPENBLAS_NUM_THREADS` in your shell or omit this optional
thread-limit setting. The included results and figures already exist; there is
no need to rerun the experiments just to view or download them. The existing
test log records 21 passing tests.

`python main.py` regenerates and overwrites `results/` and `figures/`. To keep
the included output files unchanged, write a new run elsewhere:

```bash
OPENBLAS_NUM_THREADS=1 python main.py --output ../new_run
```

For another configuration, copy `results/config.json`, change its documented
assumptions, then pass `--config PATH_TO_CONFIG.json`. The original config and
results are preserved in this repository. No implementation changes or new
experiment runs were needed for this transfer.

## Output files

- `results/prediction.csv`, `training_loss.csv`, `prediction_scores.csv`,
  `training_dataset.csv`, `bp_model.npz`: synthetic demand, BP training,
  holdout evaluation and saved model.
- `results/daily_metrics.csv`, `daily_loads.csv`, `task_results.csv`,
  `uav_events.csv`, `energy_ledger.csv`, `summary.csv`: four deployment policies,
  task outcomes, aircraft events, loads and component energy accounting.
- `results/short_comparison.csv`, `count_optimum.csv`,
  `enumeration_verification.csv`: five-UAV allocation comparison and exact
  small-case count-optimum checks.
- `results/*sensitivity.csv`, `p2_notation_audit.csv`, `flight_checks.csv`:
  unresolved-parameter sensitivity and equation diagnostics.
- `results/config.json`, `parameter_provenance.csv`, `provenance.json`,
  `validation.json`, `full_run_reproducibility.json`, `tests.log` and
  `run_summary.log`: configuration, provenance, verification and existing logs.
- `figures/fig02_*` through `fig09_*`, `entry_exit_events.*`, `total_energy.*`:
  eight figure analogues and two additional figures, each as PDF and PNG.

Original source data and some physical/model parameters are unspecified in the
paper. Generated data are synthetic; conditional curves must not be presented
as exact published measurements. See the original reproduction report for
explicit disagreements and the limitations of the flight and event models.

## Download the complete existing archive

[Download multi_uav_replication.zip](https://raw.githubusercontent.com/Nargesshabani/Nargesshabani-/main/multi_uav_replication.zip)

Original archive SHA-256:

```text
45e94a8d15dc0434a555a7d462b237ff24e6ae2c0f48887fcacb6e9e2a9d8d97
```

Verify the original transferred files from the repository root:

```bash
sha256sum -c TRANSFER_SHA256SUMS.sha256
```

The transfer checksum file covers all 80 files copied from `/workspace/output/`.
The three repository-level additions are this README, `UPLOADED_FILES.md` and
`TRANSFER_SHA256SUMS.sha256`; no original file was edited.
