# Standard Python Libraries
from datetime import datetime, timedelta
from json import dumps

# Related Third-Party Python Libraries
from django.conf import settings
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db import connection, transaction
from django.db.models import Sum
from django.utils.timezone import localtime
from django.utils import formats
from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from MySQLdb import IntegrityError
from holidays import Australia as ausholidays

# Local Application Libraries
from roster import forms
from roster.models import Roster, Person, Department, ChangeLog, Toil

# Create your views here.

############################################################################
# Function: index
# Purpose:  view for index.html view the current and future on call roster.
############################################################################
def index(request):
    # get the current date
    today = datetime.now()
    # set the min_date to the last Monday
    min_date = (today - timedelta(days=today.weekday())
                + timedelta(days=0)).date()
    # query the Roster model and filter the roster_date based on whether
    # it is greater than or equal to the min_date.
    oncall_roster = Roster.objects.filter(
              roster_date__gte = min_date).prefetch_related(
              'oss_person', 'nw_person', 'es_person')
    # return the result of the roster_query to 8 entries per page
    paginator = Paginator(oncall_roster, 8)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj  = paginator.page(paginator.num_pages)
    # create a dictionary for the context
    roster = {'dates': page_obj }
    # return the rendered request to index.html
    return render(request,'roster/index.html',context=roster)

############################################################################
# Function: contact
# Purpose:  function to show the contact details of all on call roster
#           participants.
############################################################################
# @login_required(login_url='/example url you want redirect/')
@login_required()
def contact(request):
    # get a list of on call roster users sorted by department,
    # but exclude person_id 1 where the user name is blank.
    contact_list = Person.objects.order_by('person_dept', 'person_name'
                                           ).exclude(person_name__exact="")
    paginator = Paginator(contact_list, 9)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    contacts_dict = {'users': page_obj}
    return render(request, 'roster/contact_info.html',context=contacts_dict)


############################################################################
# Function: users
# Purpose:  form for adding new users to the oncall roster
############################################################################
@login_required()
def users(request):
    # instantiate the form NewUserForm (see forms.py)
    form = forms.NewUserForm()
    if (request.method == 'POST'):
        form = forms.NewUserForm(request.POST)
        if (form.is_valid()):
            form.save()
            form = forms.NewUserForm()
            messages.success(request,"New user added successfully")
        else:
            messages.warning(request,"Your request is incomplete")
    return render(request, 'roster/add_user.html', {'form': form})

############################################################################
# Function:  update_oncall_roster
# Purpose:   Mark's dirty hack - couldn't get Django ORM to update the
#            model so reverted to raw SQL.  This function is used
#            during the update page to save changes.
############################################################################
def update_oncall_roster(roster_date,oss_person,nw_person,es_person):
    # if the xx_person is empty set thge value to 1
    if (oss_person == ""):
        oss_person = 1
    if (nw_person == ""):
        nw_person = 1
    if (es_person == ""):
        es_person = 1
    try:
        # connect to the database
        with connection.cursor() as cursor:
            # add the previous roster to the change_log
            cursor.execute("INSERT INTO change_log \
                        (`roster_id`, `date`, `oss_person_id`, `nw_person_id`, `es_person_id`) \
                        SELECT id, NOW(), oss_person_id, nw_person_id, es_person_id \
                        FROM roster WHERE id = %s",
                        [roster_date])
            # then update the roster with the new person/s
            cursor.execute("UPDATE roster SET oss_person_id = %s, nw_person_id = %s, \
                            es_person_id = %s WHERE id = %s",
                            [oss_person, nw_person, es_person, roster_date])
        return True
    except IntegrityError:
        logging.warn("failed to update change_log and roster",
                      roster_date, oss_person, nw_person, es_person)
        return False
    finally:
        cursor.close()
    return True

############################################################################
# Function: update
# Purpose:  to allow users to modify the current or future oncall rosters
# Depends:  update_oncall_roster function
############################################################################
@login_required()
def update(request):
    form = forms.UpdateRosterForm()
    roster_date = (Roster.objects.order_by(
                       'roster_date').values_list(
                       'roster_date', flat=True).last() + timedelta(days=7))
    if (request.method == 'POST'):
        form = forms.UpdateRosterForm(request.POST)
        # convert the posted variabled as strings
        roster_date = str(request.POST.get('roster_date'))
        oss_person = str(request.POST.get('oss_person'))
        nw_person = str(request.POST.get('nw_person'))
        es_person = str(request.POST.get('es_person'))
        # call the update_oncall_roster function
        my_save = update_oncall_roster(roster_date, oss_person, nw_person, es_person)
        if (my_save == True):
            messages.success(request,"oncall roster updated successfully")
        else:
            messages.warning(request,"Your request is incomplete")
    mycontext =  { 'form': form }
    return render(request, 'roster/update.html', context=mycontext)

