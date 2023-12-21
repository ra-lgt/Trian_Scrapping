from jinja2 import Environment,FileSystemLoader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from premailer import transform



class SendEmail:
    def send_available_details(self,data,source,destination):
        data["source"]=[source]*(len(data["train_service"]))
        data["destination"]=[destination]*(len(data["train_service"]))
        
        env = Environment(loader=FileSystemLoader('./templates'))
        template_vars = {'data':data,'count':len(data["train_service"])}
        template = env.get_template('email.html')
        output_html = template.render(template_vars)
        output_html_inline = transform(output_html)
        message=MIMEMultipart('alternative')
        message['subject']="Available Train From Bot"
        message["from"]="skillstormofficial01@gmail.com"
        message["to"]="raviajay9344@gmail.com"

        html_mail=MIMEText(output_html_inline,'html')
        message.attach(html_mail)
        server=smtplib.SMTP_SSL("smtp.gmail.com",465)
        server.login("skillstormofficial01@gmail.com","wgrrwnsolhyfiyrg")
        server.sendmail("skillstormofficial01@gmail.com","raviajay9344@gmail.com",message.as_string())