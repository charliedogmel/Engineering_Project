import os, zipfile
from os import path
import requests
from requests.auth import HTTPBasicAuth
import subprocess
import datetime as dt
from datetime import datetime, date, timedelta
from pymongo import MongoClient
import pandas as pd
import numpy as np
from dateutil import parser
from api_functions import register, login, create_token, data, index, forecast, historical

# account details
USERNAME = 'melissa'
PASSWORD = 'WattTime4Metis'
EMAIL = 'melissa@doloresparkpiano.com'
ORG = 'StudentsInc'

# request details
BA = 'CAISO_NORTH'  # identify grid region

# starttime and endtime are optional, if ommited will return the latest value
START = '2021-09-08T19:00:00-0000'  # UTC offset of 0 (PDT is -7, PST -8)
END = '2021-09-08T19:45:00-0000'


# create a new client instance
mongo_client = MongoClient()

def check_and_populate(ba=BA):

    db = mongo_client.watt_time
    coll_names = db.list_collection_names()
    
    if ba not in coll_names:
        token = create_token(USERNAME, PASSWORD)
        file_dir, file_path = historical(token, ba)
    
        # extract csv files from historical zip file
        zip_ref = zipfile.ZipFile(file_path)
        zip_ref.extractall(file_dir)
        zip_ref.close()
        os.remove(file_path)
    
        # create a new collection and insert data
        new_coll = db[ba]
    
        # directory of files
        dir_files = file_dir
        
        # create list of all files
        _, _, file_names = next(os.walk(file_dir))
        files = [os.path.join(file_dir, fn) for fn in file_names]
        
        # mongotool address
        mongotool = r'/usr/bin/mongoimport'
        
        # import all files to mongodb
        for file in files:
            print(file)
            commands = [mongotool, '--db', 'watt_time',
                        '--collection', ba,
                        '--file', file,
                        '--type', 'csv',
                        '--headerline']
            commands = ' '.join(commands)
            subprocess.Popen(commands, shell=True)


        new_coll.update_many({},
                             {'$rename': {"timestamp": "point_time", "MOER": "value"}},
                             False,
                             array_filters=None)

    return


def check_latest_current(ba=BA):

    token = create_token(USERNAME, PASSWORD)
    
    db = mongo_client.watt_time
    new_coll = db[ba]
    
    cursor = new_coll.find().sort('point_time', -1).limit(1)
    latest_date = list(cursor)[0]['point_time']
    start_time = latest_date
    thirty_days_after = latest_date
    
    time_now = datetime.utcnow().astimezone().replace(tzinfo=dt.timezone.utc, microsecond=0).isoformat()
    print(time_now)

    if start_time != time_now:
        while thirty_days_after < time_now:
            thirty_days_after = (datetime.fromisoformat(latest_date) + timedelta(days=30)).isoformat()
            print(thirty_days_after)
            if thirty_days_after > time_now:
                end_time = time_now
            else:
                end_time = thirty_days_after
            
            print(end_time)
            # run /data with start/stop times to update db
            update_db = data(token, BA, start_time, end_time)
            print(len(update_db))
            
            # point_time timestamp is slightly different format from /historical timestamp
            temp_df = pd.DataFrame(update_db)
            temp_df['point_time'] = [parser.parse(x).replace(tzinfo=dt.timezone.utc, microsecond=0).isoformat() for x in temp_df['point_time']]
                
            # insert next 30 (or less) days of data into BA collection
            new_coll.insert_many(temp_df.to_dict('records'))
    return


