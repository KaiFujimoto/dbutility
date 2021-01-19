#Database Utility
---------------------------------
## Welcome to Kai's baby Database Utility
* Notes
  * I'm still relatively new to SQL and MySQL with Python, so there are definitely a few bugs
  * I know that right now, I only pull and check the outer schema, the individual table schemas, and the individual columns
    * For individual columns: I only check the following: column_name, column_default, is_nullable, column_type, column_key, extra, collation_name
 
---------------------------------
## How to install
* Make sure you have an environment active, I use ```virtualenv env``` to create my environment
* ```git clone (this repository)```
* ```cd dbutility```
* ```pip install -r requirements.txt```

---------------------------------
## How to use
* In the dbutility folder: ```python main.py```
  * There should be command line prompts for you to follow