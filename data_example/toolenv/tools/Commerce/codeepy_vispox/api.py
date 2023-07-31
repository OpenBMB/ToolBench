import requests
import json
from datetime import date, datetime, timedelta
import os

from typing import Optional, Dict, Union, List


def get_company_sponsor_list(start: int, format: str, size: int, s: str=None, t: str=None, co: str=None, ci: str=None, n: str=None, st: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    ""
    start: The start index for the sponsor company in the list
        format: The returned list format. The default supported is JSON
        size: Size for the list result
        s: Generic search parameter. It searches in every field of name, city, county, tier, and subtier. If this 's' parameter is used, parameter  'n', 'ci', 'co', 't', 'st' will be ignored.
        t: Parameter for the company's visa tier (Tier 2 or Tier 5)
        co: Parameter for the company's county name
        ci: Parameter for the company's city name
        n: Parameter for the company's name
        st: Parameter for the company's visa sub-tier
        
    """
    url = f"https://vispox.p.rapidapi.com/sponsor/"
    querystring = {'start': start, 'format': format, 'size': size, }
    if s:
        querystring['s'] = s
    if t:
        querystring['t'] = t
    if co:
        querystring['co'] = co
    if ci:
        querystring['ci'] = ci
    if n:
        querystring['n'] = n
    if st:
        querystring['st'] = st
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "vispox.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

