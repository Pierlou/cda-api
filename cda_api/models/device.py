from dataclasses import dataclass

from cda_api.utils import Parser, get


@dataclass(frozen=True)
class Device:
    manufacturer_model_name: str
    software_name: str


class DeviceParser(Parser):
    def _parse(self, key: str) -> Device:
        return Device(
            manufacturer_model_name=get(self.raw, f"{key}.manufacturerModelName"),
            software_name=get(self.raw, f"{key}.softwareName"),
        )
