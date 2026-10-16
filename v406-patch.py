# v4.06: Clip/background download stall fix
# Root cause (verified in code 2026-10-16): "Clips Download Karo" dobara dabane par
# DownloadManager me DUPLICATE entries lag jati hain (clipOk sirf poori file check
# karta hai, chalti hui download ko nahi) — aur fail hui download ki koi khabar
# JS tak aati hi nahi, is liye UI 0/5 par hamesha atka rehta hai.
# Is patch me:
#  1. Har file ki download-ID track hoti hai; chalti/paused/pending download
#     dobara enqueue NAHI hogi.
#  2. getDownloadStatus() — JS ko har file ka live status (running % / failed+reason).
#  3. retryFailed() — fail downloads dobara lagao + "Dobara Try Karo" button.
# Run:  cd ~/workspace/videoapp && python3 ~/workspace/v406-patch.py

import re

def patch_java():
    p = 'android/app/src/main/java/com/hamza/videomaker/MainActivity.java'
    h = open(p, encoding='utf-8').read()
    orig = h

    # 1. Class-level: ID tracking + status helpers (RealClipBridge ke andar)
    anchor = "    class RealClipBridge {\n"
    assert h.count(anchor) == 1, "RealClipBridge anchor not unique!"
    java_helpers = r'''    class RealClipBridge {
        // v4.06: download-ID tracking — dobara dabane par DUPLICATE enqueue nahi hoga,
        // aur har file ka live status (fail reason samet) JS ko milega
        private final java.util.Map<String, Long> dlIds = new java.util.HashMap<>();

        private boolean dlActive(String key, DownloadManager dm) {
            try {
                Long id = dlIds.get(key);
                if (id == null) return false;
                android.database.Cursor c = dm.query(new DownloadManager.Query().setFilterById(id));
                try {
                    if (c != null && c.moveToFirst()) {
                        int st = c.getInt(c.getColumnIndex(DownloadManager.COLUMN_STATUS));
                        if (st == DownloadManager.STATUS_PENDING
                                || st == DownloadManager.STATUS_RUNNING
                                || st == DownloadManager.STATUS_PAUSED) return true;
                    }
                } finally { if (c != null) c.close(); }
                dlIds.remove(key);
                return false;
            } catch (Exception e) { return false; }
        }

        private void dlRemember(String key, long id) { dlIds.put(key, id); }

        @JavascriptInterface
        public String getDownloadStatus() {
            try {
                DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                StringBuilder sb = new StringBuilder("[");
                boolean first = true;
                first = appendDlStatus(sb, first, dm, "c:", CLIPS, clipDir());
                first = appendDlStatus(sb, first, dm, "b:", BACKGROUNDS, bgDir());
                sb.append("]");
                return sb.toString();
            } catch (Exception e) { return "[]"; }
        }

        private boolean appendDlStatus(StringBuilder sb, boolean first, DownloadManager dm,
                                       String prefix, String[] names, File dir) {
            for (String name : names) {
                File f = new File(dir, name);
                String state; int pct = -1; String reason = "";
                if (clipOk(f)) { state = "ok"; }
                else {
                    Long id = dlIds.get(prefix + name);
                    if (id == null) { state = "idle"; }
                    else {
                        android.database.Cursor c = null;
                        try {
                            c = dm.query(new DownloadManager.Query().setFilterById(id));
                            if (c != null && c.moveToFirst()) {
                                int st = c.getInt(c.getColumnIndex(DownloadManager.COLUMN_STATUS));
                                long done = c.getLong(c.getColumnIndex(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR));
                                long total = c.getLong(c.getColumnIndex(DownloadManager.COLUMN_TOTAL_SIZE_BYTES));
                                if (total > 0) pct = (int) (done * 100 / total);
                                if (st == DownloadManager.STATUS_SUCCESSFUL) state = "ok";
                                else if (st == DownloadManager.STATUS_FAILED) {
                                    state = "failed";
                                    reason = String.valueOf(c.getInt(c.getColumnIndex(DownloadManager.COLUMN_REASON)));
                                }
                                else if (st == DownloadManager.STATUS_PAUSED) state = "paused";
                                else if (st == DownloadManager.STATUS_RUNNING) state = "running";
                                else state = "pending";
                            } else { state = "idle"; }
                        } catch (Exception e) { state = "idle"; }
                        finally { if (c != null) c.close(); }
                    }
                }
                if (!first) sb.append(",");
                first = false;
                sb.append("{\"f\":\"").append(name).append("\",\"s\":\"").append(state)
                  .append("\",\"p\":").append(pct).append(",\"r\":\"").append(reason).append("\"}");
            }
            return first;
        }

        @JavascriptInterface
        public void retryFailed() {
            runOnUiThread(() -> {
                try {
                    DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                    java.util.List<String> keys = new java.util.ArrayList<>(dlIds.keySet());
                    for (String key : keys) {
                        Long id = dlIds.get(key);
                        if (id == null) continue;
                        android.database.Cursor c = null;
                        boolean failed = false;
                        try {
                            c = dm.query(new DownloadManager.Query().setFilterById(id));
                            if (c != null && c.moveToFirst()) {
                                failed = c.getInt(c.getColumnIndex(DownloadManager.COLUMN_STATUS))
                                        == DownloadManager.STATUS_FAILED;
                            } else failed = true;
                        } catch (Exception e) { failed = true; }
                        finally { if (c != null) c.close(); }
                        if (failed) {
                            try { dm.remove(id); } catch (Exception ignored) {}
                            dlIds.remove(key);
                            boolean isBg = key.startsWith("b:");
                            String name = key.substring(2);
                            File f = new File(isBg ? bgDir() : clipDir(), name);
                            if (f.exists()) f.delete();
                            DownloadManager.Request req = new DownloadManager.Request(
                                    Uri.parse((isBg ? BG_BASE : CLIP_BASE) + name));
                            req.setTitle("MEER " + (isBg ? "background" : "clip") + ": " + name);
                            req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE);
                            req.setDestinationUri(Uri.fromFile(f));
                            dlRemember(key, dm.enqueue(req));
                        }
                    }
                    js("onClipMsg('retry',0)");
                } catch (Exception e) { js("onClipMsg('error',0)"); }
            });
        }
'''
    h = h.replace(anchor, java_helpers, 1)
    print('JAVA helpers OK')

    # 2. downloadClips(): duplicate guard
    old_clips = """                    for (String name : CLIPS) {
                        File f = new File(dir, name);
                        if (clipOk(f)) continue; // already downloaded
                        DownloadManager.Request req =
                                new DownloadManager.Request(Uri.parse(CLIP_BASE + name));
                        req.setTitle("MEER clip: " + name);
                        req.setNotificationVisibility(
                                DownloadManager.Request.VISIBILITY_VISIBLE);
                        req.setDestinationUri(Uri.fromFile(f));
                        dm.enqueue(req);
                        started++;
                    }"""
    new_clips = """                    for (String name : CLIPS) {
                        File f = new File(dir, name);
                        if (clipOk(f)) continue; // already downloaded
                        if (dlActive("c:" + name, dm)) continue; // v4.06: pehle se download ho rahi hai
                        DownloadManager.Request req =
                                new DownloadManager.Request(Uri.parse(CLIP_BASE + name));
                        req.setTitle("MEER clip: " + name);
                        req.setNotificationVisibility(
                                DownloadManager.Request.VISIBILITY_VISIBLE);
                        req.setDestinationUri(Uri.fromFile(f));
                        dlRemember("c:" + name, dm.enqueue(req));
                        started++;
                    }"""
    assert old_clips in h, "downloadClips loop anchor missing!"
    h = h.replace(old_clips, new_clips, 1)
    print('JAVA downloadClips guard OK')

    # 3. downloadBackgrounds(): duplicate guard
    old_bg = """                    for (String name : BACKGROUNDS) {
                        File f = new File(dir, name);
                        if (clipOk(f)) continue;
                        DownloadManager.Request req =
                                new DownloadManager.Request(Uri.parse(BG_BASE + name));
                        req.setTitle("MEER background: " + name);
                        req.setNotificationVisibility(
                                DownloadManager.Request.VISIBILITY_VISIBLE);
                        req.setDestinationUri(Uri.fromFile(f));
                        dm.enqueue(req);
                        started++;
                    }"""
    new_bg = """                    for (String name : BACKGROUNDS) {
                        File f = new File(dir, name);
                        if (clipOk(f)) continue;
                        if (dlActive("b:" + name, dm)) continue; // v4.06: pehle se download ho rahi hai
                        DownloadManager.Request req =
                                new DownloadManager.Request(Uri.parse(BG_BASE + name));
                        req.setTitle("MEER background: " + name);
                        req.setNotificationVisibility(
                                DownloadManager.Request.VISIBILITY_VISIBLE);
                        req.setDestinationUri(Uri.fromFile(f));
                        dlRemember("b:" + name, dm.enqueue(req));
                        started++;
                    }"""
    assert old_bg in h, "downloadBackgrounds loop anchor missing!"
    h = h.replace(old_bg, new_bg, 1)
    print('JAVA downloadBackgrounds guard OK')

    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('JAVA V4.06 DONE')


