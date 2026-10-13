const {chromium}=require('playwright-core');
const {spawn}=require('node:child_process');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
  const port=3191,base=process.env.ETH_UI_BASE_URL||`http://127.0.0.1:${port}`;
  let server=null;
  if(!process.env.ETH_UI_BASE_URL){
    const path=require('node:path'),appRoot=path.resolve(__dirname,'..');
    const standalone=path.join(appRoot,'.next','standalone','services','ui','nextjs-app');
    assert(fs.existsSync(path.join(standalone,'server.js')),'Run the standalone UI build before browser tests');
    fs.cpSync(path.join(appRoot,'.next','static'),path.join(standalone,'.next','static'),{recursive:true});
    if(fs.existsSync(path.join(appRoot,'public')))fs.cpSync(path.join(appRoot,'public'),path.join(standalone,'public'),{recursive:true});
    server=spawn(process.execPath,[path.join(standalone,'server.js')],{
      cwd:standalone,stdio:'inherit',env:{...process.env,PORT:String(port),HOSTNAME:'127.0.0.1'}
    });
  }
  let browser;
  try {
    let ready=false;
    for(let i=0;i<100;i++){try{const r=await fetch(base);if(r.ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,200));}
    assert(ready,'Next server did not become ready');
    browser=await chromium.launch({args:['--no-sandbox']});
    const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];
    page.on('pageerror',error=>errors.push({route:new URL(page.url()).pathname,message:error.message}));
    for(const route of ['/','/status','/ontology','/api-gateway']){
      const r=await page.goto(base+route);assert.equal(r.status(),200,route);
      await page.getByRole('note').waitFor();
      assert.match(await page.getByRole('note').textContent(),/illustrative/);
      await page.waitForTimeout(250);
    }
    await page.goto(base+'/api/gateway');assert.equal(new URL(page.url()).pathname,'/api-gateway');
    fs.mkdirSync('artifacts',{recursive:true});
    await page.goto(base+'/status');await page.screenshot({path:'artifacts/legacy-status-desktop.png',fullPage:true});
    await page.setViewportSize({width:390,height:844});await page.goto(base+'/');
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile page overflows viewport');
    await page.screenshot({path:'artifacts/legacy-home-mobile.png',fullPage:true});
    assert.deepEqual(errors,[],'Browser runtime errors');
    console.log('Legacy Next real browser: routes, provenance, redirect, rendered status and mobile layout pass.');
  } finally {if(browser)await browser.close();if(server)server.kill('SIGTERM');}
})().catch(error=>{console.error(error);process.exitCode=1;});
