from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.models.ext_id import ExtId, ExtIdParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Pharm:
    # TODO: make these dicts objects
    form_code: dict | None
    as_specialized_kind: Code | None
    ingredient: dict | None


@dataclass(frozen=True)
class Consumable:
    type_code: str | None
    class_code: str | None
    template_id: list[ExtId]
    determiner_code: str | None
    code: Code | None  # TODO: handle originalText
    name: str
    pharm: Pharm | None
    # lotNumberText: None  # always nullFlavor in examples


class ConsumableParser(Parser):
    def _parse(self) -> Consumable:
        product = self.raw.get("manufacturedProduct", {}).get("manufacturedMaterials", {})
        return Consumable(
            type_code=self.raw.get("@typeCode"),
            class_code=self.raw.get("manufacturedProduct", {}).get("@classCode"),
            template_id=ExtIdParser(
                self.raw.get("manufacturedProduct", {}).get("templateId")
            ).parse()
            + ExtIdParser(product.get("templateId")).parse(),
            code=CodeParser(product.get("code")).parse(),
            name=product.get("name"),
            determiner_code=product.get("@determinerCode"),
            pharm=(
                Pharm(
                    form_code=product.get("pharm:formCode"),
                    as_specialized_kind=product.get("pharm:asSpecializeKind"),
                    ingredient=product.get("pharm:ingredient"),
                )
                if any(k.startswith("pharm:") for k in product)
                else None
            ),
        )
