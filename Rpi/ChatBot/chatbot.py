import TextToSpeech.textToSpeechOnline02 as TTS
import SpeechToText.speechToTextOnline as STT
import LLM.llm as LLM

debug01 = True

print("Initialized Chatbot")

def Main():
	# ~ userInput = "Hey there how its going on?"
	userInput = STT.Main()

	
	print("userInput:",userInput)

	if(userInput is not None):
		if(debug01): print("Not null")
		
		userInput = f"""For the user input given below
		answer as you are a JARVIS from Iron Man 
		user input = {userInput}"""
		
		print("userInput:",userInput)
		
		llmResponce = LLM.Main(userInput)

		print("llmResponce:",llmResponce)

		TTS.Main(llmResponce)

while(True):
	Main()
