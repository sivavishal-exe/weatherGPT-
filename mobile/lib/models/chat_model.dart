import 'weather_model.dart';

class GroundedFact {
  final String factType;
  final String factText;
  final String source;

  GroundedFact({
    required this.factType,
    required this.factText,
    required this.source,
  });

  factory GroundedFact.fromJson(Map<String, dynamic> json) {
    return GroundedFact(
      factType: json['fact_type'] ?? 'WEATHER_FACT',
      factText: json['fact_text'] ?? '',
      source: json['source'] ?? 'Meteorological Office',
    );
  }

  Map<String, dynamic> toJson() => {
        'fact_type': factType,
        'fact_text': factText,
        'source': source,
      };
}

class ChatResponse {
  final String query;
  final String answer;
  final List<GroundedFact> groundedFacts;
  final List<SevereWeatherAlert> officialWarnings;
  final List<String> aiRecommendations;
  final String language;
  final bool lowBandwidthMode;

  ChatResponse({
    required this.query,
    required this.answer,
    required this.groundedFacts,
    required this.officialWarnings,
    required this.aiRecommendations,
    required this.language,
    required this.lowBandwidthMode,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      query: json['query'] ?? '',
      answer: json['answer'] ?? '',
      groundedFacts: (json['grounded_facts'] as List? ?? [])
          .map((i) => GroundedFact.fromJson(i))
          .toList(),
      officialWarnings: (json['official_warnings'] as List? ?? [])
          .map((i) => SevereWeatherAlert.fromJson(i))
          .toList(),
      aiRecommendations: List<String>.from(json['ai_recommendations'] ?? []),
      language: json['language'] ?? 'en',
      lowBandwidthMode: json['low_bandwidth_mode'] ?? false,
    );
  }
}
