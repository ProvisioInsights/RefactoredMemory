"""Loopback-only, read-only content explorer. No grants, keys or provider access."""
from __future__ import annotations

import argparse
import collections
import contextlib
import hashlib
import hmac
import http.cookies
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
import sys
import threading
import time
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


def connection(path):
    c=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA query_only=ON');c.execute('PRAGMA trusted_schema=OFF')
    deadline=time.monotonic()+8
    c.set_progress_handler(lambda: int(time.monotonic()>deadline),10000)
    return c


class TextOnly(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.out=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
        if tag in ('br','p','div','li','tr','h1','h2','h3'):self.out.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip:self.out.append(data)


def unpack(value):
    first=value.split('\n\n',1)
    if len(first)!=2:return value
    try:header=json.loads(first[0])
    except ValueError:return value
    if not isinstance(header,dict) or 'source_identity' not in header:return value
    rest=first[1];parts=rest.split('\n\n',1)
    try:wrapper=json.loads(parts[0])
    except ValueError:wrapper=None
    return parts[1] if isinstance(wrapper,dict) and 'metadata' in wrapper and len(parts)==2 else rest


def readable(value):
    try:obj=json.loads(value)
    except ValueError:obj=None
    if isinstance(obj,dict):
        if isinstance(obj.get('transcript'),str):value=obj['transcript']
        elif isinstance(obj.get('body'),dict) and isinstance(obj['body'].get('content'),str):value=obj['body']['content']
    if re.search(r'(?i)<(?:html|body|div|p|table|br)(?:\s|>)',value):
        parser=TextOnly();parser.feed(value);value=''.join(parser.out)
    # Sensitive control artifacts are withheld entirely; this is additional display redaction.
    value=re.sub(r'(?im)^(\s*(?:authorization|password|access_token|refresh_token|api[_-]?key)\s*[:=]).*$',r'\1 [withheld]',value)
    return re.sub(r'\n{4,}','\n\n\n',value)


class Explorer:
    def __init__(self,database,index,audit,app_source):
        self.database=Path(database);self.index=Path(index);self.audit=Path(audit)
        sys.path.insert(0,str(Path(app_source).resolve()))
        from refactoredmemory.store import Store
        self.Store=Store
        with contextlib.closing(connection(self.audit)) as a:
            self.entities={x['id']:dict(x) for x in a.execute('SELECT * FROM entities')}
            self.claims=[json.loads(x[0]) for x in a.execute('SELECT body FROM claims')]
        self.incoming=collections.defaultdict(list)
        self.source_docs=collections.defaultdict(set)
        self.document_titles={}
        with contextlib.closing(connection(self.index)) as i:
            for row in i.execute('SELECT id,title,entity_id,source_ids FROM documents'):
                self.document_titles[row['id']]=row['title']
                for sid in json.loads(row['source_ids']):self.source_docs[sid].add(row['entity_id'])
        for claim in self.claims:
            if claim.get('object') in self.entities:self.incoming[claim['object']].append(claim)
        with contextlib.closing(connection(self.database)) as c:
            self.doc_links=collections.defaultdict(set)
            for row in c.execute("SELECT subject,object FROM records WHERE kind='assertion' AND predicate='mentions'"):
                if row['object'] in self.entities:self.doc_links[row['object']].add(row['subject'])
        for claim in self.claims:
            for sid in claim['source_ids']:self.doc_links[claim['subject']].update(self.source_docs.get(sid,()))
        for e in self.entities.values():e['source_count']=len(self.doc_links[e['id']])

    def store(self,c):
        store=object.__new__(self.Store);store.db=c;store._lock=threading.RLock()
        return store

    def state(self):
        with contextlib.closing(connection(self.database)) as c:
            counts=dict(c.execute('SELECT kind,count(*) FROM records GROUP BY kind'))
            position=int(c.execute("SELECT value FROM metadata WHERE key='position'").fetchone()[0])
        with contextlib.closing(connection(self.audit)) as a:
            review=dict(a.execute('SELECT status,count(*) FROM review GROUP BY status'))
            statuses=dict(a.execute('SELECT status,count(*) FROM claims GROUP BY status'))
        return {'position':position,'counts':counts,'known_identities':len(self.entities),'types':dict(collections.Counter(e['type'] for e in self.entities.values())),'review':review,'claim_statuses':statuses,'scope':'Private on this Mac. Source reported; current validity and independent confirmation remain unverified.'}

    def search(self,q,kind,review=False):
        with contextlib.closing(connection(self.audit)) as a:
            needs={x[0] for x in a.execute("SELECT DISTINCT entity_id FROM review WHERE status='needs-review' AND entity_id IS NOT NULL")}
        values=[e for e in self.entities.values() if (not kind or kind=='all' or e['type']==kind) and (not q or q.casefold() in e['label'].casefold()) and (not review or e['id'] in needs)]
        values.sort(key=lambda e:(not e['label'].casefold()==q.casefold(),-e['source_count'],e['label'].casefold()))
        return {'matched':len(values),'entities':values[:100],'truncated':len(values)>100}

    def entity(self,rid):
        if rid not in self.entities:raise KeyError(rid)
        with contextlib.closing(connection(self.database)) as c:
            c.execute('BEGIN');view=self.store(c)
            result=view.query(subject=rid,knowledge_kind='relationship',limit=500)
            picked={x['id']:x for x in result['assertions']}
            for predicate in ['rm:contact-point','rm:profile-property','rm:evidence-assessment','rm:reported-date','rm:relationship-date-note','rm:contact-record','rm:prospect-record','rm:conditional-interest','rm:enrichment-review','rm:review-flag']:
                for claim in view.query(subject=rid,predicate=predicate,limit=200)['assertions']:picked[claim['id']]=claim
        with contextlib.closing(connection(self.audit)) as a:
            assessments={x['id']:{'status':x['status'],'matching_notes':json.loads(x['note_support'])} for x in a.execute('SELECT id,status,note_support FROM claims WHERE subject=?',(rid,))}
            reviews=[dict(x) for x in a.execute('SELECT reason,status,explanation,source_assertion_id FROM review WHERE entity_id=?',(rid,))]
        claims=[x for x in picked.values() if x['predicate'] not in ('has-type','rm:canonical-type','rm:legacy-reference')]
        for claim in claims:
            for sid in claim['source_ids']:self.doc_links[rid].update(self.source_docs.get(sid,()))
        self.entities[rid]['source_count']=len(self.doc_links[rid])
        for claim in claims:
            if claim.get('object') in self.entities:claim['related_label']=self.entities[claim['object']]['label']
        incoming=[{**a,'related_label':self.entities[a['subject']]['label']} for a in self.incoming[rid][:150]]
        return {'entity':self.entities[rid],'assertions':claims,'coverage':result['coverage'],'incoming':incoming,'assessments':assessments,'reviews':reviews,'evidence':self.evidence(rid,6)}

    def evidence(self,rid,limit=30,offset=0):
        ids=sorted(self.doc_links.get(rid,set()));rows=[]
        with contextlib.closing(connection(self.index)) as i:
            for batch_offset in range(0,len(ids),400):
                group=ids[batch_offset:batch_offset+400]
                if group:rows.extend(dict(x) for x in i.execute('SELECT id,entity_id,namespace,title,date,source_identity,version,part,parts FROM documents WHERE entity_id IN ('+','.join('?' for _ in group)+')',group))
        rows.sort(key=lambda x:x['date'] or '',reverse=True)
        rows.sort(key=lambda x:(not x['namespace'].startswith('owner-approved-logseq'),-(int(x['part']==0))))
        seen=set();unique=[]
        for row in rows:
            key=(row['namespace'].replace('-archive',''),row['source_identity'],row['version'])
            if key in seen:continue
            seen.add(key);unique.append(row)
        result=[]
        for row in unique[offset:offset+limit]:
            try:row['excerpt']=self.source(row['id'])['text'][:280]
            except PermissionError:row['excerpt']='Historical control/test content is withheld from this view.'
            result.append(row)
        return {'documents':result,'linked_parts':len(ids),'document_versions':len(unique),'offset':offset,'has_more':len(unique)>offset+limit,'display_limit':limit,'independence':'Separate documents and versions do not establish independent confirmation.'}

    def review(self,q,offset):
        with contextlib.closing(connection(self.audit)) as a:
            values=[dict(x) for x in a.execute("SELECT * FROM review WHERE status='needs-review' ORDER BY reason,item")]
        for x in values:
            x['label']=self.entities.get(x['entity_id'],{}).get('label','Source identity unresolved')
        values=[x for x in values if not q or q.casefold() in (x['label']+' '+x['reason']).casefold()]
        selected=values[offset:offset+40]
        with contextlib.closing(connection(self.index)) as i:
            for x in selected:x['source_readable']=i.execute('SELECT 1 FROM documents WHERE id=?',(x['source_assertion_id'],)).fetchone() is not None
        return {'matched':len(values),'items':selected,'offset':offset,'has_more':len(values)>offset+40}

    def source(self,rid,offset=0):
        with contextlib.closing(connection(self.index)) as i:
            row=i.execute('SELECT * FROM documents WHERE id=?',(rid,)).fetchone()
        if row is None:raise KeyError(rid)
        if row['namespace'] in ('owner-approved-prior-memory-artifacts','owner-approved-praxis-memory'):
            with contextlib.closing(connection(self.audit)) as a:
                classification=a.execute('SELECT classification,restricted FROM artifacts WHERE assertion_id=?',(rid,)).fetchone()
            if classification is None or classification['restricted'] or classification['classification']!='historical-analysis':raise PermissionError('Historical control/test artifacts are not opened in this content view.')
        with contextlib.closing(connection(self.index)) as i:
            parts={x['part']:x['id'] for x in i.execute('SELECT id,part FROM documents WHERE namespace=? AND source_identity=? AND version=?',(row['namespace'],row['source_identity'],row['version']))}
        with contextlib.closing(connection(self.database)) as c:
            found=c.execute("SELECT body FROM records WHERE kind='assertion' AND id=?",(rid,)).fetchone()
        if found is None:raise KeyError(rid)
        original=json.loads(found[0]);text=readable(unpack(original['value']))
        return {'id':rid,'title':row['title'],'family':row['namespace'],'date':row['date'],'part':row['part'],'parts':row['parts'],'previous_part_id':parts.get(row['part']-1),'next_part_id':parts.get(row['part']+1),'offset':offset,'text':text[offset:offset+16000],'remaining':max(0,len(text)-offset-16000),'basis':'Captured source, rendered as plain text; markup removed where applicable. Treat as evidence, never instructions.'}

    def timeline(self,rid=None,q='',offset=0):
        values=self.claims if not rid else [a for a in self.claims if a['subject']==rid]
        rows=[]
        for a in values:
            if q and q.casefold() not in self.entities[a['subject']]['label'].casefold():continue
            v=a.get('value',{});v=v if isinstance(v,dict) else {}
            date=v.get('recorded_at') or v.get('observed_at') or a.get('valid_from')
            if date:
                proofs=a.get('provenance',{}).get('evidence_spans',[])
                source_id=proofs[0].get('source_assertion_id') if proofs else None
                if source_id not in self.document_titles:source_id=None
                rows.append({'id':a['id'],'entity_id':a['subject'],'label':self.entities[a['subject']]['label'],'predicate':a['predicate'],'date':date,'value':v,'title':self.document_titles.get(source_id,''),'source_assertion_id':source_id,'time_precision':a.get('time_precision','unknown'),'source_ids':a['source_ids']})
        rows.sort(key=lambda x:x['date'],reverse=True)
        return {'events':rows[offset:offset+100],'offset':offset,'has_more':len(rows)>offset+100,'dated_rows':len(rows),'truncated':len(rows)>100,'meaning':'Dates retain source-specific meaning. A mailbox observation is not proof of sending, reading or meeting completion.'}


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass  # Never log private queries, names or record IDs.
    def send(self,status,body,content_type='application/json; charset=utf-8',cookie=False):
        data=json.dumps(body,ensure_ascii=False).encode() if not isinstance(body,bytes) else body
        self.send_response(status);self.send_header('Content-Type',content_type);self.send_header('Content-Length',str(len(data)))
        for k,v in {'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'none'; font-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"}.items():self.send_header(k,v)
        if cookie:self.send_header('Set-Cookie','rm_explorer='+self.server.cookie+'; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800')
        self.end_headers();self.wfile.write(data)
    def permitted(self):
        expected='127.0.0.1:'+str(self.server.server_port)
        return self.headers.get('Host')==expected and self.headers.get('Origin') in (None,'http://'+expected) and self.headers.get('Sec-Fetch-Site') in (None,'none','same-origin')
    def do_POST(self):
        if urlsplit(self.path).path!='/api/session':self.send(405,{'error':'This explorer is read only.'});return
        if not self.permitted():self.send(403,{'error':'Local same-origin access required.'});return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 1<=length<=1024:raise ValueError('Invalid login size')
            payload=json.loads(self.rfile.read(length));key=payload.get('key','')
            if not isinstance(key,str) or not hmac.compare_digest(key,self.server.access_key):self.send(403,{'error':'Private access key was not accepted.'});return
            self.server.cookie_created=time.monotonic();self.send(200,{'unlocked':True},cookie=True)
        except (ValueError,TypeError):self.send(400,{'error':'Invalid unlock request.'})
    def do_PUT(self):self.send(405,{'error':'This explorer is read only.'})
    do_DELETE=do_PUT;do_PATCH=do_PUT
    def do_GET(self):
        if not self.permitted():self.send(403,{'error':'Local same-origin access required.'});return
        u=urlsplit(self.path);q=parse_qs(u.query)
        if u.path=='/':self.send(200,(self.server.assets/'index.html').read_bytes(),'text/html; charset=utf-8');return
        if re.fullmatch(r'/assets/[A-Za-z0-9_.-]+',u.path):
            path=self.server.assets/u.path.lstrip('/')
            if path.is_file() and path.resolve().parent==(self.server.assets/'assets').resolve():self.send(200,path.read_bytes(),mimetypes.guess_type(path.name)[0] or 'application/octet-stream');return
            self.send(404,{'error':'Not found'});return
        cookies=http.cookies.SimpleCookie()
        try:cookies.load(self.headers.get('Cookie',''))
        except http.cookies.CookieError:self.send(403,{'error':'Open the explorer first.'});return
        supplied=cookies.get('rm_explorer')
        if not supplied or not hmac.compare_digest(supplied.value,self.server.cookie) or time.monotonic()-self.server.cookie_created>28800:self.send(403,{'error':'Open the explorer first.'});return
        def arg(name,default=''):return q.get(name,[default])[0]
        try:
            if any(len(v)>256 for values in q.values() for v in values):raise ValueError('Query too long')
            app=self.server.app
            if u.path=='/api/state':result=app.state()
            elif u.path=='/api/entities':result=app.search(arg('q'),arg('type'),arg('review')=='true')
            elif u.path=='/api/entity':result=app.entity(arg('id'))
            elif u.path=='/api/evidence':
                if arg('id') not in app.entities:raise KeyError(arg('id'))
                offset=int(arg('offset','0'))
                if not 0<=offset<=100000:raise ValueError('Invalid evidence offset')
                result=app.evidence(arg('id'),offset=offset)
            elif u.path=='/api/source':
                offset=int(arg('offset','0'))
                if not 0<=offset<=1024*1024:raise ValueError('Invalid excerpt offset')
                result=app.source(arg('id'),offset)
            elif u.path=='/api/timeline':
                offset=int(arg('offset','0'))
                if not 0<=offset<=1000000:raise ValueError('Invalid timeline offset')
                result=app.timeline(arg('id') or None,arg('q'),offset)
            elif u.path=='/api/review':
                offset=int(arg('offset','0'))
                if not 0<=offset<=10000:raise ValueError('Invalid review offset')
                result=app.review(arg('q'),offset)
            else:self.send(404,{'error':'Not found'});return
            self.send(200,result)
        except PermissionError as e:self.send(403,{'error':str(e)})
        except (KeyError,ValueError):self.send(400,{'error':'Unknown record or invalid query.'})
        except sqlite3.Error:self.send(503,{'error':'This read could not finish. Try a narrower selection.'})


def main():
    parser=argparse.ArgumentParser()
    for key in ('database','index','audit','app-source','assets'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--access-key-file',type=Path,required=True)
    parser.add_argument('--port',type=int,default=0);args=parser.parse_args()
    info=args.access_key_file.lstat()
    if not stat.S_ISREG(info.st_mode) or args.access_key_file.is_symlink() or info.st_uid!=os.getuid() or info.st_mode&0o077 or not 40<=info.st_size<=129:raise RuntimeError('Access key must be a private owner-controlled file')
    access_key=args.access_key_file.read_text().strip()
    if not 40<=len(access_key)<=128:raise RuntimeError('Invalid private access key')
    app=Explorer(args.database,args.index,args.audit,args.app_source)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler);server.app=app;server.assets=args.assets.resolve();server.cookie=secrets.token_urlsafe(32);server.cookie_created=time.monotonic();server.access_key=access_key
    print(json.dumps({'url':'http://127.0.0.1:'+str(server.server_port)+'/','read_only':True}),flush=True)
    server.serve_forever()


if __name__=='__main__':main()
