class AppConstants {
  static const String appName = 'WeatherGPT';
  static const String apiBaseUrl = 'http://10.0.2.2:8000/api/v1'; // Android emulator localhost alias
  static const String localFallbackApiUrl = 'http://localhost:8000/api/v1';

  static const String keyOfflineWeatherData = 'offline_weather_data';
  static const String keyOfflineAlerts = 'offline_alerts';
  static const String keyLowBandwidthMode = 'low_bandwidth_mode';
}
