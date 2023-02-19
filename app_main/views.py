import json

import requests
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app_main.automation import automate_usdot_free, automate_usdot_paid
from app_main.utils import automation_data

headers = {
    "charset": "utf-8",
    "Content-Type": "application/json",
}


class ResponseThen(Response):
    def __init__(
        self, data, then_callback, company_id, progress_id, auto_data, **kwargs
    ):
        super().__init__(data, **kwargs)
        self.company_id = company_id
        self.progress_id = progress_id
        self.auto_data = auto_data
        self.then_callback = then_callback

    def close(self):
        super().close()
        self.then_callback(self.company_id, self.progress_id, self.auto_data)


class GetAutomationDataApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        try:
            initial_data = request.data
            company_id = initial_data.get("company_id")
            progress_id = None
            is_automate_paid = "paid" in request.data

            data = automation_data(initial_data)

            # if not (ein and ssn):
            #     data['step_19']['ein'] = 345678747
            data['step_19']['ein'] = 345678456

            res = requests.post(
                settings.AUTOMATION_PROGRESS_URL,
                data=json.dumps({"company_id": company_id}),
                headers=headers,
            )

            if res.status_code == 201:
                progress_data = res.json()
                progress_id = progress_data.get("progress_id")

            if progress_id:
                if is_automate_paid:
                    print("paid automation start")
                    return ResponseThen(
                        {"message": "automation start", "status": 1, "type": "paid"},
                        automate_usdot_paid,
                        company_id=company_id,
                        progress_id=progress_id,
                        auto_data=data,
                    )
                else:
                    print("free automation start")
                    return ResponseThen(
                        {"message": "automation start", "status": 1, "type": "free"},
                        automate_usdot_free,
                        company_id=company_id,
                        progress_id=progress_id,
                        auto_data=data,
                    )
            else:
                return Response(
                    {"message": "Something went wrong !!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
