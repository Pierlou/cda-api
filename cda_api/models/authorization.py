from dataclasses import dataclass

from cda_api.models.code import Code, CodeParser
from cda_api.utils import Parser, get


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
            content = auth.get("consent", {})
            auths.append(
                Authorization(
                    type_code=auth.get("@typeCode"),
                    class_code=content.get("@classCode"),
                    mood_code=content.get("@moodCode"),
                    code=CodeParser(content.get("code")).parse(),
                    status_code=CodeParser(content.get("statusCode")).parse(),
                )
            )
        return auths
