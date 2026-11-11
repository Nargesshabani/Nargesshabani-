# Mathematical transcription

The inventory in PAPER_ANALYSIS.md maps every numbered equation. SI units at
module boundaries: meters, seconds, joules, bits, cycles, Hz, watts. MB=10^6
bytes (assumption); dBm converted to watts before Shannon's formula. No
inter-UAV interference is specified; orthogonal links are assumed. CPU is a
single serial server at fixed 1 GHz; no frequency optimizer is in this paper.

Let v be speed and a signed acceleration along travel. Define A=πR²,
c1=3/(Ω²R²), c2=ρS/(2W), c3=mass/W, c4=ρA/W, c5=d0ρsA/2.
The paper's Eq.11 horizontal power is:

    q = c2*v² + c3*a*v²
    P = Q0*(1+c1*v²) + Q1*sqrt(1+q²)
        *sqrt(sqrt(1+q²+c4²*v⁴)-c4*v²) + c5*v³

Eq.12/13, verbatim nested radical, with z=W−mass*a for climb and
z=W+mass*a for descent:

    P = Q2 + z*v/2 + z/2*sqrt(v²+sqrt(2*z*ρ*A))

The plus Wv term in descent is preserved; do not infer physically correct
regenerative/descent behavior from it. Q2 is undefined. Code checks z≥0 and
does not silently clip invalid thrust. Motion uses an accelerate/coast/decelerate
profile. For distance L<Vmax²/a, peak speed is sqrt(L*a); otherwise Vmax.
Integrals use Gaussian quadrature per acceleration segment, independently of
the 300 s demand sampling. Hover duration excludes moving time so energy is
not double counted. Launch climbs then flies horizontally, return flies to
base then descends. Existing aircraft serve during rendezvous; newborn service
begins at rendezvous, an explicit conservative interpretation of moving service.

P1 is checked with strict `<` as printed; Algorithm 2's entry loop instead uses
`>` as printed, so exact equality differs. P2 uses queue-length variance;
constraints expose per-task delay and landing reserve feasibility. Proposed
Algorithms 1–3 are heuristics, not certified solutions of the discrete P2.

## Operational horizontal mode

An independent test of the literal Eq.11 under configured aircraft parameters
showed deployment energy above full battery for some paths. Default experiments
therefore use `horizontal_mode='force_balance'`: q=c2*v²+c3*a. This removes the
v² multiplying mass*acceleration/weight; it is an explicit dimensional repair,
not an original paper specification. `horizontal_mode='printed'` preserves the
transcription above. Vertical formulas remain literal in both modes. See
ASSUMPTIONS.md; source and operational modes must not be conflated.

## Literal P2 diagnostic

`objectives.printed_p2` also evaluates the repeated n inside the printed sum
verbatim. With N active UAVs, the sum over x becomes N*len(queue_n), and each
residual is zero. It therefore cannot express load imbalance as printed.
`load_variance` is the explicitly interpreted objective used for diagnostics.
The report includes numerical examples in p2_notation_audit.csv. Similarly,
`transmission_numerator='printed_distance'` reproduces Eq.6 numerically while
having invalid units. Default task_bits mode is the stated interpretation.
C5 is checked against **current** battery: the printed p_energy notation is
introduced as initial energy in Section II, making a literal initial-energy
check insufficient for battery safety.
