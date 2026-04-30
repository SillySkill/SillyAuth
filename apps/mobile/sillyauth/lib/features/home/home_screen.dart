import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../shared/constants/app_colors.dart';
import '../../shared/constants/app_constants.dart';
import '../../data/models/auth_account.dart';
import '../../l10n/app_localizations.dart';
import '../add_account/add_account_screen.dart';
import '../settings/settings_screen.dart';
import 'providers/account_provider.dart';
import 'screens/edit_account_screen.dart';

/// Main home screen displaying the list of TOTP accounts.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isSearching = false;
  final TextEditingController _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    // Initialize the provider
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AccountProvider>().initialize();
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: _isSearching
            ? _buildSearchField(l10n)
            : Text(l10n.appName),
        actions: [
          if (_isSearching)
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: _closeSearch,
              tooltip: l10n.cancel,
            )
          else
            IconButton(
              icon: const Icon(Icons.search),
              onPressed: _startSearch,
              tooltip: l10n.search,
            ),
          if (!_isSearching)
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: _openSettings,
              tooltip: l10n.settings,
            ),
        ],
      ),
      body: Consumer<AccountProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (provider.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.error_outline,
                    size: 64,
                    color: Theme.of(context).colorScheme.error,
                  ),
                  const SizedBox(height: AppConstants.defaultPadding),
                  Text(
                    provider.error!,
                    style: Theme.of(context).textTheme.bodyLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: AppConstants.defaultPadding),
                  ElevatedButton(
                    onPressed: () => provider.loadAccounts(),
                    child: Text(l10n.retry),
                  ),
                ],
              ),
            );
          }

          if (!provider.hasAccounts) {
            return _buildEmptyState();
          }

          // Show "No results" message when searching and no accounts match
          if (provider.isSearching && !provider.hasFilteredAccounts) {
            return _buildNoResultsState();
          }

          // Use filtered accounts when searching, otherwise use all accounts
          final displayAccounts = provider.isSearching
              ? provider.filteredAccounts
              : provider.accounts;

          return RefreshIndicator(
            onRefresh: () => provider.loadAccounts(),
            child: ReorderableListView.builder(
              padding: const EdgeInsets.all(AppConstants.defaultPadding),
              itemCount: displayAccounts.length,
              onReorder: provider.isSearching
                  ? (oldIndex, newIndex) {} // Disable reordering when searching
                  : (oldIndex, newIndex) {
                      provider.reorderAccounts(oldIndex, newIndex);
                    },
              proxyDecorator: (child, index, animation) {
                return Material(
                  elevation: 4,
                  borderRadius: BorderRadius.circular(AppConstants.defaultBorderRadius),
                  child: child,
                );
              },
              itemBuilder: (context, index) {
                final account = displayAccounts[index];
                return _AccountCard(
                  key: ValueKey(account.id),
                  account: account,
                  onTap: () => _copyCode(account.id),
                  onLongPress: () => _showAccountOptions(account),
                  onRefresh: () => provider.refreshCode(account.id),
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _addAccount,
        tooltip: l10n.addAccount,
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildEmptyState() {
    final l10n = AppLocalizations.of(context)!;
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.account_balance_wallet_outlined,
            size: 80,
            color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.5),
          ),
          const SizedBox(height: AppConstants.defaultPadding),
          Text(
            l10n.noAccountsYet,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: AppConstants.smallPadding),
          Text(
            l10n.tapPlusToAdd,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildNoResultsState() {
    final l10n = AppLocalizations.of(context)!;
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.search_off,
            size: 80,
            color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.5),
          ),
          const SizedBox(height: AppConstants.defaultPadding),
          Text(
            l10n.noSearchResults,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: AppConstants.smallPadding),
          Text(
            l10n.noSearchResultsHint,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSearchField(AppLocalizations l10n) {
    return TextField(
      controller: _searchController,
      autofocus: true,
      decoration: InputDecoration(
        hintText: l10n.searchAccounts,
        border: InputBorder.none,
        hintStyle: TextStyle(
          color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
        ),
      ),
      style: Theme.of(context).textTheme.titleMedium,
      onChanged: (value) {
        context.read<AccountProvider>().setSearchQuery(value);
      },
    );
  }

  void _startSearch() {
    setState(() {
      _isSearching = true;
    });
  }

  void _closeSearch() {
    setState(() {
      _isSearching = false;
      _searchController.clear();
    });
    context.read<AccountProvider>().clearSearch();
  }

  void _copyCode(String accountId) {
    final l10n = AppLocalizations.of(context)!;
    final provider = context.read<AccountProvider>();
    provider.copyCode(accountId);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle, color: Colors.white),
            const SizedBox(width: AppConstants.smallPadding),
            Text(l10n.codeCopied),
          ],
        ),
        backgroundColor: AppColors.success,
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _showAccountOptions(AuthAccount account) {
    final l10n = AppLocalizations.of(context)!;
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.edit),
              title: Text(l10n.edit),
              onTap: () {
                Navigator.pop(context);
                _editAccount(account);
              },
            ),
            ListTile(
              leading: Icon(Icons.delete, color: Theme.of(context).colorScheme.error),
              title: Text(
                l10n.delete,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
              onTap: () {
                Navigator.pop(context);
                _confirmDelete(account);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _editAccount(AuthAccount account) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EditAccountScreen(account: account),
      ),
    );
  }

  void _confirmDelete(AuthAccount account) {
    final l10n = AppLocalizations.of(context)!;
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.deleteAccount),
        content: Text(l10n.confirmDelete(account.name)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.cancel),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<AccountProvider>().deleteAccount(account.id);
            },
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            child: Text(l10n.delete),
          ),
        ],
      ),
    );
  }

  void _addAccount() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const AddAccountScreen(),
      ),
    );
  }

  void _openSettings() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const SettingsScreen(),
      ),
    );
  }
}

