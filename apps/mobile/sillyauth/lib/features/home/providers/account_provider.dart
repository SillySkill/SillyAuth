import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../data/models/auth_account.dart';
import '../../../data/repositories/account_repository.dart';
import '../../../core/totp/totp_generator.dart';

/// Provider for managing account state and TOTP code generation.
///
/// This class handles:
/// - Loading accounts from storage
/// - Generating TOTP codes for each account
/// - Auto-refreshing codes every 30 seconds
/// - Managing countdown timers
class AccountProvider extends ChangeNotifier {
  final AccountRepository _repository;

  List<AuthAccount> _accounts = [];
  final Map<String, String> _codes = {};
  final Map<String, int> _remainingSeconds = {};
  bool _isLoading = true;
  String? _error;
  Timer? _refreshTimer;
  String _searchQuery = '';

  AccountProvider({AccountRepository? repository})
      : _repository = repository ?? AccountRepository();

  /// List of all accounts.
  List<AuthAccount> get accounts => _accounts;

  /// Current search query.
  String get searchQuery => _searchQuery;

  /// Whether search is active (non-empty query).
  bool get isSearching => _searchQuery.isNotEmpty;

  /// Filtered list of accounts based on search query.
  /// Filters by account name or issuer (case-insensitive).
  List<AuthAccount> get filteredAccounts {
    if (_searchQuery.isEmpty) {
      return _accounts;
    }
    final query = _searchQuery.toLowerCase();
    return _accounts.where((account) {
      return account.name.toLowerCase().contains(query) ||
          account.issuer.toLowerCase().contains(query);
    }).toList();
  }

  /// Map of account IDs to their current TOTP codes.
  Map<String, String> get codes => _codes;

  /// Map of account IDs to remaining seconds until code expires.
  Map<String, int> get remainingSeconds => _remainingSeconds;

  /// Whether the provider is currently loading accounts.
  bool get isLoading => _isLoading;

  /// Error message if something went wrong.
  String? get error => _error;

  /// Whether there are any accounts.
  bool get hasAccounts => _accounts.isNotEmpty;

  /// Whether there are any filtered accounts (considering search).
  bool get hasFilteredAccounts => filteredAccounts.isNotEmpty;

  /// Sets the search query for filtering accounts.
  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  /// Clears the search query to show all accounts.
  void clearSearch() {
    _searchQuery = '';
    notifyListeners();
  }

  /// Initializes the provider by loading accounts and starting the refresh timer.
  Future<void> initialize() async {
    await loadAccounts();
    _startRefreshTimer();
  }

