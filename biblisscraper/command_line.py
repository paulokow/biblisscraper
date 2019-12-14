from datetime import datetime, timedelta, date
from biblisscraper.scraper import scrap_biblis_book_lents
import argparse
import json
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


def main():
    parser = argparse.ArgumentParser(description='Biblis account scanner')
    parser.add_argument("-c", "--config", action="store", type=argparse.FileType("r"), default=".settings", help="Config file (JSON)")

    args = parser.parse_args()

    with args.config as config:
        configobj = json.load(config)
        accounts = configobj["accounts"]

    allitems = [inneritem
                for outeritem
                in [scrap_biblis_book_lents(account["name"], account["user"], account["password"])
                        for account
                        in accounts]
                for inneritem in outeritem]
    shortitems = [x for x in allitems
                  if x["date"] <= date.today() + timedelta(days=configobj.get("notify_cut_off", 7))]

    if len(shortitems) > 0:
        #print(shortitems)
        emailcontent = build_email(shortitems, configobj.get("email_template", None))
        #print(emailcontent)
        for email in configobj.get("notify", []):
            send_email(configobj["email_settings"], emailcontent, email)


def build_email(items, template_file):
    from jinja2 import Template

    if template_file is not None:
        with open(template_file, mode="r") as f:
            template = f.read()
    else:
        template = pkg_resources.read_text('biblisscraper', 'mail_template.txt')

    template = Template(template)
    output = template.render(items=items, today=date.today())
    return output

def send_email(settings, content, target):
    print("Sending Email to: {}...".format(target))
    # import the smtplib module. It should be included in Python by default
    import smtplib
    # set up the SMTP server
    s = smtplib.SMTP(host=settings["MY_SMTP_HOST"], port=settings["MY_SMTP_PORT"])
    s.starttls()
    s.login(settings["MY_ADDRESS"], settings["MY_PASSWORD"])

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart()       # create a message


    # setup the parameters of the message
    msg['From'] = "{} <{}>".format(settings["MY_ADDRESS_NAME"], settings["MY_ADDRESS"])
    msg['To'] = target
    msg['Subject'] = "Items to return"

    # add in the message body
    msg.attach(MIMEText(content, 'plain'))

    # send the message via the server set up earlier.
    s.send_message(msg)

    print("...Done!")

if __name__ == '__main__':
    main()
