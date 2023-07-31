import requests
import json
from datetime import date, datetime, timedelta
import os

from typing import Optional, Dict, Union, List


def bty690_warped(bty690warped: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "https://www.warped-mirror.com/  bty690 warped là trang web được nhà cái Bty690 Bsports ủy quyền phát triển khai thác thị trường cá cược trực tuyến tại Việt Nam. Truy cập warped-mirror.com để lấy link đăng ký bty690.com - bsport thể thao miễn phí và nhận khuyến mãi chơi cá độ online ngay."
    
    """
    url = f"https://bty690warped.p.rapidapi.com/bty690warped"
    querystring = {}
    if bty690warped:
        querystring['bty690warped'] = bty690warped
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "bty690warped.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

