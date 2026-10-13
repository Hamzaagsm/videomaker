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
                // v3.68: backgrounds bhi clips ki tarah use ho sakte hain!
                if (!ok) for (String b : BACKGROUNDS) if (b.equals(name)) {
                    File bf = new File(bgDir(), name);
                    if (clipOk(bf)) return bf.getAbsolutePath();
                }
                if (!ok) return "";
                File f = new File(clipDir(), name);
                if (clipOk(f)) return f.getAbsolutePath();
            } catch (Exception ignored) {}
            return "";
        }

        // v3.68: ONLINE BACKGROUNDS for single car mode (har gari ka background!)
        private static final String BG_BASE =
                "https://github.com/Hamzaagsm/videomaker/releases/download/backgrounds-v1/";
        private static final String[] BACKGROUNDS = {
                "bg-hills.mp4", "bg-beach.mp4", "bg-mountain.mp4",
                "bg-city.mp4", "bg-desert.mp4", "bg-forest.mp4"
        };

        private File bgDir() {
            File d = new File(getExternalFilesDir(null), "backgrounds");
            if (!d.exists()) d.mkdirs();
            return d;
        }

        @JavascriptInterface
        public void downloadBackgrounds() {
            runOnUiThread(() -> {
                try {
                    File dir = bgDir();
                    DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                    int started = 0;
                    for (String name : BACKGROUNDS) {
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
                    }
                    js("onBgMsg('started'," + started + ")");
                    if (started == 0) js("onBgMsg('ready',0)");
                } catch (Exception e) {
                    js("onBgMsg('error',0)");
                }
            });
        }

        @JavascriptInterface
        public boolean areBackgroundsReady() {
            File dir = bgDir();
            for (String name : BACKGROUNDS) {
                if (!clipOk(new File(dir, name))) return false;
            }
            return true;
        }

        @JavascriptInterface
        public String getBackgroundPath(String name) {
            try {
                boolean ok = false;
                for (String b : BACKGROUNDS) if (b.equals(name)) { ok = true; break; }
                if (!ok) return "";
                File f = new File(bgDir(), name);
                if (clipOk(f)) return f.getAbsolutePath();
            } catch (Exception ignored) {}
            return "";
        }

        @JavascriptInterface
        public String getRandomBackgroundPath() {
            try {
                File dir = bgDir();
                java.util.List<String> available = new java.util.ArrayList<>();
                for (String b : BACKGROUNDS) {
                    File f = new File(dir, b);
                    if (clipOk(f)) available.add(f.getAbsolutePath());
                }
                if (available.isEmpty()) return "";
                int idx = new java.util.Random().nextInt(available.size());
                return available.get(idx);
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

        // v3.63: Base64 audio (TTS data URI) ko temp WAV file me save karo, path return karo
        // Kyunke nativeSpeak data:audio/wav;base64,... return karta hai, file path nahi!
        // v3.64 FIX: Purani files YAHAN delete NA karo! Loop me har segment ki file chahiye!
        // Cleanup composeVideo ke start me hoti hai (ek dafa).
        @JavascriptInterface
        public String saveAudioBase64(String base64Data, String fileName) {
            try {
                if (base64Data == null || base64Data.isEmpty()) return "";
                // data: prefix hatao agar ho
                if (base64Data.contains(",")) {
                    base64Data = base64Data.substring(base64Data.indexOf(",") + 1);
                }
                byte[] data = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT);
                if (data.length < 100) return "";
                File outDir = new File(getCacheDir(), "compose_audio");
                if (!outDir.exists()) outDir.mkdirs();
                File out = new File(outDir, fileName);
                try (java.io.FileOutputStream fos = new java.io.FileOutputStream(out)) {
                    fos.write(data);
                    fos.flush();
                }
                return out.getAbsolutePath();
            } catch (Exception e) {
                return "";
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

                // v3.64: Compose shuru hone par purani temp audio files saf karo (ek dafa!)
                // (saveAudioBase64 me nahi, warna loop me files delete ho jati hain!)
                try {
                    File auDir = new File(getCacheDir(), "compose_audio");
                    // NOTE: current segments ki files abhi ban rahi hain, is liye
                    // sirf 1 ghante se purani files delete karo
                    File[] auOlds = auDir.listFiles();
                    if (auOlds != null) {
                        long now = System.currentTimeMillis();
                        for (File o : auOlds) {
                            try {
                                if (now - o.lastModified() > 3600000) o.delete();
                            } catch (Exception ignored) {}
                        }
                    }
                } catch (Exception ignored) {}

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

                        // v3.66 FIX: PEHLE audio ki ASLI duration napo! (sync ka asal hal!)
                        // v3.69 FIX: WAV ko PEHLE AAC me convert karo! (GUARANTEED kaam karega!)
                        // TTS ka WAV MediaExtractor se nahi parha jata tha - is liye awaz nahi ati thi!
                        android.media.MediaExtractor audioExtractor = null;
                        int audioTrack = -1;
                        long actualAudioDurUs = 0;
                        if (audioPath != null && !audioPath.isEmpty()) {
                            if (audioPath.startsWith("file://")) {
                                audioPath = audioPath.substring(7);
                            }
                            File audioFile = new File(audioPath);
                            if (audioFile.exists() && audioFile.length() > 1000) {
                                // v3.69: WAV -> AAC transcode (agar WAV hai to!)
                                String aacPath = audioPath;
                                if (audioPath.toLowerCase().endsWith(".wav")) {
                                    String transcoded = wavToAac(audioPath);
                                    if (transcoded != null && !transcoded.isEmpty()) {
                                        aacPath = transcoded;
                                    }
                                }
                                audioExtractor = new android.media.MediaExtractor();
                                try {
                                    audioExtractor.setDataSource(aacPath);
                                    audioTrack = selectTrack(audioExtractor, "audio/");
                                    if (audioTrack >= 0) {
                                        audioExtractor.selectTrack(audioTrack);
                                        android.media.MediaFormat audioFormat =
                                            audioExtractor.getTrackFormat(audioTrack);
                                        if (audioTrackIndex == -1) {
                                            audioTrackIndex = muxer.addTrack(audioFormat);
                                        }
                                        // Asli duration napo: last sample time!
                                        long lastSt = 0;
                                        while (true) {
                                            int sz = audioExtractor.readSampleData(buffer, 0);
                                            if (sz < 0) break;
                                            lastSt = audioExtractor.getSampleTime();
                                            audioExtractor.advance();
                                        }
                                        actualAudioDurUs = lastSt + 20000; // last frame + margin
                                        // Rewind for actual copy later
                                        audioExtractor.seekTo(0, android.media.MediaExtractor.SEEK_TO_CLOSEST_SYNC);
                                    }
                                } catch (Exception e) {
                                    if (audioExtractor != null) {
                                        audioExtractor.release();
                                        audioExtractor = null;
                                    }
                                    audioTrack = -1;
                                    actualAudioDurUs = 0;
                                }
                            }
                        }

                        // v3.66: Segment duration = ASLI audio + 0.3s gap (JS wali ignore!)
                        // Is se video hamesha audio ke barabar - na mute, na desync!
                        if (actualAudioDurUs > 500000) { // 0.5s se zyada audio hai
                            durationSec = (actualAudioDurUs / 1000000.0) + 0.3;
                        } else if (durationSec < 1.0 || durationSec > 30.0) {
                            durationSec = 3.0; // invalid JS duration -> safe default
                        }

                        // Start muxer on first segment
                        if (s == 0) {
                            muxer.start();
                        }

                        // v3.63 FIX: Copy video samples with CONTINUOUS PTS (koi gap nahi!)
                        // Har frame ko videoPtsUs do, phir actual frame duration se aage barho.
                        // Is se clip loop ho ya na ho, freeze nahi hoga!
                        long segmentDurationUs = (long)(durationSec * 1000000);
                        long videoStartPts = videoPtsUs;
                        long frameDurUs = 33333; // default 30fps, clip se update hoga
                        int loopCount = 0;

                        while (videoPtsUs - videoStartPts < segmentDurationUs && loopCount < 20) {
                            videoExtractor.seekTo(0, android.media.MediaExtractor.SEEK_TO_CLOSEST_SYNC);
                            long prevSampleTime = -1;
                            boolean wroteInPass = false;
                            while (true) {
                                int sampleSize = videoExtractor.readSampleData(buffer, 0);
                                if (sampleSize < 0) break;
                                long st = videoExtractor.getSampleTime();
                                if (prevSampleTime >= 0 && st > prevSampleTime) {
                                    frameDurUs = st - prevSampleTime;
                                    if (frameDurUs <= 0 || frameDurUs > 1000000) frameDurUs = 33333;
                                }
                                prevSampleTime = st;
                                // Segment duration poori ho gayi?
                                if (videoPtsUs - videoStartPts >= segmentDurationUs) break;
                                bufferInfo.offset = 0;
                                bufferInfo.size = sampleSize;
                                bufferInfo.presentationTimeUs = videoPtsUs;
                                bufferInfo.flags = videoExtractor.getSampleFlags();
                                muxer.writeSampleData(videoTrackIndex, buffer, bufferInfo);
                                wroteInPass = true;
                                videoPtsUs += frameDurUs;
                                videoExtractor.advance();
                            }
                            loopCount++;
                            if (!wroteInPass) break; // kuch nahi likha -> bahar
                        }
                        // Segment end tak PTS pohunchao (gap na rahe)
                        if (videoPtsUs < videoStartPts + segmentDurationUs) {
                            videoPtsUs = videoStartPts + segmentDurationUs;
                        }

                        // Copy audio samples (ab audioPath hamesha valid file hai - v3.63)
                        if (audioExtractor != null && audioTrack >= 0 && audioTrackIndex >= 0) {
                            long audioStartPts = audioPtsUs;
                            long prevAuSt = -1;
                            long auFrameDur = 20000;
                            while (true) {
                                int sampleSize = audioExtractor.readSampleData(buffer, 0);
                                if (sampleSize < 0) break;
                                long st = audioExtractor.getSampleTime();
                                if (prevAuSt >= 0 && st > prevAuSt) {
                                    auFrameDur = st - prevAuSt;
                                    if (auFrameDur <= 0 || auFrameDur > 1000000) auFrameDur = 20000;
                                }
                                prevAuSt = st;
                                bufferInfo.offset = 0;
                                bufferInfo.size = sampleSize;
                                bufferInfo.presentationTimeUs = audioPtsUs;
                                bufferInfo.flags = audioExtractor.getSampleFlags();
                                muxer.writeSampleData(audioTrackIndex, buffer, bufferInfo);
                                audioPtsUs += auFrameDur;
                                audioExtractor.advance();
                            }
                            // Audio khatam ho to bhi segment end tak PTS barhao (sync!)
                            long audioSegEnd = audioStartPts + segmentDurationUs;
                            if (audioPtsUs < audioSegEnd) audioPtsUs = audioSegEnd;
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

        // v3.69: WAV ko AAC me convert karo! (MediaMuxer ke liye GUARANTEED compatible!)
        // TTS ka WAV kabhi kabhi MediaExtractor se nahi parha jata - is liye manual transcode!
        private String wavToAac(String wavPath) {
            File wavFile = new File(wavPath);
            if (!wavFile.exists() || wavFile.length() < 100) return "";
            try {
                // WAV header parho (manual - koi dependency nahi!)
                java.io.FileInputStream fis = new java.io.FileInputStream(wavFile);
                byte[] header = new byte[44];
                if (fis.read(header) != 44) { fis.close(); return ""; }
                // "RIFF" check
                if (header[0] != 'R' || header[1] != 'I' || header[2] != 'F' || header[3] != 'F') {
                    fis.close(); return "";
                }
                // Sample rate (bytes 24-27, little endian)
                int sampleRate = (header[24] & 0xFF) | ((header[25] & 0xFF) << 8) |
                               ((header[26] & 0xFF) << 16) | ((header[27] & 0xFF) << 24);
                // Channels (bytes 22-23)
                int channels = (header[22] & 0xFF) | ((header[23] & 0xFF) << 8);
                // Bits per sample (bytes 34-35)
                int bitsPerSample = (header[34] & 0xFF) | ((header[35] & 0xFF) << 8);
                if (sampleRate <= 0 || sampleRate > 96000) sampleRate = 22050;
                if (channels <= 0 || channels > 2) channels = 1;
                if (bitsPerSample != 16) { fis.close(); return ""; } // sirf 16-bit support

                // PCM data parho
                long dataSize = wavFile.length() - 44;
                byte[] pcmData = new byte[(int) dataSize];
                int read = 0;
                while (read < dataSize) {
                    int r = fis.read(pcmData, read, (int) (dataSize - read));
                    if (r < 0) break;
                    read += r;
                }
                fis.close();
                if (read < 100) return "";

                // AAC encoder setup
                android.media.MediaFormat format = android.media.MediaFormat.createAudioFormat(
                    android.media.MediaFormat.MIMETYPE_AUDIO_AAC, sampleRate, channels);
                format.setInteger(android.media.MediaFormat.KEY_BIT_RATE, 64000);
                format.setInteger(android.media.MediaFormat.KEY_AAC_PROFILE,
                    android.media.MediaCodecInfo.CodecProfileLevel.AACObjectLC);
                format.setInteger(android.media.MediaFormat.KEY_MAX_INPUT_SIZE, 16384);

                android.media.MediaCodec encoder = android.media.MediaCodec.createEncoderByType(
                    android.media.MediaFormat.MIMETYPE_AUDIO_AAC);
                encoder.configure(format, null, null, android.media.MediaCodec.CONFIGURE_FLAG_ENCODE);
                encoder.start();

                File aacFile = new File(getCacheDir(), "aac_" + System.currentTimeMillis() + ".aac");
                java.io.FileOutputStream fos = new java.io.FileOutputStream(aacFile);

                java.nio.ByteBuffer[] inputBuffers = encoder.getInputBuffers();
                java.nio.ByteBuffer[] outputBuffers = encoder.getOutputBuffers();
                android.media.MediaCodec.BufferInfo bufferInfo = new android.media.MediaCodec.BufferInfo();

                int offset = 0;
                boolean inputDone = false;
                boolean outputDone = false;
                long ptsUs = 0;
                int bytesPerSample = 2; // 16-bit
                long totalSamples = read / (bytesPerSample * channels);

                while (!outputDone) {
                    if (!inputDone) {
                        int inputIdx = encoder.dequeueInputBuffer(10000);
                        if (inputIdx >= 0) {
                            java.nio.ByteBuffer inputBuf = inputBuffers[inputIdx];
                            inputBuf.clear();
                            int chunkSize = Math.min(inputBuf.remaining(), read - offset);
                            if (chunkSize > 0) {
                                inputBuf.put(pcmData, offset, chunkSize);
                                long samplesInChunk = chunkSize / (bytesPerSample * channels);
                                encoder.queueInputBuffer(inputIdx, 0, chunkSize, ptsUs, 0);
                                ptsUs += (samplesInChunk * 1000000L) / sampleRate;
                                offset += chunkSize;
                            }
                            if (offset >= read) {
                                encoder.queueInputBuffer(inputIdx, 0, 0, ptsUs,
                                    android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                                inputDone = true;
                            }
                        }
                    }
                    int outputIdx = encoder.dequeueOutputBuffer(bufferInfo, 10000);
                    if (outputIdx >= 0) {
                        java.nio.ByteBuffer outputBuf = outputBuffers[outputIdx];
                        if ((bufferInfo.flags & android.media.MediaCodec.BUFFER_FLAG_CODEC_CONFIG) == 0
                            && bufferInfo.size > 0) {
                            byte[] outData = new byte[bufferInfo.size];
                            outputBuf.get(outData);
                            fos.write(outData);
                        }
                        encoder.releaseOutputBuffer(outputIdx, false);
                        if ((bufferInfo.flags & android.media.MediaCodec.BUFFER_FLAG_END_OF_STREAM) != 0) {
                            outputDone = true;
                        }
                    } else if (outputIdx == android.media.MediaCodec.INFO_OUTPUT_BUFFERS_CHANGED) {
                        outputBuffers = encoder.getOutputBuffers();
                    }
                }
                fos.close();
                encoder.stop();
                encoder.release();

                if (aacFile.exists() && aacFile.length() > 100) {
                    return aacFile.getAbsolutePath();
                }
            } catch (Exception e) {
                // Transcode fail - empty return
            }
            return "";
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

        // v3.63: Share video file from path (native composition ke liye)
        // String return karta hai taake JS error dikha sake
        @JavascriptInterface
        public String shareVideoFile(String filePath) {
            try {
                File f = new File(filePath);
                if (!f.exists()) {
                    return "error:file_not_found";
                }
                if (f.length() < 1000) {
                    return "error:file_too_small";
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
                // v3.63: ClipData bhi set karo (kuch apps ke liye zaroori)
                share.setClipData(android.content.ClipData.newRawUri("video", uri));
                MainActivity.this.startActivity(Intent.createChooser(share, "Video share karo"));
                return "ok:shared";
            } catch (IllegalArgumentException e) {
                return "error:fileprovider:" + e.getMessage();
            } catch (Exception e) {
                return "error:" + e.getMessage();
            }
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
