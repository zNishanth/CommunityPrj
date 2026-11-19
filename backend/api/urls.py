from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.SignUPView.as_view(), name="signup"),
    path("detect/", views.DetectView.as_view(), name="detect"),
    path("report/", views.ReportView.as_view(), name="report"),
    path("chain-report/", views.ChainReportView.as_view(), name="chain-report"),
    path("stats/", views.StatsUserView.as_view(), name="stats"),
]
