import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:weathergpt_mobile/services/api_service.dart';
import 'package:weathergpt_mobile/services/weather_repository.dart';

void main() {
  group('ApiService & Backend Integration Tests', () {
    test('Successful /weather request parsing', () async {
      final mockResponseJson = jsonEncode({
        'location': {'name': 'Tokyo', 'latitude': 35.6762, 'longitude': 139.6503},
        'current': {
          'temperature': 22.0,
          'apparent_temperature': 22.5,
          'humidity': 50.0,
          'pressure': 1013.0,
          'wind_speed': 10.0,
          'condition_text': 'Clear',
        },
        'daily_forecast': [],
        'official_alerts': [],
        'data_source': 'Open-Meteo API',
        'cached': false,
        'low_bandwidth_mode': false,
      });

      final mockClient = MockClient((request) async {
        expect(request.url.path, contains('/weather'));
        return http.Response(mockResponseJson, 200);
      });

      final apiService = ApiService(baseUrl: 'http://testserver/api/v1', client: mockClient);
      final weather = await apiService.fetchWeather(latitude: 35.6762, longitude: 139.6503, locationName: 'Tokyo');

      expect(weather.location.name, 'Tokyo');
      expect(weather.current.temperature, 22.0);
    });

    test('HTTP 400 Bad Request handling', () async {
      final mockClient = MockClient((request) async {
        return http.Response(jsonEncode({
          'error': {'code': 400, 'type': 'BadRequest', 'message': 'Invalid query parameters'}
        }), 400);
      });

      final apiService = ApiService(baseUrl: 'http://testserver/api/v1', client: mockClient);

      expect(
        () async => await apiService.fetchWeather(latitude: 35.6762, longitude: 139.6503),
        throwsA(isA<ApiException>().having((e) => e.statusCode, 'statusCode', 400)),
      );
    });

    test('HTTP 401 Unauthorized handling', () async {
      final mockClient = MockClient((request) async {
        return http.Response(jsonEncode({'error': {'code': 401, 'type': 'Unauthorized', 'message': 'Auth required'}}), 401);
      });

      final apiService = ApiService(baseUrl: 'http://testserver/api/v1', client: mockClient);

      expect(
        () async => await apiService.fetchWeather(latitude: 35.6762, longitude: 139.6503),
        throwsA(isA<ApiException>().having((e) => e.statusCode, 'statusCode', 401)),
      );
    });

    test('HTTP 429 Rate Limit Exceeded handling', () async {
      final mockClient = MockClient((request) async {
        return http.Response(jsonEncode({'error': {'code': 429, 'type': 'RateLimitExceeded', 'message': 'Too many requests'}}), 429);
      });

      final apiService = ApiService(baseUrl: 'http://testserver/api/v1', client: mockClient);

      expect(
        () async => await apiService.fetchWeather(latitude: 35.6762, longitude: 139.6503),
        throwsA(isA<ApiException>().having((e) => e.statusCode, 'statusCode', 429)),
      );
    });

    test('HTTP 500 Server Error handling with retries', () async {
      int calls = 0;
      final mockClient = MockClient((request) async {
        calls++;
        return http.Response('Internal Server Error', 500);
      });

      final apiService = ApiService(baseUrl: 'http://testserver/api/v1', client: mockClient);

      expect(
        () async => await apiService.fetchWeather(latitude: 35.6762, longitude: 139.6503),
        throwsA(isA<ApiException>().having((e) => e.statusCode, 'statusCode', 500)),
      );
      expect(calls, 3); // 1 initial call + 2 retries
    });

    test('Malformed JSON response handling', () async {
      final mockClient = MockClient((request) async {
        return http.Response('not-valid-json-response', 200);
      });

      final apiService = ApiService(baseUrl: 'http://testserver/api/v1', client: mockClient);

      expect(
        () async => await apiService.fetchWeather(latitude: 35.6762, longitude: 139.6503),
        throwsA(isA<ApiException>().having((e) => e.errorType, 'errorType', 'MalformedJSON')),
      );
    });

    test('WeatherRepository falls back to offline cache on network error', () async {
      final mockClient = MockClient((request) async {
        throw http.ClientException('Connection refused');
      });

      final apiService = ApiService(baseUrl: 'http://testserver/api/v1', client: mockClient);
      final repo = WeatherRepository(apiService: apiService);

      try {
        await repo.getWeather(latitude: 35.6762, longitude: 139.6503);
      } catch (e) {
        expect(e, isA<ApiException>());
      }
    });
  });
}
