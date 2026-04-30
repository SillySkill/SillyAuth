import 'package:flutter/material.dart';

import '../../../data/repositories/account_repository.dart';

/// Settings provider that manages app-wide settings.
///
/// This class provides theme mode management and notifies
/// listeners when settings change.
class SettingsProvider extends ChangeNotifier {
  final AccountRepository _repository;

  bool _isLoading = true;
  bool _appLockEnabled = false;
  bool _biometricEnabled = false;
  ThemeMode _themeMode = ThemeMode.system;
  Locale? _locale; // null means follow system locale

  SettingsProvider(this._repository);

  // Initialize settings
  Future<void> initialize() async {
    await _loadSettings();
  }

  // Getters
  bool get isLoading => _isLoading;
  bool get appLockEnabled => _appLockEnabled;
  bool get biometricEnabled => _biometricEnabled;
  ThemeMode get themeMode => _themeMode;
  Locale? get locale => _locale;

  /// Gets the theme mode as a string for storage.
  String get themeModeString {
    switch (_themeMode) {
      case ThemeMode.light:
        return 'light';
      case ThemeMode.dark:
        return 'dark';
      case ThemeMode.system:
        return 'system';
    }
  }

  /// Loads settings from the repository.
  Future<void> _loadSettings() async {
    final settings = await _repository.getSettings();

    _appLockEnabled = settings['appLockEnabled'] as bool? ?? false;
    _biometricEnabled = settings['biometricEnabled'] as bool? ?? false;

    final themeModeString = settings['themeMode'] as String? ?? 'system';
    _themeMode = _stringToThemeMode(themeModeString);

    // Load locale - null means follow system locale
    final localeString = settings['locale'] as String?;
    if (localeString != null && localeString.isNotEmpty && localeString != 'system') {
      _locale = Locale(localeString);
    } else {
      _locale = null; // Follow system locale
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Sets the app lock enabled state.
  Future<void> setAppLockEnabled(bool value) async {
    _appLockEnabled = value;
    // If app lock is disabled, also disable biometric
    if (!value) {
      _biometricEnabled = false;
    }
    await _saveSettings();
    notifyListeners();
  }

  /// Sets the biometric enabled state.
  Future<void> setBiometricEnabled(bool value) async {
    _biometricEnabled = value;
    await _saveSettings();
    notifyListeners();
  }

  /// Sets the theme mode.
  Future<void> setThemeMode(ThemeMode mode) async {
    _themeMode = mode;
    await _saveSettings();
    notifyListeners();
  }

  /// Sets the theme mode from a string.
  Future<void> setThemeModeFromString(String modeString) async {
    _themeMode = _stringToThemeMode(modeString);
    await _saveSettings();
    notifyListeners();
  }

  /// Saves current settings to the repository.
  Future<void> _saveSettings() async {
    final settings = await _repository.getSettings();

    settings['appLockEnabled'] = _appLockEnabled;
    settings['biometricEnabled'] = _biometricEnabled;
    settings['themeMode'] = themeModeString;
    settings['locale'] = _locale?.languageCode ?? '';

    await _repository.saveSettings(settings);
  }

  /// Sets the app locale.
  Future<void> setLocale(Locale? locale) async {
    _locale = locale;
    await _saveSettings();
    notifyListeners();
  }

  /// Converts a string to ThemeMode.
  ThemeMode _stringToThemeMode(String mode) {
    switch (mode) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      case 'system':
        return ThemeMode.system;
      default:
        return ThemeMode.system;
    }
  }
}
