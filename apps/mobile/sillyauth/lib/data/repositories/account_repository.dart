import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../models/auth_account.dart';

/// Repository for managing AuthAccount data persistence.
///
/// This class provides methods for CRUD operations on accounts
/// using flutter_secure_storage for secure data storage.
class AccountRepository {
  /// Key used for storing accounts in secure storage.
  static const String _accountsKey = 'accounts';

  /// Key used for storing settings in secure storage.
  static const String _settingsKey = 'settings';

  /// The underlying secure storage instance.
  final FlutterSecureStorage _storage;

  /// Creates a new AccountRepository instance.
  ///
  /// [storage] is optional and defaults to a standard FlutterSecureStorage
  /// instance. This parameter is useful for testing or when custom storage
  /// options are needed.
  AccountRepository({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(
                encryptedSharedPreferences: true,
              ),
              iOptions: IOSOptions(
                accessibility: KeychainAccessibility.first_unlock_this_device,
              ),
            );

  /// Retrieves all stored accounts.
  ///
  /// Returns a list of [AuthAccount] objects sorted by their [sortOrder].
  /// Returns an empty list if no accounts are stored.
  Future<List<AuthAccount>> getAllAccounts() async {
    try {
      final jsonString = await _storage.read(key: _accountsKey);
      if (jsonString == null || jsonString.isEmpty) {
        return [];
      }

      final List<dynamic> jsonList = json.decode(jsonString) as List<dynamic>;
      final accounts = jsonList
          .map((item) => AuthAccount.fromJson(item as Map<String, dynamic>))
          .toList();

      // Sort by sortOrder
      accounts.sort((a, b) => a.sortOrder.compareTo(b.sortOrder));
      return accounts;
    } catch (e) {
      // If there's an error reading/parsing, return empty list
      return [];
    }
  }

  /// Adds a new account to storage.
  ///
  /// The account will be assigned a unique ID if not provided.
  /// Returns the added account with its assigned ID.
  Future<AuthAccount> addAccount(AuthAccount account) async {
    final accounts = await getAllAccounts();

    // Set sort order to be at the end
    final newAccount = account.copyWith(
      sortOrder: accounts.isEmpty ? 0 : accounts.last.sortOrder + 1,
    );

    accounts.add(newAccount);
    await _saveAccounts(accounts);
    return newAccount;
  }

  /// Updates an existing account in storage.
  ///
  /// The account is identified by its [id]. If no account with the
  /// given ID exists, an exception is thrown.
  /// Returns the updated account.
  Future<AuthAccount> updateAccount(AuthAccount account) async {
    final accounts = await getAllAccounts();
    final index = accounts.indexWhere((a) => a.id == account.id);

    if (index == -1) {
      throw Exception('Account not found: ${account.id}');
    }

    accounts[index] = account;
    await _saveAccounts(accounts);
    return account;
  }

  /// Deletes an account from storage.
  ///
  /// The account is identified by its [id]. If no account with the
  /// given ID exists, this method does nothing.
  Future<void> deleteAccount(String id) async {
    final accounts = await getAllAccounts();
    accounts.removeWhere((a) => a.id == id);
    await _saveAccounts(accounts);
  }

  /// Reorders accounts based on the provided list of IDs.
  ///
  /// The [ids] list should contain all account IDs in the desired order.
  /// Each account's [sortOrder] will be updated to reflect its position
  /// in the list.
  Future<void> reorderAccounts(List<String> ids) async {
    final accounts = await getAllAccounts();

    // Create a map for quick lookup
    final accountMap = {for (var a in accounts) a.id: a};

    // Update sort orders based on the new order
    for (int i = 0; i < ids.length; i++) {
      final account = accountMap[ids[i]];
      if (account != null) {
        accountMap[ids[i]] = account.copyWith(sortOrder: i);
      }
    }

    // Save updated accounts
    final updatedAccounts = accountMap.values.toList();
    await _saveAccounts(updatedAccounts);
  }

  /// Saves the accounts list to secure storage.
  ///
  /// This is a private method that handles the actual storage operation.
  Future<void> _saveAccounts(List<AuthAccount> accounts) async {
    final jsonList = accounts.map((a) => a.toJson()).toList();
    final jsonString = json.encode(jsonList);
    await _storage.write(key: _accountsKey, value: jsonString);
  }

  /// Gets a single account by its ID.
  ///
  /// Returns [AuthAccount] if found, otherwise returns null.
  Future<AuthAccount?> getAccountById(String id) async {
    final accounts = await getAllAccounts();
    try {
      return accounts.firstWhere((a) => a.id == id);
    } catch (e) {
      return null;
    }
  }

  /// Deletes all accounts from storage.
  ///
  /// Use with caution - this action cannot be undone.
  Future<void> deleteAllAccounts() async {
    await _storage.delete(key: _accountsKey);
  }

  /// Gets the current settings from storage.
  ///
  /// Returns a map containing settings or default values if not set.
  Future<Map<String, dynamic>> getSettings() async {
    try {
      final jsonString = await _storage.read(key: _settingsKey);
      if (jsonString == null || jsonString.isEmpty) {
        return _defaultSettings();
      }
      return json.decode(jsonString) as Map<String, dynamic>;
    } catch (e) {
      return _defaultSettings();
    }
  }

  /// Saves settings to storage.
  Future<void> saveSettings(Map<String, dynamic> settings) async {
    final jsonString = json.encode(settings);
    await _storage.write(key: _settingsKey, value: jsonString);
  }

  /// Returns the default settings.
  Map<String, dynamic> _defaultSettings() {
    return {
      'appLockEnabled': false,
      'biometricEnabled': false,
      'themeMode': 'system',
      'locale': 'system', // Follow system locale by default
    };
  }

  /// Clears all stored data.
  ///
  /// Use with caution - this action cannot be undone.
  Future<void> clearAll() async {
    await _storage.deleteAll();
  }
}
