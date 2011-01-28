# TwiML returned to twilio
# See: http://www.twilio.com/docs/api/2010-04-01/twiml/


WAKEUP_CALL = """<Response>
    <Gather action="%(domain)s/twilio/question/callback" method="GET" timeout="5">
        <Say>Spell the word %(keyword)s.</Say>
        <Say>%(sentence)s</Say>
        <Say>Spell %(keyword)s.</Say>
        <Say>If you wish to unsubscribe, please spell STOP</Say>
    </Gather>
</Response>"""


VALIDATION_CALL = """<Response>
    <Gather action="%(domain)s/twilio/validation/callback?user_key=%(user_key)s" method="POST" timeout="5">
        <Say>Please confirm your phone number by pressing 1, followed by the pound sign</Say>
    </Gather>
</Response>"""


YOU_SPELLED_THE_WALRUS = """<Response>
    <Say>You are correct</Say>
</Response>
"""

THATS_NOT_HOW_YOU_SPELL_WALRUS = """<Response>
    <Say>FAIL!!! That's not how you spell %(keyword)s</Say>
    <Gather action="%(domain)s/twilio/question/callback" method="GET" timeout="5">
        <Say>Spell the word %(keyword)s.</Say>
    </Gather>
</Response>
"""

NUMBER_WAS_VALIDATED = """<Response>
    <Say>Thank you, your registration is now complete. See you in the morning!</Say>
</Response>
"""

NUMBER_WAS_NOT_VALIDATED = """<Response>
    <Gather action="%(domain)s/twilio/validation/callback?user_key=%(user_key)s" method="POST" timeout="5">
        <Say>Something went wrong. Please confirm your phone number by pressing 1, followed by the pound sign</Say>
    </Gather>
</Response>
"""

UNSUBSCRIBE = """<Response>
    <Say>Thank you, you have been removed from our service. Come back any time!</Say>
</Response>
"""