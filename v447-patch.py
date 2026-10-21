#!/usr/bin/env python3
# MEER v4.47 - EK CLICK KAHANI ENGINE (har click = nayi kahani)
# Saboot (Hamza ka screenshot + report, 2026-10-21): "EK CLICK ME KAHANI BANAO"
# dabane par sirf 2 kahaniyan baar baar ati hain - ek Twinkle wali, ek doosri.
# Wajah code me dekhi: CAR_STORIES_EN me sirf 8 chhote tukre (3 to poem hain),
# CAR_STORIES_HI me sirf 3, aur Urdu select karne par galti se FAM_STORIES
# (family wali) uth jati thi. 1 minute ke liye ~20 lines chahiye hoti hain,
# is liye wohi 8 tukre jor-jor kar ghumte rehte thay.
# Fix: carAutoStory ki nayi tareef (chunk ke aakhir me override) - ek kahani
# engine jo har click par khulne/middle/khatam ke naye hisse nayi tartib me
# jorta hai. Har zuban (EN/HI/UR) ka apna bank; UR ke liye car wali alag
# kahaniyan (family reuse wala bug bhi khatam). Ek kahani ke andar koi line
# dobara nahi (used-set guard). Baqi app ko haath nahi lagaya.
import re

HP = 'android/app/src/main/assets/www/index.html'
html = open(HP, encoding='utf-8').read()

html, n1 = re.subn(r"APP_VER\s*=\s*[\"'][\d.]+[\"']", 'APP_VER="4.47"', html)
html, n2 = re.subn(r"v4\.\d+ MEER", "v4.47 MEER", html)
print('V447 APP_VER bump:', n1, n2)

