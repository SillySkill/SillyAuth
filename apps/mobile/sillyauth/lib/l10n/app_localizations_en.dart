// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'SillyAuth';

  @override
  String get addAccount => 'Add Account';

  @override
  String get scanQrcode => 'Scan QR Code';

  @override
  String get manualInput => 'Manual Input';

  @override
  String get accountName => 'Account Name';

  @override
  String get secretKey => 'Secret Key';

  @override
  String get issuer => 'Issuer';

  @override
  String get delete => 'Delete';

  @override
  String get edit => 'Edit';

  @override
  String get cancel => 'Cancel';

  @override
  String get save => 'Save';

  @override
  String get copied => 'Copied';

  @override
  String get settings => 'Settings';

  @override
  String get appLock => 'App Lock';

  @override
  String get biometric => 'Biometric';

  @override
  String get theme => 'Theme';

  @override
  String get light => 'Light';

  @override
  String get dark => 'Dark';

  @override
  String get system => 'System';

  @override
  String get about => 'About';

  @override
  String get version => 'Version';

  @override
  String get noAccounts => 'No accounts';

  @override
  String get deleteConfirm => 'Delete this account?';

  @override
  String get invalidQrcode => 'Invalid QR Code';

  @override
  String get invalidSecret => 'Invalid Secret';

  @override
  String get search => 'Search';

  @override
  String get searchAccounts => 'Search accounts...';

  @override
  String get noSearchResults => 'No results found';

  @override
  String get noSearchResultsHint => 'Try a different search term';

  @override
  String get importAccount => 'Import Account';

  @override
  String get security => 'Security';

  @override
  String get appearance => 'Appearance';

  @override
  String get language => 'Language';

  @override
  String get info => 'Info';

  @override
  String get appLockSubtitle => 'Require authentication to open the app';

  @override
  String get biometricSubtitle => 'Use fingerprint or face to unlock';

  @override
  String get biometricUnavailable =>
      'Biometric authentication not available on this device';

  @override
  String get themeLight => 'Always use light theme';

  @override
  String get themeDark => 'Always use dark theme';

  @override
  String get themeSystem => 'Follow device settings';

  @override
  String get retry => 'Retry';

  @override
  String get deleteAccount => 'Delete Account';

  @override
  String confirmDelete(String accountName) {
    return 'Are you sure you want to delete $accountName?';
  }

  @override
  String get codeCopied => 'Code copied to clipboard';

  @override
  String accountAdded(String accountName) {
    return 'Account \"$accountName\" added successfully';
  }

  @override
  String get errorAddingAccount => 'Error adding account';

  @override
  String get secretRequired => 'Secret key is required';

  @override
  String get secretInvalid => 'Invalid Base32 format. Use A-Z and 2-7 only';

  @override
  String get secretTooShort => 'Secret key should be at least 16 characters';

  @override
  String get accountNameRequired => 'Account name is required';

  @override
  String get addingAccount => 'Adding Account...';

  @override
  String get enterAccountDetails => 'Enter Account Details';

  @override
  String get enterAccountInfo => 'Manually enter your account information';

  @override
  String get accountNameHint => 'e.g., user@example.com';

  @override
  String get accountNameHelper => 'The account identifier (usually your email)';

  @override
  String get issuerHint => 'e.g., Google, GitHub, Amazon';

  @override
  String get issuerHelper => 'The service or organization (optional)';

  @override
  String get secretHint => 'e.g., JBSWY3DPEHPK3PXP';

  @override
  String get secretHelper => 'Base32 encoded secret from your provider';

  @override
  String get showSecret => 'Show secret';

  @override
  String get hideSecret => 'Hide secret';

  @override
  String get base32Hint =>
      'The secret key must be in Base32 format (A-Z and 2-7). Spaces are automatically removed.';

  @override
  String get scanQrcodeInstructions => 'Point the camera at a TOTP QR code';

  @override
  String get onlyTotpSupported => 'Only TOTP QR codes are supported';

  @override
  String get invalidQrcodeFormat => 'Invalid QR code';

  @override
  String get cameraPermissionRequired => 'Camera Permission Required';

  @override
  String get cameraPermissionDesc =>
      'To scan QR codes, please grant camera permission.';

  @override
  String get grantPermission => 'Grant Permission';

  @override
  String get openSettings => 'Open Settings';

  @override
  String get cameraError => 'Camera Error';

  @override
  String get toggleFlashlight => 'Toggle Flashlight';

  @override
  String get switchCamera => 'Switch Camera';

  @override
  String get refreshCode => 'Refresh code';

  @override
  String get noAccountsYet => 'No accounts yet';

  @override
  String get tapPlusToAdd => 'Tap the + button to add your first account';

  @override
  String get editAccount => 'Edit Account';

  @override
  String accountUpdated(String accountName) {
    return 'Account \"$accountName\" updated successfully';
  }

  @override
  String get errorUpdatingAccount => 'Error updating account';

  @override
  String get savingAccount => 'Saving Account...';

  @override
  String get editAccountComingSoon => 'Edit account coming soon';

  @override
  String get biometricFailed => 'Biometric authentication failed';

  @override
  String get english => 'English';

  @override
  String get chinese => 'Chinese';

  @override
  String get crossPlatformAuthenticator =>
      'Cross-platform authenticator for two-factor authentication';

  @override
  String get copyright => '2024 SillyAuth. All rights reserved.';

  @override
  String get importFromFile => 'Import from File';

  @override
  String get importAccounts => 'Import Accounts';

  @override
  String get importDescription =>
      'Import accounts from a Google Authenticator export file';

  @override
  String get selectFile => 'Select File';

  @override
  String importSuccess(int count) {
    return '$count account(s) imported successfully';
  }

  @override
  String importPartial(int count, int invalidCount) {
    return '$count account(s) imported, $invalidCount invalid entry(ies) skipped';
  }

  @override
  String get importFailed => 'Failed to import accounts';

  @override
  String get noAccountsImported => 'No valid accounts found in file';

  @override
  String duplicatesSkipped(int count) {
    return '$count duplicate(s) skipped';
  }

  @override
  String invalidEntriesSkipped(int count) {
    return '$count invalid entry(ies) skipped';
  }

  @override
  String get importingAccounts => 'Importing accounts...';
}
