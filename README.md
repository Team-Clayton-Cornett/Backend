# Team Clayton Cornett Backend
## Overview
The backend is an Ubuntu 18.04 instance hosted on AWS EC2 running Django v2.2.9 with MongoDB v4.2.2 and Djongo v1.3.0 as the SQL connector.

The project is located in /opt/capstone.  
IP: 34.234.47.39  
URL: claytoncornett.tk  

Access Logs: `/var/log/apache2/access.log`  
Error Logs: `/var/log/apache2/error.log`  

Viewing the error logs: `sudo less /var/log/apache2/error.log`  

### File Hierarchy

/opt/capstone/  
    manage.py  
    capstone/  
        __init__.py  
        asgi.py  
        settings.py  
        urls.py  
        wsgi.py  
    api/  
        migrations/  
        __init__.py  
        admin.py  
        apps.py  
        models.py  
        tests.py  
        views.py  

### Views
Views are how the server deals with requests that were routed by URLs. This is where the logic is defined when a request is made via a URL.  
Views for the api app (the main app for the backend) are located at `/opt/capstone/api/views.py`  
More documentation on Django views: [https://docs.djangoproject.com/en/2.2/topics/http/views/](https://docs.djangoproject.com/en/2.2/topics/http/views/)  
*Note:* All of the API views will be returning [JSON responses](https://docs.djangoproject.com/en/2.2/ref/request-response/#jsonresponse-objects) rather than normal [HTTP responses](https://docs.djangoproject.com/en/2.2/ref/request-response/#django.http.HttpResponse).

### Models
Models are how the objects stored in the database are defined.  
Models for the api app (the main app for the backend) are located at `/opt/capstone/api/models.py`  
More documentation on Django models: [https://docs.djangoproject.com/en/2.2/topics/db/models/](https://docs.djangoproject.com/en/2.2/topics/db/models/)

### URLs
URLs are how requests to the server are routed to their respective views.  
Views for the project are located at /opt/capstone/capstone/urls.py  
The project URLs will simply have the Django admin URLs (login, logout, management, etc) and will append the app URLs (custom api URLs)  
Views for the api app (the main app for the backend) are located at `/opt/capstone/api/urls.py`  

### Templates
Templates are how the server generates the HTML that will be served to the client.  
The api app will not use templates since it will be mostly JSON responses to the app.  
Templates may be used if we integrate password reset emails, an administration web interface, etc.  
If they are utilized, they would be located in `/opt/capstone/api/templates/<template_name>.html`

## Getting Started
You must activate the virtual environment prior to running any Django management commands.  
    *&ast;from the* `/opt/capstone` *directory:&ast;* `source venv/bin/activate`  
To deactivate the virtual environment, simply run: `deactivate`  

All Django management commands are run via the manage.py script in the `/opt/capstone` directory.  
Each command is prefixed by: `python manage.py <command>`  
More documentation on Django manage.py: [https://docs.djangoproject.com/en/2.2/ref/django-admin/](https://docs.djangoproject.com/en/2.2/ref/django-admin/)  

##### Important Commands:
* `python manage.py makemigrations` - this will prepare any migrations for the database. **&ast;necessary when any models are modified&ast;**
* `python manage.py migrate` - this will perform any migrations for the database. **&ast;necessary when any models are modified&ast;**  

Any updates to the views will require a server restart via: `sudo service apache2 restart`  

## API Routes
For any REST GET routes that require the user to be authenticated, the following header must be supplied to authenticate the user: `Authorization: Token <auth_token_string>`  
For example: `Authorization: Token f5fdca63b0ed56da08b96ab69c17ef63cc64f3fd`  
Using cURL: `curl -X GET https://claytoncornett.tk/api/hello_world/?format=json -H 'Authorization: Token f5fdca63b0ed56da08b96ab69c17ef63cc64f3fd'`

* **/api/login/**  
  * Method: POST  
  * Input:  
    * username: string  
    * password: string  
  * Output:  
    * Success:  
       ```json
       {
         "token": "f5fdca63b0ed56da08b96ab69c17ef63cc64f3fd"
       }
       ```  
    * Invalid Credentials:  
      ```json
      {
        "non_field_errors": [
          "Unable to log in with provided credentials."
        ]
       }
       ```
    * Field Errors:  
      ```json
      {
        "<field_name>": [
          "This field is required."
        ]
      }
      ```
  * Description  
    * If the provided login credentials are valid, it returns a token for SSO authentication.  
    * If the provided login credentials or request are invalid, it returns error messages.  
    * ***For JSON Response, `?format=json` must be provided at the end of the URL***  
    
* **/api/user/**  
  * Method: GET  
    * Input: *None*  
    * Output:  
      * Success:  
         ```json
         {
           "email": "<email>",
           "first_name": "<first_name>",
           "last_name": "<last_name>",
           "phone": "<phone_number OR null>",
           "park": [
             <park object>
           ] OR null
         }
         ```  
      * Non-Field Errors  
        ```json
        {
          "non_field_errors": [
            "<error_description>"
          ]
         }
         ```
    * Description  
      * Returns the user's account profile in JSON.
      * ***MUST BE AUTHENTICATED***
  * Method: POST  
    * Input:  
      * email: string, *required*  
      * first_name: string, *required*  
      * last_name: string, *required*  
      * phone: string  
      * password: string, *required*  
      * password2: string, *required*, *must match password*  
      * park: array of park JSON objects, *default:* `null`  
    * Output:  
      * Success:  
         ```json
         {
           "token": "f5fdca63b0ed56da08b96ab69c17ef63cc64f3fd",
           "user": <user_JSON_object>
         }
         ```  
      * Non-Field Errors ex) User already exists:  
        ```json
        {
          "non_field_errors": [
            "Unable to log in with provided credentials."
          ]
         }
         ```
      * Field Errors ex) Invalid field, passwords did not match, etc.:  
        ```json
        {
          "<field_name>": [
            "This field is required."
          ]
        }
        ```
    * Description  
      * If all fields are valid, creates a user and a token for the user. Returns the token as well as a copy of the user's account details
      * Do not need to be authenticated, will return field and non-field errors if input does not pass validation
  * Method: PATCH  
    * Input:  
      * email: string  
      * first_name: string  
      * last_name: string  
      * phone: string  
      * password: string  
      * password2: string, *required if password is in input*, *must match password*  
      * park: array of park JSON objects, *default:* `null`  
    * Output:  
      * Success:  
         ```json
         {
           <user_JSON_object>
         }
         ```  
      * Non-Field Errors ex) User already exists:  
        ```json
        {
          "non_field_errors": [
            "Unable to log in with provided credentials."
          ]
         }
         ```
      * Field Errors ex) Invalid field, passwords did not match, etc.:  
        ```json
        {
          "<field_name>": [
            "This field is required."
          ]
        }
        ```
    * Description  
      * Updates the current user to the new field values. Only have to specify which fields are being updated. 
      * ***MUST BE AUTHENTICATED***
* **/api/user/ticket/**  
  * Method: GET  
    * Input: *None*  
    * Output:  
      * Success:  
         ```json
         [
           {
            "pk": <ticket_id>,
            "date": "<ISO_date_string>",
            "garage": {
              "pk": <garage_id>,
              "name": <garage_name>
            }
          },
          {...}
         ]
         ```  
      * Non-Field Errors  
        ```json
        {
          "non_field_errors": [
            "<error description>"
          ]
         }
         ```
    * Description  
      * Returns all of the tickets the current user has created.
      * ***MUST BE AUTHENTICATED***
  * Method: POST  
    * Input:  
      * date: string, *ISO Format*, *required*  
      * garage_id: number, *required*    
    * Output:  
      * Success:  
         ```json
         {
           "pk": <ticket_id>,
           "date": <ISO_date_string>,
           "garage": {
             "pk": <garage_id>,
             "name": <garage_name>
           }
         }
         ```  
      * Non-Field Errors  
        ```json
        {
          "non_field_errors": [
            "Unable to log in with provided credentials."
          ]
         }
         ```
      * Field Errors ex) Invalid field, garage DNE, etc.:  
        ```json
        {
          "<field_name>": [
            "This field is required."
          ]
        }
        ```
    * Description  
      * If all fields are valid, creates a ticket for the user. Returns a copy of the created ticket
      * Will return field and non-field errors if input does not pass validation
      * ***MUST BE AUTHENTICATED***
  * Method: PATCH  
    * Input:  
      * pk: number, *ticket_id*, *required*
      * date: string, *ISO Format*  
      * garage_id: number  
    * Output:  
      * Success:  
         ```json
         {
           "pk": <ticket_id>,
           "date": <ISO_date_string>,
           "garage": {
             "pk": <garage_id>,
             "name": <garage_name>
           }
         }
         ```  
      * Non-Field Errors  
        ```json
        {
          "non_field_errors": [
            "Unable to log in with provided credentials."
          ]
         }
         ```
      * Field Errors ex) Invalid field, garage DNE, etc.:  
        ```json
        {
          "<field_name>": [
            "This field is required."
          ]
        }
        ```
    * Description  
      * Updates the specified ticket to the new field values.
      * Only have to specify which fields are being updated. 
