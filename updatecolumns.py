import os, sys, getopt
import mysql.connector
from getpass import getpass
from collation_helper import get_collation

def updatecolumns(cursorremote, cursorlocal, table, column, col_detail, remote, table_schema):
    # print("table", table)
    # print("column", column)
    # print("col_detail", col_detail)
    # print("remote", remote)
    # print("table_schema", table_schema)
    #grabbing the schema information of the missing table from remote
    localschema = f"select column_default, is_nullable, column_type, column_key, extra, collation_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{table}' and TABLE_SCHEMA = '{table_schema}' and COLUMN_NAME='{column}'"

    # print(localschema)
    cursorremote.execute(localschema)
    current_schema = cursorremote.fetchall()
    # print(missingschema)
    # print(current_schema[0])
    current_schema = current_schema[0]
    createdcolumns = ""

    column_name = column

    # if the column detaiil is the one that needs to be adjusted then we put in the remote's data
    column_default = remote if col_detail == "column_default" else current_schema[0]
    is_nullable = remote if col_detail == "is_nullable" else current_schema[1]
    column_type = remote if col_detail == "column_type" else current_schema[2]
    column_key = remote if col_detail == "column_key" else current_schema[3]
    extra = remote if col_detail == "extra" else current_schema[4]
    collation_name = remote if col_detail == "collation_name" else current_schema[5]
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

    createdcolumns += f"{column_name} {parameters}"

    # print(createdcolumns)
    # print("\n")
    executecreate = f"alter table {table} change {column} {createdcolumns}"
    # print("\n")
    # print(executecreate)
    cursorlocal.execute(executecreate)
