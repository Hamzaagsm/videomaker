#!/usr/bin/env python3
# MEER v4.45 - MERI SCRIPT SMART SCENE MATCHING (Hamza ki demand 2026-10-21:
# "jo bola jaye usi ka scene khud aa jaye")
# Saboot: uski dusri video (160s) MERI SCRIPT se bani thi - apni ~30 lines wali kahani School
# select karke paste ki; purana code clips[i2 % 6] cycle se wohi 6 scenes ghumata raha.
# AB: suspMyMakeVideo poori suspense library ko ek pool bana kar har line ke alfaaz se
# sab-se-milta scene khud chunti hai. Matching ki khubiyan:
#  - ek scene ek video me SIRF ek dafa (repeat namumkin)
#  - token weight = rarity (idf): 'darwaza' jaisa khaas lafz 'raat/purana' jaise aam lafzon
#    se zyada wazan rakhta hai - is liye sahi scene jeet-ta hai
#  - Roman Urdu + Devanagari dono ke liye synonym bridge (darwaza/दरवाज़ा -> door)
#  - stopwords (aur/ka/ki/the/and...) score me shamil nahi; English stemming (opened->open)
#  - select ki hui kahani ke scenes pool me pehle (tie-break uske haq me)
# Sirf v4.43 ki apni suspMyMakeVideo function replace hoti hai - baqi sab kuch waisa ka waisa.
import re

HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.45"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.45 MEER", html)
print('V445 APP_VER bump:', n1, n2)

