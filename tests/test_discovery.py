"""Tests for lgtv.discovery module."""

import socket
import time
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from lgtv.discovery import (
    LGTVListener,
    discover_ssdp,
    discover_mdns,
    discover_tvs,
)


class TestLGTVListener:
    """Tests for LGTVListener class."""

    def test_listener_init(self):
        """LGTVListener initializes with empty tvs list."""
        listener = LGTVListener()
        assert listener.tvs == []

    def test_add_service(self):
        """add_service adds discovered TV to tvs list."""
        listener = LGTVListener()
        mock_zc = MagicMock()

        # Mock service info
        mock_info = MagicMock()
        mock_info.addresses = [b"\xc0\xa8\x01\x64"]  # 192.168.1.100
        mock_info.port = 3000
        mock_zc.get_service_info.return_value = mock_info

        listener.add_service(mock_zc, "_webostv._tcp.local.", "LG TV._webostv._tcp.local.")

        assert len(listener.tvs) == 1
        assert listener.tvs[0]["ip"] == "192.168.1.100"
        assert listener.tvs[0]["port"] == 3000
        assert listener.tvs[0]["name"] == "LG TV"

    def test_add_service_no_info(self):
        """add_service handles missing service info."""
        listener = LGTVListener()
        mock_zc = MagicMock()
        mock_zc.get_service_info.return_value = None

        listener.add_service(mock_zc, "_webostv._tcp.local.", "LG TV._webostv._tcp.local.")

        assert len(listener.tvs) == 0

    def test_add_service_no_addresses(self):
        """add_service handles service with no addresses."""
        listener = LGTVListener()
        mock_zc = MagicMock()

        mock_info = MagicMock()
        mock_info.addresses = []
        mock_zc.get_service_info.return_value = mock_info

        listener.add_service(mock_zc, "_webostv._tcp.local.", "LG TV._webostv._tcp.local.")

        assert len(listener.tvs) == 0

    def test_remove_service(self):
        """remove_service does nothing (placeholder implementation)."""
        listener = LGTVListener()
        # Should not raise
        listener.remove_service(MagicMock(), "_webostv._tcp.local.", "LG TV")

    def test_update_service(self):
        """update_service does nothing (placeholder implementation)."""
        listener = LGTVListener()
        # Should not raise
        listener.update_service(MagicMock(), "_webostv._tcp.local.", "LG TV")


