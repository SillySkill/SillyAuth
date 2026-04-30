import 'package:flutter/material.dart';

import '../../../shared/constants/app_colors.dart';
import '../../../shared/constants/app_constants.dart';
import '../../../l10n/app_localizations.dart';

/// About screen displaying app information.
///
/// Shows the app name, version, and description.
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.about),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(AppConstants.largePadding),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildAppIcon(),
              const SizedBox(height: AppConstants.largePadding),
              _buildAppName(context, l10n),
              const SizedBox(height: AppConstants.smallPadding),
              _buildVersion(context, l10n),
              const SizedBox(height: AppConstants.largePadding),
              _buildDescription(context, l10n),
              const Spacer(),
              _buildCopyright(context, l10n),
              const SizedBox(height: AppConstants.defaultPadding),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppIcon() {
    return Container(
      width: 120,
      height: 120,
      decoration: BoxDecoration(
        color: AppColors.primaryDeepBlue,
        borderRadius: BorderRadius.circular(AppConstants.largeBorderRadius),
        boxShadow: [
          BoxShadow(
            color: AppColors.primaryDeepBlue.withValues(alpha: 0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.lock_outline,
            size: 48,
            color: AppColors.gold,
          ),
          const SizedBox(height: 4),
          const Text(
            'SillyAuth',
            style: TextStyle(
              color: AppColors.textOnPrimary,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAppName(BuildContext context, AppLocalizations l10n) {
    return Text(
      l10n.appName,
      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
      textAlign: TextAlign.center,
    );
  }

  Widget _buildVersion(BuildContext context, AppLocalizations l10n) {
    return Text(
      '${l10n.version} ${AppConstants.appVersion}',
      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
      textAlign: TextAlign.center,
    );
  }

  Widget _buildDescription(BuildContext context, AppLocalizations l10n) {
    return Text(
      l10n.crossPlatformAuthenticator,
      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
      textAlign: TextAlign.center,
    );
  }

  Widget _buildCopyright(BuildContext context, AppLocalizations l10n) {
    return Text(
      l10n.copyright,
      style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
      textAlign: TextAlign.center,
    );
  }
}
