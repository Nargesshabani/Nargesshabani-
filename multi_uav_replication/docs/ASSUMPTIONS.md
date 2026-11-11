# Unverified parameters and explicit interpretation choices

All numerical assumptions are in `config.Assumptions`, serialized in every
run's `results/config.json`. Verified numbers are in `config.Paper`.

| Missing/conflicting item | Source location | Why needed; selected interpretation |
|---|---|---|
| Carrier | II-A, IV-A/Table I | Rate needs fc; 2 GHz comes from user request, not verified in PDF |
| Height | II-A/C | Slant distance, travel, energy; assume 30 m |
| Noise and excess losses | Eqs.2–5 | Shannon SNR; assume 10^-13 W, 1/20 dB |
| LoS angle convention | Eq.4 | Arctan radians default; selectable degrees; retain slant denominator |
| Task-size notation | Eq.6 | Printed distance/rate has wrong units; use task bits |
| Chip gamma and Eq.9 d | II-B | Energy needs gamma; assume 10^-28, total cycles interpretation; alternatives implemented |
| Q2, mass, S, d0 | II-C | Flight evaluation; Q2=0 W, mass=W/9.81, S=.05 m², d0=.6 |
| Horizontal acceleration term | Eq.11 | Printed c3*a*v² produces very large deployment costs; default force_balance uses c3*a, printed selectable |
| Vertical radical, descent sign | Eqs.12–13 | Dimensionally inconsistent; preserve printed nesting/sign; values conditional, no physical validation claim |
| Deadline | P1/P2, Algorithm 2 | Needed for capacity and success; assume 1 s, not inferred from 70 users/5 UAV statement |
| Arrival probability | IV-A | Binary random law unspecified; Bernoulli .5 |
| MB convention and distributions | IV-A | Assume decimal MB; independent uniform sizes and cycles |
| Task timing within 5 min | II and Fig.3 | Assume slot-boundary batch arrival; CPU and radio serial per UAV; 5-min demand sampling is not a 5-min task deadline |
| Expired tasks | Algorithm 3 | Drop at deadline, record remaining work; generic engine retains tasks crossing a slot if deadline allows |
| Coverage, spectrum sharing | II-A and greedy description | No radius/interference scheduler; full-area orthogonal links |
| Fractional av / <= | Algorithm 3 | Floor av and keep printed <=; guarantees unique assignment but not exact equal loads |
| Fixed UAV inclusion | III-B1 vs Fig.2 | Optimize N−1 movable centers; all N serve tasks, including fixed center; Fig.2 visual does not clearly obey fixed-center statement |
| New center initialization | Algorithm 1/2 | Golden-angle offsets 80 m from base avoid coincident starts; thereafter current centers |
| BP data, split, width, activation | Algorithm 2, IV-B/Figs.3–4 | Synthetic 28 days; first 80% dates train; remaining dates hold out; three-layer 3→24→1 tanh/linear, 800 epochs, minibatch 128, lr=.01 |
| BP inputs/horizon/target | Algorithm 2 | (date,slot,current count)→next-slot count; convert to expected cycles. Date encoded as day index; no holidays/weather |
| Synthetic curve | Fig.3 | Piecewise linear knots plus independent daily-amplitude and count noise; parameters in config; not digitized or claimed original data |
| BP SGD/RMSProp defaults | Fig.4 | Equal starting weights/data/shuffles; Adam .9/.999, RMSProp .9, epsilon 10^-8, all lr=.01 |
| beta initialization and offer refresh | Algorithm 2 | Initialize zero, reset on count change, recompute capacity each loop, never remove fixed role |
| Moving service geometry | III-B2 | Target positions used while moving; new aircraft serve after arrival; old aircraft covers replacement rendezvous; no continuous in-flight radio geometry |
| Replacement monitoring | III-B2 | Continuous hover EAlert checks between demand samples; task processing batch charged at start of slot; operating-power estimates use preceding observed service |
| Handoff | Algorithms 2–3 | Retain remaining cycles; restart upload when task assigned to another aircraft; replaced role inherits queue |
| Fleet limit | No limit specified; V future work | 64 guard raises error rather than silently dropping requests; unlimited fresh reserve aircraft |
| Baseline resource enumeration | IV-B Fig.5 | Exhaustive positive count scan using actual task cycles and strict P1; compute-only bound, not latency oracle |
| Allocation enumeration | IV-B Fig.7 | Literal exhaustive for small cases; analytic exact count optimum for large cases, ignores geography. Not exhaustive full discrete P2 optimization |
| Short battery comparison | IV-B Figs.8–9 | 60 slots, 70 persistent positions, five stationary UAVs; all assigned work completes even when late; flight excluded as source specifies |

The horizontal operational repair does not resolve the vertical dimensional
problem. The two modes are useful for sensitivity and debugging, not evidence
that the paper's aircraft can execute these missions. Default experiments do
not establish safety, optimality, QoS guarantees, or real-world battery life.
