package com.hamza.videomaker;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.speech.tts.Voice;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
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
