import 'package:flutter/material.dart';
import '../../core/theme.dart';

class SavedLocationsScreen extends StatefulWidget {
  const SavedLocationsScreen({Key? key}) : super(key: key);

  @override
  State<SavedLocationsScreen> createState() => _SavedLocationsScreenState();
}

class _SavedLocationsScreenState extends State<SavedLocationsScreen> {
  final List<Map<String, dynamic>> _locations = [
    {'name': 'Tokyo, Japan', 'temp': '22°C', 'cond': 'Partly Cloudy', 'lat': 35.6762, 'lon': 139.6503},
    {'name': 'London, UK', 'temp': '18°C', 'cond': 'Light Rain', 'lat': 51.5074, 'lon': -0.1278},
    {'name': 'Denver, USA', 'temp': '28°C', 'cond': 'Clear Sky', 'lat': 39.7392, 'lon': -104.9903},
  ];

  final TextEditingController _searchController = TextEditingController();

  void _addLocation(String name) {
    if (name.trim().isEmpty) return;
    setState(() {
      _locations.add({'name': name, 'temp': '20°C', 'cond': 'Clear', 'lat': 40.0, 'lon': -75.0});
    });
    _searchController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Saved Locations')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search city name...',
                prefixIcon: const Icon(Icons.search, color: AppTheme.accentCyan),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.add, color: AppTheme.accentCyan),
                  onPressed: () => _addLocation(_searchController.text),
                ),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12.0)),
              ),
              onSubmitted: _addLocation,
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              itemCount: _locations.length,
              itemBuilder: (context, index) {
                final loc = _locations[index];
                return Container(
                  margin: const EdgeInsets.only(bottom: 12.0),
                  padding: const EdgeInsets.all(16.0),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(14.0),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(loc['name'], style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          Text(loc['cond'], style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor)),
                        ],
                      ),
                      Row(
                        children: [
                          Text(loc['temp'], style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.accentCyan)),
                          IconButton(
                            icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
                            onPressed: () {
                              setState(() {
                                _locations.removeAt(index);
                              });
                            },
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
