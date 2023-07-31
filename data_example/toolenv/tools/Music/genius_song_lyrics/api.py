import requests
import json
from datetime import date, datetime, timedelta
import os

from typing import Optional, Dict, Union, List


def song_recommendations(is_id: str, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Song Recommendations"
    id: Song ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/song/recommendations/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def song_lyrics(is_id: str, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Song Lyrics"
    id: Song ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/song/lyrics/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def videos(per_page: int=10, text_format: str=None, page: int=1, artist_id: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Videos"
    per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        page: Paginated offset, (e.g., per_page=5&page=3 returns albums 11–15)
        artist_id: Artist ID
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/videos/"
    querystring = {}
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    if page:
        querystring['page'] = page
    if artist_id:
        querystring['artist_id'] = artist_id
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_contributions_unreviewed_annotations(is_id: str, per_page: int=10, next_cursor: str=None, sort: str=None, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Contributions (unreviewed annotations)"
    id: User ID
        per_page: Number of results to return per request
        next_cursor: Next cursor
        sort: One of these:

- popularity
- chronologically
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/contributions/unreviewed_annotations/"
    querystring = {'id': is_id, }
    if per_page:
        querystring['per_page'] = per_page
    if next_cursor:
        querystring['next_cursor'] = next_cursor
    if sort:
        querystring['sort'] = sort
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def annotation_details(is_id: str, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "An annotation is a piece of content about a part of a document. The document may be a song (hosted on Genius) or a web page (hosted anywhere). The part of a document that an annotation is attached to is called a referent.
		
		Annotation data returned from the API includes both the substance of the annotation and the necessary information for displaying it in its original context."
    id: Annotation ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/annotation/details/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_contributions_transcriptions(is_id: str, next_cursor: str=None, text_format: str=None, per_page: int=10, sort: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Contributions (transcriptions)"
    id: User ID
        next_cursor: Next cursor
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        per_page: Number of results to return per request
        sort: One of these:

- popularity
- chronologically
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/contributions/transcriptions/"
    querystring = {'id': is_id, }
    if next_cursor:
        querystring['next_cursor'] = next_cursor
    if text_format:
        querystring['text_format'] = text_format
    if per_page:
        querystring['per_page'] = per_page
    if sort:
        querystring['sort'] = sort
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_contributions_suggestions(is_id: str, next_cursor: str=None, per_page: int=10, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Contributions (suggestions)"
    id: User ID
        next_cursor: Next cursor
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/contributions/suggestions/"
    querystring = {'id': is_id, }
    if next_cursor:
        querystring['next_cursor'] = next_cursor
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_contributions_q_a(is_id: str, text_format: str=None, per_page: int=10, next_cursor: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Contributions (q&a)"
    id: User ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        per_page: Number of results to return per request
        next_cursor: Next cursor
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/contributions/questions_and_answers/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    if per_page:
        querystring['per_page'] = per_page
    if next_cursor:
        querystring['next_cursor'] = next_cursor
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_contributions_pyongs(is_id: str, per_page: int=10, text_format: str=None, next_cursor: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Contributions (pyongs)"
    id: User ID
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        next_cursor: Next cursor
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/contributions/pyongs/"
    querystring = {'id': is_id, }
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    if next_cursor:
        querystring['next_cursor'] = next_cursor
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_contributions_articles(is_id: str, sort: str=None, next_cursor: str=None, per_page: int=10, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Contributions (articles)"
    id: User ID
        sort: One of these:

- popularity
- chronologically
        next_cursor: Next cursor
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/contributions/articles/"
    querystring = {'id': is_id, }
    if sort:
        querystring['sort'] = sort
    if next_cursor:
        querystring['next_cursor'] = next_cursor
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_contributions_annotations(is_id: str, text_format: str=None, per_page: int=10, next_cursor: str=None, sort: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Contributions (annotations)"
    id: User ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        per_page: Number of results to return per request
        next_cursor: Next cursor
        sort: One of these:

- popularity
- chronologically
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/contributions/annotations/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    if per_page:
        querystring['per_page'] = per_page
    if next_cursor:
        querystring['next_cursor'] = next_cursor
    if sort:
        querystring['sort'] = sort
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_contributions_all(is_id: str, per_page: int=10, text_format: str=None, next_cursor: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Contributions (all)"
    id: User ID
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        next_cursor: Next cursor
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/contributions/"
    querystring = {'id': is_id, }
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    if next_cursor:
        querystring['next_cursor'] = next_cursor
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_following(is_id: str, per_page: int=10, page: int=1, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Following"
    id: User ID
        per_page: Number of results to return per request
        page: Paginated offset, (e.g., per_page=5&page=3 returns albums 11–15)
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/following/"
    querystring = {'id': is_id, }
    if per_page:
        querystring['per_page'] = per_page
    if page:
        querystring['page'] = page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_followers(is_id: str, per_page: int=30, page: int=1, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Followers"
    id: User ID
        per_page: Number of results to return per request
        page: Paginated offset, (e.g., per_page=5&page=3 returns albums 11–15)
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/followers/"
    querystring = {'id': is_id, }
    if per_page:
        querystring['per_page'] = per_page
    if page:
        querystring['page'] = page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_accomplishments(is_id: str, per_page: int=10, next_cursor: str=None, text_format: str=None, visibility: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Accomplishments"
    id: User ID
        per_page: Number of results to return per request
        next_cursor: Next cursor
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        visibility: `visible` (default) or empty
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/accomplishments/"
    querystring = {'id': is_id, }
    if per_page:
        querystring['per_page'] = per_page
    if next_cursor:
        querystring['next_cursor'] = next_cursor
    if text_format:
        querystring['text_format'] = text_format
    if visibility:
        querystring['visibility'] = visibility
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def user_details(is_id: str, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "User Details"
    id: User ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/user/details/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def leaderboard(per_page: int=10, period: str=None, page: int=1, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Leaderboard"
    per_page: Number of results to return per request
        period: Default: `day`. One of these:

- day
- week
- month
- all_time
        page: Paginated offset, (e.g., per_page=5&page=3 returns albums 11–15)
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/leaderboard/"
    querystring = {}
    if per_page:
        querystring['per_page'] = per_page
    if period:
        querystring['period'] = period
    if page:
        querystring['page'] = page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def web_page_referents(raw_annotatable_url: str, annotation_id: str=None, og_url: str=None, text_format: str=None, canonical_url: str=None, page: int=1, filter: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Web Page Referents"
    raw_annotatable_url: Web page URL
        annotation_id: Annotation ID
        og_url: The URL as specified by an og:url tag in a page's
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        canonical_url: The URL as specified by an appropriate tag in a page's
        page: Page number
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/web-page/referents/"
    querystring = {'raw_annotatable_url': raw_annotatable_url, }
    if annotation_id:
        querystring['annotation_id'] = annotation_id
    if og_url:
        querystring['og_url'] = og_url
    if text_format:
        querystring['text_format'] = text_format
    if canonical_url:
        querystring['canonical_url'] = canonical_url
    if page:
        querystring['page'] = page
    if filter:
        querystring['filter'] = filter
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def chart_albums(page: int=1, time_period: str=None, per_page: int=10, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Chart: Albums"
    page: Paginated offset, (e.g., per_page=5&page=3 returns results 11–15)
        time_period: Default: `day`. One of these:

- day
- week
- month
- all_time
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/chart/albums/"
    querystring = {}
    if page:
        querystring['page'] = page
    if time_period:
        querystring['time_period'] = time_period
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def chart_songs(chart_genre: str=None, time_period: str=None, per_page: str='10', page: int=1, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Chart: Songs"
    chart_genre: Default: `all`. One of these:

- all
- rap
- pop
- rb
- rock
- country
        time_period: Default: `day`. One of these:

- day
- week
- month
- all_time
        per_page: Number of results to return per request
        page: Paginated offset, (e.g., per_page=5&page=3 returns results 11–15)
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/chart/songs/"
    querystring = {}
    if chart_genre:
        querystring['chart_genre'] = chart_genre
    if time_period:
        querystring['time_period'] = time_period
    if per_page:
        querystring['per_page'] = per_page
    if page:
        querystring['page'] = page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def annotation_versions(is_id: str, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Annotation Versions"
    id: Annotation ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/annotation/versions/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def album_comments(is_id: str, page: int=1, per_page: int=20, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Album Comments"
    id: Album ID
        page: Paginated offset, (e.g., per_page=5&page=3 returns albums 11–15)
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/album/comments/"
    querystring = {'id': is_id, }
    if page:
        querystring['page'] = page
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def artist_leaderboard(is_id: str, per_page: int=20, page: int=1, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Artist Leaderboard"
    id: Artist ID
        per_page: Number of results to return per request
        page: Paginated offset, (e.g., per_page=5&page=3 returns albums 11–15)
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/artist/leaderboard/"
    querystring = {'id': is_id, }
    if per_page:
        querystring['per_page'] = per_page
    if page:
        querystring['page'] = page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def artist_activity(is_id: str, per_page: int=20, page: int=1, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Artist Activity"
    id: Artist ID
        per_page: Number of results to return per request
        page: Paginated offset, (e.g., per_page=5&page=3 returns albums 11–15)
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/artist/activity/"
    querystring = {'id': is_id, }
    if per_page:
        querystring['per_page'] = per_page
    if page:
        querystring['page'] = page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def web_page_lookup(raw_annotatable_url: str, og_url: str=None, canonical_url: str=None, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "A web page is a single, publicly accessible page to which annotations may be attached. Web pages map 1-to-1 with unique, canonical URLs.
		
		Information about a web page retrieved by the page's full URL (including protocol). The returned data includes Genius's ID for the page, which may be used to look up associated referents with the /referents endpoint.
		
		Data is only available for pages that already have at least one annotation."
    raw_annotatable_url: Web page URL
        og_url: The URL as specified by an og:url <meta> tag in a page's <head>
        canonical_url: The URL as specified by an appropriate <link> tag in a page's <head>
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/web-page/lookup/"
    querystring = {'raw_annotatable_url': raw_annotatable_url, }
    if og_url:
        querystring['og_url'] = og_url
    if canonical_url:
        querystring['canonical_url'] = canonical_url
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def referents(song_id: str='2396871', page: int=None, created_by_id: str=None, text_format: str=None, per_page: int=None, web_page_id: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Referents are the sections of a piece of content to which annotations are attached. Each referent is associated with a web page or a song and may have one or more annotations. Referents can be searched by the document they are attached to or by the user that created them.
		
		Referents by content item or user responsible for an included annotation.
		
		You may pass only one of song_id and web_page_id, not both."
    song_id: ID of a song to get referents for
        page: Paginated offset, (e.g., per_page=5&page=3 returns songs 11–15)
        created_by_id: ID of a user to get referents for
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        per_page: Number of results to return per request
        web_page_id: ID of a web page to get referents for
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/referents/"
    querystring = {}
    if song_id:
        querystring['song_id'] = song_id
    if page:
        querystring['page'] = page
    if created_by_id:
        querystring['created_by_id'] = created_by_id
    if text_format:
        querystring['text_format'] = text_format
    if per_page:
        querystring['per_page'] = per_page
    if web_page_id:
        querystring['web_page_id'] = web_page_id
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def album_appearances(is_id: str, page: int=1, per_page: int=20, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Album Appearances"
    id: Album ID
        page: Paginated offset, (e.g., per_page=5&page=3 returns appearances 11–15)
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/album/appearances/"
    querystring = {'id': is_id, }
    if page:
        querystring['page'] = page
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def artist_songs(is_id: str, sort: str=None, page: int=1, per_page: int=20, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Documents (songs) for the artist specified."
    id: Artist ID
        sort: `title` (default) or `popularity`
        page: Paginated offset, (e.g., per_page=5&page=3 returns songs 11–15)
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/artist/songs/"
    querystring = {'id': is_id, }
    if sort:
        querystring['sort'] = sort
    if page:
        querystring['page'] = page
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def artist_albums(is_id: str, per_page: int=20, page: int=1, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Get artist albums"
    id: Artist ID
        per_page: Number of results to return per request
        page: Paginated offset, (e.g., per_page=5&page=3 returns albums 11–15)
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/artist/albums/"
    querystring = {'id': is_id, }
    if per_page:
        querystring['per_page'] = per_page
    if page:
        querystring['page'] = page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def artist_details(is_id: str, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "An artist is how Genius represents the creator of one or more songs (or other documents hosted on Genius). It's usually a musician or group of musicians."
    id: Artist ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/artist/details/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def search(q: str, per_page: int=10, page: int=1, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "The search capability covers all content hosted on Genius (all songs)."
    q: Search query
        per_page: Number of results to return per request
        page: Paginated offset, (e.g., per_page=5&page=3 returns results 11–15)
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/search/"
    querystring = {'q': q, }
    if per_page:
        querystring['per_page'] = per_page
    if page:
        querystring['page'] = page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def song_comments(is_id: str, text_format: str=None, per_page: int=20, page: int=1, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Song Comments"
    id: Song ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        per_page: Number of results to return per request
        page: Paginated offset, (e.g., per_page=5&page=3 returns comments 11–15)
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/song/comments/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    if per_page:
        querystring['per_page'] = per_page
    if page:
        querystring['page'] = page
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def song_details(is_id: str, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "A song is a document hosted on Genius. It's usually music lyrics.
		
		Data for a song includes details about the document itself and information about all the referents that are attached to it, including the text to which they refer."
    id: Song ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/song/details/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def album_details(is_id: str, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Album Details"
    id: Album ID
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/album/details/"
    querystring = {'id': is_id, }
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def multi_search(q: str, per_page: int=3, page: int=1, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "The multi search capability covers all content hosted on Genius (all sections)."
    q: Search query
        per_page: Number of results to return per request
        page: Paginated offset, (e.g., per_page=5&page=3 returns results 11–15)
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/search/multi/"
    querystring = {'q': q, }
    if per_page:
        querystring['per_page'] = per_page
    if page:
        querystring['page'] = page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def chart_referents(page: int=1, time_period: str='day,week,month,all_time', per_page: int=10, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Chart: Referents"
    page: Paginated offset, (e.g., per_page=5&page=3 returns results 11–15)
        time_period: Default: `day`. One of these:

- day
- week
- month
- all_time
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/chart/referents/"
    querystring = {}
    if page:
        querystring['page'] = page
    if time_period:
        querystring['time_period'] = time_period
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

def chart_artists(time_period: str=None, page: int=1, per_page: int=10, text_format: str=None, toolbench_rapidapi_key: str='088440d910mshef857391f2fc461p17ae9ejsnaebc918926ff'):
    """
    "Chart: Artists"
    time_period: Default: `day`. One of these:

- day
- week
- month
- all_time
        page: Paginated offset, (e.g., per_page=5&page=3 returns results 11–15)
        per_page: Number of results to return per request
        text_format: Format for text bodies related to the document. One or more of `dom`, `plain`, `markdown`, and `html`, separated by commas (defaults to html).
        
    """
    url = f"https://genius-song-lyrics1.p.rapidapi.com/chart/artists/"
    querystring = {}
    if time_period:
        querystring['time_period'] = time_period
    if page:
        querystring['page'] = page
    if per_page:
        querystring['per_page'] = per_page
    if text_format:
        querystring['text_format'] = text_format
    
    headers = {
            "X-RapidAPI-Key": toolbench_rapidapi_key,
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }


    response = requests.get(url, headers=headers, params=querystring)
    try:
        observation = response.json()
    except:
        observation = response.text
    return observation

