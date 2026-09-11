import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../core/offline_cache.dart';
import '../../models/weather_model.dart';
import '../../services/weather_repository.dart';
import '../widgets/weather_card.dart';
import '../widgets/alert_banner.dart';
import 'chat_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final WeatherRepository _repository = WeatherRepository();
  WeatherDataResponse? _weatherData;
  bool _isLoading = true;
  bool _lowBandwidth = false;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _loadInitialData();
  }

  Future<void> _loadInitialData() async {
    final lb = await OfflineCache.isLowBandwidthMode();
    setState(() {
      _lowBandwidth = lb;
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      // Default to Tokyo or user coordinates
      final data = await _repository.getWeather(
        latitude: 35.6762,
        longitude: 139.6503,
        locationName: 'Tokyo, Japan',
        lowBandwidth: _lowBandwidth,
      );
      setState(() {
        _weatherData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Could not load weather data: $e';
        _isLoading = false;
      });
    }
  }

  void _toggleLowBandwidth(bool value) async {
    await OfflineCache.setLowBandwidthMode(value);
    setState(() {
      _lowBandwidth = value;
    });
    _loadInitialData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('WeatherGPT Intelligence'),
        actions: [
          Row(
            children: [
              const Icon(Icons.network_cell, size: 16, color: AppTheme.accentCyan),
              const SizedBox(width: 4),
              const Text('Low Data', style: TextStyle(fontSize: 11)),
              Switch(
                value: _lowBandwidth,
                activeTrackColor: AppTheme.accentCyan,
                onChanged: _toggleLowBandwidth,
              ),
            ],
          )
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.accentCyan))
          : _errorMessage.isNotEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.cloud_off, size: 64, color: AppTheme.textMuted),
                        const SizedBox(height: 12),
                        Text(_errorMessage, textAlign: TextAlign.center),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadInitialData,
                          child: const Text('Retry'),
                        )
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadInitialData,
                  child: ListView(
                    children: [
                      if (_weatherData!.officialAlerts.isNotEmpty)
                        ..._weatherData!.officialAlerts.map((a) => AlertBanner(alert: a)),
                      WeatherCard(weather: _weatherData!),
                      
                      // AI Assistant Prompt Banner
                      Container(
                        margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                        padding: const EdgeInsets.all(16.0),
                        decoration: BoxDecoration(
                          color: AppTheme.cardDark,
                          borderRadius: BorderRadius.circular(16.0),
                          border: Border.all(color: AppTheme.accentCyan.withOpacity(0.3)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.psychology, size: 36, color: AppTheme.accentCyan),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: const [
                                  Text(
                                    'Ask WeatherGPT AI',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                      color: AppTheme.textLight,
                                    ),
                                  ),
                                  Text(
                                    'Verified weather facts, travel advice, & safety',
                                    style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                                  ),
                                ],
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.arrow_forward_ios, color: AppTheme.accentCyan),
                              onPressed: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => ChatScreen(
                                      locationName: _weatherData!.location.name,
                                      latitude: _weatherData!.location.latitude,
                                      longitude: _weatherData!.location.longitude,
                                    ),
                                  ),
                                );
                              },
                            )
                          ],
                        ),
                      ),
                      
                      // Forecast List Header
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
                        child: Text(
                          'Forecast',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textLight,
                          ),
                        ),
                      ),
                      
                      // Daily Forecast Cards
                      ..._weatherData!.dailyForecast.map((day) => Container(
                            margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
                            padding: const EdgeInsets.all(14.0),
                            decoration: BoxDecoration(
                              color: AppTheme.cardDark,
                              borderRadius: BorderRadius.circular(12.0),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  day.date,
                                  style: const TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w500,
                                    color: AppTheme.textLight,
                                  ),
                                ),
                                Text(
                                  day.conditionText,
                                  style: const TextStyle(fontSize: 13, color: AppTheme.textMuted),
                                ),
                                Text(
                                  '${day.tempMin.round()}° / ${day.tempMax.round()}°',
                                  style: const TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.bold,
                                    color: AppTheme.accentCyan,
                                  ),
                                ),
                              ],
                            ),
                          )),
                      const SizedBox(height: 30),
                    ],
                  ),
                ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppTheme.accentCyan,
        icon: const Icon(Icons.chat_bubble_outline, color: AppTheme.bgDark),
        label: const Text(
          'Ask WeatherGPT',
          style: TextStyle(color: AppTheme.bgDark, fontWeight: FontWeight.bold),
        ),
        onPressed: () {
          if (_weatherData != null) {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => ChatScreen(
                  locationName: _weatherData!.location.name,
                  latitude: _weatherData!.location.latitude,
                  longitude: _weatherData!.location.longitude,
                ),
              ),
            );
          }
        },
      ),
    );
  }
}
