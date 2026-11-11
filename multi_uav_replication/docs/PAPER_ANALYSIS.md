# Phase 1–3: source extraction and implementation plan

Source: Guo, Zhou, Wang & Liu, IEEE IoT Journal 9(19), 18725–18736,
DOI 10.1109/JIOT.2022.3161703. All twelve PDF pages were read. Equations
(9)–(18) and Table I were also inspected in rendered PDF pages because text
extraction loses radicals, superscripts and table contents. Source annotations
are not executable instructions. Analysis completed before implementation.

## Verified system and parameters

Section II, pp.18727–28: homogeneous UAV servers, ground-device position and
binary task arrival per slot; full task offload; initially one fixed center UAV.
Section III-B1: optimize only movable UAV centers; c=N−1. Section III-B2:
vertical climb then horizontal travel; moving UAVs can still serve tasks.
Section IV-A and Table I (pp.18731–32): 500×500 m area, task data 0.5–1 MB,
50–150 Mcycles/task, UAV 1 GHz, receive/communication power 1 W, full battery
500 kJ, bandwidth 1 MHz, ground transmit power 30 dBm=1 W, acceleration
5 m/s², speed limit 30 m/s, weight 20 N, air density 1.225 kg/m³,
rotor radius 0.4 m, solidity 0.05 (text), profile drag 0.012,
angular speed 300 rad/s, induced correction 0.1. Section II-A specifies
LoS a=4.88, b=0.43. Table I leaves N,M,T blank. Fig.3 caption specifies 288
samples in 24 h, 5 min apart. Fig.2: 70 users and 2,3,4 UAVs. Figs.8–9:
70 users and 5 UAVs. Fig.6 includes fixed four UAVs.

**2 GHz requested by the user is not verified in this PDF.** Neither are flight
height, deadline, noise, excess losses, chip coefficient, body mass, equivalent
plate area, fuselage drag ratio, Q2, fuzzy exponent/tolerance/iteration cap,
coverage radius, data trace, activation, hidden width, learning rates or epochs.

## Equation inventory and dimensional issues

| Eq. | Source expression / role | Code destination |
|---|---|---|
|1|d=sqrt((xu−xm)²+(yu−ym)²+h²), m|communication_model.distance|
|2–3|20log10(4πfc d/c)+excess loss, dB|communication_model.path_losses|
|4|1/[1+a exp(−b(arctan(h/d)−a))]|communication_model.los_probability|
|5|B log2(1+pW 10^(−Lavg/10)/noiseW), bit/s|communication_model.rate|
|6|d_m,n / rate (printed numerator conflicts with task-size notation)|communication_model.transmission_time|
|7|tcomm pcomm, J|communication_model.communication_energy|
|8|cycles/frequency, s|computation_model.computation_time|
|9|gamma cycles d_m,n f² (printed d is ambiguous)|computation_model.computation_energy|
|10|(Q0+Q1)t; Q0=δρsAΩ³R³/8; Q1=(1+k)W^1.5/(sqrt(2)*sqrt(2ρA))|energy_model.hover_power|
|11|horizontal-flight integral; complete nested roots transcribed in MATHEMATICS.md|energy_model.horizontal_power, flight|
|12–13|vertical integrals with undefined Q2 and dimensionally problematic nested radical|energy_model.vertical_power, flight|
|14|min sum active; binary p,lambda; sum cycles*lambda < tmax sum f*p|baseline_methods.minimum_count, objectives.p1_feasible|
|15|printed queue variance with apparent n/x index typo; delay and safe landing constraints|objectives.load_variance, constraints|
|16|G=sum u^eta tau; tau=1/||Lu−Lm||^(−2)=squared slant distance|ls_fcm.objective|
|17|center=sum u^eta L / sum u^eta|ls_fcm.fit|
|18|u=1/sum_k(tau_n/tau_k)^(2/(eta−1))|ls_fcm.membership|

