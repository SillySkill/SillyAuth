import 'package:flutter/material.dart';

import '../../../l10n/app_localizations.dart';

/// Theme settings screen for selecting the app theme.
///
/// Provides options for light, dark, and system theme modes.
class ThemeSettingsScreen extends StatelessWidget {
  /// The currently selected theme mode.
  final String currentTheme;

  /// Callback when theme is changed.
  final Function(String) onThemeChanged;

  const ThemeSettingsScreen({
    super.key,
    required this.currentTheme,
    required this.onThemeChanged,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.theme),
      ),
      body: ListView(
        children: [
          _buildThemeOption(
            context,
            title: l10n.light,
            subtitle: l10n.themeLight,
            icon: Icons.light_mode,
            themeValue: 'light',
          ),
          _buildThemeOption(
            context,
            title: l10n.dark,
            subtitle: l10n.themeDark,
            icon: Icons.dark_mode,
            themeValue: 'dark',
          ),
          _buildThemeOption(
            context,
            title: l10n.system,
            subtitle: l10n.themeSystem,
            icon: Icons.settings_brightness,
            themeValue: 'system',
          ),
        ],
      ),
    );
  }

  Widget _buildThemeOption(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required String themeValue,
  }) {
    final isSelected = currentTheme == themeValue;

    return ListTile(
      leading: Icon(
        icon,
        color: isSelected
            ? Theme.of(context).colorScheme.primary
            : Theme.of(context).colorScheme.onSurfaceVariant,
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: isSelected
          ? Icon(
              Icons.check,
              color: Theme.of(context).colorScheme.primary,
            )
          : null,
      onTap: () {
        onThemeChanged(themeValue);
        Navigator.pop(context);
      },
    );
  }
}
