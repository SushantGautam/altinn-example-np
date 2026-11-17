using System.Collections.Generic;
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

/// <summary>Fake data; no live government connection and no real identifiers.</summary>
public sealed class SyntheticNepalRegistryClient : INepalRegistryClient
{
    public Task<SyntheticLicenceRecord> GetSyntheticLicence()
    {
        return Task.FromResult(new SyntheticLicenceRecord(
            "DL-NP-SYNTHETIC-001",
            "Department of Transport Management (mock)"));
    }
}
