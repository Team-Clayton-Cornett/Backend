# Team Clayton Cornett Backend
## Overview
The backend is an Ubuntu 18.04 instance hosted on AWS EC2 running Django v2.2.9 with MongoDB v4.2.2 and Djongo v1.3.0 as the SQL connector.

The main/prod project is located in `/opt/capstone`.  
IP: 34.234.47.39  
URL: claytoncornett.tk  

Access Logs: `/var/log/apache2/capstone/access.log`  
Error Logs: `/var/log/apache2/capstone/error.log`  

Viewing the error logs: `sudo less /var/log/apache2/capstone/error.log` OR `sudo cat /var/log/apache2/capstone/error.log`  

Individual dev projects are located in `~/capstone`.
URL: <pawprint>.claytoncornett.tk

Access Logs: `/var/log/apache2/capstone_<pawprint>/access.log`
Error Logs: `/var/log/apache2/capstone_<pawprint>/access.log`

Viewing the error logs: `sudo less /var/log/apache2/capstone_<pawprint>/error.log` OR `sudo cat /var/log/apache2/capstone_<pawprint>/error.log`  

### File Hierarchy

/opt/capstone/ OR ~/capstone  
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
        forms.py  
        managers.py  
        models.py  
        permissions.py  
        serializers.py  
        tests.py  
        views.py  
        viewsets.py

### Views
Views are how the server deals with requests that were routed by URLs. This is where the logic is defined when a request is made via a URL.  
Views for the api app (the main app for the backend) are located at `/opt/capstone/api/views.py`  
More documentation on Django views: [https://docs.djangoproject.com/en/2.2/topics/http/views/](https://docs.djangoproject.com/en/2.2/topics/http/views/)  
*Note:* All of the API views will be returning [JSON responses](https://docs.djangoproject.com/en/2.2/ref/request-response/#jsonresponse-objects) rather than normal [HTTP responses](https://docs.djangoproject.com/en/2.2/ref/request-response/#django.http.HttpResponse).

### Viewsets
Viewsets are how the server deals with requests that were routed by URLs and handle a lot of this through serializers. This is where the logic is defined when a request is made via a URL for Django REST Framework Serializer objects.  
Views for the api app (the main app for the backend) are located at `/opt/capstone/api/viewsets.py`  
More documentation on DRF viewsets: [https://www.django-rest-framework.org/api-guide/viewsets/](https://www.django-rest-framework.org/api-guide/viewsets/)  

### Models
Models are how the objects stored in the database are defined.  
Models for the api app (the main app for the backend) are located at `/opt/capstone/api/models.py`  
More documentation on Django models: [https://docs.djangoproject.com/en/2.2/topics/db/models/](https://docs.djangoproject.com/en/2.2/topics/db/models/)

### Serializers
Serializers are how Django REST Framework converts Django models into JSON objects.
Serializers for the api app (the main app for the backend) are located at `/opt/capstone/api/serializers.py`
More documentation on DRF serializers: [https://www.django-rest-framework.org/api-guide/serializers/](https://www.django-rest-framework.org/api-guide/serializers/)

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
      * Success (HTTP 200 SUCCESS status):  
         ```
         {
           "token": "f5fdca63b0ed56da08b96ab69c17ef63cc64f3fd"
         }
         ```  
      * Invalid Credentials (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "Unable to log in with provided credentials."
          ]
         }
         ```
      * Field Errors (HTTP 400 BAD REQUEST status):  
        ```
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
      * Success (HTTP 200 SUCCESS status):  
         ```
         {
           "email": "<email>",
           "first_name": "<first_name>",
           "last_name": "<last_name>",
           "phone": "<phone_number OR null>"
         }
         ```  
      * Non-Field Errors (HTTP 400 BAD REQUEST status):  
        ```
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
    * Output:  
      * Success (HTTP 201 CREATED status):  
         ```
         {
           "token": "f5fdca63b0ed56da08b96ab69c17ef63cc64f3fd",
           "user": <user_JSON_object>
         }
         ```  
      * Non-Field Errors ex) User already exists (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "Unable to log in with provided credentials."
          ]
         }
         ```
      * Field Errors ex) Invalid field, passwords did not match, etc. (HTTP 400 BAD REQUEST status):  
        ```
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
      * Success (HTTP 200 SUCCESS status):  
         ```
         {
           <user_JSON_object>
         }
         ```  
      * Non-Field Errors ex) User already exists (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "Unable to log in with provided credentials."
          ]
         }
         ```
      * Field Errors ex) Invalid field, passwords did not match, etc. (HTTP 400 BAD REQUEST status):  
        ```
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
  * Method: POST  
    * Input:  
      * park_id: number, *required*
      * date: string, *ISO Format*, *required*   
    * Output:  
      * Success (HTTP 201 CREATED status):  
         ```
         {
           "date": <ISO_date_string>,
         }
         ```  
      * Non-Field Errors (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "<non-field error>"
          ]
         }
         ```
      * Field Errors ex) Invalid date, park DNE, etc. (HTTP 400 BAD REQUEST status):  
        ```
        {
          "<field_name>": [
            "This field is required."
          ]
        }
        ```
    * Description  
      * If all fields are valid, creates a ticket for the specified park. Returns a copy of the created ticket
      * Will return field and non-field errors if input does not pass validation
      * Will overwrite any existing ticket data.
      * ***MUST BE AUTHENTICATED***
  * Method: PATCH  
    * Input:  
      * park_id: number, *required*
      * date: string, *ISO Format*, *required*   
    * Output:  
      * Success (HTTP 200 SUCCESS status):  
         ```
         {
           "date": <ISO_date_string>,
         }
         ```  
      * Non-Field Errors (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "<non-field error>"
          ]
         }
         ```
      * Field Errors ex) Invalid date, park DNE, etc. (HTTP 400 BAD REQUEST status):  
        ```
        {
          "<field_name>": [
            "This field is required."
          ]
        }
        ```
    * Description  
      * If all fields are valid, updates the ticket for the specified park. Returns a copy of the created ticket
      * Will return field and non-field errors if input does not pass validation
      * Will overwrite any existing ticket data.
      * ***MUST BE AUTHENTICATED***
* **/api/user/park/**  
  * Method: GET  
    * Input:  
      * pk: number, *optional*
    * Output:  
      * Success (HTTP 200 SUCCESS status):  
         ```
         [
          {
            "start": "<ISO_date_string",
            "end": "<ISO_date_string> OR null",
            "ticket": {
              "date": "<ISO_date_string>"
            } OR null,
            "garage": {
              "pk": <park_garage_id>,
              "name": "<park_garage_name>"
            }
          },
          {...}
        ]
         ```  
      * Non-Field Errors (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "<error description>"
          ]
         }
         ```
    * Description  
      * Returns all of the current user's parks.
      * If `pk` is specified, it will only return the specific park requested.
      * ***MUST BE AUTHENTICATED***
  * Method: POST  
    * Input:  
      * start: string, *ISO Format*, *required*  
      * end: string, *ISO Format*, *default:* `null`
      * garage_id: number, *required*  
      * ticket: ticket object, *default:* `null`
        * ```
          {
            "date": "<ISO_date_string>"
          }
          ```
    * Output:  
      * Success (HTTP 200 SUCCESS status):  
         ```
         {
           "start": "<ISO_date_string",
           "end": "<ISO_date_string> OR null",
           "ticket": {
             "pk": <ticket_id>,
             "date": "<ISO_date_string>",
             "garage": {
               "pk": <ticket_garage_id>,
               "name": "<ticket_garage_id>"
             }
           } OR null,
           "garage": {
             "pk": <park_garage_id>,
             "name": "<park_garage_name>"
           }
         }
         ```  
      * Non-Field Errors (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "Unable to log in with provided credentials."
          ]
         }
         ```
      * Field Errors ex) Invalid field, garage DNE, ticket DNE, etc. (HTTP 400 BAD REQUEST status):  
        ```
        {
          "<field_name>": [
            "This field is required."
          ]
        }
        ```
    * Description  
      * If all fields are valid, creates a park for the user. Returns a copy of the created park
      * Will return field and non-field errors if input does not pass validation
      * ***MUST BE AUTHENTICATED***
      
* **/api/user/password_reset/create/**  
  * Method: POST  
    * Input:  
      * email: string, *required*  
    * Output:  
      * Success (HTTP 201 CREATED status):  
         ```
         "Successfully created password reset token."
         ```  
      * Non-Field Errors (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "Unable to log in with provided credentials."
          ]
         }
         ```
      * Field Errors ex) Invalid email (HTTP 400 BAD REQUEST status):  
        ```
        {
          "<field_name>": [
            "A user with the specified email does not exist."
          ]
        }
        ```
    * Description  
      * If email is valid and associated with a user, creates a password reset token and sends an email with the token. Returns success message
      * Will return field and non-field errors if input does not pass validation
