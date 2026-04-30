# 添加项目特定的ProGuard规则
# 可以通过浏览 ProGuard 文件来了解更多
# http://proguard.sourceforge.net/index.html

# 保留所有公共API
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Application
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider
-keep public class * extends android.preference.Preference
-keep public class * extends android.view.View

# 保留 native 方法
-keepclasseswithmembernames class * {
    native <methods>;
}

# 保留枚举
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# 保留 Serializable
-keepclassmembers class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
    private void writeObject(java.io.ObjectOutputStream);
    private void readObject(java.io.ObjectInputStream);
    java.lang.Object writeReplace();
    java.lang.Object readResolve();
}

# 保留 Parcelable
-keep class * implements android.os.Parcelable {
  public static final android.os.Parcelable$Creator *;
}

# 保留R文件
-keepclassmembers class **.R$* {
    public static <fields>;
}

# 保留所有实体类
-keep class com.jcoding.aiactivity.entity.** { *; }

# 保留所有Manager类
-keep class com.jcoding.aiactivity.manager.** { *; }

# 保留所有Utils类
-keep class com.jcoding.aiactivity.utils.** { *; }

# 加密工具类特殊规则（保护密钥派生逻辑）
-keep class com.jcoding.aiactivity.utils.ConfigCrypto {
    public static <methods>;
}

# 保留 javax.crypto 相关类
-dontwarn javax.crypto.*
-keep class javax.crypto.** { *; }
-keepclassmembers class javax.crypto.** { *; }

# 保留所有Widget类
-keep class com.jcoding.aiactivity.widget.** { *; }

# Gson 配置
-keepattributes Signature
-keepattributes *Annotation*
-dontwarn sun.misc.**
-keep class com.google.gson.** { *; }
-keep class * implements com.google.gson.TypeAdapter
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer
-keepclassmembers,allowobfuscation class * {
  @com.google.gson.annotations.SerializedName <fields>;
}

# CameraX 配置
-keep class androidx.camera.** { *; }
-dontwarn androidx.camera.**

# NanoHTTPD 配置（解决重复类型问题）
-dontwarn fi.iki.elonen.**
-keep class fi.iki.elonen.** { *; }

# 腾讯云SDK配置
-keep class com.tencent.** { *; }
-dontwarn com.tencent.**

# OkHttp配置
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }

# Retrofit配置
-dontwarn retrofit2.**
-keep class retrofit2.** { *; }
-keepattributes Signature
-keepattributes Exceptions

# Glide配置
-keep public class * implements com.bumptech.glide.module.GlideModule
-keep public class * extends com.bumptech.glide.module.AppGlideModule
-keep public enum com.bumptech.glide.load.ImageHeaderParser$** {
  **[] $VALUES;
  public *;
}

# 保持反射调用的方法
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# 保留所有注解
-keepattributes *Annotation*
-keepattributes EnclosingMethod
-keepattributes InnerClass

# 保留测试代码
-keep class * extends java.lang.annotation.Annotation
-keep class * {
    @android.webkit.JavascriptInterface <methods>;
}
