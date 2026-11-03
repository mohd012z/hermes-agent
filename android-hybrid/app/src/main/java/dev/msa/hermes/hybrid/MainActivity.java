package dev.msa.hermes.hybrid;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.graphics.Color;
import android.view.View;
import android.widget.*;
import android.webkit.*;

public final class MainActivity extends Activity {
  private WebView browser;
  private String allowedOrigin;
  private EditText codeEditor;
  private Uri codeUri;
  private static final int OPEN_CODE = 1401;
  private static final int SAVE_CODE = 1402;
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    LinearLayout root = new LinearLayout(this);
    root.setOrientation(LinearLayout.VERTICAL);
    root.setPadding(18, 12, 18, 12);
    TextView heading = new TextView(this);
    heading.setText("Hermes Agent");
    heading.setTextColor(Color.rgb(25, 45, 70));
    heading.setTextSize(18);
    root.addView(heading);
    EditText address = new EditText(this);
    address.setSingleLine(true);
    address.setHint("Hermes dashboard address (HTTPS)");
    address.setInputType(android.text.InputType.TYPE_TEXT_VARIATION_URI);
    root.addView(address);
    Button connect = new Button(this);
    connect.setText("Connect to Hermes");
    TextView help = new TextView(this);
    help.setText("This client connects to an existing Hermes Agent dashboard. It does not include an AI model or automatically create a server. Start Hermes on your own device or computer first, then enter its secure dashboard address.");
    help.setPadding(0, 12, 0, 12);
    root.addView(help);
    TextView offlineTitle = new TextView(this);
    offlineTitle.setText("Offline workspace — notes only (no local AI model)");
    offlineTitle.setTextSize(16);
    root.addView(offlineTitle);
    EditText offlineNotes = new EditText(this);
    offlineNotes.setHint("Write notes here without internet. Saved only on this device.");
    offlineNotes.setMinLines(3);
    offlineNotes.setGravity(android.view.Gravity.TOP);
    offlineNotes.setText(getPreferences(MODE_PRIVATE).getString("offline_notes", ""));
    root.addView(offlineNotes);
    Button saveNotes = new Button(this);
    saveNotes.setText("Save offline notes");
    root.addView(saveNotes);
    Button offlineAi = new Button(this);
    offlineAi.setText("Open offline AI (AI Edge Gallery)");
    root.addView(offlineAi);
    TextView offlineHelp = new TextView(this);
    offlineHelp.setText("Requires Google AI Edge Gallery and a downloaded compatible model. Model inference runs in Gallery, not inside Hermes Hybrid.");
    root.addView(offlineHelp);
    TextView editorHeading = new TextView(this);
    editorHeading.setText("Offline source editor");
    editorHeading.setTextSize(16);
    root.addView(editorHeading);
    codeEditor = new EditText(this);
    codeEditor.setGravity(android.view.Gravity.TOP | android.view.Gravity.START);
    codeEditor.setTypeface(android.graphics.Typeface.MONOSPACE);
    codeEditor.setTextSize(13);
    codeEditor.setMinLines(7);
    codeEditor.setHorizontallyScrolling(true);
    codeEditor.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE | android.text.InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
    codeEditor.setHint("Open a source file, edit it, then Save as...");
    root.addView(codeEditor, new LinearLayout.LayoutParams(-1, 0, 1));
    LinearLayout codeActions = new LinearLayout(this);
    Button openCode = new Button(this);
    openCode.setText("Open code");
    Button saveCode = new Button(this);
    saveCode.setText("Save as...");
    codeActions.addView(openCode, new LinearLayout.LayoutParams(0, -2, 1));
    codeActions.addView(saveCode, new LinearLayout.LayoutParams(0, -2, 1));
    root.addView(codeActions);
    Button reviewPatch = new Button(this);
    reviewPatch.setText("Review replacement code from clipboard");
    root.addView(reviewPatch);
    Button copyCode = new Button(this);
    copyCode.setText("Copy editor code for offline AI");
    root.addView(copyCode);
    copyCode.setOnClickListener(v -> {
      String code = codeEditor.getText().toString();
      if (code.isEmpty()) { Toast.makeText(this, "Open or write code first", Toast.LENGTH_SHORT).show(); return; }
      new android.app.AlertDialog.Builder(this)
        .setTitle("Copy code to clipboard?")
        .setMessage("Clipboard contents can be read by other apps. Review and remove passwords, tokens and private data before copying.")
        .setNegativeButton("Cancel", null)
        .setPositiveButton("Copy", (dialog, which) -> {
          android.content.ClipboardManager cm = (android.content.ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
          if (cm != null) {
            cm.setPrimaryClip(android.content.ClipData.newPlainText("Hermes code", code));
            Toast.makeText(this, "Code copied", Toast.LENGTH_SHORT).show();
          }
        }).show();
    });
    reviewPatch.setOnClickListener(v -> {
      android.content.ClipboardManager cm = (android.content.ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
      if (cm == null || !cm.hasPrimaryClip()) { Toast.makeText(this, "Clipboard is empty", Toast.LENGTH_SHORT).show(); return; }
      android.content.ClipData clip = cm.getPrimaryClip();
      if (clip == null || clip.getItemCount() == 0) return;
      CharSequence candidate = clip.getItemAt(0).coerceToText(this);
      if (candidate == null || candidate.length() == 0 || candidate.length() > 1048576) {
        Toast.makeText(this, "Replacement must be 1 to 1048576 characters", Toast.LENGTH_LONG).show(); return;
      }
      String oldCode = codeEditor.getText().toString();
      String newCode = candidate.toString();
      if (oldCode.equals(newCode)) { Toast.makeText(this, "No changes detected", Toast.LENGTH_SHORT).show(); return; }
      int oldLines = oldCode.split("\\n", -1).length;
      int newLines = newCode.split("\\n", -1).length;
      new android.app.AlertDialog.Builder(this)
        .setTitle("Review replacement before applying")
        .setMessage("Current: " + oldLines + " lines, " + oldCode.length() + " characters.\\nProposed: " + newLines + " lines, " + newCode.length() + " characters.\\n\\nThis replaces the editor buffer only. The original file is not overwritten. Use Save as... to export after reviewing.\\n\\nProposed preview:\\n" + newCode.substring(0, Math.min(1600, newCode.length())))
        .setNegativeButton("Cancel", null)
        .setPositiveButton("Apply to editor", (dialog, which) -> codeEditor.setText(newCode))
        .show();
    });
    openCode.setOnClickListener(v -> {
      Intent pick = new Intent(Intent.ACTION_OPEN_DOCUMENT);
      pick.addCategory(Intent.CATEGORY_OPENABLE);
      pick.setType("*/*");
      startActivityForResult(pick, OPEN_CODE);
    });
    saveCode.setOnClickListener(v -> {
      Intent create = new Intent(Intent.ACTION_CREATE_DOCUMENT);
      create.addCategory(Intent.CATEGORY_OPENABLE);
      create.setType("text/plain");
      create.putExtra(Intent.EXTRA_TITLE, "code.txt");
      startActivityForResult(create, SAVE_CODE);
    });
    offlineAi.setOnClickListener(v -> {
      android.content.pm.PackageManager pm = getPackageManager();
      Intent launch = pm.getLaunchIntentForPackage("com.google.ai.edge.gallery");
      if (launch != null) {
        try { startActivity(launch); return; }
        catch (android.content.ActivityNotFoundException ignored) { }
      }
      Intent store = new Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/apps/details?id=com.google.ai.edge.gallery"));
      try { startActivity(store); }
      catch (android.content.ActivityNotFoundException e) {
        Toast.makeText(this, "Open Google Play and search AI Edge Gallery", Toast.LENGTH_LONG).show();
      }
    });
    saveNotes.setOnClickListener(v -> {
      getPreferences(MODE_PRIVATE).edit().putString("offline_notes", offlineNotes.getText().toString()).apply();
      Toast.makeText(this, "Saved locally", Toast.LENGTH_SHORT).show();
    });
    root.addView(connect);
    browser = new WebView(this);
    browser.setVisibility(View.GONE);
    root.addView(browser, new LinearLayout.LayoutParams(-1, 0, 1));
    root.setFitsSystemWindows(true);
    getWindow().setStatusBarColor(Color.WHITE);
    getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
    setContentView(root);
    WebSettings settings = browser.getSettings();
    settings.setJavaScriptEnabled(true);
    settings.setDomStorageEnabled(true);
    settings.setAllowFileAccess(false);
    settings.setAllowContentAccess(false);
    settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    WebView.setWebContentsDebuggingEnabled(false);
    browser.setWebViewClient(new WebViewClient() {
      @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
        return !isAllowed(request.getUrl());
      }
      @Override public void onReceivedSslError(WebView view, SslErrorHandler handler, android.net.http.SslError error) {
        handler.cancel();
      }
    });
    connect.setOnClickListener(v -> {
      Uri uri;
      try { uri = Uri.parse(address.getText().toString().trim()); }
      catch (RuntimeException e) { address.setError("Invalid URL"); return; }
      if (!"https".equalsIgnoreCase(uri.getScheme()) || uri.getHost() == null || uri.getUserInfo() != null || uri.getHost().isEmpty() || uri.getHost().endsWith(".example")) {
        address.setError("Enter the HTTPS URL of a running Hermes dashboard (not an example address)"); return;
      }
      int port = uri.getPort();
      allowedOrigin = "https://" + uri.getHost().toLowerCase(java.util.Locale.ROOT) + (port == -1 || port == 443 ? "" : ":" + port);
      browser.setVisibility(View.VISIBLE);
      browser.loadUrl(uri.toString());
    });
  }
  @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if (resultCode != RESULT_OK || data == null || data.getData() == null) return;
    Uri uri = data.getData();
    try {
      if (requestCode == OPEN_CODE) {
        try (java.io.InputStream stream = getContentResolver().openInputStream(uri)) {
          if (stream == null) throw new java.io.IOException("Cannot open file");
          java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
          byte[] buffer = new byte[8192];
          int n;
          while ((n = stream.read(buffer)) != -1) {
            if (out.size() + n > 1048576) throw new java.io.IOException("Source file exceeds 1 MiB limit");
            out.write(buffer, 0, n);
          }
          byte[] bytes = out.toByteArray();
          for (byte b : bytes) if (b == 0) throw new java.io.IOException("Binary file is not supported");
          codeEditor.setText(new String(bytes, java.nio.charset.StandardCharsets.UTF_8));
          codeUri = uri;
        }
      } else if (requestCode == SAVE_CODE) {
        try (java.io.OutputStream stream = getContentResolver().openOutputStream(uri, "wt")) {
          if (stream == null) throw new java.io.IOException("Cannot write file");
          stream.write(codeEditor.getText().toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
          stream.flush();
        }
        Toast.makeText(this, "Source saved", Toast.LENGTH_SHORT).show();
      }
    } catch (Exception e) {
      Toast.makeText(this, "File operation failed: " + e.getMessage(), Toast.LENGTH_LONG).show();
    }
  }
  private boolean isAllowed(Uri uri) {
    if (allowedOrigin == null || uri == null || !("https".equalsIgnoreCase(uri.getScheme())) || uri.getHost() == null) return false;
    int port = uri.getPort();
    String origin = "https://" + uri.getHost().toLowerCase(java.util.Locale.ROOT) + (port == -1 || port == 443 ? "" : ":" + port);
    return origin.equals(allowedOrigin);
  }
  @Override public void onBackPressed() { if (browser != null && browser.canGoBack()) browser.goBack(); else super.onBackPressed(); }
  @Override protected void onDestroy() { if (browser != null) browser.destroy(); super.onDestroy(); }
}