# function to populate historical forecasts
# data only available from 2020
def update_forecast_data():
    
    token = create_token(USERNAME, PASSWORD)

    ba_forecast = BA + '_forecast'
    db = mongo_client.watt_time
    fore_coll = db[ba_forecast]

    if ba_forecast not in db.list_collection_names():
    
        start_time = '2020-01-01T14:55:00+00:00'
        end_time = '2020-01-01T15:00:00+00:00'
        
        current_time = datetime.utcnow().astimezone().replace(tzinfo=dt.timezone.utc, microsecond=0).isoformat()

        while end_time < current_time:
            one_day_forecast = forecast(token, BA, start_time, end_time)
            fore_coll.insert_many(one_day_forecast[0]['forecast'])
            start_time = (datetime.fromisoformat(start_time) + timedelta(days=1)).isoformat()
            end_time = (datetime.fromisoformat(end_time) + timedelta(days=1)).isoformat()

    else:
        start_time = pd.to_datetime(date.today()).replace(hour=14, minute=55, tzinfo=dt.timezone.utc).isoformat()
        end_time = pd.to_datetime(date.today()).replace(hour=15, minute=0, tzinfo=dt.timezone.utc).isoformat()
    
        one_day_forecast = forecast(token, BA, start_time, end_time)
        if one_day_forecast:
            fore_coll.insert_many(one_day_forecast[0]['forecast'])

    return


def extract_datetime(df):

    # extract year, month, weekday (1-7 = M-Su) as ints
    df['year'] = [x.year for x in df['point_time']]
    df['month'] = [x.month for x in df['point_time']]
    df['weekday'] = [x.isoweekday() for x in df['point_time']]
    df['point_date'] = [x.date().isoformat() for x in df['point_time']]
    # extract time as 'HH:MM:SS'; this can be used in comparisons: < = >
    df['time'] = [str(x).split()[1].split('+')[0] for x in df['point_time']]
    
    return df

def create_dailyline_df(moer_df, forecast_df):
    
    todays_date = date.today().isoformat()
    todays_day = date.today().isoweekday()
    one_week_ago = (date.today() - timedelta(days=7)).isoformat()
    two_weeks_ago = (date.today() - timedelta(days=14)).isoformat()
    three_weeks_ago = (date.today() - timedelta(days=21)).isoformat()

    mask = moer_df['point_date'] == todays_date
    mask_one = moer_df['point_date'] == one_week_ago
    mask_two = moer_df['point_date'] == two_weeks_ago
    mask_three = moer_df['point_date'] == three_weeks_ago
    mask_fore = forecast_df['point_date'] == todays_date

    moer_daily_df = pd.DataFrame(columns = ['time', 'forecast', 'moer_today', 'moer_1week', 'moer_2week', 'moer_3week'])
    moer_daily_df['time'] = sorted(moer_df['time'].unique())
    moer_daily_df['moer_today'] = moer_df[mask].sort_values('time', ascending=True, ignore_index=True)['value']
    moer_daily_df['moer_1week'] = moer_df[mask_one].sort_values('time', ascending=True, ignore_index=True)['value']
    moer_daily_df['moer_2week'] = moer_df[mask_two].sort_values('time', ascending=True, ignore_index=True)['value']
    moer_daily_df['moer_3week'] = moer_df[mask_three].sort_values('time', ascending=True, ignore_index=True)['value']

    moer_daily_df['forecast'] = forecast_df[mask_fore].sort_values('time', ascending=True, ignore_index=True)['value']

    return moer_daily_df

