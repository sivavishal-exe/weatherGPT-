import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../models/weather_model.dart';
import '../widgets/weather_card.dart';

class CurrentWeatherScreen extends StatelessWidget {
  final WeatherDataResponse weather;

  const CurrentWeatherScreen({Key? key, required this.weather}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final curr = weather.current;
    return Scaffold(
      appBar: AppBar(
        title: Text('${weather.location.name} • Detailed Weather'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          WeatherCard(weather: weather),
          const SizedBox(height: 16),
          const Text(
            'Observation Parameters',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            childAspectRatio: 1.4,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            children: [
              _buildDetailTile(context, Icons.thermostat, 'Apparent Temp', '${curr.apparentTemperature}°C'),
              _buildDetailTile(context, Icons.water_drop, 'Humidity', '${curr.humidity}%'),
              _buildDetailTile(context, Icons.air, 'Wind Speed', '${curr.windSpeed} km/h'),
              _buildDetailTile(context, Icons.compress, 'Pressure', '${curr.pressure} hPa'),
              _buildDetailTile(context, Icons.wb_sunny, 'UV Index', '${curr.uvIndex}'),
              _buildDetailTile(context, Icons.source, 'Data Source', weather.dataSource),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDetailTile(BuildContext context, IconData icon, String label, String value) {
    return Container(
      padding: const EdgeInsets.all(14.0),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(14.0),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Row(
            children: [
              Icon(icon, size: 20, color: AppTheme.accentCyan),
              const SizedBox(width: 6),
              Text(label, style: TextStyle(fontSize: 12, color: Theme.of(context).hintColor)),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
