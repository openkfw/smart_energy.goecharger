"""API controller configuration for go-e Charger Cloud integration"""

import logging

from homeassistant.helpers.typing import HomeAssistantType, ServiceCallType

from .const import API, CHARGERS_API, DOMAIN, INIT_STATE, CAR_STATUS, CHARGING_ALLOWED

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DictObj(dict):
    """
    Simple dict class to be able to have data attribute and direct access via dot notation.
    """

    def __init__(self):
        self.data = {}


def init_service_data(data: dict) -> DictObj:
    """
    Initialize Home Assistant service call dict with data attribute and initial values.
    """

    service_data = DictObj()
    service_data.data = data

    return service_data


async def fetch_status(hass: HomeAssistantType, charger_name: str) -> dict:
    """Fetch go-e Charger Cloud car status via API."""

    api = hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]
    fetched_status = await hass.async_add_executor_job(api.request_status)

    return fetched_status


async def start_charging(hass: HomeAssistantType, charger_name: str) -> dict:
    """Start charging of a car via API, no state refresh."""

    api = hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]
    await hass.async_add_executor_job(api.set_force_charging, True)


async def stop_charging(hass: HomeAssistantType, charger_name: str) -> dict:
    """Stop charging of a car via API, no state refresh."""

    api = hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]
    await hass.async_add_executor_job(api.set_force_charging, False)


class ChargerController:
    """Represents go-e Charger Cloud controller, abstracting API calls into methods."""

    def __init__(self, hass: HomeAssistantType) -> None:
        self._hass = hass

    def _is_charging_allowed(self, charger_name: str) -> bool:
        """
        Check if charging is allowed. If not, log an error and return False, otherwise return True
        """
        data = self._hass.data[DOMAIN][f"{charger_name}_coordinator"].data[charger_name]

        if (
            data[CHARGING_ALLOWED] == "off"
            or data[CAR_STATUS] == "Charger ready, no car connected"
        ):
            _LOGGER.error(
                """Charging for the %s is not allowed, please authenticate the car
                 to allow automated charging or connect the car""",
                charger_name,
            )
            return False

        return True

    async def start_charging(self, call: ServiceCallType) -> None:
        """Get name and assigned power from the service call and call the API accordingly.
        In case charging is not allowed, log a warning and early escape."""

        charger_name = call.data.get("device_name", None)
        charging_power = call.data.get("charging_power", None)
        api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]

        _LOGGER.debug(
            "Starting charging for the device=%s with power=%s",
            charger_name,
            charging_power,
        )

        if charging_power is not None:
            await self._hass.async_add_executor_job(api.set_max_current, charging_power)

        await self._hass.async_add_executor_job(api.set_force_charging, True)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()

    async def stop_charging(self, call: ServiceCallType) -> None:
        """Get name and assigned power from the service call and call the API accordingly.
        In case charging is not allowed, log a warning and early escape."""

        charger_name = call.data.get("device_name", None)
        api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]

        _LOGGER.debug("Stopping charging for the device=%s", charger_name)

        await self._hass.async_add_executor_job(api.set_force_charging, False)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()

    async def change_charging_power(self, call: ServiceCallType) -> None:
        """Get name and power from the service call and call the API accordingly.
        In case charging is not allowed, log an error and early escape."""

        charger_name = call.data.get("device_name", None)
        charging_power = call.data.get("charging_power", None)
        api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]

        _LOGGER.debug(
            "Changing charging power for the device=%s to power=%s",
            charger_name,
            charging_power,
        )

        await self._hass.async_add_executor_job(api.set_max_current, charging_power)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()

    async def set_phase(self, call: ServiceCallType) -> None:
        """Get name and phase from the service call and call the API accordingly.
        In case the phase value is not set correctly, log an error and early escape.
        Possible phase values: 0 (Auto), 1 (1-phased), 2 (3-phased)
        """

        charger_name = call.data.get("device_name", None)
        phase = call.data.get("phase", None)
        api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]

        if not phase in [0, 1, 2]:
            return

        _LOGGER.debug(
            "Setting phase for device=%s to %s",
            charger_name,
            phase,
        )

        await self._hass.async_add_executor_job(api.set_phase, phase)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()

    async def set_transaction(self, call: ServiceCallType) -> None:
        """Get name and status from the service call and call the API accordingly.
        In case the status value is not set correctly, log an error and early escape.
        Set wallbox transaction with possible values:
        - None (no transaction)
        - 0 (authenticate all users)
        """

        charger_name = call.data.get("device_name", None)
        status = call.data.get("status", None)
        api = self._hass.data[DOMAIN][INIT_STATE][CHARGERS_API][charger_name][API]

        if not status in [None, 0]:
            return

        _LOGGER.debug(
            "Setting transaction status for device=%s to %s",
            charger_name,
            status,
        )

        await self._hass.async_add_executor_job(api.set_transaction, status)
        await self._hass.data[DOMAIN][f"{charger_name}_coordinator"].async_refresh()