def create_weeklyline_df(moer_df, forecast_df):
    
    todays_date = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=dt.timezone.utc, microsecond=0)
    todays_dow = date.today().isoweekday()
    
    week0_start = (todays_date - timedelta(days = (todays_dow - 1))).isoformat()
    week0_end = (pd.to_datetime(week0_start) + timedelta(days=6)).replace(hour=23, minute=59).isoformat()
    week1_start = (todays_date - timedelta(days = 7 + (todays_dow - 1))).isoformat()
    week2_start = (todays_date - timedelta(days = 14 + (todays_dow - 1))).isoformat()
    week3_start = (todays_date - timedelta(days = 21 + (todays_dow - 1))).isoformat()

    mask = (moer_df['point_date'] >= week0_start) & (moer_df['point_date'] <= week0_end)
    mask_one = (moer_df['point_date'] >= week1_start) & (moer_df['point_date'] < week0_start)
    mask_two = (moer_df['point_date'] >= week2_start) & (moer_df['point_date'] < week1_start)
    mask_three = (moer_df['point_date'] >= week3_start) & (moer_df['point_date'] < week2_start)
    mask_fore = (forecast_df['point_date'] >= week0_start) & (forecast_df['point_date'] <= week0_end)

    moer_weekly_df = pd.DataFrame(columns = ['point_time', 'forecast', 'moer_today', 'moer_1week', 'moer_2week', 'moer_3week', 'point_date', 'time', 'weekday'])
    moer_weekly_df['point_time'] = moer_df[mask_one].sort_values('point_time', ascending=True, ignore_index=True)['point_time']
    moer_weekly_df['point_date'] = moer_df[mask_one].sort_values('point_time', ascending=True, ignore_index=True)['point_date']
    moer_weekly_df['moer_today'] = moer_df[mask].sort_values('point_time', ascending=True, ignore_index=True)['value']
    moer_weekly_df['moer_1week'] = moer_df[mask_one].sort_values('point_time', ascending=True, ignore_index=True)['value']
    moer_weekly_df['moer_2week'] = moer_df[mask_two].sort_values('point_time', ascending=True, ignore_index=True)['value']
    moer_weekly_df['moer_3week'] = moer_df[mask_three].sort_values('point_time', ascending=True, ignore_index=True)['value']
    moer_weekly_df['time'] = moer_df[mask_one].sort_values('point_time', ascending=True, ignore_index=True)['time']
    moer_weekly_df['weekday'] = moer_df[mask_one].sort_values('point_time', ascending=True, ignore_index=True)['weekday']

    moer_weekly_df['forecast'] = forecast_df[mask_fore].sort_values('time', ascending=True, ignore_index=True)['value']

    return moer_weekly_df


# convert actual moer data to df for visuals, drop unneeded cols, filter datetime out to specific new cols
def process_data():

    db = mongo_client.watt_time
    new_coll = db[BA]
    moer_df = pd.DataFrame(list(new_coll.find()))
    moer_df.drop(columns = ['_id', 'MOER version', 'frequency', 'market', 'ba', 'datatype', 'version'], inplace=True)
    moer_df['point_time']= pd.to_datetime(moer_df['point_time'])
    moer_df = extract_datetime(moer_df)
    
    ba_forecast = BA + '_forecast'
    fore_coll = db[ba_forecast]
    forecast_df = pd.DataFrame(list(fore_coll.find()))
    forecast_df.drop(columns = ['_id', 'ba', 'version'], inplace=True)
    forecast_df['point_time']= pd.to_datetime(forecast_df['point_time'])
    forecast_df = extract_datetime(forecast_df)
    
    # create heatmap df
    moer_heatmap_df = pd.DataFrame(moer_df.groupby(['year', 'month', 'weekday', 'time'])['value'].mean())
    
    # create daily linechart df
    moer_dailyline_df = create_dailyline_df(moer_df, forecast_df)
    
    # create weekly linechart df
    moer_weeklyline_df = create_weeklyline_df(moer_df, forecast_df)
    
    # transfer to mongodb for streamlit
    ba_heatmap = BA + '_heatmap'
    ba_dailyline = BA + '_dailyline'
    ba_weeklyline = BA + '_weeklyline'
    
    db[ba_heatmap].drop()
    db[ba_dailyline].drop()
    db[ba_weeklyline].drop()
    
    moer_heatmap_df.reset_index(inplace=True)
    heatmap_dict = moer_heatmap_df.to_dict("records")
    # Insert collection
    db[ba_heatmap].insert_many(heatmap_dict)
    
    moer_dailyline_df.reset_index(inplace=True)
    dailyline_dict = moer_dailyline_df.to_dict("records")
    # Insert collection
    db[ba_dailyline].insert_many(dailyline_dict)
    
    moer_weeklyline_df.reset_index(inplace=True)
    weeklyline_dict = moer_weeklyline_df.to_dict("records")
    # Insert collection
    db[ba_weeklyline].insert_many(weeklyline_dict)
    
    return #moer_heatmap_df, moer_dailyline_df, moer_weeklyline_df


check_and_populate(BA)
check_latest_current(BA)
update_forecast_data()
process_data()