/// Widget that displays a single account card with TOTP code and countdown.
class _AccountCard extends StatelessWidget {
  final AuthAccount account;
  final VoidCallback onTap;
  final VoidCallback onLongPress;
  final VoidCallback onRefresh;

  const _AccountCard({
    super.key,
    required this.account,
    required this.onTap,
    required this.onLongPress,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    // Use select to only rebuild when this specific account's data changes
    final code = context.select<AccountProvider, String>(
      (provider) => provider.getCode(account.id),
    );
    final remaining = context.select<AccountProvider, int>(
      (provider) => provider.getRemainingSeconds(account.id),
    );
    final progress = context.select<AccountProvider, double>(
      (provider) => provider.getProgress(account.id),
    );

    // Split code into two parts (e.g., "123 456")
    final codePart1 = code.length >= 3 ? code.substring(0, 3) : code;
    final codePart2 = code.length >= 3 ? code.substring(3) : '';

    final isLowTime = remaining <= 5;

    return Card(
      margin: const EdgeInsets.only(bottom: AppConstants.defaultPadding),
      child: InkWell(
        onTap: onTap,
        onLongPress: onLongPress,
        borderRadius: BorderRadius.circular(AppConstants.defaultBorderRadius),
        child: Padding(
          padding: const EdgeInsets.all(AppConstants.defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Issuer and account name
              Row(
                children: [
                  _buildIssuerIcon(context),
                  const SizedBox(width: AppConstants.smallPadding),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          account.issuer,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        Text(
                          account.name,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Theme.of(context)
                                    .colorScheme
                                    .onSurface
                                    .withValues(alpha: 0.6),
                              ),
                        ),
                      ],
                    ),
                  ),
                  // Refresh button
                  IconButton(
                    icon: const Icon(Icons.refresh),
                    onPressed: onRefresh,
                    tooltip: l10n.refreshCode,
                  ),
                ],
              ),
              const SizedBox(height: AppConstants.defaultPadding),

              // TOTP Code display
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    codePart1,
                    style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          letterSpacing: 4,
                          color: isLowTime
                              ? Theme.of(context).colorScheme.error
                              : Theme.of(context).colorScheme.primary,
                        ),
                  ),
                  Text(
                    ' ',
                    style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          letterSpacing: 4,
                        ),
                  ),
                  Text(
                    codePart2,
                    style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          letterSpacing: 4,
                          color: isLowTime
                              ? Theme.of(context).colorScheme.error
                              : Theme.of(context).colorScheme.primary,
                        ),
                  ),
                ],
              ),
              const SizedBox(height: AppConstants.defaultPadding),

              // Countdown progress
              Row(
                children: [
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: progress,
                        minHeight: 8,
                        backgroundColor: Theme.of(context)
                            .colorScheme
                            .primary
                            .withValues(alpha: 0.2),
                        valueColor: AlwaysStoppedAnimation<Color>(
                          isLowTime
                              ? Theme.of(context).colorScheme.error
                              : Theme.of(context).colorScheme.primary,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: AppConstants.smallPadding),
                  SizedBox(
                    width: 40,
                    child: Text(
                      '${remaining}s',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            color: isLowTime
                                ? Theme.of(context).colorScheme.error
                                : Theme.of(context)
                                    .colorScheme
                                    .onSurface
                                    .withValues(alpha: 0.6),
                            fontWeight: isLowTime ? FontWeight.bold : null,
                          ),
                      textAlign: TextAlign.right,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildIssuerIcon(BuildContext context) {
    // Get first letter of issuer for the avatar
    final letter = account.issuer.isNotEmpty ? account.issuer[0].toUpperCase() : '?';

    // Generate a color based on the issuer name
    final colorIndex = account.issuer.hashCode % _issuerColors.length;
    final color = _issuerColors[colorIndex.abs()];

    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Center(
        child: Text(
          letter,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
        ),
      ),
    );
  }

  static const List<Color> _issuerColors = [
    AppColors.primaryDeepBlue,
    AppColors.gold,
    AppColors.lightBlue,
    Color(0xFF4CAF50), // Green
    Color(0xFFE91E63), // Pink
    Color(0xFF9C27B0), // Purple
    Color(0xFF00BCD4), // Cyan
    Color(0xFFFF5722), // Deep Orange
  ];
}
