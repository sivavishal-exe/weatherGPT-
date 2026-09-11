class LocationInfo {
  final String name;
  final double latitude;
  final double longitude;
  final String? country;

  LocationInfo({
    required this.name,
    required this.latitude,
    required this.longitude,
    this.country,
  });

  factory LocationInfo.fromJson(Map<String, dynamic> json) {
    return LocationInfo(
      name: json['name'] ?? 'Unknown Location',
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      country: json['country'],
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'latitude': latitude,
        'longitude': longitude,
        'country': country,
      };
}

class CurrentWeather {
  final double temperature;
  final double apparentTemperature;
  final double humidity;
  final double pressure;
  final double windSpeed;
  final String conditionText;
  final double uvIndex;

  CurrentWeather({
    required this.temperature,
    required this.apparentTemperature,
    required this.humidity,
    required this.pressure,
    required this.windSpeed,
    required this.conditionText,
    required this.uvIndex,
  });

  factory CurrentWeather.fromJson(Map<String, dynamic> json) {
    return CurrentWeather(
      temperature: (json['temperature'] as num).toDouble(),
      apparentTemperature: (json['apparent_temperature'] as num).toDouble(),
      humidity: (json['humidity'] as num).toDouble(),
      pressure: (json['pressure'] as num).toDouble(),
      windSpeed: (json['wind_speed'] as num).toDouble(),
      conditionText: json['condition_text'] ?? 'Clear',
      uvIndex: ((json['uv_index'] ?? 0.0) as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'temperature': temperature,
        'apparent_temperature': apparentTemperature,
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': windSpeed,
        'condition_text': conditionText,
        'uv_index': uvIndex,
      };
}

class DailyForecast {
  final String date;
  final double tempMin;
  final double tempMax;
  final double precipitationProbability;
  final String conditionText;

  DailyForecast({
    required this.date,
    required this.tempMin,
    required this.tempMax,
    required this.precipitationProbability,
    required this.conditionText,
  });

  factory DailyForecast.fromJson(Map<String, dynamic> json) {
    return DailyForecast(
      date: json['date'] ?? '',
      tempMin: (json['temp_min'] as num).toDouble(),
      tempMax: (json['temp_max'] as num).toDouble(),
      precipitationProbability: (json['precipitation_probability'] as num).toDouble(),
      conditionText: json['condition_text'] ?? 'Clear',
    );
  }

  Map<String, dynamic> toJson() => {
        'date': date,
        'temp_min': tempMin,
        'temp_max': tempMax,
        'precipitation_probability': precipitationProbability,
        'condition_text': conditionText,
      };
}

class SevereWeatherAlert {
  final String id;
  final String event;
  final String severity;
  final String headline;
  final String description;
  final String? instruction;
  final String source;
  final String issuedAt;
  final bool isOfficialWarning;

  SevereWeatherAlert({
    required this.id,
    required this.event,
    required this.severity,
    required this.headline,
    required this.description,
    this.instruction,
    required this.source,
    required this.issuedAt,
    this.isOfficialWarning = true,
  });

  factory SevereWeatherAlert.fromJson(Map<String, dynamic> json) {
    return SevereWeatherAlert(
      id: json['id'] ?? '',
      event: json['event'] ?? 'Alert',
      severity: json['severity'] ?? 'MODERATE',
      headline: json['headline'] ?? '',
      description: json['description'] ?? '',
      instruction: json['instruction'],
      source: json['source'] ?? 'Meteorological Office',
      issuedAt: json['issued_at'] ?? 'Recently',
      isOfficialWarning: json['is_official_warning'] ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'event': event,
        'severity': severity,
        'headline': headline,
        'description': description,
        'instruction': instruction,
        'source': source,
        'issued_at': issuedAt,
        'is_official_warning': isOfficialWarning,
      };
}

class WeatherDataResponse {
  final LocationInfo location;
  final CurrentWeather current;
  final List<DailyForecast> dailyForecast;
  final List<SevereWeatherAlert> officialAlerts;
  final String dataSource;
  final bool cached;
  final bool lowBandwidthMode;

  WeatherDataResponse({
    required this.location,
    required this.current,
    required this.dailyForecast,
    required this.officialAlerts,
    required this.dataSource,
    required this.cached,
    required this.lowBandwidthMode,
  });

  factory WeatherDataResponse.fromJson(Map<String, dynamic> json) {
    return WeatherDataResponse(
      location: LocationInfo.fromJson(json['location'] ?? {}),
      current: CurrentWeather.fromJson(json['current'] ?? {}),
      dailyForecast: (json['daily_forecast'] as List? ?? [])
          .map((i) => DailyForecast.fromJson(i))
          .toList(),
      officialAlerts: (json['official_alerts'] as List? ?? [])
          .map((i) => SevereWeatherAlert.fromJson(i))
          .toList(),
      dataSource: json['data_source'] ?? 'Verified Meteorological Data',
      cached: json['cached'] ?? false,
      lowBandwidthMode: json['low_bandwidth_mode'] ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'location': location.toJson(),
        'current': current.toJson(),
        'daily_forecast': dailyForecast.map((e) => e.toJson()).toList(),
        'official_alerts': officialAlerts.map((e) => e.toJson()).toList(),
        'data_source': dataSource,
        'cached': cached,
        'low_bandwidth_mode': lowBandwidthMode,
      };
}
