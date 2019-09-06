#!/usr/bin/env python3 -tt
# -*- coding: utf8 -*-

import requests
import re
import sys

class RedmineException(Exception):
    """Exception raised for bad thing happens with Redmine.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

def extract_authenticity_token(response):
    """Extract authenticity token from response body using a regular expression

    Parameters:
        response (Response): response from a request.

    Returns:
        string: The authenticity token
    """
    #<input type="hidden" name="authenticity_token" value="Ja5+Rl6fqKP/Y01b/GHA6Ek5lLVnNmNQbkbxvu4Pycr3hqoiL1NlWRmoGDhycp3h4MbfS2ix213YG5s9tk5PEw==" />
    #token = re.search('<input type="hidden" name="authenticity_token" value="(.*?)"[^>]*?>',response.text,re.S|re.I)

    #<meta name="csrf-token" content="Ja5+Rl6fqKP/Y01b/GHA6Ek5lLVnNmNQbkbxvu4Pycr3hqoiL1NlWRmoGDhycp3h4MbfS2ix213YG5s9tk5PEw==" />
    token = re.search('<meta name="csrf-token" content="(.*?)"[^>]*?>',response.text,re.S|re.I)
    return token.group(1)

def redmine_login(session, username, password):
    """Login procedure on Redmine server instance.

    Parameters:
        session (Session): session object to be used by the following requests.
        username (string): username of the user to be logged in.
        password (string): password of the user.

    Returns:
        Response: Response object.
    """
    r = session.get(f"{REDMINE_SERVER_URL}/login", headers={})
    if r.status_code != 200:
        raise RedmineException(f"failed to connect to the server (status={r.status_code}).")

    token = extract_authenticity_token(r)
    payload = {
        'utf8':'✓',  # %E2%9C%93
        'authenticity_token':token,
        'back_url':REDMINE_SERVER_URL,
        'username':username,
        'password':password,
        'login':'Connexion »'
    }

    r = session.post(f'{REDMINE_SERVER_URL}/login', headers={}, data=payload) #, cookies=r.cookies)    

    if r.status_code == 200 and '<div class="flash error" id="flash_error">Identifiant ou mot de passe invalide.</div>' in r.text:
        # we override the status code when username/password were invalid
        r.status_code = 401
        raise RedmineException(f"failed to authenticate on the server.")
    return r


def redmine_logout(session, authenticity_token):
    """Logout procedure on Redmine server instance.

    Parameters:
        session (Session): session object to be used by the following requests.

    Returns:
        Response: Response object.
    """
    r = session.post(f"{REDMINE_SERVER_URL}/logout", data={'authenticity_token':authenticity_token}, headers = {})
    return r

def redmine_create_git_repository(session, authenticity_token, project_name, repository_name, cookies={}):
    """Repository creation procedure on Redmine server instance.

    Parameters:
        session (Session): session object to be used by the following requests.
        authenticity_token (string): authenticity token extracted from the previous request.
        project_name (string): name of the project to which the repository will be bound.
        repository_name (string): unique name of the repository to be created.
        cookies (dict): cookies to be passed to the request.

    Returns:
        Response: Response object.
    """
    payload = {
        'utf8':'✓',
        'authenticity_token':authenticity_token,
        'repository_scm':'Xitolite',
        'repository[is_default]':'1',
        'repository[identifier]':repository_name,
        'repository[path_encording]':'UTF-8',
        'repository[create_readme]':'false',
        'repository[create_git_annex]':'false',
        'commit':'Créer' # Cr%C3%A9er
    }

    r = session.post(f'{REDMINE_SERVER_URL}/projects/{project_name}/repositories', headers={}, data=payload) #, cookies=cookies)
    return r



REDMINE_SERVER_URL = 'http://demo.redmine.org'

with requests.session() as s:
    try: 
        r = redmine_login(s, 'mylogin', 'mypassword')
        print('login successful.')
        #print(r.text)

        token = extract_authenticity_token(r)
        r = redmine_create_git_repository(s, token, 'montest', 'montest_repo_4') #, cookies=r.cookies)
        #if r.status_code != 302: # 302 redirect to /projects/montest/settings/repositories
        #    raise RedmineException(f"failed to create repository (status={r.status_code})")
        #else:
        print(f'repository successfully created (status={r.status_code}).')
        r = redmine_logout(s, token)
    except RedmineException as e:
        print(f"⛔ {e}")



