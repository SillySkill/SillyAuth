import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('zh'),
  ];

  /// No description provided for @appName.
  ///
  /// In en, this message translates to:
  /// **'SillyAuth'**
  String get appName;

  /// No description provided for @addAccount.
  ///
  /// In en, this message translates to:
  /// **'Add Account'**
  String get addAccount;

  /// No description provided for @scanQrcode.
  ///
  /// In en, this message translates to:
  /// **'Scan QR Code'**
  String get scanQrcode;

  /// No description provided for @manualInput.
  ///
  /// In en, this message translates to:
  /// **'Manual Input'**
  String get manualInput;

  /// No description provided for @accountName.
  ///
  /// In en, this message translates to:
  /// **'Account Name'**
  String get accountName;

  /// No description provided for @secretKey.
  ///
  /// In en, this message translates to:
  /// **'Secret Key'**
  String get secretKey;

  /// No description provided for @issuer.
  ///
  /// In en, this message translates to:
  /// **'Issuer'**
  String get issuer;

  /// No description provided for @delete.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get delete;

  /// No description provided for @edit.
  ///
  /// In en, this message translates to:
  /// **'Edit'**
  String get edit;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// No description provided for @save.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get save;

  /// No description provided for @copied.
  ///
  /// In en, this message translates to:
  /// **'Copied'**
  String get copied;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @appLock.
  ///
  /// In en, this message translates to:
  /// **'App Lock'**
  String get appLock;

  /// No description provided for @biometric.
  ///
  /// In en, this message translates to:
  /// **'Biometric'**
  String get biometric;

  /// No description provided for @theme.
  ///
  /// In en, this message translates to:
  /// **'Theme'**
  String get theme;

  /// No description provided for @light.
  ///
  /// In en, this message translates to:
  /// **'Light'**
  String get light;

  /// No description provided for @dark.
  ///
  /// In en, this message translates to:
  /// **'Dark'**
  String get dark;

  /// No description provided for @system.
  ///
  /// In en, this message translates to:
  /// **'System'**
  String get system;

  /// No description provided for @about.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about;

  /// No description provided for @version.
  ///
  /// In en, this message translates to:
  /// **'Version'**
  String get version;

  /// No description provided for @noAccounts.
  ///
  /// In en, this message translates to:
  /// **'No accounts'**
  String get noAccounts;

  /// No description provided for @deleteConfirm.
  ///
  /// In en, this message translates to:
  /// **'Delete this account?'**
  String get deleteConfirm;

  /// No description provided for @invalidQrcode.
  ///
  /// In en, this message translates to:
  /// **'Invalid QR Code'**
  String get invalidQrcode;

  /// No description provided for @invalidSecret.
  ///
  /// In en, this message translates to:
  /// **'Invalid Secret'**
  String get invalidSecret;

  /// No description provided for @search.
  ///
  /// In en, this message translates to:
  /// **'Search'**
  String get search;

  /// No description provided for @searchAccounts.
  ///
  /// In en, this message translates to:
  /// **'Search accounts...'**
  String get searchAccounts;

  /// No description provided for @noSearchResults.
  ///
  /// In en, this message translates to:
  /// **'No results found'**
  String get noSearchResults;

  /// No description provided for @noSearchResultsHint.
  ///
  /// In en, this message translates to:
  /// **'Try a different search term'**
  String get noSearchResultsHint;

  /// No description provided for @importAccount.
  ///
  /// In en, this message translates to:
  /// **'Import Account'**
  String get importAccount;

  /// No description provided for @security.
  ///
  /// In en, this message translates to:
  /// **'Security'**
  String get security;

  /// No description provided for @appearance.
  ///
  /// In en, this message translates to:
  /// **'Appearance'**
  String get appearance;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @info.
  ///
  /// In en, this message translates to:
  /// **'Info'**
  String get info;

  /// No description provided for @appLockSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Require authentication to open the app'**
  String get appLockSubtitle;

  /// No description provided for @biometricSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Use fingerprint or face to unlock'**
  String get biometricSubtitle;

  /// No description provided for @biometricUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Biometric authentication not available on this device'**
  String get biometricUnavailable;

  /// No description provided for @themeLight.
  ///
  /// In en, this message translates to:
  /// **'Always use light theme'**
  String get themeLight;

  /// No description provided for @themeDark.
  ///
  /// In en, this message translates to:
  /// **'Always use dark theme'**
  String get themeDark;

  /// No description provided for @themeSystem.
  ///
  /// In en, this message translates to:
  /// **'Follow device settings'**
  String get themeSystem;

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// No description provided for @deleteAccount.
  ///
  /// In en, this message translates to:
  /// **'Delete Account'**
  String get deleteAccount;

  /// No description provided for @confirmDelete.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete {accountName}?'**
  String confirmDelete(String accountName);

  /// No description provided for @codeCopied.
  ///
  /// In en, this message translates to:
  /// **'Code copied to clipboard'**
  String get codeCopied;

  /// No description provided for @accountAdded.
  ///
  /// In en, this message translates to:
  /// **'Account \"{accountName}\" added successfully'**
  String accountAdded(String accountName);

  /// No description provided for @errorAddingAccount.
  ///
  /// In en, this message translates to:
  /// **'Error adding account'**
  String get errorAddingAccount;

  /// No description provided for @secretRequired.
  ///
  /// In en, this message translates to:
  /// **'Secret key is required'**
  String get secretRequired;

  /// No description provided for @secretInvalid.
  ///
  /// In en, this message translates to:
  /// **'Invalid Base32 format. Use A-Z and 2-7 only'**
  String get secretInvalid;

  /// No description provided for @secretTooShort.
  ///
  /// In en, this message translates to:
  /// **'Secret key should be at least 16 characters'**
  String get secretTooShort;

  /// No description provided for @accountNameRequired.
  ///
  /// In en, this message translates to:
  /// **'Account name is required'**
  String get accountNameRequired;

  /// No description provided for @addingAccount.
  ///
  /// In en, this message translates to:
  /// **'Adding Account...'**
  String get addingAccount;

  /// No description provided for @enterAccountDetails.
  ///
  /// In en, this message translates to:
  /// **'Enter Account Details'**
  String get enterAccountDetails;

  /// No description provided for @enterAccountInfo.
  ///
  /// In en, this message translates to:
  /// **'Manually enter your account information'**
  String get enterAccountInfo;

  /// No description provided for @accountNameHint.
  ///
  /// In en, this message translates to:
  /// **'e.g., user@example.com'**
  String get accountNameHint;

  /// No description provided for @accountNameHelper.
  ///
  /// In en, this message translates to:
  /// **'The account identifier (usually your email)'**
  String get accountNameHelper;

  /// No description provided for @issuerHint.
  ///
  /// In en, this message translates to:
  /// **'e.g., Google, GitHub, Amazon'**
  String get issuerHint;

  /// No description provided for @issuerHelper.
  ///
  /// In en, this message translates to:
  /// **'The service or organization (optional)'**
  String get issuerHelper;

  /// No description provided for @secretHint.
  ///
  /// In en, this message translates to:
  /// **'e.g., JBSWY3DPEHPK3PXP'**
  String get secretHint;

  /// No description provided for @secretHelper.
  ///
  /// In en, this message translates to:
  /// **'Base32 encoded secret from your provider'**
  String get secretHelper;

  /// No description provided for @showSecret.
  ///
  /// In en, this message translates to:
  /// **'Show secret'**
  String get showSecret;

  /// No description provided for @hideSecret.
  ///
  /// In en, this message translates to:
  /// **'Hide secret'**
  String get hideSecret;

  /// No description provided for @base32Hint.
  ///
  /// In en, this message translates to:
  /// **'The secret key must be in Base32 format (A-Z and 2-7). Spaces are automatically removed.'**
  String get base32Hint;

  /// No description provided for @scanQrcodeInstructions.
  ///
  /// In en, this message translates to:
  /// **'Point the camera at a TOTP QR code'**
  String get scanQrcodeInstructions;

  /// No description provided for @onlyTotpSupported.
  ///
  /// In en, this message translates to:
  /// **'Only TOTP QR codes are supported'**
  String get onlyTotpSupported;

  /// No description provided for @invalidQrcodeFormat.
  ///
  /// In en, this message translates to:
  /// **'Invalid QR code'**
  String get invalidQrcodeFormat;

  /// No description provided for @cameraPermissionRequired.
  ///
  /// In en, this message translates to:
  /// **'Camera Permission Required'**
  String get cameraPermissionRequired;

  /// No description provided for @cameraPermissionDesc.
  ///
  /// In en, this message translates to:
  /// **'To scan QR codes, please grant camera permission.'**
  String get cameraPermissionDesc;

  /// No description provided for @grantPermission.
  ///
  /// In en, this message translates to:
  /// **'Grant Permission'**
  String get grantPermission;

  /// No description provided for @openSettings.
  ///
  /// In en, this message translates to:
  /// **'Open Settings'**
  String get openSettings;

  /// No description provided for @cameraError.
  ///
  /// In en, this message translates to:
  /// **'Camera Error'**
  String get cameraError;

  /// No description provided for @toggleFlashlight.
  ///
  /// In en, this message translates to:
  /// **'Toggle Flashlight'**
  String get toggleFlashlight;

  /// No description provided for @switchCamera.
  ///
  /// In en, this message translates to:
  /// **'Switch Camera'**
  String get switchCamera;

  /// No description provided for @refreshCode.
  ///
  /// In en, this message translates to:
  /// **'Refresh code'**
  String get refreshCode;

  /// No description provided for @noAccountsYet.
  ///
  /// In en, this message translates to:
  /// **'No accounts yet'**
  String get noAccountsYet;

  /// No description provided for @tapPlusToAdd.
  ///
  /// In en, this message translates to:
  /// **'Tap the + button to add your first account'**
  String get tapPlusToAdd;

  /// No description provided for @editAccount.
  ///
  /// In en, this message translates to:
  /// **'Edit Account'**
  String get editAccount;

  /// No description provided for @accountUpdated.
  ///
  /// In en, this message translates to:
  /// **'Account \"{accountName}\" updated successfully'**
  String accountUpdated(String accountName);

  /// No description provided for @errorUpdatingAccount.
  ///
  /// In en, this message translates to:
  /// **'Error updating account'**
  String get errorUpdatingAccount;

  /// No description provided for @savingAccount.
  ///
  /// In en, this message translates to:
  /// **'Saving Account...'**
  String get savingAccount;

  /// No description provided for @editAccountComingSoon.
  ///
  /// In en, this message translates to:
  /// **'Edit account coming soon'**
  String get editAccountComingSoon;

  /// No description provided for @biometricFailed.
  ///
  /// In en, this message translates to:
  /// **'Biometric authentication failed'**
  String get biometricFailed;

  /// No description provided for @english.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get english;

  /// No description provided for @chinese.
  ///
  /// In en, this message translates to:
  /// **'Chinese'**
  String get chinese;

  /// No description provided for @crossPlatformAuthenticator.
  ///
  /// In en, this message translates to:
  /// **'Cross-platform authenticator for two-factor authentication'**
  String get crossPlatformAuthenticator;

  /// No description provided for @copyright.
  ///
  /// In en, this message translates to:
  /// **'2024 SillyAuth. All rights reserved.'**
  String get copyright;

  /// No description provided for @importFromFile.
  ///
  /// In en, this message translates to:
  /// **'Import from File'**
  String get importFromFile;

  /// No description provided for @importAccounts.
  ///
  /// In en, this message translates to:
  /// **'Import Accounts'**
  String get importAccounts;

  /// No description provided for @importDescription.
  ///
  /// In en, this message translates to:
  /// **'Import accounts from a Google Authenticator export file'**
  String get importDescription;

  /// No description provided for @selectFile.
  ///
  /// In en, this message translates to:
  /// **'Select File'**
  String get selectFile;

  /// No description provided for @importSuccess.
  ///
  /// In en, this message translates to:
  /// **'{count} account(s) imported successfully'**
  String importSuccess(int count);

  /// No description provided for @importPartial.
  ///
  /// In en, this message translates to:
  /// **'{count} account(s) imported, {invalidCount} invalid entry(ies) skipped'**
  String importPartial(int count, int invalidCount);

  /// No description provided for @importFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed to import accounts'**
  String get importFailed;

  /// No description provided for @noAccountsImported.
  ///
  /// In en, this message translates to:
  /// **'No valid accounts found in file'**
  String get noAccountsImported;

  /// No description provided for @duplicatesSkipped.
  ///
  /// In en, this message translates to:
  /// **'{count} duplicate(s) skipped'**
  String duplicatesSkipped(int count);

  /// No description provided for @invalidEntriesSkipped.
  ///
  /// In en, this message translates to:
  /// **'{count} invalid entry(ies) skipped'**
  String invalidEntriesSkipped(int count);

  /// No description provided for @importingAccounts.
  ///
  /// In en, this message translates to:
  /// **'Importing accounts...'**
  String get importingAccounts;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'zh'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'zh':
      return AppLocalizationsZh();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
