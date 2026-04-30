// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Chinese (`zh`).
class AppLocalizationsZh extends AppLocalizations {
  AppLocalizationsZh([String locale = 'zh']) : super(locale);

  @override
  String get appName => '傻小码';

  @override
  String get addAccount => '添加账户';

  @override
  String get scanQrcode => '扫描二维码';

  @override
  String get manualInput => '手动输入';

  @override
  String get accountName => '账户名称';

  @override
  String get secretKey => '密钥';

  @override
  String get issuer => '发行方';

  @override
  String get delete => '删除';

  @override
  String get edit => '编辑';

  @override
  String get cancel => '取消';

  @override
  String get save => '保存';

  @override
  String get copied => '已复制';

  @override
  String get settings => '设置';

  @override
  String get appLock => '应用锁';

  @override
  String get biometric => '生物识别';

  @override
  String get theme => '主题';

  @override
  String get light => '浅色';

  @override
  String get dark => '深色';

  @override
  String get system => '跟随系统';

  @override
  String get about => '关于';

  @override
  String get version => '版本';

  @override
  String get noAccounts => '暂无账户';

  @override
  String get deleteConfirm => '确定删除此账户？';

  @override
  String get invalidQrcode => '无效二维码';

  @override
  String get invalidSecret => '无效密钥';

  @override
  String get search => '搜索';

  @override
  String get searchAccounts => '搜索账户...';

  @override
  String get noSearchResults => '未找到结果';

  @override
  String get noSearchResultsHint => '请尝试其他搜索词';

  @override
  String get importAccount => '导入账户';

  @override
  String get security => '安全';

  @override
  String get appearance => '外观';

  @override
  String get language => '语言';

  @override
  String get info => '信息';

  @override
  String get appLockSubtitle => '打开应用时需要验证';

  @override
  String get biometricSubtitle => '使用指纹或面容解锁';

  @override
  String get biometricUnavailable => '此设备不支持生物识别';

  @override
  String get themeLight => '始终使用浅色主题';

  @override
  String get themeDark => '始终使用深色主题';

  @override
  String get themeSystem => '跟随系统设置';

  @override
  String get retry => '重试';

  @override
  String get deleteAccount => '删除账户';

  @override
  String confirmDelete(String accountName) {
    return '确定删除 $accountName？';
  }

  @override
  String get codeCopied => '验证码已复制到剪贴板';

  @override
  String accountAdded(String accountName) {
    return '账户 \"$accountName\" 添加成功';
  }

  @override
  String get errorAddingAccount => '添加账户时出错';

  @override
  String get secretRequired => '密钥不能为空';

  @override
  String get secretInvalid => '无效的Base32格式，只能使用A-Z和2-7';

  @override
  String get secretTooShort => '密钥至少需要16个字符';

  @override
  String get accountNameRequired => '账户名称不能为空';

  @override
  String get addingAccount => '正在添加账户...';

  @override
  String get enterAccountDetails => '输入账户详情';

  @override
  String get enterAccountInfo => '手动输入您的账户信息';

  @override
  String get accountNameHint => '例如：user@example.com';

  @override
  String get accountNameHelper => '账户标识符（通常是您的邮箱）';

  @override
  String get issuerHint => '例如：Google、GitHub、Amazon';

  @override
  String get issuerHelper => '服务或组织（可选）';

  @override
  String get secretHint => '例如：JBSWY3DPEHPK3PXP';

  @override
  String get secretHelper => '提供商提供的Base32编码密钥';

  @override
  String get showSecret => '显示密钥';

  @override
  String get hideSecret => '隐藏密钥';

  @override
  String get base32Hint => '密钥必须是Base32格式（A-Z和2-7）。空格会自动移除。';

  @override
  String get scanQrcodeInstructions => '将摄像头对准TOTP二维码';

  @override
  String get onlyTotpSupported => '仅支持TOTP二维码';

  @override
  String get invalidQrcodeFormat => '无效的二维码';

  @override
  String get cameraPermissionRequired => '需要相机权限';

  @override
  String get cameraPermissionDesc => '要扫描二维码，请授予相机权限。';

  @override
  String get grantPermission => '授予权限';

  @override
  String get openSettings => '打开设置';

  @override
  String get cameraError => '相机错误';

  @override
  String get toggleFlashlight => '切换闪光灯';

  @override
  String get switchCamera => '切换相机';

  @override
  String get refreshCode => '刷新验证码';

  @override
  String get noAccountsYet => '暂无账户';

  @override
  String get tapPlusToAdd => '点击 + 按钮添加您的第一个账户';

  @override
  String get editAccount => '编辑账户';

  @override
  String accountUpdated(String accountName) {
    return '账户 \"$accountName\" 更新成功';
  }

  @override
  String get errorUpdatingAccount => '更新账户时出错';

  @override
  String get savingAccount => '正在保存账户...';

  @override
  String get editAccountComingSoon => '编辑账户功能即将推出';

  @override
  String get biometricFailed => '生物识别验证失败';

  @override
  String get english => '英语';

  @override
  String get chinese => '中文';

  @override
  String get crossPlatformAuthenticator => '跨平台双因素认证器';

  @override
  String get copyright => '2024 SillyAuth。保留所有权利。';

  @override
  String get importFromFile => '从文件导入';

  @override
  String get importAccounts => '导入账户';

  @override
  String get importDescription => '从Google Authenticator导出文件导入账户';

  @override
  String get selectFile => '选择文件';

  @override
  String importSuccess(int count) {
    return '成功导入 $count 个账户';
  }

  @override
  String importPartial(int count, int invalidCount) {
    return '导入 $count 个账户，跳过 $invalidCount 个无效条目';
  }

  @override
  String get importFailed => '导入账户失败';

  @override
  String get noAccountsImported => '文件中未找到有效账户';

  @override
  String duplicatesSkipped(int count) {
    return '跳过 $count 个重复项';
  }

  @override
  String invalidEntriesSkipped(int count) {
    return '跳过 $count 个无效条目';
  }

  @override
  String get importingAccounts => '正在导入账户...';
}
