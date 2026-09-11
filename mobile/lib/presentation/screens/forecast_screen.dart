import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../models/weather_model.dart';
import '../../services/weather_repository.dart';
import '../widgets/empty_state.dart';

class ForecastScreen extends StatefulWidget {
  const ForecastScreen({Key? key}) : super(key: key);

  @override
  State<ForecastScreen> createState() => _ForecastScreenState();
}

class _ForecastScreenState extends State<ForecastScreen> {
  final WeatherRepository _repository = WeatherRepository();
  WeatherDataResponse? _weatherData;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadForecast();
  }

  Future<void> _loadForecast() async {
    setState(() => _isLoading = true);
    try {
      final data = await _repository.getWeather(latitude: 35.6762, longitude: 139.6503, locationName: 'Tokyo, Japan');
      setState(() {
        _weatherData = data;
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('7-Day Weather Forecast')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.accentCyan))
          : _weatherData == null || _weatherData!.dailyForecast.isEmpty
              ? EmptyStateWidget(
                  icon: Icons.calendar_today_outlined,
                  title: 'No Forecast Data Available',
                  description: 'Could not retrieve multi-day forecast information.',
                  onRetry: _loadForecast,
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16.0),
                  itemCount: _weatherData!.dailyForecast.length,
                  itemBuilder: (context, index) {
                    final day = _weatherData!.dailyForecast[index];
                    return Container(
                      margin: const EdgeInsets.only(bottom: 12.0),
                      padding: const EdgeInsets.all(16.0),
                      decoration: BoxDecoration(
                        color: Theme.of(context).cardColor,
                        borderRadius: BorderRadius.circular(14.0),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            flex: 3,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  day.date,
                                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  day.conditionText,
                                  style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor),
                                ),
                              ],
                            ),
                          ),
                          Row(
                            children: [
                              const Icon(Icons.water_drop, size: 14, color: AppTheme.accentCyan),
                              const SizedBox(width: 4),
                              Text('${day.precipitationProbability.round()}%', style: const TextStyle(fontSize: 12)),
                            ],
                          ),
                          const SizedBox(width: 16),
                          Text(
                            '${day.tempMin.round()}° / ${day.tempMax.round()}°C',
                            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.accentCyan),
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}
