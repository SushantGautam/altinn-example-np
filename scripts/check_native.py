"""Validate the REAL Altinn application's configuration and wiring."""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

R = Path(__file__).resolve().parent.parent / "native-altinn" / "nepal-licence" / "App"
namespaces = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
              "xacml": "urn:oasis:names:tc:xacml:3.0:core:schema:wd-17"}
def read_json(path):
    return json.loads((R/path).read_text(encoding="utf-8-sig"))

m = read_json("config/applicationmetadata.json")
assert m["id"] == "ttd/nepal-licence" and m["org"] == "ttd"
assert m["dataTypes"][1]["appLogic"]["classRef"] == "Altinn.App.Models.model.model"
model = read_json("models/model.schema.json")
expected = {"licenceNumber", "requestedAddress", "reason"}
assert set(model["properties"]) == expected
assert set(model["required"]) == expected
cs = (R/"models/model.cs").read_text(encoding="utf-8-sig")
assert all(re.search(r"\b"+name+r"\b", cs) for name in expected)
page = read_json("ui/form/layouts/Side1.json")
bindings = {c.get("dataModelBindings",{}).get("simpleBinding") for c in page["data"]["layout"]}
assert expected <= bindings
assert any(c["type"] == "Button" for c in page["data"]["layout"])
bpmn = ET.parse(R/"config/process/process.bpmn")
assert bpmn.find('.//bpmn:task[@id="Task_1"]', namespaces) is not None
assert bpmn.find(".//bpmn:endEvent", namespaces) is not None
xacml = ET.parse(R/"config/authorization/policy.xml")
assert xacml.getroot().tag.endswith("Policy")
assert "ttd_nepal-licence" in xacml.getroot().attrib["PolicyId"]
program = (R/"Program.cs").read_text(encoding="utf-8-sig")
assert "AddAltinnAppServices" in program and "NepalRegistryPrefill" in program
adapter = (R/"logic/NepalRegistryPrefill.cs").read_text(encoding="utf-8-sig")
assert "IInstantiationProcessor" in adapter and "INepalRegistryClient" in adapter
print("PASS: native Altinn metadata, BPMN, XACML, model, frontend and custom prefill wiring")
