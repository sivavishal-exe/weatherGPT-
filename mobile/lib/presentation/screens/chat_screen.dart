import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../models/chat_model.dart';
import '../../services/api_service.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/voice_input_widget.dart';

class ChatMessageItem {
  final String text;
  final bool isUser;
  final List<GroundedFact>? groundedFacts;
  final List<String>? aiRecommendations;

  ChatMessageItem({
    required this.text,
    required this.isUser,
    this.groundedFacts,
    this.aiRecommendations,
  });
}

class ChatScreen extends StatefulWidget {
  final String locationName;
  final double latitude;
  final double longitude;

  const ChatScreen({
    Key? key,
    required this.locationName,
    required this.latitude,
    required this.longitude,
  }) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ApiService _apiService = ApiService();
  final TextEditingController _textController = TextEditingController();
  final List<ChatMessageItem> _messages = [];
  bool _isSending = false;

  @override
  void initState() {
    super.initState();
    // Welcome message
    _messages.add(ChatMessageItem(
      text: 'Hello! I am WeatherGPT. Ask me anything about current weather, forecasts, or safety advisories for ${widget.locationName}. All facts are verified directly from meteorological services.',
      isUser: false,
    ));
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    setState(() {
      _messages.add(ChatMessageItem(text: text, isUser: true));
      _isSending = true;
    });
    _textController.clear();

    try {
      final response = await _apiService.sendChatMessage(
        query: text,
        latitude: widget.latitude,
        longitude: widget.longitude,
        locationName: widget.locationName,
      );

      setState(() {
        _messages.add(ChatMessageItem(
          text: response.answer,
          isUser: false,
          groundedFacts: response.groundedFacts,
          aiRecommendations: response.aiRecommendations,
        ));
        _isSending = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessageItem(
          text: 'Error connecting to WeatherGPT service: $e',
          isUser: false,
        ));
        _isSending = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('WeatherGPT • ${widget.locationName}'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 10),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return ChatBubble(
                  text: msg.text,
                  isUser: msg.isUser,
                  groundedFacts: msg.groundedFacts,
                  aiRecommendations: msg.aiRecommendations,
                );
              },
            ),
          ),
          if (_isSending)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.accentCyan),
                  ),
                  SizedBox(width: 8),
                  Text('Fetching verified facts...', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                ],
              ),
            ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            color: AppTheme.cardDark,
            child: SafeArea(
              child: Row(
                children: [
                  VoiceInputWidget(
                    textController: _textController,
                    onSpeechCompleted: () {
                      if (_textController.text.trim().isNotEmpty) {
                        // Text populates input controller for user review before sending
                      }
                    },
                  ),
                  Expanded(
                    child: TextField(
                      controller: _textController,
                      style: const TextStyle(color: AppTheme.textLight),
                      decoration: const InputDecoration(
                        hintText: 'Ask WeatherGPT (or tap mic)...',
                        hintStyle: TextStyle(color: AppTheme.textMuted),
                        border: InputBorder.none,
                      ),
                      onSubmitted: _sendMessage,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.send, color: AppTheme.accentCyan),
                    onPressed: () => _sendMessage(_textController.text),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
