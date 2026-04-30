// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import 'package:silly_auth/app.dart';
import 'package:silly_auth/data/repositories/account_repository.dart';
import 'package:silly_auth/features/home/providers/account_provider.dart';
import 'package:silly_auth/features/settings/settings_provider.dart';
import 'package:silly_auth/l10n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

void main() {
  testWidgets('App renders home screen', (WidgetTester tester) async {
    // Create a mock repository for testing
    final repository = AccountRepository();

    // Build our app and trigger a frame.
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          Provider<AccountRepository>.value(value: repository),
          ChangeNotifierProvider<SettingsProvider>(
            create: (_) => SettingsProvider(repository),
          ),
          ChangeNotifierProvider<AccountProvider>(
            create: (_) => AccountProvider(repository: repository),
          ),
        ],
        child: const MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: [
            Locale('en'),
            Locale('zh'),
          ],
          home: SillyAuthApp(),
        ),
      ),
    );

    // Wait for the app to settle
    await tester.pumpAndSettle();

    // Verify that our app name appears in the app bar
    expect(find.text('SillyAuth'), findsOneWidget);

    // Verify that the settings icon is present
    expect(find.byIcon(Icons.settings), findsOneWidget);

    // Verify that the add button (FAB) is present
    expect(find.byIcon(Icons.add), findsOneWidget);
  });
}
