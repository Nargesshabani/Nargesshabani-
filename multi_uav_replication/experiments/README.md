# Executed scenarios

`python main.py` runs these scenarios via evaluation.py:

| Source | Scenario / output |
|---|---|
| Fig.2 | 70 uniform devices, fixed center and 1/2/3 movable aircraft; clustering_*.csv |
| Fig.3 | 28 synthetic historical days, independent final day, 288 observations; prediction.csv |
| Fig.4 | Same training split, initial weights, batch schedule and lr across three optimizers; training_loss.csv |
| Figs.5–6 | Fixed four, BP-only, MNEEA, actual compute-resource enumeration; daily_*.csv |
| Figs.7–8 | Shared 70-device task trace, five UAVs, 60 slots, proposed/greedy/count oracle; short_comparison.csv |
| Fig.9 | Same static comparison, full allocated task energy, flight excluded; short_comparison.csv |
| Additional | Daily component energy including all flight; energy_ledger.csv |
| Validation | Exact small-instance enumeration vs count oracle; enumeration_verification.csv |
| Sensitivity | LoS angle, deadline, Eq.9 notation, Eq.11 flight mode; *_sensitivity.csv |
| Audit | Literal Eq.15 vs intended variance; p2_notation_audit.csv |

These are source-inspired scenarios on explicitly assumed inputs. Original
trace values, initial points, deadlines and several model parameters are absent.
Refer to the reproduction report instead of treating matching figure numbers
as evidence of matching published numerical results.
