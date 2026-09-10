from dataclasses import dataclass
from datetime import datetime

from cda_api.models.code import Code, CodeParser
from cda_api.models.device import Device, DeviceParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.organization import Organization, OrganizationParser
from cda_api.models.person import Person, PersonParser
from cda_api.utils import NullObject, Parser, parse_time


@dataclass(frozen=True)
class Assigned(Person, Device):
    class_code: str | None
    code: Code | None
    context_control_code: str | None
    id: list[ExtId]
    represented_organization: Organization | None
    time: datetime | None
    type_code: str | None


class AssignedParser(Parser):
    _default_parsing_value = []

    def _parse(
        self,
        assigned_key: str,
        person_key: str = "assignedPerson",
        device_key: str | None = None,
    ) -> list[Assigned]:
        self.ensure_raw_is_list()
        res = []
        for a in self.raw:
            assigned = a[assigned_key]
            if assigned.get(person_key):
                person = PersonParser(assigned).parse(key=person_key)[0]
                device = NullObject()
            elif device_key:
                device = DeviceParser(assigned).parse(key=device_key)
                person = NullObject()
            else:
                raise TypeError(f"Could not get the assignee for {assigned}")
            res.append(
                Assigned(
                    class_code=assigned.get("@classCode"),
                    code=CodeParser(a.get("code")).parse(),
                    time=parse_time(t["@value"]) if (t := a.get("time")) else None,
                    context_control_code=a.get("@contextControlCode"),
                    type_code=a.get("@typeCode"),
                    name=person.name,
                    address=person.address,
                    telecom=person.telecom,
                    id=ExtIdParser(assigned["id"]).parse(),
                    represented_organization=OrganizationParser(
                        assigned.get("representedOrganization")
                    ).parse(),
                    manufacturer_model_name=device.manufacturer_model_name,
                    software_name=device.software_name,
                )
            )
        return res
