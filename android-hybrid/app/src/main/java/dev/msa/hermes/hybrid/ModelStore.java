package dev.msa.hermes.hybrid;

import android.content.Context;
import android.net.Uri;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.Locale;

/** User-authorized model import. This class does not perform inference. */
public final class ModelStore {
  private ModelStore() {}
  public static String importModel(Context context, Uri uri) throws Exception {
    File dir = new File(context.getFilesDir(), "models");
    if (!dir.exists() && !dir.mkdirs()) throw new java.io.IOException("Cannot create model directory");
    File pending = new File(dir, "incoming.partial");
    File active = new File(dir, "active.litertlm");
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    long size = 0;
    try {
      try (InputStream input = context.getContentResolver().openInputStream(uri);
           FileOutputStream output = new FileOutputStream(pending)) {
        if (input == null) throw new java.io.IOException("Cannot read selected file");
        byte[] buffer = new byte[65536];
        int n;
        while ((n = input.read(buffer)) != -1) {
          size += n;
          if (size > 4294967296L) throw new java.io.IOException("Model exceeds 4 GiB");
          output.write(buffer, 0, n);
          digest.update(buffer, 0, n);
        }
        output.getFD().sync();
      }
      if (size == 0) throw new java.io.IOException("Model is empty");
      if (!pending.renameTo(active)) throw new java.io.IOException("Cannot activate model");
      StringBuilder sha = new StringBuilder();
      for (byte b : digest.digest()) sha.append(String.format(Locale.ROOT, "%02x", b & 255));
      return "Imported " + size + " bytes; SHA-256 " + sha;
    } finally {
      if (pending.exists()) pending.delete();
    }
  }
}
