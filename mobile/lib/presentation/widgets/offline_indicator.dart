import 'package:flutter/material.dart';

class OfflineIndicatorBanner extends StatelessWidget {
  final bool isOffline;
  final String message;

  const OfflineIndicatorBanner({
    Key? key,
    required this.isOffline,
    this.message = 'Offline Mode • Showing cached weather data',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (!isOffline) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      color: Colors.amber.shade900,
      padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.wifi_off, size: 14, color: Colors.white),
          const SizedBox(width: 6),
          Text(
            message,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}
