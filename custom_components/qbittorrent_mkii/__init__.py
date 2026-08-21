"""The qbittorrent component."""
from datetime import timedelta

from qbittorrentapi import Client, APIConnectionError, LoginFailed, HTTPError, Forbidden403Error, InternalServerError500Error 
from requests.exceptions import RequestException, ConnectTimeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_PORT,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed
from homeassistant.helpers.event import async_track_time_interval

from .const import *
from .helpers import create_client, login_client
from .events import QBEventsAndActions

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up qBittorrent from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = await hass.async_add_executor_job(
        create_client,
        config_entry.data[CONF_URL],
        config_entry.data[CONF_VERIFY_SSL],
    )
    hass.data[DOMAIN][config_entry.entry_id] = client

    event_handler = QBEventsAndActions(hass, config_entry)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    try:
        hass.data[DOMAIN][CONF_EVENT_SCAN_INTERVAL]()

    except:
        pass

    hass.data[DOMAIN][CONF_EVENT_SCAN_INTERVAL] = async_track_time_interval(
        hass, event_handler.raise_events,
        timedelta(seconds=config_entry.options.get(CONF_EVENT_SCAN_INTERVAL, DEFAULT_EVENT_SCAN_INTERVAL))
    )

    async def _try_initial_login() -> None:
        try:
            await hass.async_add_executor_job(
                login_client,
                client,
                config_entry.data[CONF_USERNAME],
                config_entry.data[CONF_PASSWORD],
            )
        except LoginFailed:
            hass.add_job(config_entry.async_start_reauth, hass)
        except Exception as ex:
            _LOGGER.warning(f"Could not log in to qBittorrent at startup: {ex}")

    config_entry.async_create_background_task(
        hass, _try_initial_login(), "qbittorrent_initial_login"
    )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload qBittorrent config entry."""

    try:
        hass.data[DOMAIN][config_entry.entry_id].auth_log_out()
    except:
        pass

    if unload_ok := await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS):
        del hass.data[DOMAIN][config_entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]

    return unload_ok
