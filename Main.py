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



class TrainScrapping:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.src="WOODLANDS CIQ"
        self.dest="WOODLANDS CIQ"
        self.start_time=self.convert_to_24hr("10:00 PM")
        self.date=datetime.datetime.strptime("25/12/2023", "%d/%m/%Y")
        self.month=self.date.strftime("%B")
        self.curr_year=None
        self.curr_month=None
        self.available_seats={}
        self.prev_available_seats={}
        self.email=SendEmail()
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
        
        if(current_date>str(self.date.strftime("%d")) or current_month>str(self.date.month) or current_year>str(self.date.year) or current_time>self.start_time):
            sys.exit()
        else:
            self.check_for_seats()
        
        
    def check_for_seats(self):
        def add_data():
            print("-"*50)
            print(self.available_seats)
            print("-"*50)
            print(self.prev_available_seats)
            print("-"*50)
            if(train_service.text not in self.available_seats["train_service"]):
                                        
                    self.available_seats["train_service"].append(train_service.text)
                    self.available_seats["Departure"].append(Departure.text)
                    self.available_seats["Arrival"].append(Arrival.text)
                    self.available_seats["avail_seats"].append(avail_seats)
                    
            elif(avail_seats not in self.available_seats["avail_seats"] and self.available_seats):
                index=self.available_seats["train_service"].index(train_service)
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
            self.prev_available_seats=self.available_seats.copy()
            
            for row in rows:
                now = datetime.datetime.now()
                current_year=now.strftime("%Y")
                current_month=now.strftime("%m")
                current_date=now.strftime("%d")
                current_time = now.strftime("%H:%M")
                
                if("disabled" in row.get_attribute('class')):
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
                        add_data()
                        
                    elif(current_month<str(self.date.month)):
                        add_data()
                    
                    elif(current_date<str(self.date.strftime("%d"))):
                        add_data()
                        
                    elif(current_time<self.start_time and self.start_time > Departure.text or self.start_time> Arrival.text):
                        add_data()
                        
     
            compare_result=self.deep_compare(self.prev_available_seats,self.available_seats)
            
            if(compare_result):
                self.email.send_available_details(self.available_seats,self.src,self.dest)
                self.start_refresh()
            else:
                #refrsh and start scrapping
                self.start_refresh()
                pass
        
        
            
            

            #need to swap place if needed 
TS=TrainScrapping()
TS.get_link()