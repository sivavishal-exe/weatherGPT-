import 'package:flutter/material.dart';
import '../../core/theme.dart';

class MapScreen extends StatelessWidget {
  const MapScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Weather Radar & Satellite Map')),
      body: Stack(
        children: [
          Container(
            color: const Color(0xFF0F172A),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  Icon(Icons.map_outlined, size: 80, color: AppTheme.accentCyan),
                  SizedBox(height: 16),
                  Text(
                    'Interactive Precipitation Radar Layer',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Real-time cloud cover & temperature contours',
                    style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            bottom: 24,
            left: 24,
            right: 24,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.cardDark.withOpacity(0.9),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: const [
                  _MapLayerChip(icon: Icons.grain, label: 'Rainfall'),
                  _MapLayerChip(icon: Icons.thermostat, label: 'Temp'),
                  _MapLayerChip(icon: Icons.air, label: 'Wind'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MapLayerChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _MapLayerChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppTheme.accentCyan),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white)),
      ],
    );
  }
}
