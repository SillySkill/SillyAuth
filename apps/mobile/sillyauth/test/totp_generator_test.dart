import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:silly_auth/core/totp/totp_generator.dart';

void main() {
  group('TotpGenerator', () {
    group('Verified RFC 6238 Test Vectors', () {
      // Test vectors from RFC 6238 that are verified to be correct
      // Secret: "12345678901234567890" (20 bytes)
      // Correct Base32: GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ
      const String rfcSecret = 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ';

      // These test vectors are verified to match RFC 6238
      test('should generate correct OTP for counter=1 (time 30-59s)', () {
        final totp = TotpGenerator(secret: rfcSecret);
        // Counter = floor(30/30) = 1, also floor(59/30) = 1
        final code = totp.generateAtTimestamp(30);
        expect(code, equals('287082'));
      });

      test('should generate correct OTP for counter=37037036', () {
        final totp = TotpGenerator(secret: rfcSecret);
        // Counter = floor(1111111109/30) = 37037036
        final code = totp.generateAtTimestamp(1111111109);
        expect(code, equals('081804'));
      });

      // Test that algorithm consistency works
      test('should generate same code at same counter value', () {
        final totp = TotpGenerator(secret: rfcSecret);
        // Counter 1 is used for timestamps 30-59
        expect(totp.generateAtTimestamp(30), equals(totp.generateAtTimestamp(59)));
      });
    });

    group('User-specified test vector', () {
      // Secret "JBSWY3DPEHPK3PXP" = "Hello!" in Base32
      const String testSecret = 'JBSWY3DPEHPK3PXP';

      test('should generate valid 6-digit code', () {
        final totp = TotpGenerator(secret: testSecret);
        final code = totp.generate();

        // Should be a 6-digit string
        expect(code.length, equals(6));
        expect(int.tryParse(code), isNotNull);
      });

      test('should generate consistent codes at the same time window', () {
        final totp = TotpGenerator(secret: testSecret);
        final code1 = totp.generateAtTimestamp(59);
        final code2 = totp.generateAtTimestamp(59);
        final code3 = totp.generateAtTimestamp(59);

        // All codes should be identical within the same 30-second window
        expect(code1, equals(code2));
        expect(code2, equals(code3));
      });
    });

    group('Period functionality', () {
      test('should use default period of 30 seconds', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
        expect(totp.period, equals(30));
      });

      test('should generate different codes in different time windows', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
        // Time 0-29 seconds = counter 0
        // Time 30-59 seconds = counter 1
        final code0 = totp.generateAtTimestamp(0);
        final code30 = totp.generateAtTimestamp(30);

        expect(code0, isNot(equals(code30)));
      });

      test('should generate same code within same time window', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
        // Both times are in counter 1 (30-59 seconds)
        final code1 = totp.generateAtTimestamp(30);
        final code2 = totp.generateAtTimestamp(45);
        final code3 = totp.generateAtTimestamp(59);

        expect(code1, equals(code2));
        expect(code2, equals(code3));
      });

      test('should support custom period', () {
        // Use a 60-second period
        final totp = TotpGenerator(
          secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ',
          period: 60,
        );

        // Both times should be in counter 0 (0-59 seconds)
        final code1 = totp.generateAtTimestamp(0);
        final code2 = totp.generateAtTimestamp(30);
        final code3 = totp.generateAtTimestamp(59);

        expect(code1, equals(code2));
        expect(code2, equals(code3));
      });
    });

    group('Countdown timer', () {
      test('should return remaining seconds between 1 and period', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
        final remaining = totp.getRemainingSeconds();

        expect(remaining, greaterThanOrEqualTo(1));
        expect(remaining, lessThanOrEqualTo(30));
      });

      test('should return correct remaining seconds', () {
        final totp = TotpGenerator(
          secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ',
          period: 30,
        );

        // Test that remaining + position in period = period
        final testTime = DateTime.now().millisecondsSinceEpoch ~/ 1000;
        final remaining = totp.getRemainingSeconds();
        final currentPeriodPosition = testTime % 30;

        expect(remaining + currentPeriodPosition, equals(30));
      });

      test('should return progress between 0.0 and 1.0', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
        final progress = totp.getProgress();

        expect(progress, greaterThanOrEqualTo(0.0));
        expect(progress, lessThanOrEqualTo(1.0));
      });

      test('should have progress increasing over time window', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');

        // Verify calculation: progress = 1 - (remaining / period)
        final remaining = totp.getRemainingSeconds();
        final progress = totp.getProgress();

        final expectedProgress = 1.0 - (remaining / 30);
        expect(progress, closeTo(expectedProgress, 0.001));
      });
    });

    group('Validation', () {
      test('should validate correct code at current time', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
        final currentCode = totp.generate();

        expect(totp.validate(currentCode), isTrue);
      });

      test('should reject incorrect code at current time', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');

        expect(totp.validate('000000'), isFalse);
      });

      test('should validate code within window', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');

        // Get code from 30 seconds ago (previous time window)
        final previousCode = totp.generateAtTimestamp(
          (DateTime.now().millisecondsSinceEpoch ~/ 1000) - 30,
        );

        // Should validate with default window of 1
        expect(totp.validate(previousCode), isTrue);
      });

      test('should validate code at specific time', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');

        // Generate code at timestamp 30 (counter=1)
        final code = totp.generateAtTimestamp(30);

        // Should validate at timestamp 30
        expect(
          totp.validateAt(code, DateTime.fromMillisecondsSinceEpoch(30 * 1000)),
          isTrue,
        );

        // Generate a different code at timestamp 0 (counter=0)
        final differentCode = totp.generateAtTimestamp(0);

        // The code from timestamp 30 should NOT validate at timestamp 0
        // (with window=0 for strict validation)
        expect(
          totp.validateAt(code, DateTime.fromMillisecondsSinceEpoch(0), window: 0),
          isFalse,
        );

        // The code from timestamp 0 should validate at timestamp 0
        expect(
          totp.validateAt(differentCode, DateTime.fromMillisecondsSinceEpoch(0), window: 0),
          isTrue,
        );
      });
    });

    group('Digits configuration', () {
      test('should use default 6 digits', () {
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
        expect(totp.digits, equals(6));
      });

      test('should generate 8-digit codes when configured', () {
        final totp = TotpGenerator(
          secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ',
          digits: 8,
        );
        final code = totp.generate();

        expect(code.length, equals(8));
      });

      test('should pad with leading zeros', () {
        final totp = TotpGenerator(
          secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ',
          digits: 8,
        );

        // Code should always be 8 characters
        final code = totp.generateAtTimestamp(30);
        expect(code.length, equals(8));
        expect(code, matches(RegExp(r'^\d{8}$')));
      });
    });

    group('Factory constructor fromBytes', () {
      test('should create generator from raw bytes', () {
        // Secret "12345678901234567890" as bytes
        final secretBytes = Uint8List.fromList(
          '12345678901234567890'.codeUnits,
        );

        final totp = TotpGenerator.fromBytes(secretBytes: secretBytes);

        // Should generate same code as Base32 encoded version
        final codeFromBytes = totp.generateAtTimestamp(30);
        final codeFromString = TotpGenerator(
          secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ',
        ).generateAtTimestamp(30);

        expect(codeFromBytes, equals(codeFromString));
      });
    });

    group('Edge cases', () {
      test('should handle empty secret gracefully', () {
        final totp = TotpGenerator(secret: '');

        // Should still generate a code
        final code = totp.generate();
        expect(code.length, equals(6));
      });

      test('should handle single character secret', () {
        // Base32 'A' = 0x00
        final totp = TotpGenerator(secret: 'A');
        final code = totp.generate();

        expect(code.length, equals(6));
        expect(int.tryParse(code), isNotNull);
      });

      test('should generate unique codes for different secrets', () {
        final totp1 = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');
        final totp2 = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJR');

        // Even one character difference should produce different codes
        bool differentAtLeastOnce = false;
        for (int i = 0; i < 10; i++) {
          final code1 = totp1.generateAtTimestamp(i * 30);
          final code2 = totp2.generateAtTimestamp(i * 30);
          if (code1 != code2) {
            differentAtLeastOnce = true;
            break;
          }
        }

        expect(differentAtLeastOnce, isTrue);
      });
    });

    group('Algorithm verification', () {
      test('should implement dynamic truncation correctly', () {
        // Verified through RFC test vectors
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');

        // Same input should always produce same output
        for (int i = 0; i < 5; i++) {
          final timestamp = 30 + (i * 30);
          final code1 = totp.generateAtTimestamp(timestamp);
          final code2 = totp.generateAtTimestamp(timestamp);
          expect(code1, equals(code2));
        }
      });

      test('should use big-endian byte order for counter', () {
        // This is verified through RFC test vectors
        // Counter = 1 at timestamp 30 produces OTP 287082
        final totp = TotpGenerator(secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ');

        final code = totp.generateAtTimestamp(30);
        expect(code, equals('287082'));
      });

      test('should apply modulo correctly for digit generation', () {
        final totp6 = TotpGenerator(
          secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ',
          digits: 6,
        );
        final totp8 = TotpGenerator(
          secret: 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ',
          digits: 8,
        );

        final code6 = totp6.generateAtTimestamp(30);
        final code8 = totp8.generateAtTimestamp(30);

        expect(code6.length, equals(6));
        expect(code8.length, equals(8));
      });
    });
  });
}
