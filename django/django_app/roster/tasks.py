import os
from datetime import datetime, timedelta, date
from django.conf import settings
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from holidays import Australia as ausholidays
from MySQLdb import connect, IntegrityError


logger = get_task_logger(__name__)

#####################################################################################################################
# Function:     GetOncallPH
# Description:  Used by Celery periodic task to update oncall staff TOIL count by 7.35 hours when they're on call
#               during a Public Holiday.  Figure out who's on call when public holiday during week days except
#               Monday's.
#####################################################################################################################
def GetOncallPH(today):
    oncall_uids = []
    oncalldb = connect(host=os.environ['DB_HOSTNAME'],    # your host, usually localhost
                       user=os.environ['DB_USERNAME'],         # your username
                       passwd=os.environ['DB_PASSWORD'],  # your password
                       db=os.environ['DB_DATABASE'],)
    try:
        with oncalldb.cursor() as cursor:
            cursor.execute("SELECT oss_person_id, nw_person_id, es_person_id \
                            FROM roster WHERE roster_date=%s",[today])
            result = cursor.fetchall()
            for row in result:
                oncall_people = row[0];
                # 1 means no one has been assigned to the roster
                if (not oncall_people == 1):
                    oncall_uids.append(oncall_people)
        return oncall_uids
    finally:
        cursor.close()
    return True

#####################################################################################################################
# Function:     GetOncallMondayPH
# Description:  Used by Celery periodic task to update oncall staff TOIL count by 7.35 hours when they're on call
#               during a Public Holiday.  Figure out who's on call when public holiday occurs on a Monday.
#####################################################################################################################
def GetOncallMondayPH(today,yesterday):
    oncall_uids = []
    oncalldb = connect(host=os.environ['DB_HOSTNAME'],    # your host, usually localhost
                       user=os.environ['DB_USERNAME'],         # your username
                       passwd=os.environ['DB_PASSWORD'],  # your password
                       db=os.environ['DB_DATABASE'],)
    try:
        with oncalldb.cursor() as cursor:
            cursor.execute("SELECT person.id FROM person INNER JOIN roster \
                            ON (roster.oss_person_id=person.id \
                            or roster.nw_person_id=person.id \
                            or roster.es_person_id = person.id) \
                            WHERE roster_date=%s or roster_date=%s",
                            [today,yesterday])
            results = cursor.fetchall()
            for row in results:
                oncall_people = row[0];
                # 1 means no one has been assigned to the roster
                if (not oncall_people == 1):
                    oncall_uids.append(oncall_people)
        return oncall_uids
    finally:
        cursor.close()
    return True

#####################################################################################################################
# Function:     UpdateTOIL
# Description:  Used by Celery periodic task to update oncall staff TOIL count by 7.35 hours when they're on call
#               during a Public Holiday.  Requires today (date), Public Holiday (Name - string), On Call Person's 
#               database id.
#####################################################################################################################
def UpdateTOIL(today,public_holiday,id):
    oncalldb = connect(host=os.environ['DB_HOSTNAME'],    # your host, usually localhost
                       user=os.environ['DB_USERNAME'],         # your username
                       passwd=os.environ['DB_PASSWORD'],  # your password
                       db=os.environ['DB_DATABASE'],)
    # check if entry already exists
    comment = f"ENTRY AUTO-UPDATED - TOIL earned for being oncall during {public_holiday} Public Holiday"
    # convert datetime object "today" into a string
    todaystr = datetime.strftime(today, '%Y-%m-%d')
    # convert id to a string
    id = str(id)
    try:
        with oncalldb.cursor() as cursor:
            # insert the toil day for each user
            cursor.execute("INSERT INTO toil (`toil_date`, `toil_earned_1x`, \
                            `toil_earned_1_5x`, `toil_earned_2x`, \
                            `toil_earned_2_5x`, `toil_taken`, `toil_total`, \
                            `toil_notes`, `person_name_id`) \
                            VALUES (%s,7.35,0,0,0,0,7.35,%s,%s)",
                            [todaystr,comment,id])
            # commit the changes
            oncalldb.commit()
        return True
    finally:
        cursor.close()
    return True

# run the task daily Monday - Friday at 10am
@periodic_task(run_every=(crontab(day_of_week="1-5", hour=10, minute=0)), name="toil_auto_update", ignore_result=True)
#####################################################################################################################
# Function:     auto_update_toil
# Description:  Celery periodic tasks to update oncall staff TOIL count by 7.35 hours when they're on call
#               during public holidays. If public holiday occurs on weekend no TOIL is accrued, if it's a
#               public holiday Monday then both the current and pervious (12am-8am) oncall people accrue TOIL
#####################################################################################################################
def auto_update_toil():
    # get today's date
    today = datetime.now.date() 
    # Only execute if it's a week day
    if (today.weekday() < 5):
        # check if it's a public hoiday
        if (today in ausholidays(prov='SA')):
            # get the name of the public holiday
            public_holiday = ausholidays(prov='SA').get(today).strip()
            # we need to get whomever was oncall on Sunday as well
            # if it's a Monday
            if (today.weekday() == 0):
                # we need to get whomever was on call from midnight to 8am
                # so we'll need last weeks roster date (which starts on a Monday)
                yesterday = datetime.strftime(today - timedelta(7), '%Y-%m-%d')
                # pass todays date and the start of last weeks roster
                result = GetOncallMondayPH(today,yesterday)
                # interate over the results
                for id in result:
                    # foreach id update the toil table
                    updatedb = UpdateTOIL(today,public_holiday,id)
                    if (updatedb == True):
                        logger.info(f"added TOIL for {public_holiday} for {id}")
                    else:
                        logger.info(f"the update failed")
            else:
                # if the public holiday doesnt occur on a Monday
                # get the last Mondays date and override today variable.
                today = (today - timedelta(days=today.weekday())
                            + timedelta(days=0))
                result = GetOncallPH(today)
                for id in result:
                    # foreach id update the toil table
                    updatedb = UpdateTOIL(today,public_holiday,id)
                    if (updatedb == True):
                        logger.info(f"added TOIL for {public_holiday} for {id}")
                    else:
                        logger.info(f"the update failed")
