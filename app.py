import csv
from flask import Flask, request, jsonify, render_template
from random import randint
import boto3
from datetime import datetime
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
    
    client = boto3.client('iam')
    response = client.list_access_keys(UserName=username)
    result = response['AccessKeyMetadata']

    for i in result:

        join_date = i['CreateDate']

        tz_info = join_date.tzinfo
        diff = datetime.now(tz_info)-join_date


        # print(f"User: {username}, secret creds age: {diff.days}")

        return diff.days

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
        print("secret credentials age - ")
        diff = list_access_keys(username=i['UserName'])
        print(diff)
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

# print policies
def list_user_policies(username):

    # print("UserName = ",username)
    result = None

    client = boto3.client('iam')
    response = client.list_user_policies(UserName=username)
    # print(response)
    result = response['PolicyNames']

    return result

# function to get user's attached policies
def list_attached_user_policies(username):

    result = None

    client = boto3.client('iam')
    response = client.list_attached_user_policies(UserName=username)

    result = response['AttachedPolicies']
    list1 = []
    for item in result:
        list1.append(item['PolicyName'])

    return list1

# function to list user's IAM policies and make a list
def list__policies():

    result = None

    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']

    for i in result:
        list3 = []
        print(i['UserName'])
        list1 = list_user_policies(username=i['UserName'])
        list2 = list_attached_user_policies(username=i['UserName'])

        list3 = list1 + list2
        
        for policy in list3:
            print(policy)
        print("*"*80)
        
# function to find user details whose access key is older than x days
def access_key_old():

    x = int(input("Enter no. of days - "))

    result = None
    users = []

    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']

    for i in result:

        diff = int(list_access_keys(username=i['UserName']))
        # print(diff)

        if (diff > x):
            users.append({'name': i['UserName']})
            print(i['UserName'])
            print("*"*80)
    
    return users

# function to find out user whose MFA is not enabled
def mfa_enabled():

    print("Users whose MFA is not enabled - ")
    result = None

    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']

    for user in result:
        MFA = client.list_mfa_devices(UserName=user['UserName'])

        MFA_devices = MFA['MFADevices']

        if not MFA_devices:
            print(user['UserName'])

# function to check for users who have adminstration policy attached to them
def check_adminstration_policy():

    print("Users who have adminstration access - ")
    result = None

    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']

    for i in result:
        list3 = []
        list1 = list_user_policies(username=i['UserName'])
        list2 = list_attached_user_policies(username=i['UserName'])

        list3 = list1 + list2

        for search in list3:
            # print(search)
            if (search == 'AdministratorAccess'):
                print(i['UserName'])


# main function
def main():
    result = list_users()
    print(result)

    diff = list_users_age()
        
    generate_csv()

    list__policies()

    access_key_old()
        
    mfa_enabled()

    check_adminstration_policy()
    
if __name__ == "__main__":
    main()