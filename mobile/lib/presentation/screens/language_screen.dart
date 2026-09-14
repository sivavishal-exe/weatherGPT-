import 'package:flutter/material.dart';
import '../../core/theme.dart';

class LanguageScreen extends StatefulWidget {
  const LanguageScreen({Key? key}) : super(key: key);

  @override
  State<LanguageScreen> createState() => _LanguageScreenState();
}

class _LanguageScreenState extends State<LanguageScreen> {
  String _selectedLang = 'en';

  final List<Map<String, String>> _languages = [
    {'code': 'en', 'name': 'English (United States)', 'native': 'English'},
    {'code': 'hi', 'name': 'Hindi', 'native': 'हिन्दी'},
    {'code': 'ta', 'name': 'Tamil', 'native': 'தமிழ்'},
    {'code': 'ja', 'name': 'Japanese', 'native': '日本語'},
    {'code': 'es', 'name': 'Spanish', 'native': 'Español'},
    {'code': 'fr', 'name': 'French', 'native': 'Français'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Language Settings')),
      body: ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemCount: _languages.length,
        itemBuilder: (context, index) {
          final lang = _languages[index];
          final isSelected = lang['code'] == _selectedLang;
          return Container(
            margin: const EdgeInsets.only(bottom: 8.0),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(12.0),
              border: isSelected ? Border.all(color: AppTheme.accentCyan, width: 2) : null,
            ),
            child: ListTile(
              title: Text(lang['name']!, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text(lang['native']!, style: const TextStyle(color: AppTheme.textMuted)),
              trailing: isSelected ? const Icon(Icons.check_circle, color: AppTheme.accentCyan) : null,
              onTap: () {
                setState(() => _selectedLang = lang['code']!);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Language set to ${lang['name']}')),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
