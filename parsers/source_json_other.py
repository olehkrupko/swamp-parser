from parsers.source_json import JsonSource


class OtherJsonSource(JsonSource):
    datetime_format = "%Y-%m-%dT%H:%M:%S"

    @classmethod
    def parse_each(cls, each):
        datetime_string = each["published"]
        if not datetime_string:
            datetime_string = each["added"]

        return {
            "name": each["title"],  # longer alternative: each["content"]
            "href": each["id"],
            "datetime": cls.strptime(datetime_string),
        }