NEW_FN = r"""async function suspMyMakeVideo(){
  try{
    if(typeof RealClipBridge==='undefined'||typeof RealClipBridge.composeVideo!=='function'){ alert('Ye feature MEER app me chalega!'); return; }
    var ta=document.getElementById('suspMyScript');
    var raw=ta?ta.value.trim():'';
    if(!raw){ alert('Pehle apni kahani ki lines likho!'); return; }
    var lines=raw.split(/\n+/).map(function(s){ return s.trim(); }).filter(function(s){ return s.length>1; });
    if(!lines.length){ alert('Lines samajh nahi ayin - har line alag likho!'); return; }
    var story=suspPickStory();
    if(!story){ alert('Pehle kahaniyan load hone do (internet on rakho)!'); return; }
    /* v4.45 SMART MATCHING: poori library pool; har line ke liye rarity-weighted alfaaz-match;
       ek scene ek video me sirf EK dafa (purana i%6 cycle KHATAM) */
    var SYN={darwaza:'door',darwaze:'door',darwaza2:'door',ghanti:'bell',seedhi:'stairs',seedhiyan:'stairs',kamra:'room',kamre:'room',khirki:'window',khidki:'window',raat:'night',subah:'morning',sham:'evening',purana:'old',purani:'old',band:'closed',bandh:'closed',khula:'open',khul:'open',khuli:'open',awaaz:'voice',awaz:'voice',awazein:'voice',diwar:'wall',deewar:'wall',tasveer:'picture',tasveerein:'picture',bacha:'child',bachcha:'child',bachche:'child',ladka:'boy',ladki:'girl',kitab:'book',kitabein:'book',pani:'water',phool:'flower',bagh:'garden',fawwara:'fountain',phawara:'fountain',qila:'fort',kila:'fort',ghanta:'clock',ghantaghar:'clock',ghari:'clock',roshni:'light',mashal:'torch',mashaal:'torch',makan:'house',lifafa:'envelope',lifafe:'envelope',khat:'letter',khatoot:'letter',mohar:'seal',zanjeer:'chain',zanjir:'chain',tala:'lock',talay:'lock',kuan:'well',kuwa:'well',jhoola:'cradle',mez:'table',kursi:'chair',dastak:'knock',cheekh:'scream',andhera:'dark',dhool:'dust',barish:'rain',baarish:'rain',hawa:'wind',jangal:'forest',darakht:'tree',ped:'tree',pul:'bridge',nadi:'river',samandar:'sea',kashti:'boat',gari:'car',gaari:'car',gaon:'village',sheher:'town',bazaar:'market',dukkan:'shop',kutta:'dog',billi:'cat',ghora:'horse',hathi:'elephant',haathi:'elephant',saanp:'snake',chirya:'bird',titli:'butterfly',jugnu:'fireflies',jugnoo:'fireflies',chaand:'moon',chand:'moon',chandni:'moonlight',suraj:'sun',tare:'stars',taare:'stars',badal:'clouds',barf:'snow',aag:'fire',dhuan:'smoke',dhuwaan:'smoke',saaya:'shadow',saya:'shadow',khwab:'dream',khwaab:'dream',neend:'sleep',chhat:'roof',aangan:'courtyard',minar:'tower',meenar:'tower',burj:'tower',waqt:'time',samay:'time',dar:'fear',khauf:'fear',khushi:'happy',dukhi:'sad',raaz:'secret',kitaab:'book',qalam:'pen',kaghaz:'paper',darwaaza:'door'};
    var DEV={'दरवाज़ा':'door','दरवाज़े':'door','दरवाजा':'door','घंटी':'bell','घंटा':'bell','रात':'night','सुबह':'morning','शाम':'evening','पुराना':'old','पुरानी':'old','आवाज़':'voice','आवाज़ें':'voice','खिड़की':'window','दीवार':'wall','तस्वीर':'picture','तस्वीरें':'picture','बच्चा':'child','बच्चे':'child','लड़का':'boy','लड़की':'girl','किताब':'book','पानी':'water','फूल':'flower','बाग़':'garden','फ़व्वारा':'fountain','क़िला':'fort','घंटाघर':'clock','घड़ी':'clock','रोशनी':'light','मशाल':'torch','मकान':'house','हवेली':'haveli','लिफ़ाफ़ा':'envelope','ख़त':'letter','मोहर':'seal','ज़ंजीर':'chain','ताला':'lock','कुआँ':'well','झूला':'cradle','मेज़':'table','कुर्सी':'chair','स्कूल':'school','गाँव':'village','शहर':'town','बारिश':'rain','हवा':'wind','जंगल':'forest','दरख़्त':'tree','पुल':'bridge','नदी':'river','चाँद':'moon','सूरज':'sun','आग':'fire','साया':'shadow','ख़्वाब':'dream','नींद':'sleep','छत':'roof','आँगन':'courtyard','मीनार':'tower','कमरा':'room','कमरे':'room','सीढ़ी':'stairs','सीढ़ियाँ':'stairs','सीढ़ियों':'stairs','बंद':'closed','खुला':'open','खुल':'open','कदमों':'footsteps','कदम':'footsteps','रोने':'crying','रोना':'crying','हिल':'moving','हिलने':'moving','हिलता':'moving','हिलती':'moving','हिलता':'moving','बज':'ringing','बजने':'ringing','बजी':'ringing','खड़खड़ाया':'rattled','चरमराकर':'creaked','भागा':'ran','भागी':'ran','भागकर':'ran','खड़ा':'stood','खड़ी':'stood','बैठ':'sat','देखा':'saw','देख':'saw','सुना':'heard','सुनाई':'heard','आया':'came','आई':'came','आयी':'came','गया':'went','गई':'went','रखा':'kept','रखी':'kept','रखे':'kept','लटकी':'hanging','लटके':'hanging','जलाई':'lit','रोशनी2':'light','बत्ती':'lamp','बत्तियाँ':'lamp','लैंप':'lamp','मोमबत्ती':'candle','तस्वीर2':'picture'};
    var STOP={the:1,and:1,was:1,were:1,with:1,from:1,that:1,this:1,had:1,has:1,her:1,his:1,all:1,but:1,not:1,into:1,over:1,when:1,then:1,there:1,here:1,its:1,it:1,in:1,on:1,of:1,to:1,a:1,an:1,he:1,she:1,they:1,we:1,you:1,aur:1,ka:1,ki:1,ke:1,ko:1,se:1,me:1,mein:1,ek:1,tha:1,thi:1,the:1,ne:1,par:1,bhi:1,toh:1,jo:1,woh:1,yeh:1,hai:1,hain:1,hun:1,ho:1,raha:1,rahi:1,rahe:1,gaya:1,gayi:1,hua:1,hui:1,kar:1,liye:1,baad:1,phir:1,us:1,is:1,use:1,ise:1,apni:1,apne:1,apna:1,kabhi:1,sirf:1,bhi2:1,'की':1,'का':1,'के':1,'में':1,'और':1,'एक':1,'था':1,'थी':1,'थे':1,'से':1,'को':1,'ने':1,'पर':1,'भी':1,'वह':1,'यह':1,'है':1,'हैं':1,'कि':1,'तो':1,'जब':1,'तब':1,'ही':1,'नहीं':1,'गया':1,'गई':1,'रहा':1,'रही':1,'रहे':1,'हुआ':1,'हुई':1,'कर':1,'लिए':1,'बाद':1,'फिर':1,'अब':1,'उस':1,'इस':1,'उसे':1,'इसे':1,'अपनी':1,'अपने':1,'अपना':1,'अपनी':1,'कभी':1,'सिर्फ़':1,'मगर':1,'लेकिन':1,'हालांकि':1,'तभी':1,'वहाँ':1,'यहाँ':1,'कहाँ':1,'कैसे':1,'क्या':1,'कोई':1,'कुछ':1,'बहुत':1,'लगा':1,'लगी':1,'लगे':1,'दिया':1,'दिए':1,'लिया':1,'गया।':1};
    function stem(w){ if(/^[a-z]+$/.test(w)&&w.length>4){ return w.replace(/(ingly|edly|ing|ed|es|s)$/,''); } return w; }
    function toks(s){ return (s||'').toLowerCase().replace(/[^\u0900-\u097F a-z0-9 ]/g,' ').split(/\s+/).filter(function(w){ return w.length>1&&!STOP[w]; }); }
    function expand(ws){ var out=[]; for(var i=0;i<ws.length;i++){ var w=ws[i]; var e=SYN[w]||DEV[w]; if(e)out.push(stem(e)); out.push(stem(w)); } return out; }
    var pool=[];
    var allSt=(_susp&&_susp.stories)||[];
    var ordered=allSt.slice();
    ordered.sort(function(a,b){ return (b.id===story.id)-(a.id===story.id); });
    for(var si=0;si<ordered.length;si++){ var sb=ordered[si].beats||[];
      for(var bi=0;bi<sb.length;bi++){ pool.push({clip:sb[bi].clip, toks:expand(toks((sb[bi].hi||'')+' '+(sb[bi].en||'')))}); } }
    if(!pool.length){ alert('Scenes ki library load nahi hui - internet on karke app dobara kholo!'); return; }
    var df={};
    for(var di=0;di<pool.length;di++){ var seen={}; for(var dj=0;dj<pool[di].toks.length;dj++){ var t=pool[di].toks[dj]; if(!seen[t]){ seen[t]=1; df[t]=(df[t]||0)+1; } } }
    var DEMOTE={night:1,evening:1,morning:1,old:1,dark:1};
    var used={}, plan=[], zeroMatch=0;
    for(var li=0;li<lines.length;li++){
      var lw=expand(toks(lines[li])); var best=null, bestScore=-1;
      for(var pi=0;pi<pool.length;pi++){
        if(used[pool[pi].clip]) continue;
        var pt=pool[pi].toks, sc=0;
        for(var wi=0;wi<lw.length;wi++){ var tk=lw[wi]; if(pt.indexOf(tk)>=0){ var wgt=1/(df[tk]||1); if(DEMOTE[tk])wgt*=0.3; sc+=wgt; } }
        if(sc>bestScore){ bestScore=sc; best=pool[pi]; }
      }
      if(!best) break;
      used[best.clip]=1;
      if(bestScore<=0) zeroMatch++;
      plan.push({line:lines[li], clip:best.clip});
    }
    if(!plan.length){ alert('Koi scene nahi mila - pehle kahaniyan download hone do!'); return; }
    var clips=plan.map(function(p){ return p.clip; });
    if(!await suspEnsureClips(clips,true)){ alert('Scenes abhi download nahi hue - thora ruk kar dobara dabao!'); return; }
    var bar=document.getElementById('realBar'), prog=document.getElementById('realProg');
    if(prog)prog.style.display='block';
    var segments=[];
    for(var i2=0;i2<plan.length;i2++){
      if(bar)bar.style.width=(5+i2/plan.length*60)+'%';
      suspSetStatus('Awaz '+(i2+1)+'/'+plan.length+': meri kahani');
      var s=await speakSeg(plan[i2].line,suspLang,(story.pitch||1.1),'mysusp',i2);
      if(!s){ alert('Awaz nahi ban saki (line '+(i2+1)+') - dobara try karo!'); return; }
      segments.push({clip:plan[i2].clip,audio:s.audio,duration:s.duration});
    }
    if(bar)bar.style.width='75%';
    suspSetStatus('Meri kahani ki video ban rahi hai...');
    var result=RealClipBridge.composeVideo(JSON.stringify(segments),'MEER_MeriKahani_'+Date.now()+'.mp4');
    if(result&&result.indexOf('ok:')===0){
      suspSetStatus('Meri kahani ki video tayyar!');
      var note='';
      if(plan.length<lines.length) note='Note: library me abhi '+plan.length+' scenes thay, is liye pehli '+plan.length+' lines ki video bani hai. ';
      if(zeroMatch>0) note+=zeroMatch+' lines ke liye library me milta-julta scene nahi tha. ';
      if(note) alert('Video ban gayi! '+note+'Lambi ya bilkul nayi kahani ke liye kahani mujhe (Muse ko chat me) bhej do - main har line ka apna scene bana kar library me daal dunga!');
      showMadeVideo(result,'Tumhari kahani ki video ban gayi! Downloads/MEER me hai');
    }
    else { alert('Video nahi bani: '+result); suspSetStatus('Error: '+result); }
  }catch(e){ alert('Masla: '+e.message); }
}"""

