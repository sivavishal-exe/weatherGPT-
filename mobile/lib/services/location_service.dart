import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';

class UserLocationResult {
  final double latitude;
  final double longitude;
  final String locationName;
  final bool isGpsLocation;
  final String? statusMessage;

  UserLocationResult({
    required this.latitude,
    required this.longitude,
    required this.locationName,
    this.isGpsLocation = false,
    this.statusMessage,
  });
}

class LocationService {
  static UserLocationResult? _cachedLocation;
  static DateTime? _cacheTimestamp;
  static Future<UserLocationResult>? _inFlightRequest;

  /// Default fallback location if GPS is denied, disabled, or times out
  static final UserLocationResult defaultFallback = UserLocationResult(
    latitude: 28.6139,
    longitude: 77.2090,
    locationName: 'Delhi, India (Fallback)',
    isGpsLocation: false,
    statusMessage: 'Using default location (GPS unavailable or denied)',
  );

  /// Requests permissions & fetches current GPS coordinates safely without crashing.
  static Future<UserLocationResult> getCurrentUserLocation({
    Duration timeout = const Duration(seconds: 5),
    bool forceRefresh = false,
  }) async {
    if (!forceRefresh &&
        _cachedLocation != null &&
        _cacheTimestamp != null &&
        DateTime.now().difference(_cacheTimestamp!) < const Duration(minutes: 5)) {
      return _cachedLocation!;
    }

    if (_inFlightRequest != null) {
      return await _inFlightRequest!;
    }

    _inFlightRequest = _fetchLocationInternal(timeout);
    try {
      final res = await _inFlightRequest!;
      if (res.isGpsLocation) {
        _cachedLocation = res;
        _cacheTimestamp = DateTime.now();
      }
      return res;
    } finally {
      _inFlightRequest = null;
    }
  }

  static Future<UserLocationResult> _fetchLocationInternal(Duration timeout) async {
    try {
      // 1. Check if location services are enabled on device
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        debugPrint('LocationService: Location services are disabled on device.');
        return UserLocationResult(
          latitude: defaultFallback.latitude,
          longitude: defaultFallback.longitude,
          locationName: 'Delhi, India (GPS Disabled)',
          isGpsLocation: false,
          statusMessage: 'Device GPS is turned off. Please enable Location in system settings.',
        );
      }

      // 2. Check & Request permission
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          debugPrint('LocationService: Location permissions are denied by user.');
          return UserLocationResult(
            latitude: defaultFallback.latitude,
            longitude: defaultFallback.longitude,
            locationName: 'Delhi, India (Permission Denied)',
            isGpsLocation: false,
            statusMessage: 'Location permission denied. Showing fallback weather.',
          );
        }
      }

      if (permission == LocationPermission.deniedForever) {
        debugPrint('LocationService: Location permissions are permanently denied.');
        return UserLocationResult(
          latitude: defaultFallback.latitude,
          longitude: defaultFallback.longitude,
          locationName: 'Delhi, India (Permission Denied)',
          isGpsLocation: false,
          statusMessage: 'Location permission permanently denied. Enable in app settings.',
        );
      }

      // 3. Acquire position with explicit timeout safety
      final Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.medium,
        timeLimit: timeout,
      );

      final String locTitle = 'Current GPS (${position.latitude.toStringAsFixed(2)}, ${position.longitude.toStringAsFixed(2)})';
      debugPrint('LocationService: Acquired GPS location: ${position.latitude}, ${position.longitude}');

      return UserLocationResult(
        latitude: position.latitude,
        longitude: position.longitude,
        locationName: locTitle,
        isGpsLocation: true,
        statusMessage: 'Using live GPS position',
      );
    } on TimeoutException {
      debugPrint('LocationService: Timed out waiting for GPS coordinates.');
      return UserLocationResult(
        latitude: defaultFallback.latitude,
        longitude: defaultFallback.longitude,
        locationName: 'Delhi, India (GPS Timeout)',
        isGpsLocation: false,
        statusMessage: 'Location request timed out. Showing fallback weather.',
      );
    } catch (e) {
      debugPrint('LocationService Error: $e');
      return UserLocationResult(
        latitude: defaultFallback.latitude,
        longitude: defaultFallback.longitude,
        locationName: 'Delhi, India (Location Error)',
        isGpsLocation: false,
        statusMessage: 'Error acquiring location: $e',
      );
    }
  }
}
