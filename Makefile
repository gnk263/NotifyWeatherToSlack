BUCKET_NAME := gnk263-sam-bucket
STACK_NAME := Notify-Weather-To-Slack-App
SSM_LATITUDE_KEY := /Notify-Weather-To-Slack-App/Latitude
SSM_LONGITUDE_KEY := /Notify-Weather-To-Slack-App/Longitude
SSM_API_KEY := /Notify-Weather-To-Slack-App/apikey
SSM_SLACK_URL := /Notify-Weather-To-Slack-App/slack/notify-weather-tokyo/url

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
