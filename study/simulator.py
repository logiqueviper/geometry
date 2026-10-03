"""Discrete-event scheduling with explicit ownership and serialized link traffic.

All times are milliseconds. The master is node -1. Independent directed links
are full duplex. Optional shared NICs serialize a node's send and receive streams.
Control traffic, data, and results share the same link queues. Runtime is opaque
to every scheduler. Only queued (never running) tasks can migrate.
"""
from collections import deque
from dataclasses import dataclass, asdict
import heapq
import math
import numpy as np
from .geometry import geometry

POLICIES = ("static", "neighbor_push", "neighbor_steal", "global_steal", "central_rebalance", "central_queue", "guided_queue")

@dataclass(frozen=True)
class Config:
    latency_ms: float = .01
    bandwidth_mib_s: float = 100.
    task_bytes: int = 4096
    result_bytes: int = 64
    control_bytes: int = 32
    split: float = .5
    batch_cap: int = 0  # zero means uncapped half-queue donation
    shared_nic: bool = False
    master_service_ms: float = 0.
    retry_ms: float = 1.

@dataclass(frozen=True)
class Routed:
    source: int
    payload: object

class Simulation:
    def __init__(self, solid, policy, costs, seed=0, config=Config(), audit=False, peer_edges=None):
        if policy not in POLICIES:
            raise ValueError(policy)
        self.solid, self.policy, self.costs, self.config = solid, policy, np.asarray(costs), config
        assert len(costs) > 0 and np.all(self.costs > 0)
        _, _, self.adj = geometry(solid)
        self.n = len(self.adj)
        if peer_edges is not None:
            self.adj = {i:[] for i in range(self.n)}
            for i,j in peer_edges:
                assert i != j and 0 <= i < self.n and 0 <= j < self.n
                self.adj[i].append(j);self.adj[j].append(i)
            for ns in self.adj.values():ns.sort()
        assert len(costs) % self.n == 0, "Equal initial task counts required"
        self.rng = np.random.default_rng(seed)
        self.q = [deque() for _ in range(self.n)]
        self.current = [None]*self.n
        self.waiting = [None]*self.n
        self.idle = [False]*self.n
        self.epoch = [0]*self.n
        self.known_idle = [dict() for _ in range(self.n)]
        self.visited = [set() for _ in range(self.n)]
        self.pool = deque()
        self.reserved = {}
        self.token = 0
        self.events = []
        self.seq = 0
        self.t = 0.
        self.link_free = {}
        self.tx_free = {}; self.rx_free = {}
        self.master_free = 0.
        self.messages = self.bytes = self.master_messages = self.migrated = 0
        self.compute_finish = 0.
        self.started = set(); self.finished = set(); self.received = set()
        self.audit = audit
        self.trace = []
        self.in_transit = set()

    def event(self, at, callback, *args):
        self.seq += 1
        heapq.heappush(self.events, (at, self.seq, callback, args))

    def send(self, source, target, kind, payload=None, size=None):
        """Store-and-forward through master for nonadjacent worker communication."""
        if source >= 0 and target >= 0 and target not in self.adj[source]:
            self.hop(source, -1, kind, payload, size, final=target)
        else:
            self.hop(source, target, kind, payload, size)

    def hop(self, source, target, kind, payload, size, final=None):
        c = self.config
        size = c.control_bytes if size is None else size
        start = max(self.t, self.link_free.get((source,target), 0.))
        if c.shared_nic:
            start = max(start, self.tx_free.get(source,0.), self.rx_free.get(target,0.))
        end = start + size / (c.bandwidth_mib_s * 2**20 / 1000)
        self.link_free[source,target] = end
        if c.shared_nic:
            self.tx_free[source] = end; self.rx_free[target] = end
        self.messages += 1; self.bytes += size
        if source == -1 or target == -1:
            self.master_messages += 1
        self.event(end+c.latency_ms, self.arrival, source, target, kind, payload, size, final)

    def arrival(self, source, target, kind, payload, size, final):
        if target == -1 and self.config.master_service_ms:
            at = max(self.t, self.master_free) + self.config.master_service_ms
            self.master_free = at
            self.event(at, self.deliver, source, target, kind, payload, size, final)
        else:
            self.deliver(source, target, kind, payload, size, final)

    def deliver(self, source, target, kind, payload, size, final):
        if final is not None:
            self.hop(-1, final, kind, Routed(source,payload), size)
            return
        if isinstance(payload, Routed):
            source,payload = payload.source,payload.payload
        if kind == "RESULT":
            assert payload in self.finished and payload not in self.received
            self.received.add(payload)
        elif kind == "DATA":
            self.in_transit.difference_update(payload)
            self.q[target].extend(payload); self.waiting[target] = None
            self.visited[target].clear()
            self.activate(target)
        elif kind == "IDLE":
            self.known_idle[target][source] = payload
            self.offer(target)
        elif kind == "BUSY":
            if self.known_idle[target].get(source, -1) <= payload:
                self.known_idle[target].pop(source, None)
        elif kind == "OFFER":
            token, epoch = payload
            if self.idle[target] and self.waiting[target] is None and self.epoch[target] == epoch:
                self.waiting[target] = token
                self.send(target, source, "ACCEPT", token)
            else:
                self.send(target, source, "REJECT", token)
        elif kind in ("ACCEPT", "REJECT"):
            donor, receiver, ids = self.reserved.pop(payload)
            assert donor == target and receiver == source
            if kind == "ACCEPT":
                self.migrated += len(ids); self.data(donor, receiver, ids)
            else:
                self.q[donor].extend(ids); self.activate(donor)
        elif kind == "STEAL":
            ids = self.take(target)
            if ids:
                self.migrated += len(ids); self.data(target, source, ids)
            else:
                self.send(target, source, "REPLY", False)
        elif kind == "REPLY":
            self.waiting[target] = None
            self.request(target)
        elif kind == "PROBE":
            receiver, candidates = payload
            ids = self.take(target)
            if ids:
                self.migrated += len(ids)
                self.send(target, -1, "REBALANCED", (receiver, ids), self.config.control_bytes + len(ids)*self.config.task_bytes)
                self.in_transit.update(ids)
            else:
                self.send(target, -1, "PROBE_EMPTY", (receiver, candidates))
        elif kind == "REBALANCED":
            receiver, ids = payload
            self.hop(-1, receiver, "DATA", ids, self.config.control_bytes+len(ids)*self.config.task_bytes)
        elif kind == "PROBE_EMPTY":
            self.probe(*payload)
        elif kind == "REQUEST":
            if self.policy == "central_rebalance":
                candidates = [i for i in range(self.n) if i != source]
                self.rng.shuffle(candidates); self.probe(source, candidates)
            elif self.pool:
                k = 1 if self.policy == "central_queue" else max(1, math.ceil(len(self.pool)/(2*self.n)))
                ids = [self.pool.popleft() for _ in range(min(k,len(self.pool)))]
                self.data(-1, source, ids)
            else:
                self.send(-1, source, "STOP")
        elif kind == "STOP":
            if self.policy == "central_rebalance":
                self.waiting[target] = None
                self.event(self.t+self.config.retry_ms,self.retry,target)
            else:
                self.waiting[target] = "stopped"
        else:
            raise AssertionError(kind)

    def data(self, source, target, ids):
        self.in_transit.update(ids)
        self.send(source, target, "DATA", ids, self.config.control_bytes+len(ids)*self.config.task_bytes)

    def take(self, donor):
        size = math.ceil(len(self.q[donor])*self.config.split)
        if self.config.batch_cap:
            size = min(size, self.config.batch_cap)
        return [self.q[donor].pop() for _ in range(size)]

    def activate(self, worker):
        if self.q[worker] and self.current[worker] is None:
            if self.idle[worker]:
                self.idle[worker] = False
                if self.policy == "neighbor_push":
                    for j in self.adj[worker]:
                        self.send(worker, j, "BUSY", self.epoch[worker])
            task = self.q[worker].popleft()
            assert task not in self.started
            self.started.add(task); self.current[worker] = task
            if self.audit: self.trace.append((self.t, "start", task, worker))
            self.event(self.t+self.costs[task], self.complete, worker, task)
        if self.current[worker] is None and not self.q[worker] and not self.idle[worker]:
            self.idle[worker] = True; self.epoch[worker] += 1
            if self.policy == "neighbor_push":
                for j in self.adj[worker]:
                    self.send(worker, j, "IDLE", self.epoch[worker])
            elif self.policy not in ("static",):
                self.request(worker)
        if self.policy == "neighbor_push": self.offer(worker)

    def complete(self, worker, task):
        assert self.current[worker] == task and task not in self.finished
        self.finished.add(task); self.current[worker] = None
        self.compute_finish = self.t
        if self.audit: self.trace.append((self.t,"finish",task,worker))
        self.send(worker, -1, "RESULT", task, self.config.result_bytes)
        self.activate(worker)

    def offer(self, donor):
        if self.current[donor] is None: return
        candidates = list(self.known_idle[donor]); self.rng.shuffle(candidates)
        for receiver in candidates:
            if not self.q[donor]: break
            epoch = self.known_idle[donor].pop(receiver)
            ids = self.take(donor)
            self.token += 1
            self.reserved[self.token] = (donor,receiver,ids)
            self.send(donor,receiver,"OFFER",(self.token,epoch))

    def request(self, worker):
        if self.waiting[worker] is not None: return
        if self.policy in ("central_queue","guided_queue","central_rebalance"):
            self.waiting[worker] = "master"
            self.send(worker,-1,"REQUEST")
        elif self.policy in ("neighbor_steal","global_steal"):
            possible = self.adj[worker] if self.policy == "neighbor_steal" else [i for i in range(self.n) if i != worker]
            candidates = [i for i in possible if i not in self.visited[worker]]
            if candidates:
                donor = int(self.rng.choice(candidates)); self.visited[worker].add(donor)
                self.waiting[worker] = donor; self.send(worker,donor,"STEAL")
            else:
                self.event(self.t+self.config.retry_ms,self.retry,worker)

    def retry(self, worker):
        if self.current[worker] is None and not self.q[worker] and self.waiting[worker] is None:
            self.visited[worker].clear(); self.request(worker)

    def probe(self, receiver, candidates):
        if candidates:
            donor = candidates.pop()
            self.send(-1,donor,"PROBE",(receiver,candidates))
        else:
            self.send(-1,receiver,"STOP")

    def assert_ownership(self):
        ids = list(self.pool) + list(self.in_transit) + list(self.finished)
        ids += [i for q in self.q for i in q]
        ids += [i for i in self.current if i is not None]
        ids += [i for _,_,batch in self.reserved.values() for i in batch]
        assert len(ids) == len(self.costs) and len(set(ids)) == len(ids), "Lost or duplicated ownership"

    def run(self):
        order = list(range(self.n)); self.rng.shuffle(order)
        if self.policy in ("central_queue","guided_queue"):
            self.pool = deque(range(len(self.costs)))
            for i in order:
                self.idle[i] = True; self.request(i)
        else:
            for chunk_index, i in enumerate(order):
                ids = list(range(chunk_index*len(self.costs)//self.n,(chunk_index+1)*len(self.costs)//self.n))
                self.data(-1,i,ids)
        while self.events:
            self.t,_,callback,args = heapq.heappop(self.events)
            callback(*args)
            if self.audit: self.assert_ownership()
            if len(self.received) == len(self.costs):
                break  # makespan: last result collected, no artificial polling drain
        assert len(self.finished) == len(self.received) == len(self.costs)
        assert len(self.started) == len(self.costs)
        lower = max(float(self.costs.sum())/self.n, float(self.costs.max()))
        assert self.t+1e-8 >= lower
        return {"makespan_ms":self.t, "compute_finish_ms":self.compute_finish,
                "utilization":float(self.costs.sum())/(self.n*self.t),
                "lower_bound_ms":lower, "messages":self.messages,"bytes":self.bytes,
                "master_messages":self.master_messages, "migrated_tasks":self.migrated,
                "executed":len(self.finished), "collected":len(self.received)}

def workload(kind, tasks, seed):
    rng = np.random.default_rng(seed)
    if kind == "constant": costs = np.ones(tasks)
    elif kind == "exponential": costs = rng.exponential(1., tasks)
    elif kind in ("lognormal", "clustered"):
        sigma = np.sqrt(np.log(5))  # population CV=2
        costs = rng.lognormal(-sigma*sigma/2, sigma, tasks)
        if kind == "clustered": costs.sort()
    elif kind == "pareto": costs = np.minimum(rng.pareto(1.5,tasks)+1, 100)
    else: raise ValueError(kind)
    return costs / costs.mean()  # exactly tasks ms total work for every instance
