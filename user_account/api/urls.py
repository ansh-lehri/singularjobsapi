from django.urls import path
from user_account.api.views import (
    registration_view,
    login_view,
    create,
    update,
    get_jobs,
    check_user_profile_exist,
    change_password,
    logout,
    create_new_jobs,
    VerifyEmail,
    update_neo4j_job_node_session,
    urgent_mails,
)

app_name = 'user_account'

urlpatterns = [
	path('register/', registration_view, name="register"),
    path('login/',login_view,name="login"),
    path('create/',create,name="create_profile"),
    path('update/',update,name="update_profile"),
    path('myjobs/',get_jobs,name="jobs"),
    path('check/',check_user_profile_exist,name="check_user"),
    path('change_password/',change_password,name="change_password"),
    path('logout/',logout,name="logout"),
    path('new_jobs/',create_new_jobs,name="new_jobs"),
    path('email-verify/',VerifyEmail,name="email-verify"),
    path('update_neo4j_session/',update_neo4j_job_node_session,name="neo4j-session-update"),
    path('urgent_mail/',urgent_mails,name="urgent-mail"),
]