# --- Fix 2: JOURNEY dedupe guard (v4.43 ki apni journeyV3 me izafa) ---
a_decl = "    var segments=[];\n    for(var i2=0;i2<plan.length;i2++){\n      var P=plan[i2];"
if html.count(a_decl) == 1:
    html = html.replace(a_decl, "    var segments=[], usedJ={};\n    for(var i2=0;i2<plan.length;i2++){\n      var P=plan[i2];")
    print('V445 journey usedJ declare: True')
else:
    print('V445 journey usedJ declare: False (count=%d)' % html.count(a_decl))

a_guard = "if(!advOk(clip)){ continue; } /* v4.44: scene na mile to line SKIP - repeat/ghalat scene kabhi nahi */"
if html.count(a_guard) == 1:
    html = html.replace(a_guard, "if(!advOk(clip)||usedJ[clip]){ continue; } /* v4.44/45: scene na mile YA is video me pehle aa chuka ho to line SKIP - scene repeat kabhi nahi */\n      usedJ[clip]=1;")
    print('V445 journey dedupe guard: True')
else:
    print('V445 journey dedupe guard: False (count=%d)' % html.count(a_guard))

# --- Fix 3: REAL VIDEO auto-extend KHATAM (script ki lines dobara bolna band) ---
r_start = html.find('if(estSecV440<targetSecV440){')
r_done = False
if r_start >= 0:
    r_setp = html.find("lines (poore '", r_start)
    if r_setp >= 0:
        r_end = html.find('\n      }', r_setp)
        if r_end >= 0:
            r_end += len('\n      }')
            html = html[:r_start] + "/* v4.45: AUTO-EXTEND KHATAM - script jitni hai video utni hi; koi line dobara NAHI boli jayegi */\n      setP(2,'Script: '+lines.length+' lines - video script ki lambai ki hi banegi');" + html[r_end:]
            r_done = True
print('V445 real auto-extend removed:', r_done)

start_marker = 'async function suspMyMakeVideo(){'
i1 = html.find(start_marker)
if i1 < 0:
    print('V445 myscript replace: False  <-- START MARKER MISSING')
else:
    i2 = html.find('\n}\n', i1)
    if i2 < 0:
        print('V445 myscript replace: False  <-- END MARKER MISSING')
    else:
        html = html[:i1] + NEW_FN + html[i2+2:]
        print('V445 myscript smart matching: True')

open(HP, 'w', encoding='utf-8').write(html)
print('V445 done')
