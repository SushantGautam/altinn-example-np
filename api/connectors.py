"""Replaceable mock connectors. No live Nepali government systems are queried.

Every record is synthetic; these boundaries can later be implemented as real
agency adapters after agreement on contracts, consent, and authorization.
"""
from dataclasses import dataclass

PEOPLE = {
    "NP-DEMO-001": {"nid": "NP-DEMO-001", "name": "Asha Shrestha", "district": "Lalitpur", "address": "Ward 3, Lalitpur", "status": "verified (synthetic)"}
}
LICENCES = {
    "DL-09418": {"number": "DL-09418", "nid": "NP-DEMO-001", "name": "Asha Shrestha", "category": "B", "address": "Ward 3, Lalitpur", "status": "valid (synthetic)"}
}
COMPANIES = {
    "COMP-100": {"id": "COMP-100", "name": "Everest Logistics Pvt. Ltd.", "registrar": "Company Registry (mock)", "director": "raj", "registration": "77-DEMO-2026"}
}

@dataclass(frozen=True)
class Integration:
    key: str
    label: str
    kind: str
    status: str
    description: str

INTEGRATIONS = [
    Integration("nepalid", "NepalID / OIDC", "real-local", "CONNECTED", "Real OIDC authentication via local Keycloak; synthetic identities, not government identity assurance"),
    Integration("civil", "Civil / Population Registry", "mock", "SIMULATED", "Synthetic National ID and resident data; contract stub"),
    Integration("company", "Company Registry", "mock", "SIMULATED", "Synthetic business registration and director mapping"),
    Integration("dotm", "Department of Transport Management", "mock", "SIMULATED", "Synthetic driving licence and permitting records"),
    Integration("nagarik", "Nagarik mobile app / possible web", "mock", "SIMULATED", "Simulated web inbox only; current Nagarik is mobile, a future government web channel is not implemented"),
    Integration("native-bridge", "Native Altinn ↔ Nepal simulation", "local", "SIMULATED", "Local native App hooks can call a synthetic DoTM HTTP stub and publish a task-completion event into the mock Nagarik inbox; only with start-all"),
    Integration("altinn", "Altinn Platform connector", "placeholder", "NOT CONNECTED", "Adapter boundary only; workflows/authorization are demo implementations, not Altinn services"),
]

def get_person(nid: str) -> dict | None:
    return PEOPLE.get(nid)

def get_licence(number: str) -> dict | None:
    return LICENCES.get(number)

def get_company(company_id: str) -> dict | None:
    return COMPANIES.get(company_id)
