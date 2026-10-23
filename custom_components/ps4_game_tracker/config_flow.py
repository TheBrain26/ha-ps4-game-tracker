from homeassistant import config_entries
from homeassistant.helpers import selector
import voluptuous as vol
from .const import DOMAIN, CONF_MEDIA_PLAYER
from homeassistant.util import dt as dt_util
from .legacy import HELPER_DOMAINS, snapshot_helpers

class PS4GameTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            entity_id = user_input[CONF_MEDIA_PLAYER]
            await self.async_set_unique_id(entity_id)
            self._abort_if_unique_id_configured()
            self._player = entity_id
            if user_input.get("import_legacy"):
                return await self.async_step_legacy()
            return self.async_create_entry(
                title="PS4 Game Tracker", data={CONF_MEDIA_PLAYER: entity_id}
            )
        schema = vol.Schema({
            vol.Required(CONF_MEDIA_PLAYER): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="media_player")
            ),
            vol.Optional("import_legacy", default=False): bool,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_legacy(self, user_input=None):
        errors = {}
        if user_input is not None:
            state = self.hass.states.get(self._player)
            if not user_input.get("console_idle") or (
                state is not None and state.state == "playing"
            ):
                errors["base"] = "console_not_idle"
            else:
                states = {}
                for key in HELPER_DOMAINS:
                    helper = self.hass.states.get(user_input[key])
                    if helper is not None:
                        states[key] = helper.state
                try:
                    snapshot = snapshot_helpers(states, dt_util.now())
                except ValueError as err:
                    errors["base"] = str(err)
                else:
                    return self.async_create_entry(
                        title="PS4 Game Tracker",
                        data={CONF_MEDIA_PLAYER: self._player,
                              "legacy_snapshot": snapshot},
                    )
        fields = {
            vol.Required(key): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=domain)
            ) for key, domain in HELPER_DOMAINS.items()
        }
        fields[vol.Required("console_idle", default=False)] = bool
        return self.async_show_form(
            step_id="legacy", data_schema=vol.Schema(fields), errors=errors
        )

