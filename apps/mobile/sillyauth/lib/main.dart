import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import 'app.dart';
import 'data/repositories/account_repository.dart';
import 'features/settings/settings_provider.dart';
import 'features/home/providers/account_provider.dart';

/// The entry point for the SillyAuth application.
///
/// This function initializes Flutter and sets up the app with:
/// - System UI overlay style
/// - Provider setup with MultiProvider
/// - AccountRepository for data persistence
void main() async {
  // Ensure Flutter bindings are initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Set preferred orientations (portrait only for this app)
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Colors.transparent,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  // Initialize the repository for data persistence
  final accountRepository = AccountRepository();

  // Initialize settings provider to get locale preference
  final settingsProvider = SettingsProvider(accountRepository);
  await settingsProvider.initialize();

  // Run the app with MultiProvider setup
  runApp(
    MultiProvider(
      providers: [
        // Provide the AccountRepository for data persistence
        Provider<AccountRepository>.value(value: accountRepository),
        // Provide the SettingsProvider
        ChangeNotifierProvider<SettingsProvider>.value(value: settingsProvider),
        // Provide the AccountProvider for TOTP account management
        ChangeNotifierProvider<AccountProvider>(
          create: (_) => AccountProvider(repository: accountRepository),
        ),
      ],
      child: const SillyAuthApp(),
    ),
  );
}
