import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/utils/base32.dart';
import '../../../data/models/auth_account.dart';
import '../../../data/repositories/account_repository.dart';
import '../../../l10n/app_localizations.dart';

/// Manual Input Screen
///
/// Form to manually enter account details for TOTP authentication.
/// Includes validation for required fields and Base32 secret format.
class ManualInputScreen extends StatefulWidget {
  const ManualInputScreen({super.key});

  @override
  State<ManualInputScreen> createState() => _ManualInputScreenState();
}

class _ManualInputScreenState extends State<ManualInputScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form controllers
  final _nameController = TextEditingController();
  final _issuerController = TextEditingController();
  final _secretController = TextEditingController();

  // Form state
  bool _isLoading = false;
  bool _obscureSecret = true;

  @override
  void dispose() {
    _nameController.dispose();
    _issuerController.dispose();
    _secretController.dispose();
    super.dispose();
  }

  /// Validate the secret key is valid Base32
  String? _validateSecret(String? value) {
    final l10n = AppLocalizations.of(context)!;
    if (value == null || value.isEmpty) {
      return l10n.secretRequired;
    }

    // Clean the secret (remove spaces and convert to uppercase)
    final cleanedSecret = Base32.clean(value);

    if (cleanedSecret.isEmpty) {
      return l10n.secretRequired;
    }

    if (!Base32.isValid(cleanedSecret)) {
      return l10n.secretInvalid;
    }

    if (cleanedSecret.length < 16) {
      return l10n.secretTooShort;
    }

    return null;
  }

  /// Validate account name
  String? _validateName(String? value) {
    final l10n = AppLocalizations.of(context)!;
    if (value == null || value.trim().isEmpty) {
      return l10n.accountNameRequired;
    }
    return null;
  }

  /// Handle form submission
  Future<void> _onSubmit() async {
    final l10n = AppLocalizations.of(context)!;
    // Validate form
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // Clean the secret
      final secret = Base32.clean(_secretController.text);

      // Create the account
      final account = AuthAccount(
        name: _nameController.text.trim(),
        issuer: _issuerController.text.trim(),
        secret: secret,
      );

      // Save to repository
      final repository = context.read<AccountRepository>();
      await repository.addAccount(account);

      // Show success message
      if (mounted) {
        final accountName = account.issuer.isNotEmpty ? account.issuer : account.name;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.accountAdded(accountName)),
            backgroundColor: Theme.of(context).colorScheme.primary,
          ),
        );
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${l10n.errorAddingAccount}: ${e.toString()}'),
            backgroundColor: Theme.of(context).colorScheme.error,
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
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.only(bottom: 24),
              child: Column(
                children: [
                  Icon(
                    Icons.edit_note,
                    size: 48,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    l10n.enterAccountDetails,
                    style: Theme.of(context).textTheme.titleLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    l10n.enterAccountInfo,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),

            // Account Name Field
            TextFormField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: '${l10n.accountName} *',
                hintText: l10n.accountNameHint,
                prefixIcon: const Icon(Icons.person_outline),
                helperText: l10n.accountNameHelper,
              ),
              textInputAction: TextInputAction.next,
              textCapitalization: TextCapitalization.none,
              autocorrect: false,
              validator: _validateName,
            ),
            const SizedBox(height: 16),

            // Issuer Field
            TextFormField(
              controller: _issuerController,
              decoration: InputDecoration(
                labelText: l10n.issuer,
                hintText: l10n.issuerHint,
                prefixIcon: const Icon(Icons.business_outlined),
                helperText: l10n.issuerHelper,
              ),
              textInputAction: TextInputAction.next,
              textCapitalization: TextCapitalization.words,
            ),
            const SizedBox(height: 16),

            // Secret Key Field
            TextFormField(
              controller: _secretController,
              decoration: InputDecoration(
                labelText: '${l10n.secretKey} *',
                hintText: l10n.secretHint,
                prefixIcon: const Icon(Icons.key_outlined),
                helperText: l10n.secretHelper,
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscureSecret ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                  ),
                  onPressed: () {
                    setState(() {
                      _obscureSecret = !_obscureSecret;
                    });
                  },
                  tooltip: _obscureSecret ? l10n.showSecret : l10n.hideSecret,
                ),
              ),
              textInputAction: TextInputAction.done,
              textCapitalization: TextCapitalization.characters,
              obscureText: _obscureSecret,
              autocorrect: false,
              validator: _validateSecret,
              onFieldSubmitted: (_) => _onSubmit(),
            ),
            const SizedBox(height: 8),

            // Base32 format hint
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.info_outline,
                    size: 16,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      l10n.base32Hint,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Submit Button
            FilledButton.icon(
              onPressed: _isLoading ? null : _onSubmit,
              icon: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.add),
              label: Text(_isLoading ? l10n.addingAccount : l10n.addAccount),
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
      ),
    );
  }
}
