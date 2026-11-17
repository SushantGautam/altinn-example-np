using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;
using Altinn.App.Core.Features;
using Altinn.App.Models.model;
using Altinn.Platform.Storage.Interface.Models;

namespace Altinn.App.Logic;

/// <summary>
/// Native Altinn instantiation hook. In a real pilot the adapter retrieves
/// eligible fields from an approved DoTM API with lawful authorization.
/// </summary>
public sealed class NepalRegistryPrefill : IInstantiationProcessor
{
    private readonly INepalRegistryClient _registry;

    public NepalRegistryPrefill(INepalRegistryClient registry)
    {
        _registry = registry;
    }

    public async Task DataCreation(Instance instance, object data, Dictionary<string, string> prefill)
    {
        if (data is model form)
        {
            var licence = await _registry.GetSyntheticLicence();
            form.licenceNumber = licence.Reference;
        }
    }
}

/// <summary>Adapter boundary for a future, authenticated DoTM transport API.</summary>
public interface INepalRegistryClient
{
    Task<SyntheticLicenceRecord> GetSyntheticLicence();
}

public sealed record SyntheticLicenceRecord(string Reference, string Source);

/// <summary>
/// HTTP client for a LOCAL synthetic DoTM stub. No actual government
/// service or personal data is used. Without the stub it returns a safe fixture.
/// </summary>
public sealed class SyntheticNepalRegistryClient : INepalRegistryClient
{
    private readonly HttpClient _http;
    private readonly ILogger<SyntheticNepalRegistryClient> _logger;

    public SyntheticNepalRegistryClient(HttpClient http, ILogger<SyntheticNepalRegistryClient> logger)
    {
        _http = http;
        _logger = logger;
    }

    public async Task<SyntheticLicenceRecord> GetSyntheticLicence()
    {
        if (LocalDemoBridge.TryGetTarget("dotm", out Uri? uri, out string? token))
        {
            try
            {
                using var cancellation = new CancellationTokenSource(TimeSpan.FromSeconds(4));
                using var request = new HttpRequestMessage(HttpMethod.Get, uri);
                request.Headers.TryAddWithoutValidation("x-native-demo-token", token);
                using HttpResponseMessage response = await _http.SendAsync(request, cancellation.Token);
                response.EnsureSuccessStatusCode();
                SyntheticLicenceRecord? record =
                    await response.Content.ReadFromJsonAsync<SyntheticLicenceRecord>(cancellation.Token);
                if (record is { Reference.Length: > 0 })
                {
                    return record;
                }
            }
            catch (Exception e) when (e is HttpRequestException or TaskCanceledException)
            {
                _logger.LogWarning(e, "Optional synthetic DoTM adapter is unavailable; using fixture");
            }
        }

        return new SyntheticLicenceRecord(
            "DL-NP-SYNTHETIC-001",
            "Department of Transport Management (fallback synthetic fixture)");
    }
}
