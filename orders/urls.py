from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderCreateView

router = DefaultRouter()
router.register(r'', OrderViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('', include(router.urls)),
]
