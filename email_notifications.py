import sendgrid
import os

def sendemail(to, subject, sender, content):
    if not os.environ.get('SENDGRID_API_KEY'):
        sg = sendgrid.SendGridAPIClient(apikey='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')
    else:
        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

    data = {
      "personalizations": [
        {
          "to": [
            {
              "email": to
            }
          ],
          "subject": subject
        }
      ],
      "from": {
        "email": sender
      },
      "content": [
        {
          "type": "text/plain",
          "value": content
        }
      ]
    }
    response = sg.client.mail.send.post(request_body=data)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return print('Email sent!')
