import TextToSpeech.textToSpeechOnline02 as TTS
import SpeechToText.speechToTextOnline as STT
import LLM.llm as LLM
import userInputToScriptInvocation as UITSI
import Langchain.agent as Agent

debug01 = True

print("Initialized assistant.py")

conversationMode = "wakeUp" 	# sleep: Go to Hibernate
						                  # wakeUp: Goint to answer the user input
inputMode = "text" # text / speech
outputMode = "text" # text / speech

listWakeUpCalls = ["hey there", "hi there", "hey rpi"]
listSleepCalls = ["sleep now", "go to sleep", "we are done", "got it"]

roleDefining = f"""For the 'User Input' given below
answer as you are a 'JARVIS' from the 'Iron Man' movie
User Input = """

# ~ roleDefining = f"""For the 'User Input' given below
# ~ answer as you are a 'JARVIS' from the 'Iron Man' movie
# ~ User Input = """


# ~ who is the presedent of india

threadId = 0	# Memory Id for agent graph

import logging

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def InitializingLogging():
	
	# Create a file handler
	file_handler = logging.FileHandler("Logs/basic.log")
	# file_handler.setLevel(logging.DEBUG)
	file_handler.setLevel(logging.INFO)

	# Create a console handler
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.DEBUG)

	# Create a formatter and set it for both handlers
	formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
	file_handler.setFormatter(formatter)
	console_handler.setFormatter(formatter)

	# Add the handlers to the logger
	logger.addHandler(file_handler)
	logger.addHandler(console_handler)

	
	# ~ logging.basicConfig(
		# ~ level=logging.DEBUG,
		# ~ format="%(asctime)s %(levelname)s %(message)s",
		# ~ datefmt="%Y-%m-%d %H:%M:%S",
		# ~ filename="Logs/basic.log")
		
	logger.debug("InitializingLogging()")
    # ~ logging.debug("This is a debug message.")
    # ~ logging.info("This is an info message.")
    # ~ logging.warning("This is a warning message.")
    # ~ logging.error("This is an error message.")
    # ~ logging.critical("This is a critical message.")

InitializingLogging()

def BasicCmds(userInput):
	global conversationMode
	global inputMode
	global outputMode
	
	# Checking for input mode
	if (userInput.lower() == "input mode text"):
		inputMode = "text"
		return True
	
	elif (userInput.lower() == "input mode speech"):
		inputMode = "speech"
		return True

	# Checking for output mode
	elif (userInput.lower() == "output mode text"):
		outputMode = "text"
		return True
	
	elif (userInput.lower() == "output mode speech"):
		outputMode = "speech"
		return True

	# Checking for wake up call
	elif any(call in userInput.lower() for call in listWakeUpCalls):
		conversationMode = "wakeUp"
		return True
	
	# Checking for sleep call
	elif any(call in userInput.lower() for call in listSleepCalls):
		conversationMode = "sleep"
		return True

	else:
		print("## inputMode:", inputMode, ":outputMode:" , outputMode, ":conversationMode:" , conversationMode, "##")
		return False

def Input():	
	global inputMode
		
	## ## Input ## ##
	# Getting user input
	# userInput = "Hey there how its going on?" # sample 
	if(inputMode == "text"):
		userInput = input("userInput: ")	# Text 
	elif(inputMode == "speech"):
		userInput = STT.Main()			# Speech To Text
	else:
		print("Error: Invalid inputMode:", inputMode)
	
	# ~ print("userInput:",userInput)	
	logger.info(f"userInput: {userInput}")
	return userInput
	
def Processing(userInput):
	global conversationMode
	
	if(BasicCmds(userInput)):
		return
		
	
	# for debug only conversation mode only wake up
	# ~ conversationMode = "wakeUp"
	
		
	# ~ # Checking for sleep call
	# ~ if any(call in userInput.lower() for call in listSleepCalls):
		# ~ conversationMode = "sleep"
		
	# if(debug01): print("conversationMode:",conversationMode)
	
	if (conversationMode == "wakeUp"):
		# userInputToScriptInvocation
		
		# ~ terminalOutput = UITSI.Main(userInput)
		# ~ print(f"TerminalOutput: {terminalOutput}")
		
		# ~ if(terminalOutput is not None):
			# ~ # LLM User Responce generation
		# ~ else:
			# ~ # LLM General Question
		
		
		# define role to userInput
		# userInput = roleDefining + userInput			
		logger.info(f"userInputWithDefinedRole: {userInput}")
		
		# Getting responce from LLM model
		# llmResponce = LLM.Main(userInput)
		
		global threadId
		threadId += 1	
		agentResponce = Agent.Main(userInput, threadId)

		return agentResponce

def Output(assistantOutput):	
	global outputMode
	
	if(outputMode == "text"):
		logger.info(f"llmResponce: {agentResponce}")	# Text 
	elif(outputMode == "speech"):	
		TTS.Main(llmResponce) 			# Text to speech
	else:
		print("Error: Invalid outputMode:", outputMode)
			

def Main():
	
	userInput = Input()
	
	if (userInput is not None):

		if(debug01): print("input Not null")
		assistantOutput = Processing(userInput)

		if (assistantOutput is not None):
			Output(assistantOutput)
		
while(True):
	Main()
	
# ~ userInput = "Give me a youtube video link on valorant"
# ~ step 1 find youtube video link of valorant, step 2 run firefox cmd with that link
# ~ Do 1 step at a time. step 1 get 2 youtube video links of valorant game, step 2 draft a mail to my brother ved with these links
# ~ Do 1 step at a time. step 1 find top 3 music artist, step 2 get 2 youtube video links of each artist from the 3 artist, step 3 draft a mail to my brother ved with these links

