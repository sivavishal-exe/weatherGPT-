class AppConstants {
  static const String appName = 'WeatherGPT';
  static const String apiBaseUrl = 'http://127.0.0.1:8000/api/v1'; // ADB reverse port forwarded address over USB
  static const String emulatorApiUrl = 'http://10.0.2.2:8000/api/v1'; // Android emulator localhost alias
  static const String localFallbackApiUrl = 'http://10.50.77.208:8000/api/v1'; // Current Wi-Fi host IP (10.50.77.208)

  static const String keyOfflineWeatherData = 'offline_weather_data';
  static const String keyOfflineAlerts = 'offline_alerts';
  static const String keyLowBandwidthMode = 'low_bandwidth_mode';
}
