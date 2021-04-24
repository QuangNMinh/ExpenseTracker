"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auths_view
from savingyourwallet import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('register/',views.Register_View,name='RegisterPage') ,
    path('homepage/',views.Home_View,name='ExpensePage') ,
    path('profile/',views.Profile_View,name='ProfilePage') ,
    path('login/',auths_view.LoginView.as_view(template_name='loginpage.html'),name='LoginPage') ,
    path('logout/',views.Logout_view,name='LogoutPage') ,
    path('add-expense',views.Add_Expense,name='Add-Expense') ,
    path('edit-expense/<int:id>',views.Expense_Edit,name='Edit-Expense') ,
    path('expense-delete/<int:id>', views.Delete_Expense, name="Expense-Delete"),
    path('search-expense',csrf_exempt(views.Search_Expenses),name='Search-Expense') ,
    path('income/', views.Income_View, name="IncomePage"),
    path('add-income/', views.Add_Income, name="Add-Income"),
    path('edit-income/<int:id>', views.Income_Edit, name="Income-Edit"),
    path('export-expense', views.Export_Expense, name="Export-Expense"),
    path('income-delete/<int:id>', views.Delete_Income, name="Income-Delete"),
    path('search-income', csrf_exempt(views.Search_Income),name="Search_Income"),
    path('expense_category_summary', views.Expense_Category_Summary,name="Expense_Category_Summary"),
    path('income_summary', views.Income_Summary,name="Income_Summary"),
    path('export-income', views.Export_Income, name="Export-Income"),
    path('stats', views.Stats_View,name="StatsPage"),
    path('',views.Land_View,name='LandingPage') ,
    path('preference/',views.Preference_View,name='PreferencePage'),
    path('admin/', admin.site.urls),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
