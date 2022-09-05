#!/bin/env bash

. update.config
echo $url
echo $filename
echo "$url"/"$filename".tgz
echo $filename
wget "$url"/"$filename".tgz
tar -zxvf "$filename"
mongo sds --eval 'db.dropDatabase()'
mongorestore -d sds $filename --host $mongo_host
