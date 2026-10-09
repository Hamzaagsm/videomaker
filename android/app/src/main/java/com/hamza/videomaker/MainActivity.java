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
        web.addJavascriptInterface(new TTSBridge(), "HamzaTTS");
        web.addJavascriptInterface(new UpdateBridge(), "HamzaUpdate");
        web.addJavascriptInterface(new RealClipBridge(), "RealClipBridge"); // v3.21: real cartoon clips

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
    class RealClipBridge {
        private static final String CLIP_BASE =
                "https://github.com/Hamzaagsm/videomaker/releases/download/clips-v1/";
        private static final String[] CLIPS = {
                "rayo-driving.mp4", "rayo-talking.mp4",
                "bella-driving.mp4", "bella-talking.mp4",
                "rusty-driving.mp4"
        };

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
                // only allow known clip names (no path traversal)
                boolean ok = false;
                for (String c : CLIPS) if (c.equals(name)) { ok = true; break; }
                if (!ok) return "";
                File f = new File(clipDir(), name);
                if (clipOk(f)) return f.getAbsolutePath();
            } catch (Exception ignored) {}
            return "";
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
