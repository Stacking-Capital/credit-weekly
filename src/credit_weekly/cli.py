"""CLI for credit-weekly: parse ACR reports, diff weeks, encrypt vault, export Canvas & HTML data."""

from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path
from typing import Any

from .canvas_export import build_dashboard_bundle, render_canvas_tsx
from .diff import diff_snapshots
from .models import new_snapshot
from .parsers import parse_report_file
from .vault import decrypt_json_file, encrypt_json_file


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def cmd_parse(args: argparse.Namespace) -> None:
    bureaus: dict[str, Any] = {}
    for flag, b_name in (("equifax", "equifax"), ("experian", "experian"), ("transunion", "transunion")):
        val = getattr(args, flag)
        if val:
            bureaus[b_name] = parse_report_file(val, bureau=b_name)
    if not bureaus:
        raise SystemExit("Provide at least one of --equifax, --experian, or --transunion.")
    snap = new_snapshot(bureaus=bureaus, week_label=args.week, is_example_data=args.example)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    print(f"Wrote normalized snapshot -> {out} (bureaus={list(bureaus)}, util={snap['health_summary']['utilization_pct']}%)")


def cmd_diff(args: argparse.Namespace) -> None:
    prev = _load_json(args.prev)
    curr = _load_json(args.curr)
    res = diff_snapshots(prev, curr)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8")
    counts = res["alert_counts"]
    print(
        f"Diff {res['previous_week']} -> {res['current_week']}: "
        f"critical={counts['critical']}, warning={counts['warning']}, info={counts['info']}"
    )


def cmd_encrypt(args: argparse.Namespace) -> None:
    pw = args.passphrase or getpass.getpass("Vault passphrase: ")
    data = _load_json(args.input)
    dest = encrypt_json_file(data, args.out, pw)
    print(f"Encrypted -> {dest} (AES-256-GCM)")


def cmd_decrypt(args: argparse.Namespace) -> None:
    pw = args.passphrase or getpass.getpass("Vault passphrase: ")
    data = decrypt_json_file(args.input, pw)
    out = Path(args.out)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Decrypted -> {out}")


def cmd_export_dashboard(args: argparse.Namespace) -> None:
    snaps = [_load_json(p) for p in args.snapshots]
    diff_obj = _load_json(args.diff) if args.diff else (diff_snapshots(snaps[-2], snaps[-1]) if len(snaps) >= 2 else None)
    bundle = build_dashboard_bundle(snaps, diff_obj)

    if args.bundle_out:
        bp = Path(args.bundle_out)
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        print(f"Wrote Canvas/UI JSON bundle -> {bp}")

    if args.html_data_out:
        hp = Path(args.html_data_out)
        hp.parent.mkdir(parents=True, exist_ok=True)
        hp.write_text(f"window.CREDIT_WEEKLY_DATA = {json.dumps(bundle)};\n", encoding="utf-8")
        print(f"Wrote standalone HTML data.js -> {hp}")

    if args.canvas_out:
        cp = Path(args.canvas_out)
        cp.parent.mkdir(parents=True, exist_ok=True)
        cp.write_text(render_canvas_tsx(bundle), encoding="utf-8")
        print(f"Wrote Grok Page (.canvas.tsx) -> {cp}")


def cmd_demo(args: argparse.Namespace) -> None:
    root = Path(args.root or Path(__file__).resolve().parents[2])
    s1 = _load_json(root / "fixtures" / "example_snapshot_week1.json")
    s2 = _load_json(root / "fixtures" / "example_snapshot_week2.json")
    diff_obj = diff_snapshots(s1, s2)
    bundle = build_dashboard_bundle([s1, s2], diff_obj)

    dash_dir = root / "dashboard"
    dash_dir.mkdir(parents=True, exist_ok=True)
    (dash_dir / "data.js").write_text(f"window.CREDIT_WEEKLY_DATA = {json.dumps(bundle)};\n", encoding="utf-8")
    (dash_dir / "example_bundle.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    (dash_dir / "ExampleDashboard.canvas.tsx").write_text(render_canvas_tsx(bundle), encoding="utf-8")
    print(
        f"Demo built! Alerts: {diff_obj['alert_counts']} | "
        f"Open {dash_dir / 'index.html'} or feed {dash_dir / 'ExampleDashboard.canvas.tsx'} to WriteCanvas."
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="credit-weekly", description="Weekly 3-bureau credit report pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_parse = sub.add_parser("parse", help="Parse 1-3 bureau PDFs/text files into normalized JSON")
    p_parse.add_argument("--equifax")
    p_parse.add_argument("--experian")
    p_parse.add_argument("--transunion")
    p_parse.add_argument("--week", default="")
    p_parse.add_argument("--example", action="store_true")
    p_parse.add_argument("--out", required=True)
    p_parse.set_defaults(func=cmd_parse)

    p_diff = sub.add_parser("diff", help="Diff previous and current snapshot JSONs")
    p_diff.add_argument("--prev", required=True)
    p_diff.add_argument("--curr", required=True)
    p_diff.add_argument("--out", required=True)
    p_diff.set_defaults(func=cmd_diff)

    p_enc = sub.add_parser("encrypt", help="Encrypt a snapshot JSON with AES-256-GCM")
    p_enc.add_argument("--input", required=True)
    p_enc.add_argument("--out", required=True)
    p_enc.add_argument("--passphrase", default="")
    p_enc.set_defaults(func=cmd_encrypt)

    p_dec = sub.add_parser("decrypt", help="Decrypt an AES-256-GCM snapshot")
    p_dec.add_argument("--input", required=True)
    p_dec.add_argument("--out", required=True)
    p_dec.add_argument("--passphrase", default="")
    p_dec.set_defaults(func=cmd_decrypt)

    p_exp = sub.add_parser("export-dashboard", help="Build PII-scrubbed Grok Page .tsx and HTML data.js")
    p_exp.add_argument("--snapshots", nargs="+", required=True)
    p_exp.add_argument("--diff", default="")
    p_exp.add_argument("--bundle-out", default="")
    p_exp.add_argument("--html-data-out", default="")
    p_exp.add_argument("--canvas-out", default="")
    p_exp.set_defaults(func=cmd_export_dashboard)

    p_demo = sub.add_parser("demo", help="Generate dashboard data and Canvas TSX from synthetic example fixtures")
    p_demo.add_argument("--root", default="")
    p_demo.set_defaults(func=cmd_demo)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
