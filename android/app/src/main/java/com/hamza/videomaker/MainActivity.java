package com.hamza.videomaker;

import android.app.Activity;
import android.app.DownloadManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.speech.tts.Voice;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import androidx.core.content.FileProvider;
import java.io.File;
import java.io.FileInputStream;
import java.util.Locale;
import java.util.Set;

/**
 * Hamza AI Studio v3.6 — WebView wrapper with NATIVE Android TTS.
 * window.HamzaTTS exposes on-device text-to-speech to JavaScript,
 * so voice works 100% offline with no network blocking.
 *
 * v3.6 improvements:
 *  - Urdu text normalization (Arabic kaf/yeh -> Urdu forms) for clear pronunciation
 *  - checkVoice(lang) reports whether a proper voice is installed
 *  - Better locale resolution (ur-PK first, then ur)
 */
public class MainActivity extends Activity {
    private WebView web;
    private TextToSpeech tts;
    private volatile boolean ttsReady = false;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(true);
        s.setAllowFileAccessFromFileURLs(true); // v3.21: local clip files for <video>
        s.setAllowUniversalAccessFromFileURLs(true); // v3.21: local clip files
        web.setWebViewClient(new WebViewClient(){
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, android.webkit.WebResourceRequest request){
                return handleUrl(request.getUrl().toString());
            }
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url){
                return handleUrl(url);
            }
            private boolean handleUrl(String url){
                // let WebView handle web + local files
                if(url.startsWith("http://")||url.startsWith("https://")||url.startsWith("file://"))return false;
                // whatsapp://, tel:, mailto: etc -> open in external app
                try{
                    Intent i=new Intent(Intent.ACTION_VIEW,Uri.parse(url));
                    i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(i);
                }catch(Exception ignored){
                    Toast.makeText(MainActivity.this,"App nahi khul saki",Toast.LENGTH_SHORT).show();
                }
                return true;
            }
        });
        web.setWebChromeClient(new WebChromeClient());
        // v3.61: DownloadListener - blob URL downloads ko natively handle karo! (or treeqa!)
        web.setDownloadListener(new android.webkit.DownloadListener(){
            @Override
            public void onDownloadStart(String url, String userAgent, String contentDisposition, String mimetype, long contentLength){
                if(url.startsWith("blob:")){
                    // v3.62 FIX: Promise ka wait nahi hota! Callback method use karo.
                    // JS blob ko base64 me convert karke onBlobData() call karega
                    final String safeUrl = url.replace("'", "\\'");
                    final String safeMime = mimetype != null ? mimetype : "video/webm";
                    web.evaluateJavascript(
                        "(function(){" +
                        "var x=new XMLHttpRequest();" +
                        "x.open('GET','" + safeUrl + "',true);" +
                        "x.responseType='blob';" +
                        "x.onload=function(){" +
                        "  var r=new FileReader();" +
                        "  r.onload=function(){try{MeerDlBridge.onBlobData(r.result,'" + safeMime + "');}catch(e){}};" +
                        "  r.onerror=function(){try{MeerDlBridge.onBlobData('', '" + safeMime + "');}catch(e){}};" +
                        "  r.readAsDataURL(x.response);" +
                        "};" +
                        "x.onerror=function(){try{MeerDlBridge.onBlobData('', '" + safeMime + "');}catch(e){}};" +
                        "x.send();" +
                        "})();",
                        null);
                    Toast.makeText(MainActivity.this,
                        "⬇️ Download ho rahi hai...", Toast.LENGTH_SHORT).show();
                }else{
                    // Normal URL: DownloadManager
                    try{
                        android.app.DownloadManager.Request req=new android.app.DownloadManager.Request(android.net.Uri.parse(url));
                        req.setMimeType(mimetype);
                        req.setTitle("MEER Video");
                        req.setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS,"MEER/MEER-"+System.currentTimeMillis()+".webm");
                        req.setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                        ((android.app.DownloadManager)getSystemService(DOWNLOAD_SERVICE)).enqueue(req);
                        android.widget.Toast.makeText(MainActivity.this,"⬇️ Download shuru!",android.widget.Toast.LENGTH_SHORT).show();
                    }catch(Exception e){
                        android.widget.Toast.makeText(MainActivity.this,"Download fail",android.widget.Toast.LENGTH_SHORT).show();
                    }
                }
            }
        });
        web.addJavascriptInterface(new TTSBridge(), "HamzaTTS");
        web.addJavascriptInterface(new UpdateBridge(), "HamzaUpdate");
        web.addJavascriptInterface(new RealClipBridge(), "RealClipBridge"); // v3.21: real cartoon clips
        web.addJavascriptInterface(new DownloadBridge(), "MeerDlBridge"); // v3.62: blob download callback

        tts = new TextToSpeech(this, status -> {
            if (status == TextToSpeech.SUCCESS) {
                ttsReady = true;
                tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
                    @Override public void onStart(String id) {}
                    @Override public void onError(String id) {
                        js("onTTSFailed('" + id + "','synthesis error')");
                    }
                    @Override public void onDone(String id) {
                        deliverFile(id);
                    }
                    @Override public void onError(String id, int code) {
                        js("onTTSFailed('" + id + "','error " + code + "')");
                    }
                });
                js("onTTSReady()");
            }
        });

        web.loadUrl("file:///android_asset/www/index.html");
        setContentView(web);
    }

    private void js(final String code) {
        runOnUiThread(() -> {
            if (web != null) web.evaluateJavascript(code, null);
        });
    }

    private void deliverFile(String utteranceId) {
        try {
            File f = new File(getCacheDir(), "tts_" + utteranceId + ".wav");
            if (!f.exists()) { js("onTTSFailed('" + utteranceId + "','no file')"); return; }
            FileInputStream in = new FileInputStream(f);
            byte[] data = new byte[(int) f.length()];
            int read = 0;
            while (read < data.length) {
                int r = in.read(data, read, data.length - read);
                if (r < 0) break;
                read += r;
            }
            in.close();
            f.delete();
            String b64 = Base64.encodeToString(data, Base64.NO_WRAP);
            js("onTTSDone('" + utteranceId + "','data:audio/wav;base64," + b64 + "')");
        } catch (Exception e) {
            js("onTTSFailed('" + utteranceId + "','read error')");
        }
    }

    /** Normalize Urdu/Arabic script so the TTS engine pronounces words correctly. */
    static String normalizeUrdu(String text) {
        if (text == null) return "";
        StringBuilder sb = new StringBuilder(text.length());
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            switch (c) {
                case 'ك': c = 'ک'; break; // Arabic kaf -> Urdu kaf
                case 'ي': c = 'ی'; break; // Arabic yeh -> Urdu yeh (choti yeh)
                case 'ى': c = 'ی'; break; // Alef maksura -> Urdu yeh
                case 'ه': c = 'ھ'; break; // Arabic heh -> Urdu do-chashmi heh
                case 'ة': c = 'ہ'; break; // Teh marbuta -> Urdu gol heh
                default: break;
            }
            sb.append(c);
        }
        // collapse whitespace, trim
        String out = sb.toString().replaceAll("[\\s\\u200c\\u200d]+", " ").trim();
        return out;
    }

    /** Resolve the best locale for a language code. */
    static Locale resolveLocale(String lang) {
        if ("ur".equals(lang)) return new Locale("ur", "PK");
        if ("hi".equals(lang)) return new Locale("hi", "IN");
        if ("en".equals(lang)) return Locale.US;
        return new Locale(lang);
    }

    class TTSBridge {
        @JavascriptInterface
        public boolean isReady() { return ttsReady; }

        @JavascriptInterface
        public String getStatus() {
            if (!ttsReady) return "init";
            return "ready";
        }

        /**
         * Check whether a proper voice is installed for lang ("ur","hi","en").
         * Returns JSON: {"lang":"ur","available":true,"needsInstall":false,"engineVoice":"..."}
         */
        @JavascriptInterface
        public String checkVoice(final String lang) {
            boolean available = false;
            boolean needsInstall = false;
            String voiceName = "";
            try {
                if (ttsReady && tts != null) {
                    Locale loc = resolveLocale(lang);
                    int r = tts.isLanguageAvailable(loc);
                    if (r == TextToSpeech.LANG_MISSING_DATA) {
                        needsInstall = true;
                    } else if (r == TextToSpeech.LANG_AVAILABLE
                            || r == TextToSpeech.LANG_COUNTRY_AVAILABLE
                            || r == TextToSpeech.LANG_COUNTRY_VAR_AVAILABLE) {
                        available = true;
                        try {
                            Set<Voice> voices = tts.getVoices();
                            if (voices != null) {
                                for (Voice v : voices) {
                                    Locale vl = v.getLocale();
                                    if (vl != null && vl.getLanguage().equals(loc.getLanguage())) {
                                        voiceName = v.getName();
                                        break;
                                    }
                                }
                            }
                        } catch (Exception ignored) {}
                    }
                    // also try bare language as fallback probe
                    if (!available && !needsInstall) {
                        int r2 = tts.isLanguageAvailable(new Locale(loc.getLanguage()));
                        if (r2 == TextToSpeech.LANG_MISSING_DATA) needsInstall = true;
                        else if (r2 >= TextToSpeech.LANG_AVAILABLE) available = true;
                    }
                }
            } catch (Exception ignored) {}
            voiceName = voiceName.replace("\"", "");
            return "{\"lang\":\"" + lang + "\",\"available\":" + available
                    + ",\"needsInstall\":" + needsInstall
                    + ",\"engineVoice\":\"" + voiceName + "\"}";
        }

        /** Open the system TTS voice-data installer. */
        @JavascriptInterface
        public void openVoiceInstaller() {
            try {
                Intent inst = new Intent(TextToSpeech.Engine.ACTION_INSTALL_TTS_DATA);
                inst.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(inst);
            } catch (Exception ignored) {}
        }

        /**
         * Synthesize text to a WAV file, delivered via onTTSDone(utteranceId, dataUri)
         * or onTTSFailed(utteranceId, reason).
         * lang: "ur", "hi", "en". pitch: 0.5-2.0 (1=normal). rate: 0.5-2.0.
         */
        @JavascriptInterface
        public void speakToFile(final String text, final String lang, final float pitch, final float rate, final String utteranceId) {
            runOnUiThread(() -> {
                if (!ttsReady || tts == null) {
                    js("onTTSFailed('" + utteranceId + "','tts not ready')");
                    return;
                }
                try {
                    String clean = normalizeUrdu(text);
                    if (clean.isEmpty()) clean = text;
                    Locale loc = resolveLocale(lang);
                    int r = tts.setLanguage(loc);
                    if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
                        // fallback: bare language code
                        r = tts.setLanguage(new Locale(loc.getLanguage()));
                        if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
                            try {
                                Intent inst = new Intent(TextToSpeech.Engine.ACTION_INSTALL_TTS_DATA);
                                startActivity(inst);
                            } catch (Exception ignored) {}
                            js("onTTSFailed('" + utteranceId + "','voice data missing')");
                            return;
                        }
                    }
                    tts.setPitch(Math.max(0.5f, Math.min(2.0f, pitch)));
                    // slightly slower default for clearer Urdu pronunciation
                    float effRate = Math.max(0.5f, Math.min(2.0f, rate));
                    if ("ur".equals(lang) && effRate > 0.95f) effRate = 0.9f;
                    tts.setSpeechRate(effRate);
                    File out = new File(getCacheDir(), "tts_" + utteranceId + ".wav");
                    if (out.exists()) out.delete();
                    BundleCompat.synthesize(tts, clean, utteranceId, out.getAbsolutePath());
                } catch (Exception e) {
                    js("onTTSFailed('" + utteranceId + "','exception')");
                }
            });
        }
    }

    /** synthesizeToFile with Bundle params (API 21+) */
    static class BundleCompat {
        static void synthesize(TextToSpeech tts, String text, String id, String path) {
            android.os.Bundle params = new android.os.Bundle();
            params.putString(TextToSpeech.Engine.KEY_PARAM_UTTERANCE_ID, id);
            tts.synthesizeToFile(text, params, new File(path), id);
        }
    }

    /**
     * v3.16: In-app updater — downloads the new APK and opens the installer.
     * Called from JS: window.HamzaUpdate.downloadAndInstall(url)
     */
    class UpdateBridge {
        private long downloadId = -1;
        private BroadcastReceiver receiver;

        @JavascriptInterface
        public void downloadAndInstall(final String url) {
            runOnUiThread(() -> {
                try {
                    // Android 8+: need "install unknown apps" permission; system prompts if missing
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        if (!getPackageManager().canRequestPackageInstalls()) {
                            Intent perm = new Intent(android.provider.Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                                    Uri.parse("package:" + getPackageName()));
                            perm.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                            startActivity(perm);
                            Toast.makeText(MainActivity.this,
                                    "Pehle 'Allow from this source' ON karo, phir dobara Update dabao 🙏",
                                    Toast.LENGTH_LONG).show();
                            js("onUpdateMsg('permission')");
                            return;
                        }
                    }
                    Toast.makeText(MainActivity.this, "⬇️ Update download ho rahi hai...", Toast.LENGTH_SHORT).show();
                    js("onUpdateMsg('downloading')");

                    DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                    DownloadManager.Request req = new DownloadManager.Request(Uri.parse(url));
                    req.setTitle("MEER Update");
                    req.setDescription("Nayi version download ho rahi hai...");
                    req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                    req.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MEER-update.apk");
                    req.setMimeType("application/vnd.android.package-archive");
                    downloadId = dm.enqueue(req);

                    if (receiver != null) {
                        try { unregisterReceiver(receiver); } catch (Exception ignored) {}
                    }
                    receiver = new BroadcastReceiver() {
                        @Override public void onReceive(Context ctx, Intent intent) {
                            long id = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1);
                            if (id == downloadId) {
                                try { unregisterReceiver(this); } catch (Exception ignored) {}
                                installApk();
                            }
                        }
                    };
                    registerReceiver(receiver, new IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE));
                } catch (Exception e) {
                    js("onUpdateMsg('error')");
                }
            });
        }

        private void installApk() {
            try {
                File apk = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS),
                        "MEER-update.apk");
                if (!apk.exists()) {
                    js("onUpdateMsg('error')");
                    return;
                }
                Uri uri = FileProvider.getUriForFile(MainActivity.this,
                        getPackageName() + ".fileprovider", apk);
                Intent inst = new Intent(Intent.ACTION_VIEW);
                inst.setDataAndType(uri, "application/vnd.android.package-archive");
                inst.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_GRANT_READ_URI_PERMISSION);
                js("onUpdateMsg('installing')");
                startActivity(inst);
            } catch (Exception e) {
                js("onUpdateMsg('error')");
            }
        }
    }

    /**
     * v3.21: Real Cartoon — downloads real AI video clips once into app storage,
     * JS plays them locally in a hidden <video> and records via canvas.
     * Called from JS: window.RealClipBridge.downloadClips() / getClipPath(name) /
     * areClipsReady() / getDownloadedCount()
     */
    // v3.62: DownloadBridge - blob URL downloads ke liye callback
    // JS blob ko base64 me convert karke onBlobData() call karta hai
    class DownloadBridge {
        @JavascriptInterface
        public void onBlobData(String dataUrl, String mimeType) {
            runOnUiThread(() -> {
                try {
                    if (dataUrl == null || dataUrl.length() < 100) {
                        Toast.makeText(MainActivity.this,
                            "Download fail: khaali data", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    String b64 = dataUrl;
                    if (b64.contains(",")) {
                        b64 = b64.substring(b64.indexOf(",") + 1);
                    }
                    byte[] data = Base64.decode(b64, Base64.DEFAULT);
                    if (data.length < 1000) {
                        Toast.makeText(MainActivity.this,
                            "Download fail: file chhoti hai", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    String fileName = "MEER-" + System.currentTimeMillis() + ".webm";
                    if (mimeType != null && mimeType.contains("mp4")) {
                        fileName = fileName.replace(".webm", ".mp4");
                    }
                    android.content.ContentValues values = new android.content.ContentValues();
                    values.put(android.provider.MediaStore.MediaColumns.DISPLAY_NAME, fileName);
                    values.put(android.provider.MediaStore.MediaColumns.MIME_TYPE,
                        mimeType != null ? mimeType : "video/webm");
                    values.put(android.provider.MediaStore.MediaColumns.RELATIVE_PATH,
                        Environment.DIRECTORY_DOWNLOADS + "/MEER");
                    Uri uri = getContentResolver().insert(
                        android.provider.MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values);
                    if (uri != null) {
                        try (java.io.OutputStream os =
                                getContentResolver().openOutputStream(uri)) {
                            os.write(data);
                            os.flush();
                        }
                        Toast.makeText(MainActivity.this,
                            "✅ Video save ho gayi! Downloads/MEER",
                            Toast.LENGTH_LONG).show();
                    } else {
                        Toast.makeText(MainActivity.this,
                            "Download fail: save nahi hua", Toast.LENGTH_SHORT).show();
                    }
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this,
                        "Download fail: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        }
    }

    class RealClipBridge {
        private static final String CLIP_BASE =
                "https://github.com/Hamzaagsm/videomaker/releases/download/clips-v1/";
        private static final String[] CLIPS = {
                "rayo-driving.mp4", "rayo-talking.mp4",
                "bella-driving.mp4", "bella-talking.mp4",
                "rusty-driving.mp4"
        };
        // v3.22: 4 new modes — clips hosted on clips-v2 release
        private static final String CLIP_BASE_V2 =
                "https://github.com/Hamzaagsm/videomaker/releases/download/clips-v2/";
        private static final String[] CLIPS_V2 = {
                "story-narrator.mp4", "story-magic.mp4",
                "kids-hero.mp4", "kids-play.mp4",
                "interview-host.mp4",
                "drama-heroine.mp4"
        };
        // v3.23: Family Story mode — clips hosted on clips-v3 release
        private static final String CLIP_BASE_V3 =
                "https://github.com/Hamzaagsm/videomaker/releases/download/clips-v3/";
        private static final String[] CLIPS_V3 = {
                "woman-happy.mp4", "woman-walking.mp4",
                "man-friendly.mp4", "man-walking.mp4",
                "baby-cute.mp4", "baby-playing.mp4"
        };
        // v3.25: Suspense Stories mode — clips hosted on clips-v4 release
        private static final String CLIP_BASE_V4 =
                "https://github.com/Hamzaagsm/videomaker/releases/download/clips-v4/";
        private static final String[] CLIPS_V4 = {
                "suspense-night-drive.mp4", "suspense-haunted-garage.mp4",
                "suspense-mystery-door.mp4", "suspense-cars-scared.mp4",
                "suspense-flashlight.mp4"
        };

        private String[] clipsForMode(String mode) {
            if ("story".equals(mode)) return new String[]{"story-narrator.mp4", "story-magic.mp4"};
            if ("kids".equals(mode)) return new String[]{"kids-hero.mp4", "kids-play.mp4"};
            if ("interview".equals(mode)) return new String[]{"interview-host.mp4"};
            if ("drama".equals(mode)) return new String[]{"drama-heroine.mp4"};
            if ("family".equals(mode)) return CLIPS_V3;
            if ("suspense".equals(mode)) return CLIPS_V4;
            return CLIPS; // default: v1 real cartoon clips
        }

        private String clipBaseFor(String name) {
            for (String c : CLIPS_V2) if (c.equals(name)) return CLIP_BASE_V2;
            for (String c : CLIPS_V3) if (c.equals(name)) return CLIP_BASE_V3;
            return CLIP_BASE;
        }

        private File clipDir() {
            File d = new File(getExternalFilesDir(null), "clips");
            if (!d.exists()) d.mkdirs();
            return d;
        }

        private boolean clipOk(File f) {
            return f.exists() && f.length() > 100000;
        }

        @JavascriptInterface
        public void downloadClips() {
            runOnUiThread(() -> {
                try {
                    File dir = clipDir();
                    DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                    int started = 0;
                    for (String name : CLIPS) {
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
                    }
                    js("onClipMsg('started'," + started + ")");
                    if (started == 0) js("onClipMsg('ready',0)");
                } catch (Exception e) {
                    js("onClipMsg('error',0)");
                }
            });
        }

        @JavascriptInterface
        public boolean areClipsReady() {
            File dir = clipDir();
            for (String name : CLIPS) {
                if (!clipOk(new File(dir, name))) return false;
            }
            return true;
        }

        @JavascriptInterface
        public int getDownloadedCount() {
            File dir = clipDir();
            int n = 0;
            for (String name : CLIPS) {
                if (clipOk(new File(dir, name))) n++;
            }
            return n;
        }

        @JavascriptInterface
        public String getClipPath(String name) {
            try {
                // only allow known clip names (no path traversal) — v1 + v2 + v3
                boolean ok = false;
                for (String c : CLIPS) if (c.equals(name)) { ok = true; break; }
                if (!ok) for (String c : CLIPS_V2) if (c.equals(name)) { ok = true; break; }
                if (!ok) for (String c : CLIPS_V3) if (c.equals(name)) { ok = true; break; }
                if (!ok) return "";
                File f = new File(clipDir(), name);
                if (clipOk(f)) return f.getAbsolutePath();
            } catch (Exception ignored) {}
            return "";
        }

        // v3.22: per-mode clip management for Story/Kids/Interview/Drama
        @JavascriptInterface
        public void downloadModeClips(String mode) {
            runOnUiThread(() -> {
                try {
                    File dir = clipDir();
                    DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                    int started = 0;
                    for (String name : clipsForMode(mode)) {
                        File f = new File(dir, name);
                        if (clipOk(f)) continue; // already downloaded
                        DownloadManager.Request req =
                                new DownloadManager.Request(Uri.parse(clipBaseFor(name) + name));
                        req.setTitle("MEER clip: " + name);
                        req.setNotificationVisibility(
                                DownloadManager.Request.VISIBILITY_VISIBLE);
                        req.setDestinationUri(Uri.fromFile(f));
                        dm.enqueue(req);
                        started++;
                    }
                    js("onModeClipMsg('" + mode + "','started'," + started + ")");
                    if (started == 0) js("onModeClipMsg('" + mode + "','ready',0)");
                } catch (Exception e) {
                    js("onModeClipMsg('" + mode + "','error',0)");
                }
            });
        }

        @JavascriptInterface
        public boolean areModeClipsReady(String mode) {
            File dir = clipDir();
            for (String name : clipsForMode(mode)) {
                if (!clipOk(new File(dir, name))) return false;
            }
            return true;
        }

        @JavascriptInterface
        public int getModeDownloadedCount(String mode) {
            File dir = clipDir();
            int n = 0;
            for (String name : clipsForMode(mode)) {
                if (clipOk(new File(dir, name))) n++;
            }
            return n;
        }

        @JavascriptInterface
        public int getModeTotalClips(String mode) {
            return clipsForMode(mode).length;
        }

        // v3.42: Save generated video to Downloads (best quality, original blob)
        @JavascriptInterface
        public String saveVideo(String base64Data, String fileName) {
            try {
                if (base64Data == null || base64Data.isEmpty()) return "error:empty";
                // Strip data URI prefix if present
                if (base64Data.contains(",")) {
                    base64Data = base64Data.substring(base64Data.indexOf(",") + 1);
                }
                byte[] data = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT);
                if (data.length < 1000) return "error:too_small";

                String mimeType = "video/webm";
                if (fileName.endsWith(".mp4")) mimeType = "video/mp4";

                android.content.ContentValues values = new android.content.ContentValues();
                values.put(android.provider.MediaStore.MediaColumns.DISPLAY_NAME, fileName);
                values.put(android.provider.MediaStore.MediaColumns.MIME_TYPE, mimeType);
                values.put(android.provider.MediaStore.MediaColumns.RELATIVE_PATH,
                        android.os.Environment.DIRECTORY_DOWNLOADS + "/MEER");

                android.content.ContentResolver resolver = getContentResolver();
                android.net.Uri uri = resolver.insert(
                        android.provider.MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values);
                if (uri == null) return "error:insert_failed";

                try (java.io.OutputStream os = resolver.openOutputStream(uri)) {
                    if (os == null) return "error:stream_failed";
                    os.write(data);
                    os.flush();
                }
                return "ok:" + fileName;
            } catch (Exception e) {
                return "error:" + e.getMessage();
            }
        }

        // v3.44: Chunked video save (bari videos ke liye - binder limit fix)
        private java.io.ByteArrayOutputStream chunkBuffer = null;
        private String chunkFileName = null;
        private int chunkExpected = 0;
        private int chunkReceived = 0;

        @JavascriptInterface
        public synchronized String saveVideoStart(String fileName, int totalChunks) {
            try {
                chunkBuffer = new java.io.ByteArrayOutputStream();
                chunkFileName = fileName;
                chunkExpected = totalChunks;
                chunkReceived = 0;
                return "ok:started";
            } catch (Exception e) {
                return "error:" + e.getMessage();
            }
        }

        @JavascriptInterface
        public synchronized String saveVideoChunk(String base64Chunk) {
            try {
                if (chunkBuffer == null) return "error:not_started";
                if (base64Chunk.contains(",")) {
                    base64Chunk = base64Chunk.substring(base64Chunk.indexOf(",") + 1);
                }
                byte[] data = android.util.Base64.decode(base64Chunk, android.util.Base64.DEFAULT);
                chunkBuffer.write(data);
                chunkReceived++;
                return "ok:chunk_" + chunkReceived;
            } catch (Exception e) {
                return "error:" + e.getMessage();
            }
        }

        @JavascriptInterface
        public synchronized String saveVideoFinish() {
            try {
                if (chunkBuffer == null) return "error:not_started";
                byte[] data = chunkBuffer.toByteArray();
                chunkBuffer = null;
                if (data.length < 1000) return "error:too_small";

                String mimeType = "video/webm";
                if (chunkFileName.endsWith(".mp4")) mimeType = "video/mp4";

                android.content.ContentValues values = new android.content.ContentValues();
                values.put(android.provider.MediaStore.MediaColumns.DISPLAY_NAME, chunkFileName);
                values.put(android.provider.MediaStore.MediaColumns.MIME_TYPE, mimeType);
                values.put(android.provider.MediaStore.MediaColumns.RELATIVE_PATH,
                        android.os.Environment.DIRECTORY_DOWNLOADS + "/MEER");

                android.content.ContentResolver resolver = getContentResolver();
                android.net.Uri uri = resolver.insert(
                        android.provider.MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values);
                if (uri == null) return "error:insert_failed";

                try (java.io.OutputStream os = resolver.openOutputStream(uri)) {
                    if (os == null) return "error:stream_failed";
                    os.write(data);
                    os.flush();
                }
                String result = "ok:" + chunkFileName;
                chunkFileName = null;
                return result;
            } catch (Exception e) {
                chunkBuffer = null;
                return "error:" + e.getMessage();
            }
        }

        // v3.62: NATIVE video composition! Canvas recording ki bajaye clips + audio ko natively joro.
        // Segments JSON: [{clip:"rayo-driving.mp4", audio:"/path/to/audio.wav", duration:5.2}, ...]
        // Output: MP4 file in Downloads/MEER
        @JavascriptInterface
        public String composeVideo(String segmentsJson, String fileName) {
            try {
                org.json.JSONArray segs = new org.json.JSONArray(segmentsJson);
                if (segs.length() == 0) return "error:no_segments";

                // Output file
                File outDir = new File(Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_DOWNLOADS), "MEER");
                if (!outDir.exists()) outDir.mkdirs();
                File outFile = new File(outDir, fileName);
                if (!fileName.endsWith(".mp4")) {
                    outFile = new File(outDir, fileName + ".mp4");
                }

                android.media.MediaMuxer muxer = new android.media.MediaMuxer(
                    outFile.getAbsolutePath(),
                    android.media.MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);

                int videoTrackIndex = -1;
                int audioTrackIndex = -1;
                long videoPtsUs = 0;
                long audioPtsUs = 0;

                java.nio.ByteBuffer buffer = java.nio.ByteBuffer.allocate(1024 * 1024);
                android.media.MediaCodec.BufferInfo bufferInfo = new android.media.MediaCodec.BufferInfo();

                for (int s = 0; s < segs.length(); s++) {
                    org.json.JSONObject seg = segs.getJSONObject(s);
                    String clipName = seg.optString("clip", "");
                    String audioPath = seg.optString("audio", "");
                    double durationSec = seg.optDouble("duration", 3.0);

                    // Get clip file path
                    String clipPath = getClipPath(clipName);
                    if (clipPath == null || clipPath.isEmpty()) continue;
                    // Remove file:// prefix if present
                    if (clipPath.startsWith("file://")) {
                        clipPath = clipPath.substring(7);
                    }
                    File clipFile = new File(clipPath);
                    if (!clipFile.exists()) continue;

                    // Extract video from clip
                    android.media.MediaExtractor videoExtractor = new android.media.MediaExtractor();
                    try {
                        videoExtractor.setDataSource(clipFile.getAbsolutePath());
                        int videoTrack = selectTrack(videoExtractor, "video/");
                        if (videoTrack < 0) {
                            videoExtractor.release();
                            continue;
                        }
                        videoExtractor.selectTrack(videoTrack);
                        android.media.MediaFormat videoFormat = videoExtractor.getTrackFormat(videoTrack);

                        if (videoTrackIndex == -1) {
                            videoTrackIndex = muxer.addTrack(videoFormat);
                        }

                        // Extract audio from TTS file (if provided)
                        android.media.MediaExtractor audioExtractor = null;
                        int audioTrack = -1;
                        if (audioPath != null && !audioPath.isEmpty()) {
                            if (audioPath.startsWith("file://")) {
                                audioPath = audioPath.substring(7);
                            }
                            File audioFile = new File(audioPath);
                            if (audioFile.exists()) {
                                audioExtractor = new android.media.MediaExtractor();
                                try {
                                    audioExtractor.setDataSource(audioFile.getAbsolutePath());
                                    audioTrack = selectTrack(audioExtractor, "audio/");
                                    if (audioTrack >= 0) {
                                        audioExtractor.selectTrack(audioTrack);
                                        android.media.MediaFormat audioFormat =
                                            audioExtractor.getTrackFormat(audioTrack);
                                        if (audioTrackIndex == -1) {
                                            audioTrackIndex = muxer.addTrack(audioFormat);
                                        }
                                    }
                                } catch (Exception e) {
                                    if (audioExtractor != null) {
                                        audioExtractor.release();
                                        audioExtractor = null;
                                    }
                                    audioTrack = -1;
                                }
                            }
                        }

                        // Start muxer on first segment
                        if (s == 0) {
                            muxer.start();
                        }

                        // Copy video samples (loop if needed to match duration)
                        long segmentDurationUs = (long)(durationSec * 1000000);
                        long videoStartPts = videoPtsUs;
                        long clipDurationUs = getTrackDurationUs(videoExtractor, videoTrack);

                        // If clip is shorter than needed, loop it
                        while (videoPtsUs - videoStartPts < segmentDurationUs) {
                            videoExtractor.seekTo(0, android.media.MediaExtractor.SEEK_TO_CLOSEST_SYNC);
                            while (true) {
                                int sampleSize = videoExtractor.readSampleData(buffer, 0);
                                if (sampleSize < 0) break;

                                bufferInfo.offset = 0;
                                bufferInfo.size = sampleSize;
                                bufferInfo.presentationTimeUs = videoPtsUs +
                                    videoExtractor.getSampleTime();
                                bufferInfo.flags = videoExtractor.getSampleFlags();

                                // Check if we've exceeded segment duration
                                if (videoPtsUs + videoExtractor.getSampleTime() - videoStartPts
                                        > segmentDurationUs) {
                                    break;
                                }

                                muxer.writeSampleData(videoTrackIndex, buffer, bufferInfo);
                                videoExtractor.advance();
                            }
                            if (clipDurationUs <= 0) break; // Avoid infinite loop
                            videoPtsUs += clipDurationUs;
                            // Safety: don't loop more than 10 times
                            if ((videoPtsUs - videoStartPts) / clipDurationUs > 10) break;
                        }
                        // Ensure video PTS advances to segment end
                        videoPtsUs = Math.max(videoPtsUs, videoStartPts + segmentDurationUs);

                        // Copy audio samples
                        if (audioExtractor != null && audioTrack >= 0 && audioTrackIndex >= 0) {
                            long audioStartPts = audioPtsUs;
                            while (true) {
                                int sampleSize = audioExtractor.readSampleData(buffer, 0);
                                if (sampleSize < 0) break;

                                bufferInfo.offset = 0;
                                bufferInfo.size = sampleSize;
                                bufferInfo.presentationTimeUs = audioPtsUs +
                                    audioExtractor.getSampleTime();
                                bufferInfo.flags = audioExtractor.getSampleFlags();

                                muxer.writeSampleData(audioTrackIndex, buffer, bufferInfo);
                                audioExtractor.advance();
                            }
                            // Advance audio PTS by actual audio duration
                            long audioDur = getTrackDurationUs(audioExtractor, audioTrack);
                            audioPtsUs = Math.max(audioPtsUs + audioDur,
                                audioStartPts + segmentDurationUs);
                            audioExtractor.release();
                        } else {
                            // No audio: advance audio PTS to keep sync
                            audioPtsUs = Math.max(audioPtsUs, videoPtsUs);
                        }

                        videoExtractor.release();

                    } catch (Exception e) {
                        try { videoExtractor.release(); } catch (Exception ignored) {}
                        // Continue with next segment
                    }
                }

                try { muxer.stop(); } catch (Exception ignored) {}
                try { muxer.release(); } catch (Exception ignored) {}

                if (videoTrackIndex == -1) {
                    return "error:no_video_track";
                }

                // Notify media scanner
                try {
                    android.media.MediaScannerConnection.scanFile(
                        MainActivity.this,
                        new String[]{outFile.getAbsolutePath()},
                        new String[]{"video/mp4"}, null);
                } catch (Exception ignored) {}

                return "ok:" + outFile.getAbsolutePath();

            } catch (Exception e) {
                return "error:" + e.getMessage();
            }
        }

        private int selectTrack(android.media.MediaExtractor extractor, String mimePrefix) {
            int numTracks = extractor.getTrackCount();
            for (int i = 0; i < numTracks; i++) {
                android.media.MediaFormat format = extractor.getTrackFormat(i);
                String mime = format.getString(android.media.MediaFormat.KEY_MIME);
                if (mime != null && mime.startsWith(mimePrefix)) {
                    return i;
                }
            }
            return -1;
        }

        private long getTrackDurationUs(android.media.MediaExtractor extractor, int trackIndex) {
            try {
                android.media.MediaFormat format = extractor.getTrackFormat(trackIndex);
                if (format.containsKey(android.media.MediaFormat.KEY_DURATION)) {
                    return format.getLong(android.media.MediaFormat.KEY_DURATION);
                }
            } catch (Exception ignored) {}
            return 0;
        }

        // v3.62: Share video file from path (native composition ke liye)
        @JavascriptInterface
        public void shareVideoFile(String filePath) {
            runOnUiThread(() -> {
                try {
                    File f = new File(filePath);
                    if (!f.exists()) {
                        Toast.makeText(MainActivity.this,
                            "File nahi mili", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    Uri uri = androidx.core.content.FileProvider.getUriForFile(
                        MainActivity.this,
                        getPackageName() + ".fileprovider",
                        f);
                    Intent share = new Intent(Intent.ACTION_SEND);
                    share.setType("video/mp4");
                    share.putExtra(Intent.EXTRA_STREAM, uri);
                    share.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    share.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(Intent.createChooser(share, "Video share karo"));
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this,
                        "Share fail: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        }
    }

    @Override
    protected void onDestroy() {
        if (tts != null) { try { tts.stop(); tts.shutdown(); } catch (Exception ignored) {} }
        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }
}
