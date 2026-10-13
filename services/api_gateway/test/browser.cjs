const {spawn}=require('node:child_process');
const assert=require('node:assert/strict');
const {mkdtempSync,rmSync}=require('node:fs');
const {tmpdir}=require('node:os');
const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright-core');
(async()=>{
 const dir=mkdtempSync(path.join(tmpdir(),'onchain-browser-'));
 const port=18080;const processServer=spawn(process.execPath,['server.js'],{cwd:path.resolve(__dirname,'..'),env:{...process.env,API_TOKEN:'',PORT:String(port),GRAPH_DB_PATH:path.join(dir,'graph.sqlite')},stdio:['ignore','pipe','inherit']});
 let browser;
 try{
  let ready=false;for(let i=0;i<100;i++){try{const r=await fetch(`http://127.0.0.1:${port}/v1/health`);if(r.ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,100));}assert(ready,'gateway failed to start');
  browser=await chromium.launch({headless:true,...(process.env.CHROME_BIN?{executablePath:process.env.CHROME_BIN}:{}),args:['--no-sandbox']});
  for(const width of [1280,390]){
   const page=await browser.newPage({viewport:{width,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(`http://127.0.0.1:${port}`);await page.getByText('No live chain or AI provider',{exact:false}).waitFor();
   await page.getByLabel('Name',{exact:true}).fill(`Treasury ${width}`);await page.getByLabel('Ethereum address').fill('bad');await page.getByRole('button',{name:'Add entity',exact:true}).click();await page.getByRole('status').filter({hasText:'Address must contain'}).waitFor();
   await page.getByLabel('Ethereum address').fill('0x'+String(width===1280?'a':'b').repeat(40));await page.getByRole('button',{name:'Add entity',exact:true}).click();await page.getByRole('status').filter({hasText:'Entity saved'}).waitFor();
   await page.getByLabel('Name',{exact:true}).fill(`Exchange ${width}`);await page.getByLabel('Type',{exact:true}).selectOption('EXCHANGE');await page.getByRole('button',{name:'Add entity',exact:true}).click();await page.getByRole('button',{name:`Exchange ${width}`,exact:false}).waitFor();
   await page.getByLabel('From',{exact:true}).selectOption({label:`Treasury ${width}`});await page.getByLabel('To',{exact:true}).selectOption({label:`Exchange ${width}`});await page.getByRole('button',{name:'Connect entities'}).click();await page.getByRole('status').filter({hasText:'Connection saved'}).waitFor();
   await page.locator('#network').getByText(`Treasury ${width} → TRANSACTS_WITH → Exchange ${width}`,{exact:true}).waitFor();
   await page.reload();await page.getByRole('button',{name:`Treasury ${width}`,exact:false}).waitFor();
   await page.getByLabel('Search entities').fill(`Treasury ${width}`);await page.getByRole('button',{name:`Treasury ${width}`,exact:false}).click();await page.locator('#network').getByText(`Treasury ${width} → TRANSACTS_WITH → Exchange ${width}`,{exact:true}).waitFor();
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`overflow at ${width}`);assert.deepEqual(errors,[]);await page.close();
  }
  console.log('PASS: real graph creation, validation, relationships, reload, search, desktop/mobile browser');
 }finally{if(browser)await browser.close();processServer.kill('SIGTERM');await new Promise(r=>processServer.on('exit',r));rmSync(dir,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
