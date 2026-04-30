import 'package:uuid/uuid.dart';

/// Data model representing a TOTP (Time-based One-Time Password) account.
///
/// This class stores all the information needed to generate and verify
/// one-time passwords for two-factor authentication.
class AuthAccount {
  /// Unique identifier for the account (UUID format).
  final String id;

  /// Display name for the account (e.g., user@example.com).
  final String name;

  /// Issuer name (e.g., Google, GitHub, Amazon).
  final String issuer;

  /// Base32 encoded secret key for TOTP generation.
  final String secret;

  /// Number of digits in the generated code (default: 6).
  final int digits;

  /// Time period in seconds for each code (default: 30).
  final int period;

  /// Sort order for display purposes.
  final int sortOrder;

  /// Timestamp when the account was created.
  final DateTime createdAt;

  /// Creates a new AuthAccount with the specified parameters.
  ///
  /// If [id] is not provided, a new UUID will be generated.
  /// Default values are used for [digits] (6) and [period] (30).
  AuthAccount({
    String? id,
    required this.name,
    required this.issuer,
    required this.secret,
    this.digits = 6,
    this.period = 30,
    this.sortOrder = 0,
    DateTime? createdAt,
  })  : id = id ?? const Uuid().v4(),
        createdAt = createdAt ?? DateTime.now();

  /// Creates an AuthAccount from a JSON map.
  ///
  /// This factory constructor is used when loading accounts from storage.
  factory AuthAccount.fromJson(Map<String, dynamic> json) {
    return AuthAccount(
      id: json['id'] as String,
      name: json['name'] as String,
      issuer: json['issuer'] as String,
      secret: json['secret'] as String,
      digits: json['digits'] as int? ?? 6,
      period: json['period'] as int? ?? 30,
      sortOrder: json['sortOrder'] as int? ?? 0,
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'] as String)
          : DateTime.now(),
    );
  }

  /// Converts the AuthAccount to a JSON map.
  ///
  /// This method is used when saving accounts to storage.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'issuer': issuer,
      'secret': secret,
      'digits': digits,
      'period': period,
      'sortOrder': sortOrder,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  /// Creates a copy of this AuthAccount with the specified changes.
  ///
  /// This is useful for updating specific fields while preserving others.
  AuthAccount copyWith({
    String? id,
    String? name,
    String? issuer,
    String? secret,
    int? digits,
    int? period,
    int? sortOrder,
    DateTime? createdAt,
  }) {
    return AuthAccount(
      id: id ?? this.id,
      name: name ?? this.name,
      issuer: issuer ?? this.issuer,
      secret: secret ?? this.secret,
      digits: digits ?? this.digits,
      period: period ?? this.period,
      sortOrder: sortOrder ?? this.sortOrder,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AuthAccount && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'AuthAccount(id: $id, name: $name, issuer: $issuer)';
  }
}
