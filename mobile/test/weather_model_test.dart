import 'package:flutter_test/flutter_test.dart';
import 'package:weathergpt_mobile/models/weather_model.dart';

void main() {
  group('Weather Model JSON Deserialization Tests', () {
    test('LocationInfo parsing from valid JSON', () {
      final json = {
        'name': 'Tokyo, Japan',
        'latitude': 35.6762,
        'longitude': 139.6503,
        'country': 'Japan',
      };
      final loc = LocationInfo.fromJson(json);
      expect(loc.name, 'Tokyo, Japan');
      expect(loc.latitude, 35.6762);
      expect(loc.longitude, 139.6503);
      expect(loc.country, 'Japan');
    });

    test('CurrentWeather parsing from JSON', () {
      final json = {
        'temperature': 22.5,
        'apparent_temperature': 23.0,
        'humidity': 55.0,
        'pressure': 1013.25,
        'wind_speed': 12.0,
        'condition_text': 'Partly Cloudy',
        'uv_index': 4.5,
      };
      final curr = CurrentWeather.fromJson(json);
      expect(curr.temperature, 22.5);
      expect(curr.apparentTemperature, 23.0);
      expect(curr.humidity, 55.0);
      expect(curr.conditionText, 'Partly Cloudy');
    });

    test('WeatherDataResponse parsing with alerts', () {
      final json = {
        'location': {'name': 'Denver', 'latitude': 39.7, 'longitude': -104.9},
        'current': {
          'temperature': 15.0,
          'apparent_temperature': 15.0,
          'humidity': 40.0,
          'pressure': 1010.0,
          'wind_speed': 25.0,
          'condition_text': 'Windy',
        },
        'daily_forecast': [
          {
            'date': '2026-09-10',
            'temp_min': 10.0,
            'temp_max': 20.0,
            'precipitation_probability': 15.0,
            'condition_text': 'Sunny',
          }
        ],
        'official_alerts': [
          {
            'id': 'a1',
            'event': 'High Wind Warning',
            'severity': 'HIGH',
            'headline': 'Wind gusts up to 60mph',
            'description': 'Secure loose items',
            'source': 'NOAA NWS',
            'issued_at': 'Today',
            'is_official_warning': true,
          }
        ],
        'data_source': 'Open-Meteo & NOAA NWS',
        'cached': false,
        'low_bandwidth_mode': false,
      };

      final response = WeatherDataResponse.fromJson(json);
      expect(response.location.name, 'Denver');
      expect(response.dailyForecast.length, 1);
      expect(response.officialAlerts.length, 1);
      expect(response.officialAlerts.first.event, 'High Wind Warning');
      expect(response.officialAlerts.first.isOfficialWarning, isTrue);
    });
  });
}