class TestDiscoverSsdp:
    """Tests for discover_ssdp function."""

    def test_discover_ssdp_finds_tv(self):
        """discover_ssdp returns discovered TVs."""
        with patch("lgtv.discovery.socket.socket") as MockSocket:
            mock_sock = MagicMock()
            MockSocket.return_value = mock_sock

            # Simulate receiving an LG TV response
            response = (
                "HTTP/1.1 200 OK\r\n"
                "SERVER: webOS/4.0 UPnP/1.0 LG WebOSTV/1.0\r\n"
                "LOCATION: http://192.168.1.100:1925/\r\n"
                "\r\n"
            ).encode()

            mock_sock.recvfrom.side_effect = [
                (response, ("192.168.1.100", 1900)),
                socket.timeout(),
            ]

            tvs = discover_ssdp(timeout=1)

            assert len(tvs) == 1
            assert tvs[0]["ip"] == "192.168.1.100"
            assert tvs[0]["discovery_method"] == "SSDP"

    def test_discover_ssdp_sends_search_request(self):
        """discover_ssdp sends SSDP M-SEARCH request."""
        with patch("lgtv.discovery.socket.socket") as MockSocket:
            mock_sock = MagicMock()
            MockSocket.return_value = mock_sock
            mock_sock.recvfrom.side_effect = socket.timeout()

            discover_ssdp(timeout=1)

            # Verify sendto was called with SSDP multicast address
            mock_sock.sendto.assert_called_once()
            args = mock_sock.sendto.call_args[0]
            assert b"M-SEARCH" in args[0]
            assert args[1] == ("239.255.255.250", 1900)

    def test_discover_ssdp_multiple_tvs(self):
        """discover_ssdp deduplicates multiple responses from same TV."""
        with patch("lgtv.discovery.socket.socket") as MockSocket:
            mock_sock = MagicMock()
            MockSocket.return_value = mock_sock

            response = b"HTTP/1.1 200 OK\r\nSERVER: LG WebOSTV\r\n\r\n"

            # Same TV responds twice
            mock_sock.recvfrom.side_effect = [
                (response, ("192.168.1.100", 1900)),
                (response, ("192.168.1.100", 1900)),
                socket.timeout(),
            ]

            tvs = discover_ssdp(timeout=1)

            # Should only have one entry
            assert len(tvs) == 1

    def test_discover_ssdp_filters_non_lg_responses(self):
        """discover_ssdp filters out non-LG responses."""
        with patch("lgtv.discovery.socket.socket") as MockSocket:
            mock_sock = MagicMock()
            MockSocket.return_value = mock_sock

            # Non-LG response
            response = b"HTTP/1.1 200 OK\r\nSERVER: Some Other Device\r\n\r\n"

            mock_sock.recvfrom.side_effect = [
                (response, ("192.168.1.200", 1900)),
                socket.timeout(),
            ]

            tvs = discover_ssdp(timeout=1)

            assert len(tvs) == 0

    def test_discover_ssdp_handles_errors(self):
        """discover_ssdp handles socket errors gracefully."""
        with patch("lgtv.discovery.socket.socket") as MockSocket:
            MockSocket.side_effect = OSError("Network error")

            # Should not raise, returns empty list
            tvs = discover_ssdp(timeout=1)
            assert tvs == []

    def test_discover_ssdp_extracts_model(self):
        """discover_ssdp extracts model from SERVER header."""
        with patch("lgtv.discovery.socket.socket") as MockSocket:
            mock_sock = MagicMock()
            MockSocket.return_value = mock_sock

            response = b"HTTP/1.1 200 OK\r\nSERVER: webOS/5.0 OLED65C1\r\n\r\n"

            mock_sock.recvfrom.side_effect = [
                (response, ("192.168.1.100", 1900)),
                socket.timeout(),
            ]

            tvs = discover_ssdp(timeout=1)

            assert len(tvs) == 1
            assert tvs[0]["model"] == "webOS/5.0 OLED65C1"


class TestDiscoverMdns:
    """Tests for discover_mdns function."""

    def test_discover_mdns_setup(self):
        """discover_mdns sets up Zeroconf browser."""
        with patch("lgtv.discovery.Zeroconf") as MockZeroconf, \
             patch("lgtv.discovery.ServiceBrowser") as MockBrowser, \
             patch("lgtv.discovery.time.sleep"):
            mock_zc = MagicMock()
            MockZeroconf.return_value = mock_zc

            discover_mdns(timeout=1)

            MockZeroconf.assert_called_once()
            MockBrowser.assert_called_once()
            # Should browse for webostv service
            assert "_webostv._tcp.local." in str(MockBrowser.call_args)

    def test_discover_mdns_returns_tvs(self):
        """discover_mdns returns TVs discovered by listener."""
        with patch("lgtv.discovery.Zeroconf") as MockZeroconf, \
             patch("lgtv.discovery.ServiceBrowser") as MockBrowser, \
             patch("lgtv.discovery.time.sleep"), \
             patch("lgtv.discovery.LGTVListener") as MockListener:
            mock_zc = MagicMock()
            MockZeroconf.return_value = mock_zc

            mock_listener = MagicMock()
            mock_listener.tvs = [
                {"ip": "192.168.1.100", "name": "Living Room TV", "port": 3000}
            ]
            MockListener.return_value = mock_listener

            tvs = discover_mdns(timeout=1)

            assert len(tvs) == 1
            assert tvs[0]["ip"] == "192.168.1.100"
            assert tvs[0]["discovery_method"] == "mDNS"

    def test_discover_mdns_handles_errors(self):
        """discover_mdns handles errors gracefully."""
        with patch("lgtv.discovery.Zeroconf") as MockZeroconf:
            MockZeroconf.side_effect = Exception("mDNS error")

            # Should not raise
            tvs = discover_mdns(timeout=1)
            assert tvs == []

    def test_discover_mdns_closes_resources(self):
        """discover_mdns closes Zeroconf and cancels browser."""
        with patch("lgtv.discovery.Zeroconf") as MockZeroconf, \
             patch("lgtv.discovery.ServiceBrowser") as MockBrowser, \
             patch("lgtv.discovery.time.sleep"):
            mock_zc = MagicMock()
            MockZeroconf.return_value = mock_zc

            mock_browser = MagicMock()
            MockBrowser.return_value = mock_browser

            discover_mdns(timeout=1)

            mock_browser.cancel.assert_called_once()
            mock_zc.close.assert_called_once()


