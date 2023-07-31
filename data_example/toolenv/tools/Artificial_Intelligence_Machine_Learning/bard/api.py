import requests
import json
from datetime import date, datetime, timedelta
import os

from typing import Optional, Dict, Union, List


def ask(question: str, bard_secure_1psid_cookie_value: str, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "https://i.ibb.co/5WHmCQ8/Screenshot-2023-05-30-231728-1.png"
    bard_secure_1psid_cookie_value: A string representing your bard __Secure-1PSID cookie (You can get your __Secure-1PSID cookie by simply accessing Developer Consolle and search for __Secure-1PSID  cookie Name https://i.ibb.co/5WHmCQ8/Screenshot-2023-05-30-231728-1.png )
        
    """
    url = f"https://bard1.p.rapidapi.com/ask"
    querystring = {'question': question, 'bard___Secure-1PSID_cookie_value': bard_secure_1psid_cookie_value, }
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "bard1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

