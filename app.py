import os
import boto3
import pymysql
from flask import Flask, request, render_template
from datetime import date, datetime
import json

app = Flask(__name__)

# Configure AWS credentials
s3 = boto3.client('s3')
rds_host = 'rds-database-1.cvnkpkz7gh8g.us-east-1.rds.amazonaws.com'
rds_database = 'mydb'

# Retrieve RDS credentials from AWS Secrets Manager
def get_rds_credentials():
    secret_name = "test/mysql"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return secret

# Establish RDS connection using retrieved credentials
def establish_rds_connection():
    secret = get_rds_credentials()
    rds_credentials = json.loads(secret)

    conn = pymysql.connect(
        host=rds_host,
        user=rds_credentials['username'],
        password=rds_credentials['password'],
        database=rds_database
    )
    return conn

# Establish RDS connection
conn = establish_rds_connection()

# Create S3 bucket
bucket_name = 's3-upload-atri'
s3.create_bucket(Bucket=bucket_name)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        file_extension = os.path.splitext(filename)[1]

        # Upload file to S3 bucket
        s3.upload_fileobj(file, bucket_name, filename)

        # Save file metadata in RDS database
        query = "INSERT INTO s3_upload_metadata (filename, file_extension, upload_date, upload_time) VALUES (%s, %s, %s, %s)"

        # Get the current date and time
        current_date = date.today()
        current_time = datetime.now().strftime("%H:%M:%S")

        # Pass the values as arguments to the execute function
        cursor = conn.cursor()
        cursor.execute(query, (filename, file_extension, current_date, current_time))
        conn.commit()

        return 'File uploaded successfully!'

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)