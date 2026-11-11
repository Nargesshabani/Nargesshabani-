# Reproducibility report

## Outcome

An executable, modular **conditional implementation** has been produced and
run. This work does **not** establish full reproduction of the paper. Original
training/traffic data, key numerical parameters and several mathematical
conventions are unavailable. Some printed equations are inconsistent. Source
transcriptions, interpreted operational formulas and unverified assumptions are
kept visible and separately selectable where useful.

All requested deliverable categories are included: source, dependencies,
README, equation documentation, algorithm mapping, tests, CSVs, figures,
reproducibility analysis and a missing-parameter register. This means the
software/artifact work is delivered; it does not mean scientific equivalence
to the authors' implementation or figures has been demonstrated.

## Executed daily results

Default scenario: 288 five-minute demand observations; synthetic held-out day;
one initially fixed-center aircraft; 1 GHz CPUs; 500 kJ batteries; task ranges
from the paper. Slot-boundary task batches have an assumed 1 s deadline. Every
policy receives the same 10,748 tasks. All four use Algorithm 3 to isolate the
deployment policy. Energy uses the documented horizontal force-balance
interpretation and printed, dimensionally unresolved vertical equations.

| Deployment policy | Task deadline success | Mean active UAVs | Mean queue SD | Accounted energy (MJ) | Replacements |
|---|---:|---:|---:|---:|---:|
| fixed | 9.83% | 4.000 | 0.641 | 49.671 | 96 |
| prediction | 11.19% | 4.111 | 0.627 | 51.070 | 93 |
| proposed | 11.33% | 4.618 | 0.644 | 57.394 | 27 |
| enumeration | 10.82% | 4.215 | 0.578 | 52.351 | 42 |

These results fail to reproduce the paper's near-perfect stabilized success
result. They are reported without selecting a deadline or radio convention
that makes the curves look favorable. They also do not establish that MNEEA
always stays one or two aircraft above enumeration or changes counts less
often. Frequent count fluctuations remain with this synthetic trace and the
printed beta reset condition. These discrepancies are scientifically relevant.

Total daily energy includes launches, redeployment, hover, task communication,
computation, replacement rendezvous hover and return flights of retired
vehicles. Active aircraft are still aloft at the final horizon: their future
return energy is reserved but not charged as a completed mission. There is no
single-fleet battery curve across replacements; every new physical aircraft
has a new ID, initial energy and route cost. Reserve checks passed under these
numerical formulas, with a 10^-7 J floating-point tolerance. This is not a
physical safety validation of the source equations.

## Prediction and isolated load-balancing experiment

Synthetic historical data: 28 days, 22 dates train / 6 dates hold out, with a
separate day 28 used for daily experiments. One hidden layer, tanh hidden
activation, linear output, width 24, 800 epochs; date/time/current count to
next-slot count. The original training dataset, activations, hidden width,
optimizer settings and exact prediction target/horizon are not supplied.

| Optimizer | Held-out MSE (devices²) | Held-out MAE (devices) |
|---|---:|---:|
| sgd | 82.572 | 7.163 |
| rmsprop | 65.646 | 6.381 |
| adam | 63.197 | 6.375 |

70 devices, five stationary UAVs, 60 slots, shared positions/tasks:

| Task allocation | Mean queue SD | Final battery spread (J), flight excluded |
|---|---:|---:|
| proposed | 0.577 | 63.926 |
| greedy | 1.892 | 141.385 |
| count_optimum | 0.372 | 36.220 |

This static battery comparison charges every allocated task to completion,
including late tasks, and excludes flight as specified in Fig.9. The daily
engine drops tasks at deadline. The count optimum ignores geography; literal
small-instance enumeration verifies its variance. An analytic equal-count
assignment is used at large size, explicitly avoiding a false claim that N^M
states were exhaustively enumerated for 70 users.

## Equation and algorithm validation

21 unit/integration tests pass (`results/tests.log`). Checks cover dimensional
conversions where meaningful, independent distance/rate/compute values,
triangular/trapezoidal flight distance conservation, quadrature order agreement,
zero-speed hover, the literal LS-FCM membership exponent and zero-distance
cases, initialization/seed reproducibility, unique FIFO task assignments,
preferential retention, nearest-available baseline behavior, exact small-case
enumeration, P1 strict equality, entry/exit/feedback, fixed-role preservation,
EAlert replacement, long idle replacement, deadline processing, model
persistence and literal P2 degeneracy.

