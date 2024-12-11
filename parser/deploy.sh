#!/usr/bin/env bash

cd parser
pip install -r requirements.txt -t ./deps
cd deps
zip -r ../function.zip .
cd ..
zip function.zip parse_repos.py

yc serverless function create --name github-parser
yc serverless function version create \
  --function-name=github-parser \
  --runtime python311 \
  --entrypoint parse_repos.handler \
  --memory 128m \
  --execution-timeout 300s \
  --source-path ./function.zip \
  --environment POSTGRES_HOST="host" POSTGRES_PORT="5432" POSTGRES_USER="user" POSTGRES_PASSWORD="pass" POSTGRES_DB="db" GITHUB_TOKEN="ghp_xxxxxx"

yc serverless trigger create timer --name parser-cron \
  --cron-expression "0 0 * * *" \
  --invoke-function-name github-parser