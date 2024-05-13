from datetime import datetime
from random import randint

from flask import Blueprint, render_template, url_for, flash, redirect, request
from pydantic import ValidationError


from src.database.models.messaging import SMSCompose, RecipientTypes, EmailCompose, SMSInbox

from src.authentication import login_required
from src.database.models.users import User


messaging_route = Blueprint('messaging', __name__)


@messaging_route.get('/admin/administrator/cloudflare')
@login_required
async def get_cloudflare(user: User):
    context = dict(user=user)
    return render_template('admin/managers/messaging/cloudflare.html', **context)


@messaging_route.get('/admin/administrator/messaging/topup')
@login_required
async def get_topup(user: User):
    context = dict(user=user)
    return render_template('admin/managers/messaging/topup.html', **context)


@messaging_route.get('/admin/administrator/messaging/settings')
@login_required
async def get_admin(user: User):
    context = dict(user=user)
    return render_template('admin/managers/messaging/settings.html', **context)


@messaging_route.post('/admin/administrator/messaging/sms-settings')
@login_required
async def update_sms_settings(user: User):
    """

    :param user:
    :return:
    """
    flash(message="Successfully updated SMS Settings", category="success")
    return redirect(url_for('messaging.get_admin'))


@messaging_route.post('/admin/administrator/messaging/whatsapp-settings')
@login_required
async def update_whatsapp_settings(user: User):
    """

    :param user:
    :return:
    """

    flash(message="Successfully updated SMS Settings", category="success")
    return redirect(url_for('messaging.get_admin'))


def create_fake_cell(length: int = 10) -> str:
    """
    Generate a fake cell number.

    :param length: Length of the cell number (default is 10)
    :return: Fake cell number
    """
    return ''.join([str(randint(0, 9)) for _ in range(length)])


def create_fake_sms_data(to_branch: str, message: str, count: int = 10) -> list[SMSInbox]:
    """
    Generate fake SMSInbox data for testing.

    :param to_branch: Branch ID
    :param message: Message content
    :param count: Number of SMSInbox instances to generate (default is 10)
    :return: List of SMSInbox instances
    """
    sms_data = []
    for _ in range(count):
        sms_data.append(SMSInbox(
            from_cell=create_fake_cell(),
            to_branch=to_branch,
            message=message,
            is_read=bool(randint(0, 1)),  # Randomly set is_read to True or False
        ))
    return sms_data


@messaging_route.get('/admin/administrator/messaging/inbox')
@login_required
async def get_inbox(user: User):
    sms_inbox = await messaging_controller.get_sms_inbox(branch_id=user.branch_id)
    if not sms_inbox:
        # Generate at least ten fake SMS records for testing
        sms_inbox = create_fake_sms_data(to_branch="branch_id", message="Test message", count=10)

    context = dict(user=user, sms_inbox=sms_inbox)
    return render_template('admin/managers/messaging/inbox.html', **context)


@messaging_route.get('/admin/administrator/messaging/read-sms')
@login_required
async def read_sms_message(user: User, message_id: str):
    """

    :param user:
    :param message_id:
    :return:
    """
    context = dict(user=user)
    sms_inbox: list[SMSInbox] = await messaging_controller.get_sms_inbox(branch_id=user.branch_id)
    for sms in sms_inbox:
        if sms.message_id == message_id:
            context.update(sms=sms)
            return render_template("admin/managers/messaging/read_sms.html", **context)


@messaging_route.get('/admin/administrator/messaging/sent')
@login_required
async def get_sent(user: User):
    context = dict(user=user)
    return render_template('admin/managers/messaging/sent.html', **context)


@messaging_route.get('/admin/administrator/messaging/compose')
@login_required
async def get_compose(user: User):
    recipient_list: list[str] = RecipientTypes.get_fields()
    company_branches = await company_controller.get_company_branches(company_id=user.company_id)
    context = dict(user=user, company_branches=company_branches, recipient_list=recipient_list)
    return render_template('admin/managers/messaging/compose.html', **context)


