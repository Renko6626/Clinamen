"""Profile larger bullet sets with the production PPO rollout and update paths.

Each invocation runs one fresh process and records phase timing, load, and memory.
This is a performance probe; short random-initialized runs do not tune learning.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import statistics
import time


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def resources() -> dict:
    files = ["cpu.max", "cpu.stat", "cpuset.cpus.effective", "memory.max", "memory.current"]
    result = {"affinity": sorted(os.sched_getaffinity(0)), "cgroup": {}}
    for name in files:
        path = Path("/sys/fs/cgroup") / name
        if path.exists():
            result["cgroup"][name] = path.read_text().strip()
    for name in ["cpu.cfs_quota_us", "cpu.cfs_period_us", "cpu.stat"]:
        path = Path("/sys/fs/cgroup/cpu") / name
        if path.exists():
            result["cgroup"]["v1/" + name] = path.read_text().strip()
    return result


def cpu_limit(info: dict, advertised: float) -> int:
    limits = [float(len(info["affinity"])), advertised]
    cg = info["cgroup"]
    if "cpu.max" in cg:
        quota, period = cg["cpu.max"].split()
        if quota != "max":
            limits.append(int(quota) / int(period))
    elif int(cg.get("v1/cpu.cfs_quota_us", "-1")) > 0:
        limits.append(int(cg["v1/cpu.cfs_quota_us"]) / int(cg["v1/cpu.cfs_period_us"]))
    return max(1, math.floor(min(limits)))


def run_trial(args) -> None:
    import psutil
    import torch
    from stgtrain.cards import configured_cards, start_intent_mixes
    from stgtrain.config import load_config, dump_toml
    from stgtrain.envwrap import EnvWrapper
    from stgtrain.episodes import EpisodeTracker
    from stgtrain.perf import PhaseTimer, PerfWriter, LoadSampler, machine_info, PHASES
    from stgtrain.metrics import summarize_episodes
    from stgtrain.ppo import PPO
    from stgtrain.reward import RewardFn
    from stgtrain.train import build_components

    args.out.mkdir(parents=True, exist_ok=False)
    setup_start = time.perf_counter()
    cfg = load_config(args.config, {"env": {"threads": args.threads}, "run": {"total_updates": args.updates}})
    torch.set_num_threads(2)
    torch.manual_seed(cfg["run"]["seed"])
    if not torch.cuda.is_available():
        raise RuntimeError("A visible CUDA GPU is required")
    device = torch.device("cuda")
    dump_toml(cfg, args.out / "config.toml")
    images, starts, _, feats, factory = build_components(cfg, device)
    ppo = PPO(cfg, factory, device)
    initial = {"kind": "random", "performance_probe_only": True}
    mixes = start_intent_mixes(configured_cards(cfg["env"]), starts, cfg["intent"]["mix"], False)
    env = EnvWrapper(cfg, images, starts, device, seed=cfg["run"]["seed"], start_intent_mixes=mixes)
    reward = RewardFn(cfg)
    tracker = EpisodeTracker(env.n, device, list(reward.terms), cfg["reward"]["hold_radius"],
                             cfg["reward"]["edge_margin"], cfg["env"]["frame_skip"], cfg["intent"]["interval"][1])
    timer = PhaseTimer(5, device)
    writer = PerfWriter(args.out / "perf.jsonl")
    sampler = LoadSampler(writer, 1.0)
    proc = psutil.Process()
    write_json(args.out / "machine.json", {"machine": machine_info(), "resources": resources(), "initial": initial})
    observations = env.reset()
    torch.cuda.synchronize()
    setup_s = time.perf_counter() - setup_start
    frames = cfg["env"]["num_envs"] * cfg["ppo"]["num_steps"] * cfg["env"]["frame_skip"]
    rows, phases = [], []
    before = resources()
    steady_before = None
    sampler.start()
    started = time.perf_counter()
    try:
        with (args.out / "iterations.jsonl").open("w") as stream:
            for update in range(1, args.updates + 1):
                timer.start_iteration(update)
                tick = time.perf_counter()
                cpu0 = sum(proc.cpu_times()[:2])
                observations, batch, next_value = ppo.rollout(env, feats, reward, tracker, timer, observations)
                with timer.phase("update"):
                    stats = ppo.train_step(batch, next_value, update, args.updates, timer=timer)
                finished = tracker.pop_finished()
                summarize_episodes(finished, "ep/")
                torch.cuda.synchronize()
                elapsed = time.perf_counter() - tick
                if not all(math.isfinite(float(v)) for v in stats.values()):
                    raise RuntimeError("Non-finite PPO statistic")
                row = {"update": update, "seconds": elapsed, "sps": frames / elapsed,
                       "profiled": update % 5 == 0, "wall": time.perf_counter() - started,
                       "process_cpu_cores": (sum(proc.cpu_times()[:2]) - cpu0) / elapsed}
                rows.append(row)
                stream.write(json.dumps(row) + "\n")
                stream.flush()
                phase = timer.pop_iteration()
                if phase is not None:
                    phase.update(kind="phase", update=update)
                    writer.write(phase)
                    phases.append(phase)
                print(json.dumps(row), flush=True)
                if update == 10:
                    steady_before = resources()
    finally:
        sampler.stop()
        writer.close()
        write_json(args.out / "resources-after.json", {"before": before, "steady_before": steady_before, "after": resources()})
    # Profiling inserts synchronizations. Keep those iterations out of normal throughput.
    steady = [r for r in rows if r["update"] > 10 and not r["profiled"]]
    steady_phases = [r for r in phases if r["update"] > 10]
    sps = frames * len(steady) / sum(r["seconds"] for r in steady)
    phase_seconds = {p: statistics.mean(r.get(p + "_s", 0) for r in steady_phases) for p in PHASES}
    phase_total = statistics.mean(r["total_s"] for r in steady_phases)
    summary = {"k_bullets": cfg["featurize"]["k_bullets"], "layers": cfg["model"]["joint_sa_layers"], "num_minibatches": cfg["ppo"]["num_minibatches"], "minibatch_samples": frames // cfg["ppo"]["num_minibatches"], "training_starts": len(starts), "parameters": sum(p.numel() for p in ppo.agent.parameters()), "max_torch_reserved_GiB": torch.cuda.max_memory_reserved()/2**30, "threads": args.threads, "updates": args.updates, "setup_s": setup_s,
               "trial_wall_s": time.perf_counter() - started, "steady_iterations": len(steady),
               "steady_sps": sps, "steady_median_sps": statistics.median(r["sps"] for r in steady),
               "warmup_first_10_s": sum(r["seconds"] for r in rows[:10]),
               "process_cpu_cores": statistics.mean(r["process_cpu_cores"] for r in steady),
               "phase_seconds": phase_seconds, "phase_fraction": {p: t / phase_total for p, t in phase_seconds.items()},
               "phase_profile_total_s": phase_total, "load_summary_including_warmup": sampler.summary(),
               "max_torch_allocated_GiB": torch.cuda.max_memory_allocated() / 2**30,
               "hourly_usd": args.hourly, "hours_per_billion_frames": 1e9 / sps / 3600,
               "usd_per_billion_frames": args.hourly * 1e9 / sps / 3600,
               "samples_are_learning_evidence": False}
    write_json(args.out / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description="K128/K256 production PPO performance probe; no learning claims.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=30)
    parser.add_argument("--updates", type=int, default=30)
    parser.add_argument("--hourly", type=float, required=True)
    args = parser.parse_args()
    if args.updates < 20:
        parser.error("Need at least 20 updates including warmup")
    run_trial(args)

if __name__ == "__main__":
    main()
