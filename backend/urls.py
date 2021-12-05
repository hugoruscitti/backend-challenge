from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from ecommerce import views


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
]
