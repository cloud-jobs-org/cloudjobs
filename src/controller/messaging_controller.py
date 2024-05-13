import asyncio
import time
from datetime import datetime

from flask import Flask

from src.controller import Controllers
from src.database.models.messaging import SMSInbox, EmailCompose, SMSCompose
from src.database.sql.messaging import SMSInboxORM, SMSComposeORM


def date_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class EmailService:

    def __init__(self):
        pass

    async def send_email(self, recipient: str, subject: str, body: str):
        # Code to send email via email service API
        print(f"Sending email to {recipient} with subject: {subject} and body: {body}")
        # Simulate sending email asynchronously
        # await asyncio.sleep(2)
        print("Email sent successfully")

    async def receive_email(self, sender: str, subject: str, body: str):
        # Code to receive email from email service API
        print(f"Received email from {sender} with subject: {subject} and body: {body}")


class SMSService(Controllers):
    def __init__(self):
        super().__init__()
        self.sms_service_api = None

        # Inbox Messages
        self.inbox_queue: dict[str: list[SMSInbox]] = {}

        # Sent Messages
        self.sent_messages_queue: dict[str: list[SMSCompose]] = {}

        # a dict of reference or message_id from the api provider matched with the branch_id in the application
        self.sent_references: dict[str: list[str]] = {}

    def init_app(self, app: Flask):

        super().init_app(app=app)
        # TODO Initialize the SMS API

    async def check_incoming_sms_api(self) -> list[SMSInbox]:
        """
            for whichever SMS API i am using map the message to SMS Inbox and return
        :return:
        """
        # TODO Complete the API Implementation to fetch incoming SMS Messages Here
        if self.sms_service_api:
            # Use the References to match incoming messages to previously sent messages in order to identify responses
            for branch_id, references in self.sent_references:
                for message_sent_reference in references:
                    # save each reference used when constructing the inboxMessage
                    pass

        return []

    async def send_sms(self, composed_sms: SMSCompose):
        """
            Sending the SMS Messages to the Outside World this will feed the Sent Box
        :param composed_sms:
        :return:
        """
        # Code to send SMS via SMS service API
        print(f"Sending SMS to {composed_sms.to_cell} with message: {composed_sms.message}")

        if self.sms_service_api:
            # API is initialized do send message
            # sent reference from the api call when sending the message
            sent_reference = ""
            composed_sms.reference = sent_reference
            sent_references = self.sent_references.get(composed_sms.to_branch, [])
            sent_references.append(sent_reference)
            self.sent_references[composed_sms.to_branch] = sent_references

        composed_sms.date_time_sent = date_time()

        # The Sent Messages will read from this Queue
        composed_messages: list[SMSCompose] = self.sent_messages_queue.get(composed_sms.to_branch, [])
        composed_messages.append(composed_sms)

        self.sent_messages_queue[composed_sms.to_branch] = composed_messages

        # Saving the Sent Messages to the Database
        with self.get_session() as session:
            session.add(SMSComposeORM(**composed_sms.dict()))
            session.commit()

        # Simulate sending SMS asynchronously
        # await asyncio.sleep(1)
        print("SMS sent successfully")

    async def retrieve_sms_responses_service(self):
        """
            Fetching the SMS Messages which are sent to this company or as responses
            this will feed the inbox
        :return:
        """
        # Code to receive SMS from SMS service API
        if self.sms_service_api:

            # Message Retrieved from API
            incoming__messages: list[SMSInbox] = await self.check_incoming_sms_api()

            for message in incoming__messages:
                inbox_messages: list[SMSInbox] = self.inbox_queue.get(message.to_branch, [])

                sent_references: list[str] = self.sent_references[message.to_branch]
                sent_references.remove(message.parent_reference)
                self.sent_references[message.to_branch] = sent_references
                original_message = await self.mark_message_as_responded(reference=message.parent_reference)
                message.previous_history += f"""
                -------------------------------------------------------------------------------------------------------
                date_response : {date_time()}
                
                original_message:

                {original_message.message}
                """

                inbox_messages.append(message)
                self.inbox_queue[message.to_branch] = inbox_messages

                # Storing the Message to Database
                await self.store_sms_to_database_inbox(sms_message=message)

    async def store_sms_to_database_inbox(self, sms_message: SMSInbox) -> SMSInbox:
        with self.get_session() as session:
            session.add(SMSInboxORM(**sms_message.dict()))
            session.commit()
            return sms_message

    async def get_inbox_messages_from_database(self, branch_id: str) -> list[SMSInbox]:
        with self.get_session() as session:
            inbox_list = session.query(SMSInboxORM).filter_by(to_branch=branch_id).all()
            return [SMSInbox(**inbox.to_dict()) for inbox in inbox_list if isinstance(inbox, SMSInboxORM)]

    async def get_sent_box_messages_from_database(self, branch_id: str) -> list[SMSCompose]:
        with self.get_session() as session:
            compose_orm_list = session.query(SMSComposeORM).filter_by(branch_id=branch_id).all()
            return [SMSCompose(**sms.to_dict()) for sms in compose_orm_list if isinstance(sms, SMSComposeORM)]

    async def mark_message_as_responded(self, reference: str) -> SMSCompose | None:
        with self.get_session() as session:
            message_orm = session.query(SMSComposeORM).filter_by(reference=reference).first()
            if isinstance(message_orm, SMSComposeORM):
                sms_compose = SMSCompose(**message_orm.to_dict())
                message_orm.client_responded = True
                message_orm.is_delivered = True

                sms_compose.is_delivered = True
                sms_compose.client_responded = True
                session.commit()

                return sms_compose
            return None


