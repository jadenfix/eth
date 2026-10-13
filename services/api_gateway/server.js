import {createServer} from 'node:http';
import {DatabaseSync} from 'node:sqlite';
import {randomUUID, timingSafeEqual} from 'node:crypto';
import {mkdirSync, readFileSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const entityTypes = new Set(['ADDRESS', 'CONTRACT', 'TOKEN', 'EXCHANGE', 'POOL', 'BRIDGE', 'ORGANIZATION', 'PERSON']);
const relationshipTypes = new Set(['OWNS', 'CONTROLS', 'TRANSACTS_WITH', 'DEPLOYED', 'INTERACTS_WITH', 'PART_OF', 'SIMILAR_TO', 'RELATED_TO']);
const fail = (status, message) => { const e = new Error(message); e.status = status; throw e; };
function text(value, field, max = 200) {
  if (typeof value !== 'string' || !value.trim() || value.length > max) fail(400, `${field} must be a nonempty string (max ${max})`);
  return value.trim();
}
function integer(raw, fallback, min, max) {
  if (raw === null || raw === undefined) return fallback;
  if (!/^\d+$/.test(String(raw))) fail(400, 'Invalid integer query parameter');
  const n = Number(raw); if (n < min || n > max) fail(400, `Query parameter must be between ${min} and ${max}`); return n;
}
async function body(req) {
  if (!(req.headers['content-type'] || '').startsWith('application/json')) fail(415, 'Content-Type must be application/json');
  const chunks = []; let length = 0;
  for await (const chunk of req) { length += chunk.length; if (length > 65536) fail(413, 'Body exceeds 64 KiB'); chunks.push(chunk); }
  let data; try { data = JSON.parse(Buffer.concat(chunks)); } catch { fail(400, 'Malformed JSON'); }
  if (!data || Array.isArray(data) || typeof data !== 'object') fail(400, 'Body must be an object');
  return data;
}
export function createGateway({databasePath = ':memory:', token = process.env.API_TOKEN} = {}) {
  if (databasePath !== ':memory:') mkdirSync(dirname(resolve(databasePath)), {recursive: true});
  const db = new DatabaseSync(databasePath);
  db.exec(`PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS entities(id TEXT PRIMARY KEY, address TEXT UNIQUE, payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS relationships(id TEXT PRIMARY KEY, from_id TEXT NOT NULL REFERENCES entities(id), to_id TEXT NOT NULL REFERENCES entities(id), type TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(from_id,to_id,type));
    CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS signals(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS feedback(signal_id TEXT NOT NULL REFERENCES signals(id), user_id TEXT NOT NULL, rating INTEGER NOT NULL, comment TEXT, PRIMARY KEY(signal_id,user_id));`);
  const entity = id => { const row = db.prepare('SELECT payload FROM entities WHERE id=?').get(id); if (!row) fail(404, 'Entity not found'); return JSON.parse(row.payload); };
  const list = table => db.prepare(`SELECT payload FROM ${table} ORDER BY rowid`).all().map(x => JSON.parse(x.payload));
  const server = createServer(async (req, res) => {
    const send = (status, data) => { res.writeHead(status, {'Content-Type': 'application/json', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'}); res.end(JSON.stringify(data)); };
    try {
      const url = new URL(req.url, 'http://localhost');
      if (req.method === 'GET' && url.pathname === '/') {
        res.writeHead(200, {'Content-Type': 'text/html; charset=utf-8', 'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'", 'X-Content-Type-Options':'nosniff'});
        return res.end(readFileSync(new URL('./public/index.html', import.meta.url)));
      }
      if (req.method === 'GET' && ['/app.js','/style.css'].includes(url.pathname)) {
        res.writeHead(200, {'Content-Type': url.pathname.endsWith('.js') ? 'text/javascript' : 'text/css', 'X-Content-Type-Options':'nosniff'});
        return res.end(readFileSync(new URL('./public' + url.pathname, import.meta.url)));
      }
      if (token && url.pathname !== '/v1/health') {
        const received = Buffer.from(req.headers.authorization || ''); const expected = Buffer.from(`Bearer ${token}`);
        if (received.length !== expected.length || !timingSafeEqual(received, expected)) fail(401, 'Authentication required');
      }
      const path = url.pathname.replace(/^\/api(?=\/)/, '');
      if (req.method === 'GET' && ['/v1/health','/health'].includes(path)) return send(200, {status:'healthy', mode:'local-graph', storage:'sqlite', chain_connected:false, provider_connected:false, entities:list('entities').length, relationships:list('relationships').length});
      if (req.method === 'POST' && path === '/v1/entities') {
        const input = await body(req); const type = text(input.type, 'type'); if (!entityTypes.has(type)) fail(400,'Invalid entity type');
        const address = input.address == null ? null : text(input.address,'address',42).toLowerCase();
        if (address && !/^0x[0-9a-f]{40}$/.test(address)) fail(400,'Address must contain 40 hexadecimal digits');
        if (['ADDRESS','CONTRACT','TOKEN'].includes(type) && !address) fail(400,'Address is required for this entity type');
        const name = input.name == null ? null : text(input.name,'name');
        if (input.labels != null && (!Array.isArray(input.labels) || input.labels.length > 20 || input.labels.some(v => typeof v !== 'string' || v.length > 80))) fail(400,'Invalid labels');
        if (input.properties != null && (Array.isArray(input.properties) || typeof input.properties !== 'object')) fail(400,'properties must be an object');
        const record = {id:randomUUID(),type,address,name,labels:input.labels || [],properties:input.properties || {},riskScore:null,createdAt:new Date().toISOString()};
        try { db.prepare('INSERT INTO entities VALUES(?,?,?)').run(record.id,address,JSON.stringify(record)); } catch(e) { if (e.code==='ERR_SQLITE_ERROR' && e.message.includes('UNIQUE')) fail(409,'Address already exists'); throw e; }
        return send(201,record);
      }
      if (req.method === 'GET' && ['/v1/entities/search','/v1/entities'].includes(path)) {
        const query = (url.searchParams.get('query') || '').toLowerCase(); const limit = integer(url.searchParams.get('limit'),50,1,100); const offset = integer(url.searchParams.get('offset'),0,0,100000);
        const results = list('entities').filter(e => `${e.name || ''} ${e.address || ''} ${e.labels.join(' ')}`.toLowerCase().includes(query));
        return send(200,{entities:results.slice(offset,offset+limit),total_count:results.length,has_more:offset+limit<results.length});
      }
      if (req.method === 'POST' && path === '/v1/relationships') {
        const input = await body(req); const type = text(input.type,'type'); if (!relationshipTypes.has(type)) fail(400,'Invalid relationship type');
        const fromEntityId = text(input.fromEntityId,'fromEntityId'); const toEntityId = text(input.toEntityId,'toEntityId'); entity(fromEntityId); entity(toEntityId);
        if (fromEntityId === toEntityId) fail(400,'Self relationships are not allowed');
        const record = {id:randomUUID(),type,fromEntityId,toEntityId,createdAt:new Date().toISOString()};
        try { db.prepare('INSERT INTO relationships VALUES(?,?,?,?,?)').run(record.id,fromEntityId,toEntityId,type,JSON.stringify(record)); } catch(e) { if(e.message.includes('UNIQUE')) fail(409,'Relationship already exists'); throw e; }
        return send(201,record);
      }
      const match = path.match(/^\/v1\/entities\/([^/]+)(\/network)?$/);
      if (req.method === 'GET' && match) {
        const center = entity(decodeURIComponent(match[1])); if (!match[2]) return send(200,{entity:center});
        const depth = integer(url.searchParams.get('depth'),2,1,5); const ids = new Set([center.id]); const edges = list('relationships'); let frontier = [center.id];
        for(let i=0;i<depth;i++) { const next=[]; for(const e of edges) { if(frontier.includes(e.fromEntityId) && !ids.has(e.toEntityId)) {ids.add(e.toEntityId);next.push(e.toEntityId);} if(frontier.includes(e.toEntityId) && !ids.has(e.fromEntityId)) {ids.add(e.fromEntityId);next.push(e.fromEntityId);} } frontier=next; }
        return send(200,{center,nodes:[...ids].map(entity),edges:edges.filter(e=>ids.has(e.fromEntityId)&&ids.has(e.toEntityId)),depth});
      }
      if (req.method === 'GET' && ['/v1/events','/events','/v1/signals','/signals'].includes(path)) {
        const table = path.endsWith('signals') ? 'signals':'events'; const all=list(table); const limit=integer(url.searchParams.get('limit'),50,1,100); const offset=integer(url.searchParams.get('offset'),0,0,100000);
        return send(200,{[table]:all.slice(offset,offset+limit),total_count:all.length,has_more:offset+limit<all.length,source:'local',provider_connected:false});
      }
      if (req.method === 'POST' && ['/v1/feedback','/feedback'].includes(path)) {
        const input=await body(req); const id=text(input.signal_id,'signal_id'); const user=text(input.user_id,'user_id');
        if(![-1,1].includes(input.rating)) fail(400,'rating must be -1 or 1');
        if(!db.prepare('SELECT 1 FROM signals WHERE id=?').get(id)) fail(404,'Signal not found');
        const comment=input.comment==null?null:text(input.comment,'comment',2000);
        db.prepare('INSERT INTO feedback VALUES(?,?,?,?) ON CONFLICT(signal_id,user_id) DO UPDATE SET rating=excluded.rating,comment=excluded.comment').run(id,user,input.rating,comment);
        return send(200,{success:true,message:'Feedback saved'});
      }
      fail(404,'Endpoint not found');
    } catch(e) { if(!res.headersSent) send(e.status || 500,{error:e.status?e.message:'Internal server error'}); else res.destroy(); }
  });
  server.on('close',()=>db.close());
  return server;
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const server=createGateway({databasePath:process.env.GRAPH_DB_PATH || './data/graph.sqlite'});
  server.listen(Number(process.env.PORT || 8080),process.env.HOST || '127.0.0.1',()=>console.log(`Graph gateway listening on ${server.address().port}; local graph, no live provider`));
  for(const signal of ['SIGINT','SIGTERM']) process.on(signal,()=>server.close(()=>process.exit(0)));
}
