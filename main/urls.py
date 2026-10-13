from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import health, views

schema_view = get_schema_view(
    openapi.Info(
        title=f"{settings.SITE_NAME} API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('', views.index),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('user/', include('accounts.urls')),
    path('social-auth/', include('social_auth.urls')),
    path('api/', include('api.urls')),
    path('health/', health.HealthCheckView.as_view(), name='health'),
    path('ready/', health.ReadyCheckView.as_view(), name='ready'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
