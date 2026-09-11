import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/weather_model.dart';
import 'constants.dart';

class OfflineCache {
  static Future<void> saveWeather(WeatherDataResponse weather) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = jsonEncode(weather.toJson());
    await prefs.setString(AppConstants.keyOfflineWeatherData, jsonStr);
  }

  static Future<WeatherDataResponse?> getCachedWeather() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString(AppConstants.keyOfflineWeatherData);
    if (jsonStr != null && jsonStr.isNotEmpty) {
      try {
        final Map<String, dynamic> map = jsonDecode(jsonStr);
        final response = WeatherDataResponse.fromJson(map);
        return response;
      } catch (_) {
        return null;
      }
    }
    return null;
  }

  static Future<void> setLowBandwidthMode(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(AppConstants.keyLowBandwidthMode, enabled);
  }

  static Future<bool> isLowBandwidthMode() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(AppConstants.keyLowBandwidthMode) ?? false;
  }
}
