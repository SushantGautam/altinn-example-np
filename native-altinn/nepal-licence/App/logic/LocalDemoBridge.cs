using System;
using System.IO;
using System.Text.Json;

namespace Altinn.App.Logic;

/// <summary>
/// Two local-only ways to configure the synthetic Nepal adapters:
/// 1. Host process mode: existing environment variables;
/// 2. Container mode: ephemeral JSON supplied by the local `demo` CLI after
///    studioctl has built/launched the native Altinn app container.
///
/// No runtime tokens are stored in Git, baked into Docker images or shared
/// with the citizen browser. This is not government service authentication.
/// </summary>
internal static class LocalDemoBridge
{
    internal sealed class Settings
    {
        public string? Token { get; set; }
        public string? DotmUrl { get; set; }
        public string? NagarikUrl { get; set; }
    }

    internal static bool TryGetTarget(string kind, out Uri? endpoint, out string? token)
    {
        endpoint = null;
        token = Environment.GetEnvironmentVariable("NATIVE_WEBHOOK_TOKEN");
        string? target = Environment.GetEnvironmentVariable(kind == "dotm"
            ? "DOTM_MOCK_REGISTRY_URL" : "NAGARIK_DEMO_WEBHOOK_URL");

        const string path = "/tmp/altinn-nepal-bridge.json";
        if (File.Exists(path))
        {
            try
            {
                Settings? settings = JsonSerializer.Deserialize<Settings>(File.ReadAllText(path));
                if (settings is not null)
                {
                    token = settings.Token;
                    target = kind == "dotm" ? settings.DotmUrl : settings.NagarikUrl;
                }
            }
            catch (IOException)
            {
                return false;
            }
            catch (JsonException)
            {
                return false;
            }
            catch (UnauthorizedAccessException)
            {
                return false;
            }
        }

        if (string.IsNullOrWhiteSpace(token) || !Uri.TryCreate(target, UriKind.Absolute, out var candidate)
            || candidate.Scheme != Uri.UriSchemeHttp
            || candidate.Host is not ("localhost" or "127.0.0.1" or "portal"))
        {
            return false;
        }

        // "portal" is resolvable only inside the isolated demo Docker network.
        // This is deliberately not a generic or production connector.
        endpoint = candidate;
        return true;
    }
}
