from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from ecommerce import views
from rest_framework.authtoken.views import obtain_auth_token


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('orders', views.OrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token),
    path('api/', include(router.urls)),
]
