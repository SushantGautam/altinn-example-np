"""Generate a tiny local lab PKI without exposing the CA private key to services.

Only pki-init sees the CA key volume. Each agency has its own certificate/key
volume. Demo CA is NOT a government trust anchor. Never reuse these credentials
for real identity proofing or production services.
"""
import os
import pathlib
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

ROOT = pathlib.Path(os.getenv("PKI_DIR", "/pki"))
ENDPOINTS = [
    "exchange-broker", "transport-edge", "civil-edge", "company-edge",
    "transport-records", "civil-records", "company-records",
]
CA_PATH = ROOT / "ca-private"
CA_KEY = CA_PATH / "ca.key"
CA_CERT = CA_PATH / "ca.crt"


def write_secret(path, data, mode=0o600):
    with open(path, "wb") as file:
        file.write(data)
    os.chmod(path, mode)


def new_private_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=3072)


def certificate_builder(public_key, issuer, subject, duration):
    now = datetime.now(timezone.utc)
    return (x509.CertificateBuilder()
            .subject_name(subject).issuer_name(issuer)
            .public_key(public_key).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=10))
            .not_valid_after(now + duration)
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True))


def ensure_ca():
    CA_PATH.mkdir(parents=True, exist_ok=True)
    if CA_KEY.exists() and CA_CERT.exists():
        key = serialization.load_pem_private_key(CA_KEY.read_bytes(), password=None)
        crt = x509.load_pem_x509_certificate(CA_CERT.read_bytes())
        return key, crt
    key = new_private_key()
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Altinn Nepal local demonstration CA")])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder()
            .subject_name(subject).issuer_name(subject)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=1))
            .not_valid_after(now + timedelta(days=30))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(
                x509.KeyUsage(digital_signature=True, content_commitment=False,
                              key_encipherment=False, data_encipherment=False,
                              key_agreement=False, key_cert_sign=True, crl_sign=True,
                              encipher_only=False, decipher_only=False),
                critical=True)
            .sign(key, hashes.SHA256()))
    write_secret(CA_KEY, key.private_bytes(serialization.Encoding.PEM,
                 serialization.PrivateFormat.TraditionalOpenSSL,
                 serialization.NoEncryption()))
    write_secret(CA_CERT, cert.public_bytes(serialization.Encoding.PEM), 0o644)
    return key, cert


def issue(key, ca):
    for name in ENDPOINTS:
        path = ROOT / name
        path.mkdir(parents=True, exist_ok=True)
        key_path, cert_path, trust_path = path / "tls.key", path / "tls.crt", path / "ca.crt"
        trust_path.write_bytes(ca.public_bytes(serialization.Encoding.PEM))
        os.chmod(trust_path, 0o644)
        if key_path.exists() and cert_path.exists():
            cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
            if cert.not_valid_after_utc > datetime.now(timezone.utc) + timedelta(days=1):
                continue
        private = new_private_key()
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
        usages = [ExtendedKeyUsageOID.SERVER_AUTH, ExtendedKeyUsageOID.CLIENT_AUTH]
        if name == "exchange-broker":
            usages = [ExtendedKeyUsageOID.CLIENT_AUTH]
        if name.endswith("-records"):
            usages = [ExtendedKeyUsageOID.SERVER_AUTH]
        cert = (certificate_builder(private.public_key(), ca.subject, subject, timedelta(days=7))
                .add_extension(x509.SubjectAlternativeName([x509.DNSName(name)]),critical=False)
                .add_extension(x509.ExtendedKeyUsage(usages),critical=False)
                .sign(key, hashes.SHA256()))
        write_secret(key_path, private.private_bytes(serialization.Encoding.PEM,
                     serialization.PrivateFormat.TraditionalOpenSSL,
                     serialization.NoEncryption()))
        write_secret(cert_path, cert.public_bytes(serialization.Encoding.PEM), 0o644)
    print("Local lab PKI ready. Only the init container can access the CA private key.")


if __name__ == "__main__":
    os.umask(0o077)
    ca_key, ca_cert = ensure_ca()
    issue(ca_key, ca_cert)