def patch_html():
    p = 'android/app/src/main/assets/www/index.html'
    h = open(p, encoding='utf-8').read()
    orig = h

    # 1. Retry button (Clips Download Karo ke neeche)
    old_btn = '<button class="btn btn2" onclick="realDownloadClips()">⬇️ Clips Download Karo</button>'
    new_btn = ('<button class="btn btn2" onclick="realDownloadClips()">⬇️ Clips Download Karo</button>\n'
               '    <button class="btn" onclick="try{RealClipBridge.retryFailed();}catch(e){}" '
               'style="margin-top:6px">🔁 Dobara Try Karo</button>')
    assert old_btn in h, "button anchor missing!"
    h = h.replace(old_btn, new_btn, 1)
    print('HTML retry button OK')

    # 2. onClipMsg: 'retry' + started==0 par ghalat "tayyar" message ka fix
    old_cb = """function onClipMsg(st,n){ /* native downloadClips() callback */
  const s=$('realClipStat');
  if(!s)return;
  if(st==='started')s.textContent=n>0?('⬇️ '+n+' clips download ho rahi hain...'):'✅ Clips tayyar hain!';
  else if(st==='ready')s.textContent='✅ Clips tayyar hain!';
  else if(st==='error')s.textContent='❌ Download me masla — dobara try karo';
  realClipCheck();
}"""
    new_cb = """function onClipMsg(st,n){ /* native downloadClips() callback */
  const s=$('realClipStat');
  if(!s)return;
  if(st==='started'){
    let c=0;try{c=RealClipBridge.getDownloadedCount();}catch(e){}
    s.textContent=(n>0||c<5)?('⬇️ '+c+'/5 clips download ho rahi hain...'):'✅ Clips tayyar hain!';
  }
  else if(st==='retry')s.textContent='🔁 Fail downloads dobara lag rahe...';
  else if(st==='ready')s.textContent='✅ Clips tayyar hain!';
  else if(st==='error')s.textContent='❌ Download me masla — dobara try karo';
  realClipCheck();
}"""
    assert old_cb in h, "onClipMsg anchor missing!"
    h = h.replace(old_cb, new_cb, 1)
    print('HTML onClipMsg OK')

    # 3. Polling interval: fail/progress nazar aaye
    old_poll = "      $('realClipStat').textContent=n>=5?'✅ 5/5 clips tayyar!':'⬇️ '+n+'/5 clips download ho rahe...';"
    new_poll = """      var extra='';
      try{
        if(typeof RealClipBridge.getDownloadStatus==='function'){
          var st=JSON.parse(RealClipBridge.getDownloadStatus()||'[]');
          var failed=st.filter(function(x){return x.s==='failed';});
          var active=st.filter(function(x){return x.s==='running'||x.s==='pending'||x.s==='paused';});
          if(failed.length>0)extra=' ❌ '+failed.length+' fail — "🔁 Dobara Try Karo" dabao';
          else if(n<5&&active.length>0){
            var pc=active.map(function(x){return x.p;}).filter(function(p){return p>=0;});
            if(pc.length>0)extra=' ('+Math.max.apply(null,pc)+'% ho raha...)';
          }
        }
      }catch(e){}
      $('realClipStat').textContent=n>=5?'✅ 5/5 clips tayyar!':('⬇️ '+n+'/5 clips download ho rahe...'+extra);"""
    assert old_poll in h, "poll anchor missing!"
    h = h.replace(old_poll, new_poll, 1)
    print('HTML poll status OK')

    # 4. Version 4.06
    h = re.sub(r"const APP_VER='4\.05'", "const APP_VER='4.06'", h)
    h = h.replace("v4.05", "v4.06")
    print('HTML version OK')

    if h != orig:
        open(p, 'w', encoding='utf-8').write(h)
    print('HTML V4.06 DONE')


patch_java()
patch_html()
print('V4.06 ALL DONE')
