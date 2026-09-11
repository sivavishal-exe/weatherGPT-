import 'dart:async';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LocalCachedRecord {
  final String id;
  final String category; // 'weather', 'forecast', 'alert', 'saved_location'
  final String key;
  final Map<String, dynamic> data;
  final DateTime cachedAt;
  final bool isStale;

  LocalCachedRecord({
    required this.id,
    required this.category,
    required this.key,
    required this.data,
    required this.cachedAt,
    this.isStale = false,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'category': category,
        'key': key,
        'data': data,
        'cachedAt': cachedAt.toIso8601String(),
        'isStale': isStale,
      };

  factory LocalCachedRecord.fromJson(Map<String, dynamic> json) => LocalCachedRecord(
        id: json['id'] as String,
        category: json['category'] as String,
        key: json['key'] as String,
        data: json['data'] as Map<String, dynamic>,
        cachedAt: DateTime.parse(json['cachedAt'] as String),
        isStale: json['isStale'] as bool? ?? false,
      );
}

class SQLiteDatabaseHelper {
  static const String _storageKeyPrefix = 'sqlite_db_table_';
  static const Duration _cacheTtl = Duration(minutes: 15);

  /// Saves cached record into offline local database
  static Future<void> insertOrUpdateRecord({
    required String table,
    required String key,
    required Map<String, dynamic> data,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final record = LocalCachedRecord(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      category: table,
      key: key,
      data: data,
      cachedAt: DateTime.now(),
      isStale: false,
    );
    await prefs.setString('$_storageKeyPrefix${table}_$key', jsonEncode(record.toJson()));
  }

  /// Retrieves record, automatically evaluating staleness timestamp
  static Future<LocalCachedRecord?> getRecord({
    required String table,
    required String key,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString('$_storageKeyPrefix${table}_$key');
    if (jsonStr == null) return null;

    try {
      final record = LocalCachedRecord.fromJson(jsonDecode(jsonStr));
      final age = DateTime.now().difference(record.cachedAt);
      final isStale = age > _cacheTtl;

      // Mark stale if expired
      return LocalCachedRecord(
        id: record.id,
        category: record.category,
        key: record.key,
        data: record.data,
        cachedAt: record.cachedAt,
        isStale: isStale,
      );
    } catch (_) {
      return null;
    }
  }

  /// Deletes record from table
  static Future<void> deleteRecord({
    required String table,
    required String key,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('$_storageKeyPrefix${table}_$key');
  }
}
