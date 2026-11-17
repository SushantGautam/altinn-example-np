"""Negative security assertions executed INSIDE isolated Docker service networks."""
import socket
import sys

import httpx


def must_not_resolve(name):
    try:
        socket.getaddrinfo(name, 8000)
    except socket.gaierror:
        print("PASS: isolated DNS cannot resolve " + name)
    else:
        raise AssertionError("Private service is discoverable outside its network: " + name)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "broker":
        # An unauthenticated TLS client must not reach the agency API.
        try:
            response = httpx.get("https://transport-edge:8000/health",
                                 verify="/pki/ca.crt", timeout=3)
        except httpx.TransportError:
            print("PASS: agency edge rejected TLS handshake without a client certificate")
        else:
            assert response.status_code >= 400, response.status_code
            print("PASS: agency edge denied missing client certificate")
        must_not_resolve("transport-records")
    elif mode == "transport":
        must_not_resolve("civil-records")
        must_not_resolve("company-records")
    else:
        raise ValueError("Unknown network check mode")
