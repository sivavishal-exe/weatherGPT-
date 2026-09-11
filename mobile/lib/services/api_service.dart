import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import '../models/weather_model.dart';
import '../models/chat_model.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;
  final String errorType;

  ApiException({
    required this.statusCode,
    required this.message,
    this.errorType = 'ApiException',
  });

  @override
  String toString() => 'ApiException [$statusCode]: $message ($errorType)';
}

class ApiService {
  final String baseUrl;
  final http.Client client;

  ApiService({
    this.baseUrl = AppConstants.apiBaseUrl,
    http.Client? client,
  }) : client = client ?? http.Client();

  /// Centralized HTTP Execution Wrapper with Timeout, Retry, and Error Handling
  Future<http.Response> _executeWithRetry(
    Future<http.Response> Function() requestFn, {
    int maxRetries = 2,
    Duration timeout = const Duration(seconds: 10),
  }) async {
    int attempt = 0;
    while (attempt <= maxRetries) {
      attempt++;
      try {
        final response = await requestFn().timeout(timeout);
        
        if (response.statusCode >= 200 && response.statusCode < 300) {
          return response;
        }

        // Parse structured error payload if available
        String errorMessage = 'HTTP ${response.statusCode} Error';
        String errorType = 'HttpError';

        try {
          final jsonMap = jsonDecode(response.body);
          if (jsonMap is Map && jsonMap.containsKey('error')) {
            final err = jsonMap['error'];
            errorMessage = err['message'] ?? errorMessage;
            errorType = err['type'] ?? errorType;
          }
        } catch (_) {
          // Fall back to raw response body if not JSON
          if (response.body.isNotEmpty) {
            errorMessage = response.body;
          }
        }

        // Handle specific status codes
        switch (response.statusCode) {
          case 400:
            throw ApiException(statusCode: 400, message: errorMessage, errorType: 'BadRequest');
          case 401:
            throw ApiException(statusCode: 401, message: 'Unauthorized access. Please login.', errorType: 'Unauthorized');
          case 403:
            throw ApiException(statusCode: 403, message: 'Access forbidden.', errorType: 'Forbidden');
          case 429:
            throw ApiException(statusCode: 429, message: 'Rate limit exceeded. Please wait.', errorType: 'RateLimitExceeded');
          case 500:
          case 502:
          case 503:
          case 504:
            if (attempt <= maxRetries) {
              await Future.delayed(Duration(milliseconds: 300 * attempt));
              continue;
            }
            throw ApiException(statusCode: response.statusCode, message: 'Server unavailable: $errorMessage', errorType: 'ServerUnavailable');
          default:
            throw ApiException(statusCode: response.statusCode, message: errorMessage, errorType: errorType);
        }
      } on TimeoutException {
        if (attempt <= maxRetries) {
          await Future.delayed(Duration(milliseconds: 300 * attempt));
          continue;
        }
        throw ApiException(statusCode: 408, message: 'Connection timed out. Please check your network.', errorType: 'Timeout');
      } on SocketException {
        throw ApiException(statusCode: 0, message: 'No internet connection available.', errorType: 'NoInternet');
      } on FormatException {
        throw ApiException(statusCode: 422, message: 'Malformed JSON response from server.', errorType: 'MalformedResponse');
      } catch (e) {
        if (e is ApiException) rethrow;
        throw ApiException(statusCode: 500, message: 'Unexpected connection error: $e', errorType: 'NetworkError');
      }
    }
    throw ApiException(statusCode: 503, message: 'Service unavailable after retries', errorType: 'ServiceUnavailable');
  }

  /// GET /api/v1/weather (alias for sync_service)
  Future<WeatherDataResponse> getWeather({
    required double lat,
    required double lon,
    String? locationName,
  }) => fetchWeather(latitude: lat, longitude: lon, locationName: locationName);

