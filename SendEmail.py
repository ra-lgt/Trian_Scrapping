from jinja2 import Environment,FileSystemLoader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib



class SendEmail:
    def send_available_details(self,data):
        
        env = Environment(loader=FileSystemLoader('./templates'))
        template_vars = {'username': username, 'email': email,'message':messages}
        template = env.get_template('email.html')
        output_html = template.render(template_vars)
        # message=MIMEMultipart('alternative')
        # message['subject']="OTP Verification: Your One-Time Password"
        # message["from"]="skillstormofficial01@gmail.com"
        # message["to"]=email

        # html_mail=MIMEText(output_html,'html')
        # message.attach(html_mail)
        # server=smtplib.SMTP_SSL("smtp.gmail.com",465)
        # server.login("skillstormofficial01@gmail.com","wgrrwnsolhyfiyrg")
        # server.sendmail("skillstormofficial01@gmail.com",email,message.as_string())