############################################################################
# Function: ajax_return_oncall
# Purpose:  return the values from the Ajax query to determine who's
#           oncall for a given week.  This function is called as part
#           of the update page.  Users should not interact with this
#           directly, however javascript does.
############################################################################
def ajax_return_oncall(request):
    if (request.method == "GET"):
        sel_date = request.GET.get('selected_date')
        qs1 = Roster.objects.filter(
                     roster_date = sel_date).values_list(
                     'oss_person_id','nw_person_id','es_person_id')
        result_json = dumps(list(qs1), cls=DjangoJSONEncoder)
        return HttpResponse(result_json)

############################################################################
# Function: ajax_return_changelog
# Purpose: return the entries in the change_log for a given date.
#          called via JavaScript.
############################################################################
def ajax_return_changelog(request):
    if (request.method == "GET"):
        sel_date_id = request.GET.get('selected_date_val')
        qs2 = ChangeLog.objects.filter(
              roster_id = sel_date_id).select_related(
              'Person__person_name').order_by('-date').values_list(
              'date', 'oss_person__person_name', 'nw_person__person_name', 'es_person__person_name')
        result_json = dumps(list(qs2), cls=DjangoJSONEncoder)
        return HttpResponse(result_json)

############################################################################
# Function:  db_add_roster_date
# Pupose:    add a new date to to the roster table.
#            called by add_roster_date.
# *** not my finest work *****
############################################################################
def db_add_roster_date(roster_date, roster_end_date, oss_person_id,nw_person_id, es_person_id):
    # convert date object to a string
    start_date = datetime.strftime(roster_date, '%Y-%m-%d')
    get_public_holiday = check_public_holidays(start_date)
    if (get_public_holiday):
        # if the number of dates returned is greater than 1
        # loop through and assign the string dates multiple
        # values.
        if (len(get_public_holiday) > 1):
            index = 0
            # use the lenth of the list to determine whether we
            # need commas or not and where to place them.
            for i in range(len(get_public_holiday)):
                if (index == 0):
                    public_holiday = get_public_holiday[index] + ", "
                    index += 1
                elif (index > 0 and (len(get_public_holiday) - 1) > index):
                    public_holiday += get_public_holiday[index] + ", "
                    index += 1
                elif (index > 0 and (len(get_public_holiday) - 1) == index):
                    public_holiday += get_public_holiday[index]
                    index += 1
        # if there's only one public holiday just get the single value
        elif (len(get_public_holiday) == 1):
            public_holiday = get_public_holiday[0]
    else:
        public_holiday = ""
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO roster \
                            (`id`,`roster_date`, `roster_end_date`, `oss_person_id`, \
                            `nw_person_id`, `es_person_id`, `changed`, `public_holiday`)\
                            VALUES (NULL, %s, %s, %s, %s, %s, 0, (%s))",
                            [roster_date, roster_end_date, oss_person_id, nw_person_id, es_person_id, public_holiday])
        return True
    except IntegrityError:
        logging.warn("failed to update change_log and roster",
                      new_roster_date, oss_person_id, nw_person_id, es_person_id)
        return False
    finally:
        cursor.close()
    return True

############################################################################
# Function:     add_roster_date
# Purpose:      add a new date to the roster.
# Requires:     db_add_roster_date
############################################################################
@login_required()
def add_roster_date(request):
    db_last_date = Roster.objects.order_by(
               'roster_date').values_list('roster_date', flat=True).last()
    roster_date = (Roster.objects.order_by(
                       'roster_date').values_list(
                       'roster_date', flat=True).last() + timedelta(days=7))
    roster_end_date = roster_date + timedelta(days=7)
    print(db_last_date, roster_date, roster_end_date)
    pgcontext = {'last_date': str(db_last_date)}
    if (request.method == 'POST'):
        oss_person_id = 1
        nw_person_id = 1
        es_person_id = 1
        my_save = db_add_roster_date(roster_date, roster_end_date, oss_person_id, nw_person_id, es_person_id)
        if (my_save == True):
            messages.success(request,"New roster date added successfully")
        else:
            messages.warning(request,"Your request is incomplete")
    return render(request, 'roster/add_roster_date.html', context=pgcontext)

