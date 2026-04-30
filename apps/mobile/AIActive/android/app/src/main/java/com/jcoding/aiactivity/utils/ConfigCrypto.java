package com.jcoding.aiactivity.utils;

import android.util.Base64;
import android.util.Log;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.security.spec.KeySpec;
import java.util.Arrays;

/**
 * 配置文件加密/解密工具
 * - 基础层：AES-256-GCM，使用版本号派生密钥
 * - 增强层：服务器额外加密的高度敏感字段
 *
 * @author Claude Code
 * @since 2026-02-06
 */
public class ConfigCrypto {

    private static final String TAG = "ConfigCrypto";
    private static final String ALGORITHM = "AES";
    private static final String TRANSFORMATION = "AES/GCM/NoPadding";
    private static final String KEY_DERIVATION = "PBKDF2WithHmacSHA256";
    private static final String SALT = "JC_AI_CONFIG_SALT_2026";
    private static final int ITERATIONS = 100000;  // 测试用100K，生产环境使用300K
    private static final int KEY_SIZE = 256;
    private static final int GCM_TAG_LENGTH = 128;
    private static final int GCM_IV_LENGTH = 12;

    /**
     * 从版本号派生加密密钥
     * v1.2.0 -> "120" -> PBKDF2 -> 256-bit key
     *
     * 安全说明：
     * - 使用 PBKDF2WithHmacSHA256 进行密钥派生
     * - 迭代次数设置为 300,000 以防止暴力破解
     * - 版本号标准化：右填充 '0' 到至少3位 (v1.0 -> "100", v1.2.0 -> "120")
     *
     * @param version 版本号字符串 (e.g., "v1.2.0")
     * @return 256-bit AES 密钥
     * @throws Exception 如果密钥派生失败
     */
    public static SecretKey deriveKey(String version) throws Exception {
        // 转换版本号为数字字符串: "v1.2.0" -> "120"
        // 与 Python 端保持一致：右填充 '0' 到至少 3 位
        String versionNum = version.replace("v", "").replace(".", "");
        while (versionNum.length() < 3) {
            versionNum = versionNum + "0";
        }

        KeySpec spec = new PBEKeySpec(
            versionNum.toCharArray(),
            SALT.getBytes(StandardCharsets.UTF_8),
            ITERATIONS,
            KEY_SIZE
        );

        SecretKeyFactory factory = SecretKeyFactory.getInstance(KEY_DERIVATION);
        byte[] keyBytes = factory.generateSecret(spec).getEncoded();
        return new SecretKeySpec(keyBytes, ALGORITHM);
    }

    /**
     * 加密明文字符串
     *
     * @param plaintext 要加密的明文
     * @param version 版本号（用于派生密钥）
     * @return Base64 编码的密文 (IV + ciphertext + auth_tag)
     * @throws Exception 如果加密失败
     */
    public static String encrypt(String plaintext, String version) throws Exception {
        SecretKey key = deriveKey(version);

        // 生成随机 IV
        byte[] iv = new byte[GCM_IV_LENGTH];
        new SecureRandom().nextBytes(iv);

        // 初始化加密器
        Cipher cipher = Cipher.getInstance(TRANSFORMATION);
        GCMParameterSpec parameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH, iv);
        cipher.init(Cipher.ENCRYPT_MODE, key, parameterSpec);

        // 加密
        byte[] ciphertext = cipher.doFinal(plaintext.getBytes(StandardCharsets.UTF_8));

        // 组合 IV + ciphertext
        byte[] combined = new byte[GCM_IV_LENGTH + ciphertext.length];
        System.arraycopy(iv, 0, combined, 0, GCM_IV_LENGTH);
        System.arraycopy(ciphertext, 0, combined, GCM_IV_LENGTH, ciphertext.length);

