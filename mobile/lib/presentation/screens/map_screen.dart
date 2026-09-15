import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../services/location_service.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({Key? key}) : super(key: key);

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> with SingleTickerProviderStateMixin {
  late AnimationController _sweepController;
  String _selectedLayer = 'precipitation'; // precipitation, temperature, wind, satellite
  int _rangeKm = 100;
  bool _isPlaying = true;
  UserLocationResult _currentLoc = UserLocationResult(
    latitude: 9.98,
    longitude: 77.49,
    locationName: 'Local Radar Station',
  );

  @override
  void initState() {
    super.initState();
    _sweepController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();
    _loadLocation();
  }

  Future<void> _loadLocation() async {
    try {
      final loc = await LocationService.getCurrentUserLocation();
      if (mounted) {
        setState(() => _currentLoc = loc);
      }
    } catch (_) {}
  }

  @override
  void dispose() {
    _sweepController.dispose();
    super.dispose();
  }

  void _togglePlay() {
    setState(() {
      _isPlaying = !_isPlaying;
      if (_isPlaying) {
        _sweepController.repeat();
      } else {
        _sweepController.stop();
      }
    });
  }

  void _zoomIn() {
    if (_rangeKm > 50) setState(() => _rangeKm -= 50);
  }

  void _zoomOut() {
    if (_rangeKm < 200) setState(() => _rangeKm += 50);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Weather Radar & Satellite Map'),
        actions: [
          IconButton(
            icon: Icon(_isPlaying ? Icons.pause_circle_outline : Icons.play_circle_outline),
            tooltip: _isPlaying ? 'Pause Radar Sweep' : 'Resume Radar Sweep',
            onPressed: _togglePlay,
          ),
          IconButton(
            icon: const Icon(Icons.my_location),
            tooltip: 'Center on My GPS',
            onPressed: _loadLocation,
          ),
        ],
      ),
      body: Stack(
        children: [
          // Background Radar Scope
          Container(
            color: const Color(0xFF030712),
            child: AnimatedBuilder(
              animation: _sweepController,
              builder: (context, child) {
                return CustomPaint(
                  size: Size.infinite,
                  painter: _RadarScopePainter(
                    angle: _sweepController.value * 2 * math.pi,
                    layer: _selectedLayer,
                    rangeKm: _rangeKm,
                  ),
                );
              },
            ),
          ),

          // Top Telemetry Header
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: AppTheme.cardDark.withOpacity(0.88),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppTheme.accentCyan.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: _isPlaying ? Colors.greenAccent : Colors.amberAccent,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: (_isPlaying ? Colors.greenAccent : Colors.amberAccent).withOpacity(0.6),
                          blurRadius: 6,
                          spreadRadius: 2,
                        )
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${_currentLoc.locationName} • ${_currentLoc.latitude.toStringAsFixed(2)}°N, ${_currentLoc.longitude.toStringAsFixed(2)}°E',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.white),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Doppler Weather Radar (DWR) • Range: $_rangeKm km',
                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppTheme.accentCyan.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      _selectedLayer.toUpperCase(),
                      style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.accentCyanLight),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Zoom Controls
          Positioned(
            right: 16,
            top: 90,
            child: Column(
              children: [
                _RadarControlButton(icon: Icons.add, onPressed: _zoomIn),
                const SizedBox(height: 8),
                _RadarControlButton(icon: Icons.remove, onPressed: _zoomOut),
              ],
            ),
          ),

          // dBZ / Scale Legend
          Positioned(
            left: 16,
            bottom: 84,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(
                color: AppTheme.cardDark.withOpacity(0.85),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.white12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _getLegendTitle(),
                    style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white70),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      _legendColor(Colors.greenAccent, 'Light'),
                      const SizedBox(width: 8),
                      _legendColor(Colors.amber, 'Mod'),
                      const SizedBox(width: 8),
                      _legendColor(Colors.deepOrange, 'Heavy'),
                      const SizedBox(width: 8),
                      _legendColor(Colors.purpleAccent, 'Severe'),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // Bottom Layer Selector Bar
          Positioned(
            bottom: 16,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              decoration: BoxDecoration(
                color: AppTheme.cardDark.withOpacity(0.92),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.accentCyan.withOpacity(0.2)),
                boxShadow: const [
                  BoxShadow(color: Colors.black45, blurRadius: 10, offset: Offset(0, 4)),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _layerButton(
                    id: 'precipitation',
                    icon: Icons.grain,
                    label: 'Rainfall',
                  ),
                  _layerButton(
                    id: 'temperature',
                    icon: Icons.thermostat,
                    label: 'Temp',
                  ),
                  _layerButton(
                    id: 'wind',
                    icon: Icons.air,
                    label: 'Wind',
                  ),
                  _layerButton(
                    id: 'satellite',
                    icon: Icons.cloud_outlined,
                    label: 'Clouds',
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getLegendTitle() {
    switch (_selectedLayer) {
      case 'precipitation':
        return 'Precipitation Intensity (dBZ)';
      case 'temperature':
        return 'Thermal Index (°C)';
      case 'wind':
        return 'Wind Velocity (km/h)';
      case 'satellite':
        return 'Infrared Cloud Depth (%)';
      default:
        return 'Intensity Scale';
    }
  }

  Widget _legendColor(Color color, String label) {
    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 9, color: Colors.white70)),
      ],
    );
  }

  Widget _layerButton({required String id, required IconData icon, required String label}) {
    final isSelected = _selectedLayer == id;
    return GestureDetector(
      onTap: () => setState(() => _selectedLayer = id),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.accentCyan.withOpacity(0.25) : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
          border: isSelected ? Border.all(color: AppTheme.accentCyan, width: 1.5) : null,
        ),
        child: Row(
          children: [
            Icon(icon, size: 16, color: isSelected ? AppTheme.accentCyanLight : AppTheme.textMuted),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected ? Colors.white : AppTheme.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RadarControlButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onPressed;

  const _RadarControlButton({required this.icon, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.cardDark.withOpacity(0.85),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white12),
      ),
      child: IconButton(
        icon: Icon(icon, color: Colors.white),
        iconSize: 20,
        constraints: const BoxConstraints(minWidth: 40, minHeight: 40),
        padding: EdgeInsets.zero,
        onPressed: onPressed,
      ),
    );
  }
}

class _RadarScopePainter extends CustomPainter {
  final double angle;
  final String layer;
  final int rangeKm;

  _RadarScopePainter({required this.angle, required this.layer, required this.rangeKm});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final maxRadius = math.min(size.width, size.height) * 0.42;

    // Range rings
    final ringPaint = Paint()
      ..color = const Color(0xFF1E293B).withOpacity(0.8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    final ringHighlight = Paint()
      ..color = AppTheme.accentCyan.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;

    for (int i = 1; i <= 4; i++) {
      final r = maxRadius * (i / 4.0);
      canvas.drawCircle(center, r, i == 4 ? ringHighlight : ringPaint);
    }

    // Crosshairs
    final crosshairPaint = Paint()
      ..color = const Color(0xFF1E293B).withOpacity(0.9)
      ..strokeWidth = 1.0;

    canvas.drawLine(Offset(center.dx - maxRadius, center.dy), Offset(center.dx + maxRadius, center.dy), crosshairPaint);
    canvas.drawLine(Offset(center.dx, center.dy - maxRadius), Offset(center.dx, center.dy + maxRadius), crosshairPaint);

    // Weather Echo Simulation based on layer
    _drawWeatherEchoes(canvas, center, maxRadius);

    // Sweep Beam & Fade Tail
    final sweepPaint = Paint()
      ..shader = SweepGradient(
        center: FractionalOffset(center.dx / size.width, center.dy / size.height),
        startAngle: 0.0,
        endAngle: math.pi * 2,
        colors: [
          AppTheme.accentCyan.withOpacity(0.0),
          AppTheme.accentCyan.withOpacity(0.0),
          AppTheme.accentCyan.withOpacity(0.05),
          AppTheme.accentCyanLight.withOpacity(0.35),
        ],
        stops: const [0.0, 0.7, 0.85, 1.0],
        transform: GradientRotation(angle),
      ).createShader(Rect.fromCircle(center: center, radius: maxRadius));

    canvas.drawCircle(center, maxRadius, sweepPaint);

    // Leading scan line
    final linePaint = Paint()
      ..color = AppTheme.accentCyanLight
      ..strokeWidth = 2.0;

    final beamEnd = Offset(
      center.dx + maxRadius * math.cos(angle),
      center.dy + maxRadius * math.sin(angle),
    );
    canvas.drawLine(center, beamEnd, linePaint);

    // Center pulse dot
    final centerDot = Paint()..color = AppTheme.accentCyan;
    canvas.drawCircle(center, 4, centerDot);

    // Cardinal direction labels
    _drawLabels(canvas, center, maxRadius);
  }

  void _drawWeatherEchoes(Canvas canvas, Offset center, double maxRadius) {
    final echoPaint = Paint()..style = PaintingStyle.fill;

    // Simulated storm/rain clusters
    if (layer == 'precipitation') {
      // Cluster 1: Northeast Moderate rain
      echoPaint.color = Colors.greenAccent.withOpacity(0.5);
      canvas.drawOval(
        Rect.fromCenter(center: Offset(center.dx + maxRadius * 0.45, center.dy - maxRadius * 0.35), width: 70, height: 45),
        echoPaint,
      );
      echoPaint.color = Colors.amber.withOpacity(0.6);
      canvas.drawOval(
        Rect.fromCenter(center: Offset(center.dx + maxRadius * 0.48, center.dy - maxRadius * 0.33), width: 35, height: 22),
        echoPaint,
      );
      echoPaint.color = Colors.deepOrange.withOpacity(0.7);
      canvas.drawCircle(Offset(center.dx + maxRadius * 0.50, center.dy - maxRadius * 0.32), 10, echoPaint);

      // Cluster 2: Southwest light drizzle
      echoPaint.color = Colors.greenAccent.withOpacity(0.35);
      canvas.drawOval(
        Rect.fromCenter(center: Offset(center.dx - maxRadius * 0.35, center.dy + maxRadius * 0.4), width: 85, height: 60),
        echoPaint,
      );
    } else if (layer == 'temperature') {
      // Temperature thermal contours
      echoPaint.color = Colors.orangeAccent.withOpacity(0.3);
      canvas.drawCircle(Offset(center.dx + maxRadius * 0.2, center.dy + maxRadius * 0.1), maxRadius * 0.5, echoPaint);
      echoPaint.color = Colors.deepOrange.withOpacity(0.35);
      canvas.drawCircle(Offset(center.dx + maxRadius * 0.2, center.dy + maxRadius * 0.1), maxRadius * 0.25, echoPaint);
    } else if (layer == 'wind') {
      // Wind streamline arrows
      final windPaint = Paint()
        ..color = AppTheme.accentCyanLight.withOpacity(0.7)
        ..strokeWidth = 1.5;
      for (double dx = -0.5; dx <= 0.5; dx += 0.35) {
        for (double dy = -0.5; dy <= 0.5; dy += 0.35) {
          final pt = Offset(center.dx + maxRadius * dx, center.dy + maxRadius * dy);
          canvas.drawLine(pt, Offset(pt.dx + 20, pt.dy - 10), windPaint);
        }
      }
    } else {
      // Satellite clouds
      echoPaint.color = Colors.white.withOpacity(0.25);
      canvas.drawOval(
        Rect.fromCenter(center: Offset(center.dx - maxRadius * 0.2, center.dy - maxRadius * 0.3), width: 140, height: 80),
        echoPaint,
      );
      canvas.drawOval(
        Rect.fromCenter(center: Offset(center.dx + maxRadius * 0.3, center.dy + maxRadius * 0.2), width: 120, height: 70),
        echoPaint,
      );
    }
  }

  void _drawLabels(Canvas canvas, Offset center, double maxRadius) {
    const textStyle = TextStyle(color: AppTheme.textMuted, fontSize: 11, fontWeight: FontWeight.bold);
    final textPainter = TextPainter(textDirection: TextDirection.ltr);

    final labels = [
      {'text': 'N', 'offset': Offset(center.dx - 4, center.dy - maxRadius - 18)},
      {'text': 'S', 'offset': Offset(center.dx - 4, center.dy + maxRadius + 4)},
      {'text': 'E', 'offset': Offset(center.dx + maxRadius + 6, center.dy - 6)},
      {'text': 'W', 'offset': Offset(center.dx - maxRadius - 20, center.dy - 6)},
    ];

    for (var l in labels) {
      textPainter.text = TextSpan(text: l['text'] as String, style: textStyle);
      textPainter.layout();
      textPainter.paint(canvas, l['offset'] as Offset);
    }
  }

  @override
  bool shouldRepaint(covariant _RadarScopePainter oldDelegate) =>
      oldDelegate.angle != angle || oldDelegate.layer != layer || oldDelegate.rangeKm != rangeKm;
}
