"""TV discovery service using SSDP and mDNS."""

import socket
import time
from typing import List, Dict, Optional
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener


class LGTVListener(ServiceListener):
    """Service listener for LG TV discovery via mDNS."""

    def __init__(self):
        self.tvs = []

    def add_service(self, zc: Zeroconf, type_: str, name: str):
        """Handle service discovery."""
        info = zc.get_service_info(type_, name)
        if info:
            addresses = [socket.inet_ntoa(addr) for addr in info.addresses]
            if addresses:
                tv_info = {
                    "name": name.split(".")[0],
                    "ip": addresses[0],
                    "port": info.port,
                    "type": type_,
                }
                self.tvs.append(tv_info)

    def remove_service(self, zc: Zeroconf, type_: str, name: str):
        """Handle service removal."""
        pass

    def update_service(self, zc: Zeroconf, type_: str, name: str):
        """Handle service update."""
        pass


def discover_ssdp(timeout: int = 3) -> List[Dict]:
    """Discover LG TVs using SSDP.

    Args:
        timeout: Discovery timeout in seconds

    Returns:
        List of discovered TVs with their information
    """
    tvs = []

    # SSDP discovery message
    ssdp_request = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: 239.255.255.250:1900\r\n"
        "MAN: \"ssdp:discover\"\r\n"
        "MX: 3\r\n"
        "ST: urn:lge-com:service:webos-second-screen:1\r\n"
        "\r\n"
    )

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(timeout)
        sock.sendto(ssdp_request.encode(), ("239.255.255.250", 1900))

        end_time = time.time() + timeout
        seen_ips = set()

        while time.time() < end_time:
            try:
                remaining = end_time - time.time()
                if remaining <= 0:
                    break

                sock.settimeout(max(0.1, remaining))
                data, addr = sock.recvfrom(65507)
                response = data.decode("utf-8", errors="ignore")

                # Parse response for LG TV
                if "LG" in response or "webOS" in response:
                    ip = addr[0]
                    if ip not in seen_ips:
                        seen_ips.add(ip)

                        # Try to extract model/name from response
                        model = None
                        for line in response.split("\r\n"):
                            if "SERVER:" in line or "Model:" in line:
                                model = line.split(":", 1)[1].strip()
                                break

                        tvs.append({
                            "ip": ip,
                            "model": model,
                            "discovery_method": "SSDP",
                        })

            except socket.timeout:
                break
            except Exception:
                continue

        sock.close()

    except Exception:
        pass

    return tvs


def discover_mdns(timeout: int = 3) -> List[Dict]:
    """Discover LG TVs using mDNS/Zeroconf.

    Args:
        timeout: Discovery timeout in seconds

    Returns:
        List of discovered TVs with their information
    """
    tvs = []

    try:
        zeroconf = Zeroconf()
        listener = LGTVListener()

        # Look for webOS TVs
        browser = ServiceBrowser(
            zeroconf,
            "_webostv._tcp.local.",
            listener
        )

        time.sleep(timeout)

        browser.cancel()
        zeroconf.close()

        for tv in listener.tvs:
            tvs.append({
                "ip": tv["ip"],
                "name": tv.get("name"),
                "port": tv.get("port", 3000),
                "discovery_method": "mDNS",
            })

    except Exception:
        pass

    return tvs


def discover_tvs(timeout: int = 5) -> List[Dict]:
    """Discover LG TVs on the network using multiple methods.

    Args:
        timeout: Discovery timeout in seconds

    Returns:
        List of discovered TVs with their information
    """
    all_tvs = []
    seen_ips = set()

    # Try mDNS first
    mdns_tvs = discover_mdns(timeout)
    for tv in mdns_tvs:
        ip = tv["ip"]
        if ip not in seen_ips:
            seen_ips.add(ip)
            all_tvs.append(tv)

    # Try SSDP
    ssdp_tvs = discover_ssdp(timeout)
    for tv in ssdp_tvs:
        ip = tv["ip"]
        if ip not in seen_ips:
            seen_ips.add(ip)
            all_tvs.append(tv)

    # Also try the default hostname
    try:
        default_ip = socket.gethostbyname("lgsmarttv.lan")
        if default_ip not in seen_ips:
            all_tvs.append({
                "ip": default_ip,
                "name": "lgsmarttv.lan",
                "discovery_method": "hostname",
            })
    except socket.gaierror:
        pass

    return all_tvs
