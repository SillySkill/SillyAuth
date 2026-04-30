import 'package:flutter/material.dart';
import 'package:local_auth/local_auth.dart';
import 'package:provider/provider.dart';

import '../../../data/repositories/account_repository.dart';
import '../../../shared/constants/app_constants.dart';
import '../../../l10n/app_localizations.dart';
import 'screens/theme_settings_screen.dart';
import 'screens/about_screen.dart';
import 'settings_provider.dart';

/// Settings screen for the SillyAuth app.
///
/// Provides options for app lock, biometric authentication, theme selection,
/// and accessing the about page.
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _isLoading = true;
  bool _appLockEnabled = false;
  bool _biometricEnabled = false;
  bool _biometricAvailable = false;
  String _themeMode = 'system';
  String _language = 'en';

  final LocalAuthentication _localAuth = LocalAuthentication();

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final repository = context.read<AccountRepository>();
    final settings = await repository.getSettings();

    // Check if biometric is available
    bool canCheckBiometrics = false;
    try {
      canCheckBiometrics = await _localAuth.canCheckBiometrics;
    } catch (e) {
      canCheckBiometrics = false;
    }

    setState(() {
      _appLockEnabled = settings['appLockEnabled'] as bool? ?? false;
      _biometricEnabled = settings['biometricEnabled'] as bool? ?? false;
      _themeMode = settings['themeMode'] as String? ?? 'system';
      _language = settings['locale'] as String? ?? 'system';
      _biometricAvailable = canCheckBiometrics;
      _isLoading = false;
    });
  }

  Future<void> _saveSettings() async {
    final repository = context.read<AccountRepository>();
    final settings = await repository.getSettings();

    settings['appLockEnabled'] = _appLockEnabled;
    settings['biometricEnabled'] = _biometricEnabled;
    settings['themeMode'] = _themeMode;
    settings['locale'] = _language;

    await repository.saveSettings(settings);

    // Update the locale in settings provider
    if (mounted) {
      final settingsProvider = context.read<SettingsProvider>();
      // If "system", set locale to null to follow system
      if (_language == 'system') {
        await settingsProvider.setLocale(null);
      } else {
        await settingsProvider.setLocale(Locale(_language));
      }
    }
  }

  Future<void> _toggleLanguage(String language) async {
    setState(() {
      _language = language;
    });
    await _saveSettings();
  }

  Future<void> _toggleAppLock(bool value) async {
    setState(() {
      _appLockEnabled = value;
      // If app lock is disabled, also disable biometric
      if (!value) {
        _biometricEnabled = false;
      }
    });
    await _saveSettings();
  }

  Future<void> _toggleBiometric(bool value) async {
    final l10n = AppLocalizations.of(context)!;
    if (value && _biometricAvailable) {
      // Verify biometric before enabling
      try {
        final authenticated = await _localAuth.authenticate(
          localizedReason: 'Verify your identity to enable biometric authentication',
          options: const AuthenticationOptions(
            stickyAuth: true,
            biometricOnly: true,
          ),
        );

        if (authenticated) {
          setState(() {
            _biometricEnabled = true;
          });
          await _saveSettings();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.biometricFailed),
            ),
          );
        }
      }
    } else {
      setState(() {
        _biometricEnabled = false;
      });
      await _saveSettings();
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.settings),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              children: [
                _buildSectionHeader(l10n.security),
                _buildAppLockTile(),
                if (_appLockEnabled) _buildBiometricTile(),
                const Divider(),
                _buildSectionHeader(l10n.appearance),
                _buildThemeTile(),
                _buildLanguageTile(),
                const Divider(),
                _buildSectionHeader(l10n.info),
                _buildAboutTile(),
              ],
            ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        AppConstants.defaultPadding,
        AppConstants.defaultPadding,
        AppConstants.defaultPadding,
        AppConstants.smallPadding,
      ),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: Theme.of(context).colorScheme.primary,
        ),
      ),
    );
  }

  Widget _buildAppLockTile() {
    final l10n = AppLocalizations.of(context)!;
    return SwitchListTile(
      title: Text(l10n.appLock),
      subtitle: Text(l10n.appLockSubtitle),
      secondary: Icon(
        Icons.lock_outline,
        color: Theme.of(context).colorScheme.primary,
      ),
      value: _appLockEnabled,
      onChanged: _toggleAppLock,
    );
  }

  Widget _buildBiometricTile() {
    final l10n = AppLocalizations.of(context)!;
    String subtitle;
    if (!_biometricAvailable) {
      subtitle = l10n.biometricUnavailable;
    } else {
      subtitle = l10n.biometricSubtitle;
    }

    return SwitchListTile(
      title: Text(l10n.biometric),
      subtitle: Text(subtitle),
      secondary: Icon(
        Icons.fingerprint,
        color: Theme.of(context).colorScheme.primary,
      ),
      value: _biometricEnabled,
      onChanged: _biometricAvailable ? _toggleBiometric : null,
    );
  }

  Widget _buildThemeTile() {
    final l10n = AppLocalizations.of(context)!;
    String themeText;
    switch (_themeMode) {
      case 'light':
        themeText = l10n.light;
        break;
      case 'dark':
        themeText = l10n.dark;
        break;
      case 'system':
      default:
        themeText = l10n.system;
        break;
    }

    return ListTile(
      leading: Icon(
        Icons.palette_outlined,
        color: Theme.of(context).colorScheme.primary,
      ),
      title: Text(l10n.theme),
      subtitle: Text(themeText),
      trailing: const Icon(Icons.chevron_right),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ThemeSettingsScreen(
              currentTheme: _themeMode,
              onThemeChanged: (String theme) async {
                setState(() {
                  _themeMode = theme;
                });
                await _saveSettings();
              },
            ),
          ),
        );
      },
    );
  }

  Widget _buildLanguageTile() {
    final l10n = AppLocalizations.of(context)!;
    String languageText;
    switch (_language) {
      case 'zh':
        languageText = l10n.chinese;
        break;
      case 'en':
        languageText = l10n.english;
        break;
      case 'system':
      default:
        languageText = l10n.system;
        break;
    }

    return ListTile(
      leading: Icon(
        Icons.language,
        color: Theme.of(context).colorScheme.primary,
      ),
      title: Text(l10n.language),
      subtitle: Text(languageText),
      trailing: const Icon(Icons.chevron_right),
      onTap: () {
        _showLanguageDialog();
      },
    );
  }

  void _showLanguageDialog() {
    final l10n = AppLocalizations.of(context)!;
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(l10n.language),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: Text(l10n.system),
              leading: Icon(
                _language == 'system' ? Icons.radio_button_checked : Icons.radio_button_off,
                color: _language == 'system' ? Theme.of(context).colorScheme.primary : null,
              ),
              onTap: () {
                _toggleLanguage('system');
                Navigator.pop(dialogContext);
              },
            ),
            ListTile(
              title: Text(l10n.english),
              leading: Icon(
                _language == 'en' ? Icons.radio_button_checked : Icons.radio_button_off,
                color: _language == 'en' ? Theme.of(context).colorScheme.primary : null,
              ),
              onTap: () {
                _toggleLanguage('en');
                Navigator.pop(dialogContext);
              },
            ),
            ListTile(
              title: Text(l10n.chinese),
              leading: Icon(
                _language == 'zh' ? Icons.radio_button_checked : Icons.radio_button_off,
                color: _language == 'zh' ? Theme.of(context).colorScheme.primary : null,
              ),
              onTap: () {
                _toggleLanguage('zh');
                Navigator.pop(dialogContext);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAboutTile() {
    final l10n = AppLocalizations.of(context)!;
    return ListTile(
      leading: Icon(
        Icons.info_outline,
        color: Theme.of(context).colorScheme.primary,
      ),
      title: Text(l10n.about),
      subtitle: Text('${l10n.version} ${AppConstants.appVersion}'),
      trailing: const Icon(Icons.chevron_right),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const AboutScreen(),
          ),
        );
      },
    );
  }
}
