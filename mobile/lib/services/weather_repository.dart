import '../core/offline_cache.dart';
import '../models/weather_model.dart';
import 'api_service.dart';

class WeatherRepository {
  final ApiService apiService;

  WeatherRepository({ApiService? apiService})
      : apiService = apiService ?? ApiService();

  Future<WeatherDataResponse> getWeather({
    required double latitude,
    required double longitude,
    String? locationName,
    bool lowBandwidth = false,
  }) async {
    try {
      final freshWeather = await apiService.fetchWeather(
        latitude: latitude,
        longitude: longitude,
        locationName: locationName,
        lowBandwidth: lowBandwidth,
      );
      // Update offline cache upon successful fetch
      await OfflineCache.saveWeather(freshWeather);
      return freshWeather;
    } catch (e) {
      // Offline fallback
      final cached = await OfflineCache.getCachedWeather();
      if (cached != null) {
        return WeatherDataResponse(
          location: cached.location,
          current: cached.current,
          dailyForecast: cached.dailyForecast,
          officialAlerts: cached.officialAlerts,
          dataSource: '${cached.dataSource} (Offline Cache)',
          cached: true,
          lowBandwidthMode: lowBandwidth,
        );
      }
      rethrow;
    }
  }

  Future<List<SevereWeatherAlert>> getAlerts({
    required double latitude,
    required double longitude,
  }) async {
    try {
      return await apiService.fetchAlerts(
        latitude: latitude,
        longitude: longitude,
      );
    } catch (e) {
      final cached = await OfflineCache.getCachedWeather();
      return cached?.officialAlerts ?? [];
    }
  }
}
