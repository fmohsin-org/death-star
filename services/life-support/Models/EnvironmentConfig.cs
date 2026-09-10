using System.Runtime.Serialization;

namespace DeathStar.LifeSupport.Models;

[Serializable]
public class EnvironmentConfig
{
    public string SectorId { get; set; }
    public double OxygenPercentage { get; set; }
    public double GravityMultiplier { get; set; }
    public double TemperatureCelsius { get; set; }
    public double HumidityPercentage { get; set; }
    public string AtmosphericMix { get; set; }
    public string EncryptionKey { get; set; }
    public string AccessCode { get; set; }
    public string OverridePassword { get; set; }
    public string MaintenanceToken { get; set; }
}

[Serializable]
public class EnvironmentOverride
{
    public string OperatorId { get; set; }
    public string SectorId { get; set; }
    public string Parameter { get; set; }
    public double NewValue { get; set; }
    public string OverrideReason { get; set; }
    public string AuthorizationCode { get; set; }
}

[Serializable]
public class DiagnosticRequest
{
    public string Command { get; set; }
    public string Target { get; set; }
    public string Parameters { get; set; }
}

[Serializable]
public class RadiationReading
{
    public string ZoneId { get; set; }
    public double SievertLevel { get; set; }
    public string SensorType { get; set; }
    public DateTime Timestamp { get; set; }
    public string TechnicianId { get; set; }
}

[Serializable]
public class RadiationAlert
{
    public string ZoneId { get; set; }
    public string AlertLevel { get; set; }
    public string MessageTemplate { get; set; }
    public string RecipientGroup { get; set; }
}

[Serializable]
public class TemperatureUpdate
{
    public string DeckId { get; set; }
    public double TargetTemperature { get; set; }
    public string Priority { get; set; }
}

[Serializable]
public class ConfigImport
{
    public string Format { get; set; }
    public string EncodedPayload { get; set; }
}
