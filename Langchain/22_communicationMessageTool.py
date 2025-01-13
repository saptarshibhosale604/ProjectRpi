from langchain_community.utilities.twilio import TwilioAPIWrapper

twilio = TwilioAPIWrapper(
	account_sid="ACef716edc82de8e3926e33c79a0bca324",
	auth_token="b0d84a3f50425c84519267a854a06b95",
	from_number="+1 276 409 9702"
)

result = twilio.run("hello world", "+91 7058033447")

print("## ## result:", result)
