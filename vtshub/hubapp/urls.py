from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('explore/', views.explore, name='explore'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('upload/', views.upload, name='upload'),

    # Problem details
    path('problem/<int:pk>/', views.problem_detail, name='problem_detail'),

    # Designer profile
    path('designer/<int:designer_id>/', views.designer_profile, name='designer_profile'),

    # Marketplace case details
    path('marketplace/<int:pk>/', views.case_detail, name='case_detail'),

    # Solution submission
    path('submit-solution/<int:pk>/', views.submit_solution, name='submit_solution'),

    # AI feedback & refinement
    path('submission/<int:pk>/feedback/', views.ai_design_feedback, name='ai_design_feedback'),
    path('submission/<int:pk>/refine/', views.refine_solution, name='refine_solution'),
    path('submission/<int:pk>/update/', views.update_submission, name='update_submission'),
    path('submission/<int:pk>/updated/', views.submission_updated_success, name='submission_updated_success'),

    # Gemini API
    path('api/gemini/', views.proxy_gemini, name='proxy_gemini'),

    # Password reset
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='hubapp/passwordreset.html',
            email_template_name='hubapp/password_reset_email.html',
            subject_template_name='hubapp/password_reset_subject.txt',
            success_url='/password-reset/done/'
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='hubapp/passwordresetdone.html'
        ),
        name='password_reset_done'
    ),

    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='hubapp/passwordconfirm.html',
            success_url='/password-reset/complete/'
        ),
        name='password_reset_confirm'
    ),

    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='hubapp/passwordresetcomplete.html'
        ),
        name='password_reset_complete'
    ),
]