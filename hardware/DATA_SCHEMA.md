# Hardware observation schema — prospective

No hardware observations exist yet. Store one `runs.csv` row per repetition and
one JSON-lines event file per run. Include failures; do not drop unfavorable runs.

Required run columns:

```
run_id,phase,topology,graph_hash,policy,workload,task_manifest_hash,task_count,
repetition,randomized_order_index,master_host,worker_count,start_monotonic_ns,
last_result_monotonic_ns,makespan_ms,executed_ids,collected_unique_ids,
duplicate_results,timeouts,retries,input_bytes,result_bytes,control_bytes,
kernel,python_version,git_commit,exit_status,excluded,exclusion_reason
```

`phase` is `warmup`, `calibration`, or `validation`. A master monotonic clock
measures last-result makespan; do not subtract unsynchronized worker wall clocks.
All IDs must match the manifest. Final unique-result correctness is separate from
exactly-once execution after a crash; re-execution can be necessary.

Event fields:
`run_id,node_id,monotonic_ns,event,task_id,attempt_id,peer,message_type,bytes`.
Events on different machines require a separately documented synchronization
error bound to interpret cross-node timing. Keep raw clocks and synchronization
metadata instead of silently correcting them.

Link microbenchmarks:
`measurement_id,phase,source,target,logical_edge,physical_port,message_bytes,
simultaneous_edge_count,repetition,rtt_us,throughput_mib_s,cpu_time_us,temperature_c`.
RTT/2 is an assumption for symmetric one-way latency, not a directly observed
one-way value. Keep individual samples, not only means or best throughput.

Hardware fingerprint JSON must identify node/board models, CPU governors, core
pinning, memory, interfaces/buses, switch model/firmware/VLAN map, cable lengths,
software versions, network MTU, and ambient/thermal/power logging capability.
