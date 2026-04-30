import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';

import 'shared/theme/app_theme.dart';
import 'features/home/home_screen.dart';
import 'features/add_account/add_account_screen.dart';
import 'features/settings/settings_screen.dart';
import 'features/settings/settings_provider.dart';
import 'features/settings/screens/theme_settings_screen.dart';
import 'features/settings/screens/about_screen.dart';
import 'l10n/app_localizations.dart';

/// The main app widget that configures theme and routing.
///
/// This widget sets up the MaterialApp with:
/// - Theme configuration (light/dark)
/// - Route navigation between screens
/// - Provider integration for state management
/// - Localization support
class SillyAuthApp extends StatelessWidget {
  /// Creates a SillyAuthApp instance.
  const SillyAuthApp({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer<SettingsProvider>(
      builder: (context, settingsProvider, child) {
        return MaterialApp(
          title: 'SillyAuth',
          debugShowCheckedModeBanner: false,
          // Theme configuration based on settings
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: settingsProvider.themeMode,
          // Localization configuration
          locale: settingsProvider.locale,
          // When locale is null, follow system locale
          localeResolutionCallback: (locale, supportedLocales) {
            // If user has selected a specific locale, use it
            if (settingsProvider.locale != null) {
              return settingsProvider.locale;
            }
            // Otherwise, follow system locale
            return locale;
          },
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: const [
            Locale('en'),
            Locale('zh'),
          ],
          // Home screen with navigation
          home: const HomeScreen(),
          // Named routes for navigation
          routes: {
            '/home': (context) => const HomeScreen(),
            '/add-account': (context) => const AddAccountScreen(),
            '/settings': (context) => const SettingsScreen(),
            '/theme-settings': (context) => ThemeSettingsScreen(
                  currentTheme: settingsProvider.themeModeString,
                  onThemeChanged: (String theme) {
                    settingsProvider.setThemeModeFromString(theme);
                  },
                ),
            '/about': (context) => const AboutScreen(),
          },
        );
      },
    );
  }
}

/// Route names for navigation throughout the app.
class AppRoutes {
  AppRoutes._();

  static const String home = '/';
  static const String addAccount = '/add-account';
  static const String settings = '/settings';
  static const String themeSettings = '/theme-settings';
  static const String about = '/about';

  /// Navigation helper to push a new route.
  static void navigateTo(BuildContext context, String route) {
    Navigator.pushNamed(context, route);
  }

  /// Navigation helper to push a new route and remove all previous routes.
  static void navigateAndRemoveUntil(BuildContext context, String route) {
    Navigator.pushNamedAndRemoveUntil(context, route, (route) => false);
  }

  /// Navigation helper to pop the current route.
  static void pop(BuildContext context) {
    Navigator.pop(context);
  }

  /// Navigation helper to push a route and get a result.
  static Future<T?> navigateForResult<T>(BuildContext context, String route) {
    return Navigator.push<T>(context, MaterialPageRoute(
      builder: (context) => _getRouteWidget(route),
    ));
  }

  /// Gets the appropriate widget for a route.
  static Widget _getRouteWidget(String route) {
    Widget widget;
    switch (route) {
      case addAccount:
        widget = const AddAccountScreen();
        break;
      case settings:
        widget = const SettingsScreen();
        break;
      case about:
        widget = const AboutScreen();
        break;
      case home:
      default:
        widget = const HomeScreen();
    }
    // Wrap with localization to ensure l10n is available
    return Localizations(
      locale: const Locale('zh'),
      delegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      child: widget,
    );
  }
}
