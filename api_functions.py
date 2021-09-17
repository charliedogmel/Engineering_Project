import requests
from requests.auth import HTTPBasicAuth
from os import path

def register(username, password, email, org):
    url = 'https://api2.watttime.org/register'
    params = {'username': username,
              'password': password,
              'email': email,
              'org': org}
    rsp = requests.post(url, json=params)
    print(rsp.text)


def login(username, password):
    url = 'https://api2.watttime.org/login'
    try:
        rsp = requests.get(url, auth=HTTPBasicAuth(username, password))
    except BaseException as e:
        print('There was an error making your login request: {}'.format(e))
        return None

    try:
        token = rsp.json()['token']
    except BaseException:
        print('There was an error logging in. The message returned from the '
              'api is {}'.format(rsp.text))
        return None

    return token


def create_token(username, password):
    token = login(username, password)
    if not token:
        print('You will need to fix your login credentials (username and password '
              'at the start of this file) before you can query other endpoints. '
              'Make sure that you have registered at least once by uncommenting '
              'the register(username, password, email, org) line near the bottom '
              'of this file.')
        exit()
    return token


def data(token, ba, starttime, endtime):
    url = 'https://api2.watttime.org/data'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba, 'starttime': starttime, 'endtime': endtime}

    rsp = requests.get(url, headers=headers, params=params)
    # print(rsp.text)  # uncomment to see raw response
    return rsp.json()


def index(token, ba):
    url = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}

    rsp = requests.get(url, headers=headers, params=params)
    # print(rsp.text)  # uncomment to see raw response
    return rsp.json()


def forecast(token, ba, starttime=None, endtime=None):
    url = 'https://api2.watttime.org/forecast'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    if starttime:
        params.update({'starttime': starttime, 'endtime': endtime})

    rsp = requests.get(url, headers=headers, params=params)
    # print(rsp.text)  # uncomment to see raw response
    return rsp.json()


def historical(token, ba):
    url = 'https://api2.watttime.org/historical'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    rsp = requests.get(url, headers=headers, params=params)
    cur_dir = path.dirname(path.realpath('my_project'))
    file_dir = path.join(cur_dir, '{}_historical'.format(ba))
    file_name = '{}_historical.zip'.format(ba)
    file_path = path.join(file_dir, file_name)
    with open(file_path, 'wb') as fp:
        fp.write(rsp.content)

    print('Wrote historical data for {} to {}'.format(ba, file_path))
    return file_dir, file_path


if __name__ == '__main__':
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
    
    # Only register once!!
    # register(USERNAME, PASSWORD, EMAIL, ORG)

    token = create_token(USERNAME, PASSWORD)

    realtime_index = index(token, BA)
    print(realtime_index)

    print('Please note: the following endpoints require a WattTime subscription')
    historical_moer = data(token, BA, START, END)
    print(historical_moer)

    forecast_moer = forecast(token, BA)
    print(forecast_moer)



    
