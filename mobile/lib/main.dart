import 'package:flutter/material.dart';
import 'core/theme.dart';
import 'presentation/screens/splash_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const WeatherGPTApp());
}

class WeatherGPTApp extends StatefulWidget {
  const WeatherGPTApp({Key? key}) : super(key: key);

  @override
  State<WeatherGPTApp> createState() => _WeatherGPTAppState();
}

class _WeatherGPTAppState extends State<WeatherGPTApp> {
  ThemeMode _themeMode = ThemeMode.dark;

  void toggleTheme() {
    setState(() {
      _themeMode = _themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WeatherGPT Intelligence',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: _themeMode,
      home: const SplashScreen(),
    );
  }
}
