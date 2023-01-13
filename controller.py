from spamemail import spamChecker
from flask import Flask, render_template, request
app = Flask(__name__, template_folder="templates")
import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import re
def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});') 

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext


@app.route("/")
def hello():
    return render_template("base.html")

@app.route("/", methods=['POST','GET'])
def account():
    data = request.form
    username = data['username']
    password=data['password']
    imap_server=data['providor']
    
    # use your email provider's IMAP server, you can look for your provider's IMAP server on Google
    # or check this page: https://www.systoolsgroup.com/imap/
    # for office 365, it's this:
    # imap_server = "outlook.office365.com"

    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(username, password)

    spam_var=0
    ham_var=0
    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    N = int(data['total'])
    
    # total number of emails
    messages = int(messages[0])


    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    if encoding!=None:
                        subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                print("Subject:", subject)
                print("From:", From)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                            initBody=body
                            # print("Old body:",body)
                            body=re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", body)
                            # body=body.replace("<table>","").replace("</table>","").replace("<tr>","").replace("</tr>","").replace("<td>","").replace("</td>","").replace("\n","")
                            body=body.replace("\n","")
                            body=cleanhtml(body)
                            # print(" new body:"+body)
                            status=spamChecker(body)
                            
                            # print("Status:",status)
                            if "spotify" in body or "nayapay" or "Yahoo" in body:
                                status[0]="ham"
                            # print("new status:",status)
                            f = open("checkerFile.txt", "a")
                            f.write("subject: "+subject+" From: "+From+"Body: "+body+"\n")
                            f.close()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            # print("body:",body)
                            pass
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    initBody=body
                    if content_type == "text/plain":
                        # print only text email parts
                        # print(body)
                        body=re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", body)
                        # print("old body:",body)
                        status=spamChecker(body)
                        # body=body.replace("<table>","").replace("</table>","").replace("<tr>","").replace("</tr>","").replace("<td>","").replace("</td>","").replace("\n","")
                        body=body.replace("\n","")
                        body=cleanhtml(body)
                        # print("new body:",body)
                        # print("Status:",status)
                        if "spotify" in body or "nayapay" in body or "Yahoo" in body:
                                status[0]="ham"
                        # print("new staus:",status)
                        f = open("checkerFile.txt", "a")
                        f.write("subject: "+subject+" From: "+From+"Body: "+body+"\n")
                        f.close()
                if content_type == "text/html":
                    
                    body=re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", body)
                    # print("old body:",body)
                    
                    # body=body.replace("<table>","").replace("</table>","").replace("<tr>","").replace("</tr>","").replace("<td>","").replace("</td>","").replace("\n","")
                    body=body.replace("\n","")
                    body=cleanhtml(body)
                    status=spamChecker(body)
                    # print("new body:",body)
                    # print("Status:",status)
                    if "spotify" in body or  "nayapay" in body or "Yahoo" in body:
                            status[0]="ham"
                    # print("new staus:",status)
                    # subject=subject.replace(" 'b ","").replace(" ' ","")
                    subject=str(subject)
                    f = open("checkerFile.txt", "a")
                    f.write("subject: "+subject+" From: "+From+"Body: "+body+"\n")
                    f.close()
                    
                    
                    
                    
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        os.mkdir(folder_name)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(initBody)
                    # open in the default browser
                    if status[0]=="ham":
                        ham_var+=1
                        webbrowser.open(filepath)
                    elif status[0]=="spam":
                        spam_var+=1
                print("="*100)
    # close the connection and logout
    imap.close()
    imap.logout()
    return render_template("result.html",spam=spam_var,ham=ham_var)



if __name__=="__main__":
    app.run(debug=True)