@messaging_route.get('/admin/employees/messaging/inbox')
@login_required
async def get_employee_inbox(user: User):
    context = dict(user=user)
    return render_template('admin/managers/messaging/inbox.html', **context)


@messaging_route.get('/admin/employees/messaging/sent')
@login_required
async def get_employee_sent(user: User):
    context = dict(user=user)
    return render_template('admin/managers/messaging/sent.html', **context)


@messaging_route.get('/admin/employees/messaging/compose')
@login_required
async def get_employee_compose(user: User):
    recipient_list: list[str] = RecipientTypes.get_fields()
    # Removing Sending SMS to Employees
    # recipient_list.pop(str(RecipientTypes.EMPLOYEES.value))
    company_branches = await company_controller.get_company_branches(company_id=user.company_id)
    context = dict(user=user, company_branches=company_branches, recipient_list=recipient_list)
    return render_template('admin/managers/messaging/compose.html', **context)


#################################################################################################

async def send_sms_to_branch_policy_holders(composed_sms: SMSCompose):
    """
        # TODO investigate how to run this as a separate thread and just respond to user separately
        will send sms to branch policy holders
    :param composed_sms:
    :return:
    """
    # Obtain Policy Holders in Branch
    branch_clients = await company_controller.get_branch_policy_holders(branch_id=composed_sms.to_branch)
    # Use The Contact ID's to obtain the Contact Records from database
    contact_list = [await company_controller.get_contact(contact_id=contact_id)
                    for contact_id in [client.contact_id for client in branch_clients if client.contact_id]]
    # Obtain Cell Number from each Contact Record where there is a Cell Number
    recipient_list = [contact.cell for contact in contact_list if contact.cell]
    # For Every Cell Number Send a Message - this will insert the message into the out message Queue
    for cell in recipient_list:
        composed_sms.to_cell = cell
        composed_sms.date_time_composed = date_time()
        is_sent = await messaging_controller.send_sms(composed_sms=composed_sms)
        print(f"is SMS Sent : {is_sent}")
        #TODO - we can start updating the local database showing the sms was sent
        # on the Queue after its delivered we can update the message delivered on the local database


async def send_sms_to_branch_employees(composed_sms: SMSCompose):
    """
        # TODO investigate how to run this as a separate thread and just respond to user separately

        will send sms to branch_employees
    :param composed_sms:
    :return:
    """
    branch_employees = await company_controller.get_branch_employees(branch_id=composed_sms.to_branch)
    employees_contact_numbers = []
    for employee in branch_employees:
        # Check if the employee has a contact number
        if employee.contact_number:
            employees_contact_numbers.append(employee.contact_number)
        # If not, but has a contact ID, get the contact's cell number
        elif employee.contact_id:
            # Fetch contact details
            contact = await company_controller.get_contact(contact_id=employee.contact_id)
            # Extract cell numbers from contacts
            employees_contact_numbers.append(contact.cell)
    # Send SMS to each employee's contact number
    for cell in employees_contact_numbers:
        composed_sms.to_cell = cell
        composed_sms.date_time_composed = date_time()
        is_sent = await messaging_controller.send_sms(composed_sms=composed_sms)
        #TODO - we can start updating the local database showing the sms was sent
        # on the Queue after its delivered we can update the message delivered on the local database


async def send_sms_to_branch_lapsed_policy_holders(composed_sms: SMSCompose):
    """
        # TODO investigate how to run this as a separate thread and just respond to user separately

    :param composed_sms:
    :return:
    """
    lapsed_policy_holders: list[
        ClientPersonalInformation] = await company_controller.get_branch_policy_holders_with_lapsed_policies(
        branch_id=composed_sms.to_branch)
    policy_holder_contact_numbers = []

    for policy_holder in lapsed_policy_holders:
        if policy_holder.contact_id:
            # Fetch contact details
            contact = await company_controller.get_contact(contact_id=policy_holder.contact_id)
            # Extract cell numbers from contacts
            policy_holder_contact_numbers.append(contact.cell)

    for cell in policy_holder_contact_numbers:
        composed_sms.to_cell = cell
        composed_sms.date_time_composed = date_time()
        is_sent = await messaging_controller.send_sms(composed_sms=composed_sms)


