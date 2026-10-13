const {chromium}=require('playwright-core');
const {spawn}=require('node:child_process');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
  const port=3191,base=`http://127.0.0.1:${port}`;
  const server=spawn(process.execPath,[require.resolve('next/dist/bin/next'),'start','--hostname','127.0.0.1','--port',String(port)],{stdio:'inherit'});
  let browser;
  try {
    let ready=false;
    for(let i=0;i<100;i++){try{const r=await fetch(base);if(r.ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,200));}
    assert(ready,'Next server did not become ready');
    browser=await chromium.launch({args:['--no-sandbox']});
    const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];
    page.on('pageerror',error=>errors.push(error.message));
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
  } finally {if(browser)await browser.close();server.kill('SIGTERM');}
})().catch(error=>{console.error(error);process.exitCode=1;});
