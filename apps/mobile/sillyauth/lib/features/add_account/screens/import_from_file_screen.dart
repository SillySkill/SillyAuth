import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';

import '../../../core/utils/otpauth_parser.dart';
import '../../../data/models/auth_account.dart';
import '../../../data/repositories/account_repository.dart';
import '../../../l10n/app_localizations.dart';

/// Import from File Screen
///
/// Allows importing TOTP accounts from a text file exported
/// from Google Authenticator.
class ImportFromFileScreen extends StatefulWidget {
  const ImportFromFileScreen({super.key});

  @override
  State<ImportFromFileScreen> createState() => _ImportFromFileScreenState();
}

class _ImportFromFileScreenState extends State<ImportFromFileScreen> {
  bool _isLoading = false;

  /// Handle file selection and import
  Future<void> _selectAndImportFile() async {
    if (!mounted) return;

    final l10n = AppLocalizations.of(context)!;
    final scaffoldMessenger = ScaffoldMessenger.of(context);
    final colorScheme = Theme.of(context).colorScheme;

    try {
      // Show loading
      setState(() {
        _isLoading = true;
      });

      // Pick the file
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['txt'],
        allowMultiple: false,
      );

      if (result == null || result.files.isEmpty) {
        // User cancelled
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
        }
        return;
      }

      final file = result.files.first;
      final filePath = file.path;

      if (filePath == null) {
        if (mounted) {
          scaffoldMessenger.showSnackBar(
            SnackBar(
              content: Text(l10n.importFailed),
              backgroundColor: colorScheme.error,
            ),
          );
        }
        return;
      }

      // Read file content
      final content = await File(filePath).readAsString();

      // Get existing secrets for duplicate checking
      if (!mounted) return;
      final repository = context.read<AccountRepository>();
      final existingAccounts = await repository.getAllAccounts();
      final existingSecrets =
          existingAccounts.map((a) => a.secret.toUpperCase()).toSet();

      // Parse the file
      final parseResult = OtpAuthParser.parseWithExistingCheck(
        content,
        existingSecrets,
      );

      if (!parseResult.hasSuccess) {
        if (mounted) {
          String message = l10n.noAccountsImported;
          if (parseResult.invalidUris.isNotEmpty) {
            message += '\n${l10n.invalidEntriesSkipped(parseResult.invalidUris.length)}';
          }
          scaffoldMessenger.showSnackBar(
            SnackBar(
              content: Text(message),
              backgroundColor: colorScheme.error,
            ),
          );
        }
        setState(() {
          _isLoading = false;
        });
        return;
      }

      // Import the accounts
      int importedCount = 0;
      for (final accountData in parseResult.accounts) {
        final account = AuthAccount(
          name: accountData['name'] as String,
          issuer: accountData['issuer'] as String,
          secret: accountData['secret'] as String,
          digits: accountData['digits'] as int? ?? 6,
          period: accountData['period'] as int? ?? 30,
        );
        await repository.addAccount(account);
        importedCount++;
      }

      if (mounted) {
        // Show success message
        String message;
        if (parseResult.hasErrors) {
          message = l10n.importPartial(
            importedCount,
            parseResult.invalidUris.length + parseResult.duplicateSecrets.length,
          );
        } else {
          message = l10n.importSuccess(importedCount);
        }

        scaffoldMessenger.showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: colorScheme.primary,
          ),
        );

        // Navigate back to trigger refresh
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      if (mounted) {
        scaffoldMessenger.showSnackBar(
          SnackBar(
            content: Text('${l10n.importFailed}: ${e.toString()}'),
            backgroundColor: colorScheme.error,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.only(bottom: 24),
            child: Column(
              children: [
                Icon(
                  Icons.file_upload_outlined,
                  size: 64,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(height: 16),
                Text(
                  l10n.importAccounts,
                  style: Theme.of(context).textTheme.titleLarge,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  l10n.importDescription,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),

          // Example format card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      size: 20,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Example Format',
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  'otpauth://totp/Google:user@gmail.com?secret=JBSWY3DPEHPK3PXP&issuer=Google\n'
                  'otpauth://totp/GitHub:developer?secret=GEZDGNBVGY3TQOJQ&issuer=GitHub',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontFamily: 'monospace',
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),

          // Select File Button
          FilledButton.icon(
            onPressed: _isLoading ? null : _selectAndImportFile,
            icon: _isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.folder_open),
            label: Text(_isLoading ? l10n.importingAccounts : l10n.selectFile),
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
          const SizedBox(height: 16),

          // Cancel Button
          OutlinedButton(
            onPressed: _isLoading
                ? null
                : () {
                    Navigator.of(context).pop();
                  },
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
            child: Text(l10n.cancel),
          ),
        ],
      ),
    );
  }
}