* **/api/user/password_reset/validate_token/**  
  * Method: POST  
    * Input:  
      * email: string, *required*  
      * token: string, *required*
    * Output:  
      * Success (HTTP 200 SUCCESS status):  
         ```
         {
           "token": "<password_reset_token>",
           "email": "<email>"
         }
         ```  
      * Non-Field Errors (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "<error message>"
          ]
         }
         ```
      * Field Errors ex) Invalid email (HTTP 400 BAD REQUEST status):  
        ```
        {
          "<field_name>": [
            "<error message>"
          ]
        }
        ```
        * Invalid Token (HTTP 400 BAD REQUEST status):  
        ```
        {
          "token": "Invalid token provided.",
          "attempts": <number of attempts remaining>
        }
        ```
    * Description  
      * If the provided email and token are valid, returns the email and token with 200 status. 
      * If the provided token is invalid for email, attempts is decremented by one and error message returned.
      * Only 3 attempts are allowed until a new token must be created
      * Will return field and non-field errors if input does not pass validation
* **/api/user/password_reset/reset/**  
  * Method: POST  
    * Input:  
      * email: string, *required*  
      * token: string, *required*
      * password: string, *required*
      * password2: string, *required*
    * Output:  
      * Success (HTTP 200 SUCCESS status):  
         ```
         {
           "token": "<user auth token>",
           "email": "<email>"
         }
         ```  
      * Non-Field Errors (HTTP 400 BAD REQUEST status):  
        ```
        {
          "non_field_errors": [
            "<error message>"
          ]
         }
         ```
      * Field Errors ex) Invalid email (HTTP 400 BAD REQUEST status):  
        ```
        {
          "<field_name>": [
            "<error message>"
          ]
        }
        ```
        * Invalid Token (HTTP 400 BAD REQUEST status):  
        ```
        {
          "token": "Invalid token provided.",
          "attempts": <number of attempts remaining>
        }
        ```
    * Description  
      * If the provided email and token are valid and the provided passwords are valid, returns the email and user auth token with 200 status. 
      * If the provided token is invalid for email, attempts is decremented by one and error message returned.
      * If the passwords are not valid, returns error message.
      * Only 3 attempts are allowed for invalid token until a new token must be created
      * Will return field and non-field errors if input does not pass validation
