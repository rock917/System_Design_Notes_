from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
PACKAGED = HERE.name == 'build'
EXAMPLES = (ROOT if PACKAGED else ROOT / "outputs/system-design-master-handbook") / 'examples'
SCRATCH = HERE / 'test-tmp'
SCRATCH.mkdir(parents=True, exist_ok=True)
assert SCRATCH.resolve().is_relative_to(HERE)
tempfile.tempdir = str(SCRATCH)
os.environ["TMP"] = str(SCRATCH)
os.environ["TEMP"] = str(SCRATCH)
sys.path.insert(0, str(EXAMPLES))
suite = unittest.defaultTestLoader.discover(str(EXAMPLES), pattern="test_examples.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)
outdir = EXAMPLES / "actual_outputs"
outdir.mkdir(exist_ok=True)
outputs = {}
for module in ["algorithms", "orders", "messaging", "concurrency", "performance", "security", "protocols", "incident_drill"]:
    process = subprocess.run([sys.executable, str(EXAMPLES / (module + ".py"))], capture_output=True, text=True)
    outputs[module] = {"exit_code": process.returncode, "stdout": process.stdout, "stderr": process.stderr}
    (outdir / (module + ".txt")).write_text(process.stdout + process.stderr, encoding="utf-8")
report = {"tests_run": result.testsRun, "passed": result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
          "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
          "skip_reasons": [reason for _, reason in result.skipped], "python": sys.version,
          "demo_results": outputs}
(HERE / "test_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: value for key,value in report.items() if key != "demo_results"}, indent=2))
sys.exit(0 if result.wasSuccessful() and all(x["exit_code"]==0 for x in outputs.values()) else 1)
