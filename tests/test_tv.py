"""Tests for lgtv.tv module."""

import pytest
from unittest.mock import MagicMock, patch

from lgtv.tv import TVController, TVConnectionError, TVAuthenticationError


class TestTVControllerInit:
    """Tests for TVController initialization."""

    def test_init_with_tv_name(self, sample_config, mock_webos_client):
        """TVController initializes with tv_name from config."""
        controller = TVController(sample_config, tv_name="living_room")

        assert controller.ip == "192.168.1.100"
        assert controller.tv_name == "living_room"
        assert controller.stored_key == "abc123key"

    def test_init_with_default_tv(self, sample_config, mock_webos_client):
        """TVController uses default TV when tv_name is None."""
        controller = TVController(sample_config, tv_name=None)

        assert controller.ip == "192.168.1.100"
        assert controller.tv_name == "living_room"

    def test_init_with_direct_ip(self, sample_config, mock_webos_client):
        """TVController accepts direct IP address."""
        controller = TVController(sample_config, ip="10.0.0.50")

        assert controller.ip == "10.0.0.50"
        assert controller.tv_name is None
        assert controller.stored_key is None

    def test_init_ip_overrides_tv_name(self, sample_config, mock_webos_client):
        """Direct IP overrides tv_name when both provided."""
        controller = TVController(sample_config, tv_name="living_room", ip="10.0.0.50")

        assert controller.ip == "10.0.0.50"
        assert controller.tv_name is None

    def test_init_tv_not_found(self, sample_config, mock_webos_client):
        """TVController raises error when TV not found in config."""
        with pytest.raises(TVConnectionError, match="TV 'nonexistent' not found"):
            TVController(sample_config, tv_name="nonexistent")

    def test_init_no_default_tv(self, empty_config, mock_webos_client):
        """TVController raises error when no default TV configured."""
        with pytest.raises(TVConnectionError, match="No default TV configured"):
            TVController(empty_config)

    def test_init_calls_connect(self, sample_config, mock_webos_client):
        """TVController calls WebOSClient.connect during init."""
        TVController(sample_config, tv_name="living_room")

        mock_webos_client.return_value.connect.assert_called()


class TestTVControllerConnect:
    """Tests for TVController connection logic."""

    def test_connect_tries_secure_first(self, sample_config):
        """_connect tries secure connection first."""
        with patch("lgtv.tv.WebOSClient") as MockClient:
            client_instance = MagicMock()
            MockClient.return_value = client_instance
            MockClient.REGISTERED = 1

            def register_side_effect(store):
                yield MockClient.REGISTERED

            client_instance.register.side_effect = register_side_effect

            TVController(sample_config, tv_name="living_room")

            # First call should be with secure=True
            first_call = MockClient.call_args_list[0]
            assert first_call[1].get("secure") is True

    def test_connect_falls_back_to_insecure(self, sample_config):
        """_connect falls back to insecure when secure fails."""
        with patch("lgtv.tv.WebOSClient") as MockClient:
            MockClient.REGISTERED = 1

            call_count = [0]

            def client_factory(*args, **kwargs):
                call_count[0] += 1
                client_instance = MagicMock()

                if kwargs.get("secure") is True:
                    # Secure connection fails
                    client_instance.connect.side_effect = ConnectionRefusedError()
                else:
                    # Insecure succeeds
                    client_instance.connect.return_value = None

                    def register_side_effect(store):
                        yield MockClient.REGISTERED

                    client_instance.register.side_effect = register_side_effect

                return client_instance

            MockClient.side_effect = client_factory

            TVController(sample_config, tv_name="living_room")

            # Should have tried twice
            assert call_count[0] == 2

    def test_connect_with_stored_key(self, sample_config, mock_webos_client):
        """_connect uses stored key for registration."""
        TVController(sample_config, tv_name="living_room")

        # Verify register was called
        mock_webos_client.return_value.register.assert_called()

    def test_connect_connection_refused(self, sample_config):
        """_connect raises TVConnectionError on connection refused."""
        with patch("lgtv.tv.WebOSClient") as MockClient:
            client_instance = MagicMock()
            client_instance.connect.side_effect = ConnectionRefusedError()
            MockClient.return_value = client_instance

            with pytest.raises(TVConnectionError, match="Connection refused"):
                TVController(sample_config, tv_name="living_room")

    def test_connect_connection_reset(self, sample_config):
        """_connect handles connection reset errors."""
        with patch("lgtv.tv.WebOSClient") as MockClient:
            client_instance = MagicMock()
            client_instance.connect.side_effect = OSError("Connection reset by peer")
            MockClient.return_value = client_instance

            with pytest.raises(TVConnectionError, match="Connection reset"):
                TVController(sample_config, tv_name="living_room")

    def test_connect_timeout(self, sample_config):
        """_connect raises TVConnectionError on timeout."""
        with patch("lgtv.tv.WebOSClient") as MockClient:
            client_instance = MagicMock()
            client_instance.connect.side_effect = TimeoutError()
            MockClient.return_value = client_instance

            with pytest.raises(TVConnectionError, match="Connection timeout"):
                TVController(sample_config, tv_name="living_room")


