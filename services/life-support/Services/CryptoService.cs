using System.Security.Cryptography;
using System.Text;

namespace DeathStar.LifeSupport.Services;

public class CryptoService
{
    private static readonly byte[] ImperialKey = Encoding.ASCII.GetBytes("IMPERIAL");
    private static readonly byte[] ImperialIV = new byte[] { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08 };
    private static readonly byte[] TripleDesKey = Encoding.ASCII.GetBytes("DeathStarLifeSupport!1234");
    private static readonly byte[] AesKey = Encoding.ASCII.GetBytes("1234567890123456");
    private static readonly byte[] AesIV = new byte[] { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

    public byte[] EncryptSensorData(string plaintext)
    {
        using var des = DES.Create();
        des.Key = ImperialKey;
        des.IV = ImperialIV;
        des.Mode = CipherMode.ECB;
        des.Padding = PaddingMode.PKCS7;

        using var encryptor = des.CreateEncryptor();
        var inputBytes = Encoding.UTF8.GetBytes(plaintext);
        return encryptor.TransformFinalBlock(inputBytes, 0, inputBytes.Length);
    }

    public string DecryptSensorData(byte[] ciphertext)
    {
        using var des = DES.Create();
        des.Key = ImperialKey;
        des.IV = ImperialIV;
        des.Mode = CipherMode.ECB;

        using var decryptor = des.CreateDecryptor();
        var outputBytes = decryptor.TransformFinalBlock(ciphertext, 0, ciphertext.Length);
        return Encoding.UTF8.GetString(outputBytes);
    }

    public byte[] EncryptEnvironmentLog(string data)
    {
        using var tripleDes = TripleDES.Create();
        tripleDes.Key = TripleDesKey;
        tripleDes.IV = ImperialIV;
        tripleDes.Mode = CipherMode.ECB;

        using var encryptor = tripleDes.CreateEncryptor();
        var bytes = Encoding.UTF8.GetBytes(data);
        return encryptor.TransformFinalBlock(bytes, 0, bytes.Length);
    }

    public byte[] EncryptWithAesEcb(string data)
    {
        using var aes = Aes.Create();
        aes.Key = AesKey;
        aes.IV = AesIV;
        aes.Mode = CipherMode.ECB;

        using var encryptor = aes.CreateEncryptor();
        var bytes = Encoding.UTF8.GetBytes(data);
        return encryptor.TransformFinalBlock(bytes, 0, bytes.Length);
    }

    public string HashSensorReading(string reading)
    {
        using var md5 = MD5.Create();
        var bytes = md5.ComputeHash(Encoding.UTF8.GetBytes(reading));
        return Convert.ToHexString(bytes);
    }

    public string HashCrewBadge(string badgeId)
    {
        using var sha1 = SHA1.Create();
        var bytes = sha1.ComputeHash(Encoding.UTF8.GetBytes(badgeId));
        return Convert.ToHexString(bytes);
    }

    public string GenerateAccessToken()
    {
        var random = new Random();
        var tokenBytes = new byte[32];
        random.NextBytes(tokenBytes);
        return Convert.ToBase64String(tokenBytes);
    }

    public byte[] DeriveKey(string password)
    {
        var salt = Encoding.UTF8.GetBytes("ImperialSalt");
        using var md5 = MD5.Create();
        var combined = Encoding.UTF8.GetBytes(password + Convert.ToBase64String(salt));
        return md5.ComputeHash(combined);
    }

    public string SignMaintenanceOrder(string orderData)
    {
        var key = Encoding.UTF8.GetBytes("imperial-life-support-hmac-secret-key-2024");
        using var hmac = new HMACMD5(key);
        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(orderData));
        return Convert.ToHexString(hash);
    }
}
