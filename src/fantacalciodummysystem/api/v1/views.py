# SPDX-License-Identifier: AGPL-3.0-only

from django.db import Error, connection
from django.http import HttpRequest, HttpResponse
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from fantacalciodummysystem.accounts import views as auth_views
from fantacalciodummysystem.accounts.models import User

from ..problems import MEDIA_TYPE, problem, problem_data
from .serializers import DisplayNameSerializer, HealthSerializer


class ProfilePatchView(APIView):
    # Authentication and permissions intentionally inherited from REST_FRAMEWORK.
    http_method_names = ["patch"]

    def patch(self, request: Request) -> Response:
        user = request.user
        if not isinstance(user, User):
            raise NotAuthenticated()
        serializer = DisplayNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.display_name = serializer.validated_data["display_name"]
        user.save(update_fields=["display_name"])
        return Response(
            {"id": str(user.pk), "email": user.email, "display_name": user.display_name}
        )


_profile_patch = ProfilePatchView.as_view()


def me(request: HttpRequest) -> HttpResponse:
    # Do not expose the csrf_exempt attribute of DRF's as_view wrapper: Django
    # middleware must still check unsafe methods, including anonymous requests.
    if request.method == "GET":
        return auth_views.me(request)
    if request.method == "PATCH":
        return _profile_patch(request)
    response = problem("method_not_allowed", 405)
    response["Allow"] = "GET, PATCH"
    return response


class LivenessView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ["get"]
    serializer_class = HealthSerializer

    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})


class ReadinessView(LivenessView):
    def get(self, request: Request) -> Response:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                if cursor.fetchone() != (1,):
                    return self.unavailable()
        except Error:
            return self.unavailable()
        return Response({"status": "ok"})

    @staticmethod
    def unavailable() -> Response:
        return Response(
            problem_data("service_unavailable", 503),
            status=503,
            content_type=MEDIA_TYPE,
        )


def unknown(request: HttpRequest) -> HttpResponse:
    return problem("not_found", 404)
