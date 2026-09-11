import 'package:flutter_test/flutter_test.dart';
import 'package:weathergpt_mobile/models/chat_model.dart';

void main() {
  group('Chat Model Deserialization Tests', () {
    test('ChatResponse parsing with grounded facts and recommendations', () {
      final json = {
        'query': 'Is it raining in Tokyo?',
        'answer': 'No rain is observed in Tokyo currently.',
        'grounded_facts': [
          {
            'fact_type': 'CURRENT_WEATHER',
            'fact_text': 'Temperature in Tokyo is 22°C with Partly Cloudy sky.',
            'source': 'Open-Meteo Meteorological Data'
          }
        ],
        'official_warnings': [],
        'ai_recommendations': ['AI Advisory: Carry light jacket.'],
        'language': 'en',
        'low_bandwidth_mode': false,
      };

      final chatRes = ChatResponse.fromJson(json);
      expect(chatRes.query, 'Is it raining in Tokyo?');
      expect(chatRes.groundedFacts.length, 1);
      expect(chatRes.groundedFacts.first.source, 'Open-Meteo Meteorological Data');
      expect(chatRes.aiRecommendations.length, 1);
      expect(chatRes.aiRecommendations.first, contains('AI Advisory:'));
    });
  });
}
