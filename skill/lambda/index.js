const Alexa = require('ask-sdk-core');
const Util = require('./util');
const Common = require('./common');

// The namespace of the custom directive to be sent by this skill
const NAMESPACE = 'Custom.Mindstorms.Gadget';

// The name of the custom directive to be sent this skill
const NAME_CONTROL = 'control';

const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
    },
    handle: async function(handlerInput) {

        let request = handlerInput.requestEnvelope;
        let { apiEndpoint, apiAccessToken } = request.context.System;
        let apiResponse = await Util.getConnectedEndpoints(apiEndpoint, apiAccessToken);
        if ((apiResponse.endpoints || []).length === 0) {
            return handlerInput.responseBuilder
            .speak(`I couldn't find an EV3 Brick connected to this Echo device. Please check to make sure your EV3 Brick is connected, and try again.`)
            .getResponse();
        }

        // Store the gadget endpointId to be used in this skill session
        let endpointId = apiResponse.endpoints[0].endpointId || [];
        Util.putSessionAttribute(handlerInput, 'endpointId', endpointId);

        return handlerInput.responseBuilder
            .speak("Hi, I'm ALBERT. What would you like to do?")
            .reprompt("Try saying, 'Make a plate'")
            .getResponse();
    }
};

// Construct and send a custom directive to ALBERT to make a plate
const MakePlateIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'MakePlateIntent';
    },
    handle: function (handlerInput) {
        const request = handlerInput.requestEnvelope;

        // Get data from session attribute
        const attributesManager = handlerInput.attributesManager;
        const endpointId = attributesManager.getSessionAttributes().endpointId || [];

        // Construct the directive
        const directive = Util.build(endpointId, NAMESPACE, NAME_CONTROL,
            {
                type: 'make_plate'
            });

        const speechOutput = "Creating plate from sample";

        return handlerInput.responseBuilder
            .speak(speechOutput)
            // .reprompt("awaiting command")
            .addDirective({
                'type': 'CustomInterfaceController.StartEventHandler',
                'token': endpointId,
                'expiration': {
                    'durationInMilliseconds': 90000,
                },
                'eventFilter': {
                    'filterExpression':{
                        'and': [
                            {'==': [{'var': 'header.namespace'}, 'Custom.Mindstorms.Gadget']},
                        ]
                    },
                    'filterMatchAction': 'SEND_AND_TERMINATE'
                }
            })
            .addDirective(directive)
            .getResponse();
    }
};

const CheckPlateIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'CheckPlateIntent';
    },
    handle: function (handlerInput) {
        const request = handlerInput.requestEnvelope;

        // Get data from session attribute
        const attributesManager = handlerInput.attributesManager;
        const endpointId = attributesManager.getSessionAttributes().endpointId || [];

        const plateNumber = Alexa.getSlotValue(request, 'PlateID');
        
        // Construct the directive
        const directive = Util.build(endpointId, NAMESPACE, NAME_CONTROL,
            {
                type: 'check_plate',
                plate_number: plateNumber
            });

        const speechOutput = `Checking plate ${plateNumber}`;

        return handlerInput.responseBuilder
            .speak(speechOutput)
            .addDirective({
                'type': 'CustomInterfaceController.StartEventHandler',
                'token': endpointId,
                'expiration': {
                    'durationInMilliseconds': 90000,
                },
                'eventFilter': {
                    'filterExpression':{
                        'and': [
                            {'==': [{'var': 'header.namespace'}, 'Custom.Mindstorms.Gadget']},
                        ]
                    },
                    'filterMatchAction': 'SEND_AND_TERMINATE'
                }
            })
            .addDirective(directive)
            .getResponse();
    }
};

const GadgetEventHandler = {
    canHandle(handlerInput) {
      return handlerInput.requestEnvelope.request.type === 'CustomInterfaceController.EventsReceived';
    },
    handle(handlerInput) {
        // Handles status acknowledgement from the robot.
        console.log("== Received custom event ==");
        
        let { request } = handlerInput.requestEnvelope;
        let payload = request.events[0].payload;
        let namespace = request.events[0].header.namespace;
        let name = request.events[0].header.name;
        
        console.log(namespace);
        console.log(name);
        console.log(payload);
        
        if (name === 'plate_finished') {
          return handlerInput.responseBuilder
            .speak(`Plate ${payload.plate_number} was completed and placed in storage. You can retrieve it by asking me to check plate ${payload.plate_number}.`)
            .getResponse();
        }
        else if (name === 'plate_status') {
            if (payload.plate_number > 0) {
                return handlerInput.responseBuilder
                    .speak(`Plate ${payload.plate_number} has reflectivity of ${payload.reflectivity}`)
                    .getResponse();
            } else {
                return handlerInput.responseBuilder
                    .speak(`That plate does not exist. Please use an existing plate number`)
                    .withShouldEndSession(false)
                    .getResponse();
            }

        }
    }
}


// The SkillBuilder acts as the entry point for your skill, routing all request and response
// payloads to the handlers above. Make sure any new handlers or interceptors you've
// defined are included below. The order matters - they're processed top to bottom.
exports.handler = Alexa.SkillBuilders.custom()
    .addRequestHandlers(
        LaunchRequestHandler,
        MakePlateIntentHandler,
        CheckPlateIntentHandler,
        GadgetEventHandler,
        Common.HelpIntentHandler,
        Common.CancelAndStopIntentHandler,
        Common.SessionEndedRequestHandler,
        Common.IntentReflectorHandler, // make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
    )
    .addRequestInterceptors(Common.RequestInterceptor)
    .addErrorHandlers(
        Common.ErrorHandler,
    )
    .lambda();