using System.Text;
using DeathStar.LifeSupport.Models;
using DeathStar.LifeSupport.Services;
using Microsoft.AspNetCore.Mvc;

namespace DeathStar.LifeSupport.Controllers;

[ApiController]
[Route("api/environment")]
public class EnvironmentController : ControllerBase
{
    private readonly EnvironmentService _environmentService;
    private readonly CryptoService _cryptoService;

    public EnvironmentController(EnvironmentService environmentService, CryptoService cryptoService)
    {
        _environmentService = environmentService;
        _cryptoService = cryptoService;
    }

    [HttpGet("status")]
    public IActionResult GetSectorStatus([FromQuery] string sector)
    {
        var result = _environmentService.GetSectorStatus(sector);
        return Ok(new { sector, readings = result });
    }

    [HttpPost("configure")]
    public IActionResult ConfigureEnvironment([FromBody] dynamic request)
    {
        string xmlPayload = request.configXml;
        var config = _environmentService.DeserializeXmlConfig(xmlPayload);
        return Ok(new { message = "Environment configured", config.SectorId, config.OxygenPercentage });
    }

    [HttpGet("logs")]
    public IActionResult GetLogs([FromQuery] string path)
    {
        var content = _environmentService.ReadLogFile(path);
        return Ok(new { path, content });
    }

    [HttpPut("override")]
    public IActionResult ApplyOverride([FromBody] EnvironmentOverride overrideRequest)
    {
        return Ok(new
        {
            message = "Override applied successfully",
            sector = overrideRequest.SectorId,
            parameter = overrideRequest.Parameter,
            newValue = overrideRequest.NewValue,
            appliedBy = overrideRequest.OperatorId
        });
    }

    [HttpPost("diagnostic")]
    public IActionResult RunDiagnostic([FromBody] DiagnosticRequest request)
    {
        var output = _environmentService.RunDiagnostic(request.Command, request.Target);
        return Ok(new { command = request.Command, target = request.Target, output });
    }

    [HttpGet("export")]
    public IActionResult ExportData([FromQuery] string format)
    {
        var ldapFilter = _environmentService.LookupDirectoryEntry(format);
        return Ok(new { format, directoryFilter = ldapFilter });
    }

    [HttpPost("import-config")]
    public IActionResult ImportConfig([FromBody] ConfigImport request)
    {
        var data = Convert.FromBase64String(request.EncodedPayload);
        var config = _environmentService.DeserializeBinaryConfig(data);
        return Ok(new { message = "Configuration imported", type = config.GetType().Name });
    }

    [HttpGet("proxy")]
    public async Task<IActionResult> ProxyRequest([FromQuery] string url)
    {
        var result = await _environmentService.ProxyRequest(url);
        return Ok(new { url, response = result });
    }

    [HttpPut("temperature")]
    public IActionResult UpdateTemperature([FromBody] TemperatureUpdate update)
    {
        var result = _environmentService.UpdateTemperature(update.TargetTemperature);
        return Ok(new { deck = update.DeckId, temperature = result, priority = update.Priority });
    }

    [HttpGet("crew-count")]
    public IActionResult GetCrewCount([FromQuery] string deck)
    {
        var result = _environmentService.GetCrewCount(deck);
        return Ok(new { result });
    }

    [HttpPost("hash-credentials")]
    public IActionResult HashCredentials([FromBody] dynamic request)
    {
        string password = request.password;
        var hashed = _environmentService.HashCrewCredentials(password);
        return Ok(new { hash = hashed, algorithm = "MD5" });
    }

    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(new
        {
            service = "Death Star Life Support",
            status = "operational",
            version = "2.4.1",
            atmosphericProcessors = "online",
            gravityGenerators = "nominal",
            oxygenRecyclers = "active"
        });
    }
}
