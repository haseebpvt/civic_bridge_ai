from twilio.rest import Client

client = Client(
    "AC03aa6a3de06a799dc0c5bd2fba664184",
    "972a5887bf945c2b00147b7fd69daeda",
)

from_number = "whatsapp:+14155238886"
to_number = "whatsapp:+919526866889"

client.messages.create(
    body="Hello there! How are you doing?",
    to=to_number,
    from_=from_number,
)
