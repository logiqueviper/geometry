# Prototype runbook draft — human equipment required

This runbook prepares the next stage; there is no deployed prototype, calibrated
simulator, finalized bill of materials, or measured price in this repository.
The full experiment harness is a later gated implementation step.

1. Inventory available boards, identical worker count, master, interface count,
   and switch/VLAN support. Approve wiring and any purchases before spending.
   A direct-edge design requires peer degree plus one interface per worker:
   4 (tetrahedron/cube/dodecahedron), 5 (octahedron), or 6 (icosahedron).
   USB adapters may share a bus, so interface count does not prove independent
   bandwidth. The master also needs the specified aggregate spoke capacity.
2. Choose direct physical links or VLAN-emulated logical edges. A switch on one
   physical port per node implements a shared NIC, not independent per-edge
   transmitters. Bind traffic to the intended VLAN/interface; reject accidental
   nonadjacent worker routes. Document the real switch contention model.
3. Generate and review edge lists from `study/geometry.py`; use the same graph
   hash in simulation and hardware logs. Peer subnet/VLAN IDs and port maps must
   be generated and reviewed for the selected vendor equipment before applying
   privileged configuration commands. No generic command is assumed to work
   on an unspecified switch.
4. Install the same OS/software image; record kernel, CPU governor, core pinning,
   MTU, background load, and temperatures. Validate task outputs and ID manifests
   before timing a scheduler. Do not change the cloud machine's system settings.
5. Collect per-link message-size latency/throughput samples and simultaneous-edge
   samples; include at least 10,000 latency observations per planned link regime.
   Measure per-message CPU overhead and each node's application task distribution.
6. Fit simulator parameters on the declared calibration configurations only.
   Freeze the fit before validation. Keep calibration and validation IDs disjoint.
7. Run warm-ups explicitly marked `warmup`, then at least twenty repetitions per
   hardware cell in a saved randomized order. Log rest periods and temperatures.
   Record every failed run and its reason before evaluating exclusion effects.
8. Return raw CSV/JSONL and environment fingerprints using `DATA_SCHEMA.md`.
   Compute MAPE, RMSE, maximum error, and scheduler-rank correlation on validation
   configurations. A 5% target is a target, not a result or guarantee.

Cloud-only loopback/emulated execution can test protocol behavior but cannot
stand in for link/CPU calibration or physical-cluster validation.
