#!/bin/bash

USER="labuser"
PASSWORD="labpassword"
JSON_FILE="data/inventory.json"

echo "Reading inventory..."

IPS=$(jq -r '.. | .ip? // empty' $JSON_FILE)

for ip in $IPS; do
(
   echo "Deploying key → $ip"
   sshpass -p "$PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no $USER@$ip
) &
done

wait

echo "SSH Key deployment completed"