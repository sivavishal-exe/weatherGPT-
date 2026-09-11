import 'package:flutter/material.dart';
import '../../services/voice_service.dart';

class VoiceInputWidget extends StatefulWidget {
  final TextEditingController textController;
  final ValueChanged<String>? onTranscribedText;
  final VoidCallback? onSpeechCompleted;

  const VoiceInputWidget({
    Key? key,
    required this.textController,
    this.onTranscribedText,
    this.onSpeechCompleted,
  }) : super(key: key);

  @override
  State<VoiceInputWidget> createState() => _VoiceInputWidgetState();
}

class _VoiceInputWidgetState extends State<VoiceInputWidget>
    with SingleTickerProviderStateMixin {
  final VoiceService _voiceService = VoiceService();
  late AnimationController _animationController;
  late Animation<double> _pulseAnimation;

  bool _isListening = false;
  String _liveTranscript = '';
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.25).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    _voiceService.dispose();
    super.dispose();
  }

  Future<void> _toggleListening() async {
    if (_isListening) {
      await _voiceService.stopListening();
      _stopAnimation();
      setState(() {
        _isListening = false;
      });
      widget.onSpeechCompleted?.call();
    } else {
      setState(() {
        _errorMessage = null;
        _liveTranscript = '';
      });

      await _voiceService.startListening(
        onResult: (text, isFinal) {
          setState(() {
            _liveTranscript = text;
            widget.textController.text = text;
          });
          widget.onTranscribedText?.call(text);

          if (isFinal) {
            _stopAnimation();
            setState(() {
              _isListening = false;
            });
            widget.onSpeechCompleted?.call();
          }
        },
        onError: (errorMsg) {
          _stopAnimation();
          setState(() {
            _isListening = false;
            _errorMessage = errorMsg;
          });
        },
        onStatus: (status) {
          if (status == 'listening') {
            _startAnimation();
            setState(() {
              _isListening = true;
            });
          } else if (status == 'notListening' || status == 'done') {
            _stopAnimation();
            setState(() {
              _isListening = false;
            });
          }
        },
      );
    }
  }

  void _startAnimation() {
    _animationController.repeat(reverse: true);
  }

  void _stopAnimation() {
    _animationController.stop();
    _animationController.reset();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (_isListening)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            margin: const EdgeInsets.only(bottom: 8),
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.blue.withOpacity(0.3)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.record_voice_over, color: Colors.blue, size: 18),
                const SizedBox(width: 8),
                Flexible(
                  child: Text(
                    _liveTranscript.isNotEmpty
                        ? _liveTranscript
                        : "Listening... Speak your weather query",
                    style: const TextStyle(
                      color: Colors.blue,
                      fontWeight: FontWeight.w500,
                      fontSize: 14,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        if (_errorMessage != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text(
              _errorMessage!,
              style: const TextStyle(color: Colors.redAccent, fontSize: 12),
            ),
          ),
        ScaleTransition(
          scale: _pulseAnimation,
          child: IconButton(
            icon: Icon(
              _isListening ? Icons.mic : Icons.mic_none,
              color: _isListening ? Colors.redAccent : Colors.blueAccent,
            ),
            iconSize: 28,
            tooltip: _isListening ? "Stop Voice Recording" : "Tap to Speak",
            onPressed: _toggleListening,
          ),
        ),
      ],
    );
  }
}
