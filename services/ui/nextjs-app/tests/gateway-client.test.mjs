import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {requestJson, readSignals, severityColor, readHealth} from '../src/utils/gateway-client.mjs';

test('actual HTTP failure never becomes successful dashboard data or feedback', async t => {
  const server=createServer((req,res)=>{
    if(req.url==='/missing'){res.writeHead(503,{'Content-Type':'application/json'});res.end('{"error":"provider unavailable"}');}
    else if(req.url==='/empty'){res.writeHead(204);res.end();}
    else if(req.url==='/broken'){res.writeHead(200,{'Content-Type':'application/json'});res.end('not JSON');}
    else{res.writeHead(200,{'Content-Type':'application/json'});res.end('[]');}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  t.after(()=>new Promise(resolve=>server.close(resolve)));
  const base=`http://127.0.0.1:${server.address().port}`;
  assert.deepEqual(readSignals(await requestJson(base+'/signals')),[]);
  await assert.rejects(requestJson(base+'/missing'),/HTTP 503/);
  await assert.rejects(requestJson(base+'/missing',{method:'POST',body:'{}'}),/HTTP 503/);
  await assert.rejects(requestJson(base+'/broken'),SyntaxError);
  assert.equal(await requestJson(base+'/empty',{method:'POST'}),null);
});
test('malformed signals cannot enter rendered state',()=>{
  for(const value of [null,{},[{signal_id:'x',description:'d',confidence_score:NaN,severity:'HIGH'}],[{signal_id:'x',description:'d',confidence_score:1.2,severity:'LOW'}]])assert.throws(()=>readSignals(value));
  const signal={agent_name:'agent',signal_type:'OBSERVATION',timestamp:'2026-01-01T00:00:00Z',signal_id:'s1',description:'Observed anomaly',confidence_score:.7,severity:'MEDIUM'};
  assert.deepEqual(readSignals([signal]),[signal]);assert.equal(severityColor('unknown'),'gray');
  assert.throws(()=>readHealth({status:'healthy'}));
  assert.deepEqual(readHealth({ingestion_rate:0,processing_latency:0,active_agents:0,signal_accuracy:0}),{ingestion_rate:0,processing_latency:0,active_agents:0,signal_accuracy:0});
});
