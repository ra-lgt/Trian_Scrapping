from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime



class TrainScrapping:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.src="WOODLANDS CIQ"
        self.dest="WOODLANDS CIQ"
        self.start_time=self.convert_to_24hr("03:45 PM")
        self.date=datetime.strptime("26/12/2024", "%d/%m/%Y")
        self.month=self.date.strftime("%B")
        self.curr_year=None
        self.curr_month=None
        self.available_seats={}
        
    def convert_to_24hr(self,time_str):
        time_obj = datetime.strptime(time_str, '%I:%M %p')  # Parse 12-hour format
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
        
        import pdb
        pdb.set_trace()
        

        for date_div in date_divs:
            
            if(date_div.get_attribute("class")!="lightpick__day is-previous-month is-disabled" and date_div.text==str(self.date.day)):  
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
        
        
    def check_for_seats(self):
        import pdb
        pdb.set_trace()
        tbody = WebDriverWait(self.driver, 10).until(
             EC.presence_of_element_located((By.CLASS_NAME, "bg-white depart-trips"))
                )
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        
        for row in rows:
            if("disabled" in row.get_attribute('class')):
                continue
            else:
                data=row.find_element(By.TAG_NAME,"td")
                element = data.find_element(By.CSS_SELECTOR, "td.f20.blue-left-border")
                
                if "train_service" not in self.available_seats:
                    self.available_seats["train_service"]=list()
                if("Departure" not in self.available_seats):
                    self.available_seats['Departure']=list()
                if("Arrival" not in self.available_seats):
                    self.available_seats['Arrival']=list()
                if("available_seats" not in self.available_seats):
                    self.available_seats['Available seats']=list()
                    
                self.available_seats["train_service"].append(element.text)
                
                
        


            
            #need to swap place if needed 
TS=TrainScrapping()
TS.get_link()