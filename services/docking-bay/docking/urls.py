"""URL routing for docking bay operations."""
from django.urls import path
from docking.views import bay_views
from docking.views import cross_repo_views

urlpatterns = [
    path("ships", bay_views.ship_list, name="ship-list"),
    path("ships/<int:pk>", bay_views.ship_detail, name="ship-detail"),
    path("register-ship", bay_views.register_ship, name="register-ship"),
    path("permit", bay_views.issue_permit, name="issue-permit"),
    path("cargo-scan", bay_views.cargo_scan, name="cargo-scan"),
    path("cargo-upload", bay_views.cargo_upload, name="cargo-upload"),
    path("bay-status", bay_views.bay_status, name="bay-status"),
    path("import-registry", bay_views.import_registry, name="import-registry"),
    path("export", bay_views.export_permit, name="export-permit"),
    path("clearance-check", bay_views.clearance_check, name="clearance-check"),
    path("proxy", bay_views.proxy_request, name="proxy-request"),

    # Imperial shared library integration
    path("imperial/reports", cross_repo_views.imperial_docking_report, name="imperial-reports"),
    path("imperial/registry", cross_repo_views.imperial_ship_registry, name="imperial-registry"),
    path("imperial/config", cross_repo_views.imperial_bay_config, name="imperial-config"),
    path("imperial/config-xml", cross_repo_views.imperial_bay_xml_config, name="imperial-config-xml"),
    path("imperial/audit", cross_repo_views.imperial_docking_audit, name="imperial-audit"),
    path("imperial/search", cross_repo_views.imperial_docking_search, name="imperial-search"),
    path("imperial/query", cross_repo_views.imperial_docking_query, name="imperial-query"),
    path("imperial/encrypt", cross_repo_views.imperial_encrypt_credentials, name="imperial-encrypt"),
    path("imperial/sync-fees", cross_repo_views.imperial_sync_fees, name="imperial-sync-fees"),
    path("imperial/webhooks/receive", cross_repo_views.imperial_receive_webhook, name="imperial-receive-webhook"),
    path("imperial/webhooks/process", cross_repo_views.imperial_process_webhook, name="imperial-process-webhook"),
]
