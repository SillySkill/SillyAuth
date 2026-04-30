/// URI parsing utilities for otpauth:// format
///
/// This module provides functions to parse and extract information
/// from TOTP QR code URIs in the otpauth:// format.
class OtpAuthUri {
  /// Parses an otpauth:// URI and extracts TOTP parameters.
  ///
  /// Format: otpauth://totp/Issuer:AccountName?secret=SECRET&issuer=Issuer&algorithm=SHA1&digits=6&period=30
  ///
  /// Returns a map with the following keys:
  /// - type: 'totp' or 'hotp'
  /// - label: the full label (issuer:name)
  /// - issuer: the issuer name
  /// - name: the account name
  /// - secret: the Base32 secret
  /// - algorithm: SHA1, SHA256, or SHA512 (defaults to SHA1)
  /// - digits: number of digits (defaults to 6)
  /// - period: time period in seconds (defaults to 30)
  ///
  /// Throws [FormatException] if the URI is invalid.
  static Map<String, dynamic> parse(String uri) {
    if (!uri.startsWith('otpauth://')) {
      throw FormatException('Invalid otpauth URI: must start with otpauth://');
    }

    final parsedUri = Uri.parse(uri);

    if (parsedUri.host != 'totp' && parsedUri.host != 'hotp') {
      throw FormatException('Invalid otpauth URI: must be totp or hotp type');
    }

    final type = parsedUri.host;
    final path = parsedUri.path;

    // Remove leading slash
    String label = path.startsWith('/') ? path.substring(1) : path;

    // Decode the label (URL encoded)
    label = Uri.decodeComponent(label);

    // Extract issuer and name from label (format: "Issuer:Name" or just "Name")
    String issuer = '';
    String name = label;

    if (label.contains(':')) {
      final parts = label.split(':');
      issuer = parts[0].trim();
      name = parts.sublist(1).join(':').trim();
    }

    // Parse query parameters
    final params = parsedUri.queryParameters;

    // Get secret (required)
    final secret = params['secret'];
    if (secret == null || secret.isEmpty) {
      throw FormatException('Invalid otpauth URI: secret is required');
    }

    // Get issuer from query param if not in label
    if (issuer.isEmpty && params['issuer'] != null) {
      issuer = params['issuer']!;
    }

    // Get optional parameters with defaults
    final algorithm = params['algorithm']?.toUpperCase() ?? 'SHA1';
    final digits = int.tryParse(params['digits'] ?? '6') ?? 6;
    final period = int.tryParse(params['period'] ?? '30') ?? 30;

    return {
      'type': type,
      'label': label,
      'issuer': issuer,
      'name': name,
      'secret': secret.toUpperCase().replaceAll(' ', ''),
      'algorithm': algorithm,
      'digits': digits,
      'period': period,
    };
  }

  /// Validates if a string is a valid otpauth:// URI
  static bool isValid(String uri) {
    try {
      parse(uri);
      return true;
    } catch (e) {
      return false;
    }
  }
}
