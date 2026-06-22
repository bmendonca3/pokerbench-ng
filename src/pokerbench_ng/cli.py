"""Command line interface for PokerBench-NG."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import sys
import time
from pathlib import Path

from pokerbench_ng.agents.protocol import AgentAction, AgentLegalAction, AgentRequest, AgentResponse
from pokerbench_ng.agents.subprocess_agent import SubprocessAgentAdapter
from pokerbench_ng.agents.validation import load_agent_manifest, validate_agent_manifest
from pokerbench_ng import __version__
from pokerbench_ng.bots.always_fold import AlwaysFoldBot
from pokerbench_ng.bots.call_check import CallCheckBot
from pokerbench_ng.bots.random_legal import RandomLegalBot
from pokerbench_ng.reporting.json_report import write_json_report
from pokerbench_ng.reporting.leaderboard import leaderboard_entry
from pokerbench_ng.reporting.markdown_report import write_markdown_report
from pokerbench_ng.rollout.match import run_match
from pokerbench_ng.rollout.scheduler import load_rollout_config, load_seed_manifest, seed_schedule
from pokerbench_ng.static.scorer import EvaluatedResponse, evaluate_static_spots
from pokerbench_ng.static.spots import load_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pokerbench-ng",
        description="Clean-room local-first benchmark for AI poker agents.",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    subparsers = parser.add_subparsers(dest="command")

    validate_agent = subparsers.add_parser(
        "validate-agent", help="Validate an agent manifest file."
    )
    validate_agent.add_argument("manifest", help="Path to agent.yaml or agent.json.")

    subparsers.add_parser("init-agent", help="Print a minimal agent manifest template.")
    eval_static = subparsers.add_parser("eval-static", help="Run static EV-loss evaluation.")
    eval_static.add_argument("--agent", required=True, help="Path to agent manifest.")
    eval_static.add_argument("--spots", required=True, help="Path to static spot JSONL.")
    eval_static.add_argument("--out-dir", default="reports", help="Output directory.")

    eval_rollout = subparsers.add_parser("eval-rollout", help="Run controlled rollout evaluation.")
    eval_rollout.add_argument("--agent", required=True, help="Path to agent manifest.")
    eval_rollout.add_argument("--config", required=True, help="Path to rollout config.")
    eval_rollout.add_argument("--hands", type=int, default=None, help="Override number of hands.")
    eval_rollout.add_argument(
        "--opponent",
        choices=sorted(_OPPONENTS),
        default="call_check",
        help="Fixed baseline opponent.",
    )
    eval_rollout.add_argument("--out-dir", default="reports", help="Metrics output directory.")
    eval_rollout.add_argument("--runs-dir", default="runs", help="Run-detail output directory.")

    eval_suite = subparsers.add_parser("eval-suite", help="Run the MVP static and rollout suite.")
    eval_suite.add_argument("--agent", required=True, help="Path to agent manifest.")
    eval_suite.add_argument("--suite", default="mvp_hunl", help="Suite id.")

    report = subparsers.add_parser("report", help="Render a Markdown report from metrics JSON.")
    report.add_argument("metrics", help="Path to metrics JSON.")
    report.add_argument("--out", default=None, help="Markdown output path.")

    leaderboard = subparsers.add_parser("leaderboard", help="Build a leaderboard entry from metrics JSON.")
    leaderboard.add_argument("metrics", help="Path to metrics JSON.")
    leaderboard.add_argument("--agent-name", default="unknown", help="Agent display name.")
    leaderboard.add_argument("--out", default=None, help="Leaderboard JSON output path.")
    return parser


def _print_agent_template() -> int:
    template = {
        "schema_version": "1.0",
        "agent": {
            "name": "ExampleAgent",
            "version": "0.0.1",
            "track_class": "agent",
            "entrypoint": "python agent.py",
        },
    }
    print(json.dumps(template, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    if args.command == "init-agent":
        return _print_agent_template()

    if args.command == "validate-agent":
        path = Path(args.manifest)
        manifest = load_agent_manifest(path)
        errors = validate_agent_manifest(manifest)
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        print(f"valid agent manifest: {path}")
        return 0

    if args.command == "eval-static":
        return _eval_static(args)

    if args.command == "eval-rollout":
        return _eval_rollout(args)

    if args.command == "eval-suite":
        if args.suite != "mvp_hunl":
            print(f"unknown suite: {args.suite}", file=sys.stderr)
            return 2
        static_status = _eval_static(
            argparse.Namespace(
                agent=args.agent,
                spots="src/pokerbench_ng/data/public_spots/dev.example.jsonl",
                out_dir="reports",
            )
        )
        rollout_status = _eval_rollout(
            argparse.Namespace(
                agent=args.agent,
                config="configs/mvp_hunl_rollout.yaml",
                hands=5,
                opponent="call_check",
                out_dir="reports",
                runs_dir="runs",
            )
        )
        return static_status or rollout_status

    if args.command == "report":
        metrics_path = Path(args.metrics)
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        out = Path(args.out) if args.out else metrics_path.with_suffix(".md")
        write_markdown_report(out, metrics)
        print(out)
        return 0

    if args.command == "leaderboard":
        metrics_path = Path(args.metrics)
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        entry = leaderboard_entry(metrics, args.agent_name)
        out = Path(args.out) if args.out else metrics_path.with_suffix(".leaderboard.json")
        write_json_report(out, entry)
        print(out)
        return 0

    parser.print_help()
    return 0


def _eval_static(args: argparse.Namespace) -> int:
    agent_manifest = Path(args.agent)
    adapter = _adapter_from_manifest(agent_manifest)
    spots = list(load_jsonl(Path(args.spots)))
    responses = []
    for index, spot in enumerate(spots):
        request = AgentRequest(
            schema_version="1.0",
            request_id=str(spot.get("spot_id", f"spot-{index}")),
            legal_actions=[AgentLegalAction.from_dict(action) for action in spot.get("legal_actions", [])],
            state={key: value for key, value in spot.items() if key not in {"policy", "legal_actions"}},
            metadata={"spot_index": index},
        )
        responses.append(_safe_agent_response(adapter, request))
    metrics = evaluate_static_spots(spots, responses)
    metrics["reproducibility"] = _reproducibility_metadata(
        agent_manifest,
        scoring_version="static_v1",
        inputs={"spots": Path(args.spots)},
    )
    run_id = _run_id("static")
    out_dir = Path(args.out_dir)
    metrics_path = out_dir / f"{run_id}.metrics.json"
    markdown_path = out_dir / f"{run_id}.md"
    leaderboard_path = out_dir / f"{run_id}.leaderboard.json"
    write_json_report(metrics_path, metrics)
    write_markdown_report(markdown_path, metrics)
    write_json_report(leaderboard_path, leaderboard_entry(metrics, _agent_name(agent_manifest)))
    print(metrics_path)
    print(markdown_path)
    print(leaderboard_path)
    return 0


def _eval_rollout(args: argparse.Namespace) -> int:
    agent_manifest = Path(args.agent)
    adapter = _adapter_from_manifest(agent_manifest)
    config = load_rollout_config(Path(args.config))
    requested_hands = args.hands or int(config.get("hands", 5))
    manifest_path = config.get("seed_manifest")
    if manifest_path and Path(manifest_path).exists():
        seeds = load_seed_manifest(Path(manifest_path))[:requested_hands]
        if len(seeds) < requested_hands:
            seeds = seeds + seed_schedule(requested_hands - len(seeds), start_seed=max(seeds or [0]) + 1)
    else:
        seeds = seed_schedule(requested_hands)
    opponent = _opponent_from_name(args.opponent)
    metrics = run_match(adapter, opponent, seeds)
    opponent_metadata = _opponent_metadata(args.opponent, opponent)
    metrics["opponent"] = opponent_metadata
    repro_inputs = {"config": Path(args.config)}
    if manifest_path and Path(manifest_path).exists():
        repro_inputs["seed_manifest"] = Path(manifest_path)
    metrics["reproducibility"] = _reproducibility_metadata(
        agent_manifest,
        scoring_version="rollout_v1",
        inputs=repro_inputs,
        seed_schedule=seeds,
        opponent=opponent_metadata,
    )
    run_id = _run_id("rollout")
    out_dir = Path(args.out_dir)
    runs_dir = Path(args.runs_dir)
    metrics_path = out_dir / f"{run_id}.metrics.json"
    markdown_path = out_dir / f"{run_id}.md"
    run_path = runs_dir / f"{run_id}.json"
    leaderboard_path = out_dir / f"{run_id}.leaderboard.json"
    write_json_report(metrics_path, metrics)
    write_json_report(
        run_path,
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "opponent": opponent_metadata,
            "reproducibility": metrics["reproducibility"],
            "hands": metrics.get("hands_detail", []),
        },
    )
    write_markdown_report(markdown_path, metrics)
    write_json_report(leaderboard_path, leaderboard_entry(metrics, _agent_name(agent_manifest)))
    print(metrics_path)
    print(run_path)
    print(markdown_path)
    print(leaderboard_path)
    return 0


def _adapter_from_manifest(path: Path) -> SubprocessAgentAdapter:
    manifest = load_agent_manifest(path)
    errors = validate_agent_manifest(manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    entrypoint = str(manifest["agent"]["entrypoint"])
    parts = shlex.split(entrypoint)
    if not parts:
        raise SystemExit("agent.entrypoint cannot be empty")
    if parts[0] in {"python", "python3"}:
        script = Path(parts[1])
        if not script.is_absolute():
            script = path.parent / script
        command = [sys.executable, str(script)] + parts[2:]
    else:
        command = parts
    return SubprocessAgentAdapter(command)


def _agent_name(path: Path) -> str:
    return str(load_agent_manifest(path).get("agent", {}).get("name", path.stem))


_OPPONENTS = {
    "always_fold": AlwaysFoldBot,
    "call_check": CallCheckBot,
    "random_legal": RandomLegalBot,
}


def _opponent_from_name(name: str) -> object:
    try:
        factory = _OPPONENTS[name]
    except KeyError as exc:
        raise SystemExit(f"unknown opponent: {name}") from exc
    if name == "random_legal":
        return factory(seed=17)
    return factory()


def _opponent_metadata(name: str, opponent: object) -> dict[str, str]:
    return {
        "id": name,
        "name": str(getattr(opponent, "name", name)),
        "version": str(getattr(opponent, "version", __version__)),
    }


def _reproducibility_metadata(
    agent_manifest: Path,
    scoring_version: str,
    inputs: dict[str, Path],
    seed_schedule: list[int] | None = None,
    opponent: dict[str, str] | None = None,
) -> dict[str, object]:
    metadata: dict[str, object] = {
        "benchmark_version": __version__,
        "package_version": __version__,
        "scoring_version": scoring_version,
        "agent_manifest_path": str(agent_manifest),
        "agent_manifest_hash": _file_sha256(agent_manifest),
        "inputs": {
            name: {"path": str(path), "sha256": _file_sha256(path)}
            for name, path in sorted(inputs.items())
        },
    }
    if seed_schedule is not None:
        metadata["seed_schedule_hash"] = _text_sha256(",".join(str(seed) for seed in seed_schedule))
        metadata["seed_count"] = len(seed_schedule)
    if opponent is not None:
        metadata["opponent"] = opponent
    return metadata


def _file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return f"sha256:{hasher.hexdigest()}"


def _text_sha256(text: str) -> str:
    return f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def _safe_agent_response(adapter: SubprocessAgentAdapter, request: AgentRequest) -> EvaluatedResponse:
    try:
        return EvaluatedResponse(adapter.act(request))
    except Exception as exc:
        for action in request.legal_actions:
            if action.type in {"check", "fold"}:
                return EvaluatedResponse(
                    AgentResponse("1.0", request.request_id, AgentAction(action.type)),
                    getattr(exc, "classification", "malformed"),
                )
        return EvaluatedResponse(
            AgentResponse("1.0", request.request_id, AgentAction("fold")),
            getattr(exc, "classification", "malformed"),
        )


def _run_id(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


if __name__ == "__main__":
    raise SystemExit(main())
