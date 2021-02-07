import os, sys, getopt
import mysql.connector
from getpass import getpass
from collation_helper import get_collation
from updatingmissing import update_missing
from addmissingcolumn import add_missing
from clean_parameters import clean_parameters
from updatecolumns import updatecolumns
import os.path
from os import path

def main(argv):
    file = open("report.txt", "w")
    remote_host = "None"
    remote_user = "None"
    remote_password = "None"
    remote_database = "None"
    local_host = "None"
    local_user = "None"
    local_password = "None"
    local_database = "None"

    if path.exists("userinfo.txt"):
        f = open("userinfo.txt", "r")
        lines = f.readlines()
        remote = lines[0]
        local = lines[1]
        remote = remote.split(", ")
        local = local.split(", ")
        remote_host = remote[0]
        remote_user = remote[1]
        remote_password = remote[2]
        remote_database = remote[3][:-1]
        local_host = local[0]
        local_user = local[1]
        local_password = local[2]
        local_database = local[3][:-1]
    else:
        remote_host = input("Remote host (ex: 10.8.0.1 or localhost): ")
        remote_user = input("Remote user (ex: root or user123): ")
        remote_password = getpass("Remote password: ")
        remote_database = input("Remote database (ex: yourdbname): ")
        local_host = input("Local host (ex: 10.8.0.1 or localhost): ")
        local_user = input("Local user (ex: root or user123): ")
        local_password = getpass("Local password: ")
        local_database = input("Local database (ex: urdbname): ")

    print("connecting to remote.....\n")
    file.write("connecting to remote.....\n")
    try:
        #mydbremote = mysql.connector.connect(host="10.8.0.1",user="root",password="Waterwater1!",database="safire")
        mydbremote = mysql.connector.connect(host=remote_host,user=remote_user,password=remote_password,database=remote_database)
        print("Successfully Connected to:", mydbremote.get_server_info())
        file.write(f"Successfully Connected to: {mydbremote.get_server_info()}\n")
    except:
        print("Something went wrong, unable to connect to db")
        file.write(f"Something went wrong, unable to connect to db\n")
        raise
        return
        print("\n")
        file.write("\n")

    print("connecting to local.....\n")
    file.write("connecting to local.....\n")
    try:
        # mydblocal = mysql.connector.connect(host="localhost",user="root",password="*****", database="safire")
        mydblocal = mysql.connector.connect(host=local_host,user=local_user,password=local_password,database=local_database)
        print("Successfully Connected to:", mydblocal.get_server_info())
        file.write(f"Successfully Connected to: {mydblocal.get_server_info()}\n")
    except:
        print("Something went wrong, unable to connect to db")
        file.write(f"Something went wrong, unable to connect to db\n")
        raise
        return
        print("\n")
        file.write("\n")

    #if the user successfully gets here, we store information in userinfo.txt so he doesnt need
    # to login again
    if path.exists("userinfo.txt"):
        pass
    else:
        userinfo = open("userinfo.txt", "w")
        userinfo.write(f"{remote_host}, {remote_user}, {remote_password}, {remote_database}\n")
        userinfo.write(f"{local_host}, {local_user}, {local_password}, {local_database}\n")
        userinfo.close()

    print("=====================================\n")
    file.write("=====================================\n")
    print("'             DB Utility            '\n")
    file.write("'             DB Utility            '\n")
    print("=====================================\n")
    file.write("=====================================\n")

    # enter your code here!
    cursorremote = mydbremote.cursor()
    cursorlocal = mydblocal.cursor()

    cursorremote.execute("SHOW TABLES")
    cursorlocal.execute("SHOW TABLES")
    # local_databases = cursorlocal.fetchall()
    remote_databases = cursorremote.fetchall()
    local_databases = cursorlocal.fetchall()

    remote_db_array = []
    for remotedb in remote_databases:
        remote_db_array.append(remotedb[0])

    local_db_array = []
    for localdb in local_databases:
        local_db_array.append(localdb[0])

    print("Remote DB Tables: \n")
    file.write("Remote DB Tables: \n")
    print(remote_db_array)
    file.write(f"{remote_db_array} \n")
    print("\n")
    file.write("\n")
    print("Local DB Tables: \n")
    file.write("Local DB Tables: \n")
    print(local_db_array)
    file.write(f"{local_db_array}\n")
    print("\n")
    file.write("\n")

    print("Looking for missing tables...\n")
    file.write("Looking for missing tables...\n")

    local_missing = []
    for missing in remote_db_array:
        if missing not in local_db_array:
            local_missing.append(missing)

    print("MISSING TABLES:", local_missing)
    file.write(f"MISSING TABLES: {local_missing}\n")
    print("\n")
    file.write("\n")

    #create new table for missing columns in a new database

    if len(local_missing) == 0:
        print("Your overall databse tables are in line with server.\n")
        file.write("Your overall databse tables are in line with server.\n")
    else:
        #check if user wants to add new tables to their local database
        addtablecheck = input("Would you like to automatically add the missing tables to your database? (y/n) ")
        if addtablecheck.lower() == 'y' or addtablecheck.lower() == 'yes':
            print("Your local database is missing tables, adding missing tables to your database...\n")
            file.write("Your local database is missing tables, adding missing tables to your database...\n")
            #i decided to create tables directly into the local database because if a table didn't exist there before, it wouldn't affect anything.
            update_missing(cursorremote, cursorlocal, local_missing, "safire")
        else:
            print("Ok, we will move on to comparing individual table structures to find missing parts.")
            file.write("Ok, we will move on to comparing individual table structures to find missing parts.\n")


    print("\n")
    file.write("\n")
    print("Comparing individual schemas from each table.... \n")
    file.write("Comparing individual schemas from each table.... \n")

    #cursorlocal
    #cursorremote
    mismatched_columns = []
    for table in remote_db_array:
        # print(f"Checking {table} for missing columnss....\n")
        table_mismatch_details = {}
        schemaquery = f"select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{table}' and TABLE_SCHEMA = 'safire'"
        query_categories = ["column_name", "column_default", "is_nullable", "column_type", "column_key", "extra", "collation_name"]
        cursorremote.execute(schemaquery)
        remote_table_schema = cursorremote.fetchall()
        cursorlocal.execute(schemaquery)
        local_table_schema = cursorlocal.fetchall()

        remote_table = []
        local_table = []
        for item in remote_table_schema:
            remote_table.append(item[0])

        for item in local_table_schema:
            local_table.append(item[0])

        missing_columns = []

        i = 0
        for item in remote_table:
            if item not in local_table:
                #i want to keep the order of the columns the same to make comparing easier down the line
                if i == 0:
                    missing_columns.append(["FIRST", item])
                else:
                    missing_columns.append([f"AFTER {local_table[i-1]}", item])

            i += 1

        #I've made the decision that order does not matter, so i'll just add the missing columns at the end

        # print(missing_columns)


        if len(missing_columns) == 0:
            print(f"Your {table} in line with server.")
            file.write(f"Your {table} in line with server.\n")
            # pass
        else:
            #check if user wants to add new tables to their local database
            addtablecheck = input("Would you like to automatically add the missing columns to your database? (y/n) ")
            if addtablecheck.lower() == 'y' or addtablecheck.lower() == 'yes':
                print("Your local database is missing tables, adding missing tables to your database...\n")
                file.write("Your local database is missing tables, adding missing tables to your database...\n")
                #just like before, im creating things directly in the table cause if it wasn't there before, then it damages nothing xD
                add_missing(cursorremote, cursorlocal, missing_columns, table, "safire")
            else:
                print("Ok, we will move on to comparing individual table structures to find missing parts.")
                file.write("Ok, we will move on to comparing individual table structures to find missing parts.\n")
        # for column
        # update the remote_table_schema and the local_table_schema arrays after the change has happened
        cursorremote.execute(schemaquery)
        remote_table_schema = cursorremote.fetchall()
        cursorlocal.execute(schemaquery)
        local_table_schema = cursorlocal.fetchall()
        # print("remote schema", remote_table_schema)
        # print("local schema", local_table_schema)
        # print(f"Checking {table}'s columns for mismatches....")
        i = 0
        colbycol = {}
        for remote_column in remote_table_schema:
            #i'm assuming column names are unique
            column_name = remote_column[0]
            schemaquery = f"select column_name, column_default, is_nullable, column_type, column_key, extra, collation_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{table}' and TABLE_SCHEMA = 'safire' and column_name = '{column_name}'"
            cursorremote.execute(schemaquery)
            remote_column = cursorremote.fetchall()
            remote_column = remote_column[0] #comes back as an array with a single element, so just getting the first element
            cursorlocal.execute(schemaquery)
            local_column = cursorlocal.fetchall()
            local_column = local_column[0]
            j = 0
            colbycol[remote_column[0]] = []
            for col in remote_column:
                loc = local_column[j]

                # print("before clean ", col, "and ", loc)
                if loc:
                    if type(loc) is not str:
                        loc = loc.decode("utf-8").lower()
                else:
                    loc = "NoneType"

                if col:
                    if type(col) is not str:
                        col = col.decode("utf-8").lower()
                else:
                    col = "NoneType"

                #clean parameters takes out everything but spaces and numbers and letters
                # this way i can effectively compare things
                col2 = clean_parameters(col)
                loc2 = clean_parameters(loc)
                # print("after clean ", col, "and ", loc)

                if col2 in loc2 or loc2 in col2 or col2 == loc2:
                    pass
                else:
                    if col2 == "nonetype" and loc2 == "defaultgenerated":
                        pass
                    elif "defaultgenerated" in loc2:
                        pass
                    elif col2 == "null" and loc2 == "nonetype" or loc2 == "null" and col2 == "nonetype":
                        pass
                    else:
                        colbycol[remote_column[0]].append({query_categories[j]: [col, loc]})

                    # print(colbycol)


                j += 1

            if len(colbycol[remote_column[0]]) == 0:
                # print("there were no mismatches for this column")
                del colbycol[remote_column[0]]

            i += 1

        # print(f"number of mismatches: {len(colbycol.keys())} \n")
        if len(colbycol.keys()) > 0:
            table_mismatch_details[table] = colbycol
            mismatched_columns.append(table_mismatch_details)

    print("\n")
    file.write("\n")
    print("Checking if there are differences in each column.... \n")
    file.write("Checking if there are differences in each column.... \n")
    if len(mismatched_columns) > 0:
        print("\n")
        file.write("\n")
        print("Summary of columns that had differences: \n")
        file.write("Summary of columns that had differences: \n")
        for mismatched in mismatched_columns:
            mis_tab_keys = list(mismatched)
            table = mis_tab_keys[0]
            # table = mismatched[mis_col_keys[i]]
            print(f"Table > {table}")
            file.write(f"Table > {table}\n")
            mis_col_keys = list(mismatched[table])
            for column in mis_col_keys:
                print(f"     column > {column}")
                file.write(f"     column > {column}\n")
                for detail in mismatched[table][column]:
                    mis_det_keys = list(detail)
                    det = mis_det_keys[0]
                    print(f"          column_detail > {det}")
                    file.write(f"          column_detail > {det}\n")
                    det_rem = detail[det][0]
                    det_loc = detail[det][1]
                    print(f"                   remote > {det_rem}")
                    file.write(f"                   remote > {det_rem}\n")
                    print(f"                   local > {det_loc}")
                    file.write(f"                   local > {det_loc}\n")


            print("\n")
            file.write("\n")


        print("Going through each difference...")
        file.write("Going through each difference...\n")

        for mismatched in mismatched_columns:
            mis_tab_keys = list(mismatched)
            table = mis_tab_keys[0]
            # table = mismatched[mis_col_keys[i]]
            print(f"Table > {table}")
            file.write(f"Table > {table}\n")
            mis_col_keys = list(mismatched[table])
            for column in mis_col_keys:
                print(f"     column > {column}")
                file.write(f"     column > {column}\n")
                for detail in mismatched[table][column]:
                    mis_det_keys = list(detail)
                    det = mis_det_keys[0]
                    print(f"          column_detail > {det}")
                    file.write(f"          column_detail > {det}\n")
                    det_rem = detail[det][0]
                    det_loc = detail[det][1]
                    print(f"                   remote > {det_rem}")
                    file.write(f"                   remote > {det_rem}\n")
                    print(f"                   local > {det_loc}")
                    file.write(f"                   local > {det_loc}\n")
                    print("\n")
                    file.write("\n")
                    prompt_fix = input("Would you like to change this? (y/n) ")
                    if prompt_fix.lower() == 'y' or prompt_fix.lower() == 'yes':
                        print("Your local database is missing tables, adding missing tables to your database...\n")
                        file.write("Your local database is missing tables, adding missing tables to your database...\n")
                        updatecolumns(cursorremote, cursorlocal, table, column, det, det_rem, "safire")
                        print("\n")
                        file.write("\n")

            print("\n")
            file.write("\n")
    else:
        print("There are no differences between remote table columns and local table columns! \n")
        file.write("There are no differences between remote table columns and local table columns! \n")


    print("Database service completed!")
    file.write("Database service completed!\n")

if __name__ == "__main__":
    main(sys.argv[1:])