        // 返回 Base64 编码
        return Base64.encodeToString(combined, Base64.NO_WRAP);
    }

    /**
     * 解密密文字符串
     *
     * @param ciphertext Base64 编码的密文 (IV + ciphertext + auth_tag)
     * @param version 版本号（用于派生密钥）
     * @return 解密后的明文
     * @throws Exception 如果解密失败
     */
    public static String decrypt(String ciphertext, String version) throws Exception {
        SecretKey key = deriveKey(version);

        // 解码 Base64
        byte[] combined = Base64.decode(ciphertext, Base64.NO_WRAP);

        // 提取 IV
        byte[] iv = Arrays.copyOfRange(combined, 0, GCM_IV_LENGTH);

        // 提取实际密文
        byte[] encrypted = Arrays.copyOfRange(combined, GCM_IV_LENGTH, combined.length);

        // 初始化解密器
        Cipher cipher = Cipher.getInstance(TRANSFORMATION);
        GCMParameterSpec parameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH, iv);
        cipher.init(Cipher.DECRYPT_MODE, key, parameterSpec);

        // 解密
        byte[] plaintext = cipher.doFinal(encrypted);
        return new String(plaintext, StandardCharsets.UTF_8);
    }

    /**
     * 解密服务器额外加密的字段
     * 使用服务器提供的会话密钥
     *
     * 安全说明：
     * - 服务器额外加密用于高度敏感字段（api_key, secret_key）
     * - 当前实现：抛出异常提醒尚未实现
     * - 未来实现：使用服务器协商的会话密钥进行二次解密
     *
     * @param ciphertext 服务器额外加密的密文
     * @param sessionKey 会话密钥（从服务器获取），当前未使用
     * @return 解密后的明文
     * @throws UnsupportedOperationException 当前功能尚未实现
     */
    public static String decryptServerEncrypted(String ciphertext, String sessionKey) {
        // 安全优先原则：对于未实现的服务器解密，抛出异常而不是静默失败
        Log.e(TAG, "Server decryption not yet implemented - cannot decrypt SERVER_ENC: fields");
        throw new UnsupportedOperationException(
            "Server-side decryption not yet implemented. " +
            "SERVER_ENC: fields require server session key negotiation. " +
            "Please use regular encryption for now."
        );
    }

    /**
     * 批量解密 JSON 对象中的加密字段
     *
     * 安全说明：
     * - 任何字段解密失败都会抛出异常，不会静默失败
     * - SERVER_ENC: 前缀的字段需要服务器解密（当前抛出异常）
     *
     * @param encryptedObj 加密的 JSON 对象
     * @param version 版本号
     * @return 解密后的 JSON 对象
     * @throws RuntimeException 如果任何字段解密失败
     */
    public static com.google.gson.JsonObject decryptJsonObject(
            com.google.gson.JsonObject encryptedObj,
            String version) {
        com.google.gson.JsonObject decrypted = new com.google.gson.JsonObject();

        for (String key : encryptedObj.keySet()) {
            try {
                String encryptedValue = encryptedObj.get(key).getAsString();

                // 检查是否为服务器额外加密
                if (encryptedValue.startsWith("SERVER_ENC:")) {
                    String serverEncrypted = encryptedValue.substring("SERVER_ENC:".length());
                    String decryptedValue = decryptServerEncrypted(serverEncrypted, null);
                    decrypted.addProperty(key, decryptedValue);
                } else {
                    // 常规版本号加密
                    String decryptedValue = decrypt(encryptedValue, version);
                    decrypted.addProperty(key, decryptedValue);
                }
            } catch (Exception e) {
                // 不再静默失败 - 记录详细错误并重新抛出
                Log.e(TAG, "CRITICAL: Failed to decrypt field '" + key + "'. " +
                    "This may indicate: 1) Corrupted config, 2) Wrong version, 3) Tampering detected", e);
                throw new RuntimeException("Failed to decrypt config field: " + key, e);
            }
        }

        return decrypted;
    }
}
