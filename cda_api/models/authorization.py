from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.utils import Parser


@dataclass(frozen=True)
class Authorization:
    type_code: str | None
    class_code: str | None
    mood_code: str | None
    code: Code | None
    status_code: Code | None


class AuthorizationParser(Parser):
    def _parse(self) -> list[Authorization]:
        self.ensure_raw_is_list()
        auths = []
        for auth in self.raw:
            consent = auth.get("consent", {})
            auths.append(
                Authorization(
                    type_code=auth.get("@typeCode"),
                    class_code=consent.get("@classCode"),
                    mood_code=consent.get("@moodCode"),
                    code=CodeParser(consent.get("code")).parse(),
                    status_code=CodeParser(consent.get("statusCode")).parse(),
                )
            )
        return auths
