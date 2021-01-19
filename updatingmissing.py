import os, sys, getopt
import mysql.connector
from getpass import getpass
from collation_helper import get_collation

def update_missing(cursorremote, cursorlocal, local_missing, table_schema):
    # print(table_name)
    # print(table_schema)
    for missing in local_missing:
        print("Adding this:", missing)
        #grabbing the schema information of the missing table from remote

        remoteschema = f"select column_name, column_default, is_nullable, column_type, column_key, extra, collation_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{missing}' and TABLE_SCHEMA = '{table_schema}'"

        # print(remoteschema)
        cursorremote.execute(remoteschema)
        missingschema = cursorremote.fetchall()
        # print(missingschema)
        # print(missingschema)
        createdcolumns = ""
        for column in missingschema:
            column_name = column[0]
            column_default = column[1]
            is_nullable = column[2]
            column_type = column[3]
            column_key = column[4]
            extra = column[5]
            collation_name = column[6]
            char_set = ""
            # parameters = f"{column_type} {char_set} {collation_name} {is_nullable} {extra} {column_key}"
            parameters = f"{column_type}"
            if collation_name != None:
                char_set = get_collation(collation_name)
                char_set = f" CHARACTER SET {char_set}"
                collation_name = f" COLLATE {collation_name}"
                parameters += char_set + collation_name

            if is_nullable == "NO":
                is_nullable = " NOT NULL"
                parameters += is_nullable

            if column_default != None:
                parameters += f" DEFAULT {column_default}"

            if len(extra) > 0:
                parameters += f" {extra}"

            if column_key == "PRI":
                column_key = " PRIMARY KEY"
                parameters += column_key

            if column != missingschema[-1]:
                createdcolumns += f"{column_name} {parameters}, "
            else:
                createdcolumns += f"{column_name} {parameters}"
        #
        # print(createdcolumns)
        # print("\n")
        executecreate = f"create table {missing} ({createdcolumns})"
        print("\n")
        print(executecreate)
        cursorlocal.execute(executecreate)
