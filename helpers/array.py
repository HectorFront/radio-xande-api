from array import array

class ArrayHelper:
    
    @staticmethod
    def reverse_list_json(list):
        return list[::-1]
    
    @staticmethod
    def is_array(data):
        return isinstance(data, (list, array))