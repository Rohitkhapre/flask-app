import boto3

client = boto3.client('secretsmanager')

response = client.create_secret(
    Name = 'MyDBsecret',
    SecretString = '{"username": "admin", "password": "pass@123" }'
)