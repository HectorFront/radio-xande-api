class FieldsHelper:
    
    @staticmethod
    def is_valid_field(value):
        return value is not None or str(value).strip() != ""
    
    @staticmethod
    def is_valid_field_with_optional_fields(key, value, fields_optional = []):
        if (key not in fields_optional and FieldsHelper.is_valid_field(value)) or key in fields_optional:
            return True
        return False