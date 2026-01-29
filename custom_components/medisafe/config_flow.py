import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import MedisafeApiClient
from .const import CONF_PASSWORD
from .const import CONF_USERNAME
from .const import DOMAIN

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for medisafe."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        self._errors = {}

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            if valid:
                if (
                    self.source == config_entries.SOURCE_RECONFIGURE
                    or self.source == config_entries.SOURCE_REAUTH
                ):
                    return self.async_update_reload_and_abort(
                        self.hass.config_entries.async_get_entry(
                            self.context["entry_id"]
                        ),
                        data=user_input,
                    )
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )

            self._errors["base"] = "auth"

        return await self._show_config_form(user_input)

    async def async_step_reconfigure(self, user_input=None):
        self._errors = {}
        return await self._show_config_form(user_input)

    async def async_step_reauth(self, user_input=None):
        self._errors = {}
        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=self._errors,
            description_placeholders={
                "medisafe_url": "https://web.medisafe.com/",
                "docs_url": "https://github.com/keally1123/medisafe",
            },
        )

    async def _test_credentials(self, username, password):
        """Return true if credentials are valid."""
        try:
            client = MedisafeApiClient(
                username, password, async_create_clientsession(self.hass)
            )
            await client.async_get_data()
            return True
        except Exception:
            return False
