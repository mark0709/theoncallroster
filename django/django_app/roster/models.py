from django.db import models
from django.utils import timezone

# Create your models here.
# The Person Table
# person_id 1 is special - we use this to display unassigned id's in the roster and change_log
class Person(models.Model):
    person_name = models.CharField(max_length=50, unique=True)
    person_uid = models.CharField(max_length=8, unique=True, null=False, default='')
    person_dept = models.ForeignKey('Department', default='1', on_delete=models.CASCADE)
    number = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length = 100, unique=True)
    roster_order = models.CharField(max_length = 2, default='0')
    is_team_lead = models.CharField(max_length = 1, default='0', null=False)

    # this class will overrride the table name being appname_tablename
    class Meta():
        db_table = 'person'


    # override the default model save function so that we
    # ensure that the person_name starts with a capital letter for
    # the first name and surname.
    def save(self, *args, **kwargs):
        for field_name in ['person_name']:
            val = getattr(self, field_name, False)
            if (val):
                setattr(self, field_name, val.title())
        super(Person, self).save(*args, **kwargs)

    # This will allow us to return a string rather than the memory address
    def __str__ (self):
       return self.person_name

# The Department Table
class Department(models.Model):
    dept_desc = models.CharField(max_length=50, unique=True)
    class Meta():
        db_table = 'dept'

    def __str__ (self):
        return self.dept_desc

# The Roster Table
class Roster(models.Model):
    roster_date = models.DateField()
    roster_end_date = models.DateField(default=timezone.now)
    oss_person = models.ForeignKey('Person',
                                    on_delete=models.CASCADE,
                                    related_name='+', null=False, blank=True, default='1',
                                    limit_choices_to={'person_dept': 1},)
    nw_person = models.ForeignKey('Person',
                                   on_delete=models.CASCADE,
                                   related_name='+', null=False, blank=True, default='1',
                                   limit_choices_to={'person_dept': 2},)
    es_person = models.ForeignKey('Person',
                                   on_delete=models.CASCADE,
                                   related_name='+', null=False, blank=True, default='1',
                                   limit_choices_to={'person_dept': 3},)
    public_holiday = models.CharField(max_length=50, null=False, default='')

    class Meta():
        db_table = 'roster'
        ordering = ['id']

    def __str__(self):
        return str(self.roster_date)

# The Change_log Table
class ChangeLog(models.Model):
    class Meta():
        db_table = 'change_log'

    roster_id = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    roster_date = models.ForeignKey('Roster',
                                     on_delete=models.CASCADE,
                                     related_name='+')
    oss_person = models.ForeignKey('Person',
                                    on_delete=models.CASCADE,
                                    related_name='+', null=False, blank=True, default='1',
                                    limit_choices_to={'person_dept': 1},)
    nw_person = models.ForeignKey('Person',
                                   on_delete=models.CASCADE,
                                   related_name='+', null=False, blank=True, default='1',
                                   limit_choices_to={'person_dept': 2},)
    es_person = models.ForeignKey('Person',
                                   on_delete=models.CASCADE,
                                   related_name='+', null=False, blank=True, default='1',
                                   limit_choices_to={'person_dept': 3},)
# The toil Table
class Toil(models.Model):
    class Meta():
        db_table = 'toil'

    person_name = models.ForeignKey('Person', default='1', on_delete=models.CASCADE)
    toil_date = models.DateField()
    toil_earned_1x = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    toil_earned_1_5x = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    toil_earned_2x = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    toil_earned_2_5x = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    toil_taken = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    toil_total = models.DecimalField(max_digits=6,decimal_places=2,default=0)
    toil_notes = models.CharField(max_length=100)
