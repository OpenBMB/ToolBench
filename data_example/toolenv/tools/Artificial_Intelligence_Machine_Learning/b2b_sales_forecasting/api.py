import requests
import json
from datetime import date, datetime, timedelta
import os

from typing import Optional, Dict, Union, List


def description_of_machine_learning_model_parameters(model_id: str, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "API returns a general description of ML model, like Classification Accuracy, list of allowed qualitative sales attributes and their values. Only those values are allowed when describing opportunity."
    
    """
    url = f"https://b2b-sales-forecasting.p.rapidapi.com/model/{model_id}"
    querystring = {}
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "b2b-sales-forecasting.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

