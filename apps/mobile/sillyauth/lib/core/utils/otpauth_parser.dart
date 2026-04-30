import '../utils/otpauth_uri.dart';

/// Result of parsing multiple otpauth:// URIs
class OtpAuthParseResult {
  /// List of successfully parsed accounts
  final List<Map<String, dynamic>> accounts;

  /// List of invalid URIs that could not be parsed
  final List<String> invalidUris;

  /// List of secrets that are duplicates of already parsed URIs
  final List<String> duplicateSecrets;

  OtpAuthParseResult({
    required this.accounts,
    required this.invalidUris,
    required this.duplicateSecrets,
  });

  /// Number of successfully imported accounts
  int get successCount => accounts.length;

  /// Whether any accounts were successfully parsed
  bool get hasSuccess => accounts.isNotEmpty;

  /// Whether there were any errors
  bool get hasErrors => invalidUris.isNotEmpty || duplicateSecrets.isNotEmpty;
}

/// Parser for multiple otpauth:// URIs from text content
///
/// Handles Google Authenticator export format where each line
/// contains a single otpauth:// URI.
class OtpAuthParser {
  /// Parses multiple otpauth:// URIs from a text string.
  ///
  /// Each line in the text is treated as a separate URI.
  /// Empty lines are skipped.
  ///
  /// Returns an [OtpAuthParseResult] containing:
  /// - Successfully parsed accounts
  /// - List of invalid URIs
  /// - List of duplicate secrets (if any were found)
  static OtpAuthParseResult parse(String text) {
    final lines = text.split('\n');
    final accounts = <Map<String, dynamic>>[];
    final invalidUris = <String>[];
    final seenSecrets = <String>{};

    for (final line in lines) {
      // Trim whitespace
      final uri = line.trim();

      // Skip empty lines
      if (uri.isEmpty) {
        continue;
      }

      // Skip non-otpauth lines
      if (!uri.startsWith('otpauth://')) {
        invalidUris.add(uri);
        continue;
      }

      try {
        final parsed = OtpAuthUri.parse(uri);
        final secret = parsed['secret'] as String;

        // Check for duplicate secrets
        if (seenSecrets.contains(secret.toUpperCase())) {
          invalidUris.add(uri);
          continue;
        }

        seenSecrets.add(secret.toUpperCase());
        accounts.add(parsed);
      } catch (e) {
        // Invalid URI - skip it
        invalidUris.add(uri);
      }
    }

    return OtpAuthParseResult(
      accounts: accounts,
      invalidUris: invalidUris,
      duplicateSecrets: [],
    );
  }

  /// Parses multiple otpauth:// URIs and checks against existing accounts
  /// to detect duplicates.
  ///
  /// [existingSecrets] is a set of secrets that already exist in the storage.
  static OtpAuthParseResult parseWithExistingCheck(
    String text,
    Set<String> existingSecrets,
  ) {
    final result = parse(text);
    final duplicateSecrets = <String>[];
    final validAccounts = <Map<String, dynamic>>[];

    for (final account in result.accounts) {
      final secret = (account['secret'] as String).toUpperCase();
      if (existingSecrets.contains(secret)) {
        duplicateSecrets.add(secret);
      } else {
        validAccounts.add(account);
      }
    }

    return OtpAuthParseResult(
      accounts: validAccounts,
      invalidUris: result.invalidUris,
      duplicateSecrets: duplicateSecrets,
    );
  }
}