class TestTVControllerAuthentication:
    """Tests for TVController authentication."""

    def test_auth_stored_key_accepted(self, sample_config):
        """Authentication succeeds with valid stored key."""
        with patch("lgtv.tv.WebOSClient") as MockClient:
            client_instance = MagicMock()
            MockClient.return_value = client_instance
            MockClient.REGISTERED = 1

            def register_side_effect(store):
                yield MockClient.REGISTERED

            client_instance.register.side_effect = register_side_effect

            # Should not raise
            controller = TVController(sample_config, tv_name="living_room")
            assert controller.client is not None

    def test_auth_stored_key_rejected(self, sample_config):
        """Authentication raises error when stored key is rejected."""
        with patch("lgtv.tv.WebOSClient") as MockClient:
            client_instance = MagicMock()
            MockClient.return_value = client_instance
            MockClient.PROMPTED = 0
            MockClient.REGISTERED = 1

            def register_side_effect(store):
                yield MockClient.PROMPTED  # Key was rejected, prompting for new key

            client_instance.register.side_effect = register_side_effect

            # Note: The code wraps TVAuthenticationError in TVConnectionError
            # because the auth error happens during _connect()
            with pytest.raises(TVConnectionError, match="Stored key rejected"):
                TVController(sample_config, tv_name="living_room")

    def test_auth_error_during_register(self, sample_config):
        """Authentication raises error on registration failure."""
        with patch("lgtv.tv.WebOSClient") as MockClient:
            client_instance = MagicMock()
            MockClient.return_value = client_instance

            def register_side_effect(store):
                raise Exception("Registration failed")
                yield  # Never reached

            client_instance.register.side_effect = register_side_effect

            # Note: The code wraps TVAuthenticationError in TVConnectionError
            # because the auth error happens during _connect()
            with pytest.raises(TVConnectionError, match="Authentication failed"):
                TVController(sample_config, tv_name="living_room")


class TestTVControllerPair:
    """Tests for TVController.pair method."""

    def test_pair_success(self, sample_config, mock_webos_client):
        """pair() returns key on successful pairing."""
        controller = TVController(sample_config, ip="192.168.1.200")

        # Reset the mock register to simulate pairing
        def pair_register_side_effect(store):
            yield mock_webos_client.PROMPTED
            store["client_key"] = "new_pairing_key"
            yield mock_webos_client.REGISTERED

        mock_webos_client.return_value.register.side_effect = pair_register_side_effect

        key = controller.pair()
        assert key == "new_pairing_key"

    def test_pair_no_key_returned(self, sample_config, mock_webos_client):
        """pair() raises error when no key is returned."""
        controller = TVController(sample_config, ip="192.168.1.200")

        def pair_register_side_effect(store):
            yield mock_webos_client.REGISTERED
            # No key set in store

        mock_webos_client.return_value.register.side_effect = pair_register_side_effect

        with pytest.raises(TVAuthenticationError, match="no key received"):
            controller.pair()

    def test_pair_failure(self, sample_config, mock_webos_client):
        """pair() raises error on pairing failure."""
        controller = TVController(sample_config, ip="192.168.1.200")

        def pair_register_side_effect(store):
            raise Exception("User rejected pairing")
            yield

        mock_webos_client.return_value.register.side_effect = pair_register_side_effect

        with pytest.raises(TVAuthenticationError, match="Pairing failed"):
            controller.pair()


