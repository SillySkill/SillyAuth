import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../data/models/auth_account.dart';
import '../../../l10n/app_localizations.dart';
import '../providers/account_provider.dart';

/// Edit Account Screen
///
/// Form screen to edit an existing account's name and issuer.
/// Pre-populates the form with current account data.
class EditAccountScreen extends StatefulWidget {
  /// The account to edit
  final AuthAccount account;

  const EditAccountScreen({
    super.key,
    required this.account,
  });

  @override
  State<EditAccountScreen> createState() => _EditAccountScreenState();
}

class _EditAccountScreenState extends State<EditAccountScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form controllers
  late final TextEditingController _nameController;
  late final TextEditingController _issuerController;

  // Form state
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Pre-populate with existing values
    _nameController = TextEditingController(text: widget.account.name);
    _issuerController = TextEditingController(text: widget.account.issuer);
  }

  @override
  void dispose() {
    _nameController.dispose();
    _issuerController.dispose();
    super.dispose();
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
      // Create updated account with existing values preserved
      final updatedAccount = widget.account.copyWith(
        name: _nameController.text.trim(),
        issuer: _issuerController.text.trim(),
      );

      // Update via provider
      await context.read<AccountProvider>().updateAccount(updatedAccount);

      // Show success message
      if (mounted) {
        final accountName = updatedAccount.issuer.isNotEmpty
            ? updatedAccount.issuer
            : updatedAccount.name;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.accountUpdated(accountName)),
            backgroundColor: Theme.of(context).colorScheme.primary,
          ),
        );
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${l10n.errorUpdatingAccount}: ${e.toString()}'),
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
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.editAccount),
      ),
      body: SingleChildScrollView(
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
                      l10n.editAccount,
                      style: Theme.of(context).textTheme.titleLarge,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.account.issuer.isNotEmpty
                          ? '${widget.account.issuer} - ${widget.account.name}'
                          : widget.account.name,
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
                textInputAction: TextInputAction.done,
                textCapitalization: TextCapitalization.words,
                onFieldSubmitted: (_) => _onSubmit(),
              ),
              const SizedBox(height: 32),

              // Save Button
              FilledButton.icon(
                onPressed: _isLoading ? null : _onSubmit,
                icon: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.save),
                label: Text(_isLoading ? l10n.savingAccount : l10n.save),
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
      ),
    );
  }
}
