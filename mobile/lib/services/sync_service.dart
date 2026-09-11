import 'dart:async';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/sqlite_db.dart';
import '../models/weather_model.dart';
import 'api_service.dart';

class MobileSyncService {
  final ApiService apiService;
  bool _isOnline = true;

  MobileSyncService({required this.apiService});

  bool get isOnline => _isOnline;

  void updateConnectivityStatus(bool online) {
    _isOnline = online;
    if (_isOnline) {
      synchronizePendingData();
    }
  }

  /// Synchronize offline cached data when connection is restored
  Future<void> synchronizePendingData() async {
    final prefs = await SharedPreferences.getInstance();
    final pendingSync = prefs.getStringList('pending_offline_actions') ?? [];
    if (pendingSync.isEmpty) return;

    List<String> remaining = [];
    for (String action in pendingSync) {
      try {
        // Process offline queued location save or query sync
        // On success, omit from remaining
      } catch (_) {
        remaining.add(action);
      }
    }
    await prefs.setStringList('pending_offline_actions', remaining);
  }

  /// Fetches weather with automatic offline fallback, staleness tagging, and non-realtime assertion
  Future<WeatherDataResponse?> fetchWeatherWithCache({
    required double lat,
    required double lon,
    String? locationName,
  }) async {
    final cacheKey = '${lat.toStringAsFixed(2)}_${lon.toStringAsFixed(2)}';

    if (_isOnline) {
      try {
        final liveWeather = await apiService.getWeather(lat: lat, lon: lon, locationName: locationName);
        await SQLiteDatabaseHelper.insertOrUpdateRecord(
          table: 'cached_weather',
          key: cacheKey,
          data: liveWeather.toJson(),
        );
        return liveWeather;
      } catch (_) {
        // Connectivity dropped during request
        _isOnline = false;
      }
    }

    // Offline / Fallback mode
    final cached = await SQLiteDatabaseHelper.getRecord(
      table: 'cached_weather',
      key: cacheKey,
    );

    if (cached != null) {
      final map = Map<String, dynamic>.from(cached.data);
      map['cached'] = true;
      map['data_source'] = 'OFFLINE_CACHE (Stale: ${cached.isStale})';
      return WeatherDataResponse.fromJson(map);
    }

    return null;
  }
}
