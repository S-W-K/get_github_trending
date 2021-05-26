#!/bin/sh

# setup ssh-private-key
mkdir -p /root/.ssh/
echo "${{ secrets.TRENDING_SCR }}" > /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa
ssh-keyscan -t rsa github.com >> /root/.ssh/known_hosts