############################################################################
# Function: public_holidays
# Requires: roster_date
# Purpose:  function for determining whether there's an SA public
#           holiday during the week of the roster start date.
############################################################################
def check_public_holidays(roster_date):
    # get the current year and next year
    start_date = roster_date
    current_year  = datetime.strptime(roster_date, '%Y-%m-%d').year
    next_year = current_year + 1
    # create a n empty dictionary for the public holiday dates and names
    sapubhols = {}
    # get the public holidays for SA
    for date, name in sorted(ausholidays(prov='SA',
                                         years=[current_year,next_year]
                                        ).items()):
        # check if date is a saturday or sunday
        # if so don't add it to the sapubhols dictionary
        if (date.weekday() < 5):
            sapubhols[date] = name

    # get the end date of the weekly on call roster
    end_date = str((datetime.strptime(roster_date, '%Y-%m-%d')
                    + timedelta(days=7)).date())
    # create an empty list for the public holidays
    phdays = []
    # check if the start_date and end_date encompasses the
    # public holiday date/s.
    for d,n in sapubhols.items():
        # convert the datetime object for the public holidays to a string
        d = str((datetime.strptime(str(d), '%Y-%m-%d')).date())
        # check if a public holiday occurs between the start
        # or the end of the roster period
        if (start_date <= d <= end_date):
            # if a public holiday occurs add the name of the public holiday
            phdays.append(n)
    # return the list public holidays
    return(phdays)

############################################################################
# Function:  search
# Purpose:   search for a particular roster date
############################################################################
def search(request):
    form = forms.SearchRosterForm()
    return render(request, 'roster/search.html', {'form': form})

############################################################################
# Function:  LoginView
# Purpose:    Log in page for restricted pages.
############################################################################
class LoginView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

############################################################################
# Function:   toilbalace
# Purpose:    return a logged in users toil balance and history
############################################################################
def toilbalance(request):
    # returns the username as a string, which is used in queryset1
    username = request.user.username
    # only return results for the logged in user
    queryset1 = Toil.objects.select_related(
                'person_name__person_name','person_name__person_uid').filter(
                person_name__person_uid__exact=username).values_list(
                'person_name__person_name', 'person_name__person_uid').distinct()
    # get the users toil balance by summing up the toil_total column
    queryset2 = Toil.objects.all().select_related('person_name__person_name',
                'person_name__person_uid').filter(person_name__person_uid__exact=username
                ).aggregate(balance=Sum('toil_total'))['balance']
    # get the users toil history and sort in reverse date order
    queryset3 = Toil.objects.all().filter(
                person_name__person_uid__exact=username).order_by('-toil_date')
    # create a context to render the results
    toil = {'toil': queryset1, 'balance': queryset2,
            'current_user': username, 'toil_history': queryset3}
    return render(request,'roster/toilbalance.html',context=toil)

############################################################################
# Function:   toilsummary
# Purpose:    return a summary for team leaders so they can see each team
#             members toil balance.
############################################################################
def toilsummary(request):
    username = request.user.username
    # check if the user is a team lead and if so get their team
    tl_team = Person.objects.all().select_related('person_dept').filter(
              person_uid__exact=username,
              is_team_lead__exact=1).values_list('person_dept', flat=True)[0]
    # get the team leaders staff and sum up their toil balances per team member
    tl_team_staff = Toil.objects.all().filter(
                    person_name__person_dept_id=tl_team).values(
                    'person_name__person_name').annotate(toilsummary = Sum('toil_total')).order_by('person_name')
    # create a context to render in the toilsummary page
    toilsum = {'toilsum': tl_team_staff}
    return render(request,'roster/toilsummary.html',context=toilsum)

############################################################################
# Function:   toilupdate
# Purpose:    return a form for users so they can update their own TOIL.
############################################################################
@login_required()
def toilupdate(request):
    username = request.user.username
    # instantiate the form UpdateTOILForm (see forms.py)
    form = forms.UpdateTOILForm(username=username)
    if (request.method == 'POST'):
        form = forms.UpdateTOILForm(request.POST, username=username)
        if (form.is_valid()):
            username = request.user.username
            form.save()
            messages.success(request,"TOIL updated successfully")
        else:
            messages.warning(request,"TOIL update incomplete")
    return render(request, 'roster/update_toil.html', {'form': form})