class WhatsAppService:
    def __init__(self):
        pass

    async def send_whatsapp_message(self, recipient: str, message: str):
        # Code to send WhatsApp message via WhatsApp service API
        print(f"Sending WhatsApp message to {recipient} with message: {message}")
        # Simulate sending WhatsApp message asynchronously
        # await asyncio.sleep(3)
        print("WhatsApp message sent successfully")

    async def receive_whatsapp_message(self, sender: str, message: str):
        # Code to receive WhatsApp message from WhatsApp service API
        print(f"Received WhatsApp message from {sender} with message: {message}")


class MessagingController(Controllers):
    def __init__(self):

        super().__init__()
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.whatsapp_service = WhatsAppService()

        self.email_queue = asyncio.Queue()
        self.sms_queue = asyncio.Queue()
        self.whatsapp_queue = asyncio.Queue()

        self.loop = asyncio.get_event_loop()

    # ------------------------------------------------------------------------------------------------------------------
    #----  Routes ---

    async def get_sms_inbox(self, branch_id: str) -> list[SMSInbox]:

        return self.sms_service.inbox_queue.get(branch_id, [])

    def init_app(self, app: Flask):
        super().init_app(app=app)
        self.loop.create_task(self.start_app())
        print("Loop Initialized")

    async def send_email(self, email: EmailCompose):
        """
            TODO When Actually sending the Email Consider
        :param email:
        :return:
        """
        await self.email_queue.put(email)

    async def send_sms(self, composed_sms: SMSCompose):
        await self.sms_queue.put(composed_sms)
        print(f"composed SMS in Queue : {composed_sms}")

        return True

    async def send_whatsapp_message(self, recipient: str, message: str):
        await self.whatsapp_queue.put((recipient, message))
        return True

    async def process_email_queue(self):
        print("Processing Email")
        if self.email_queue.empty():
            print("No Email Messages")
            return

        recipient, subject, body = await self.email_queue.get()
        await self.email_service.send_email(recipient, subject, body)
        self.email_queue.task_done()

    async def process_sms_queue(self):

        print("processing sms outgoing message queues")
        if self.sms_queue.empty():
            print("no sms messages to send")
            return

        composed_sms: SMSCompose = await self.sms_queue.get()
        response = await self.sms_service.send_sms(composed_sms=composed_sms)
        # response will carry a response message from the api provider at this point
        # TO
        self.sms_queue.task_done()

    async def process_whatsapp_queue(self):

        print("processing whatsapp out going message queues")
        if self.whatsapp_queue.empty():
            print("No WhatsAPP Messages")
            return

        recipient, message = await self.whatsapp_queue.get()
        await self.whatsapp_service.send_whatsapp_message(recipient, message)
        self.whatsapp_queue.task_done()

    async def start_app(self):
        print("Thread Started-------------------------------------------------")
        i = 0
        time_started = time.time()
        timer_multiplier = 10

        async def standard_time() -> str:
            hours = int(time_elapsed // 3600)
            minutes = int((time_elapsed % 3600) // 60)
            seconds = int(time_elapsed % 60)
            return f"{hours} hours, {minutes} minutes, {seconds}"

        while True:
            # Out Going Message Queues
            i += 1
            await self.process_email_queue()
            await self.process_sms_queue()
            await self.process_whatsapp_queue()

            # Incoming Message Queues
            print("Started Processing Incoming Messages")
            await self.sms_service.retrieve_sms_responses_service()

            # This Means the loop will run every 5 minutes
            await asyncio.sleep(60 * timer_multiplier)

            time_elapsed = time.time() - time_started
            display_time = await standard_time()
            print(f"Counter {str(i)}--------------------------- Time Elapsed : {display_time}")
