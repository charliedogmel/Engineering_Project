import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
import datetime as dt
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter, MinuteLocator
import plotly.express as px
import altair as alt


def main():
    st.set_page_config(layout='wide')

    st.markdown("""
    <style>
    .standard-text { font-size:24px; }
    .title { font-size:36px; }
    .sidebar-text{ font-size:26px; }
    .subheader{ font-size:20px }
    </style>
    """, unsafe_allow_html=True)
    
    mongo_client = MongoClient(**st.secrets["mongo"])
    db = mongo_client.watt_time

    st.write('''
    # The Cleanest Time to Clean!
    Or play video games, make a smoothie, use power tools, plug in your electric [bike, moped, motorcycle, car], etc.  
    Basically anything that involves using electricity!
    ''')
    st.text("")
    st.write('''
    - Simply select your electricity grid region
    - Observe the forecasted Marginal Operating Emissions Rate (MOER) value
    - If it's low, you're good to go!
    ''')
    st.text("")
    st.text("")
    

    col3, col4, col5 = st.columns([20,5,1])
    with col3:
        #st.markdown('<p class="subheader">Created with MOER </p>', unsafe_allow_html=True)
        st.write('Created with real-time and historical MOER values from')
    with col4:
        st.image('./watttime_logo.png')
    with col5:
        st.write('API')
    

    st.markdown('<p class="standard-text">Select your Grid Region</p>', unsafe_allow_html=True)
    BA = st.selectbox('', ['CAISO_NORTH'])
    ba_heatmap = BA + '_heatmap'
    ba_dailyline = BA + '_dailyline'
    ba_weeklyline = BA + '_weeklyline'

    heatmap_df = pd.DataFrame(list(db[ba_heatmap].find({}, {'_id': 0, 'year': 1, 'month': 1, 'weekday': 1, 'time': 1, 'value': 1})))
    dailyline_df = pd.DataFrame(list(db[ba_dailyline].find({}, {'_id': 0, 'time': 1, 'forecast': 1, 'moer_today': 1,
                                                                'moer_1week': 1, 'moer_2week': 1, 'moer_3week': 1})))
    weeklyline_df = pd.DataFrame(list(db[ba_weeklyline].find({}, {'_id': 0, 'point_time': 1, 'forecast': 1, 'moer_today': 1,
                                                                  'moer_1week': 1, 'moer_2week': 1, 'moer_3week': 1})))

    st.text("")

            
    # display daily line chart

    st.write(
        ''' 
    ## **Daily Forecast**
    ''')
    
    st.write('''
    #### Choose previous week(s) by number to compare and contrast:
    '''
    )

    fig2, ax2 = plt.subplots()#figsize = (24, 18))

    weeks = st.multiselect("", [1, 2, 3])

    plt.plot(dailyline_df['time'], dailyline_df['forecast'], label = "Today's Forecast", linestyle="-")
    plt.plot(dailyline_df['time'], dailyline_df['moer_today'], label = "Today's Actual", linestyle="--")

    if (1 in weeks):
        plt.plot(dailyline_df['time'], dailyline_df['moer_1week'], label = "1 Week Ago Today", linestyle="-.")
    if (2 in weeks):
        plt.plot(dailyline_df['time'], dailyline_df['moer_2week'], label = "2 Weeks Ago Today", linestyle="--")
    if (3 in weeks):
        plt.plot(dailyline_df['time'], dailyline_df['moer_3week'], label = "3 Weeks Ago Today", linestyle="--")
    plt.xlabel('Time of Day')
    plt.ylabel('MOER Value')
    
    x_ticks = np.arange(0, 288, 12)
    plt.xticks(x_ticks, rotation = 45)
    plt.legend()
    st.pyplot(fig2)

    # display historical moer as an interactive heatmap
    st.write('''
    ## **Actual MOER Values** #### 
    ### **By Weekday and Time of Day**''')
    
    col1, col2 = st.columns([1, 5])
    col1.markdown('<p class="subheader">Select Year</p>', unsafe_allow_html=True)
    select_year = col1.radio('', heatmap_df['year'].unique())
    st.markdown('<p class="standard-text">Select Time of Day of MOER Value</p>', unsafe_allow_html=True)
    st.text("(Time in UTC - Add 7 hours for PST)")
    slider_time = st.slider('',
                              datetime.strptime(heatmap_df['time'].unique().min(), '%H:%M:%S').time(),
                              datetime.strptime(heatmap_df['time'].unique().max(), '%H:%M:%S').time())
    slider_time = slider_time.strftime('%H:%M:%S')


    fig, ax = plt.subplots()#figsize = (24, 18))
    # ax.set_title('Monthly MOER values by Day of the Week')

    # prepare data for heatmap: filter, then transform into matrix
    df = heatmap_df[(heatmap_df['year'] == select_year) &
                    (heatmap_df['time'] == slider_time)].reset_index().copy()

    day_month = {1: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0},
                 2: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0},
                 3: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0},
                 4: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0},
                 5: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0},
                 6: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0},
                 7: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}}
    
    for i in range(len(df)):
        day_month[df.loc[i]['weekday']][df.loc[i]['month']] = df.loc[i]['value']
        
    data_rows = list(day_month.values())
    heatmap_data = []

    for i in range(0, len(data_rows)):
        heatmap_data.append(list(data_rows[i].values()))
            
    sns.heatmap(data = heatmap_data, square=True, cbar_kws={"shrink": .6},
                     xticklabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                     yticklabels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    col2.pyplot(fig)

    # display weekly line chart

    st.write(
        ''' 
    ## **Weekly Forecast**
    ''')
    
    st.write('''
    #### Choose previous weeks to compare and contrast:
    '''
    )

    fig3, ax3 = plt.subplots()

    weekly_weeks = st.multiselect("", ["One Week", "Two Weeks", "Three Weeks"])

    plt.plot(weeklyline_df['point_time'], weeklyline_df['forecast'], label = "This Week's Forecast", linestyle="-")
    plt.plot(weeklyline_df['point_time'], weeklyline_df['moer_today'], label = "This Week's Actual", linestyle="--")

    if ("One Week" in weekly_weeks):
        plt.plot(weeklyline_df['point_time'], weeklyline_df['moer_1week'], label = "1 Week Ago", linestyle="-.")
    if ("Two Weeks" in weekly_weeks):
        plt.plot(weeklyline_df['point_time'], weeklyline_df['moer_2week'], label = "2 Weeks Ago", linestyle="--")
    if ("Three Weeks" in weekly_weeks):
        plt.plot(weeklyline_df['point_time'], weeklyline_df['moer_3week'], label = "3 Weeks Ago", linestyle="--")
    plt.xlabel('Day and Time')
    plt.ylabel('MOER Value')
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()
    
    plt.legend()
    st.pyplot(fig3)

if __name__ == '__main__':
    main()
