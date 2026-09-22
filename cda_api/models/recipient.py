from dataclasses import dataclass

from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.models.organization import Organization, OrganizationParser
from cda_api.models.person import Person, PersonParser
from cda_api.utils import NullObject, Parser


@dataclass(frozen=True)
class Recipient(Person):
    template_id: list[ExtId]
    id: list[ExtId]
    received_organization: Organization | None


class RecipientParser(Parser):
    def _parse(self) -> list[Recipient]:
        self.ensure_raw_is_list()
        recipients = []
        for d in self.raw:
            rec = d["intendedRecipient"]
            person = NullObject()
            if "informationRecipient" in rec.keys():
                person = PersonParser(rec).parse(key="informationRecipient")[0]
            orga = None
            if "receivedOrganization" in rec.keys():
                orga = OrganizationParser(rec["receivedOrganization"]).parse()
            recipients.append(
                Recipient(
                    id=ExtIdParser(rec.get("id")).parse(),
                    template_id=ExtIdParser(rec.get("templateId")).parse(),
                    name=person.name,
                    address=person.address,
                    telecom=person.telecom,
                    received_organization=orga,
                )
            )
        return recipients
