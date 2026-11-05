import concurrent.futures
import tempfile
import unittest
from pathlib import Path
from .engine import Engine, Step, WorkflowError

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=str(Path(tmp.name)/'workflow.db')
        self.now=[100.]
        self.handlers={'emit':lambda d:{'n':d['n']+1,'_outbox':[{'topic':'telegram','payload':{'n':d['n']+1}}]}}
        self.engine=Engine(self.path,self.handlers,clock=lambda:self.now[0],max_attempts=2,lease_seconds=5)
        self.engine.start('run',[Step('send','emit')],{'n':0})
    def test_restart_and_idempotency(self):
        self.engine.advance('run')
        recovered=Engine(self.path,self.handlers,clock=lambda:self.now[0])
        self.assertEqual(recovered.status('run')['output'],{'n':1})
        self.assertEqual(recovered.advance('run')['state'],'DONE')
        self.assertEqual(len(recovered.deliveries()),1)
    def test_fencing(self):
        self.engine.advance('run')
        first=self.engine.claim('a')
        self.now[0]+=6
        second=self.engine.claim('b')
        self.assertEqual(second['fence'],first['fence']+1)
        with self.assertRaises(WorkflowError):self.engine.settle(first,True)
        self.engine.settle(second,True)
        self.assertEqual(self.engine.deliveries()[0][1],'DONE')
    def test_bounded_retries(self):
        self.engine.advance('run')
        first=self.engine.claim('a')
        self.engine.settle(first,False,2)
        self.assertIsNone(self.engine.claim('b'))
        self.now[0]+=2
        second=self.engine.claim('b')
        self.engine.settle(second,False)
        self.assertEqual(self.engine.deliveries()[0][1],'DEAD')
    def test_concurrent_claim(self):
        self.engine.advance('run')
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            claims=list(pool.map(self.engine.claim,map(str,range(8))))
        self.assertEqual(sum(x is not None for x in claims),1)
    def test_concurrent_advance(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(self.engine.advance,['run']*8))
        self.assertEqual(self.engine.status('run')['output'],{'n':1})
        self.assertEqual(len(self.engine.deliveries()),1)
    def test_approval(self):
        self.engine.start('approve',[Step('send','emit',True)],{'n':0})
        self.assertEqual(self.engine.advance('approve')['state'],'WAIT_APPROVAL')
        self.engine.approve('approve',0)
        self.assertEqual(self.engine.advance('approve')['state'],'DONE')
    def test_rollback_invalid_effect(self):
        self.engine.handlers['emit']=lambda d:{'_outbox':[{'topic':'x','payload':{}},{'topic':'x','payload':{}}]}
        with self.assertRaises(WorkflowError):self.engine.advance('run')
        self.assertEqual(self.engine.status('run')['cursor'],0)
        self.assertEqual(self.engine.deliveries(),[])
    def test_conflict(self):
        with self.assertRaises(WorkflowError):self.engine.start('run',[Step('send','emit')],{'n':9})
    def test_expired_settlement(self):
        self.engine.advance('run')
        claim=self.engine.claim('a')
        self.now[0]+=6
        with self.assertRaises(WorkflowError):self.engine.settle(claim,True)
    def test_exhausted_expired_lease(self):
        self.engine.advance('run')
        self.engine.claim('a')
        self.now[0]+=6
        self.engine.claim('b')
        self.now[0]+=6
        self.assertIsNone(self.engine.claim('c'))
        self.assertEqual(self.engine.deliveries()[0][1],'DEAD')
