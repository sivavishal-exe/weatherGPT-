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
  String baseUrl;
  final http.Client client;

  ApiService({
    String? baseUrl,
    http.Client? client,
  })  : baseUrl = baseUrl ?? AppConstants.apiBaseUrl,
        client = client ?? http.Client();

  /// Centralized HTTP Execution Wrapper with Timeout, Retry, and Multi-URL Fallback
  Future<http.Response> _executeWithRetry(
    Future<http.Response> Function(String activeBaseUrl) requestFn, {
    int maxRetries = 1,
    Duration timeout = const Duration(seconds: 5),
  }) async {
    final List<String> fallbackUrls = [
      baseUrl,
      if (baseUrl != AppConstants.localFallbackApiUrl) AppConstants.localFallbackApiUrl,
      if (baseUrl != AppConstants.emulatorApiUrl) AppConstants.emulatorApiUrl,
    ];

    for (final targetUrl in fallbackUrls) {
      int attempt = 0;
      while (attempt <= maxRetries) {
        attempt++;
        try {
          baseUrl = targetUrl;
          final response = await requestFn(targetUrl).timeout(timeout);
          
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
            if (response.body.isNotEmpty) {
              errorMessage = response.body;
            }
          }

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
          break; // Try next fallback URL if available
        } on SocketException {
          break; // Host unreachable on this URL, try next fallback URL
        } on FormatException {
          throw ApiException(statusCode: 422, message: 'Malformed JSON response from server.', errorType: 'MalformedResponse');
        } catch (e) {
          if (e is ApiException) rethrow;
          break;
        }
      }
    }
    throw ApiException(
      statusCode: 0,
      message: 'Unable to reach backend server at $baseUrl or fallback hosts. Ensure backend is running.',
      errorType: 'NoInternet',
    );
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

    final response = await _executeWithRetry((activeUrl) {
      final uri = Uri.parse('$activeUrl/weather').replace(queryParameters: queryParams);
      return client.get(
        uri,
        headers: {
          'Accept': 'application/json',
          'X-Low-Bandwidth': lowBandwidth ? 'true' : 'false',
        },
      );
    });

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

    final response = await _executeWithRetry((activeUrl) {
      final uri = Uri.parse('$activeUrl/forecast').replace(queryParameters: queryParams);
      return client.get(
        uri,
        headers: {'Accept': 'application/json'},
      );
    });

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

    final response = await _executeWithRetry((activeUrl) {
      final uri = Uri.parse('$activeUrl/alerts').replace(queryParameters: queryParams);
      return client.get(
        uri,
        headers: {'Accept': 'application/json'},
      );
    });

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
    final bodyMap = {
      'query': query,
      'latitude': latitude,
      'longitude': longitude,
      'location_name': locationName,
      'language': language,
      'low_bandwidth': lowBandwidth,
    };

    final response = await _executeWithRetry(
      (activeUrl) {
        final uri = Uri.parse('$activeUrl/chat');
        return client.post(
          uri,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: jsonEncode(bodyMap),
        );
      },
      timeout: const Duration(seconds: 8),
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

    final response = await _executeWithRetry((activeUrl) {
      final uri = Uri.parse('$activeUrl/climate').replace(queryParameters: queryParams);
      return client.get(
        uri,
        headers: {'Accept': 'application/json'},
      );
    });

    try {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } catch (_) {
      throw ApiException(statusCode: 422, message: 'Malformed climate JSON response.', errorType: 'MalformedJSON');
    }
  }
}
