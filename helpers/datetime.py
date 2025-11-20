from dateutil import parser

class ServiceDatetime:
    
    @staticmethod
    def is_valid_datetime(date_string):
        try:
            # Attempt to parse the date string
            parser.parse(date_string)
            return True
        except (ValueError, OverflowError):
            return False