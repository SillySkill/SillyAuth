import 'dart:typed_data';

import 'package:crypto/crypto.dart';

import '../utils/base32.dart';

/// TOTP (Time-based One-Time Password) generator.
///
/// Implements the TOTP algorithm as specified in RFC 6238.
/// Generates time-based one-time passwords compatible with Google Authenticator
/// and other TOTP-based authentication apps.
class TotpGenerator {
  /// Default time step in seconds (30 seconds as per spec).
  static const int defaultPeriod = 30;

  /// Default number of digits for the OTP (6 digits as per spec).
  static const int defaultDigits = 6;

  /// The secret key (Base32 encoded).
  final String secret;

  /// Time step in seconds (default: 30).
  final int period;

  /// Number of digits in the generated OTP (default: 6).
  final int digits;

  /// The secret key decoded as bytes.
  Uint8List? _secretBytes;

  /// Creates a new TOTP generator with the given secret key.
  ///
  /// The [secret] should be a Base32-encoded string. Additional parameters:
  /// - [period]: Time step in seconds (default: 30)
  /// - [digits]: Number of digits in the OTP (default: 6)
  ///
  /// Example:
  /// ```dart
  /// final totp = TotpGenerator('JBSWY3DPEHPK3PXP');
  /// final code = totp.generate();
  /// ```
  TotpGenerator({
    required this.secret,
    this.period = defaultPeriod,
    this.digits = defaultDigits,
  }) {
    _secretBytes = Base32.decode(secret);
  }

  /// Creates a TOTP generator from raw secret bytes.
  ///
  /// Takes raw [secretBytes] instead of a Base32-encoded string.
  factory TotpGenerator.fromBytes({
    required Uint8List secretBytes,
    int period = defaultPeriod,
    int digits = defaultDigits,
  }) {
    final generator = TotpGenerator(
      secret: Base32.encode(secretBytes),
      period: period,
      digits: digits,
    );
    generator._secretBytes = secretBytes;
    return generator;
  }

  /// Generates a TOTP code for the current time.
  ///
  /// Returns a string of [digits] length, zero-padded if necessary.
  ///
  /// Example:
  /// ```dart
  /// final totp = TotpGenerator(secret: 'JBSWY3DPEHPK3PXP');
  /// final code = totp.generate(); // e.g., "123456"
  /// ```
  String generate() {
    return generateAt(DateTime.now());
  }

  /// Generates a TOTP code for a specific time.
  ///
  /// Takes a [DateTime] and returns the OTP for that moment.
  ///
  /// Example:
  /// ```dart
  /// final totp = TotpGenerator(secret: 'JBSWY3DPEHPK3PXP');
  /// final code = totp.generateAt(DateTime(2024, 1, 1, 0, 0, 0));
  /// ```
  String generateAt(DateTime time) {
    final counter = _getCounterForTime(time);
    return _generateCode(counter);
  }

  /// Generates a TOTP code for a specific Unix timestamp.
  ///
  /// Takes a Unix timestamp in [seconds] and returns the OTP.
  ///
  /// Example:
  /// ```dart
  /// final totp = TotpGenerator(secret: 'JBSWY3DPEHPK3PXP');
  /// final code = totp.generateAtTimestamp(1704067200);
  /// ```
  String generateAtTimestamp(int seconds) {
    final counter = seconds ~/ period;
    return _generateCode(counter);
  }

  /// Gets the time step counter for a given time.
  ///
  /// Calculates: counter = floor(unix_timestamp / period)
  int _getCounterForTime(DateTime time) {
    final unixTimestamp = time.millisecondsSinceEpoch ~/ 1000;
    return unixTimestamp ~/ period;
  }

  /// Generates the TOTP code for a given counter value.
  ///
  /// Implements the TOTP algorithm:
  /// 1. Convert counter to 8-byte big-endian
  /// 2. Compute HMAC-SHA1(secret, counter)
  /// 3. Get dynamic truncation from the hash
  /// 4. Convert to integer and take modulo 10^digits
  String _generateCode(int counter) {
    // Convert counter to 8-byte big-endian
    final counterBytes = _intToBytes(counter);

    // Compute HMAC-SHA1
    final hmac = Hmac(sha1, _secretBytes!);
    final hash = hmac.convert(counterBytes).bytes;

    // Dynamic truncation
    final offset = hash[hash.length - 1] & 0x0F;
    final binary = ((hash[offset] & 0x7F) << 24) |
        ((hash[offset + 1] & 0xFF) << 16) |
        ((hash[offset + 2] & 0xFF) << 8) |
        (hash[offset + 3] & 0xFF);

    // Generate otp with modulo
    final otp = binary % _pow10(digits);

    // Pad with leading zeros if necessary
    return otp.toString().padLeft(digits, '0');
  }

  /// Converts an integer to an 8-byte big-endian byte array.
  Uint8List _intToBytes(int value) {
    final bytes = Uint8List(8);
    for (int i = 7; i >= 0; i--) {
      bytes[i] = value & 0xFF;
      value >>= 8;
    }
    return bytes;
  }

  /// Calculates 10 raised to the power of [exponent].
  int _pow10(int exponent) {
    int result = 1;
    for (int i = 0; i < exponent; i++) {
      result *= 10;
    }
    return result;
  }

  /// Gets the remaining seconds until the next time step.
  ///
  /// Returns a value between 0 and [period]-1.
  ///
  /// Example:
  /// ```dart
  /// final totp = TotpGenerator(secret: 'JBSWY3DPEHPK3PXP');
  /// final remaining = totp.getRemainingSeconds(); // e.g., 25
  /// ```
  int getRemainingSeconds() {
    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    return period - (now % period);
  }

  /// Gets the progress (0.0 to 1.0) through the current time step.
  ///
  /// Example:
  /// ```dart
  /// final totp = TotpGenerator(secret: 'JBSWY3DPEHPK3PXP');
  /// final progress = totp.getProgress(); // e.g., 0.17
  /// ```
  double getProgress() {
    final remaining = getRemainingSeconds();
    return 1.0 - (remaining / period);
  }

  /// Validates a TOTP code against the current time.
  ///
  /// Takes a [code] string and validates it against the current time.
  /// Optionally accepts a [window] parameter to allow for clock drift
  /// (checks codes at [current_time - window * period, current_time + window * period]).
  ///
  /// Example:
  /// ```dart
  /// final totp = TotpGenerator(secret: 'JBSWY3DPEHPK3PXP');
  /// final isValid = totp.validate('123456'); // true or false
  /// ```
  bool validate(String code, {int window = 1}) {
    return validateAt(code, DateTime.now(), window: window);
  }

  /// Validates a TOTP code against a specific time.
  ///
  /// Takes a [code] string and validates it against a specific [time].
  /// Optionally accepts a [window] parameter to allow for clock drift.
  bool validateAt(String code, DateTime time, {int window = 1}) {
    final targetCounter = _getCounterForTime(time);

    for (int i = -window; i <= window; i++) {
      final counter = targetCounter + i;
      final expectedCode = _generateCode(counter);
      if (expectedCode == code) {
        return true;
      }
    }

    return false;
  }

  @override
  String toString() {
    return 'TotpGenerator(secret: ***, period: $period, digits: $digits)';
  }
}
