namespace DeathStar.LifeSupport.Config;

public static class AppSettings
{
    public static readonly string StationId = "DS-1-LIFE-SUPPORT";

    public static readonly string DatabaseConnectionString =
        "Server=imperial-db.deathstar.local;Database=LifeSupportDB;User Id=ls_admin;Password=Imp3r1alL1f3Supp0rt!;";

    public static readonly string ImperialEncryptionKey = "4f6a8b2d-1e3c-4a5f-9d7b-8c2e1f3a4b5d";

    public static readonly string LifeSupportOverrideCode = "OVERRIDE-LS-7742-ALPHA";

    public static readonly string AwsAccessKeyId = "AKIAIOSFODNN7EXAMPLE";
    public static readonly string AwsSecretAccessKey = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY";

    public static readonly string RedisConnectionString =
        "imperial-cache.deathstar.local:6379,password=R3d1s_Imp3r1al_2024!,ssl=false";

    public static readonly string JwtSigningSecret = "ImperialLifeSupportJWT_s3cr3t_k3y_2024_d34th_st4r";

    public static readonly string SmtpPassword = "smtp_1mp3r1al_m41l!";

    public static readonly string ImperialApiKey = "sk_live_51Imperial4LifeSupport7DeathStar9Key";

    public static readonly string SlackWebhookUrl =
        "https://hooks.slack.com/services/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ook";

    public static readonly int MaxOxygenLevel = 100;
    public static readonly int MinOxygenLevel = 18;
    public static readonly double StandardGravity = 9.81;
    public static readonly double StandardTemperatureCelsius = 22.0;
}
