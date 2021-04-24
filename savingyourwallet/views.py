from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from .form import RegisterForm, UserUpdateForm
from django.contrib import messages
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required
from django.conf import settings
from savingyourwallet.models import UserPreference, Category, Expense, UserIncome
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
import os
import json
import datetime
import csv


# Create your views here.
#Landing Page
def Land_View(request,*args, **kwargs):
    return render(request,"landingpage.html",{'title':'Landing Page'})
#Login Page
def Login_View(request,*args, **kwargs):
    return render(request,"loginpage.html",{'title':'Login Page'})
#Logout Page
def Logout_view(request,*args, **kwargs):
    logout(request)
    return redirect("LoginPage")
#Register Page
def Register_View(request,*args, **kwargs):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            form.save()
            messages.success(request,f'Account created!')
        return redirect("LoginPage")
    else:
        form = RegisterForm()
    return render(request,"register.html",{"form":form, 'title':'Register Page'})
#Expense Page
@login_required
def Home_View(request,*args, **kwargs):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    todays_date = datetime.date.today()
    Last_30days_ago = todays_date-datetime.timedelta(days=30)
    Last_30days_expenses = Expense.objects.filter(owner=request.user,date__gte=Last_30days_ago, date__lte=todays_date)
    totalexpense = Last_30days_expenses.aggregate(Sum('amount')) or 0
    income = UserIncome.objects.filter(owner=request.user)
    Last_30days_income = UserIncome.objects.filter(owner=request.user,date__gte=Last_30days_ago, date__lte=todays_date)
    totalincome = Last_30days_income.aggregate(Sum('amount')) or 0
    totalincome = income.aggregate(Sum('amount'))
    totalleft = totalincome['amount__sum'] - totalexpense['amount__sum'] or 0
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = None
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except ObjectDoesNotExist:
        currency = "USD - United States Dollar"
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
        'totalexpense':totalexpense['amount__sum'],
        'totalincome':totalincome['amount__sum'],
        'totalleft':totalleft,
        'title':'Expense Page'
    }
    return render(request,"expensepage.html",context)
#Search expense
def Search_Expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__icontains=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)
#Add expense
@login_required
def Add_Expense(request,*args, **kwargs):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST,
        'title':'Adding Expense'
    }
    if request.method == 'GET':
        return render(request,"add-expense.html",context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.warning(request, 'Amount is required')
            return render(request,"add-expense.html",context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.warning(request, 'Description is required')
            return render(request,"add-expense.html",context)
        if not date:
            messages.warning(request, 'Date is required')
            return render(request,"add-expense.html",context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('ExpensePage')
#Edit expense
@login_required
def Expense_Edit(request, id,*args, **kwargs):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,
        'title':'Editing expense'
    }
    if request.method == 'GET':
        return render(request, 'edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.warning(request, 'Amount is required')
            return render(request, 'edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.warning(request, 'Description is required')
            return render(request, 'edit-expense.html', context)
        if not date:
            messages.warning(request, 'Date is required')
            return render(request, 'edit-expense.html', context)    

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('ExpensePage')
#Delete expense
def Delete_Expense(request, id,*args, **kwargs):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('ExpensePage')
#Get expense data for chart
def Expense_Category_Summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)
#Export expense into .csv file
def Export_Expense(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
         str(datetime.date.today()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])

    expenses = Expense.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category,expense.date])
    
    return response
#Income page
@login_required
def Income_View(request,*args, **kwargs):
    expenses = Expense.objects.filter(owner=request.user)
    todays_date = datetime.date.today()
    Last_30days_ago = todays_date-datetime.timedelta(days=30)
    Last_30days_expenses = Expense.objects.filter(owner=request.user,date__gte=Last_30days_ago, date__lte=todays_date)
    totalexpense = Last_30days_expenses.aggregate(Sum('amount'))
    income = UserIncome.objects.filter(owner=request.user)
    Last_30days_income = UserIncome.objects.filter(owner=request.user,date__gte=Last_30days_ago, date__lte=todays_date)
    totalincome = Last_30days_income.aggregate(Sum('amount'))
    totalleft = totalincome['amount__sum'] - totalexpense['amount__sum']
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = None
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except ObjectDoesNotExist:
        currency = "USD - United States Dollar"
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency,
        'totalexpense':totalexpense['amount__sum'],
        'totalincome':totalincome['amount__sum'],
        'totalleft':totalleft,
        'title':'Income Page'
    }
    return render(request, 'incomepage.html', context)
#Search income
def Search_Income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)
#Add income
@login_required
def Add_Income(request,*args, **kwargs):
    context = {
        'values': request.POST,
        'title':'Adding income'
    }
    if request.method == 'GET':
        return render(request, 'add-income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.warning(request, 'Amount is required')
            return render(request, 'add-income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.warning(request, 'Description is required')
            return render(request, 'add-income.html', context)
        if not date:
            messages.warning(request, 'Date is required')
            return render(request, 'add-income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('IncomePage')

#Edit income
@login_required
def Income_Edit(request, id,*args, **kwargs):
    income = UserIncome.objects.get(pk=id)
    context = {
        'income': income,
        'values': income,
        'title':'Editing income'
    }
    if request.method == 'GET':
        return render(request, 'edit-income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.warning(request, 'Amount is required')
            return render(request, 'edit-income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.warning(request, 'Description is required')
            return render(request, 'edit-income.html', context)
        if not date:
            messages.warning(request, 'Date is required')
            return render(request, 'edit-income.html', context)
        income.amount = amount
        income. date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated  successfully')

        return redirect('IncomePage')

#Delete income
def Delete_Income(request, id,*args, **kwargs):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('IncomePage')
#Get income for chart
def Income_Summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    incomes = UserIncome.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}
    def get_source(UserIncome):
        return UserIncome.source
    source_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)

        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in incomes:
        for y in source_list:
            finalrep[y] = get_income_source_amount(y)
    return JsonResponse({'income_data': finalrep}, safe=False)
def Export_Income(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Incomes' + \
         str(datetime.date.today()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])

    incomes = UserIncome.objects.filter(owner=request.user)
    for income in incomes:
        writer.writerow([income.amount,income.description,income.source,income.date])
    
    return response
#Profile Page
@login_required
def Profile_View(request,*args, **kwargs):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('/profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        context = {
        'u_form': u_form
    }

    return render(request, 'profile.html',{'u_form': u_form,'title':'Profile Page'})
#Preference Page
@login_required
def Preference_View(request,*args, **kwargs):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path) as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})
    exists = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None
    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)
    if request.method == 'GET':

        return render(request, 'preference.html', {'currencies': currency_data,'user_preferences': user_preferences,'title':'Preference Page'})
    else:

        currency = request.POST['currency']
        if exists:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Changes saved')
        return render(request, 'preference.html', {'currencies': currency_data, 'user_preferences': user_preferences,'title':'Preference Page'})
#Summary page       
@login_required
def Stats_View(request,*args, **kwargs):
    return render(request, 'stats.html',{'title':'Summary Page'})
#Logout notification
@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    messages.add_message(request, messages.INFO, 'Successfully logged out!')
