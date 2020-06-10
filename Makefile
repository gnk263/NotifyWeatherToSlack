BUCKET_NAME := gnk263-sam-bucket
STACK_NAME := Notify-Weather-To-Slack-App
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
			ApiKey=$(SSM_API_KEY) \
			SlackUrl=$(SSM_SLACK_URL)

delete-stack:
	aws cloudformation delete-stack \
		-- stack-name $(STACK_NAME)