# **LabIT Backend**

This repository contains code for the LabIT backend. This code takes 
care of:

    * Ordering a test
    * Creating an HL7 message
    * Sending the HL7 message back to this backend and parsing it
    * Authentication for mobile front-ends 
    * Sending push notifications
    * Acknowledging receipt of a notification
    * Updating a client services dashboard to show status of notifications
    
    
This is hosted on Heroku and talks to a database hosted on AWS. The
database credentials are in a file called **secrets.py**

## To run this locally:

1. Create a virtual environment if you want.
```mkvirtualenv labitenv```
2. Install the requirements.
```pip install -r requiriements.txt```
3. Run the server
```python manage.py runserver```