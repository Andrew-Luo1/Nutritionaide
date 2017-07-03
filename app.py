from __future__ import print_function
import json
from nutritionix import Nutritionix

def build_speechlet_response(output, should_end_session):
	return {
		'outputSpeech': {
			'type': 'PlainText',
			'text': output
		},
		'shouldEndSession': should_end_session
	}


def build_response(session_attributes, speechlet_response):
	return {
		'version': '1.0',
		'sessionAttributes': session_attributes,
		'response': speechlet_response
	}


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
	session_attributes = {}
	card_title = "Welcome"
	speech_output = "Welcome to Nutrition Aid. Ask me for the nutrition information of a fruit, vegetable, or any popular American food."
	reprompt_text = ""
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session))

def get_help_response():
	session_attributes = {}
	card_title = "Welcome"
	speech_output = "Ask me about the name of any food. This can be a vegetable, fruit, or even something like pizza! "
	reprompt_text = ""
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session))

def handle_session_end_request():
	card_title = "Session Ended"
	speech_output = "Understood. "
	should_end_session = True
	return build_response({}, build_speechlet_response(speech_output, should_end_session))



def say_good_bye(intent, session):
	session_attributes = {}
	reprompt_text = None
	card_title = "Session Ended"
	speech_output = "Be healthy!"
	should_end_session = True
	return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session))


def get_nutri_info_intent(intent, session):
	session_attributes = {}
	reprompt_text = None
	foodName = intent['slots']['foodName']['value']

	speech_output = nutritioninfo(foodName)
	should_end_session = True
	return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session))

def nutritioninfo(theFood):
    
    nix = Nutritionix(app_id="869a3aa9", api_key="d478a1d292a3a5e7a36bf3bfe7376fa3")
    
    foodName = theFood
    food = nix.search().nxql(
     
        limit= 0,   
        filters={
        },
        fields=["item_name", "nf_calories", "nf_sodium", "nf_dietary_fiber","nf_protein", "nf_saturated_fat", "nf_sugars': 9", "nf_total_fat"],
        query=foodName
        
    ).json()

    
    firstResult = food["hits"][0]
        
    f1 = firstResult["fields"]
    
    str_resp = ""
    
    for item_tuple in f1.items():
        str_resp += item_tuple[0] + ": " + str(item_tuple[1]) + ". "
    
    str_resp = str_resp.replace('nf_', '')
    str_resp = str_resp.replace('item_name:', 'The item that I will describe using standard units is:')
    str_resp = str_resp.replace('_', ' ')
    return str_resp

# --------------- Specific Events ------------------

def on_intent(intent_request, session):
	print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])
	intent = intent_request['intent']
	intent_name = intent_request['intent']['name']
	if intent_name == "GetNutriInfoIntent":
		return get_nutri_info_intent(intent, session)
	elif intent_name == "GoodByeIntent":
		return say_good_bye(intent, session)
	elif intent_name == "AMAZON.HelpIntent":
		return get_help_response()
	elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		return handle_session_end_request()
	else:
		raise ValueError("Invalid intent")

# --------------- Generic Events ------------------

def on_session_started(session_started_request, session):
	print("on_session_started requestId=" + session_started_request['requestId']+ ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
	print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
	return get_welcome_response()
	
def on_session_ended(session_ended_request, session):
	print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
	print("event.session.application.applicationId=" + event['session']['application']['applicationId'])
	if event['session']['new']:
		on_session_started({'requestId': event['request']['requestId']}, event['session'])
	if event['request']['type'] == "LaunchRequest":
		return on_launch(event['request'], event['session'])
	elif event['request']['type'] == "IntentRequest":
		return on_intent(event['request'], event['session'])
	elif event['request']['type'] == "SessionEndedRequest":
		return on_session_ended(event['request'], event['session'])