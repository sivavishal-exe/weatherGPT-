import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:speech_to_text/speech_recognition_error.dart';
import 'package:speech_to_text/speech_recognition_result.dart';

typedef VoiceResultCallback = void Function(String recognizedText, bool isFinal);
typedef VoiceErrorCallback = void Function(String errorMessage);
typedef VoiceStatusCallback = void Function(String status);

class VoiceService {
  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _isInitialized = false;
  bool _isListening = false;

  bool get isListening => _isListening;
  bool get isInitialized => _isInitialized;

  /// Requests hardware microphone permissions & initializes SpeechToText engine.
  Future<bool> initialize({
    VoiceErrorCallback? onError,
    VoiceStatusCallback? onStatus,
  }) async {
    if (_isInitialized) return true;

    try {
      // 1. Verify Microphone Permission
      final status = await Permission.microphone.request();
      if (!status.isGranted) {
        onError?.call("Microphone permission denied. Please grant access in system settings.");
        return false;
      }

      // 2. Initialize SpeechToText engine
      _isInitialized = await _speech.initialize(
        onError: (SpeechRecognitionError error) {
          _isListening = false;
          debugPrint("VoiceService Error: ${error.errorMsg} (permanent: ${error.permanent})");
          onError?.call(_formatErrorMessage(error.errorMsg));
        },
        onStatus: (String status) {
          debugPrint("VoiceService Status: $status");
          _isListening = status == "listening";
          onStatus?.call(status);
        },
      );

      if (!_isInitialized) {
        onError?.call("Speech recognition service is not available on this device.");
      }

      return _isInitialized;
    } catch (e) {
      debugPrint("VoiceService Exception during initialization: $e");
      onError?.call("Failed to initialize speech recognition: $e");
      return false;
    }
  }

  /// Triggers native hardware recording session.
  Future<void> startListening({
    required VoiceResultCallback onResult,
    VoiceErrorCallback? onError,
    VoiceStatusCallback? onStatus,
    String languageCode = 'en-US',
  }) async {
    if (_isListening) return;

    final ready = await initialize(onError: onError, onStatus: onStatus);
    if (!ready) return;

    try {
      _isListening = true;
      await _speech.listen(
        onResult: (SpeechRecognitionResult result) {
          onResult(result.recognizedWords, result.finalResult);
        },
        listenOptions: stt.SpeechListenOptions(
          localeId: languageCode,
          cancelOnError: true,
          partialResults: true,
          listenMode: stt.ListenMode.dictation,
        ),
      );
    } catch (e) {
      _isListening = false;
      onError?.call("Failed to start voice recording: $e");
    }
  }

  /// Safely stops active listening session.
  Future<void> stopListening() async {
    if (_isListening) {
      await _speech.stop();
      _isListening = false;
    }
  }

  /// Cancels listening and purges transient audio buffer.
  Future<void> cancelListening() async {
    if (_isListening) {
      await _speech.cancel();
      _isListening = false;
    }
  }

  /// Clean up resources on screen dispose
  void dispose() {
    stopListening();
  }

  String _formatErrorMessage(String errorMsg) {
    if (errorMsg.contains("error_no_match")) {
      return "No speech detected. Please try speaking clearly.";
    } else if (errorMsg.contains("error_network")) {
      return "Network connection issue during voice recognition.";
    } else if (errorMsg.contains("error_busy")) {
      return "Voice engine busy. Please retry in a moment.";
    }
    return "Voice Recognition Error: $errorMsg";
  }
}
