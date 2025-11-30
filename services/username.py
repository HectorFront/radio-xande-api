from model.user import UserModel

class ServiceUsername:
    
    @staticmethod
    def username_existing(username: str):
        return UserModel.get_by_username(username)
    
    @staticmethod
    def create_username(name: str):
        format_username = "".join(str(name).split(" ")[:2]).lower()
        if not ServiceUsername.username_existing(format_username):
            return format_username
        count = UserModel.get_count_users_by_username_pattern(format_username)
        return f"{format_username}{count + 1}"
        