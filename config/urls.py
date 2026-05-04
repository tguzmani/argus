from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/repositories/", include("apps.repositories.urls")),
    path("api/pulls/", include("apps.pulls.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
]
