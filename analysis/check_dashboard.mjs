/* Validate the generated offline UI in a real Chromium instance via local CDP. */
import {spawn} from 'node:child_process';
import {readFile,writeFile,mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const profile=await mkdtemp(join(tmpdir(),'platonic-browser-'));
const port=9400+process.pid%400;
const httpPort=port+500;
const server=spawn('python3',['-m','http.server',String(httpPort),'--bind','127.0.0.1','--directory',join(root,'visualizations')],{stdio:'ignore'});
const browser=spawn('chromium',['--headless','--no-sandbox','--disable-gpu','--no-first-run',
 '--no-default-browser-check','--remote-debugging-address=127.0.0.1',`--remote-debugging-port=${port}`,
 `--user-data-dir=${profile}`,'--window-size=1440,1400','about:blank'],{stdio:['ignore','ignore','pipe']});
let errors='',ws;
browser.stderr.on('data',chunk=>{errors+=chunk.toString()});
const delay=ms=>new Promise(r=>setTimeout(r,ms));
try{
 let tabs;
 for(let i=0;i<60;i++){
  try{tabs=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();if(tabs.some(t=>t.type==='page'))break}catch{}
  await delay(100);
 }
 if(!tabs)throw Error('Chromium did not start: '+errors.slice(-500));
 ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
 await new Promise((yes,no)=>{ws.addEventListener('open',yes,{once:true});ws.addEventListener('error',no,{once:true})});
 let sequence=0;const pending=new Map();const runtimeErrors=[];
 ws.addEventListener('message',message=>{const item=JSON.parse(message.data);if(item.method==='Runtime.exceptionThrown')runtimeErrors.push(item.params.exceptionDetails.text);if(item.id){const p=pending.get(item.id);pending.delete(item.id);item.error?p.reject(Error(JSON.stringify(item.error))):p.resolve(item.result)}});
 function command(method,params={}){return new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))})}
 const evaluate=async expression=>{const result=await command('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw Error(JSON.stringify(result.exceptionDetails));return result.result.value};
 await command('Page.enable');await command('Runtime.enable');
 for(let i=0;i<30;i++){try{if((await fetch(`http://127.0.0.1:${httpPort}/dashboard.html`)).ok)break}catch{}await delay(100)}
 const navigation=await command('Page.navigate',{url:`http://127.0.0.1:${httpPort}/dashboard.html`});
 if(navigation.errorText)throw Error('Page navigation: '+navigation.errorText);
 for(let i=0;i<60;i++){if(await evaluate("document.querySelectorAll('[data-seed]').length===210"))break;await delay(100)}
 const checks=[];
 async function check(name,expression){const ok=await evaluate(expression);if(!ok)throw Error(name);checks.push(name)}
 if(!await evaluate("document.querySelectorAll('[data-seed]').length===210")){
  console.log('Browser diagnostic:',await evaluate("JSON.stringify({url:location.href,ready:document.readyState,title:document.title,body:document.body?.innerText.slice(0,1000),count:document.querySelectorAll('[data-seed]').length})"),runtimeErrors);
 }
 await check('All 210 default observations rendered',"document.querySelectorAll('[data-seed]').length===210");
 await check('Default topology and independent-cost workload',"document.getElementById('solid').value==='icosahedron'&&document.getElementById('workload').value==='lognormal'");
 await check('Twelve workers and master in geometry',"document.querySelectorAll('#geometry circle').length===13");
 await evaluate("document.getElementById('solid').value='dodecahedron';document.getElementById('workload').value='clustered';document.getElementById('solid').dispatchEvent(new Event('change',{bubbles:true}));");
 await check('Topology and workload controls redraw every observation',"document.querySelectorAll('#geometry circle').length===21&&document.querySelectorAll('[data-seed]').length===210");
 await check('Displayed interval matches saved source',"document.getElementById('push-effect').textContent.startsWith(DATA.effects['dodecahedron|clustered|static'].mean.toFixed(3)+'×')");
 await evaluate("document.getElementById('metric').value='bytes';document.getElementById('metric').dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('table-toggle').click();");
 await check('Traffic metric and accessible table work',"!document.getElementById('data-table').hidden&&document.querySelectorAll('#data-table tbody tr').length===7&&document.querySelector('#data-table tbody td:nth-child(2)').textContent.includes('MiB')");
 await evaluate("document.getElementById('workload').value='constant';document.getElementById('workload').dispatchEvent(new Event('change',{bubbles:true}));");
 await check('Equal-cost null result retained',"document.getElementById('push-effect').textContent.startsWith('1.000×')");
 const before=await evaluate("document.querySelector('#geometry line').getAttribute('x2')");
 await evaluate("document.getElementById('rotation').value=150;document.getElementById('rotation').dispatchEvent(new Event('input',{bubbles:true}));");
 const after=await evaluate("document.querySelector('#geometry line').getAttribute('x2')");if(before===after)throw Error('Geometry rotation did not redraw');checks.push('Rotation changes the projected geometry');
 await evaluate("document.getElementById('solid').value='icosahedron';document.getElementById('workload').value='lognormal';document.getElementById('metric').value='makespan_ms';document.getElementById('rotation').value=35;document.getElementById('solid').dispatchEvent(new Event('change',{bubbles:true}));if(!document.getElementById('data-table').hidden)document.getElementById('table-toggle').click();");
 await command('Emulation.setDeviceMetricsOverride',{width:1440,height:1400,deviceScaleFactor:1,mobile:false});
 await delay(100);
 let layout=await command('Page.getLayoutMetrics');let size=layout.cssContentSize;
 let capture=await command('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:1440,height:Math.ceil(size.height),scale:1}});
 await writeFile(join(root,'visualizations/dashboard-desktop.png'),Buffer.from(capture.data,'base64'));
 await command('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 await delay(100);
 await check('Mobile layout has no page-level horizontal overflow',"document.documentElement.scrollWidth<=window.innerWidth+1");
 layout=await command('Page.getLayoutMetrics');size=layout.cssContentSize;
 capture=await command('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:390,height:Math.ceil(size.height),scale:1}});
 await writeFile(join(root,'visualizations/dashboard-mobile.png'),Buffer.from(capture.data,'base64'));
 if(runtimeErrors.length)throw Error('Runtime errors: '+runtimeErrors.join('; '));checks.push('No JavaScript runtime exceptions');
 await writeFile(join(root,'results/dashboard-verification.json'),JSON.stringify({engine:'Chromium via local CDP',checks,passed:checks.length,screenshots:['visualizations/dashboard-desktop.png','visualizations/dashboard-mobile.png'],runtime_external_dependencies:0},null,2)+'\n');
 console.log(`Dashboard passed ${checks.length} real-browser checks; desktop and mobile screenshots saved.`);
}finally{if(ws)ws.close();browser.kill('SIGTERM');server.kill('SIGTERM');await delay(250);await rm(profile,{recursive:true,force:true}).catch(()=>{})}
