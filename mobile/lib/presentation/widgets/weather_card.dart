import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../models/weather_model.dart';

class WeatherCard extends StatelessWidget {
  final WeatherDataResponse weather;

  const WeatherCard({Key? key, required this.weather}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final current = weather.current;
    final location = weather.location;

    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16.0),
          gradient: const LinearGradient(
            colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      location.name,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textLight,
                      ),
                    ),
                    Text(
                      weather.cached ? 'Offline Cached Weather' : weather.dataSource,
                      style: TextStyle(
                        fontSize: 12,
                        color: weather.cached ? AppTheme.advisoryAmber : AppTheme.accentCyan,
                      ),
                    ),
                  ],
                ),
                Icon(
                  _getWeatherIcon(current.conditionText),
                  size: 48,
                  color: AppTheme.accentCyan,
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              crossAxisAlignment: CrossAxisAlignment.baseline,
              textBaseline: TextBaseline.alphabetic,
              children: [
                Text(
                  '${current.temperature.round()}°',
                  style: const TextStyle(
                    fontSize: 56,
                    fontWeight: FontWeight.w300,
                    color: AppTheme.textLight,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  current.conditionText,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                    color: AppTheme.textMuted,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(color: Color(0xFF334155)),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildMetricItem(Icons.water_drop_outlined, '${current.humidity.round()}%', 'Humidity'),
                _buildMetricItem(Icons.air, '${current.windSpeed.round()} km/h', 'Wind'),
                _buildMetricItem(Icons.compress, '${current.pressure.round()} hPa', 'Pressure'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricItem(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, size: 20, color: AppTheme.textMuted),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: AppTheme.textLight,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: AppTheme.textMuted,
          ),
        ),
      ],
    );
  }

  IconData _getWeatherIcon(String condition) {
    final cond = condition.toLowerCase();
    if (cond.contains('rain') || cond.contains('drizzle')) return Icons.grain;
    if (cond.contains('snow')) return Icons.ac_unit;
    if (cond.contains('thunder')) return Icons.flash_on;
    if (cond.contains('cloud')) return Icons.cloud;
    return Icons.wb_sunny;
  }
}