Eq.4 uses slant distance rather than horizontal range; angle units unspecified.
Literal mode uses radians, as NumPy arctan returns. Optional degrees is a
sensitivity, not a correction claimed to be original. Eq.6 cannot divide meters
by bit/s to get seconds: executable interpretation uses task bits. Eq.9 defaults
to cycles*f²*gamma (cycles are total cycles, as in Eq.8 and Table I); alternative
literal-distance and data-multiplied interpretations are explicit config modes.
Literal-distance gamma must have units J s²/(cycle m), rather than standard
J s²/cycle; there is no source value to distinguish interpretations.
Eq.10's extra sqrt(2) is preserved. Eq.12–13 contain sqrt(v²+sqrt(2(W∓ma)ρA)),
which adds quantities of incompatible units. Literal formulas are implemented
and flagged as dimensional failures, not silently repaired. Missing Q2 is set
by an explicit assumption. Flight energy therefore is **conditional numerical
evaluation**, not a validated physical prediction. P2 is a discrete assignment
problem despite the paper calling it convex. We use conventional variance
(sum queue lengths with x indexing), documenting the printed typo.

## Algorithm extraction and mapping

1. Algorithm 1, p.18730: initialize from current movable UAV locations; compute
membership (18); update centers (17); evaluate G (16) with old membership;
update membership; stop on |delta G|≤kappa or iteration limit. Keep fixed UAV
out of the updates. Eq.18 is retained even though its exponent does not minimize
Eq.16 with squared tau. Consequently monotone convergence is not guaranteed.
New UAV initial horizontal coordinates are unspecified: deterministic distinct
points around launch center are an assumption to avoid identical centers.
2. Algorithm 2, p.18730: initialize fixed UAV, train BP; check EAlert replacement;
reset beta on user count change; predict needed cycles; add while need/offer>
tmax; remove least battery movable UAV while need/(offer−f)<tmax and beta=0;
if previous success<1 and alpha=0 add and set beta; recluster on change;
allocate (Algorithm 3); update energy, location, queues and success.
EAlert=hover(tfly)+comm(tfly)+compute(tfly)+landing. Preserve one fixed role even
when its physical aircraft is replaced. coffer must be recomputed inside loops
although omitted in pseudocode; beta initialization missing, assumed zero.
Line 8's model(d,t,a) conflicts with historical S=(date,time,count). We train a
three-layer BP regressor for next-slot count from date,time,current count, then
multiply predicted count by expected cycles*arrival probability. Training is
synthetic, held out by date, not the undisclosed source dataset. Adam chosen in
Section IV-B; SGD and RMSProp trained on identical splits and initial weights.
3. Algorithm 3, p.18731: preassign new tasks by fuzzy cluster; retain earlier
queues first; compute av; retain first av tasks, pool excess; underfull UAVs
choose nearest pooled task; sort by arrival slot. av rounding is not specified;
use floor. Printed `<=av` is retained (so one extra task is possible). Old tasks
are preferentially retained, not unconditionally pinned. All tasks remain unique.

## Experiments and baselines

Figs.2–9: clustering; actual vs predicted demand; loss across SGD/RMSProp/Adam;
active UAV counts proposed vs resource enumeration; failure fixed-four vs
prediction-only vs MNEEA; queue SD proposed/greedy/enumeration; five-UAV loads;
five-UAV communication+compute battery curves **excluding flight**, as source.
Greedy: nearest UAV with available resources (p.18733). Enumeration count:
exhaustive scan for Eq.14. Assignment enumeration: exhaustive small-case
search plus exact balanced-count optimum by quotient/remainder for large M,
ignoring geography, as described on pp.18733–34. This is explicitly an exact
count optimum, not a claim to execute N^M enumeration at M=70.

Evaluation will export all generated numerical data, events and configuration.
No original numeric trace or reference implementation is supplied; no generated
curve may be labeled an exact reconstruction of the reported measurements.
