Little python script that automate the creation of git repository in a Redmine project as this feature is not available in the REST API.

## Requirements

- Python
- Requests (https://requests-fr.readthedocs.io/en/latest/)

    ```bash
    pip install requests
    ```

## Configuration

You will need to edit the python script in order to provide:
- the URL of the redmine server (`REDMINE_SERVER_URL`)
- your login and password as parameters of the `login` function
- the project name and the repository name in the `redmine_create_git_repository` function


