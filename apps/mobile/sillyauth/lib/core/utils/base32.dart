import 'dart:typed_data';

/// Base32 encoding and decoding utility class.
///
/// Provides methods to encode and decode data using the standard Base32 alphabet
/// (RFC 4648), which uses uppercase letters A-Z and digits 2-7.
class Base32 {
  /// The standard Base32 alphabet as defined in RFC 4648.
  static const String _alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';

  /// Padding character used for Base32 encoding.
  static const String _padding = '=';

  /// Lookup table for decoding Base32 characters to integers (0-31).
  static final List<int> _decodeTable = List<int>.generate(128, (index) {
    final char = String.fromCharCode(index).toUpperCase();
    final pos = _alphabet.indexOf(char);
    return pos != -1 ? pos : -1;
  });

  /// Private constructor to prevent instantiation.
  Base32._();

  /// Encodes bytes to a Base32 string.
  ///
  /// Takes a [Uint8List] of data and returns a Base32-encoded string.
  /// The output is padded with '=' characters to make the length a multiple of 8.
  ///
  /// Example:
  /// ```dart
  /// final bytes = Uint8List.fromList([0x66, 0x6f, 0x6f]); // "foo"
  /// final encoded = Base32.encode(bytes); // "MZXW6==="
  /// ```
  static String encode(Uint8List data) {
    if (data.isEmpty) {
      return '';
    }

    final buffer = StringBuffer();
    int value = 0;
    int bitsCount = 0;

    for (final byte in data) {
      value = (value << 8) | byte;
      bitsCount += 8;

      while (bitsCount >= 5) {
        bitsCount -= 5;
        final index = (value >> bitsCount) & 0x1F;
        buffer.write(_alphabet[index]);
      }
    }

    // Handle remaining bits
    if (bitsCount > 0) {
      final index = (value << (5 - bitsCount)) & 0x1F;
      buffer.write(_alphabet[index]);
    }

    // Add padding
    final remainder = buffer.length % 8;
    if (remainder != 0) {
      final paddingNeeded = 8 - remainder;
      for (int i = 0; i < paddingNeeded; i++) {
        buffer.write(_padding);
      }
    }

    return buffer.toString();
  }

  /// Decodes a Base32 string to bytes.
  ///
  /// Takes a Base32-encoded [String] and returns the decoded [Uint8List].
  /// Padding characters ('=') are optional and ignored during decoding.
  ///
  /// Throws [FormatException] if the input contains invalid Base32 characters.
  ///
  /// Example:
  /// ```dart
  /// final decoded = Base32.decode('MZXW6==='); // Uint8List([0x66, 0x6f, 0x6f])
  /// ```
  static Uint8List decode(String input) {
    // Remove padding and whitespace
    final cleanedInput = input
        .toUpperCase()
        .replaceAll(_padding, '')
        .replaceAll(' ', '')
        .trim();

    if (cleanedInput.isEmpty) {
      return Uint8List(0);
    }

    // Validate input characters
    for (int i = 0; i < cleanedInput.length; i++) {
      final charCode = cleanedInput.codeUnitAt(i);
      if (charCode >= 128 || _decodeTable[charCode] == -1) {
        throw FormatException(
          'Invalid Base32 character "${cleanedInput[i]}" at position $i',
        );
      }
    }

    final buffer = BytesBuilder();
    int bits = 0;
    int value = 0;

    for (int i = 0; i < cleanedInput.length; i++) {
      final charCode = cleanedInput.codeUnitAt(i);
      final decodedValue = _decodeTable[charCode];

      value = (value << 5) | decodedValue;
      bits += 5;

      if (bits >= 8) {
        bits -= 8;
        final byte = (value >> bits) & 0xFF;
        buffer.addByte(byte);
      }
    }

    return buffer.toBytes();
  }

  /// Validates if a string is a valid Base32 encoded string.
  ///
  /// Returns true if the string contains only valid Base32 characters
  /// (A-Z, 2-7) and optional padding characters.
  ///
  /// Example:
  /// ```dart
  /// Base32.isValid('JBSWY3DPEHPK3PXP'); // true
  /// Base32.isValid('invalid!'); // false
  /// ```
  static bool isValid(String input) {
    if (input.isEmpty) {
      return true;
    }

    final cleanedInput = input.toUpperCase().replaceAll(_padding, '');

    for (int i = 0; i < cleanedInput.length; i++) {
      final charCode = cleanedInput.codeUnitAt(i);
      if (charCode >= 128 || _decodeTable[charCode] == -1) {
        return false;
      }
    }

    return true;
  }

  /// Cleans a Base32 string by removing padding and converting to uppercase.
  ///
  /// Useful for normalizing secret keys before storage or use.
  ///
  /// Example:
  /// ```dart
  /// Base32.clean('jbswy3dpehpk3pxp='); // "JBSWY3DPEHPK3PXP"
  /// ```
  static String clean(String input) {
    return input
        .toUpperCase()
        .replaceAll(_padding, '')
        .trim();
  }
}
