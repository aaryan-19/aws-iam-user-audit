from logging import currentframe
import sys
import csv
from time import time
from flask import Flask, request, jsonify, render_template
from random import randint
import boto3
from datetime import datetime
import pytz

# Import DictWriter class from CSV module
from csv import DictWriter

# function to list users
def list_users():

    result = None

    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']

    return result

# function to list access key age
def list_access_keys(username):

    result = None
    print("secret credentials age - ")

    client = boto3.client('iam')
    response = client.list_access_keys(UserName=username)
    result = response['AccessKeyMetadata']

    for i in result:


        join_date = i['CreateDate']

        tz_info = join_date.tzinfo
        diff = datetime.now(tz_info)-join_date

        print(f"User: {username}, secret creds age: {diff.days}")


# function to list user's age and user's secret age
def list_users_age():

    result = None

    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']


    for i in result:
        print(i['UserName'])
        join_date = i['CreateDate']  

        tz_info = join_date.tzinfo

        diff = datetime.now(tz_info)-join_date
        print(f"User: {i['UserName']} Age: {diff.days}")
        list_access_keys(username=i['UserName'])
        print("*"*80)

# generate report
def generate_csv():

    result = list_users()

    # open the file in the write mode
    f = open('Report.csv', 'w')

    # header for excel
    header = ['Path','UserName','UserId','Arn','CreateDate','PasswordLastUsed']
    
    # create the csv writer
    writer = csv.writer(f)

    # write a row to the csv file
    writer.writerow(header)

    # using loop to insert details of single users in row
    for row in result:
        
        dictwriter_object = DictWriter(f, fieldnames=header)
  
        #Pass the dictionary as an argument to the Writerow()
        dictwriter_object.writerow(row)

    # close the file
    f.close()


# main function
def main():
    # result = list_users()

    # list_users_age(
        
    generate_csv()

if __name__ == "__main__":
    main()
 
