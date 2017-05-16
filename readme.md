# Overview

This script listens to tweets and captures them into a DynamoDB database.
It uses the `tweepy` library; it's a python Twitter client.

The Twitter streaming API is called, and all tweets are pushed onto an AWS SNS queue.

The code in `lambda/captureTweet.py` runs in AWS Lambda. It's triggered by each tweet
in the SNS queue.


## Installation

Deploy on an AWS EC2 instance, Amazon Linux ami. Nothing big needed, t2.micro is fine.

1. Set up linux dependencies:
  ```
  $ yum -y install curl git unzip emacs-nox binutils python34
  ```

2. Install pip for python3

  ```
  $ curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
  $ sudo python3 get-pip.py
  $ rm get-pip.py
  ```

3. Set up Python3 dependencies:

  ```
  $ sudo /usr/local/bin/pip3 install PyYaml tweepy boto3
  ```

## Credentials and configuration

1. You'll need Twitter API credentials to listen to twitter. Put these into `config.yml`

2. You'll need AWS API credentials to write to SNS. Put these into `config.yml`

3. Choose the hashtags you wish to listen to. Put these into `tags.yml`

4. Create an AWS SNS queue, and update the value of `SNS_ARN` in `grab.py`.

5. Create a Lambda using the code in `lambda/captureTweet.py`.

6. Create a trigger to run `captureTweet` for each event in your SNS queue.

7. Create a DynamoDB database to hold the tweets, with a table called `tweetstream`.

## Usage

  ```
  $ ./grab.py
  ```
