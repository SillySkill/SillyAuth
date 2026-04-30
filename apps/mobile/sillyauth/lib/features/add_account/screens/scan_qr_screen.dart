import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:provider/provider.dart';

import '../../../core/utils/otpauth_uri.dart';
import '../../../data/models/auth_account.dart';
import '../../../data/repositories/account_repository.dart';
import '../../../l10n/app_localizations.dart';

/// QR Code Scanner Screen
///
/// Uses mobile_scanner package to scan TOTP QR codes,
/// parses the otpauth:// URI format, and saves the account.
class ScanQrScreen extends StatefulWidget {
  const ScanQrScreen({super.key});

  @override
  State<ScanQrScreen> createState() => _ScanQrScreenState();
}

class _ScanQrScreenState extends State<ScanQrScreen> {
  final MobileScannerController _scannerController = MobileScannerController(
    detectionSpeed: DetectionSpeed.normal,
    facing: CameraFacing.back,
    torchEnabled: false,
  );

  bool _isProcessing = false;
  bool _hasPermission = false;
  bool _permissionDenied = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _checkPermission();
  }

  @override
  void dispose() {
    _scannerController.dispose();
    super.dispose();
  }

  /// Check camera permission status
  Future<void> _checkPermission() async {
    final status = await Permission.camera.status;

    if (status.isGranted) {
      setState(() {
        _hasPermission = true;
        _permissionDenied = false;
      });
    } else if (status.isDenied) {
      final result = await Permission.camera.request();
      setState(() {
        _hasPermission = result.isGranted;
        _permissionDenied = result.isDenied;
      });
    } else if (status.isPermanentlyDenied) {
      setState(() {
        _hasPermission = false;
        _permissionDenied = true;
      });
    }
  }

  /// Handle QR code detection
  Future<void> _onDetect(BarcodeCapture capture) async {
    // Prevent multiple simultaneous processing
    if (_isProcessing) return;

    final List<Barcode> barcodes = capture.barcodes;

    for (final barcode in barcodes) {
      final String? rawValue = barcode.rawValue;

      if (rawValue == null || !rawValue.startsWith('otpauth://')) {
        continue;
      }

      setState(() {
        _isProcessing = true;
        _errorMessage = null;
      });

      try {
        // Parse the otpauth URI
        final Map<String, dynamic> params = OtpAuthUri.parse(rawValue);

        // Validate it's a TOTP (we don't support HOTP yet)
        if (params['type'] != 'totp') {
          final l10n = AppLocalizations.of(context)!;
          setState(() {
            _errorMessage = l10n.onlyTotpSupported;
            _isProcessing = false;
          });
          return;
        }

        // Create the AuthAccount
        final account = AuthAccount(
          name: params['name'] as String,
          issuer: params['issuer'] as String? ?? '',
          secret: params['secret'] as String,
          digits: params['digits'] as int? ?? 6,
          period: params['period'] as int? ?? 30,
        );

        // Save to repository
        final repository = context.read<AccountRepository>();
        await repository.addAccount(account);

        // Show success and navigate back
        if (mounted) {
          final l10n = AppLocalizations.of(context)!;
          final accountName = account.issuer.isNotEmpty ? account.issuer : account.name;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.accountAdded(accountName)),
              backgroundColor: Theme.of(context).colorScheme.primary,
            ),
          );
          Navigator.of(context).pop(true);
        }

        return;
      } catch (e) {
        if (!mounted) return;
        final l10n = AppLocalizations.of(context)!;
        setState(() {
          _errorMessage = '${l10n.invalidQrcodeFormat}: ${e.toString()}';
          _isProcessing = false;
        });
      }
    }
  }

  /// Request camera permission
  Future<void> _requestPermission() async {
    final result = await Permission.camera.request();
    setState(() {
      _hasPermission = result.isGranted;
      _permissionDenied = result.isPermanentlyDenied;
    });

    if (result.isPermanentlyDenied) {
      // Open app settings
      await openAppSettings();
    }
  }

  /// Toggle flashlight
  void _toggleTorch() {
    _scannerController.toggleTorch();
  }

  /// Switch camera
  void _switchCamera() {
    _scannerController.switchCamera();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    // Permission denied UI
    if (_permissionDenied || !_hasPermission) {
      return _buildPermissionDeniedUI();
    }

    return Column(
      children: [
        Expanded(
          flex: 3,
          child: Stack(
            children: [
              // Camera preview
              MobileScanner(
                controller: _scannerController,
                onDetect: _onDetect,
                errorBuilder: (context, error, child) {
                  return _buildCameraErrorUI(error.errorCode.name);
                },
              ),

              // Scanning overlay
              _buildScanningOverlay(),

              // Processing indicator
              if (_isProcessing)
                Container(
                  color: Colors.black54,
                  child: const Center(
                    child: CircularProgressIndicator(),
                  ),
                ),
            ],
          ),
        ),

        // Bottom controls
        Container(
          padding: const EdgeInsets.all(16),
          color: Theme.of(context).colorScheme.surface,
          child: Column(
            children: [
              // Instructions
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(
                  l10n.scanQrcodeInstructions,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),

              // Error message
              if (_errorMessage != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.errorContainer,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.error_outline,
                        color: Theme.of(context).colorScheme.error,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

              // Control buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  IconButton.filled(
                    onPressed: _toggleTorch,
                    icon: const Icon(Icons.flash_on),
                    tooltip: l10n.toggleFlashlight,
                  ),
                  IconButton.filled(
                    onPressed: _switchCamera,
                    icon: const Icon(Icons.cameraswitch),
                    tooltip: l10n.switchCamera,
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildScanningOverlay() {
    return CustomPaint(
      painter: ScannerOverlayPainter(
        borderColor: Theme.of(context).colorScheme.primary,
        backgroundColor: Colors.black54,
        borderLength: 40,
        borderWidth: 4,
        cornerRadius: 12,
      ),
      child: const SizedBox.expand(),
    );
  }

  Widget _buildPermissionDeniedUI() {
    final l10n = AppLocalizations.of(context)!;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.camera_alt_outlined,
              size: 80,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(height: 24),
            Text(
              l10n.cameraPermissionRequired,
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              l10n.cameraPermissionDesc,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            ElevatedButton.icon(
              onPressed: _requestPermission,
              icon: const Icon(Icons.camera),
              label: Text(l10n.grantPermission),
            ),
            if (_permissionDenied) ...[
              const SizedBox(height: 16),
              TextButton(
                onPressed: () => openAppSettings(),
                child: Text(l10n.openSettings),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildCameraErrorUI(String error) {
    final l10n = AppLocalizations.of(context)!;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 80,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 24),
            Text(
              l10n.cameraError,
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              error,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            ElevatedButton.icon(
              onPressed: () {
                _scannerController.start();
              },
              icon: const Icon(Icons.refresh),
              label: Text(l10n.retry),
            ),
          ],
        ),
      ),
    );
  }
}

/// Custom painter for scanner overlay
class ScannerOverlayPainter extends CustomPainter {
  final Color borderColor;
  final Color backgroundColor;
  final double borderLength;
  final double borderWidth;
  final double cornerRadius;

  ScannerOverlayPainter({
    required this.borderColor,
    required this.backgroundColor,
    required this.borderLength,
    required this.borderWidth,
    required this.cornerRadius,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final double scanAreaWidth = size.width * 0.7;
    final double scanAreaHeight = scanAreaWidth;
    final double left = (size.width - scanAreaWidth) / 2;
    final double top = (size.height - scanAreaHeight) / 2;

    // Draw semi-transparent background
    final backgroundPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.fill;

    // Create scanner area rect
    final scanRect = RRect.fromRectAndRadius(
      Rect.fromLTWH(left, top, scanAreaWidth, scanAreaHeight),
      Radius.circular(cornerRadius),
    );

    // Draw background with hole
    final path = Path()
      ..addRect(Rect.fromLTWH(0, 0, size.width, size.height))
      ..addRRect(scanRect);
    path.fillType = PathFillType.evenOdd;

    canvas.drawPath(path, backgroundPaint);

    // Draw border corners
    final borderPaint = Paint()
      ..color = borderColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = borderWidth
      ..strokeCap = StrokeCap.round;

    // Top-left corner
    canvas.drawLine(
      Offset(left, top + borderLength),
      Offset(left, top + cornerRadius),
      borderPaint,
    );
    canvas.drawLine(
      Offset(left, top + cornerRadius),
      Offset(left + cornerRadius, top),
      borderPaint,
    );
    canvas.drawLine(
      Offset(left + cornerRadius, top),
      Offset(left + borderLength, top),
      borderPaint,
    );

    // Top-right corner
    canvas.drawLine(
      Offset(left + scanAreaWidth - borderLength, top),
      Offset(left + scanAreaWidth - cornerRadius, top),
      borderPaint,
    );
    canvas.drawLine(
      Offset(left + scanAreaWidth - cornerRadius, top),
      Offset(left + scanAreaWidth, top + cornerRadius),
      borderPaint,
    );
    canvas.drawLine(
      Offset(left + scanAreaWidth, top + cornerRadius),
      Offset(left + scanAreaWidth, top + borderLength),
      borderPaint,
    );

    // Bottom-left corner
    canvas.drawLine(
      Offset(left, top + scanAreaHeight - borderLength),
      Offset(left, top + scanAreaHeight - cornerRadius),
      borderPaint,
    );
    canvas.drawLine(
      Offset(left, top + scanAreaHeight - cornerRadius),
      Offset(left + cornerRadius, top + scanAreaHeight),
      borderPaint,
    );
    canvas.drawLine(
      Offset(left + cornerRadius, top + scanAreaHeight),
      Offset(left + borderLength, top + scanAreaHeight),
      borderPaint,
    );

    // Bottom-right corner
    canvas.drawLine(
      Offset(left + scanAreaWidth - borderLength, top + scanAreaHeight),
      Offset(left + scanAreaWidth - cornerRadius, top + scanAreaHeight),
      borderPaint,
    );
    canvas.drawLine(
      Offset(left + scanAreaWidth - cornerRadius, top + scanAreaHeight),
      Offset(left + scanAreaWidth, top + scanAreaHeight - cornerRadius),
      borderPaint,
    );
    canvas.drawLine(
      Offset(left + scanAreaWidth, top + scanAreaHeight - cornerRadius),
      Offset(left + scanAreaWidth, top + scanAreaHeight - borderLength),
      borderPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
