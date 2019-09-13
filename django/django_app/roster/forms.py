from datetime import datetime, timedelta

from django import forms
from django.core import validators
from django.db.models import Q

from roster.models import Roster, Person, Department, Toil

############################################################################
# Class:      NewUserForm
# Purpose:    Add Users to the On Call Roster
############################################################################
class NewUserForm(forms.ModelForm):
    class Meta():
        model = Person
        fields = '__all__'
        labels = {
                   "person_name":"Name",
                   "person_uid":"Uni ID",
                   "person_dept":"Department",
                   "number":"Mobile Number",
                   "email":"Email",
                  }
    # make sure a mobile number only consists of numbers
    mobile_regex = validators.RegexValidator(regex=r'^\d{9,11}$',
                   message="Phone number must be entered in the format: '999999999'. Up to 11 digits allowed.")
    # make sure the users uid is in the format a1 followed by 6 digits
    uid_regex = validators.RegexValidator(regex=r'^a1\d{6}$',
                   message="Must contain a valid University of Adelaide uid in the format : 'a1xxxxxx'.")
    person_uid = forms.CharField(validators=[uid_regex], max_length=8, label='Uni ID')
    number = forms.CharField(validators=[mobile_regex], max_length=11, label='Mobile Number')
    # don't let bots see hiddeninput fields
    botcatcher = forms.CharField(required=False,
                                widget=forms.HiddenInput(),
                                validators = [validators.MaxLengthValidator(0)]
                                )
    # This function checks that the data being submitted is valid
    def clean(self):
        uofa = ['adelaide.edu.au']
        all_clean_data = super().clean()
        email = all_clean_data['email']
        mobile_number = all_clean_data['number']
        name = all_clean_data['person_name']
        email_domain = all_clean_data['email'].split('@')[1]
        if (email_domain not in uofa):
            raise forms.ValidationError("Adding new users using non University of Adelaide email addresses is prohibited.")

############################################################################
# Class:      UpdateRosterForm
# Purpose:    Form to allow users to change who's on call
############################################################################
class UpdateRosterForm(forms.ModelForm):
    class Meta():
        model = Roster
        fields = ('roster_date', 'oss_person', 'nw_person', 'es_person')
        labels = {
                   "roster_date":"Start On Call Date",
                   "oss_person":"Server & Storage Services",
                   "nw_person":"Network Services",
                   "es_person":"Enterprise Systems"
                  }

    def __init__(self, *args, **kwargs):
        super(UpdateRosterForm, self).__init__(*args, **kwargs)
        # get todays date
        self.now = datetime.now()
        self.today = self.now.date()
        # determine the last Monday based on todays date
        self.min_date = (self.today - timedelta(days=self.today.weekday()) + timedelta(days=0))
        # select the date based on todays date last Monday
        self.fields['roster_date'] = forms.ModelChoiceField(
            queryset=Roster.objects.filter(
            roster_date__gte=self.min_date),
            initial = self.min_date,
            label='Start On Call Date'
            )
        # Override to ignore the team on call number
        self.fields['oss_person'].queryset = Person.objects.filter(
                                  person_dept_id__exact=1).exclude(person_name__icontains="On Call")
        # Also exclude Peter Hughes from the Networks On Call Roster
        self.fields['nw_person'].queryset = Person.objects.filter(person_dept_id__exact=2).exclude(Q(
                                            person_name__icontains="On Call") | Q(person_name__exact="Peter Hughes"))
        self.fields['es_person'].queryset = Person.objects.filter(
                                  person_dept_id__exact=3).exclude(person_name__icontains="On Call")

############################################################################
# Class:      SearchRosterForm
# Purpose:    Form to allow users to query who was oncall for a given week.
############################################################################
class SearchRosterForm(forms.ModelForm):
    class Meta():
        model = Roster
        fields = '__all__'
        labels = {
                    "roster_date":"On Call Week Starting",
        }

    def __init__(self, *args, **kwargs):
       # make the roster_date a dropdown based on a query of the Roster model
       super(SearchRosterForm, self).__init__(*args, **kwargs)
       self.fields['roster_date'] = forms.ModelChoiceField(
           queryset=Roster.objects.all(),
           empty_label=None,
           label='On Call Week Starting'
           )

############################################################################
# Class:      UpdateTOILForm
# Purpose:    This locks down the user to their own toil updates based on
#             their login details.
#             update_toil.js determines the loadings for each of the values
#             input into the form.
############################################################################
# This class provides a calendar like interface for selecting the date of
# the toil.  This is called as a widget for toil_date in the UpdateTOILForm.
class DateInput(forms.DateInput):
    input_type = 'date'

# This is the actual UpdateTOILForm
class UpdateTOILForm(forms.ModelForm):
    class Meta():
        model = Toil
        fields = ('person_name', 'toil_date','toil_earned_1x', 'toil_earned_1_5x',
                  'toil_earned_2x', 'toil_earned_2_5x', 'toil_taken',
                  'toil_notes', 'toil_total')
        labels = {
                    "person_name":"Name",
                    "toil_date":"Date",
                    "toil_earned_1x":"Toil Earned (standard time)",
                    "toil_earned_1_5x":"Toil Earned (1.5 times)",
                    "toil_earned_2x":"Toil Earned (double time)",
                    "toil_earned_2_5x":"Toil Earned (2.5 times)",
                    "toil_taken":"Hours Taken",
                    "totil_total":"Total",
                    "toil_notes":"Comments",
        }
        # make the comments section text box larger and add the calendar
        # widget when selecting the TOIL date.
        widgets = {
          'toil_notes': forms.Textarea(attrs={'rows':2, 'cols':50}),
          'toil_date': DateInput(),
        }

    # override the default init function so that we pass the
    # logged in ussrname to the query for the TOIL update form.
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username',None)
        super(UpdateTOILForm, self).__init__(*args, **kwargs)
        self.fields['person_name'] = forms.ModelChoiceField(
            queryset=Person.objects.filter(
            person_uid__exact=self.username), initial = self.username)
