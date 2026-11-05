"""Isolated-process smoke and regression checks for trusted reference benchmark."""
import json
import subprocess
import sys
import unittest
from pathlib import Path
from .benchmark import evaluate, reference

class CodingBenchmarkTests(unittest.TestCase):
    def test_reference(self):
        result = evaluate(reference)
        self.assertEqual((result.passed,result.failed),(505,0))

    def test_incorrect_candidate_rejected(self):
        self.assertGreater(evaluate(lambda values,target: None,trials=50).failed,0)

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            evaluate(reference,trials=-1)

    def test_subprocess_isolation(self):
        root = str(Path(__file__).resolve().parents[2])
        name = __package__ + '.benchmark'
        program = ('import json,sys;sys.path.insert(0,sys.argv[1]);'
                   'from '+name+' import evaluate,reference;'
                   'r=evaluate(reference);'
                   'print(json.dumps({"passed":r.passed,"failed":r.failed}))')
        child = subprocess.run([sys.executable,'-I','-c',program,root],
                               capture_output=True,text=True,timeout=10,check=True)
        self.assertEqual(json.loads(child.stdout)['passed'],505)

    def test_timeout_detection(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            subprocess.run([sys.executable,'-c','import time;time.sleep(2)'],
                           capture_output=True,timeout=0.01,check=True)
