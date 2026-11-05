"""Durable SQLite workflow with fenced at-least-once outbox delivery."""
import json, sqlite3, time
from contextlib import contextmanager
from dataclasses import dataclass

class WorkflowError(Exception): pass
@dataclass(frozen=True)
class Step:
    name: str
    handler: str
    approval: bool = False

class Engine:
    def __init__(self,path,handlers,clock=time.time,max_attempts=3,lease_seconds=30):
        if max_attempts<1 or lease_seconds<=0: raise ValueError('invalid configuration')
        self.path,self.handlers,self.clock=path,dict(handlers),clock
        self.max_attempts,self.lease_seconds=max_attempts,lease_seconds
        with self._db() as db:
            db.executescript("""CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,plan TEXT,input TEXT,cursor INTEGER,state TEXT,output TEXT);
            CREATE TABLE IF NOT EXISTS approvals(id TEXT,step INTEGER,PRIMARY KEY(id,step));
            CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY,topic TEXT,payload TEXT,state TEXT DEFAULT 'READY',attempts INTEGER DEFAULT 0,next_at REAL DEFAULT 0,owner TEXT,fence INTEGER DEFAULT 0,lease_until REAL DEFAULT 0);""")
    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=10)
        try:
            with db: yield db
        finally: db.close()
    def start(self,id,steps,data):
        if not id or not steps or not isinstance(data,dict) or len({s.name for s in steps})!=len(steps) or any(s.handler not in self.handlers for s in steps): raise WorkflowError('invalid plan')
        plan=json.dumps([s.__dict__ for s in steps],sort_keys=True); payload=json.dumps(data,sort_keys=True)
        with self._db() as db:
            db.execute('INSERT OR IGNORE INTO runs VALUES (?,?,?,?,?,?)',(id,plan,payload,0,'READY',payload))
            if db.execute('SELECT plan,input FROM runs WHERE id=?',(id,)).fetchone()!=(plan,payload): raise WorkflowError('idempotency conflict')
        return self.status(id)
    def status(self,id):
        with self._db() as db: row=db.execute('SELECT cursor,state,output FROM runs WHERE id=?',(id,)).fetchone()
        if row is None: raise WorkflowError('unknown run')
        return dict(cursor=row[0],state=row[1],output=json.loads(row[2]))
    def approve(self,id,step):
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT plan,cursor FROM runs WHERE id=?',(id,)).fetchone()
            if not row or step!=row[1] or step>=len(json.loads(row[0])) or not json.loads(row[0])[step]['approval']: raise WorkflowError('invalid approval')
            db.execute('INSERT OR IGNORE INTO approvals VALUES (?,?)',(id,step))
    def advance(self,id):
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT plan,cursor,state,output FROM runs WHERE id=?',(id,)).fetchone()
            if not row: raise WorkflowError('unknown run')
            plan,cursor,state,output=row; steps=json.loads(plan)
            if cursor==len(steps): return dict(cursor=cursor,state=state,output=json.loads(output))
            step=steps[cursor]
            if step['approval'] and not db.execute('SELECT 1 FROM approvals WHERE id=? AND step=?',(id,cursor)).fetchone():
                db.execute("UPDATE runs SET state='WAIT_APPROVAL' WHERE id=?",(id,))
                return dict(cursor=cursor,state='WAIT_APPROVAL',output=json.loads(output))
            result=self.handlers[step['handler']](json.loads(output))
            if not isinstance(result,dict): raise WorkflowError('invalid handler output')
            result=dict(result); effects=result.pop('_outbox',[])
            if not isinstance(effects,list): raise WorkflowError('invalid outbox')
            topics=set()
            for effect in effects:
                if not isinstance(effect,dict) or not isinstance(effect.get('topic'),str) or not effect['topic'] or not isinstance(effect.get('payload'),dict) or effect['topic'] in topics: raise WorkflowError('invalid effect')
                topics.add(effect['topic'])
                key=json.dumps([id,cursor,effect['topic']],separators=(',',':'))
                db.execute('INSERT INTO outbox(id,topic,payload) VALUES (?,?,?)',(key,effect['topic'],json.dumps(effect['payload'],sort_keys=True)))
            cursor+=1; state='DONE' if cursor==len(steps) else 'READY'
            db.execute('UPDATE runs SET cursor=?,state=?,output=? WHERE id=?',(cursor,state,json.dumps(result,sort_keys=True),id))
            return dict(cursor=cursor,state=state,output=result)
    def claim(self,worker):
        if not worker: raise WorkflowError('worker required')
        now=self.clock()
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute("UPDATE outbox SET state='DEAD',owner=NULL WHERE state='LEASED' AND lease_until<=? AND attempts>=?",(now,self.max_attempts))
            row=db.execute("SELECT id,topic,payload,fence FROM outbox WHERE (state='READY' OR (state='LEASED' AND lease_until<=?)) AND next_at<=? AND attempts<? ORDER BY rowid LIMIT 1",(now,now,self.max_attempts)).fetchone()
            if row is None:return None
            key,topic,payload,fence=row; fence+=1
            db.execute("UPDATE outbox SET state='LEASED',owner=?,fence=?,lease_until=?,attempts=attempts+1 WHERE id=?",(worker,fence,now+self.lease_seconds,key))
            return dict(id=key,topic=topic,payload=json.loads(payload),fence=fence,worker=worker)
    def settle(self,claim,success,backoff=1):
        if backoff<0: raise ValueError('negative backoff')
        now=self.clock()
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute("SELECT attempts FROM outbox WHERE id=? AND state='LEASED' AND owner=? AND fence=? AND lease_until>?",(claim['id'],claim['worker'],claim['fence'],now)).fetchone()
            if not row: raise WorkflowError('stale lease')
            state='DONE' if success else ('DEAD' if row[0]>=self.max_attempts else 'READY')
            db.execute('UPDATE outbox SET state=?,owner=NULL,lease_until=0,next_at=? WHERE id=?',(state,now if success else now+backoff*2**(row[0]-1),claim['id']))
    def deliveries(self):
        with self._db() as db:return db.execute('SELECT topic,state,attempts,fence FROM outbox ORDER BY rowid').fetchall()
