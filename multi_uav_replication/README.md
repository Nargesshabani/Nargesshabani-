# Multi-UAV edge computing: a transparent, conditional reproduction

Executable Python implementation of the mathematical models and three
algorithms from Guo et al., “Achieve Load Balancing in Multi-UAV Edge Computing
IoT Networks: A Dynamic Entry and Exit Mechanism,” IEEE Internet of Things
Journal, 2022, DOI 10.1109/JIOT.2022.3161703.

**This is not a verified reproduction of the published numerical results.** The
PDF does not supply the original data or several essential parameters, and
contains inconsistent formulas. The supplied simulations use explicit
assumptions and report the resulting disagreements. Read
[REPRODUCIBILITY_REPORT.md](REPRODUCIBILITY_REPORT.md) before interpreting plots.

## Run

Python 3.10 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 python main.py
```

No network access or external dataset is needed after dependency installation.
NumPy and Matplotlib are the only runtime dependencies. Unit tests use unittest.
`python validate_results.py` checks the generated CSVs independently.
The tested dependency versions are pinned in `requirements-tested.txt`.

Outputs are already included. `python main.py` deterministically overwrites
`results/` and `figures/`. To use another destination:

```bash
OPENBLAS_NUM_THREADS=1 python main.py --output /tmp/uav-run
```

To change assumptions, copy `results/config.json`, edit its `assumptions`
object, and run `python main.py --config your_config.json`. The `paper` object
contains verified values. The default carrier frequency of 2 GHz was requested
by the user but could not be verified in the PDF. Select
`horizontal_mode: "printed"` to evaluate Eq.11 verbatim: full daily missions can
fail a battery constraint in that mode. Such failure is intentional and is
never hidden by clipping energy or battery. The default `force_balance` mode
is a documented interpretation, not a faithful Eq.11 transcription.

## What is included

- Wireless Eqs.1–7, computation Eqs.8–9, four flight modes Eqs.10–13,
  trapezoidal/triangular velocity profiles and numerical flight integration.
- P1 resource feasibility and count scan; P2 queue variance and explicit delay
  and landing checks. Algorithms are heuristics, not exact P2 solvers.
- Algorithm 1 with printed tau and membership exponent; fixed center retained.
- Three-layer BP with training, inference, persistence, Adam/SGD/RMSProp;
  date-separated training and holdout; serialized synthetic training samples.
- Algorithm 2 prediction, EAlert, entry, least-battery exit, replacement,
  feedback beta/alpha decisions, redeployment and task service.
- Algorithm 3 preassignment, old-task priority, pooling, nearest-task selection,
  printed `<=av` filling, FIFO, and task handoff.
- Fixed-four, prediction-only, resource-count enumeration, nearest-available
  greedy, exhaustive small-case allocation, and large-case exact count oracle.
- Daily and five-UAV short experiments; CSV data for every figure; PDFs and
  300 dpi PNGs; assumption sensitivities; unit and integration tests.

## Layout / paper-to-code map

| Module | Purpose |
|---|---|
| config.py | Verified paper values and separate assumption dataclass |
| communication_model.py | Eqs.1–7, watts/dBm and bits/s |
| computation_model.py | Eqs.8–9 and explicit notation interpretations |
| energy_model.py | Eqs.10–13; flight profiles, route and EAlert |
| ls_fcm.py | Algorithm 1; Eqs.16–18 |
| bp_prediction.py | Algorithm 2 BP component; saved NumPy model |
| mneea.py | Algorithm 2 decision sequence |
| load_balancing.py | Algorithm 3 |
| baseline_methods.py | Count enumeration, greedy and task-count optimum |
| objectives.py | Eqs.14–15 objective/constraint evaluators |
| environment.py | Aircraft lifecycle, serial task service, energy ledger |
| task_generator.py / iot_devices.py / uav.py | Seeded input and state |
| evaluation.py | Experiment orchestration, CSV export, sensitivities |
| visualization.py | Figures corresponding to Figs.2–9 plus total energy |
| tests/ | Equation, algorithm and end-to-end checks |
| docs/ | Source extraction, mathematical transcription and assumptions |

The detailed, equation-by-equation mapping is in
[docs/PAPER_ANALYSIS.md](docs/PAPER_ANALYSIS.md), with mathematical formulas in
[docs/MATHEMATICS.md](docs/MATHEMATICS.md) and all unresolved choices in
[docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md).

## Experiments and output interpretation

`prediction.csv`: held-out next-day 288-point demand and prediction, not the
original Fig.3 dataset. Training day indices are distinct from the final day.
`prediction_scores.csv`: holdout MSE/MAE; `training_loss.csv`: training curves.
`daily_metrics.csv`: four policies on identical tasks, 288 slots each;
`task_results.csv`: individual deadline outcomes; `uav_events.csv`: launch,
exit, replacement and redeployment events; `energy_ledger.csv`: all accounted
energy components, including retired aircraft. `daily_loads.csv` reports
pre-service queue counts; `summary.csv` gives task-weighted success and daily
energy, not averages of success fractions when task counts differ.

`short_comparison.csv`: 70 fixed device positions, five stationary UAVs,
Algorithm 3 versus nearest-available greedy and ideal balanced-count allocation.
Full allocated work is charged even if late in this isolated battery experiment;
flight is excluded, matching the source's Fig.9 description. This differs from
the daily deadline-drop queue engine. `enumeration_verification.csv` compares
literal exhaustive search with the analytic count optimum on small problems.
The large-case optimum ignores geography and is not a solution of constrained P2.

Sensitivity CSVs expose dependence on unresolved angle, deadline, compute-energy
notation, and horizontal-flight interpretation. No tuning is performed to make
the proposed method win. All output figure captions label synthetic/conditional
results. Original figure traces are unavailable, so no quantitative original
versus replication error can be reported.

## Limits of the event model

Positions of active users are independently sampled each demand slot; the paper
does not provide a mobility law. New UAV service begins after launch travel;
old UAVs cover replacement rendezvous. During existing-aircraft redeployment,
the target geometry approximates moving-link geometry. Flight and hover time
are separated to avoid counting hover power during travel. Replacement flight
and old-aircraft rendezvous hover are charged explicitly; new-aircraft battery
begins at full minus route energy. Task-service energy is charged as a slot batch,
and replacement communication/CPU power uses observed per-slot means. These
choices do not constitute a continuous aircraft/radio/task co-simulation.

Aircraft are replaced proactively on continuous hover intervals between demand
updates. A rendezvous can straddle a sample boundary; its full cost is booked
at the replacement event. Thus an energy ledger is mission accounting, not an
instantaneous power trace. Initial deployment can cause missed deadlines.
No frequency optimization, inter-UAV interference, finite charging pool, thermal
model or flight weather model is invented; none is specified by this paper.

The literal vertical equations remain dimensionally inconsistent. Safe landing
checks here mean nonnegative reserve under configured numerical equations,
not a physical aircraft safety claim. All scientific conclusions are conditional
on these limitations and on the assumed traffic and deadline.
