package com.hamza.videomaker;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.File;
import java.io.FileInputStream;
import java.util.Locale;

/**
 * Hamza AI Studio — WebView wrapper with NATIVE Android TTS.
 * window.HamzaTTS exposes on-device text-to-speech to JavaScript,
 * so voice works 100% offline with no network blocking.
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
        web.setWebViewClient(new WebViewClient());
        web.setWebChromeClient(new WebChromeClient());
        web.addJavascriptInterface(new TTSBridge(), "HamzaTTS");

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
            // pass via a small JS call; base64 of a short phrase is fine
            js("onTTSDone('" + utteranceId + "','data:audio/wav;base64," + b64 + "')");
        } catch (Exception e) {
            js("onTTSFailed('" + utteranceId + "','read error')");
        }
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
                    Locale loc = new Locale(lang);
                    int r = tts.setLanguage(loc);
                    if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
                        // try with country, then default
                        if (lang.equals("ur")) loc = new Locale("ur", "PK");
                        else if (lang.equals("hi")) loc = new Locale("hi", "IN");
                        else loc = Locale.US;
                        r = tts.setLanguage(loc);
                        if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
                            // ask user to install voice data once
                            Intent inst = new Intent(TextToSpeech.Engine.ACTION_INSTALL_TTS_DATA);
                            try { startActivity(inst); } catch (Exception ignored) {}
                            js("onTTSFailed('" + utteranceId + "','voice data missing')");
                            return;
                        }
                    }
                    tts.setPitch(Math.max(0.5f, Math.min(2.0f, pitch)));
                    tts.setSpeechRate(Math.max(0.5f, Math.min(2.0f, rate)));
                    File out = new File(getCacheDir(), "tts_" + utteranceId + ".wav");
                    if (out.exists()) out.delete();
                    BundleCompat.synthesize(tts, text, utteranceId, out.getAbsolutePath());
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
