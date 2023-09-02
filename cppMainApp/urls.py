from django.contrib import admin
from django.urls import path
from .views import GetAllDataSpecificTable, GetAllTablesNames, UpdateDataSpecificTableViaUniqueIdentification,delete_table,delete_entry,update_entry

urlpatterns = [
    path('', GetAllTablesNames.as_view()),
    path('table/<str:table_name>/', GetAllDataSpecificTable.as_view()),
    path('update_data_unique_condition/', UpdateDataSpecificTableViaUniqueIdentification.as_view()),
    path('delete_table/',delete_table.as_view(),name="Delete_table"),
    path('delete_entry/',delete_entry.as_view(),name="Delete_entry"),
    path('update_entry/',update_entry.as_view(),name="Update_entry")

]
