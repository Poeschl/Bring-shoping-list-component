import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_USERNAME, CONF_ID, EVENT_HOMEASSISTANT_START
from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.bring_shopping_list.const import CONF_LISTS, CONF_LOCALE, DEFAULT_LOCALE, DOMAIN, SENSOR_PREFIX

ICON = "mdi:cart"
ICONEMPTY = "mdi:cart-outline"

LOGGER = logging.getLogger(__name__)

LIST_SCHEMA = vol.Schema({
    vol.Required(CONF_ID): cv.matches_regex('^.{9}-.{4}-.{4}-.{4}-.{12}$'),
    vol.Optional(CONF_NAME, default=''): cv.string,
    vol.Optional(CONF_LOCALE, default=DEFAULT_LOCALE): cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_LISTS): vol.All(cv.ensure_list, vol.Schema(LIST_SCHEMA)),
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Bring! shopping list sensor."""

    @callback
    def schedule_import(_):
        """Schedule delayed import after HA is fully started."""
        async_call_later(hass, 10, do_import)

    @callback
    def do_import(_):
        """Process YAML import."""
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=dict(config)
            )
        )

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, schedule_import)


async def async_setup_entry(hass, entry, async_add_entities):
    """Add Bring! shopping list entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        BringSensor(coordinator)
    ]

    async_add_entities(sensors, True)


class BringSensor(CoordinatorEntity):

    @property
    def name(self):
        """Return the name of the sensor."""
        return SENSOR_PREFIX + self.coordinator.name

    @property
    def state(self):
        """Return the state of the sensor."""
        return len(self.coordinator.items)

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return ICON if len(self.coordinator.items) > 0 else ICONEMPTY

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {"Purchase": self.coordinator.items,
                 "List_Id": self.coordinator.list_id}
        return attrs
