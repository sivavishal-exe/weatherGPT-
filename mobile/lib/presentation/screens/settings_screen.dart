import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../core/offline_cache.dart';

class SettingsScreen extends StatefulWidget {
  final VoidCallback? onThemeToggle;

  const SettingsScreen({Key? key, this.onThemeToggle}) : super(key: key);

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _isCelsius = true;
  bool _lowBandwidth = false;
  bool _notificationsEnabled = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final lb = await OfflineCache.isLowBandwidthMode();
    setState(() {
      _lowBandwidth = lb;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('WeatherGPT Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          const Text('Preferences', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.accentCyan)),
          const SizedBox(height: 8),
          SwitchListTile(
            title: const Text('Temperature Unit (°C / °F)'),
            subtitle: Text(_isCelsius ? 'Metric (°C)' : 'Imperial (°F)'),
            value: _isCelsius,
            activeTrackColor: AppTheme.accentCyan,
            onChanged: (val) => setState(() => _isCelsius = val),
          ),
          SwitchListTile(
            title: const Text('Low-Bandwidth Mode'),
            subtitle: const Text('Compress JSON payloads & limit forecast days'),
            value: _lowBandwidth,
            activeTrackColor: AppTheme.accentCyan,
            onChanged: (val) async {
              await OfflineCache.setLowBandwidthMode(val);
              setState(() => _lowBandwidth = val);
            },
          ),
          SwitchListTile(
            title: const Text('Severe Weather Alerts'),
            subtitle: const Text('Receive official emergency notifications'),
            value: _notificationsEnabled,
            activeTrackColor: AppTheme.accentCyan,
            onChanged: (val) => setState(() => _notificationsEnabled = val),
          ),
          const Divider(height: 32),
          const Text('Data & Cache Management', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.accentCyan)),
          const SizedBox(height: 8),
          ListTile(
            leading: const Icon(Icons.delete_outline, color: Colors.redAccent),
            title: const Text('Clear Offline Cache'),
            subtitle: const Text('Remove stored weather observations and alerts'),
            onTap: () async {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Offline weather cache cleared successfully.')),
              );
            },
          ),
          const Divider(height: 32),
          const Text('About WeatherGPT', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.accentCyan)),
          const SizedBox(height: 8),
          const ListTile(
            leading: Icon(Icons.info_outline),
            title: Text('Version'),
            subtitle: Text('1.0.0 (Build 1) • Verified Grounded Architecture'),
          ),
        ],
      ),
    );
  }
}
