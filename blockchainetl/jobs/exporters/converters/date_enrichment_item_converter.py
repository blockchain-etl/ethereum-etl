from datetime import datetime


class DateEnrichmentItemConverter:

    def __init__(self, match_fields):
        self.match_field_names = set(match_fields)

    def convert_item(self, item):
        if not item:
            return item

        result = item
        for match_field_name in self.match_field_names:
            if match_field_name in item:
                result = item.copy()
                result['date'] = datetime.utcfromtimestamp(item[match_field_name]).today()
                return result
        return result