class TestTVControllerProperties:
    """Tests for TVController lazy-loaded properties."""

    def test_system_property_lazy_init(self, sample_config, mock_webos_client):
        """system property initializes SystemControl on first access."""
        with patch("lgtv.tv.SystemControl") as MockSystemControl:
            mock_system = MagicMock()
            MockSystemControl.return_value = mock_system

            controller = TVController(sample_config, tv_name="living_room")
            assert controller._system is None

            _ = controller.system  # Trigger lazy initialization
            MockSystemControl.assert_called_once()
            assert controller._system is not None

    def test_system_property_cached(self, sample_config, mock_webos_client):
        """system property returns cached instance."""
        with patch("lgtv.tv.SystemControl") as MockSystemControl:
            mock_system = MagicMock()
            MockSystemControl.return_value = mock_system

            controller = TVController(sample_config, tv_name="living_room")

            system1 = controller.system
            system2 = controller.system

            # Should only initialize once
            MockSystemControl.assert_called_once()
            assert system1 is system2

    def test_media_property(self, sample_config, mock_webos_client):
        """media property returns MediaControl."""
        with patch("lgtv.tv.MediaControl") as MockMediaControl:
            mock_media = MagicMock()
            MockMediaControl.return_value = mock_media

            controller = TVController(sample_config, tv_name="living_room")
            media = controller.media

            MockMediaControl.assert_called_once()
            assert media is mock_media

    def test_app_property(self, sample_config, mock_webos_client):
        """app property returns ApplicationControl."""
        with patch("lgtv.tv.ApplicationControl") as MockAppControl:
            mock_app = MagicMock()
            MockAppControl.return_value = mock_app

            controller = TVController(sample_config, tv_name="living_room")
            app = controller.app

            MockAppControl.assert_called_once()
            assert app is mock_app

    def test_input_property(self, sample_config, mock_webos_client):
        """input property returns InputControl."""
        with patch("lgtv.tv.InputControl") as MockInputControl:
            mock_input = MagicMock()
            MockInputControl.return_value = mock_input

            controller = TVController(sample_config, tv_name="living_room")
            inp = controller.input

            MockInputControl.assert_called_once()
            assert inp is mock_input

    def test_tv_property(self, sample_config, mock_webos_client):
        """tv property returns TvControl."""
        with patch("lgtv.tv.TvControl") as MockTvControl:
            mock_tv = MagicMock()
            MockTvControl.return_value = mock_tv

            controller = TVController(sample_config, tv_name="living_room")
            tv = controller.tv

            MockTvControl.assert_called_once()
            assert tv is mock_tv

    def test_source_property(self, sample_config, mock_webos_client):
        """source property returns SourceControl."""
        with patch("lgtv.tv.SourceControl") as MockSourceControl:
            mock_source = MagicMock()
            MockSourceControl.return_value = mock_source

            controller = TVController(sample_config, tv_name="living_room")
            source = controller.source

            MockSourceControl.assert_called_once()
            assert source is mock_source


class TestTVControllerDisconnect:
    """Tests for TVController.disconnect method."""

    def test_disconnect_calls_close(self, sample_config, mock_webos_client):
        """disconnect() calls client.close()."""
        controller = TVController(sample_config, tv_name="living_room")
        controller.disconnect()

        mock_webos_client.return_value.close.assert_called_once()

    def test_disconnect_handles_error(self, sample_config, mock_webos_client):
        """disconnect() handles errors gracefully."""
        mock_webos_client.return_value.close.side_effect = Exception("Close failed")

        controller = TVController(sample_config, tv_name="living_room")
        # Should not raise
        controller.disconnect()

    def test_disconnect_no_client(self, sample_config, mock_webos_client):
        """disconnect() handles case when client is None."""
        controller = TVController(sample_config, tv_name="living_room")
        controller.client = None
        # Should not raise
        controller.disconnect()


class TestTVControllerContextManager:
    """Tests for TVController context manager behavior."""

    def test_context_manager_enter(self, sample_config, mock_webos_client):
        """__enter__ returns the controller instance."""
        controller = TVController(sample_config, tv_name="living_room")

        with controller as ctx:
            assert ctx is controller

    def test_context_manager_exit_calls_disconnect(self, sample_config, mock_webos_client):
        """__exit__ calls disconnect()."""
        controller = TVController(sample_config, tv_name="living_room")

        with controller:
            pass

        mock_webos_client.return_value.close.assert_called()

    def test_context_manager_exit_on_exception(self, sample_config, mock_webos_client):
        """__exit__ calls disconnect() even on exception."""
        controller = TVController(sample_config, tv_name="living_room")

        with pytest.raises(ValueError):
            with controller:
                raise ValueError("Test error")

        mock_webos_client.return_value.close.assert_called()

    def test_context_manager_exit_returns_false(self, sample_config, mock_webos_client):
        """__exit__ returns False to propagate exceptions."""
        controller = TVController(sample_config, tv_name="living_room")

        result = controller.__exit__(None, None, None)
        assert result is False
