import 'package:flutter/material.dart';

/// App color constants matching the Silly.png icon
///
/// The icon features:
/// - Deep blue background (#1a237e)
/// - Gold/yellow stars (#FFD700)
/// - White "Silly" text
/// - Light blue "Auth" text (#87CEEB)
class AppColors {
  AppColors._();

  // Primary colors - Deep blue from icon background
  static const Color primaryDeepBlue = Color(0xFF1a237e);
  static const Color primaryLight = Color(0xFF534bae);
  static const Color primaryDark = Color(0xFF000051);

  // Secondary/Accent colors - Gold from stars
  static const Color gold = Color(0xFFFFD700);
  static const Color goldLight = Color(0xFFFFE44D);
  static const Color goldDark = Color(0xFFC7A600);

  // Light blue for "Auth" text
  static const Color lightBlue = Color(0xFF87CEEB);
  static const Color lightBlueLight = Color(0xFFBFFFFF);
  static const Color lightBlueDark = Color(0xFF5DADE2);

  // Background colors
  static const Color backgroundLight = Color(0xFFF5F5F5);
  static const Color backgroundDark = Color(0xFF121212);
  static const Color surfaceLight = Color(0xFFFFFFFF);
  static const Color surfaceDark = Color(0xFF1E1E1E);

  // Card/Surface variants
  static const Color cardLight = Color(0xFFFFFFFF);
  static const Color cardDark = Color(0xFF2D2D2D);

  // Text colors
  static const Color textPrimaryLight = Color(0xFF212121);
  static const Color textSecondaryLight = Color(0xFF757575);
  static const Color textPrimaryDark = Color(0xFFFFFFFF);
  static const Color textSecondaryDark = Color(0xFFB0B0B0);

  // Text on primary colors (for contrast)
  static const Color textOnPrimary = Color(0xFFFFFFFF);
  static const Color textOnSecondary = Color(0xFF000000);

  // Error/Success/Warning colors
  static const Color error = Color(0xFFD32F2F);
  static const Color errorLight = Color(0xFFEF5350);
  static const Color success = Color(0xFF388E3C);
  static const Color successLight = Color(0xFF66BB6A);
  static const Color warning = Color(0xFFF57C00);
  static const Color warningLight = Color(0xFFFFB74D);

  // Divider colors
  static const Color dividerLight = Color(0xFFE0E0E0);
  static const Color dividerDark = Color(0xFF424242);

  // App-specific colors
  static const Color starColor = gold;
  static const Color sillyTextColor = textOnPrimary;
  static const Color authTextColor = lightBlue;
}
