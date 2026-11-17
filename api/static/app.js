/* Interactive government demo. No live government API or Altinn production services. */
const root = document.querySelector("#root");
const toast = document.querySelector("#toast");
const state = { me:null, page:"overview", metrics:null, cases:[], inbox:[], audit:[], delegations:[], registries:null, company:null, integrations:[], users:[], busy:false };
const e = (v) => String(v == null ? "" : v).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const niceDate = (s) => s ? new Date(s).toLocaleString("en-GB", {dateStyle:"medium",timeStyle:"short"}) : "—";
const label = (s) => s ? String(s).replace(/_/g," ").replace(/-/g," ") : "—";
const short = (s, max=95) => String(s||"").length > max ? String(s).slice(0,max)+"…" : String(s||"");
const pages = [
  ["overview","◫","Overview",()=>true],
  ["government","🇳🇵","For government",()=>true],
  ["native","⚙","Native Altinn",()=>true],
  ["services","▤","Services",r=>["citizen","director","accountant"].includes(r)],
  ["cases","◷","My applications",r=>r!=="observer"],
  ["delegations","♧","Delegated access",r=>["director","accountant"].includes(r)],
  ["officer","▣","Agency desk",r=>r==="officer"],
  ["inbox","✉","Nagarik inbox",r=>r!=="observer"],
  ["ecosystem","◇","Ecosystem map",()=>true],
  ["audit","≡","Audit & impact",r=>["observer","officer"].includes(r)]
];
async function request(url, opts={}) {
  const headers = {...(opts.body ? {"Content-Type":"application/json"} : {}),...(opts.headers||{})};
  if (opts.method && opts.method!=="GET" && state.me) headers["X-CSRF-Token"] = state.me.csrf_token;
  let res;
  try {res=await fetch(url,{credentials:"same-origin",...opts,headers});}
  catch {throw new Error("Cannot reach the demonstration service");}
  let data;try{data=await res.json();}catch{data={detail:"Unexpected server response"};}
  if (!res.ok) throw new Error(typeof data.detail==="string" ? data.detail : "Request failed ("+res.status+")");
  return data;
}
function notify(msg,error=false) {
  toast.innerHTML='<div class="notification '+(error?"error":"")+'">'+e(msg)+'</div>';
  clearTimeout(notify.timeout);notify.timeout=setTimeout(()=>toast.innerHTML="",4500);
}
async function boot(){
  try {state.users=await request("/api/demo-users");} catch {state.users=[];}
  try {state.me=await request("/api/me");await refresh();}catch{state.me=null;render();}
}
async function refresh(){
  const targets={metrics:"/api/metrics",cases:"/api/cases",inbox:"/api/inbox",audit:"/api/audit",delegations:"/api/delegations",registries:"/api/registries/me",company:"/api/registries/company",integrations:"/api/integrations"};
  const results=await Promise.allSettled(Object.entries(targets).map(async ([key,url])=>[key,await request(url)]));
  for(const result of results) if(result.status==="fulfilled"){
    const [key,val]=result.value;state[key]=key==="inbox"?val.notifications:key==="audit"?val.events:key==="cases"?val.cases:key==="delegations"?val.delegations:key==="integrations"?val.integrations:val;
  }
  render();
}
function navigate(page){state.page=page;render();window.scrollTo({top:0,behavior:"smooth"});}
function role(){return state.me?.user?.role||"guest";}
function badge(status){
  const css=status==="CONNECTED"?"approved":status==="SIMULATED"?"submitted":status==="NOT CONNECTED"?"rejected":String(status||"").toLowerCase();
  return '<span class="status '+e(css)+'">'+e(label(status))+'</span>';
}
function sidebar(){
  const r=role();
  return '<aside class="sidebar"><div class="brand"><span class="crest" aria-hidden="true">🇳🇵</span><div><strong>Nepal Digital Services</strong><small>Interoperability demonstrator</small></div></div>'+
    '<div class="side-label">Explore platform</div><nav class="nav" aria-label="Main navigation">'+
    pages.filter(p=>p[3](r)).map(p=>'<button data-nav="'+p[0]+'" class="'+(state.page===p[0]?"active":"")+'"><span class="nav-ico">'+p[1]+'</span>'+p[2]+'</button>').join("")+
    '</nav><div class="side-bottom">'+(state.me?'<div class="identity">'+e(state.me.user.name)+'<small>'+e(state.me.user.role_label)+'</small></div><a class="subtle-link" href="/auth/logout">⇄ Switch demo identity</a>':'<div class="identity">No active session<small>Choose a demo identity to begin.</small></div><a class="subtle-link" href="/auth/login">Sign in with NepalID →</a>')+
    '<p style="font-size:10px;color:#7894a5;line-height:1.5;margin-top:20px">Concept demonstration · synthetic data only · not affiliated with Nepal government</p></div></aside>';
}
function layout(body,title="Shared government services"){
  root.innerHTML='<div class="shell">'+sidebar()+'<div class="main"><header class="topbar"><div><div class="eyebrow">Nepal digital public services · illustrative demo</div><h1>'+e(title)+'</h1></div><div class="top-right"><span class="pill orange">SIMULATED AGENCY DATA</span><span class="pill">'+(state.me?e(state.me.user.role_label):"PUBLIC PREVIEW")+'</span></div></header><main class="content">'+body+'</main></div></div>';
}
function hero(eyebrow,title,desc,action,aside){
  return '<section class="hero"><div><div class="micro">'+e(eyebrow)+'</div><h2>'+title+'</h2><p>'+desc+'</p><div class="actions">'+action+'</div></div><div class="hero-side">'+aside+'</div></section>';
}
function stepAside(items,title="Follow the journey"){
  return '<h3>'+e(title)+'</h3>'+items.map((t,i)=>'<div class="step"><span class="step-bubble">'+(i+1)+'</span>'+e(t)+'</div>').join("");
}
function architecture(){
 return '<div class="diagram"><div class="branches">'+
 '<div class="layer">📱 Nagarik App<br><small>Existing mobile channel<br>not connected here</small></div>'+
 '<div class="layer">🌐 Nagarik Web<br><small>Possible future government channel<br>not built here</small></div>'+
 '<div class="layer">🖥 Visual demo<br><small>Browser simulator only<br>not a government channel</small></div>'+
 '</div><div class="arrow">↓ Possible shared government services (target architecture) ↓</div>'+
 '<div class="layer highlight">Reusable services: identity integration · authorization · agency processes · notifications<br><small style="font-weight:400;color:#c3d4df">This is a proposed design, not an already-connected Nepal system.</small></div>'+
 '<div class="arrow">↓ Today in this repository ↓</div>'+
 '<div class="branches">'+
 '<div class="layer">⚙ Actual Altinn App<br><small>Native .NET, BPMN, XACML<br>LocalTest shared-service emulators</small></div>'+
 '<div class="layer">🔐 Demo Keycloak login<br><small>Real OIDC protocol<br>synthetic identities, separate from LocalTest</small></div>'+
 '<div class="layer">📋 Simulator workflows<br><small>Separate local officer and delegation logic<br>not Altinn Access Management</small></div>'+
 '</div><div class="arrow">↓ Token-protected local bridge for synthetic data only ↓</div>'+
 '<div class="branches"><div class="layer">🪪 Civil registry<br><small>fake records</small></div><div class="layer">🚘 DoTM<br><small>fake licence lookup</small></div><div class="layer">🏢 Company registry<br><small>fake business records</small></div></div>'+
 '<div class="layer">✉ Simulated Nagarik-style inbox — no live mobile app connection</div></div>';
}
function governmentBrief(){
 return '<section class="hero"><div><div class="micro">A simple proposal for Nepal</div><h2>Keep Nagarik App.<br>Make government services easier to deliver.</h2><p>Nagarik App serves people on mobile today. We are demonstrating how government offices could share secure, reusable systems behind it. A future Nagarik Web could use those same services, if the government builds it with approved authentication and permissions.</p><div class="actions"><button class="btn primary" data-nav="ecosystem">See how the system could connect →</button><button class="btn ghost" data-nav="native">See actual Altinn code</button></div></div><div class="hero-side"><h3>सरल भाषामा</h3><p>नागरिक एप अहिले मोबाइलमा छ। हाम्रो उद्देश्य नयाँ एपले यसलाई बदल्नु होइन। कार्यालयका निवेदन, अभिलेख जाँच, अनुमति र सूचना दिने कामका लागि साझा प्रणाली उपयोगी हुन्छ कि भनेर नमुना देखाउने हो।</p><p>भविष्यमा सरकारले वेब सेवा उपलब्ध गराए पनि त्यसै साझा आधारबाट सेवा दिन सकिन्छ।</p></div></section>'+
 '<div class="section-heading"><div><h2>What would a citizen see?</h2><p>One small example: correcting an address on a driving licence.</p></div></div>'+
 '<div class="grid three">'+
 feature("📱","1. Apply on a familiar channel","Today: Nagarik mobile. In the future: potentially Nagarik Web, if approved and built.")+
 feature("🏛","2. Office processes the request","The responsible transport office checks existing records and an authorized employee makes a decision.")+
 feature("✉","3. Receive an update","The citizen sees an application status or notice in an approved channel. This demo inbox is only a mock.")+
 '</div>'+
 '<div class="section-heading"><div><h2>What value could government test?</h2><p>Reuse technology and compare outcomes, instead of building another front-end app.</p></div></div>'+
 '<div class="grid three">'+
 feature("🔁","Reuse across departments","Forms and processes could be built on common components instead of starting from scratch.")+
 feature("🤝","Who is allowed to act?","A company director could grant specific rights to an accountant, then withdraw them without sharing passwords.")+
 feature("🔎","Clear responsibility","Staff can see who received a request, who acted, and when it changed status.")+
 '</div>'+
 '<div class="section-heading"><h2>What is actually ready?</h2></div><div class="card"><div class="flow-row"><strong>GENUINE Altinn application</strong><span class="status approved">real app code</span></div><p>Runs native Altinn .NET form, BPMN process and policy, with official LocalTest emulators for shared services.</p><div class="flow-row"><strong>VISUAL Nepal scenarios</strong><span class="status submitted">simulated</span></div><p>Citizen, officer, accountant and business roles are illustrative and use only made-up data.</p><div class="flow-row"><strong>Real Nepal systems, BankID, Nagarik mobile integration</strong><span class="status rejected">not connected</span></div><p>These need government approval, verified identity integration, contracts and serious deployment work.</p></div>'+
 '<div class="mini-note"><strong>The next ask:</strong> One interested agency, one simple service, sample data and a technical contact. Run a pilot and measure whether the approach saves effort, improves accountability and remains under Nepal government control.</div>';
}