NEW_BLOCK = r"""
/* ===== MEER v4.47: EK CLICK KAHANI ENGINE =====
   Purana bank (EN 8 / HI 3 tukre) khatam - ab har click par engine nayi
   kahani bunta hai: opening + kai adventure hisse + ikhtitam, har hisse
   nayi tartib me, jagah/cheez ke slots har dafa naye. Ek kahani ke andar
   koi line dobara nahi ati. {P}=jagah, {I}=cheez (arc ke andar ek hi rehte
   hain), {n1}{n2}{n3}=kirdaar (aakhir me naam bhar jate hain). */
var CG47={
en:{place:["Sunny Town","Rainbow Valley","Pine Hill","Lake City","Green Meadows","Star Village","River Bend","Cloud Top Town","Maple Street","Blue Bay"],
item:["shiny red kite","little lost teddy","golden key","magic map","singing bell","blue balloon","wooden flute","sparkling stone","tiny lantern","paper boat"],
open:[
["{n1}: Good morning, friends! What a bright day!","{n2}: Good morning, {n1}! I slept so well!","{n3}: My engine is warm and ready!","{n1}: Today something exciting will happen, I can feel it!"],
["{n1}: Wake up, wake up! The sun is shining!","{n2}: Five more minutes, please!","{n3}: Ha ha! {n2} is still sleepy!","{n1}: Come on! Adventure does not wait!"],
["{n1}: Friends, I have a surprise plan for today!","{n2}: A surprise? Tell us, tell us!","{n3}: My wheels are already dancing!","{n1}: Then follow me, everyone!"],
["{n1}: What a lovely morning in {P}!","{n2}: The birds are singing with my horn!","{n3}: Beep beep! Good morning, world!","{n1}: Let us see what today brings!"],
["{n1}: I polished my bonnet today!","{n2}: You shine like a mirror, {n1}!","{n3}: And I filled my tank to the top!","{n1}: Perfect! We are ready for anything!"],
["{n1}: Did you hear? Something fun is happening in {P}!","{n2}: Really? What is it?","{n3}: Do not keep us waiting!","{n1}: We will find out together!"]],
adv:[
["{n1}: Friends, shall we have a friendly race?","{n2}: Yes! To the big tree and back!","{n3}: I will count! Three, two, one, go!","{n1}: Vroom! I am flying!","{n2}: Wait for me! My wheels are spinning!","{n3}: What a race! Everyone is a winner today!"],
["{n2}: Oh no! I lost my {I}!","{n1}: Do not worry, we will find it together!","{n3}: I saw something shining near {P}!","{n2}: Let us look carefully!","{n1}: There it is! Under the leaf!","{n2}: Hurray! Thank you, my friends!"],
["{n3}: My engine is tired, I cannot climb this hill.","{n1}: Lean on me, I will pull you!","{n2}: And I will push from behind!","{n3}: You are true friends!","{n1}: Slowly, slowly, almost there!","{n2}: We did it! Teamwork wins!"],
["{n1}: Look at those dark clouds!","{n2}: Rain is coming! Wipers ready!","{n3}: Splish splash! Puddles everywhere!","{n1}: Drive slow and safe, everyone!","{n2}: Look, the rain is stopping!","{n3}: A rainbow! The sky is smiling!"],
["{n1}: Let us have a picnic at {P}!","{n2}: I packed sandwiches and juice!","{n3}: And I brought a big blanket!","{n1}: This grass is so soft!","{n2}: Yummy! Best picnic ever!","{n3}: Let us play hide and seek after eating!"],
["{n1}: That little car is crying. Let us help!","{n2}: What happened, little friend?","{n3}: He lost his way home!","{n1}: Follow us, we know the road!","{n2}: Slowly now, stay close!","{n3}: Home at last! His family is so happy!"],
["{n1}: It is getting dark, headlights on!","{n2}: Wow, so many stars tonight!","{n3}: That one is twinkling at me!","{n1}: Let us count the stars together!","{n2}: One, two, three, four...","{n3}: I lost count! The sky is full of diamonds!"],
["{n1}: Today is the kite festival in {P}!","{n2}: So many colours in the sky!","{n3}: A kite is stuck in that tree!","{n1}: I will stretch and free it!","{n2}: Careful, {n1}! Almost there!","{n3}: It flies again! Everyone is cheering!"],
["{n1}: I am so muddy today!","{n2}: Then it is car-wash day!","{n3}: Bubbles! So many bubbles!","{n1}: The brushes tickle me! Ha ha!","{n2}: Now you shine like new!","{n3}: Let us stay clean... oh, a puddle!"],
["{n1}: Shh! Today is the birthday of {n2}!","{n3}: I decorated the garage with balloons!","{n2}: Why is everyone so quiet today?","{n1}: Surprise! Happy birthday, {n2}!","{n3}: We baked a cake shaped like a tyre!","{n2}: This is the best day of my life!"],
["{n1}: Oh, the little bridge is broken!","{n2}: How will we cross the river?","{n3}: I see flat stones over there!","{n1}: One by one, very slowly!","{n2}: I am scared... but I can do it!","{n3}: We crossed! Brave cars never give up!"],
["{n1}: Let us visit the market in {P}!","{n2}: I want shiny new hubcaps!","{n3}: And I want sweet mangoes!","{n1}: Look, fresh flowers for everyone!","{n2}: The market is so colourful!","{n3}: Time to go home before dark!"]],
close:[
["{n1}: What a wonderful day it was!","{n2}: I will never forget it!","{n3}: Tomorrow, a new adventure! Good night, friends!"],
["{n1}: Home sweet home!","{n2}: My wheels are tired but my heart is happy!","{n3}: Sleep tight, everyone! See you at sunrise!"],
["{n1}: Friends make every road beautiful!","{n2}: True! Together we can do anything!","{n3}: The end! But our story goes on!"],
["{n1}: The stars are out, time to rest!","{n2}: Good night, {n1}! Good night, {n3}!","{n3}: Sweet dreams, my dear friends!"],
["{n1}: Let us park under the moonlight!","{n2}: Today my smile is bigger than my headlights!","{n3}: Good night! Tomorrow we ride again!"],
["{n1}: And so, three friends returned home happily!","{n2}: With full tanks and happy hearts!","{n3}: Bye bye, everyone! Until the next story!"]]},
hi:{place:["सूरज नगर","इंद्रधनुष घाटी","चीड़ पहाड़ी","झील शहर","हरी वादी","तारा गाँव","नदी मोड़","बादल नगर","आम गली","नीली खाड़ी"],
item:["चमकदार लाल पतंग","छोटा खोया टेडी","सुनहरी चाबी","जादुई नक्शा","गाती घंटी","नीला गुब्बारा","लकड़ी की बाँसुरी","चमकता पत्थर","छोटी लालटेन","कागज़ की नाव"],
open:[
["{n1}: सुप्रभात दोस्तों! कितना सुहाना दिन है!","{n2}: सुप्रभात {n1}! मेरी नींद बहुत अच्छी हुई!","{n3}: मेरा इंजन गरम और तैयार है!","{n1}: आज कुछ मज़ेदार होगा, मुझे लग रहा है!"],
["{n1}: उठो उठो! सूरज निकल आया है!","{n2}: बस पाँच मिनट और सोने दो!","{n3}: हा हा! {n2} अभी भी नींद में है!","{n1}: चलो! मज़ा इंतज़ार नहीं करता!"],
["{n1}: दोस्तों, आज के लिए मेरा एक सरप्राइज़ प्लान है!","{n2}: सरप्राइज़? बताओ बताओ!","{n3}: मेरे पहिए तो अभी से नाच रहे हैं!","{n1}: तो सब मेरे पीछे आओ!"],
["{n1}: {P} में कितनी प्यारी सुबह है!","{n2}: चिड़ियाँ मेरे हॉर्न के साथ गा रही हैं!","{n3}: बीप बीप! सुप्रभात दुनिया!","{n1}: देखते हैं आज क्या होता है!"]],
adv:[
["{n1}: दोस्तों, दोस्ताना रेस करें?","{n2}: हाँ! बड़े पेड़ तक और वापस!","{n3}: मैं गिनती करता हूँ! तीन, दो, एक, गो!","{n1}: वरूम! मैं तो उड़ रहा हूँ!","{n2}: मेरे लिए रुको! पहिए घूम रहे हैं!","{n3}: क्या रेस थी! आज सब विजेता हैं!"],
["{n2}: अरे नहीं! मेरा {I} खो गया!","{n1}: चिंता मत करो, साथ मिलकर ढूँढेंगे!","{n3}: मैंने {P} के पास कुछ चमकता देखा था!","{n2}: ध्यान से देखते हैं!","{n1}: वो रहा! पत्ते के नीचे!","{n2}: वाह! शुक्रिया मेरे दोस्तों!"],
["{n3}: मेरा इंजन थक गया है, मैं यह पहाड़ी नहीं चढ़ सकता।","{n1}: मेरा सहारा लो, मैं खींचूँगा!","{n2}: और मैं पीछे से धक्का दूँगा!","{n3}: तुम सच्चे दोस्त हो!","{n1}: धीरे धीरे, बस पहुँच गए!","{n2}: हम कर गए! मिलकर काम हमेशा जीतता है!"],
["{n1}: वो काले बादल देखो!","{n2}: बारिश आने वाली है! वाइपर तैयार!","{n3}: छप छप! हर तरफ़ पानी!","{n1}: सब धीरे और संभल कर चलो!","{n2}: देखो, बारिश रुक रही है!","{n3}: इंद्रधनुष! आसमान मुस्कुरा रहा है!"],
["{n1}: चलो {P} में पिकनिक करते हैं!","{n2}: मैंने सैंडविच और जूस रखा है!","{n3}: और मैं बड़ी चादर लाया हूँ!","{n1}: यह घास कितनी नरम है!","{n2}: यम्मी! सबसे अच्छी पिकनिक!","{n3}: खाने के बाद छुपन-छुपाई खेलेंगे!"],
["{n1}: अंधेरा हो रहा है, हेडलाइट जलाओ!","{n2}: वाह, आज कितने तारे हैं!","{n3}: वो वाला मुझे देखकर टिमटिमा रहा है!","{n1}: चलो साथ तारे गिनते हैं!","{n2}: एक, दो, तीन, चार...","{n3}: मैं गिनती भूल गया! आसमान हीरों से भरा है!"],
["{n1}: आज {P} में पतंग महोत्सव है!","{n2}: आसमान में कितने रंग हैं!","{n3}: एक पतंग उस पेड़ में फँस गई!","{n1}: मैं खिंचकर उसे छुड़ाऊँगा!","{n2}: संभल कर {n1}! बस हो गया!","{n3}: वो फिर उड़ गई! सब तालियाँ बजा रहे हैं!"],
["{n1}: अरे, छोटा पुल टूटा हुआ है!","{n2}: हम नदी कैसे पार करेंगे?","{n3}: उधर चपटे पत्थर दिख रहे हैं!","{n1}: एक-एक करके, बहुत धीरे!","{n2}: मुझे डर लग रहा है... पर मैं कर सकता हूँ!","{n3}: हम पार हो गए! बहादुर कभी हार नहीं मानते!"]],
close:[
["{n1}: कितना शानदार दिन था!","{n2}: मैं इसे कभी नहीं भूलूँगा!","{n3}: कल एक नया किस्सा! शुभ रात्रि दोस्तों!"],
["{n1}: घर प्यारा घर!","{n2}: पहिए थके हैं पर दिल खुश है!","{n3}: सब सो जाओ! सुबह मिलते हैं!"],
["{n1}: दोस्त हर रास्ता सुंदर बना देते हैं!","{n2}: सच! साथ मिलकर हम कुछ भी कर सकते हैं!","{n3}: समाप्त! पर हमारी कहानी चलती रहेगी!"],
["{n1}: चलो चाँदनी में पार्क करते हैं!","{n2}: आज मेरी मुस्कान हेडलाइट से बड़ी है!","{n3}: शुभ रात्रि! कल फिर चलेंगे!"]]},
ur:{place:["Suraj Nagar","Rainbow Ghaati","Pahaari Town","Jheel City","Sabz Waadi","Taara Gaon","Darya Morr","Baadal Nagar","Aam Gali","Neeli Khaari"],
item:["chamkadar lal patang","chhota khoya teddy","sunehri chaabi","jadui naqsha","gaati ghanti","neela gubbara","lakri ki bansuri","chamakta pathar","chhoti laltain","kaghaz ki naav"],
open:[
["{n1}: Suprabhat doston! Kitna pyara din hai!","{n2}: Suprabhat {n1}! Meri neend bohat achi hui!","{n3}: Mera engine garam aur tayyar hai!","{n1}: Aaj kuch mazay ka hoga, mujhe lag raha hai!"],
["{n1}: Utho utho! Sooraj nikal aya hai!","{n2}: Bas paanch minute aur sonay do!","{n3}: Ha ha! {n2} abhi bhi neend me hai!","{n1}: Chalo! Maza intezar nahi karta!"],
["{n1}: Doston, aaj ke liye mera surprise plan hai!","{n2}: Surprise? Batao batao!","{n3}: Mere pahiye to abhi se naach rahe hain!","{n1}: To sab mere peeche ao!"],
["{n1}: {P} me kitni pyari subah hai!","{n2}: Chirya mere horn ke saath ga rahi hain!","{n3}: Beep beep! Suprabhat duniya!","{n1}: Dekhte hain aaj kya hota hai!"]],
adv:[
["{n1}: Doston, dostana race karen?","{n2}: Haan! Bare darakht tak aur wapas!","{n3}: Main ginti karta hoon! Teen, do, ek, go!","{n1}: Vroom! Main to urr raha hoon!","{n2}: Mere liye ruko! Pahiye ghoom rahe hain!","{n3}: Kya race thi! Aaj sab winner hain!"],
["{n2}: Arey nahi! Mera {I} kho gaya!","{n1}: Fikar mat karo, mil kar dhundenge!","{n3}: Maine {P} ke paas kuch chamakta dekha tha!","{n2}: Dhyaan se dekhte hain!","{n1}: Wo raha! Patte ke neeche!","{n2}: Wah! Shukriya mere doston!"],
["{n3}: Mera engine thak gaya hai, main ye pahaari nahi charh sakta.","{n1}: Mera sahara lo, main kheenchunga!","{n2}: Aur main peeche se dhakka dunga!","{n3}: Tum sachay dost ho!","{n1}: Aahista aahista, bas pohanch gaye!","{n2}: Hum kar gaye! Mil kar kaam hamesha jeetta hai!"],
["{n1}: Wo kaale baadal dekho!","{n2}: Baarish ane wali hai! Wiper tayyar!","{n3}: Chhap chhap! Her taraf paani!","{n1}: Sab aahista aur sambhal kar chalo!","{n2}: Dekho, baarish ruk rahi hai!","{n3}: Rainbow! Aasmaan muskura raha hai!"],
["{n1}: Chalo {P} me picnic karte hain!","{n2}: Maine sandwich aur juice rakha hai!","{n3}: Aur main bari chaadar laya hoon!","{n1}: Ye ghaas kitni naram hai!","{n2}: Yummy! Sab se achi picnic!","{n3}: Khane ke baad chhupan chhupai khelenge!"],
["{n1}: Andhera ho raha hai, headlight jalao!","{n2}: Wah, aaj kitne taare hain!","{n3}: Wo wala mujhe dekh kar timtima raha hai!","{n1}: Chalo saath taare ginte hain!","{n2}: Ek, do, teen, chaar...","{n3}: Main ginti bhool gaya! Aasmaan heeron se bhara hai!"],
["{n1}: Aaj {P} me patang mela hai!","{n2}: Aasmaan me kitne rang hain!","{n3}: Ek patang us darakht me phans gayi!","{n1}: Main kheench kar use chhuraunga!","{n2}: Sambhal kar {n1}! Bas ho gaya!","{n3}: Wo phir urr gayi! Sab taaliyan baja rahe hain!"],
["{n1}: Arey, chhota pul toota hua hai!","{n2}: Hum nadi kaise paar karenge?","{n3}: Udhar chaptay pathar dikh rahe hain!","{n1}: Ek ek karke, bohat aahista!","{n2}: Mujhe darr lag raha hai... par main kar sakta hoon!","{n3}: Hum paar ho gaye! Bahaadur kabhi haar nahi maante!"]],
close:[
["{n1}: Kitna shaandar din tha!","{n2}: Main ise kabhi nahi bhoolunga!","{n3}: Kal ek naya qissa! Shab bakhair doston!"],
["{n1}: Ghar pyara ghar!","{n2}: Pahiye thake hain par dil khush hai!","{n3}: Sab so jao! Subah milte hain!"],
["{n1}: Dost har rasta khoobsurat bana dete hain!","{n2}: Sach! Saath mil kar hum kuch bhi kar sakte hain!","{n3}: Khatam! Par hamari kahani chalti rahegi!"],
["{n1}: Chalo chaandni me park karte hain!","{n2}: Aaj meri muskurahat headlight se bari hai!","{n3}: Shab bakhair! Kal phir chalenge!"]]}
};
carAutoStory=function(){
  var n1=($('realName1')?.value||'Rayo').trim()||'Rayo';
  var n2=($('realName2')?.value||'Bella').trim()||'Bella';
  var n3=($('realName3')?.value||'Rusty').trim()||'Rusty';
  var durMin=1; try{durMin=parseInt($('realDur').value)||1;}catch(e){}
  var carLang='en'; try{carLang=$('realLang').value||'en';}catch(e){}
  var B=CG47[carLang]||CG47.en;
  var need=Math.max(10,Math.round(durMin*60/3));
  function rnd(a){ return a[Math.floor(Math.random()*a.length)]; }
  function shuffled(n){ var x=[]; for(var i=0;i<n;i++)x.push(i); for(var j=x.length-1;j>0;j--){ var k=Math.floor(Math.random()*(j+1)); var t=x[j]; x[j]=x[k]; x[k]=t; } return x; }
  var used={}, out=[];
  function pushArc(arc,cap){
    var P=rnd(B.place), I=rnd(B.item);
    for(var i=0;i<arc.length;i++){
      if(cap && out.length>=need) return;
      var L=arc[i].split('{P}').join(P).split('{I}').join(I);
      if(used[L]) continue;
      used[L]=1; out.push(L);
    }
  }
  pushArc(rnd(B.open),true);
  var order=shuffled(B.adv.length), pass=0;
  while(out.length<need && pass<3){
    for(var k=0;k<order.length && out.length<need;k++) pushArc(B.adv[order[k]],true);
    pass++;
  }
  pushArc(rnd(B.close),false);
  var script=out.join('\n').split('{n1}').join(n1).split('{n2}').join(n2).split('{n3}').join(n3);
  $('realScript').value=script;
  try{realUpdateEst();}catch(e){}
  var n=out.length;
  var secs=Math.round(n*3), mins=Math.floor(secs/60), rem=secs%60;
  var dur=mins>0?mins+' min '+rem+' sec':secs+' sec';
  alert('Nayi kahani ready! '+n+' dialogues | ~'+dur+'\nHar click par engine nayi kahani bunta hai!\nAb "REAL VIDEO BANAO" dabao!');
};
"""

anchor = "\n(function(){\n  function rebind()"
if anchor in html:
    html = html.replace(anchor, NEW_BLOCK + anchor, 1)
    print('V447 kahani engine override: True')
else:
    print('V447 kahani engine override: False  <-- ANCHOR MISSING')

open(HP, 'w', encoding='utf-8').write(html)
print('V447 done')
