import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../services/voice_service.dart';
import 'chat_screen.dart';

class VoiceScreen extends StatefulWidget {
  const VoiceScreen({Key? key}) : super(key: key);

  @override
  State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen> {
  final VoiceService _voiceService = VoiceService();
  String _recognizedText = '';
  String _status = 'Tap microphone to start speaking';
  bool _isListening = false;

  @override
  void dispose() {
    _voiceService.dispose();
    super.dispose();
  }

  void _toggleListening() async {
    if (_isListening) {
      await _voiceService.stopListening();
      setState(() {
        _isListening = false;
        _status = 'Listening stopped';
      });
    } else {
      setState(() {
        _status = 'Initializing microphone...';
      });

      await _voiceService.startListening(
        onResult: (text, isFinal) {
          setState(() {
            _recognizedText = text;
            if (isFinal) {
              _isListening = false;
              _status = 'Recognized final text';
            }
          });
        },
        onError: (err) {
          setState(() {
            _isListening = false;
            _status = err;
          });
        },
        onStatus: (st) {
          setState(() {
            _isListening = st == 'listening';
            _status = 'Status: $st';
          });
        },
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Voice Assistant Studio')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _status,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: AppTheme.textMuted),
            ),
            const SizedBox(height: 32),
            GestureDetector(
              onTap: _toggleListening,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                padding: const EdgeInsets.all(32.0),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _isListening ? Colors.redAccent.withOpacity(0.3) : AppTheme.accentCyan.withOpacity(0.2),
                  border: Border.all(
                    color: _isListening ? Colors.redAccent : AppTheme.accentCyan,
                    width: 3,
                  ),
                ),
                child: Icon(
                  _isListening ? Icons.mic : Icons.mic_none,
                  size: 72,
                  color: _isListening ? Colors.redAccent : AppTheme.accentCyan,
                ),
              ),
            ),
            const SizedBox(height: 32),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16.0),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(14.0),
              ),
              child: Text(
                _recognizedText.isEmpty ? 'Recognized speech will appear here...' : _recognizedText,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 16, color: AppTheme.textLight),
              ),
            ),
            if (_recognizedText.isNotEmpty) ...[
              const SizedBox(height: 20),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.accentCyan,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                icon: const Icon(Icons.auto_awesome),
                label: const Text('Ask WeatherGPT AI', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => ChatScreen(initialQuery: _recognizedText),
                    ),
                  );
                },
              ),
            ],
          ],
        ),
      ),
    );
  }
}
