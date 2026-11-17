using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text.Json.Serialization;
using System.Xml.Serialization;
using Microsoft.AspNetCore.Mvc.ModelBinding;
using Newtonsoft.Json;

namespace Altinn.App.Models.model
{
    [XmlRoot(ElementName = "model")]
    public class model
    {
        [XmlElement("licenceNumber", Order = 1)]
        [JsonProperty("licenceNumber")]
        [JsonPropertyName("licenceNumber")]
        public string licenceNumber { get; set; }

        [XmlElement("requestedAddress", Order = 2)]
        [JsonProperty("requestedAddress")]
        [JsonPropertyName("requestedAddress")]
        public string requestedAddress { get; set; }

        [XmlElement("reason", Order = 3)]
        [JsonProperty("reason")]
        [JsonPropertyName("reason")]
        public string reason { get; set; }
    }
}
