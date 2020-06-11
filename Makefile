BUCKET_NAME := gnk263-sam-bucket
TARGET_NAME := tokyo
BASE_STACK_NAME := Notify-Weather-To-Slack-App

###

STACK_NAME := $(BASE_STACK_NAME)-$(TARGET_NAME)
SSM_LATITUDE_KEY := /$(BASE_STACK_NAME)/$(TARGET_NAME)/Latitude
SSM_LONGITUDE_KEY := /$(BASE_STACK_NAME)/$(TARGET_NAME)/Longitude
SSM_SLACK_URL := /$(BASE_STACK_NAME)/$(TARGET_NAME)/slack_url
SSM_API_KEY := /$(BASE_STACK_NAME)/apikey

###

deploy:
	sam build

	sam package \
		--output-template-file packaged.yaml \
		--s3-bucket $(BUCKET_NAME)

	sam deploy \
		--template-file packaged.yaml \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			TargetName=$(TARGET_NAME) \
			Latitude=$(SSM_LATITUDE_KEY) \
			Longitude=$(SSM_LONGITUDE_KEY) \
			ApiKey=$(SSM_API_KEY) \
			SlackUrl=$(SSM_SLACK_URL)

test:
	LATITUDE=123.45 \
	LONGITUDE=12.345 \
	API_KEY=xxxyyyzzz \
	SLACK_URL=dummy \
		python -m pytest tests/ -v

delete-stack:
	aws cloudformation delete-stack \
		--stack-name $(STACK_NAME)

display-setting:
	@echo BUCKET_NAME = $(BUCKET_NAME)
	@echo TARGET_NAME = $(TARGET_NAME)
	@echo BASE_STACK_NAME = $(BASE_STACK_NAME)
	@echo STACK_NAME = $(STACK_NAME)
	@echo SSM_LATITUDE_KEY = $(SSM_LATITUDE_KEY)
	@echo SSM_LONGITUDE_KEY = $(SSM_LONGITUDE_KEY)
	@echo SSM_SLACK_URL = $(SSM_SLACK_URL)
	@echo SSM_API_KEY = $(SSM_API_KEY)