  /// GET /api/v1/weather
  Future<WeatherDataResponse> fetchWeather({
    required double latitude,
    required double longitude,
    String? locationName,
    int days = 7,
    bool lowBandwidth = false,
  }) async {
    final queryParams = {
      'latitude': latitude.toString(),
      'longitude': longitude.toString(),
      'days': days.toString(),
      'low_bandwidth': lowBandwidth.toString(),
    };
    if (locationName != null && locationName.isNotEmpty) {
      queryParams['location_name'] = locationName;
    }

    final uri = Uri.parse('$baseUrl/weather').replace(queryParameters: queryParams);

    final response = await _executeWithRetry(() => client.get(
          uri,
          headers: {
            'Accept': 'application/json',
            'X-Low-Bandwidth': lowBandwidth ? 'true' : 'false',
          },
        ));

    try {
      final jsonMap = jsonDecode(response.body);
      return WeatherDataResponse.fromJson(jsonMap);
    } catch (_) {
      throw ApiException(statusCode: 422, message: 'Malformed weather JSON response.', errorType: 'MalformedJSON');
    }
  }

  /// GET /api/v1/forecast
  Future<List<DailyForecast>> fetchForecast({
    required double latitude,
    required double longitude,
    int days = 7,
    String? locationName,
  }) async {
    final queryParams = {
      'latitude': latitude.toString(),
      'longitude': longitude.toString(),
      'days': days.toString(),
    };
    if (locationName != null && locationName.isNotEmpty) {
      queryParams['location_name'] = locationName;
    }

    final uri = Uri.parse('$baseUrl/forecast').replace(queryParameters: queryParams);

    final response = await _executeWithRetry(() => client.get(
          uri,
          headers: {'Accept': 'application/json'},
        ));

    try {
      final List list = jsonDecode(response.body);
      return list.map((i) => DailyForecast.fromJson(i)).toList();
    } catch (_) {
      throw ApiException(statusCode: 422, message: 'Malformed forecast JSON array.', errorType: 'MalformedJSON');
    }
  }

  /// GET /api/v1/alerts
  Future<List<SevereWeatherAlert>> fetchAlerts({
    required double latitude,
    required double longitude,
  }) async {
    final queryParams = {
      'latitude': latitude.toString(),
      'longitude': longitude.toString(),
    };

    final uri = Uri.parse('$baseUrl/alerts').replace(queryParameters: queryParams);

    final response = await _executeWithRetry(() => client.get(
          uri,
          headers: {'Accept': 'application/json'},
        ));

    try {
      final List list = jsonDecode(response.body);
      return list.map((i) => SevereWeatherAlert.fromJson(i)).toList();
    } catch (_) {
      throw ApiException(statusCode: 422, message: 'Malformed alerts JSON array.', errorType: 'MalformedJSON');
    }
  }

  /// POST /api/v1/chat
  Future<ChatResponse> sendChatMessage({
    required String query,
    double? latitude,
    double? longitude,
    String? locationName,
    String language = 'en',
    bool lowBandwidth = false,
  }) async {
    final uri = Uri.parse('$baseUrl/chat');
    final bodyMap = {
      'query': query,
      'latitude': latitude,
      'longitude': longitude,
      'location_name': locationName,
      'language': language,
      'low_bandwidth': lowBandwidth,
    };

    final response = await _executeWithRetry(
      () => client.post(
        uri,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode(bodyMap),
      ),
      timeout: const Duration(seconds: 15),
    );

    try {
      final jsonMap = jsonDecode(response.body);
      return ChatResponse.fromJson(jsonMap);
    } catch (_) {
      throw ApiException(statusCode: 422, message: 'Malformed chat JSON response.', errorType: 'MalformedJSON');
    }
  }

  /// GET /api/v1/climate
  Future<Map<String, dynamic>> fetchClimateAnalytics({
    required String locationName,
    required double currentTemp,
    int month = 9,
  }) async {
    final queryParams = {
      'location_name': locationName,
      'current_temp': currentTemp.toString(),
      'month': month.toString(),
    };

    final uri = Uri.parse('$baseUrl/climate').replace(queryParameters: queryParams);

    final response = await _executeWithRetry(() => client.get(
          uri,
          headers: {'Accept': 'application/json'},
        ));

    try {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } catch (_) {
      throw ApiException(statusCode: 422, message: 'Malformed climate JSON response.', errorType: 'MalformedJSON');
    }
  }
}
