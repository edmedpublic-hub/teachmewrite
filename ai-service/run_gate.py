#!/usr/bin/env python3
"""TeachMeWrite AI golden-set gate. Runs each case 3 times, 2-of-3 rule.
Usage: python run_gate.py <service_url> [--runs N] [--threshold K] [--out result.json]
Exit 0 = all cases pass, exit 1 = any case fails. This is what CI reads."""
import argparse, json, sys, time
from pathlib import Path
import httpx

def _norm(resp):
    if hasattr(resp, "model_dump"):
        return resp.model_dump()
    return resp

def score_case(case, response):
    resp = _norm(response)
    exp = case["expected"]
    failures = []
    issues = resp.get("issues", [])
    cats = {i["category"] for i in issues}
    blob = " ".join((i.get("explanation","")+" "+i.get("example","")).lower() for i in issues)
    for c in exp["must_flag_categories"]:
        if c not in cats: failures.append(f"missing category '{c}'")
    for c in exp["must_not_flag_categories"]:
        if c in cats: failures.append(f"forbidden category '{c}' flagged")
    lo, hi = exp["score_range"]
    score = resp.get("overall_score")
    if score is None: failures.append("missing overall_score")
    elif not (lo <= score <= hi): failures.append(f"score {score} outside [{lo},{hi}]")
    needles = exp["must_mention_any"]
    if needles and not any(n.lower() in blob for n in needles):
        failures.append(f"none of {needles} appeared")
    return {"pass": len(failures)==0, "failures": failures}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("service_url")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--threshold", type=int, default=2)
    ap.add_argument("--golden", default=str(Path(__file__).parent / "golden_set.jsonl"))
    ap.add_argument("--out", default="gate_result.json")
    args = ap.parse_args()

    cases = [json.loads(l) for l in Path(args.golden).read_text(encoding="utf-8").splitlines() if l.strip()]
    if not cases: print("ERROR: empty golden set", file=sys.stderr); sys.exit(1)

    try:
        h = httpx.get(f"{args.service_url}/health", timeout=30.0)
        if h.status_code != 200: print(f"ERROR: /health {h.status_code}", file=sys.stderr); sys.exit(1)
    except Exception as e:
        print(f"ERROR: service unreachable: {e}", file=sys.stderr); sys.exit(1)

    results, t0 = [], time.time()
    for i, case in enumerate(cases, 1):
        payload = {"student_text": case["student_text"], "level": case["level"]}
        runs = []
        for _ in range(args.runs):
            try:
                r = httpx.post(f"{args.service_url}/feedback", json=payload, timeout=120.0)
                runs.append(score_case(case, r.json()) if r.status_code == 200
                            else {"pass": False, "failures": [f"HTTP {r.status_code}"]})
            except Exception as e:
                runs.append({"pass": False, "failures": [f"exception: {e}"]})
        pc = sum(1 for x in runs if x["pass"])
        verdict = "PASS" if pc >= args.threshold else "FAIL"
        results.append({"id": case["id"], "verdict": verdict, "pass_count": pc, "runs": runs})
        print(f"[{i:02d}/{len(cases)}] {case['id']}  {verdict} {pc}/{args.runs}")
        if verdict == "FAIL":
            for x in runs:
                if not x["pass"]:
                    for f in x["failures"]: print(f"           - {f}")
                    break

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    print(f"\nGate: {passed}/{len(results)} passed in {time.time()-t0:.1f}s")
    Path(args.out).write_text(json.dumps({"service_url": args.service_url, "passed": passed,
        "total": len(results), "runs": args.runs, "threshold": args.threshold,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "detailed": results}, indent=2))
    sys.exit(0 if passed == len(results) else 1)

if __name__ == "__main__":
    main()
