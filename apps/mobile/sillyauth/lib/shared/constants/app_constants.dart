/// App constants for SillyAuth application
class AppConstants {
  AppConstants._();

  // App information
  static const String appName = 'SillyAuth';
  static const String appVersion = '1.0.0';

  // TOTP defaults (RFC 6238 standard)
  static const int totpDigits = 6;
  static const int totpPeriod = 30; // seconds
  static const String totpAlgorithm = 'SHA1'; // SHA1, SHA256, SHA512

  // Storage keys for secure storage
  static const String storageKeyAccounts = 'totp_accounts';
  static const String storageKeySettings = 'app_settings';
  static const String storageKeyBiometricEnabled = 'biometric_enabled';
  static const String storageKeyLastUnlock = 'last_unlock_time';

  // UI constants
  static const double defaultPadding = 16.0;
  static const double smallPadding = 8.0;
  static const double largePadding = 24.0;
  static const double defaultBorderRadius = 12.0;
  static const double smallBorderRadius = 8.0;
  static const double largeBorderRadius = 16.0;

  // Animation durations
  static const Duration shortAnimation = Duration(milliseconds: 200);
  static const Duration mediumAnimation = Duration(milliseconds: 350);
  static const Duration longAnimation = Duration(milliseconds: 500);

  // TOTP display
  static const int codeRefreshBuffer = 5; // seconds before expiry to show warning

  // QR code scanning
  static const double qrScannerOverlayRadius = 20.0;
  static const double qrScannerBorderWidth = 3.0;

  // Account list
  static const int maxAccountNameLength = 50;
  static const int maxIssuerLength = 50;

  // Timeouts
  static const Duration networkTimeout = Duration(seconds: 30);
  static const Duration biometricTimeout = Duration(seconds: 30);
}
