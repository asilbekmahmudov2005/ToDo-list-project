from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Asosiy sahifalar
    path('', views.dashboard_view, name='dashboard'),
    path('today/', views.today_tasks_view, name='today_tasks'),
    path('all/', views.all_tasks_view, name='all_tasks'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('settings/', views.settings_view, name='settings'),

    # Task CRUD
    path('tasks/create/', views.task_create_view, name='task_create'),
    path('tasks/<int:task_id>/json/', views.task_detail_json, name='task_detail_json'),
    path('tasks/<int:task_id>/update/', views.task_update_view, name='task_update'),
    path('tasks/<int:task_id>/delete/', views.task_delete_view, name='task_delete'),
    path('tasks/<int:task_id>/toggle/', views.task_toggle_status_view, name='task_toggle_status'),
]