`validate_results.py` independently checks equal tasks across policies, unique
task outcomes, outcome conservation, successful-task delays, nonnegative energy
charges, landing reserves, energy-ledger sums, oracle agreement, date-separated
training/holdout data, and experiment dimensions. It writes validation.json
and SHA-256 hashes of all CSVs.

A second full execution produced byte-identical prediction, loss, daily metric,
task-result, aircraft-event, energy-ledger, short-comparison and summary CSVs
in this environment (`full_run_reproducibility.json`). This is deterministic
reproducibility of this implementation, not replication of unavailable author
outputs. Cross-platform bitwise equivalence of floating-point kernels is not
claimed. Matplotlib PDF metadata may vary across rendering runs.

## Blocking source issues and measured sensitivity

1. **Eq.6:** printed distance divided by bit rate is dimensionally invalid.
   Default uses task bits; selectable printed mode exists for diagnosis.
2. **Eq.9:** task CPU cycles are total cycles in Eq.8/Table I, yet Eq.9 adds a
   d_m,n factor that elsewhere denotes distance. Default total-cycle dynamic
   CPU energy is explicitly interpreted; distance and data-multiplied options
   are available. Gamma is unspecified. Result magnitudes are highly sensitive.
3. **Eq.10:** printed extra sqrt(2) in induced-power denominator is retained.
4. **Eq.11:** printed c3*a*v² term makes a 100 m horizontal trip cost roughly
   554 kJ under the configured missing aircraft parameters, above 500 kJ.
   At 500 m it costs roughly 1.799 MJ. An explicitly assumed q=c2*v²+c3*a
   force-balance interpretation costs about 1.303 kJ and 6.101 kJ respectively.
   It is the operational default; original printed mode remains executable.
5. **Eqs.12–13:** Q2 is undefined and the nested radical is dimensionally
   invalid; printed signs/nesting remain. No independent aircraft measurements
   or corrected author formula are available. Numerical integration accuracy
   cannot establish physical correctness.
6. **Eqs.16/18:** tau is squared distance while the membership exponent is
   2/(eta−1). This is not the minimizer of the printed G for that tau; both
   printed formulas are retained. Objective decrease is not asserted.
7. **Eq.15:** literal repeated n makes the objective degenerate (zero for all
   active UAVs). Both literal and variance interpretations are implemented.
   P2's binary assignment nature also contradicts the paper's convexity claim.
8. **Algorithm 2:** beta initial value and updating offer within loops are
   absent; initialized beta and refreshed capacities are documented repairs.
   The fixed role is preserved, including replacement by another aircraft.
9. **Algorithm 3:** av rounding unspecified and printed <= can overfill by one.
   Floor and literal <= are retained rather than substituting ideal balancing.

A shared static 29-task sensitivity snapshot gives:

| LoS angle convention | 1 s success | 2 s success | 5 s success |
|---|---:|---:|---:|
| radians | 17.24% | 44.83% | 100.00% |
| degrees | 31.03% | 62.07% | 100.00% |

These values isolate sensitivity; they are not a tuning recommendation or a
claim that either convention matches the authors' implementation.

## Remaining gaps and differences

The exact missing-item/source-location/why-needed/assumption register is in
`docs/ASSUMPTIONS.md`. In particular the requested 2 GHz carrier could not be
verified. The PDF's Table I does not fix M,N,T; experimental cases are inferred
only where stated in figure captions/text. There is no author data or code
against which to compute curve RMSE, confidence intervals or original result
agreement. No reference curve points have been fabricated or digitized.

The service engine is an explicit approximation: serial communication then
CPU, batch arrival, independent uniform device positions between samples,
target geometry for existing moving aircraft, rendezvous role handoff and
slot-batch task-energy charging. New aircraft arrival delay is modeled; the
old role covers replacements. Full rendezvous costs may be booked before the
next sample. These differences preclude claiming a fully continuous joint
flight/radio/CPU reproduction. No thermal model is invented to mimic the
paper's qualitative overheating argument.

To establish a faithful numerical replication, obtain the authors' data and
training specification, intended Eq.6/9/11–13/15–18 interpretations, missing
radio/aircraft values, deadline and task timing/arrival laws, deployment and
handoff timing rules, baseline implementations and original measurement
traces. Replace assumption entries with verified values, refine the event
engine where required, and rerun the full suite and original-curve comparison.
