package com.tencent.cloud.sdktts;

@ShareKey(key = "SecretConfig")
public class SecretConfig {

    private static class SecretConfigHolder {
        private static final SecretConfig instance = new SecretConfig();
    }

    static public SecretConfig get() {
        return SecretConfigHolder.instance;
    }

    @ShareKey(key = "online_secret_id")
    public String online_secret_id = "";

    @ShareKey(key = "online_secret_key")
    public String online_secret_key = "";

    @ShareKey(key = "offline_online_secret_id")
    public String offline_online_secret_id = "";

    @ShareKey(key = "offline_online_secret_key")
    public String offline_online_secret_key = "";

    @ShareKey(key = "offline_online_lic_key")
    public String offline_online_lic_key = "";

    @ShareKey(key = "offline_online_lic_pk")
    public String offline_online_lic_pk = "";

    @ShareKey(key = "offline_lic")
    public String offline_lic = "";
    
    @ShareKey(key = "offline_lic_sign")
    public String offline_lic_sign = "";

    @ShareKey(key = "offline_lic_pk")
    public String offline_lic_pk = "";

    @ShareKey(key = "auth_way")
    public int auth_way = 1;

}