function nativeAltinn(){
 return hero("Official Altinn source · supported local stack",
 "Native Altinn Apps.<br>BPMN and XACML.",
 "This repository contains an actual .NET Altinn App with a service model, process, XACML policy and Altinn UI. LocalTest emulates shared Norwegian platform APIs. No production Nepali institution is connected.",
 '<a class="btn primary" href="http://local.altinn.cloud:8000/ttd/nepal-licence/" target="_blank" rel="noopener">Open native Altinn ↗</a><button class="btn ghost" data-nav="ecosystem">Explore integration stubs</button>',
 stepAside(["Start Altinn LocalTest with studioctl","Run real Altinn App runtime","Log in with LocalTest test user","Submit the native Altinn application"],"Native execution path"))+
 '<div class="section-heading"><div><h2>Native versus emulated</h2><p>Every layer is labelled precisely.</p></div></div><div class="grid three">'+
 feature("⚙","ACTUAL: Altinn Apps","Altinn.App.Api/Core, native form UI, model and process engine.")+
 feature("📋","ACTUAL: BPMN and XACML","Official Altinn app process and access policy, evaluated within the local stack.")+
 feature("🗄","EMULATED: Shared platform","LocalTest emulates storage, authentication and authorization APIs. National services are not deployed.")+
 '</div><div class="callout warn gap-top"><strong>Launch native Altinn on its own or alongside this simulator</strong><code class="endpoint">bash scripts/start-all.sh</code><p>Requires .NET 10, studioctl and Docker/Podman. LocalTest user accounts are separate from the sandbox Keycloak users.</p></div>'+
 '<div class="section-heading"><h2>Nepal registry integration</h2></div><div class="card"><h3>Native instantiation prefill</h3><p>The Altinn App registers a real IInstantiationProcessor and calls a replaceable INepalRegistryClient. That client calls a token-protected mock DoTM HTTP endpoint in combined mode, with a static synthetic fallback otherwise. No real DoTM API is connected.</p><span class="status submitted">SYNTHETIC ADAPTER</span></div>';
}

