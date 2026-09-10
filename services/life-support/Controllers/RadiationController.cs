using DeathStar.LifeSupport.Models;
using DeathStar.LifeSupport.Services;
using Microsoft.AspNetCore.Mvc;

namespace DeathStar.LifeSupport.Controllers;

[ApiController]
[Route("api/radiation")]
public class RadiationController : ControllerBase
{
    private readonly EnvironmentService _environmentService;
    private readonly CryptoService _cryptoService;

    public RadiationController(EnvironmentService environmentService, CryptoService cryptoService)
    {
        _environmentService = environmentService;
        _cryptoService = cryptoService;
    }

    [HttpGet("levels")]
    public IActionResult GetRadiationLevels([FromQuery] string zone)
    {
        var result = _environmentService.GetRadiationLevels(zone);
        return Ok(new { zone, readings = result });
    }

    [HttpPost("alert")]
    public IActionResult SendRadiationAlert([FromBody] RadiationAlert alert)
    {
        var formattedMessage = _environmentService.FormatAlertMessage(
            alert.MessageTemplate, alert.ZoneId, alert.AlertLevel);
        return Ok(new
        {
            zone = alert.ZoneId,
            level = alert.AlertLevel,
            message = formattedMessage,
            recipients = alert.RecipientGroup
        });
    }

    [HttpPost("upload-readings")]
    public async Task<IActionResult> UploadReadings(IFormFile file)
    {
        if (file == null || file.Length == 0)
            return BadRequest(new { error = "No file provided" });

        var savedPath = await _environmentService.SaveUploadedFile(file.FileName, file.OpenReadStream());
        return Ok(new
        {
            message = "Radiation readings uploaded",
            fileName = file.FileName,
            size = file.Length,
            path = savedPath
        });
    }

    [HttpGet("report")]
    public IActionResult GetReport([FromQuery] string template)
    {
        var content = _environmentService.LoadReportTemplate(template);
        return Ok(new { template, content });
    }

    [HttpGet("zones")]
    public IActionResult ListZones()
    {
        return Ok(new
        {
            zones = new[]
            {
                new { id = "RZ-01", name = "Reactor Core Perimeter", shielding = "heavy" },
                new { id = "RZ-02", name = "Superlaser Assembly", shielding = "reinforced" },
                new { id = "RZ-03", name = "Hyperdrive Chamber", shielding = "standard" },
                new { id = "RZ-04", name = "Crew Quarters Block A", shielding = "light" },
                new { id = "RZ-05", name = "Detention Level", shielding = "minimal" },
                new { id = "RZ-06", name = "Hangar Bay", shielding = "moderate" }
            }
        });
    }

    [HttpPost("encrypt-reading")]
    public IActionResult EncryptReading([FromBody] RadiationReading reading)
    {
        var data = $"{reading.ZoneId}|{reading.SievertLevel}|{reading.Timestamp}";
        var encrypted = _cryptoService.EncryptSensorData(data);
        var hash = _cryptoService.HashSensorReading(data);
        return Ok(new { encrypted = Convert.ToBase64String(encrypted), integrity = hash });
    }
}
