"""Integration for the Bring! Shopping List"""
import logging
from datetime import timedelta
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_NAME
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.bring_shopping_list.const import CONF_LOCALE, CONF_LISTS, DEFAULT_LOCALE, SENSOR_PREFIX, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup(hass, config):
    """Platform setup, do nothing."""
    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Load the saved entities."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    list_id = entry.data[CONF_LISTS]
    name = entry.data.get(CONF_NAME, list_id)
    locale = entry.data(CONF_LOCALE, DEFAULT_LOCALE)

    coordinator = BringDataUpdateCoordinator(hass, username, password, list_id, name, locale)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=f"{SENSOR_PREFIX}{list_id}")

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")


class BringDataUpdateCoordinator(DataUpdateCoordinator[int]):
    """Class to manage fetching shopping list data from endpoint."""

    def __init__(self, hass, username, password, list_id, name, locale):
        """Initialize Bring data updater."""
        self.username = username
        self.password = password
        self.list_id = list_id
        self.locale = locale
        self.name = name

        self.items = []

        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> Optional[int]:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        # self._items = []
        # self._recently = []
        # # get articles US
        # url = f"https://web.getbring.com/locale/articles.{self._locale}.json"
        # articles = get(url=url).json()
        #
        # url = f"https://api.getbring.com/rest/bringlists/{self._listId}/details"
        # details = get(url=url).json()
        #
        # url = f'https://api.getbring.com/rest/bringlists/{self._listId}'
        # data = get(url=url).json()

        purchase = data["purchase"]
        recently = data["recently"]

        self._purchase = self._get_list(purchase, details, articles)
        self._recently = self._get_list(recently, details, articles)

        return len(purchase)

    def _get_list(self, source=None, details=None, articles=None):
        if articles is None:
            articles = []
        items = []
        for p in source:
            found = False
            for d in details:
                if p["name"] == d["itemId"]:
                    found = True
                    break

            item = {"image": p["name"],
                    "name": p["name"],
                    "specification": p["specificitemation"]}

            if found:
                item["image"] = d["userIconItemId"]

            item["key"] = item["image"]

            if item["name"] in articles:
                item["name"] = articles[item["name"]]
            else:
                if found == 0:
                    item["image"] = item["name"][0]

            item["image"] = self._purge(item["image"])

            if "+" in item["specification"]:
                specs = item["specification"].split("+")

                for spec in specs:
                    temp = dict(item.items())
                    temp["specification"] = spec.strip()
                    items.append(temp)

            else:
                items.append(item)

        return items

    @staticmethod
    def _purge(item):
        return item.lower() \
            .replace("é", "e") \
            .replace("ä", "ae") \
            .replace("-", "_") \
            .replace("ö", "oe") \
            .replace("ü", "ue") \
            .replace(" ", "_")
