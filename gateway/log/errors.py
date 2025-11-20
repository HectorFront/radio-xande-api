from schema.log_errors import LogErrors
from helpers import CrudHelper
from domain.http_response import HttpResponse

class LogErrorsGateway:

    @staticmethod
    def register_log(request):
        try:
            data = request.json
            log = LogErrors(
                url=data.get("url"),
                options=data.get("options"),
                status_code=int(data.get("status_code")),
                status_text=data.get("status_text"),
                error=data.get("error")
            )
            if CrudHelper.insert(log):
                CrudHelper.flush_to_database()
                CrudHelper.commit_to_database()
            return HttpResponse.ok()
        except Exception as err:
            return HttpResponse.internal_server_error("Internal server error", err)