function landing(){
  const cards = [
    ["👤","Citizen","Sign in, prefill from registries, submit, track a licence correction."],
    ["🏢","Business director","Delegate narrowly scoped authority; no password sharing."],
    ["🧮","Accountant","Submit for a company only while a valid delegation exists."],
    ["👩‍💼","DoTM officer","Review applications, request information and issue a decision."],
    ["📊","Government observer","Watch cross-agency activity and reset the demonstration."]
  ];
  return hero("Digital public infrastructure · interactive pilot","One service journey.<br>Multiple government roles.","A visual, synthetic demonstration of citizen requests, officer decisions, company permissions and notifications. Real local OIDC login with fake users; not an official Nagarik mobile or web service.",'<a class="btn primary" href="/auth/login">Launch live journey →</a><button class="btn ghost" data-nav="ecosystem">Explore architecture</button>',stepAside(["Authenticate as a citizen or business","Exchange information between agencies","Process and approve a request","Deliver a result back to the inbox"],"A government service in four steps"))+
  '<div class="section-heading"><div><h2>Choose whose experience to explore</h2><p>Use one of these identities in NepalID. All demo accounts use the password <strong>Demo123!</strong></p></div></div><div class="login-people">'+cards.map((c,i)=>'<div class="persona"><div class="avatar">'+c[0]+'</div><strong>'+c[1]+'</strong><small>'+e(c[2])+'</small><div style="font-size:11px;margin-top:10px;color:#b57928;font-weight:800">'+["asha","raj","priya","maya","kiran"][i]+'</div></div>').join("")+'</div>'+
  '<div class="section-heading"><div><h2>What makes this different from another app?</h2><p>One reusable platform behind multiple channels and institutions.</p></div></div><div class="grid three">'+
  feature("🔐","Government-wide identity","Actual OIDC sign-in with a test identity provider, not just a fake login screen.")+
  feature("🤝","Delegated authority","A director authorizes and later revokes an accountant’s ability to act for a company.")+
  feature("🔗","Cross-agency workflow","Synthetic registries, transport records, approvals, an inbox, and an inspectable audit trail.")+
  '</div><div class="section-heading"><h2>Architecture at a glance</h2></div>'+architecture()+
  '<div class="mini-note"><strong>What you are seeing:</strong> This web portal is a presentation simulator, not Nagarik App or Nagarik Web. The repository also has a real native Altinn App running separately with LocalTest emulators. All government records here are fictional.</div>';
}
function feature(icon,title,desc){return '<div class="card"><div class="iconbox">'+icon+'</div><h3>'+title+'</h3><p>'+desc+'</p></div>';}
function overview(){
 const m=state.metrics||{};
 const action=role()==="officer"?'<button class="btn primary" data-nav="officer">Open officer desk →</button>':role()==="observer"?'<button class="btn primary" data-nav="audit">View government impact →</button>':role()==="director"?'<button class="btn primary" data-nav="delegations">Manage delegation →</button>':'<button class="btn primary" data-nav="services">Start an application →</button>';
 const items=role()==="officer"?["Open submitted requests","Verify application information","Record an approval or request changes","Applicant receives notification"]:role()==="observer"?["Monitor service activity","Follow event-by-event processing","Inspect connector readiness","Reset for the next presentation"]:["Authenticate with NepalID","Prefill from shared registries","Submit an application","Receive result in Nagarik inbox"];
 return hero("From digital access to digital service delivery","Build services once.<br>Reuse across government.","A concrete exploration of how Nepal’s existing citizen-facing ecosystem could connect to reusable identity, workflow, authorization and agency integrations.",action+'<button class="btn ghost" data-nav="ecosystem">Explore ecosystem</button>',stepAside(items))+
  '<div class="section-heading"><div><h2>Government service pulse</h2><p>Live counts from this self-contained demonstration; not national statistics.</p></div><span class="pill green">LOCAL SERVICES RUNNING</span></div><div class="grid four">'+
  kpi(m.cases||0,"Applications","Persisted in a local database")+
  kpi(m.awaiting_review||0,"Awaiting review","In government officer queue")+
  kpi(m.approved||0,"Approved","Test decision outcomes")+
  kpi(m.active_delegations||0,"Delegations","Active business authorizations")+
  '</div><div class="section-heading"><div><h2>A connected ecosystem</h2><p>See how one service spans multiple institutions.</p></div><button class="btn secondary small" data-nav="ecosystem">View all connections →</button></div><div class="grid two"><div>'+architecture()+'</div><div class="card"><h3>What to show a government official</h3>'+
  flow("01","Sign in","A local OIDC identity provider establishes a verified demo session.")+
  flow("02","Reuse registry data","No retyping a name, national identity number or company name.")+
  flow("03","Prove delegated access","Grant or revoke access for an accountant without sharing passwords.")+
  flow("04","Trace a decision","Officer processing, applicant notification and audit trail are connected.")+
  '</div></div><div class="mini-note">All government integrations shown are replaceable stubs. The reference architecture separates the citizen-facing experience from the services behind it.</div>';
}
function kpi(value,name,hint){return '<div class="card kpi"><div class="num">'+e(value)+'</div><div class="label">'+e(name)+'</div><div class="hint">'+e(hint)+'</div></div>';}
function flow(number,name,desc){return '<div class="flow-row"><span class="step-bubble">'+number+'</span><div style="flex:1"><strong>'+name+'</strong><small>'+desc+'</small></div></div>';}
function services(){
 const citizen=role()==="citizen", org=["director","accountant"].includes(role());
 const r=state.registries, co=state.company?.company;
 const intro='<div class="section-heading"><div><h2>Government services</h2><p>Choose a service. Data lookup and application routing are simulated agency connections.</p></div></div>';
 if(citizen){
  return intro+'<div class="grid two"><div class="card"><div class="item-title"><h3>🚘 Driving licence address correction</h3>'+badge("SIMULATED")+'</div><p>Department of Transport Management · an illustrative pilot service.</p><div class="callout"><strong>Automatic prefill from existing records</strong>Public registry and transport registry provide the values below. You only supply the requested correction.</div><form id="licence-form" class="form-grid gap-top">'+
  field("Full name",r?.person?.name||"Loading...","name",true)+field("Test national ID",r?.person?.nid||"—","nid",true)+field("Licence reference",r?.licence?.number||"—","licence",true)+field("Current address",r?.licence?.address||"—","address",true)+
  '<label class="field span2">New address<input name="new_address" required minlength="6" maxlength="160" placeholder="e.g. Ward 6, Kathmandu"></label><label class="field span2">Reason for correction<textarea name="reason" required minlength="4" maxlength="300" placeholder="Describe why the details should be updated"></textarea></label><button type="submit" class="btn dark span2">Submit to Department of Transport Management →</button></form></div>'+
  '<div class="card"><h3>What is happening behind the form?</h3>'+flow("1","Authenticate","NepalID local OIDC establishes identity.")+flow("2","Prefill","Mock civil registry and DoTM records are consulted.")+flow("3","Process","Shared workflow stores a submitted case for officer review.")+flow("4","Notify","Nagarik inbox-style view receives the decision.")+'<div class="callout warn gap-top"><strong>No government submission occurs.</strong>Everything in this example is synthetic. A legally accepted licence amendment would require integration with authorized DoTM systems and administrative approval.</div></div></div>';
 }
 if(org){
  const allowed=role()==="director" || state.delegations.some(d=>d.active===1 && d.grantee==="priya");
  return intro+'<div class="grid two"><div class="card"><div class="item-title"><h3>🏢 Transport operator permit renewal</h3>'+badge(allowed?"approved":"NOT CONNECTED")+'</div><p>Submit for <strong>Everest Logistics Pvt. Ltd.</strong> using a shared business registry identity.</p>'+
  (role()==="accountant"?'<div class="callout '+(allowed?"":"warn")+'"><strong>'+(allowed?"Delegation active":"Delegation required")+'</strong>'+(allowed?"Raj has granted Priya the transport-permit scope.":"Raj must grant Priya a transport-permit scope before the request will be accepted.")+'</div>':'<div class="callout"><strong>Director access</strong>As the synthetic registered director, Raj may submit directly or delegate the task.</div>')+
  '<form id="permit-form" class="form-grid gap-top">'+field("Registered company",co?.name||"Everest Logistics Pvt. Ltd.","company",true)+field("Company registry ID","COMP-100","org",true)+
  '<label class="field span2">Permit reference<input name="permit" value="TP-DEMO-221" minlength="5" maxlength="30" required></label><label class="field span2">Reason for renewal<textarea name="reason" minlength="4" maxlength="300" required>Annual operator permit renewal</textarea></label><button type="submit" class="btn dark span2">Submit company application →</button></form></div>'+
  '<div class="card"><h3>Why delegation matters</h3><p>Authentication answers who logged in. Authorization answers what that person may do for a particular company.</p>'+
  flow("1","Raj is a company director","Business representation is derived from synthetic registry data.")+
  flow("2","Raj grants Priya a limited right","Only transport-permit submission is covered.")+
  flow("3","Priya signs in independently","Her own OIDC identity is checked.")+
  flow("4","Revoke and test denial","The permission can be removed immediately.")+
  '<button class="btn secondary gap-top" data-nav="delegations">Manage delegated authorization →</button></div></div>';
 }
 return '<div class="empty">This identity has a review or oversight role. Select the Agency Desk or Audit & impact page.</div>';
}
function field(name,value,id,readonly=false){return '<label class="field">'+e(name)+'<input name="'+id+'" value="'+e(value)+'" '+(readonly?"readonly":"")+'></label>';}
function cases(){
 let list=state.cases||[];
 return '<div class="section-heading"><div><h2>Applications and decisions</h2><p>Persistent example applications, visible only to authorized demo roles.</p></div><button class="btn secondary small" data-nav="services">New application →</button></div>'+
 (list.length?'<div class="grid two">'+list.map(c=>'<div class="card"><div class="item-title"><strong>'+e(c.id)+'</strong>'+badge(c.status)+'</div><h3>'+e(c.service_name)+'</h3><p>'+e(c.agency)+'</p><div class="metadata"><span>Submitted by '+e(c.applicant)+'</span><span>'+niceDate(c.created_at)+'</span></div><hr class="divider"><div class="muted">'+Object.entries(c.payload).map(([key,value])=>'<div style="margin:6px 0"><strong>'+e(label(key))+':</strong> '+e(short(value,120))+'</div>').join("")+'</div>'+(c.decision_note?'<div class="callout gap-top"><strong>Officer decision</strong>'+e(c.decision_note)+'</div>':'')+(c.verification_url?'<a class="btn secondary small gap-top" target="_blank" rel="noopener" href="'+e(c.verification_url)+'" style="display:inline-block;text-decoration:none">Verify demonstration decision ↗</a>':'')+'</div>').join("")+'</div>':'<div class="empty">No applications in your authorized view. Submit an application, or ask the director to grant representation.</div>');
}
function delegations(){
 const r=role(), d=state.delegations||[], active=d.filter(x=>x.active===1);
 return '<div class="section-heading"><div><h2>Delegated representation</h2><p>Demonstrate scoped company authorization, rather than sharing passwords.</p></div></div>'+
 '<div class="grid two"><div class="card"><div class="item-title"><h3>🏢 Everest Logistics Pvt. Ltd.</h3>'+badge(active.length?"approved":"submitted")+'</div><p>Synthetic business registration <strong>COMP-100</strong></p><div class="callout"><strong>'+(r==="director"?"You are the registered director":"You are an independent accountant")+'</strong>'+(r==="director"?"You can grant or revoke Priya’s right to submit a transport operator permit.":"You can only act on this company's behalf while Raj has granted the relevant permission.")+'</div>'+
 (r==="director"?'<button class="btn dark gap-top" data-action="grant" '+(active.length?"disabled":"")+'>Grant Priya permission →</button>':'<button class="btn secondary gap-top" data-nav="services">Try company application →</button>')+
 '</div><div class="card"><h3>Authorization ledger</h3>'+(d.length?d.map(x=>'<div class="record"><div class="item-title"><strong>'+e(x.grantee)+' → '+e(x.organisation_id)+'</strong>'+badge(x.active?"approved":"rejected")+'</div><p>Scope: <strong>'+e(x.scope)+'</strong></p><small>Granted by '+e(x.grantor)+' · '+niceDate(x.created_at)+'</small>'+(r==="director"&&x.active?'<div><button class="btn danger small gap-top" data-revoke="'+x.id+'">Revoke now</button></div>':'')+'</div>').join(""):'<div class="empty">No delegations recorded. Start by granting Priya a limited permission.</div>')+'</div></div>'+
 '<div class="section-heading"><h2>Why this is different from a login</h2></div><div class="grid three">'+feature("👤","Separate identities","Priya never needs Raj’s password.")+feature("🎯","Scoped permission","The grant applies to a defined service, not the whole account.")+feature("🛑","Revocable rights","After revocation, a new company submission is blocked server-side.")+'</div>';
}
function officer(){
 const list=state.cases||[];
 return '<div class="section-heading"><div><h2>Department of Transport Management</h2><p>Officer workspace · illustrative government review workflow</p></div><span class="pill green">'+list.filter(c=>c.status==="submitted"||c.status==="needs-info").length+' ACTIONABLE</span></div>'+
 '<div class="callout"><strong>Agency access control</strong>Only the officer identity may record government decisions. Citizen and accountant sessions cannot use this API endpoint.</div>'+
 '<div class="grid two gap-top">'+(list.length?list.map(c=>'<div class="card" data-case="'+e(c.id)+'"><div class="item-title"><strong>'+e(c.id)+'</strong>'+badge(c.status)+'</div><h3>'+e(c.service_name)+'</h3><div class="muted">Applicant: '+e(c.applicant)+' · '+niceDate(c.created_at)+'</div><hr class="divider"><div class="muted">'+Object.entries(c.payload).map(([k,v])=>'<div style="margin:6px 0"><strong>'+e(label(k))+':</strong> '+e(short(v))+'</div>').join("")+'</div>'+
 ((c.status==="approved"||c.status==="rejected")?'<p><strong>Decision already recorded.</strong> '+e(c.decision_note||"")+'</p>':'<div class="form-grid gap-top"><label class="field">Decision<select data-decision><option value="approved">Approve</option><option value="needs-info">Request more information</option><option value="rejected">Reject</option></select></label><label class="field span2">Officer note<textarea data-note placeholder="Reason for the decision" required>Verified against synthetic records</textarea></label><button class="btn dark span2" data-review="'+e(c.id)+'">Record official demo decision →</button></div>')+'</div>').join(""):'<div class="empty">No cases in the queue.</div>')+'</div>';
}
function inbox(){
 return '<div class="section-heading"><div><h2>Nagarik-style demo inbox</h2><p>Visualizes how the existing mobile Nagarik channel might receive events in a future approved integration.</p></div>'+badge("SIMULATED")+'</div>'+
 '<div class="callout warn"><strong>Not connected to the real mobile Nagarik App, nor a future Nagarik Web.</strong> These notifications are produced by the local workflow and stored in this demonstration database. A real deployment needs a government-approved Nagarik integration.</div>'+
 '<div class="card gap-top">'+((state.inbox||[]).length?state.inbox.map(n=>'<div class="record"><div class="item-title"><h3>✉ '+e(n.title)+'</h3><small>'+niceDate(n.created_at)+'</small></div><p>'+e(n.body)+'</p>'+(n.case_id?'<span class="endpoint">'+e(n.case_id)+'</span>':'')+'</div>').join(""):'<div class="empty">No messages. Submit an application or have an officer decide one.</div>')+'</div>';
}
function ecosystem(){
 let data=state.integrations||[];
 return '<div class="section-heading"><div><h2>Visual ecosystem map</h2><p>Compare the existing mobile channel, possible future web access and actual local demo components.</p></div></div>'+
 '<div class="grid two"><div>'+architecture()+'</div><div class="card"><h3>Integration principles</h3>'+flow("1","Nagarik stays the front door","Nagarik App is mobile today; this demo portal is not official Nagarik Web.")+flow("2","OIDC establishes identity","Real local authentication; not identity proofing.")+flow("3","Common authorization governs access","Narrowly scoped grants and officer permissions.")+flow("4","Agency systems remain authoritative","Public and transport records are looked up, not replaced.")+flow("5","Decisions return to citizens","Inbox notification and a demo verification reference.")+'</div></div>'+
 '<div class="section-heading"><div><h2>Connection readiness</h2><p>Green = actual demo component. Amber = synthetic integration. Red = not yet connected.</p></div></div><div class="grid three">'+data.map(d=>'<div class="card integration"><div class="head"><h3>'+e(d.label)+'</h3>'+badge(d.status)+'</div><p>'+e(d.description)+'</p><code>'+e(d.key)+'</code></div>').join("")+'</div>'+
 '<div class="mini-note"><strong>Native Altinn clarification:</strong> the local workflow, authorisation and audit shown here are demo implementations inspired by Altinn. They are not the Norwegian Altinn platform source running underneath this interface. This separation is intentional so the demonstration is reproducible, honest and easy to replace with official platform integrations.</div>';
}
function audit(){
 const m=state.metrics||{}, events=state.audit||[];
 return '<div class="section-heading"><div><h2>Audit & government impact</h2><p>Explain the platform without discussing code or infrastructure details.</p></div>'+(role()==="observer"?'<button class="btn danger small" data-action="reset">Reset demo to sample data</button>':'')+'</div>'+
 '<div class="grid four">'+kpi(m.services||2,"Service templates","Built on shared infrastructure")+kpi(m.agency_integrations||0,"Live agency APIs","Current government connections")+kpi(m.active_delegations||0,"Active grants","Scoped business representation")+kpi(m.audit_events||0,"Recorded events","Traceable sample activity")+'</div>'+
 '<div class="grid two gap-top"><div class="card"><h3>Recent event timeline</h3><div class="timeline gap-top">'+(events.length?events.slice(0,18).map(v=>'<div class="event"><strong>'+e(label(v.action))+' · '+e(v.actor)+'</strong><small>'+niceDate(v.created_at)+(v.case_id?' · '+e(v.case_id):'')+'</small><p>'+e(v.detail)+'</p></div>').join(""):'<div class="empty">No activity yet.</div>')+'</div></div>'+
 '<div class="card"><h3>What the government should evaluate</h3>'+flow("✓","Speed","Time to create another service using common components.")+flow("✓","Security","Separation of authentication, authorization and agency approval.")+flow("✓","Accountability","Who performed each action and for which application.")+flow("✓","Interoperability","Replaceable connectors for national and agency registries.")+flow("✓","Independence","Ability for local teams to operate and extend infrastructure.")+
 '<div class="callout warn gap-top"><strong>These are demonstration metrics, not evidence of national impact.</strong> A pilot should measure development effort, processing time, support load, reliability and actual costs.</div></div></div>';
}
function render(){
 const title={overview:"Government service overview",government:"For government leaders",native:"Native Altinn application",services:"Apply for a service",cases:"Applications & decisions",delegations:"Representation & permissions",officer:"DoTM agency workspace",inbox:"Citizen service inbox",ecosystem:"Connected government map",audit:"Oversight & audit"}[state.page]||"Nepal Digital Government";
 const r=role(), allowed=pages.some(p=>p[0]===state.page && p[3](r));
 if(!allowed)state.page="overview";
 let content;
 if(!state.me)content=state.page==="government"?governmentBrief():state.page==="native"?nativeAltinn():state.page==="ecosystem"?'<div class="section-heading"><h2>Architecture preview</h2></div>'+architecture()+'<div class="actions"><a class="btn dark" href="/auth/login">Sign in to interact →</a></div><div class="mini-note">Only NepalID is a real local OIDC connection. No Nepali government system is connected.</div>':landing();
 else content=({overview,government:governmentBrief,native:nativeAltinn,services,cases,delegations,officer,inbox,ecosystem,audit}[state.page]||overview)();
 layout(content,title);
}
root.addEventListener("click",async(ev)=>{
 const nav=ev.target.closest("[data-nav]");if(nav){navigate(nav.dataset.nav);return;}
 const action=ev.target.closest("[data-action]");if(action){
  try{
   if(action.dataset.action==="grant"){await request("/api/delegations",{method:"POST",body:JSON.stringify({grantee:"priya",scope:"transport-permit"})});notify("Priya now has the transport-permit permission. Sign in as Priya to try it.");}
   if(action.dataset.action==="reset"){if(!confirm("Reset all example cases, notifications and delegations?"))return;await request("/api/demo/reset",{method:"POST",body:"{}"});notify("Demo reset to synthetic sample data.");}
   await refresh();
  }catch(err){notify(err.message,true);}
  return;
 }
 const rev=ev.target.closest("[data-revoke]");if(rev){
  try{await request("/api/delegations/"+encodeURIComponent(rev.dataset.revoke),{method:"DELETE"});notify("Delegation revoked immediately.");await refresh();}
  catch(err){notify(err.message,true);}return;
 }
 const btn=ev.target.closest("[data-review]");if(btn){
  const panel=btn.closest("[data-case]");const decision=panel.querySelector("[data-decision]").value;const note=panel.querySelector("[data-note]").value;
  try{await request("/api/cases/"+encodeURIComponent(btn.dataset.review)+"/decision",{method:"PATCH",body:JSON.stringify({status:decision,note})});notify("Decision recorded. Applicant inbox updated.");await refresh();}
  catch(err){notify(err.message,true);}
 }
});
root.addEventListener("submit",async(ev)=>{
 const form=ev.target;if(!["licence-form","permit-form"].includes(form.id))return;
 ev.preventDefault();if(state.busy)return;state.busy=true;
 const values=Object.fromEntries(new FormData(form).entries());
 const payload=form.id==="licence-form"?{service:"licence-correction",new_address:values.new_address,reason:values.reason}:{service:"transport-permit",permit:values.permit,reason:values.reason};
 try{const response=await request("/api/cases",{method:"POST",body:JSON.stringify(payload)});notify("Application "+response.case_id+" submitted to the agency desk.");await refresh();navigate("cases");}
 catch(err){notify(err.message,true);}finally{state.busy=false;}
});
boot();
