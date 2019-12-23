from django.urls import path

from . import views

app_name = 'constructor'


urlpatterns = [
    path('<int:pk>', views.ChecklistConstructorView.as_view(), name='constructor'),
    path('create-section', views.create_section, name='create-section'),
    path('delete-section', views.delete_section, name='delete_section'),
    path('create-general-question', views.create_general_question, name='create_general_question'),
    path('create-open-question', views.create_open_question, name='create_open_question'),
    path('create-int-choices-question',
         views.create_int_choices_question,
         name='create_int_choices_question'),
    path('constructor/create-text-choices-question',
         views.create_text_choices_question,
         name='create_text_choices_question'),
    path('delete-question', views.delete_question, name='delete-question'),
    path('create-int-option', views.create_int_option, name='create_int_option'),
    path('create-text-option', views.create_text_option, name='create_text_option'),
    path('delete-option', views.delete_option, name='delete_option'),
]
