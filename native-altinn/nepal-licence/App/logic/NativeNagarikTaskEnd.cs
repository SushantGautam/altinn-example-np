using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading;
using System.Threading.Tasks;
using Altinn.App.Core.Features;
using Altinn.Platform.Storage.Interface.Models;
using Microsoft.Extensions.Logging;

namespace Altinn.App.Logic;

/// <summary>
/// Genuine Altinn BPMN process lifecycle hook. A secure, minimal demo event
/// is emitted to a replaceable Nagarik integration adapter; no personal data.
/// </summary>
public sealed class NativeNagarikTaskEnd : IProcessTaskEnd
{
    private readonly IHttpClientFactory _http;
    private readonly ILogger<NativeNagarikTaskEnd> _logger;

    public NativeNagarikTaskEnd(IHttpClientFactory http, ILogger<NativeNagarikTaskEnd> logger)
    {
        _http = http;
        _logger = logger;
    }

    public async Task End(string taskId, Instance instance)
    {
        if (taskId != "Task_1")
        {
            return;
        }

        if (!LocalDemoBridge.TryGetTarget("nagarik", out Uri? destination, out string? secret))
        {
            _logger.LogInformation("Native Altinn process finished data task; optional Nepal integration is disabled");
            return;
        }

        using var cancellation = new CancellationTokenSource(TimeSpan.FromSeconds(4));
        using var request = new HttpRequestMessage(HttpMethod.Post, destination);
        request.Headers.TryAddWithoutValidation("x-native-demo-token", secret);
        request.Content = JsonContent.Create(new
        {
            source = "ttd/nepal-licence",
            event_type = "native.altinn.task.completed",
            event_id = "native." + instance.Id + "." + taskId,
            instance_id = instance.Id
        });

        try
        {
            using HttpResponseMessage result = await _http.CreateClient().SendAsync(request, cancellation.Token);
            if (!result.IsSuccessStatusCode)
            {
                _logger.LogWarning("Synthetic Nagarik callback rejected with status {Status}", (int)result.StatusCode);
            }
        }
        catch (Exception error) when (error is HttpRequestException or TaskCanceledException)
        {
            // An illustrative inbox should never block Altinn's own processing.
            _logger.LogWarning(error, "Optional Nagarik demonstration callback was unavailable");
        }
    }
}
