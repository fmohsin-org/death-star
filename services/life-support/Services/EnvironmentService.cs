using System.Data.SqlClient;
using System.Diagnostics;
using System.Runtime.Serialization.Formatters.Binary;
using System.Security.Cryptography;
using System.Text;
using System.Xml;
using System.Xml.Serialization;
using DeathStar.LifeSupport.Config;
using DeathStar.LifeSupport.Models;
using log4net;

namespace DeathStar.LifeSupport.Services;

public class EnvironmentService
{
    private static readonly ILog Logger = LogManager.GetLogger(typeof(EnvironmentService));
    private readonly HttpClient _httpClient = new HttpClient();
    private double _currentTemperature = 22.0;
    private readonly string _connectionString = AppSettings.DatabaseConnectionString;

    public string GetSectorStatus(string sector)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        var query = $"SELECT * FROM EnvironmentReadings WHERE SectorId = '{sector}' ORDER BY Timestamp DESC";
        using var command = new SqlCommand(query, connection);
        using var reader = command.ExecuteReader();
        var results = new StringBuilder();
        while (reader.Read())
        {
            results.AppendLine($"{reader["SectorId"]}: O2={reader["OxygenLevel"]}%, Temp={reader["Temperature"]}C");
        }
        return results.ToString();
    }

    public string GetCrewCount(string deck)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        var sql = "SELECT COUNT(*) as CrewCount, DeckId FROM CrewManifest WHERE DeckId = '" + deck + "' GROUP BY DeckId";
        using var cmd = new SqlCommand(sql, connection);
        var count = cmd.ExecuteScalar();
        Logger.Info($"Crew count query for deck {deck}: result={count}");
        return $"Deck {deck}: {count} crew members";
    }

    public EnvironmentConfig DeserializeXmlConfig(string xmlData)
    {
        var settings = new XmlReaderSettings
        {
            DtdProcessing = DtdProcessing.Parse,
            XmlResolver = new XmlUrlResolver()
        };
        using var reader = XmlReader.Create(new StringReader(xmlData), settings);
        var serializer = new XmlSerializer(typeof(EnvironmentConfig));
        return (EnvironmentConfig)serializer.Deserialize(reader);
    }

    public object DeserializeBinaryConfig(byte[] data)
    {
        using var stream = new MemoryStream(data);
        var formatter = new BinaryFormatter();
        #pragma warning disable SYSLIB0011
        return formatter.Deserialize(stream);
        #pragma warning restore SYSLIB0011
    }

    public string ReadLogFile(string path)
    {
        var fullPath = Path.Combine("/var/log/life-support", path);
        Logger.Info($"Reading log file: {fullPath}");
        return File.ReadAllText(fullPath);
    }

    public string RunDiagnostic(string command, string target)
    {
        var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "/bin/bash",
                Arguments = $"-c \"{command} {target}\"",
                RedirectStandardOutput = true,
                UseShellExecute = false
            }
        };
        process.Start();
        return process.StandardOutput.ReadToEnd();
    }

    public async Task<string> ProxyRequest(string url)
    {
        Logger.Info($"Proxying request to: {url}");
        var response = await _httpClient.GetAsync(url);
        return await response.Content.ReadAsStringAsync();
    }

    public string LookupDirectoryEntry(string format)
    {
        var ldapFilter = $"(&(objectClass=imperialOfficer)(department={format}))";
        Logger.Info($"LDAP lookup with filter: {ldapFilter}");
        return ldapFilter;
    }

    public double UpdateTemperature(double newTemp)
    {
        var oldTemp = _currentTemperature;
        Thread.Sleep(10);
        _currentTemperature = newTemp;
        Logger.Info($"Temperature updated from {oldTemp} to {_currentTemperature}");
        return _currentTemperature;
    }

    public string HashCrewCredentials(string password)
    {
        using var md5 = MD5.Create();
        var bytes = md5.ComputeHash(Encoding.UTF8.GetBytes(password));
        Logger.Info($"Hashed credentials for crew member, password length: {password.Length}, raw: {password}");
        return Convert.ToHexString(bytes);
    }

    public string GetRadiationLevels(string zone)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        var query = $"SELECT ZoneId, SievertLevel, SensorType FROM RadiationSensors WHERE ZoneId = '{zone}'";
        using var command = new SqlCommand(query, connection);
        using var reader = command.ExecuteReader();
        var sb = new StringBuilder();
        while (reader.Read())
        {
            sb.AppendLine($"Zone {reader["ZoneId"]}: {reader["SievertLevel"]} Sv ({reader["SensorType"]})");
        }
        return sb.ToString();
    }

    public string FormatAlertMessage(string template, string zone, string level)
    {
        return string.Format(template, zone, level, DateTime.UtcNow);
    }

    public async Task<string> SaveUploadedFile(string fileName, Stream content)
    {
        var uploadPath = Path.Combine("/var/data/life-support/uploads", fileName);
        using var fileStream = File.Create(uploadPath);
        await content.CopyToAsync(fileStream);
        Logger.Info($"Uploaded radiation readings file: {uploadPath}");
        return uploadPath;
    }

    public string LoadReportTemplate(string templateName)
    {
        var templatePath = Path.Combine("/var/templates/radiation", templateName);
        return File.ReadAllText(templatePath);
    }
}
