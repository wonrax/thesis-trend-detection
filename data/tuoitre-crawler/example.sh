#!/bin/sh

python3 data/tuoitre-crawler/main.py -cespt -f ./suc-khoe-articles.csv -n 5 -d 0.1 --category=suc-khoe 2> crawlError.log > crawl.log &