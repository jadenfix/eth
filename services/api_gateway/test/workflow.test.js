import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createGateway} from '../server.js';
import {OnchainClient} from '../../../sdk/js/index.js';
async function start(options){const server=createGateway(options);await new Promise(r=>server.listen(0,'127.0.0.1',r));return {server,client:new OnchainClient(`http://127.0.0.1:${server.address().port}`,{token:options.token})};}
const close=server=>new Promise((r,j)=>server.close(e=>e?j(e):r()));
test('real HTTP SDK: validated entities, multi-hop graph, restart persistence and honest health',async()=>{
 const dir=mkdtempSync(join(tmpdir(),'onchain-')); const databasePath=join(dir,'graph.sqlite'); let server;
 try{
  let running=await start({databasePath});server=running.server;let client=running.client;
  assert.equal((await client.getHealth()).provider_connected,false);
  assert.equal((await client.request('/v1/signals')).total_count,0);
  await assert.rejects(client.createEntity({type:'ADDRESS',address:'0xNO'}),e=>e.status===400);
  const a=await client.createEntity({type:'ADDRESS',name:'Treasury',address:'0x'+'a'.repeat(40)});
  const b=await client.createEntity({type:'CONTRACT',name:'Router',address:'0x'+'b'.repeat(40)});
  const c=await client.createEntity({type:'EXCHANGE',name:'Exchange'});
  await assert.rejects(client.createEntity({type:'ADDRESS',address:'0x'+'A'.repeat(40)}),e=>e.status===409);
  await assert.rejects(client.createRelationship({type:'OWNS',fromEntityId:a.id,toEntityId:'missing'}),e=>e.status===404);
  await assert.rejects(client.createRelationship({type:'OWNS',fromEntityId:a.id,toEntityId:a.id}),e=>e.status===400);
  await client.createRelationship({type:'INTERACTS_WITH',fromEntityId:a.id,toEntityId:b.id});
  await client.createRelationship({type:'PART_OF',fromEntityId:b.id,toEntityId:c.id});
  await assert.rejects(client.createRelationship({type:'PART_OF',fromEntityId:b.id,toEntityId:c.id}),e=>e.status===409);
  assert.equal((await client.getNetwork(a.id,1)).nodes.length,2);
  assert.equal((await client.getNetwork(a.id,2)).nodes.length,3);
  assert.equal((await client.searchEntities('treasury')).entities[0].id,a.id);
  await assert.rejects(client.getNetwork(a.id,99),e=>e.status===400);
  await assert.rejects(client.submitFeedback({signal_id:'unavailable',user_id:'reviewer',rating:1}),e=>e.status===404);
  await close(server);server=null;
  running=await start({databasePath});server=running.server;client=running.client;
  assert.equal((await client.getNetwork(a.id)).edges.length,2);
  assert.equal((await client.getHealth()).entities,3);
 }finally{if(server)await close(server);rmSync(dir,{recursive:true,force:true});}
});
test('auth, malformed JSON, oversized body and unknown endpoints fail explicitly',async()=>{
 const {server,client}=await start({token:'test-local-secret'});
 try{
  const anonymous=new OnchainClient(client.baseURL);
  await assert.rejects(anonymous.searchEntities(),e=>e.status===401);
  assert.equal((await client.searchEntities()).total_count,0);
  await assert.rejects(client.request('/v1/entities',{method:'POST',body:'{'}),e=>e.status===400);
  await assert.rejects(client.request('/v1/entities',{method:'POST',body:JSON.stringify({name:'x'.repeat(70000)})}),e=>e.status===413);
  await assert.rejects(client.request('/v1/unknown'),e=>e.status===404);
  const html=await fetch(client.baseURL);assert.match(await html.text(),/No live chain or AI provider/);
 }finally{await close(server);}
});
