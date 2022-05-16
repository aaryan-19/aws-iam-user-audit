import csv
from flask import Flask, request, jsonify, render_template
from random import randint
import boto3
from datetime import datetime
from csv import DictWriter
import json

app = Flask("aws-users-audit")

@app.route('/')
def hello_world():
   return 'Hello World'

# function to list users
@app.route('/list-users')
def list_users():

    result = None

    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']

    return json.dumps(result, default=str)

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
@app.route('/list-users-age')
def list_users_age():

    result = None
    final_result = []

    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']

    for i in result:
        # print(i['UserName'])
        join_date = i['CreateDate']  

        tz_info = join_date.tzinfo

        diff_user = datetime.now(tz_info)-join_date
        # print(f"User: {i['UserName']} Age: {diff_user.days}")
        # print("secret credentials age - ")
        diff = list_access_keys(username=i['UserName'])
        # print(diff)
        # print("*"*80)
        final_result.append({
            'UserName': i['UserName'],
            'CreateDate': i['CreateDate'],
            'Age': diff_user.days,
            'AccessKeysAge': diff
        })
    
    return json.dumps(final_result, default=str)

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
# @app.route('/list-user-policies')
def list_user_policies(username):

    # print("UserName = ",username)
    result = None

    client = boto3.client('iam')
    response = client.list_user_policies(UserName=username)
    # print(response)
    result = response['PolicyNames']

    # return json.dumps(result,default=str)
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
@app.route('/list-policies')
def list__policies():

    result = None
    final_result = []
    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']

    for i in result:
        list3 = []
        # print(i['UserName'])
        list1 = list_user_policies(username=i['UserName'])
        list2 = list_attached_user_policies(username=i['UserName'])

        list3 = list1 + list2
        
        for policy in list3:
            print(policy)

        final_result.append({
            'UserName': i['UserName'],
            'Policy List': list3
        })        
        # print("*"*80)
    return json.dumps(final_result,default=str)
        
# function to find user details whose access key is older than x days
@app.route('/access-key-old/<days>')
def access_key_old(days):

    # x = int(input("Enter no. of days - "))

    x = int(days)
    # final_result = []

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
            # print(i['UserName'])
            # print("*"*80)

            
    
    return json.dumps(users,default=str)

# function to find out user whose MFA is not enabled
@app.route('/mfa-enabled')
def mfa_enabled():

    # print("Users whose MFA is not enabled - ")
    result = None
    final_result = []

    client = boto3.client('iam')
    response = client.list_users()
    result = response['Users']

    for user in result:
        MFA = client.list_mfa_devices(UserName=user['UserName'])

        MFA_devices = MFA['MFADevices']

        if not MFA_devices:
            # print(user['UserName'])
            final_result.append({
            'UserName': user['UserName'],
            'MFA': "Disabled"
            })     
    
    return json.dumps(final_result,default=str)

# function to check for users who have adminstration policy attached to them
@app.route('/check-admin-policy')
def check_adminstration_policy():

    # print("Users who have adminstration access - ")
    result = None
    final_result = []

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
                # print(i['UserName'])
                final_result.append({
                    'Username':i['UserName']
                })
    return json.dumps(final_result,default=str)


# main function
def main():
    # Converted into API
    result = list_users()
    # print(result)

    # Converted into API
    diff = list_users_age()
    
    # Ignore for now
    generate_csv()

    # Converted into API
    list__policies()

    # Converted into API
    access_key_old()
        
    # Converted into API    
    mfa_enabled()

    # Converted into API 
    check_adminstration_policy()
    
if __name__ == "__main__":
    app.run()
    # main()