def date_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def create_response(user: User):
    if user.is_employee and not user.is_company_admin:
        return redirect(url_for('messaging.get_employee_compose'))

    # This will return company admin compose
    return redirect(url_for('messaging.get_compose'))


@messaging_route.post('/admin/messaging/sms/compose')
@login_required
async def send_composed_sms_message(user: User):
    """
        processes both managers and employees compose message
        will redirect to the compose of employee or manager upon completion
    :param user:
    :return:
    """
    try:
        composed_sms = SMSCompose(**request.form)

    except ValidationError as e:
        print(str(e))
        flash(message="Error sending SMS please ensure to fill in the form", category="danger")
        return await create_response(user=user)

    if composed_sms.recipient_type.casefold() == RecipientTypes.EMPLOYEES.value.casefold():
        # Could Be interesting to just send this to a separate thread
        await send_sms_to_branch_employees(composed_sms=composed_sms)

    elif composed_sms.recipient_type.casefold() == RecipientTypes.CLIENTS.value.casefold():
        await send_sms_to_branch_policy_holders(composed_sms=composed_sms)

    elif composed_sms.recipient_type.casefold() == RecipientTypes.LAPSED_POLICY.value.casefold():
        # Get policyholders with Lapsed Policies
        await send_sms_to_branch_lapsed_policy_holders(composed_sms)

    flash(message="Message Successfully sent", category="success")
    return await create_response(user=user)


@messaging_route.post('/admin/messaging/whatsapp/compose')
@login_required
async def send_whatsapp_message(user: User):
    """

    :param user:
    :return:
    """
    flash(message="Successfully sent whatsapp message", category="success")
    return await create_response(user=user)


# Sending Email Messages Routes
async def send_emails(composed_email: EmailCompose,
                      persons_list: list[ClientPersonalInformation | EmployeeDetails]) -> bool:
    for person in persons_list:
        if person.contact_id:
            contact = await company_controller.get_contact(contact_id=person.contact_id)
            if contact.email:
                composed_email.to_email = contact.email
                is_sent = await messaging_controller.send_email(composed_email)

    return True


@messaging_route.post('/admin/messaging/email/compose')
@login_required
async def send_email_message(user: User):
    """

    :param user:
    :return:
    """
    try:
        composed_email = EmailCompose(**request.form)

    except ValidationError as e:
        print(str(e))
        flash(message="Error sending SMS please ensure to fill in the form", category="danger")
        return await create_response(user=user)

    if composed_email.recipient_type == RecipientTypes.EMPLOYEES.value:

        branch_employees: list[EmployeeDetails] = await company_controller.get_branch_employees(
            branch_id=composed_email.to_branch)
        await send_emails(composed_email=composed_email, persons_list=branch_employees)

    elif composed_email.recipient_type == RecipientTypes.CLIENTS.value:

        policy_holders: list[ClientPersonalInformation] = await company_controller.get_branch_policy_holders(
            branch_id=composed_email.to_branch)
        await send_emails(composed_email=composed_email, persons_list=policy_holders)

    elif composed_email.recipient_type == RecipientTypes.LAPSED_POLICY.value:
        # obtaining policyholders with lapsed policies
        policy_holders = await company_controller.get_branch_policy_holders_with_lapsed_policies(
            branch_id=composed_email.to_branch)
        await send_emails(composed_email=composed_email, persons_list=policy_holders)
    else:
        flash(message="Could Not Send Email Message", category="success")
        return await create_response(user=user)

    flash(message="Successfully sent email message", category="success")
    return await create_response(user=user)
