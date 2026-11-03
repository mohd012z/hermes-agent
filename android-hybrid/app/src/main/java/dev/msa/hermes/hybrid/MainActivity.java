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
    root.addView(connect);
    browser = new WebView(this);
    browser.setVisibility(View.GONE);
    root.addView(browser, new LinearLayout.LayoutParams(-1, 0, 1));
    root.setFitsSystemWindows(true);
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
  private boolean isAllowed(Uri uri) {
    if (allowedOrigin == null || uri == null || !("https".equalsIgnoreCase(uri.getScheme())) || uri.getHost() == null) return false;
    int port = uri.getPort();
    String origin = "https://" + uri.getHost().toLowerCase(java.util.Locale.ROOT) + (port == -1 || port == 443 ? "" : ":" + port);
    return origin.equals(allowedOrigin);
  }
  @Override public void onBackPressed() { if (browser != null && browser.canGoBack()) browser.goBack(); else super.onBackPressed(); }
  @Override protected void onDestroy() { if (browser != null) browser.destroy(); super.onDestroy(); }
}
