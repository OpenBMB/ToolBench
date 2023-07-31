import requests
import json
from datetime import date, datetime, timedelta
import os

from typing import Optional, Dict, Union, List


def getproductbyslug(toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    " "
    
    """
    url = f"https://crime-rate1.p.rapidapi.com/product/getProduct/consequatur-id-quod-vel-et-accusantium-suscipit-praesentium-architecto-optio"
    querystring = {}
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "crime-rate1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def getproducts(sort_field: str, sort_direction: str, search: str='Velit', per_page: int=21, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    " "
    
    """
    url = f"https://crime-rate1.p.rapidapi.com/product"
    querystring = {'sort_field': sort_field, 'sort_direction': sort_direction, }
    if search:
        querystring['search'] = search
    if per_page:
        querystring['per_page'] = per_page
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "crime-rate1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

