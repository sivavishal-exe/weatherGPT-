import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class SecureStorage {
  static const String _secretKey = 'weathergpt_secure_local_key_2026';

  static String _transform(String input) {
    List<int> bytes = utf8.encode(input);
    List<int> keyBytes = utf8.encode(_secretKey);
    List<int> result = [];
    for (int i = 0; i < bytes.length; i++) {
      result.add(bytes[i] ^ keyBytes[i % keyBytes.length]);
    }
    return base64Encode(result);
  }

  static String _untransform(String input) {
    try {
      List<int> bytes = base64Decode(input);
      List<int> keyBytes = utf8.encode(_secretKey);
      List<int> result = [];
      for (int i = 0; i < bytes.length; i++) {
        result.add(bytes[i] ^ keyBytes[i % keyBytes.length]);
      }
      return utf8.decode(result);
    } catch (_) {
      return '';
    }
  }

  static Future<void> writeSecureString(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    final encrypted = _transform(value);
    await prefs.setString(key, encrypted);
  }

  static Future<String?> readSecureString(String key) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(key);
    if (raw != null && raw.isNotEmpty) {
      return _untransform(raw);
    }
    return null;
  }

  static Future<void> deleteSecure(String key) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(key);
  }
}
