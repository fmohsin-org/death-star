using DeathStar.LifeSupport.Services;
using DeathStar.LifeSupport.Config;
using log4net;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

builder.Services.AddSingleton<EnvironmentService>();
builder.Services.AddSingleton<CryptoService>();

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(5199);
});

var app = builder.Build();

app.UseCors();
app.UseDeveloperExceptionPage();

app.MapControllers();

var logger = LogManager.GetLogger(typeof(Program));
logger.Info($"Life Support System initialized — Station: {AppSettings.StationId}");
logger.Info($"Database: {AppSettings.DatabaseConnectionString}");

app.Run();