  /// Loads all accounts from the repository.
  Future<void> loadAccounts() async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      _accounts = await _repository.getAllAccounts();
      await _refreshAllCodes();
    } catch (e) {
      _error = 'Failed to load accounts: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Refreshes the TOTP code for a specific account.
  Future<void> refreshCode(String accountId) async {
    final account = _accounts.firstWhere(
      (a) => a.id == accountId,
      orElse: () => throw Exception('Account not found'),
    );

    final totp = TotpGenerator(
      secret: account.secret,
      period: account.period,
      digits: account.digits,
    );

    _codes[accountId] = totp.generate();
    _remainingSeconds[accountId] = totp.getRemainingSeconds();
    notifyListeners();
  }

  /// Refreshes TOTP codes for all accounts.
  Future<void> _refreshAllCodes() async {
    for (final account in _accounts) {
      final totp = TotpGenerator(
        secret: account.secret,
        period: account.period,
        digits: account.digits,
      );

      _codes[account.id] = totp.generate();
      _remainingSeconds[account.id] = totp.getRemainingSeconds();
    }
    notifyListeners();
  }

  /// Starts the auto-refresh timer.
  void _startRefreshTimer() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      _updateCountdowns();
    });
  }

  /// Updates the countdown for all accounts.
  /// Uses a ticker to throttle UI updates to avoid performance issues.
  int _updateCounter = 0;

  void _updateCountdowns() {
    bool hasChanges = false;

    for (final account in _accounts) {
      final totp = TotpGenerator(
        secret: account.secret,
        period: account.period,
        digits: account.digits,
      );

      final newRemaining = totp.getRemainingSeconds();
      final currentRemaining = _remainingSeconds[account.id] ?? 0;

      // If remaining seconds decreased, we need to refresh the code
      if (newRemaining > currentRemaining || newRemaining == account.period) {
        // Code just refreshed
        _codes[account.id] = totp.generate();
        hasChanges = true;
      }

      _remainingSeconds[account.id] = newRemaining;
    }

    _updateCounter++;

    // Only notify when:
    // 1. Code actually changed (hasChanges), OR
    // 2. Every second to update countdown display (throttled)
    if (hasChanges || _updateCounter >= 1) {
      _updateCounter = 0;
      notifyListeners();
    }
  }

  /// Adds a new account.
  Future<void> addAccount(AuthAccount account) async {
    try {
      final newAccount = await _repository.addAccount(account);
      _accounts.add(newAccount);

      // Generate code for the new account
      final totp = TotpGenerator(
        secret: newAccount.secret,
        period: newAccount.period,
        digits: newAccount.digits,
      );

      _codes[newAccount.id] = totp.generate();
      _remainingSeconds[newAccount.id] = totp.getRemainingSeconds();

      notifyListeners();
    } catch (e) {
      _error = 'Failed to add account: $e';
      notifyListeners();
    }
  }

  /// Updates an existing account.
  Future<void> updateAccount(AuthAccount account) async {
    try {
      final updatedAccount = await _repository.updateAccount(account);
      final index = _accounts.indexWhere((a) => a.id == account.id);

      if (index != -1) {
        _accounts[index] = updatedAccount;
        notifyListeners();
      }
    } catch (e) {
      _error = 'Failed to update account: $e';
      notifyListeners();
    }
  }

  /// Deletes an account.
  Future<void> deleteAccount(String accountId) async {
    try {
      await _repository.deleteAccount(accountId);
      _accounts.removeWhere((a) => a.id == accountId);
      _codes.remove(accountId);
      _remainingSeconds.remove(accountId);
      notifyListeners();
    } catch (e) {
      _error = 'Failed to delete account: $e';
      notifyListeners();
    }
  }

  /// Reorders accounts based on the given old and new indices.
  ///
  /// This method handles reordering in the local list and persists
  /// the new order to storage via the repository.
  Future<void> reorderAccounts(int oldIndex, int newIndex) async {
    try {
      // Adjust newIndex if needed (ReorderableListView behavior)
      if (newIndex > oldIndex) {
        newIndex -= 1;
      }

      // Remove the item from the old position
      final account = _accounts.removeAt(oldIndex);
      // Insert it at the new position
      _accounts.insert(newIndex, account);

      // Update sort orders for all accounts
      final ids = _accounts.map((a) => a.id).toList();
      for (int i = 0; i < _accounts.length; i++) {
        _accounts[i] = _accounts[i].copyWith(sortOrder: i);
      }

      // Persist the new order to storage
      await _repository.reorderAccounts(ids);

      notifyListeners();
    } catch (e) {
      _error = 'Failed to reorder accounts: $e';
      notifyListeners();
    }
  }

  /// Gets the TOTP code for a specific account.
  String getCode(String accountId) {
    return _codes[accountId] ?? '------';
  }

  /// Gets the remaining seconds for a specific account.
  int getRemainingSeconds(String accountId) {
    return _remainingSeconds[accountId] ?? 0;
  }

  /// Gets the progress (0.0 to 1.0) for a specific account's countdown.
  double getProgress(String accountId) {
    final account = _accounts.firstWhere(
      (a) => a.id == accountId,
      orElse: () => throw Exception('Account not found'),
    );

    final remaining = _remainingSeconds[accountId] ?? account.period;
    return 1.0 - (remaining / account.period);
  }

  /// Copies the TOTP code for an account to clipboard.
  Future<void> copyCode(String accountId) async {
    final code = _codes[accountId];
    if (code != null) {
      await Clipboard.setData(ClipboardData(text: code));
    }
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
}
