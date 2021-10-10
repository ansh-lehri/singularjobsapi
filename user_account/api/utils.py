from django.core.mail import EmailMessage


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        #EmailThread(email).start()
        print("SENDING MAIL  &&&&&&&&&&&&7777777777777777777777777777777777777777777777777777777777777")
        email.send()
        
        
        
'''        
send_to_users = ["av110976@gmail.com","yashikatyagi2000@gmail.com","vsonu024@gmail.com","neharai101098@gmail.com","asthasachan02@gmail.com","deependra2199@gmail.com","katiyarvishal0011@gmail.com","shubhendras21@gmail.com","anshlehri0599@gmail.com"]

for user in ['anshlehrigola@gmail.com']:
    
    email_body = 'Hello '+user + "\n\n"+'We would like to apologize for the inconvenience caused while creating profile earlier today because of LinkedIn profile. Also, during maintenance yesterday night, we came around a bug, because of your skills were not getting created as they were supposed to which lead to either no or inappropriate recommendations.\nWe have updated all your skills and have uodated your job lists to best case possible.\n\n Once again, we would like to express our most sincere appologies for the inconvenience caused.'
    email_data = {'email_body': email_body, 'to_email': user,'email_subject': 'Applogies for inconvenience while using the site.'}
    
    Util.send_email(email_data)
    print("mail sent successfully to: ")
    print(user)
    
'''