class TestDiscoverTvs:
    """Tests for discover_tvs function."""

    def test_discover_tvs_combines_methods(self):
        """discover_tvs combines results from mDNS and SSDP."""
        with patch("lgtv.discovery.discover_mdns") as mock_mdns, \
             patch("lgtv.discovery.discover_ssdp") as mock_ssdp, \
             patch("lgtv.discovery.socket.gethostbyname") as mock_dns:
            mock_mdns.return_value = [
                {"ip": "192.168.1.100", "discovery_method": "mDNS"}
            ]
            mock_ssdp.return_value = [
                {"ip": "192.168.1.101", "discovery_method": "SSDP"}
            ]
            mock_dns.side_effect = socket.gaierror()

            tvs = discover_tvs(timeout=1)

            assert len(tvs) == 2
            ips = [tv["ip"] for tv in tvs]
            assert "192.168.1.100" in ips
            assert "192.168.1.101" in ips

    def test_discover_tvs_deduplicates(self):
        """discover_tvs deduplicates TVs found by multiple methods."""
        with patch("lgtv.discovery.discover_mdns") as mock_mdns, \
             patch("lgtv.discovery.discover_ssdp") as mock_ssdp, \
             patch("lgtv.discovery.socket.gethostbyname") as mock_dns:
            # Same TV found by both methods
            mock_mdns.return_value = [
                {"ip": "192.168.1.100", "discovery_method": "mDNS"}
            ]
            mock_ssdp.return_value = [
                {"ip": "192.168.1.100", "discovery_method": "SSDP"}
            ]
            mock_dns.side_effect = socket.gaierror()

            tvs = discover_tvs(timeout=1)

            # Should only have one entry (from mDNS since it's tried first)
            assert len(tvs) == 1
            assert tvs[0]["ip"] == "192.168.1.100"

    def test_discover_tvs_tries_default_hostname(self):
        """discover_tvs tries resolving lgsmarttv.lan."""
        with patch("lgtv.discovery.discover_mdns") as mock_mdns, \
             patch("lgtv.discovery.discover_ssdp") as mock_ssdp, \
             patch("lgtv.discovery.socket.gethostbyname") as mock_dns:
            mock_mdns.return_value = []
            mock_ssdp.return_value = []
            mock_dns.return_value = "192.168.1.50"

            tvs = discover_tvs(timeout=1)

            mock_dns.assert_called_once_with("lgsmarttv.lan")
            assert len(tvs) == 1
            assert tvs[0]["ip"] == "192.168.1.50"
            assert tvs[0]["name"] == "lgsmarttv.lan"
            assert tvs[0]["discovery_method"] == "hostname"

    def test_discover_tvs_hostname_not_found(self):
        """discover_tvs handles hostname resolution failure."""
        with patch("lgtv.discovery.discover_mdns") as mock_mdns, \
             patch("lgtv.discovery.discover_ssdp") as mock_ssdp, \
             patch("lgtv.discovery.socket.gethostbyname") as mock_dns:
            mock_mdns.return_value = []
            mock_ssdp.return_value = []
            mock_dns.side_effect = socket.gaierror()

            # Should not raise
            tvs = discover_tvs(timeout=1)
            assert tvs == []

    def test_discover_tvs_hostname_not_duplicate(self):
        """discover_tvs doesn't add hostname if IP already discovered."""
        with patch("lgtv.discovery.discover_mdns") as mock_mdns, \
             patch("lgtv.discovery.discover_ssdp") as mock_ssdp, \
             patch("lgtv.discovery.socket.gethostbyname") as mock_dns:
            mock_mdns.return_value = [
                {"ip": "192.168.1.50", "discovery_method": "mDNS"}
            ]
            mock_ssdp.return_value = []
            mock_dns.return_value = "192.168.1.50"  # Same IP

            tvs = discover_tvs(timeout=1)

            # Should only have one entry
            assert len(tvs) == 1
