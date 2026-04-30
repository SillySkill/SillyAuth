import 'package:flutter/material.dart';

import '../../l10n/app_localizations.dart';
import 'screens/scan_qr_screen.dart';
import 'screens/manual_input_screen.dart';
import 'screens/import_from_file_screen.dart';

/// Add Account Screen with three tabs:
///
/// 1. Scan QR Code - Uses camera to scan TOTP QR code
/// 2. Manual Input - Form to enter account details manually
/// 3. Import from File - Import accounts from a text file
class AddAccountScreen extends StatelessWidget {
  const AddAccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text(l10n.addAccount),
          bottom: TabBar(
            tabs: [
              Tab(
                icon: const Icon(Icons.qr_code_scanner),
                text: l10n.scanQrcode,
              ),
              Tab(
                icon: const Icon(Icons.edit),
                text: l10n.manualInput,
              ),
              Tab(
                icon: const Icon(Icons.file_upload_outlined),
                text: l10n.importFromFile,
              ),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            ScanQrScreen(),
            ManualInputScreen(),
            ImportFromFileScreen(),
          ],
        ),
      ),
    );
  }
}
