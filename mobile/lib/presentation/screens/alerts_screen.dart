import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../models/weather_model.dart';
import '../../services/weather_repository.dart';
import '../../services/location_service.dart';
import '../widgets/alert_banner.dart';
import '../widgets/empty_state.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({Key? key}) : super(key: key);

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> {
  final WeatherRepository _repository = WeatherRepository();
  List<SevereWeatherAlert> _alerts = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAlerts();
  }

  Future<void> _loadAlerts() async {
    setState(() => _isLoading = true);
    try {
      final loc = await LocationService.getCurrentUserLocation();
      final alerts = await _repository.getAlerts(latitude: loc.latitude, longitude: loc.longitude);
      if (alerts.isNotEmpty) {
        setState(() {
          _alerts = alerts;
          _isLoading = false;
        });
      } else {
        final data = await _repository.getWeather(latitude: loc.latitude, longitude: loc.longitude);
        setState(() {
          _alerts = data.officialAlerts;
          _isLoading = false;
        });
      }
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Official Severe Weather Warnings')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.warningRed))
          : _alerts.isEmpty
              ? EmptyStateWidget(
                  icon: Icons.shield_outlined,
                  title: 'No Active Severe Weather Warnings',
                  description: 'All official meteorological warnings for your region are normal.',
                  onRetry: _loadAlerts,
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12.0),
                  itemCount: _alerts.length,
                  itemBuilder: (context, index) {
                    return AlertBanner(alert: _alerts[index]);
                  },
                ),
    );
  }
}
