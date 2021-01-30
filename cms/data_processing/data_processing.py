from collections import Iterator

import dialogflow
from google.cloud.dialogflow_v2 import QueryInput, DetectIntentResponse, TextInput
from google.protobuf.struct_pb2 import Struct
from os import environ as env

from cms.data_processing.constants import ProcessedAttribute


class DialogflowClient(dialogflow.SessionsClient):

    def __init__(self, transport=None, channel=None, credentials=None, client_config=None, client_info=None, client_options=None):
        super().__init__(transport, channel, credentials, client_config, client_info, client_options)
        self.session = self.session_path(env['DIALOGFLOW_PROJECT_ID'], env['SESSION_ID'])
        self.language_code = env['DIALOGFLOW_LANGUAGE_CODE']


class Processor(DialogflowClient):

    def unit_and_value_from_text(self, text: str) -> Iterator[ProcessedAttribute]:
        """
        Creates a processed attribute object from raw text.
        :param text: raw text data
        :return: iterator of ProcessedAttribute objects
        """
        text_input: TextInput = TextInput(text=text, language_code=self.language_code)
        query_input: QueryInput = QueryInput(text=text_input)
        response: DetectIntentResponse = self.detect_intent(session=self.session, query_input=query_input)
        if response.query_result.parameters:
            for attribute_type, struct in response.query_result.parameters.fields.items():
                struct: Struct
                yield ProcessedAttribute(
                    attribute_type=attribute_type,
                    amount=struct.fields['amount'].number_value,
                    unit=struct.fields['unit'].string_value
                )
