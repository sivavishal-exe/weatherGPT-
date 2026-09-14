import 'package:flutter/material.dart';
import '../../core/theme.dart';
import '../../core/security.dart';
import 'auth_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String? _userEmail;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    final email = await SecureStorage.readSecureString('user_email');
    setState(() {
      _userEmail = email ?? 'Guest User';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('User Profile')),
      body: ListView(
        padding: const EdgeInsets.all(20.0),
        children: [
          const CircleAvatar(
            radius: 40,
            backgroundColor: AppTheme.accentCyan,
            child: Icon(Icons.person, size: 50, color: AppTheme.bgDark),
          ),
          const SizedBox(height: 12),
          Text(
            _userEmail ?? 'Guest User',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          const Text(
            'WeatherGPT Community Member',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 24),
          ListTile(
            leading: const Icon(Icons.security, color: AppTheme.accentCyan),
            title: const Text('Authentication Status'),
            subtitle: Text(_userEmail != null && _userEmail != 'Guest User' ? 'Authenticated (Active Session)' : 'Not Logged In'),
            trailing: ElevatedButton(
              onPressed: () {
                Navigator.push(context, MaterialPageRoute(builder: (context) => const AuthScreen())).then((_) => _loadProfile());
              },
              child: Text(_userEmail != null && _userEmail != 'Guest User' ? 'Switch' : 'Login'),
            ),
          ),
          const Divider(height: 32),
          const Text('Account Preferences', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.accentCyan)),
          const SizedBox(height: 8),
          const ListTile(
            leading: Icon(Icons.star_outline),
            title: Text('Subscription Tier'),
            subtitle: Text('Free Meteorological Tier'),
          ),
          const ListTile(
            leading: Icon(Icons.notifications_active_outlined),
            title: Text('Default Alert Region'),
            subtitle: Text('Tokyo, Japan'),
          ),
        ],
      ),
    );
  }
}
