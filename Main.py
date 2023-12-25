from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import re
from SendEmail import SendEmail
from deepdiff import DeepDiff
from selenium.webdriver.common.alert import Alert
import sys
from copy import deepcopy
import threading
import os


class TrainScrapping:
    def __init__(self,src,dest,start_time,start_date,email_id,end_time):
        self.driver = webdriver.Firefox()
        self.src=src.upper()
        self.dest=dest.upper()
        self.start_time=self.convert_to_24hr(start_time)
        self.end_time=self.convert_to_24hr(end_time)
        self.date=datetime.datetime.strptime(start_date, "%d/%m/%Y")
        self.month=self.date.strftime("%B")
        self.curr_year=None
        self.curr_month=None
        self.available_seats={}
        self.prev_available_seats={}
        self.email=SendEmail()
        self.email_id=email_id
    def convert_to_24hr(self,time_str):
        time_obj = datetime.datetime.strptime(time_str, '%I:%M %p')  # Parse 12-hour format
        return time_obj.strftime('%H:%M')  # Format as 24-hour format
        
    def get_link(self):
        try:
            url="https://shuttleonline.ktmb.com.my/Home/Shuttle"
            self.driver.get(url)
            self.driver.implicitly_wait(20)
            self.provide_details()
        except Exception as e:
            print("Couldn't able to get the url",e)
            
    def provide_details(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#validationSummaryModal div.modal-body div.text-center button"))
                )
            element.click()
        except:
            print("Button not found or not clickable.")

        
        source_element=self.driver.find_element(By.ID,"FromStationId").get_attribute("value")
        dest_element=self.driver.find_element(By.ID,"ToStationId").get_attribute("value")
        
        if(source_element!=self.src):
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "i.fa.fa-exchange.web-exchange"))
            ).click()

            
        # date_element=self.driver.find_element(By.ID,"OnwardDate")
        submit_element=self.driver.find_element(By.ID,"btnSubmit")
        
        date_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "OnwardDate"))
            )
        date_input.click()
               
        month = self.driver.find_element(By.CLASS_NAME, "lightpick__select-months")


        self.curr_month = Select(month).first_selected_option.text
        
        year = self.driver.find_element(By.CLASS_NAME, "lightpick__select-years")
        
        self.curr_year = Select(year).first_selected_option.text
        
        
        
        while(self.curr_month!=self.month or self.curr_year!=str(self.date.year)):
            next_month_year = self.driver.find_element(By.CLASS_NAME, "lightpick__next-action")
            next_month_year.click()
            year = self.driver.find_element(By.CLASS_NAME, "lightpick__select-years")
            month = self.driver.find_element(By.CLASS_NAME, "lightpick__select-months")
            self.curr_month = Select(month).first_selected_option.text
            self.curr_year = Select(year).first_selected_option.text
            time.sleep(1)
            
        
        
        desired_datetime = 1703339685876
        days_container = self.driver.find_element(By.CSS_SELECTOR, "div.lightpick__days")
        date_divs = days_container.find_elements(By.TAG_NAME, "div")
        

        date_divs = days_container.find_elements(By.TAG_NAME, "div")

        for date_div in date_divs:
            
            if(date_div.get_attribute("class") not in ["lightpick__day is-previous-month is-disabled","lightpick__day is-available is-previous-month"] and date_div.text==str(self.date.day)):  
                date_div.click()
                break
                
        submit_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnSubmit"))
            )
        submit_element.click()
        
        
        try:
            close = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "popupModalCloseButton"))
            )
            close.click()
        except:
            print("Button with ID 'popupModalCloseButton' not found or not clickable.")
            
        
        self.check_for_seats()
        
    def check_if_no_seat(self):
        try:
            span_element = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.font-weight-bold"))
            )
            if(span_element.text=="No trips found."):
                return True
            else:
                return False
            
        except:
            return False
    
    def deep_compare(self,prev,current):
        diff = DeepDiff(prev,current)
        
        if diff:
            return True
        else:
            return False
    
    def start_refresh(self):
        self.driver.refresh()
        wait = WebDriverWait(self.driver, 10)  # Wait up to 10 seconds for the alert
        alert = wait.until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert.accept()
        
        
        now=datetime.datetime.now()
        current_year=now.strftime("%Y")
        current_month=now.strftime("%m")
        current_date=now.strftime("%d")
        current_time = now.strftime("%H:%M")
        
        if(current_date>str(self.date.strftime("%d")) or current_month>str(self.date.month) or current_year>str(self.date.year)):
            os._exit(0)
        try:
            tag=WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-md-2.col-sm-12.border-right.bg-white.paddlr20 > b.c8888"))
            )
            if(tag.text!="JOURNEY PLAN"):
                self.check_for_seats()
            else:
                return
                
            
        except:
            return
    
        finally:
            self.check_for_seats()
        
        
    def check_for_seats(self):
        train_service=None
        Departure=None
        Arrival=None
        avail_seats=None

        self.prev_available_seats=deepcopy(self.available_seats)
        def add_data():
            if(train_service.text not in self.available_seats["train_service"]):
                                        
                    self.available_seats["train_service"].append(train_service.text)
                    self.available_seats["Departure"].append(Departure.text)
                    self.available_seats["Arrival"].append(Arrival.text)
                    self.available_seats["avail_seats"].append(avail_seats)
                    
            else:
                index=self.available_seats["train_service"].index(train_service.text)
                self.available_seats["avail_seats"][index]=avail_seats
                
        try:
            close = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "popupModalCloseButton"))
            )
            close.click()
        except:
            print("Button with ID 'popupModalCloseButton' not found or not clickable.")
            
        
        
        
        flag=self.check_if_no_seat()
        
        if(flag==True):
            pass # refresh the page
        
        else:
            tbody = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table > tbody.bg-white.depart-trips"))
                    )
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            
            
            for row in rows:
                now = datetime.datetime.now()
                current_year=now.strftime("%Y")
                current_month=now.strftime("%m")
                current_date=now.strftime("%d")
                current_time = now.strftime("%H:%M")
                # import pdb
                # pdb.set_trace()
                
                if("disabled" in row.get_attribute('class')):
                    train_service = row.find_element(By.CSS_SELECTOR, "tr > td.f20.blue-left-border")
                    if("train_service" in self.available_seats and train_service.text in self.available_seats['train_service']):
                        index=self.available_seats["train_service"].index(train_service.text)
                        for key,value in self.available_seats.items():
                            del self.available_seats[key][index]
                    else:
                        continue
                else:
                    # data=row.find_element(By.TAG_NAME,"td")
                    train_service = row.find_element(By.CSS_SELECTOR, "tr > td.f20.blue-left-border")
                    Departure=row.find_element(By.CSS_SELECTOR,"tr > td.text-center.f22")
                    Arrival=row.find_element(By.CSS_SELECTOR,"tr > td.text-center.f22.text-nowrap")
                    string=row.text
                    match= re.search(r"\bm?\s*(\d+)\s*MYR?\b", string)
                    avail_seats=match.group(1)
                    
                    
                    if "train_service" not in self.available_seats:
                        self.available_seats["train_service"]=list()
                    if("Departure" not in self.available_seats):
                        self.available_seats['Departure']=list()
                    if("Arrival" not in self.available_seats):
                        self.available_seats['Arrival']=list()
                    if("avail_seats" not in self.available_seats):
                        self.available_seats['avail_seats']=list()
                    
                    if(current_year<str(self.date.year)):
                        if((self.start_time<Departure.text or self.start_time<Arrival.text) and (self.end_time>Departure.text or self.end_time>Arrival.text)):
                            add_data()
                        
                    elif(current_month<str(self.date.month)):
                        if((self.start_time<Departure.text or self.start_time<Arrival.text) and (self.end_time>Departure.text or self.end_time>Arrival.text)):
                            add_data()
                    
                    elif(current_date<str(self.date.strftime("%d"))):
                        if((self.start_time<Departure.text or self.start_time<Arrival.text) and (self.end_time>Departure.text or self.end_time>Arrival.text)):
                            add_data()
                        
                    elif(current_time<self.start_time and (self.start_time < Departure.text or self.start_time < Arrival.text) and (self.end_time> Departure.text or self.end_time>Arrival.text)):
                        add_data()
                        
     
            compare_result=self.deep_compare(self.prev_available_seats,self.available_seats)
            
            if(compare_result):
                self.email.send_available_details(self.available_seats,self.src,self.dest,self.email_id)
                self.start_refresh()
            else:
                #refrsh and start scrapping
                self.start_refresh()
                pass
        
        
            
            

            #need to swap place if needed 

print("*"*100)
print("Dont't worry i'll check the available tickets run me :)")
print("KINDLY PROVIDE INPUTS BASED ON THE EXAMPLES")
print("*"*100)

src=input("Enter the Source (eg: WOODLANDS CIQ):").strip()
dest=input("Enter the Destination (eg:WOODLANDS CIQ):").strip()


start_date=input("Enter the date on which you have to travel format dd/mm/yyyy eg(25/12/2023) '/' is important:").strip()
start_time=input("Enter the start time eg(10:00 PM) format should be 12 : ").strip()
end_time=input("Enter the end timing eg(10:00 PM) format should be 12 : ").strip()
email_id=input("Enter the email you need to get the notification:").strip()

print("THANK YOU")
print("*"*100)
print("Hold tightly we're going to launch")
TS=TrainScrapping(src,dest,start_time,start_date,email_id,end_time)
while(True):
    thread=threading.Thread(target=TS.get_link)
    thread.start()
    print("NEW THREAD")
    
    thread.join()