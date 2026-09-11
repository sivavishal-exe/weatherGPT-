import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../models/chat_model.dart';

class ChatBubble extends StatelessWidget {
  final String text;
  final bool isUser;
  final List<GroundedFact>? groundedFacts;
  final List<String>? aiRecommendations;

  const ChatBubble({
    Key? key,
    required this.text,
    required this.isUser,
    this.groundedFacts,
    this.aiRecommendations,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6.0, horizontal: 12.0),
        padding: const EdgeInsets.all(14.0),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.82,
        ),
        decoration: BoxDecoration(
          color: isUser ? AppTheme.accentCyan.withOpacity(0.2) : AppTheme.cardDark,
          borderRadius: BorderRadius.circular(16.0),
          border: Border.all(
            color: isUser ? AppTheme.accentCyan : const Color(0xFF334155),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              text,
              style: TextStyle(
                fontSize: 14.5,
                height: 1.4,
                color: isUser ? AppTheme.textLight : const Color(0xFFE2E8F0),
              ),
            ),
            if (!isUser && groundedFacts != null && groundedFacts!.isNotEmpty) ...[
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.verified_outlined, size: 14, color: AppTheme.accentCyan),
                        SizedBox(width: 4),
                        Text(
                          'Verified Fact Grounding Source:',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.accentCyan,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      groundedFacts!.first.source,
                      style: const TextStyle(fontSize: 10.5, color: AppTheme.textMuted),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
