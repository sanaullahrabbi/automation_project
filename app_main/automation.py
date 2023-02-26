import re
import time
from pathlib import Path
import requests
from django.conf import settings
import json

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

headers = {
    "charset": "utf-8",
    "Content-Type": "application/json",
}
parent_root = Path(__file__).parent.parent


options = Options()
options.add_argument("--no-sandbox")  # Bypass OS security model
options.add_argument("--headless")  # Runs Chrome in headless mode.
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")  # applicable to windows os only
options.add_argument("start-maximized")  #
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--log-level=3")


class Automation:
    wait_before_ss = 3
    save_ss_to = ""
    step = 0
    progress_id = None
    company_id = None

    def __init__(self):
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
        self.driver.set_window_size(1920, 1080)
        self.driver.get("https://portal.fmcsa.dot.gov/UrsRegistrationWizard/")
        self.timeout = 90

    def update_error_status(self):
        if self.progress_id:
            res = requests.put(
                f"{settings.AUTOMATION_PROGRESS_URL}",
                data=json.dumps(
                    {
                        "progress_id": self.progress_id,
                        "driver_close": True,
                        "closed_step": self.step,
                    }
                ),
                headers=headers,
            )
            print(res.status_code)

    def element_is_presence(self, id):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, id))
            )
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.update_error_status()
            self.driver.quit()

    def element_clicked_by_id(self, id):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, id))
            )
            time.sleep(2)
            self.driver.find_element(By.ID, id).click()
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.update_error_status()
            self.driver.quit()

    def element_clicked_by_xpath(self, xpath):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            time.sleep(2)
            self.driver.find_element(By.XPATH, xpath).click()
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.update_error_status()
            self.driver.quit()

    def element_filled_by_id(self, id, value):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, id))
            )
            time.sleep(2)
            inputFld = self.driver.find_element(By.ID, id)
            inputFld.clear()
            inputFld.send_keys(value)
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.update_error_status()
            self.driver.quit()

    def element_filled_enter_by_id(self, id, value):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, id))
            )
            time.sleep(2)
            inputFld = self.driver.find_element(By.ID, id)
            inputFld.clear()
            inputFld.send_keys(value)
            inputFld.send_keys(Keys.ENTER)
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.update_error_status()
            self.driver.quit()

    def element_value_by_id(self, id):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, id))
            )
            time.sleep(2)
            return self.driver.find_element(By.ID, id)
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.update_error_status()
            self.driver.quit()

    def check_keys_value_exists(self, element, *keys):
        """
        Check if *keys (nested) exists in `element` (dict).
        """
        if not isinstance(element, dict):
            raise AttributeError("keys_exists() expects dict as first argument.")
        if len(keys) == 0:
            raise AttributeError(
                "keys_exists() expects at least two arguments, one given."
            )

        _element = element
        for key in keys:
            try:
                _element = _element[key]
                # print(_element)
            except KeyError:
                return None, False  # key , value not exist
        if _element or _element == 0:
            return _element, True  # key , value exist
        else:
            return None, True  # key exist , value not exist

    def automate_by_value(self, autoobj=lambda: None, element_id="", data={}, *keys):
        itemValue, itemExist = self.check_keys_value_exists(data, *keys)
        # print(itemValue, itemExist)
        if (itemValue or itemValue == 0) and itemExist and element_id:
            autoobj(element_id, itemValue)
        else:
            return False

    def update_auto_progress_with_ss(self, progress_id=None, step=0):
        try:
            if self.progress_id:
                res = requests.put(
                    f"{settings.AUTOMATION_PROGRESS_URL}",
                    data=json.dumps(
                        {"progress_id": self.progress_id, "current_step": step}
                    ),
                    headers=headers,
                )
                print(res.status_code)
                self.step = step
                time.sleep(self.wait_before_ss)
                if self.save_ss_to:
                    self.driver.get_screenshot_as_file(
                        f"{self.save_ss_to}/step_{step}.png"
                    )
                print(f"Complete: step-{step}")
        except Exception as e:
            print(e)

    def complete_auto_progress(self):
        try:
            if self.progress_id:
                res = requests.put(
                    f"{settings.AUTOMATION_PROGRESS_URL}",
                    data=json.dumps(
                        {"progress_id": self.progress_id, "complete": True}
                    ),
                    headers=headers,
                )
        except Exception as e:
            print(e)

    def update_company_usdot(self, usdot=None):
        try:
            if usdot and self.company_id:
                res = requests.put(
                    f"{settings.AUTOMATION_START_URL}{self.company_id}",
                    data=json.dumps({"usdot": usdot}),
                    headers=headers,
                )
        except Exception as e:
            print(e)


def automate_usdot_free(company_id, progress_id, data):
    try:
        auto = Automation()
        auto.progress_id = progress_id
        auto.company_id = company_id
        save_ss_to = f"./media/fmcsa/automation/company_{company_id}"
        Path(parent_root / save_ss_to).mkdir(parents=True, exist_ok=True)
        auto.save_ss_to = save_ss_to

        # step 1
        auto.element_clicked_by_id("applicantNEWImgLabel")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=1)

        # step 2
        auto.element_is_presence("form_B0191P190011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=2)

        # step 3
        auto.element_is_presence("form_B0191P190021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=3)

        # step 4
        auto.element_is_presence("form_B0191P190031")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=4)

        # step 5
        auto.element_is_presence("form_B0191P190041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=5)

        # step 6
        auto.element_is_presence("form_B0191P190051")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=6)

        # step 7
        auto.element_is_presence("form_B0191P190061")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=7)

        # step 8
        auto.element_is_presence("form_B0191P190071")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=8)

        # step 9
        auto.element_is_presence("form_registration_newuser")

        auto.automate_by_value(
            auto.element_filled_by_id,
            "newUserPasswd",
            data,
            "step_9",
            "create_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "newUserPasswdAgain",
            data,
            "step_9",
            "confirm_password",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion1SelectList",
            data,
            "step_9",
            "security_question_1",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer1",
            data,
            "step_9",
            "security_answer_1",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion2SelectList",
            data,
            "step_9",
            "security_question_2",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer2",
            data,
            "step_9",
            "security_answer_2",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion3SelectList",
            data,
            "step_9",
            "security_question_3",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer3",
            data,
            "step_9",
            "security_answer_3",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=9)

        # step 10
        auto.element_is_presence("form_B0031P030021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=10)

        # step 11
        auto.element_is_presence("form_applicationContact")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03001_APP_CONTACT_TYPE",
            data,
            "step_11",
            "application_contact_type",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03002_APP_CONT_FIRST_NAME",
            data,
            "step_11",
            "application_contact_first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03022_APP_CONT_MIDDLE_NAME",
            data,
            "step_11",
            "application_contact_middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03003_APP_CONT_LAST_NAME",
            data,
            "step_11",
            "application_contact_last_name",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03023_APP_CONT_SUFFIX",
            data,
            "step_11",
            "application_contact_suffix",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03021_APP_CONT_TITLE",
            data,
            "step_11",
            "application_contact_title",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03011_APP_CONT_COUNTRY",
            data,
            "step_11",
            "application_contact_country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03004_APP_CONT_ADDR1",
            data,
            "step_11",
            "application_contact_street_address_line_1",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03005_APP_CONT_ADDR2",
            data,
            "step_11",
            "application_contact_street_address_line_2",
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03010_APP_CONT_POSTAL_CODE",
            data,
            "step_11",
            "application_contact_postal_code",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03012_APP_CONT_TEL_NUM_ccode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "country_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_acode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_pcode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "phone_number",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_ecode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "extra_phone_number",
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03018_APP_CONT_PREF_METHOD",
            data,
            "step_11",
            "application_contact_preferred_contact_method",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03015_APP_CONT_EMAIL",
            data,
            "step_11",
            "application_contact_email_address",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03016_APP_CONT_EMAIL_CONFIRM",
            data,
            "step_11",
            "application_contact_confirm_email_address",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=11)

        # step 12
        auto.element_is_presence("form_B0041P040021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=12)

        # step 13
        auto.element_is_presence("form_B0041P040011")
        if data["step_13"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0041P040011S04013_Q04035_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0041P040011S04013_Q04035_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=13)

        # step 14
        auto.element_is_presence("form_B0041P040061")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0041P040061S04001_Q04001_LEGAL_BUS_NAME_id",
            data,
            "step_14",
            "legal_business_name",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=14)

        # step 15
        auto.element_is_presence("form_dba")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=15)

        # step 16
        auto.element_is_presence("form_B0041P040081")
        if data["step_16"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0041P040081S04018_Q04039_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0041P040081S04018_Q04039_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=16)

        # step 17
        auto.element_is_presence("form_dbAddress")
        if data["step_17"]["mailing_address_sameas_principal"]:
            auto.element_clicked_by_id("mailingAddressSameAsPrincipal")

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=17)

        # step 18
        auto.element_is_presence("form_B0041P040101")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_ccode_id",
            data,
            "step_18",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_acode_id",
            data,
            "step_18",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_pcode_id",
            data,
            "step_18",
            "phone_number",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=18)

        # step 19
        auto.element_is_presence("form_B0041P040111")
        einValue, einExist = auto.check_keys_value_exists(data, "step_19", "ein")
        ssnValue, ssnExist = auto.check_keys_value_exists(data, "step_19", "ssn")
        if einExist:
            auto.element_clicked_by_id(
                "questionCode_B0041P040111S04006_Q04024_EIN_SSN_id_1"
            )
            auto.element_filled_by_id(
                "questionCode_B0041P040111S04006_Q04040_id", einValue
            )
        elif ssnExist:
            auto.element_clicked_by_id(
                "questionCode_B0041P040111S04006_Q04024_EIN_SSN_id_2"
            )
            auto.element_filled_by_id(
                "questionCode_B0041P040111S04006_Q04040_id", ssnValue
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=19)

        # step 20
        auto.element_is_presence("form_B0041P040201")
        if data["step_20"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0041P040201S04024_Q04054_GOVT_UNIT_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0041P040201S04024_Q04054_GOVT_UNIT_id_N"
            )

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=20)

        # step 21
        auto.element_is_presence("form_bdProprietor")
        checkboxs = auto.driver.find_element(
            By.XPATH,
            '//*[@id="form_bdProprietor"]/table/tbody/tr/td/table/tbody/tr[2]/td/table',
        ).find_elements(By.TAG_NAME, "tr")
        for i in checkboxs:
            if data["step_21"]["checked"] in i.find_element(By.TAG_NAME, "label").text:
                i.find_element(By.TAG_NAME, "input").click()

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q04032_FORM_OF_BUS_STATE",
            data,
            "step_21",
            "choose_one",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=21)

        # step 22
        auto.element_is_presence("form_bdOwnership")
        checkboxs = auto.driver.find_element(
            By.XPATH,
            '//*[@id="form_bdOwnership"]/table/tbody/tr/td/table/tbody/tr[2]/td/table',
        ).find_elements(By.TAG_NAME, "tr")
        for i in checkboxs:
            if data["step_22"]["checked"] in i.find_element(By.TAG_NAME, "label").text:
                i.find_element(By.TAG_NAME, "input").click()
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=22)

        # step 23
        auto.element_is_presence("form_bdTitles")
        auto.element_clicked_by_id("proprietorRadio_1")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorFirstName_1_id",
            data,
            "step_23",
            "first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorMiddleName_1_id",
            data,
            "step_23",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorLastName_1_id",
            data,
            "step_23",
            "last_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "proprietorTitle_1_id", data, "step_23", "title"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "proprietorEmail_1_id", data, "step_23", "email"
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "proprietorTelephone_1_ccode_id",
            data,
            "step_23",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorTelephone_1_acode_id",
            data,
            "step_23",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorTelephone_1_pcode_id",
            data,
            "step_23",
            "phone_number",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=23)

        # step 24
        auto.element_is_presence("form_bdCompAddr")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q04041_COUNTRY",
            data,
            "step_24",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q04048_POSTAL_CODE",
            data,
            "step_24",
            "postal_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q04042_ADDRESS1",
            data,
            "step_24",
            "street_address_or_route_number_line_1",
        )
        # auto.automate_by_value(auto.element_filled_by_id,'Q04043_ADDRESS2',data,'step_24','street_address_or_route_number_line_2')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=24)

        # step 25
        auto.element_is_presence("form_B0041P040181")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=25)

        # step 26
        auto.element_is_presence("form_B0051P050261")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=26)

        # step 27
        auto.element_is_presence("form_B0051P050011")
        if data["step_27"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050011S05001_Q05001_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050011S05001_Q05001_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=27)

        # step 28
        auto.element_is_presence('form_B0051P050021')
        if data['step_28']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050021S05002_Q05002_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050021S05002_Q05002_id_N')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=28)

        # step 29
        auto.element_is_presence('form_B0051P050031')
        if data['step_29']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050031S05003_Q05003_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050031S05003_Q05003_id_N')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=29)

        # # step 30
        # auto.element_is_presence("form_B0051P050041")
        # auto.element_clicked_by_id("questionCode_B0051P050041S05004_Q05004_id_OC0104")
        # auto.driver.get_screenshot_as_file(f"{save_ss_to}/step_30.png")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=30)

        # # step 31
        # auto.element_is_presence("form_B0051P050051")
        # if data["step_31"]["checked"]:
        #     auto.element_clicked_by_id("questionCode_B0051P050051S05005_Q05006_id_Y")
        # else:
        #     auto.element_clicked_by_id("questionCode_B0051P050051S05005_Q05006_id_N")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=31)

        # step 32
        auto.element_is_presence('form_B0051P050071')
        if data['step_32']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050071S05007_Q05008_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050071S05007_Q05008_id_N')
            
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=32)

        # step 33
        # auto.element_is_presence("form_B0051P050111")
        # if data["step_33"]["checked"]:
        #     auto.element_clicked_by_id("questionCode_B0051P050111S05011_Q05030_id_Y")
        # else:
        #     auto.element_clicked_by_id("questionCode_B0051P050111S05011_Q05030_id_N")
        # auto.element_clicked_by_id("menu_next_text")
        auto.element_is_presence('form_B0051P050081')
        auto.element_clicked_by_id('questionCode_B0051P050081S05008_Q05005_id_OC0302')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=33)

        # step 34
        auto.element_is_presence('form_B0051P050091')
        if data['step_34']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050091S05009_Q05028_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050091S05009_Q05028_id_N')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=34)

        # step 35
        auto.element_is_presence('form_B0051P050111')
        if data['step_35']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050111S05011_Q05030_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050111S05011_Q05030_id_N')

        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=35)

        # step 36
        auto.element_is_presence('form_B0051P050221')
        if data['step_36']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050221S05022_Q05013_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050221S05022_Q05013_id_N')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=36)

        # step 37
        auto.element_is_presence('form_B0051P050271')
        if data['step_37']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050271S05027_Q05015_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050271S05027_Q05015_id_N')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=37)

        # step 38
        auto.element_is_presence('form_B0051P050311')
        if data['step_38']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050311S05031_Q05019_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050311S05031_Q05019_id_N')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=38)

        # step 39
        auto.element_is_presence('form_B0051P050321')
        if data['step_39']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050321S05032_Q05021_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050321S05032_Q05021_id_N')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=39)

        # step 40
        auto.element_is_presence('form_B0051P050331')
        if data['step_40']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050331S05033_Q05022_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050331S05033_Q05022_id_N')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=40)

        # step 41
        auto.element_is_presence('form_B0051P050391')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=41)

        # step 42
        auto.element_is_presence('form_B0051P050241')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=42)

        # step 43
        auto.element_is_presence('form_B0061P060011')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=43)

        # step 44
        auto.element_is_presence('form_B0061P060121')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060121S06061_Q06117_NON_CMV_PROP_ONLY_id',data,'step_44','non_cmv_property')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=44)

        # step 45
        auto.element_is_presence('form_B0061P060021')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06004_Q06001_STRAIGHT_TRUCK_OWNED_id',data,'step_43','straight_trucks','owned')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06004_Q06002_STRAIGHT_TRUCK_TERMLEASED_id',data,'step_43','straight_trucks', 'term_leased')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06004_Q06003_STRAIGHT_TRUCK_TRIPLEASED_id',data,'step_43','straight_trucks','trip_leased')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06004_Q06004_STRAIGHT_TRUCK_DRIVEWAY_id',data,'step_43','straight_trucks','tow_driveway')

        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06042_Q06005_TRUCK_TRACTOR_OWNED_id',data,'step_43','truck_tractors','owned')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06042_Q06006_TRUCK_TRACTOR_TERMLEASED_id',data,'step_43','truck_tractors','term_leased')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06042_Q06007_TRUCK_TRACTOR_TRIPLEASED_id',data,'step_43','truck_tractors','trip_leased')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06042_Q06008_TRUCK_TRACTOR_DRIVEWAY_id',data,'step_43','truck_tractors','tow_driveway')

        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06043_Q06009_TRAILER_OWNED_id',data,'step_43','trailers','owned')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06043_Q06010_TRAILER_TERMLEASED_id',data,'step_43','trailers','term_leased')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06043_Q06011_TRAILER_TRIPLEASED_id',data,'step_43','trailers','trip_leased')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06043_Q06012_TRAILER_DRIVEWAY_id',data,'step_43','trailers','tow_driveway')

        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06044_Q06013_IEP_OWNED_id',data,'step_43','iep_trailer_chassis_only','owned')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06044_Q06014_IEP_TERMLEASED_id',data,'step_43','iep_trailer_chassis_only','term_leased')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06044_Q06015_IEP_TRIPLEASED_id',data,'step_43','iep_trailer_chassis_only','trip_leased')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06044_Q06016_IEP_DRIVEWAY_id',data,'step_43','iep_trailer_chassis_only','tow_driveway')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060021S06044_Q06080_IEP_SERVICED_id',data,'step_43','iep_trailer_chassis_only','serviced')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=45)

        # step 46
        auto.element_is_presence('form_B0061P060071')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060071S06007_Q06046_id',data,'step_46','canada')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060071S06007_Q06047_id',data,'step_46','mexico')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=46)

        # step 47
        auto.element_is_presence('form_B0061P060081')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060081S06008_Q06048_id',data,'step_47','questionCode_B0061P060081S06008_Q06048_id')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=47)

        # step 48
        auto.element_is_presence('form_B0061P060091')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0061P060091S06009_Q06049_id',data,'step_48','questionCode_B0061P060091S06009_Q06049_id')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=48)

        # step 49
        auto.element_is_presence('form_B0071P070021')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=49)

        # step 50
        auto.element_is_presence('form_B0061P060101')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=50)

        # step 51
        auto.element_is_presence("form_B0071P070011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=51)

        # step 52
        auto.element_is_presence('form_B0071P070021')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0071P070021S07002_Q07001_id',data,'step_52','questionCode_B0071P070021S07002_Q07001_id')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0071P070021S07002_Q07002_id',data,'step_52','questionCode_B0071P070021S07002_Q07002_id')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=52)

        # step 53
        auto.element_is_presence('form_B0071P070051')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0071P070051S07003_Q07003_id',data,'step_53','questionCode_B0071P070051S07003_Q07003_id')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0071P070051S07003_Q07004_id',data,'step_53','questionCode_B0071P070051S07003_Q07004_id')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=53)

        # #step 54
        # auto.element_is_presence('form_B0131P130011')
        # auto.driver.get_screenshot_as_file(f'{save_ss_to}/step_54.png')
        # auto.element_clicked_by_id('menu_next_text')
        # print('Complete: step-54')
        # progress.current_step = 54
        # progress.save()

        # # In[59]:

        # #step 55
        # auto.element_is_presence('form_B0131P130061')

        # if data['step_55']['checked']:
        #     auto.element_clicked_by_id('questionCode_B0131P130061S13006_Q13007_id_Y')
        # else:
        #     auto.element_clicked_by_id('questionCode_B0131P130061S13006_Q13007_id_N')

        # auto.driver.get_screenshot_as_file(f'{save_ss_to}/step_55.png')
        # auto.element_clicked_by_id('menu_next_text')

        # print('Complete: step-55')
        # progress.current_step = 55
        # progress.save()

        # In[60]:

        # step 56
        auto.element_is_presence('form_B0071P070061')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0071P070061S07004_Q07005_id',data,'step_56','questionCode_B0071P070061S07004_Q07005_id')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=56)

        # step 57
        auto.element_is_presence('form_B0071P070031')

        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0071P070031S07005_Q07006_id',data,'step_57','canada')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0071P070031S07005_Q07007_id',data,'step_57','mexico')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=57)

        # step 58
        auto.element_is_presence("form_B0071P070041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=58)

        # step 59
        auto.element_is_presence("form_B0131P130071")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=59)

        # #step 60
        auto.element_is_presence("form_B0141P140011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=60)

        # #step 61
        auto.element_is_presence('form_B0141P140021')
        if data['step_61']['checked']:
            auto.element_clicked_by_id('questionCode_B0141P140021S14002_Q14002_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0141P140021S14002_Q14002_id_N')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=61)

        # #step 62
        auto.element_is_presence("form_B0141P140041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=62)

        # #step 63
        auto.element_is_presence("form_B0151P150011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=63)

        # #step 64
        auto.element_is_presence('form_certificationEsign')
        auto.automate_by_value(auto.element_filled_by_id,'Q15002_FNAME',data,'step_64','first_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q15007_MIDDLE_NAME',data,'step_64','middle_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q15003_LNAME',data,'step_64','last_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q15005_ESIGN',data,'step_64','esignature_application_password')
        auto.automate_by_value(auto.element_filled_by_id,'Q15004_TITLE',data,'step_64','title')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=64)

        # #step 65
        auto.element_is_presence("form_B0161P160011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=65)

        # #step 66
        auto.element_is_presence("form_B0161P160021")
        auto.element_clicked_by_id('questionCode_B0161P160021S16002_Q16002_id_Y')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=66)

        # #step 67
        auto.element_is_presence('form_B0161P160031')
        auto.element_clicked_by_id('questionCode_B0161P160031S16003_Q16003_id_Y')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=67)

        # #step 68
        auto.element_is_presence('form_B0161P160041')
        auto.element_clicked_by_id('questionCode_B0161P160041S16004_Q16004_id_Y')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=68)

        # #step 69
        auto.element_is_presence('form_B0161P160051')
        auto.element_clicked_by_id('questionCode_B0161P160051S16005_Q16005_id_Y')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=69)

        # #step 70
        auto.element_is_presence('form_B0161P160061')
        auto.element_clicked_by_id('questionCode_B0161P160061S16006_Q16006_id_Y')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=70)

        # #step 71
        auto.element_is_presence('form_B0161P160081')
        auto.element_clicked_by_id('questionCode_B0161P160081S16008_Q16008_id_Y')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=71)

        # #step 72
        auto.element_is_presence('form_B0161P160101')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0161P160101S16010_Q16010_id',data,'step_69','electronic_signature_application_password')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=72)

        # #step 73
        auto.element_is_presence("form_B0161P160191")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=73)

        # #step 74
        auto.element_is_presence("form_B0171P170011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=74)

        # #step 75
        auto.element_is_presence('form_applicantsOathEsign')
        auto.automate_by_value(auto.element_filled_by_id,'Q17002_FNAME',data,'step_64','first_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q17007_MIDDLE_NAME',data,'step_64','middle_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q17003_LNAME',data,'step_64','last_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q17005_ESIGN',data,'step_64','esignature_application_password')
        auto.automate_by_value(auto.element_filled_by_id,'Q17004_TITLE',data,'step_64','title')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=75)

        # #step 76
        auto.element_is_presence("form_B0231P230011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=76)

        # #step 77
        auto.element_is_presence('form_B0231P230021')
        if data['step_74']['checked']:
            auto.element_clicked_by_id('questionCode_B0231P230021S23002_Q23002_COMP_CONTACT_NME_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0231P230021S23002_Q23002_COMP_CONTACT_NME_id_N')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=77)

        # #step 78
        auto.element_is_presence('form_B0231P230041')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0231P230041S23004_Q23012_USERID_id',data,'step_75','user_id')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0231P230041S23004_Q23013_PASSWORD_id',data,'step_75','password')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0231P230041S23004_Q23014_PASSWORD_VERIFY_id',data,'step_75','password')
        auto.automate_by_value(auto.element_filled_enter_by_id,'questionCode_B0231P230041S23004_Q23034_COMP_OFF_PREF_CONT_METHOD_id',data,'step_75','method_of_contact')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0231P230041S23004_Q23038_COMP_OFF_EMAIL_id',data,'step_75','email')
        auto.automate_by_value(auto.element_filled_by_id,'questionCode_B0231P230041S23004_Q23039_COMP_OFF_EMAIL_CFM_id',data,'step_75','email')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=78)

        # #step 79
        auto.element_is_presence('form_B0231P230091')
        if data['step_76']['checked']:
            auto.element_clicked_by_id('questionCode_B0231P230091S23009_Q23041_SEC_QUES_NEW_SET_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0231P230091S23009_Q23041_SEC_QUES_NEW_SET_id_N')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=79)

        # #step 80
        auto.element_is_presence("form_companyRob")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=80)

        # #step 81
        auto.element_is_presence('form_rob')
        auto.automate_by_value(auto.element_filled_by_id,'Q23022_ROB_FNAME',data,'step_78','first_name')
        # auto.automate_by_value(auto.element_filled_by_id,'Q23041_ROB_MNAME',data,'step_78','middle_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q23023_ROB_LNAME',data,'step_78','last_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q23024_ROB_TITLE',data,'step_78','title')
        auto.element_clicked_by_id('Q23025_ROB_CNFM')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=81)

        # #step 82
        auto.element_is_presence('form_companyRoles')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=82)

        # #step 83
        auto.element_is_presence('form_roleResponsibility')
        auto.automate_by_value(auto.element_filled_by_id,'Q23027_RESP_FNAME',data,'step_80','first_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q23028_RESP_LNAME',data,'step_80','last_name')
        auto.automate_by_value(auto.element_filled_by_id,'Q23029_RESP_TITLE',data,'step_80','title')
        auto.element_clicked_by_id('Q23030_RESP_CNFM')

        auto.element_clicked_by_id('menu_next_text')
        auto.update_auto_progress_with_ss(progress_id=progress_id, step=83)

        # #step 84
        auto.element_is_presence('form_B0181P180011')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=84)

        # step 85
        auto.element_is_presence("form_B0181P180071")
        paymentMsg = auto.element_value_by_id(
            "questionDesc_Q18028_NEW_REG_PAYMENT_OK_MSG"
        )
        auto.update_auto_progress_with_ss(progress_id=progress_id, step=84)

        if paymentMsg:
            intList = re.findall(r"\b\d+\b", paymentMsg.text)
            if intList:
                usdot = int(intList[0])
                print(usdot)
                auto.update_company_usdot(usdot)

        auto.complete_auto_progress()
        time.sleep(5)
        auto.driver.quit()
        print("automation complete ---")

    except Exception as e:
        auto.driver.quit()
        print("driver quit on error")
        print(e)
    finally:
        auto.driver.quit()
        print("driver quit")

    return True


def automate_usdot_household(company_id, progress_id, data):
    try:
        auto = Automation()
        auto.progress_id = progress_id
        auto.company_id = company_id
        save_ss_to = f"./media/fmcsa/automation/company_{company_id}"
        Path(parent_root / save_ss_to).mkdir(parents=True, exist_ok=True)
        auto.save_ss_to = save_ss_to

        # step 1
        auto.element_clicked_by_id("applicantNEWImgLabel")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=1)

        # step 2
        auto.element_is_presence("form_B0191P190011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=2)

        # step 3
        auto.element_is_presence("form_B0191P190021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=3)

        # step 4
        auto.element_is_presence("form_B0191P190031")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=4)

        # step 5
        auto.element_is_presence("form_B0191P190041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=5)

        # step 6
        auto.element_is_presence("form_B0191P190051")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=6)

        # step 7
        auto.element_is_presence("form_B0191P190061")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=7)

        # step 8
        auto.element_is_presence("form_B0191P190071")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=8)

        # step 9
        auto.element_is_presence("form_registration_newuser")

        auto.automate_by_value(
            auto.element_filled_by_id,
            "newUserPasswd",
            data,
            "step_9",
            "create_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "newUserPasswdAgain",
            data,
            "step_9",
            "confirm_password",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion1SelectList",
            data,
            "step_9",
            "security_question_1",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer1",
            data,
            "step_9",
            "security_answer_1",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion2SelectList",
            data,
            "step_9",
            "security_question_2",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer2",
            data,
            "step_9",
            "security_answer_2",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion3SelectList",
            data,
            "step_9",
            "security_question_3",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer3",
            data,
            "step_9",
            "security_answer_3",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=9)

        # step 10
        auto.element_is_presence("form_B0031P030021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=10)

        # step 11
        auto.element_is_presence("form_applicationContact")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03001_APP_CONTACT_TYPE",
            data,
            "step_11",
            "application_contact_type",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03002_APP_CONT_FIRST_NAME",
            data,
            "step_11",
            "application_contact_first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03022_APP_CONT_MIDDLE_NAME",
            data,
            "step_11",
            "application_contact_middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03003_APP_CONT_LAST_NAME",
            data,
            "step_11",
            "application_contact_last_name",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03023_APP_CONT_SUFFIX",
            data,
            "step_11",
            "application_contact_suffix",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03021_APP_CONT_TITLE",
            data,
            "step_11",
            "application_contact_title",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03011_APP_CONT_COUNTRY",
            data,
            "step_11",
            "application_contact_country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03004_APP_CONT_ADDR1",
            data,
            "step_11",
            "application_contact_street_address_line_1",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03005_APP_CONT_ADDR2",
            data,
            "step_11",
            "application_contact_street_address_line_2",
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03010_APP_CONT_POSTAL_CODE",
            data,
            "step_11",
            "application_contact_postal_code",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03012_APP_CONT_TEL_NUM_ccode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "country_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_acode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_pcode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "phone_number",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_ecode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "extra_phone_number",
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03018_APP_CONT_PREF_METHOD",
            data,
            "step_11",
            "application_contact_preferred_contact_method",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03015_APP_CONT_EMAIL",
            data,
            "step_11",
            "application_contact_email_address",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03016_APP_CONT_EMAIL_CONFIRM",
            data,
            "step_11",
            "application_contact_confirm_email_address",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=11)

        # step 12
        auto.element_is_presence("form_B0041P040021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=12)

        # step 13
        auto.element_is_presence("form_B0041P040011")
        if data["step_13"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0041P040011S04013_Q04035_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0041P040011S04013_Q04035_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=13)

        # step 14
        auto.element_is_presence("form_B0041P040061")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0041P040061S04001_Q04001_LEGAL_BUS_NAME_id",
            data,
            "step_14",
            "legal_business_name",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=14)

        # step 15
        auto.element_is_presence("form_dba")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=15)

        # step 16
        auto.element_is_presence("form_B0041P040081")
        if data["step_16"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0041P040081S04018_Q04039_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0041P040081S04018_Q04039_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=16)

        # step 17
        auto.element_is_presence("form_dbAddress")
        if data["step_17"]["mailing_address_sameas_principal"]:
            auto.element_clicked_by_id("mailingAddressSameAsPrincipal")

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=17)

        # step 18
        auto.element_is_presence("form_B0041P040101")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_ccode_id",
            data,
            "step_18",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_acode_id",
            data,
            "step_18",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_pcode_id",
            data,
            "step_18",
            "phone_number",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=18)

        # step 19
        auto.element_is_presence("form_B0041P040111")
        einValue, einExist = auto.check_keys_value_exists(data, "step_19", "ein")
        ssnValue, ssnExist = auto.check_keys_value_exists(data, "step_19", "ssn")
        if einExist:
            auto.element_clicked_by_id(
                "questionCode_B0041P040111S04006_Q04024_EIN_SSN_id_1"
            )
            auto.element_filled_by_id(
                "questionCode_B0041P040111S04006_Q04040_id", einValue
            )
        elif ssnExist:
            auto.element_clicked_by_id(
                "questionCode_B0041P040111S04006_Q04024_EIN_SSN_id_2"
            )
            auto.element_filled_by_id(
                "questionCode_B0041P040111S04006_Q04040_id", ssnValue
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=19)

        # step 20
        auto.element_is_presence("form_B0041P040201")
        if data["step_20"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0041P040201S04024_Q04054_GOVT_UNIT_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0041P040201S04024_Q04054_GOVT_UNIT_id_N"
            )

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=20)

        # step 21
        auto.element_is_presence("form_bdProprietor")
        checkboxs = auto.driver.find_element(
            By.XPATH,
            '//*[@id="form_bdProprietor"]/table/tbody/tr/td/table/tbody/tr[2]/td/table',
        ).find_elements(By.TAG_NAME, "tr")
        for i in checkboxs:
            if data["step_21"]["checked"] in i.find_element(By.TAG_NAME, "label").text:
                i.find_element(By.TAG_NAME, "input").click()

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q04032_FORM_OF_BUS_STATE",
            data,
            "step_21",
            "choose_one",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=21)

        # step 22
        auto.element_is_presence("form_bdOwnership")
        checkboxs = auto.driver.find_element(
            By.XPATH,
            '//*[@id="form_bdOwnership"]/table/tbody/tr/td/table/tbody/tr[2]/td/table',
        ).find_elements(By.TAG_NAME, "tr")
        for i in checkboxs:
            if data["step_22"]["checked"] in i.find_element(By.TAG_NAME, "label").text:
                i.find_element(By.TAG_NAME, "input").click()
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=22)

        # step 23
        auto.element_is_presence("form_bdTitles")
        auto.element_clicked_by_id("proprietorRadio_1")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorFirstName_1_id",
            data,
            "step_23",
            "first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorMiddleName_1_id",
            data,
            "step_23",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorLastName_1_id",
            data,
            "step_23",
            "last_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "proprietorTitle_1_id", data, "step_23", "title"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "proprietorEmail_1_id", data, "step_23", "email"
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "proprietorTelephone_1_ccode_id",
            data,
            "step_23",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorTelephone_1_acode_id",
            data,
            "step_23",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorTelephone_1_pcode_id",
            data,
            "step_23",
            "phone_number",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=23)

        # step 24
        auto.element_is_presence("form_bdCompAddr")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q04041_COUNTRY",
            data,
            "step_24",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q04048_POSTAL_CODE",
            data,
            "step_24",
            "postal_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q04042_ADDRESS1",
            data,
            "step_24",
            "street_address_or_route_number_line_1",
        )
        # auto.automate_by_value(auto.element_filled_by_id,'Q04043_ADDRESS2',data,'step_24','street_address_or_route_number_line_2')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=24)

        # step 25
        auto.element_is_presence("form_B0041P040181")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=25)

        # step 26
        auto.element_is_presence("form_B0051P050261")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=26)

        # step 27
        auto.element_is_presence("form_B0051P050011")
        if data["step_27"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050011S05001_Q05001_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050011S05001_Q05001_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=27)

        # step 28
        auto.element_is_presence("form_B0051P050021")
        if data["step_28"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050021S05002_Q05002_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050021S05002_Q05002_id_N")
        auto.element_clicked_by_id("menu_next_text")
        auto.update_auto_progress_with_ss(progress_id=progress_id, step=28)

        # step 29
        auto.element_is_presence("form_B0051P050031")
        if data["step_29"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050031S05003_Q05003_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050031S05003_Q05003_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=29)

        # step 30
        auto.element_is_presence("form_B0051P050041")
        auto.element_clicked_by_id("questionCode_B0051P050041S05004_Q05004_id_OC0104")
        auto.driver.get_screenshot_as_file(f"{save_ss_to}/step_30.png")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=30)

        # step 31
        auto.element_is_presence("form_B0051P050051")
        if data["step_31"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050051S05005_Q05006_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050051S05005_Q05006_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=31)

        # step 32
        auto.element_is_presence("form_B0051P050071")
        if data["step_32"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050071S05007_Q05008_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050071S05007_Q05008_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=32)

        # step 33
        auto.element_is_presence("form_B0051P050111")
        if data["step_33"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050111S05011_Q05030_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050111S05011_Q05030_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=33)

        # step 34
        auto.element_is_presence("form_B0051P050221")
        if data["step_34"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050221S05022_Q05013_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050221S05022_Q05013_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=34)

        # step 35
        auto.element_is_presence("form_B0051P050271")
        if data["step_35"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050271S05027_Q05015_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050271S05027_Q05015_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=35)

        # step 36
        auto.element_is_presence("form_B0051P050311")
        if data["step_36"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050311S05031_Q05019_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050311S05031_Q05019_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=36)

        # step 37
        auto.element_is_presence("form_B0051P050321")
        if data["step_37"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050321S05032_Q05021_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050321S05032_Q05021_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=37)

        # step 38
        auto.element_is_presence("form_B0051P050331")
        if data["step_38"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050331S05033_Q05022_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050331S05033_Q05022_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=38)

        # step 39
        auto.element_is_presence("form_B0051P050391")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=39)

        # step 40
        auto.element_is_presence("form_B0051P050241")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=40)

        # step 41
        auto.element_is_presence("form_B0061P060011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=41)

        # step 42
        auto.element_is_presence("form_B0061P060121")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060121S06061_Q06117_NON_CMV_PROP_ONLY_id",
            data,
            "step_42",
            "non_cmv_property",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=42)

        # step 43
        auto.element_is_presence("form_B0061P060021")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06004_Q06001_STRAIGHT_TRUCK_OWNED_id",
            data,
            "step_43",
            "straight_trucks",
            "owned",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06004_Q06002_STRAIGHT_TRUCK_TERMLEASED_id",
            data,
            "step_43",
            "straight_trucks",
            "term_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06004_Q06003_STRAIGHT_TRUCK_TRIPLEASED_id",
            data,
            "step_43",
            "straight_trucks",
            "trip_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06004_Q06004_STRAIGHT_TRUCK_DRIVEWAY_id",
            data,
            "step_43",
            "straight_trucks",
            "tow_driveway",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06042_Q06005_TRUCK_TRACTOR_OWNED_id",
            data,
            "step_43",
            "truck_tractors",
            "owned",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06042_Q06006_TRUCK_TRACTOR_TERMLEASED_id",
            data,
            "step_43",
            "truck_tractors",
            "term_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06042_Q06007_TRUCK_TRACTOR_TRIPLEASED_id",
            data,
            "step_43",
            "truck_tractors",
            "trip_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06042_Q06008_TRUCK_TRACTOR_DRIVEWAY_id",
            data,
            "step_43",
            "truck_tractors",
            "tow_driveway",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06043_Q06009_TRAILER_OWNED_id",
            data,
            "step_43",
            "trailers",
            "owned",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06043_Q06010_TRAILER_TERMLEASED_id",
            data,
            "step_43",
            "trailers",
            "term_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06043_Q06011_TRAILER_TRIPLEASED_id",
            data,
            "step_43",
            "trailers",
            "trip_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06043_Q06012_TRAILER_DRIVEWAY_id",
            data,
            "step_43",
            "trailers",
            "tow_driveway",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06013_IEP_OWNED_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "owned",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06014_IEP_TERMLEASED_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "term_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06015_IEP_TRIPLEASED_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "trip_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06016_IEP_DRIVEWAY_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "tow_driveway",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06080_IEP_SERVICED_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "serviced",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=43)

        # step 44
        auto.element_is_presence("form_B0061P060071")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060071S06007_Q06046_id",
            data,
            "step_44",
            "canada",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060071S06007_Q06047_id",
            data,
            "step_44",
            "mexico",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=44)

        # step 45
        auto.element_is_presence("form_B0061P060081")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060081S06008_Q06048_id",
            data,
            "step_45",
            "questionCode_B0061P060081S06008_Q06048_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=45)

        # step 46
        auto.element_is_presence("form_B0061P060091")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060091S06009_Q06049_id",
            data,
            "step_46",
            "questionCode_B0061P060091S06009_Q06049_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=46)

        # step 47
        auto.element_is_presence("form_B0061P060101")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=47)

        # step 48
        auto.element_is_presence("form_B0071P070011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=48)

        # step 49
        auto.element_is_presence("form_B0071P070021")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070021S07002_Q07001_id",
            data,
            "step_49",
            "questionCode_B0071P070021S07002_Q07001_id",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070021S07002_Q07002_id",
            data,
            "step_49",
            "questionCode_B0071P070021S07002_Q07002_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=49)

        # step 50
        auto.element_is_presence("form_B0071P070051")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070051S07003_Q07003_id",
            data,
            "step_50",
            "questionCode_B0071P070051S07003_Q07003_id",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070051S07003_Q07004_id",
            data,
            "step_50",
            "questionCode_B0071P070051S07003_Q07004_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=50)

        # step 51
        auto.element_is_presence("form_B0071P070061")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070061S07004_Q07005_id",
            data,
            "step_51",
            "questionCode_B0071P070061S07004_Q07005_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=51)

        # step 52
        auto.element_is_presence("form_B0071P070031")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070031S07005_Q07006_id",
            data,
            "step_44",
            "canada",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070031S07005_Q07007_id",
            data,
            "step_44",
            "mexico",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=52)

        # step 53
        auto.element_is_presence("form_B0071P070041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=53)

        # #step 54
        # auto.element_is_presence('form_B0131P130011')
        # auto.driver.get_screenshot_as_file(f'{save_ss_to}/step_54.png')
        # auto.element_clicked_by_id('menu_next_text')
        # print('Complete: step-54')
        # progress.current_step = 54
        # progress.save()

        # # In[59]:

        # #step 55
        # auto.element_is_presence('form_B0131P130061')

        # if data['step_55']['checked']:
        #     auto.element_clicked_by_id('questionCode_B0131P130061S13006_Q13007_id_Y')
        # else:
        #     auto.element_clicked_by_id('questionCode_B0131P130061S13006_Q13007_id_N')

        # auto.driver.get_screenshot_as_file(f'{save_ss_to}/step_55.png')
        # auto.element_clicked_by_id('menu_next_text')

        # print('Complete: step-55')
        # progress.current_step = 55
        # progress.save()

        # In[60]:

        # step 56
        auto.element_is_presence("form_B0131P130071")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=56)

        # step 57
        auto.element_is_presence("form_B0141P140011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=57)

        # step 58
        auto.element_is_presence("form_B0141P140021")
        if data["step_58"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0141P140021S14002_Q14002_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0141P140021S14002_Q14002_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=58)

        # step 59
        auto.element_is_presence("form_B0141P140041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=59)

        # #step 60
        auto.element_is_presence("form_B0151P150011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=60)

        # #step 61
        auto.element_is_presence("form_certificationEsign")
        auto.automate_by_value(
            auto.element_filled_by_id, "Q15002_FNAME", data, "step_61", "first_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q15007_MIDDLE_NAME",
            data,
            "step_61",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q15003_LNAME", data, "step_61", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q15005_ESIGN",
            data,
            "step_61",
            "esignature_application_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q15004_TITLE", data, "step_61", "title"
        )

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=61)

        # #step 62
        auto.element_is_presence("form_B0161P160011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=62)

        # #step 63
        auto.element_is_presence("form_B0161P160021")
        auto.element_clicked_by_id("questionCode_B0161P160021S16002_Q16002_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=63)

        # #step 64
        auto.element_is_presence("form_B0161P160031")
        auto.element_clicked_by_id("questionCode_B0161P160031S16003_Q16003_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=64)

        # #step 65
        auto.element_is_presence("form_B0161P160041")
        auto.element_clicked_by_id("questionCode_B0161P160041S16004_Q16004_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=65)

        # #step 66
        auto.element_is_presence("form_B0161P160051")
        auto.element_clicked_by_id("questionCode_B0161P160051S16005_Q16005_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=66)

        # #step 67
        auto.element_is_presence("form_B0161P160061")
        auto.element_clicked_by_id("questionCode_B0161P160061S16006_Q16006_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=67)

        # #step 68
        auto.element_is_presence("form_B0161P160081")
        auto.element_clicked_by_id("questionCode_B0161P160081S16008_Q16008_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=68)

        # #step 69
        auto.element_is_presence("form_B0161P160101")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0161P160101S16010_Q16010_id",
            data,
            "step_69",
            "electronic_signature_application_password",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=69)

        # #step 70
        auto.element_is_presence("form_B0161P160191")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=70)

        # #step 71
        auto.element_is_presence("form_B0171P170011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=71)

        # #step 72
        auto.element_is_presence("form_applicantsOathEsign")
        auto.automate_by_value(
            auto.element_filled_by_id, "Q17002_FNAME", data, "step_61", "first_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q17007_MIDDLE_NAME",
            data,
            "step_61",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q17003_LNAME", data, "step_61", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q17005_ESIGN",
            data,
            "step_61",
            "esignature_application_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q17004_TITLE", data, "step_61", "title"
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=72)

        # #step 73
        auto.element_is_presence("form_B0231P230011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=73)

        # #step 74
        auto.element_is_presence("form_B0231P230021")
        if data["step_74"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0231P230021S23002_Q23002_COMP_CONTACT_NME_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0231P230021S23002_Q23002_COMP_CONTACT_NME_id_N"
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=74)

        # #step 75
        auto.element_is_presence("form_B0231P230041")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23012_USERID_id",
            data,
            "step_75",
            "user_id",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23013_PASSWORD_id",
            data,
            "step_75",
            "password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23014_PASSWORD_VERIFY_id",
            data,
            "step_75",
            "password",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0231P230041S23004_Q23034_COMP_OFF_PREF_CONT_METHOD_id",
            data,
            "step_75",
            "method_of_contact",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23038_COMP_OFF_EMAIL_id",
            data,
            "step_75",
            "email",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23039_COMP_OFF_EMAIL_CFM_id",
            data,
            "step_75",
            "email",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=75)

        # #step 76
        auto.element_is_presence("form_B0231P230091")
        if data["step_76"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0231P230091S23009_Q23041_SEC_QUES_NEW_SET_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0231P230091S23009_Q23041_SEC_QUES_NEW_SET_id_N"
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=76)

        # #step 77
        auto.element_is_presence("form_companyRob")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=77)

        # #step 78
        auto.element_is_presence("form_rob")
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23022_ROB_FNAME", data, "step_78", "first_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q23041_ROB_MNAME",
            data,
            "step_78",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23023_ROB_LNAME", data, "step_78", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23024_ROB_TITLE", data, "step_78", "title"
        )
        auto.element_clicked_by_id("Q23025_ROB_CNFM")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=78)

        # #step 79
        auto.element_is_presence("form_companyRoles")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=79)

        # #step 80
        auto.element_is_presence("form_roleResponsibility")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q23027_RESP_FNAME",
            data,
            "step_80",
            "first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q23043_RESP_MNAME",
            data,
            "step_80",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23028_RESP_LNAME", data, "step_80", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23029_RESP_TITLE", data, "step_80", "title"
        )
        auto.element_clicked_by_id("Q23030_RESP_CNFM")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=80)

        # #step 81
        auto.element_is_presence("form_B0181P180011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=81)

        # step 82
        auto.element_is_presence("form_B0181P180071")
        paymentMsg = auto.element_value_by_id(
            "questionDesc_Q18028_NEW_REG_PAYMENT_OK_MSG"
        )
        auto.update_auto_progress_with_ss(progress_id=progress_id, step=84)

        if paymentMsg:
            intList = re.findall(r"\b\d+\b", paymentMsg.text)
            if intList:
                usdot = int(intList[0])
                print(usdot)
                auto.update_company_usdot(usdot)

        auto.complete_auto_progress()
        time.sleep(5)
        auto.driver.quit()
        print("automation complete ---")

    except Exception as e:
        auto.driver.quit()
        print("driver quit on error")
        print(e)
    finally:
        auto.driver.quit()
        print("driver quit")

    return True


def automate_usdot_mc_dot(company_id, progress_id, data):
    try:
        auto = Automation()
        auto.progress_id = progress_id
        auto.company_id = company_id
        save_ss_to = f"./media/fmcsa/automation/company_{company_id}"
        Path(parent_root / save_ss_to).mkdir(parents=True, exist_ok=True)
        auto.save_ss_to = save_ss_to

        # step 1
        auto.element_clicked_by_id("applicantNEWImgLabel")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=1)

        # step 2
        auto.element_is_presence("form_B0191P190011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=2)

        # step 3
        auto.element_is_presence("form_B0191P190021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=3)

        # step 4
        auto.element_is_presence("form_B0191P190031")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=4)

        # step 5
        auto.element_is_presence("form_B0191P190041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=5)

        # step 6
        auto.element_is_presence("form_B0191P190051")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=6)

        # step 7
        auto.element_is_presence("form_B0191P190061")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=7)

        # step 8
        auto.element_is_presence("form_B0191P190071")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=8)

        # step 9
        auto.element_is_presence("form_registration_newuser")

        auto.automate_by_value(
            auto.element_filled_by_id,
            "newUserPasswd",
            data,
            "step_9",
            "create_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "newUserPasswdAgain",
            data,
            "step_9",
            "confirm_password",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion1SelectList",
            data,
            "step_9",
            "security_question_1",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer1",
            data,
            "step_9",
            "security_answer_1",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion2SelectList",
            data,
            "step_9",
            "security_question_2",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer2",
            data,
            "step_9",
            "security_answer_2",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion3SelectList",
            data,
            "step_9",
            "security_question_3",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer3",
            data,
            "step_9",
            "security_answer_3",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=9)

        # step 10
        auto.element_is_presence("form_B0031P030021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=10)

        # step 11
        auto.element_is_presence("form_applicationContact")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03001_APP_CONTACT_TYPE",
            data,
            "step_11",
            "application_contact_type",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03002_APP_CONT_FIRST_NAME",
            data,
            "step_11",
            "application_contact_first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03022_APP_CONT_MIDDLE_NAME",
            data,
            "step_11",
            "application_contact_middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03003_APP_CONT_LAST_NAME",
            data,
            "step_11",
            "application_contact_last_name",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03023_APP_CONT_SUFFIX",
            data,
            "step_11",
            "application_contact_suffix",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03021_APP_CONT_TITLE",
            data,
            "step_11",
            "application_contact_title",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03011_APP_CONT_COUNTRY",
            data,
            "step_11",
            "application_contact_country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03004_APP_CONT_ADDR1",
            data,
            "step_11",
            "application_contact_street_address_line_1",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03005_APP_CONT_ADDR2",
            data,
            "step_11",
            "application_contact_street_address_line_2",
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03010_APP_CONT_POSTAL_CODE",
            data,
            "step_11",
            "application_contact_postal_code",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03012_APP_CONT_TEL_NUM_ccode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "country_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_acode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_pcode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "phone_number",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_ecode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "extra_phone_number",
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03018_APP_CONT_PREF_METHOD",
            data,
            "step_11",
            "application_contact_preferred_contact_method",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03015_APP_CONT_EMAIL",
            data,
            "step_11",
            "application_contact_email_address",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03016_APP_CONT_EMAIL_CONFIRM",
            data,
            "step_11",
            "application_contact_confirm_email_address",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=11)

        # step 12
        auto.element_is_presence("form_B0041P040021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=12)

        # step 13
        auto.element_is_presence("form_B0041P040011")
        if data["step_13"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0041P040011S04013_Q04035_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0041P040011S04013_Q04035_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=13)

        # step 14
        auto.element_is_presence("form_B0041P040061")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0041P040061S04001_Q04001_LEGAL_BUS_NAME_id",
            data,
            "step_14",
            "legal_business_name",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=14)

        # step 15
        auto.element_is_presence("form_dba")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=15)

        # step 16
        auto.element_is_presence("form_B0041P040081")
        if data["step_16"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0041P040081S04018_Q04039_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0041P040081S04018_Q04039_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=16)

        # step 17
        auto.element_is_presence("form_dbAddress")
        if data["step_17"]["mailing_address_sameas_principal"]:
            auto.element_clicked_by_id("mailingAddressSameAsPrincipal")

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=17)

        # step 18
        auto.element_is_presence("form_B0041P040101")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_ccode_id",
            data,
            "step_18",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_acode_id",
            data,
            "step_18",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_pcode_id",
            data,
            "step_18",
            "phone_number",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=18)

        # step 19
        auto.element_is_presence("form_B0041P040111")
        einValue, einExist = auto.check_keys_value_exists(data, "step_19", "ein")
        ssnValue, ssnExist = auto.check_keys_value_exists(data, "step_19", "ssn")
        if einExist:
            auto.element_clicked_by_id(
                "questionCode_B0041P040111S04006_Q04024_EIN_SSN_id_1"
            )
            auto.element_filled_by_id(
                "questionCode_B0041P040111S04006_Q04040_id", einValue
            )
        elif ssnExist:
            auto.element_clicked_by_id(
                "questionCode_B0041P040111S04006_Q04024_EIN_SSN_id_2"
            )
            auto.element_filled_by_id(
                "questionCode_B0041P040111S04006_Q04040_id", ssnValue
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=19)

        # step 20
        auto.element_is_presence("form_B0041P040201")
        if data["step_20"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0041P040201S04024_Q04054_GOVT_UNIT_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0041P040201S04024_Q04054_GOVT_UNIT_id_N"
            )

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=20)

        # step 21
        auto.element_is_presence("form_bdProprietor")
        checkboxs = auto.driver.find_element(
            By.XPATH,
            '//*[@id="form_bdProprietor"]/table/tbody/tr/td/table/tbody/tr[2]/td/table',
        ).find_elements(By.TAG_NAME, "tr")
        for i in checkboxs:
            if data["step_21"]["checked"] in i.find_element(By.TAG_NAME, "label").text:
                i.find_element(By.TAG_NAME, "input").click()

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q04032_FORM_OF_BUS_STATE",
            data,
            "step_21",
            "choose_one",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=21)

        # step 22
        auto.element_is_presence("form_bdOwnership")
        checkboxs = auto.driver.find_element(
            By.XPATH,
            '//*[@id="form_bdOwnership"]/table/tbody/tr/td/table/tbody/tr[2]/td/table',
        ).find_elements(By.TAG_NAME, "tr")
        for i in checkboxs:
            if data["step_22"]["checked"] in i.find_element(By.TAG_NAME, "label").text:
                i.find_element(By.TAG_NAME, "input").click()
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=22)

        # step 23
        auto.element_is_presence("form_bdTitles")
        auto.element_clicked_by_id("proprietorRadio_1")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorFirstName_1_id",
            data,
            "step_23",
            "first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorMiddleName_1_id",
            data,
            "step_23",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorLastName_1_id",
            data,
            "step_23",
            "last_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "proprietorTitle_1_id", data, "step_23", "title"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "proprietorEmail_1_id", data, "step_23", "email"
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "proprietorTelephone_1_ccode_id",
            data,
            "step_23",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorTelephone_1_acode_id",
            data,
            "step_23",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorTelephone_1_pcode_id",
            data,
            "step_23",
            "phone_number",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=23)

        # step 24
        auto.element_is_presence("form_bdCompAddr")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q04041_COUNTRY",
            data,
            "step_24",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q04048_POSTAL_CODE",
            data,
            "step_24",
            "postal_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q04042_ADDRESS1",
            data,
            "step_24",
            "street_address_or_route_number_line_1",
        )
        # auto.automate_by_value(auto.element_filled_by_id,'Q04043_ADDRESS2',data,'step_24','street_address_or_route_number_line_2')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=24)

        # step 25
        auto.element_is_presence("form_B0041P040181")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=25)

        # step 26
        auto.element_is_presence("form_B0051P050261")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=26)

        # step 27
        auto.element_is_presence("form_B0051P050011")
        if data["step_27"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050011S05001_Q05001_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050011S05001_Q05001_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=27)

        # step 28
        auto.element_is_presence("form_B0051P050021")
        if data["step_28"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050021S05002_Q05002_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050021S05002_Q05002_id_N")
        auto.element_clicked_by_id("menu_next_text")
        auto.update_auto_progress_with_ss(progress_id=progress_id, step=28)

        # step 29
        auto.element_is_presence("form_B0051P050031")
        if data["step_29"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050031S05003_Q05003_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050031S05003_Q05003_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=29)

        # step 30
        auto.element_is_presence("form_B0051P050041")
        auto.element_clicked_by_id("questionCode_B0051P050041S05004_Q05004_id_OC0104")
        auto.driver.get_screenshot_as_file(f"{save_ss_to}/step_30.png")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=30)

        # step 31
        auto.element_is_presence("form_B0051P050051")
        if data["step_31"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050051S05005_Q05006_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050051S05005_Q05006_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=31)

        # step 32
        auto.element_is_presence("form_B0051P050071")
        if data["step_32"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050071S05007_Q05008_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050071S05007_Q05008_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=32)

        # step 33
        auto.element_is_presence("form_B0051P050111")
        if data["step_33"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050111S05011_Q05030_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050111S05011_Q05030_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=33)

        # step 34
        auto.element_is_presence("form_B0051P050221")
        if data["step_34"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050221S05022_Q05013_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050221S05022_Q05013_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=34)

        # step 35
        auto.element_is_presence("form_B0051P050271")
        if data["step_35"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050271S05027_Q05015_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050271S05027_Q05015_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=35)

        # step 36
        auto.element_is_presence("form_B0051P050311")
        if data["step_36"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050311S05031_Q05019_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050311S05031_Q05019_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=36)

        # step 37
        auto.element_is_presence("form_B0051P050321")
        if data["step_37"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050321S05032_Q05021_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050321S05032_Q05021_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=37)

        # step 38
        auto.element_is_presence("form_B0051P050331")
        if data["step_38"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0051P050331S05033_Q05022_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0051P050331S05033_Q05022_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=38)

        # step 39
        auto.element_is_presence("form_B0051P050391")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=39)

        # step 40
        auto.element_is_presence("form_B0051P050241")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=40)

        # step 41
        auto.element_is_presence("form_B0061P060011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=41)

        # step 42
        auto.element_is_presence("form_B0061P060121")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060121S06061_Q06117_NON_CMV_PROP_ONLY_id",
            data,
            "step_42",
            "non_cmv_property",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=42)

        # step 43
        auto.element_is_presence("form_B0061P060021")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06004_Q06001_STRAIGHT_TRUCK_OWNED_id",
            data,
            "step_43",
            "straight_trucks",
            "owned",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06004_Q06002_STRAIGHT_TRUCK_TERMLEASED_id",
            data,
            "step_43",
            "straight_trucks",
            "term_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06004_Q06003_STRAIGHT_TRUCK_TRIPLEASED_id",
            data,
            "step_43",
            "straight_trucks",
            "trip_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06004_Q06004_STRAIGHT_TRUCK_DRIVEWAY_id",
            data,
            "step_43",
            "straight_trucks",
            "tow_driveway",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06042_Q06005_TRUCK_TRACTOR_OWNED_id",
            data,
            "step_43",
            "truck_tractors",
            "owned",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06042_Q06006_TRUCK_TRACTOR_TERMLEASED_id",
            data,
            "step_43",
            "truck_tractors",
            "term_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06042_Q06007_TRUCK_TRACTOR_TRIPLEASED_id",
            data,
            "step_43",
            "truck_tractors",
            "trip_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06042_Q06008_TRUCK_TRACTOR_DRIVEWAY_id",
            data,
            "step_43",
            "truck_tractors",
            "tow_driveway",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06043_Q06009_TRAILER_OWNED_id",
            data,
            "step_43",
            "trailers",
            "owned",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06043_Q06010_TRAILER_TERMLEASED_id",
            data,
            "step_43",
            "trailers",
            "term_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06043_Q06011_TRAILER_TRIPLEASED_id",
            data,
            "step_43",
            "trailers",
            "trip_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06043_Q06012_TRAILER_DRIVEWAY_id",
            data,
            "step_43",
            "trailers",
            "tow_driveway",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06013_IEP_OWNED_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "owned",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06014_IEP_TERMLEASED_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "term_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06015_IEP_TRIPLEASED_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "trip_leased",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06016_IEP_DRIVEWAY_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "tow_driveway",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060021S06044_Q06080_IEP_SERVICED_id",
            data,
            "step_43",
            "iep_trailer_chassis_only",
            "serviced",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=43)

        # step 44
        auto.element_is_presence("form_B0061P060071")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060071S06007_Q06046_id",
            data,
            "step_44",
            "canada",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060071S06007_Q06047_id",
            data,
            "step_44",
            "mexico",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=44)

        # step 45
        auto.element_is_presence("form_B0061P060081")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060081S06008_Q06048_id",
            data,
            "step_45",
            "questionCode_B0061P060081S06008_Q06048_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=45)

        # step 46
        auto.element_is_presence("form_B0061P060091")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0061P060091S06009_Q06049_id",
            data,
            "step_46",
            "questionCode_B0061P060091S06009_Q06049_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=46)

        # step 47
        auto.element_is_presence("form_B0061P060101")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=47)

        # step 48
        auto.element_is_presence("form_B0071P070011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=48)

        # step 49
        auto.element_is_presence("form_B0071P070021")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070021S07002_Q07001_id",
            data,
            "step_49",
            "questionCode_B0071P070021S07002_Q07001_id",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070021S07002_Q07002_id",
            data,
            "step_49",
            "questionCode_B0071P070021S07002_Q07002_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=49)

        # step 50
        auto.element_is_presence("form_B0071P070051")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070051S07003_Q07003_id",
            data,
            "step_50",
            "questionCode_B0071P070051S07003_Q07003_id",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070051S07003_Q07004_id",
            data,
            "step_50",
            "questionCode_B0071P070051S07003_Q07004_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=50)

        # step 51
        auto.element_is_presence("form_B0071P070061")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070061S07004_Q07005_id",
            data,
            "step_51",
            "questionCode_B0071P070061S07004_Q07005_id",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=51)

        # step 52
        auto.element_is_presence("form_B0071P070031")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070031S07005_Q07006_id",
            data,
            "step_44",
            "canada",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0071P070031S07005_Q07007_id",
            data,
            "step_44",
            "mexico",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=52)

        # step 53
        auto.element_is_presence("form_B0071P070041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=53)

        # step 54
        auto.element_is_presence("form_B0131P130011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=54)

        # step 55
        auto.element_is_presence("form_B0131P130061")
        if data["step_55"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0131P130061S13006_Q13007_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0131P130061S13006_Q13007_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=55)

        # step 56
        auto.element_is_presence("form_B0131P130071")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=56)

        # step 57
        auto.element_is_presence("form_B0141P140011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=57)

        # step 58
        auto.element_is_presence("form_B0141P140021")
        if data["step_58"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0141P140021S14002_Q14002_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0141P140021S14002_Q14002_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=58)

        # step 59
        auto.element_is_presence("form_B0141P140041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=59)

        # #step 60
        auto.element_is_presence("form_B0151P150011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=60)

        # #step 61
        auto.element_is_presence("form_certificationEsign")
        auto.automate_by_value(
            auto.element_filled_by_id, "Q15002_FNAME", data, "step_61", "first_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q15007_MIDDLE_NAME",
            data,
            "step_61",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q15003_LNAME", data, "step_61", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q15005_ESIGN",
            data,
            "step_61",
            "esignature_application_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q15004_TITLE", data, "step_61", "title"
        )

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=61)

        # #step 62
        auto.element_is_presence("form_B0161P160011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=62)

        # #step 63
        auto.element_is_presence("form_B0161P160021")
        auto.element_clicked_by_id("questionCode_B0161P160021S16002_Q16002_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=63)

        # #step 64
        auto.element_is_presence("form_B0161P160031")
        auto.element_clicked_by_id("questionCode_B0161P160031S16003_Q16003_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=64)

        # #step 65
        auto.element_is_presence("form_B0161P160041")
        auto.element_clicked_by_id("questionCode_B0161P160041S16004_Q16004_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=65)

        # #step 66
        auto.element_is_presence("form_B0161P160051")
        auto.element_clicked_by_id("questionCode_B0161P160051S16005_Q16005_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=66)

        # #step 67
        auto.element_is_presence("form_B0161P160061")
        auto.element_clicked_by_id("questionCode_B0161P160061S16006_Q16006_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=67)

        # #step 68
        auto.element_is_presence("form_B0161P160081")
        auto.element_clicked_by_id("questionCode_B0161P160081S16008_Q16008_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=68)

        # #step 69
        auto.element_is_presence("form_B0161P160101")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0161P160101S16010_Q16010_id",
            data,
            "step_69",
            "electronic_signature_application_password",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=69)

        # #step 70
        auto.element_is_presence("form_B0161P160191")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=70)

        # #step 71
        auto.element_is_presence("form_B0171P170011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=71)

        # #step 72
        auto.element_is_presence("form_applicantsOathEsign")
        auto.automate_by_value(
            auto.element_filled_by_id, "Q17002_FNAME", data, "step_61", "first_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q17007_MIDDLE_NAME",
            data,
            "step_61",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q17003_LNAME", data, "step_61", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q17005_ESIGN",
            data,
            "step_61",
            "esignature_application_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q17004_TITLE", data, "step_61", "title"
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=72)

        # #step 73
        auto.element_is_presence("form_B0231P230011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=73)

        # #step 74
        auto.element_is_presence("form_B0231P230021")
        if data["step_74"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0231P230021S23002_Q23002_COMP_CONTACT_NME_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0231P230021S23002_Q23002_COMP_CONTACT_NME_id_N"
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=74)

        # #step 75
        auto.element_is_presence("form_B0231P230041")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23012_USERID_id",
            data,
            "step_75",
            "user_id",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23013_PASSWORD_id",
            data,
            "step_75",
            "password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23014_PASSWORD_VERIFY_id",
            data,
            "step_75",
            "password",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0231P230041S23004_Q23034_COMP_OFF_PREF_CONT_METHOD_id",
            data,
            "step_75",
            "method_of_contact",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23038_COMP_OFF_EMAIL_id",
            data,
            "step_75",
            "email",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23039_COMP_OFF_EMAIL_CFM_id",
            data,
            "step_75",
            "email",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=75)

        # #step 76
        auto.element_is_presence("form_B0231P230091")
        if data["step_76"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0231P230091S23009_Q23041_SEC_QUES_NEW_SET_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0231P230091S23009_Q23041_SEC_QUES_NEW_SET_id_N"
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=76)

        # #step 77
        auto.element_is_presence("form_companyRob")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=77)

        # #step 78
        auto.element_is_presence("form_rob")
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23022_ROB_FNAME", data, "step_78", "first_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q23041_ROB_MNAME",
            data,
            "step_78",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23023_ROB_LNAME", data, "step_78", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23024_ROB_TITLE", data, "step_78", "title"
        )
        auto.element_clicked_by_id("Q23025_ROB_CNFM")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=78)

        # #step 79
        auto.element_is_presence("form_companyRoles")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=79)

        # #step 80
        auto.element_is_presence("form_roleResponsibility")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q23027_RESP_FNAME",
            data,
            "step_80",
            "first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q23043_RESP_MNAME",
            data,
            "step_80",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23028_RESP_LNAME", data, "step_80", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23029_RESP_TITLE", data, "step_80", "title"
        )
        auto.element_clicked_by_id("Q23030_RESP_CNFM")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=80)

        # #step 81
        auto.element_is_presence("form_B0181P180011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=81)

        # step 82
        auto.element_is_presence("form_B0181P180021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=82)

        # #step 83
        auto.element_is_presence("form_paymentInfo")
        if data["step_83"]["card"] == "vi":
            auto.element_clicked_by_id("Q18007_CREDIT_CARD_TYPEVisa")
        elif data["step_83"]["card"] == "mc":
            auto.element_clicked_by_id("Q18007_CREDIT_CARD_TYPEMasterCard")
        elif data["step_83"]["card"] == "ax":
            auto.element_clicked_by_id("Q18007_CREDIT_CARD_TYPEAmex")
        else:
            auto.element_clicked_by_id("Q18007_CREDIT_CARD_TYPEDiscover")

        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q18008_CREDIT_CARD_NUM",
            data,
            "step_83",
            "credit_card_number",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q18009_CREDIT_CARD_EXP_MM",
            data,
            "step_83",
            "choose_exp_month",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q18010_CREDIT_CARD_EXP_YY",
            data,
            "step_83",
            "choose_exp_year",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q18011_CC_SECURITY_CODE",
            data,
            "step_83",
            "security_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q18012_CC_FNAME", data, "step_83", "first_name"
        )
        # auto.automate_by_value(auto.element_filled_by_id,'Q18017_CC_MNAME',data,'step_83','middle_name')
        auto.automate_by_value(
            auto.element_filled_by_id, "Q18016_CC_LNAME", data, "step_83", "last_name"
        )
        # auto.automate_by_value(auto.element_filled_by_id,'Q18____CC_SUFFIX',data,'step_83','suffix')
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q18013_CC_ESIGN",
            data,
            "step_83",
            "electronic_signature_application_password",
        )
        # auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=83)
        auto.element_clicked_by_id("dijit_form_Button_4")

        # step 84
        auto.element_is_presence("form_B0181P180041")
        paymentMsg = auto.element_value_by_id("questionDesc_Q18015")
        auto.update_auto_progress_with_ss(progress_id=progress_id, step=84)

        if paymentMsg:
            intList = re.findall(r"\b\d+\b", paymentMsg.text)
            if intList:
                usdot = int(intList[1])
                print(usdot)
                auto.update_company_usdot(usdot)

        auto.complete_auto_progress()
        time.sleep(5)
        auto.driver.quit()
        print("automation complete ---")

    except Exception as e:
        auto.driver.quit()
        print(e)

    finally:
        auto.driver.quit()
        print("driver quit")

    return True


def automate_usdot_broker(company_id, progress_id, data):
    try:
        auto = Automation()
        auto.progress_id = progress_id
        auto.company_id = company_id
        save_ss_to = f"./media/fmcsa/automation/company_{company_id}"
        Path(parent_root / save_ss_to).mkdir(parents=True, exist_ok=True)
        auto.save_ss_to = save_ss_to

        # step 1
        auto.element_clicked_by_id("applicantNEWImgLabel")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=1)

        # step 2
        auto.element_is_presence("form_B0191P190011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=2)

        # step 3
        auto.element_is_presence("form_B0191P190021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=3)

        # step 4
        auto.element_is_presence("form_B0191P190031")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=4)

        # step 5
        auto.element_is_presence("form_B0191P190041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=5)

        # step 6
        auto.element_is_presence("form_B0191P190051")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=6)

        # step 7
        auto.element_is_presence("form_B0191P190061")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=7)

        # step 8
        auto.element_is_presence("form_B0191P190071")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=8)

        # step 9
        auto.element_is_presence("form_registration_newuser")

        auto.automate_by_value(
            auto.element_filled_by_id,
            "newUserPasswd",
            data,
            "step_9",
            "create_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "newUserPasswdAgain",
            data,
            "step_9",
            "confirm_password",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion1SelectList",
            data,
            "step_9",
            "security_question_1",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer1",
            data,
            "step_9",
            "security_answer_1",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion2SelectList",
            data,
            "step_9",
            "security_question_2",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer2",
            data,
            "step_9",
            "security_answer_2",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "secQuestion3SelectList",
            data,
            "step_9",
            "security_question_3",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "securityAnswer3",
            data,
            "step_9",
            "security_answer_3",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=9)

        # step 10
        auto.element_is_presence("form_B0031P030021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=10)

        # step 11
        auto.element_is_presence("form_applicationContact")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03001_APP_CONTACT_TYPE",
            data,
            "step_11",
            "application_contact_type",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03002_APP_CONT_FIRST_NAME",
            data,
            "step_11",
            "application_contact_first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03022_APP_CONT_MIDDLE_NAME",
            data,
            "step_11",
            "application_contact_middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03003_APP_CONT_LAST_NAME",
            data,
            "step_11",
            "application_contact_last_name",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03023_APP_CONT_SUFFIX",
            data,
            "step_11",
            "application_contact_suffix",
        )

        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03021_APP_CONT_TITLE",
            data,
            "step_11",
            "application_contact_title",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03011_APP_CONT_COUNTRY",
            data,
            "step_11",
            "application_contact_country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03004_APP_CONT_ADDR1",
            data,
            "step_11",
            "application_contact_street_address_line_1",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03005_APP_CONT_ADDR2",
            data,
            "step_11",
            "application_contact_street_address_line_2",
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03010_APP_CONT_POSTAL_CODE",
            data,
            "step_11",
            "application_contact_postal_code",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03012_APP_CONT_TEL_NUM_ccode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "country_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_acode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_pcode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "phone_number",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03012_APP_CONT_TEL_NUM_ecode_id",
            data,
            "step_11",
            "application_contact_telephone_number",
            "extra_phone_number",
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q03018_APP_CONT_PREF_METHOD",
            data,
            "step_11",
            "application_contact_preferred_contact_method",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03015_APP_CONT_EMAIL",
            data,
            "step_11",
            "application_contact_email_address",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q03016_APP_CONT_EMAIL_CONFIRM",
            data,
            "step_11",
            "application_contact_confirm_email_address",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=11)

        # step 12
        auto.element_is_presence("form_B0041P040021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=12)

        # step 13
        auto.element_is_presence("form_B0041P040011")
        if data["step_13"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0041P040011S04013_Q04035_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0041P040011S04013_Q04035_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=13)

        # step 14
        auto.element_is_presence("form_B0041P040061")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0041P040061S04001_Q04001_LEGAL_BUS_NAME_id",
            data,
            "step_14",
            "legal_business_name",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=14)

        # step 15
        auto.element_is_presence("form_dba")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=15)

        # step 16
        auto.element_is_presence("form_B0041P040081")
        if data["step_16"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0041P040081S04018_Q04039_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0041P040081S04018_Q04039_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=16)

        # step 17
        auto.element_is_presence("form_dbAddress")
        if data["step_17"]["mailing_address_sameas_principal"]:
            auto.element_clicked_by_id("mailingAddressSameAsPrincipal")

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=17)

        # step 18
        auto.element_is_presence("form_B0041P040101")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_ccode_id",
            data,
            "step_18",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_acode_id",
            data,
            "step_18",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0041P040101S04005_Q04021_BUS_TEL_NUM_pcode_id",
            data,
            "step_18",
            "phone_number",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=18)

        # step 19
        auto.element_is_presence("form_B0041P040111")
        einValue, einExist = auto.check_keys_value_exists(data, "step_19", "ein")
        ssnValue, ssnExist = auto.check_keys_value_exists(data, "step_19", "ssn")
        if einExist:
            auto.element_clicked_by_id(
                "questionCode_B0041P040111S04006_Q04024_EIN_SSN_id_1"
            )
            auto.element_filled_by_id(
                "questionCode_B0041P040111S04006_Q04040_id", einValue
            )
        elif ssnExist:
            auto.element_clicked_by_id(
                "questionCode_B0041P040111S04006_Q04024_EIN_SSN_id_2"
            )
            auto.element_filled_by_id(
                "questionCode_B0041P040111S04006_Q04040_id", ssnValue
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=19)

        # step 20
        auto.element_is_presence("form_B0041P040201")
        if data["step_20"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0041P040201S04024_Q04054_GOVT_UNIT_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0041P040201S04024_Q04054_GOVT_UNIT_id_N"
            )

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=20)

        # step 21
        auto.element_is_presence("form_bdProprietor")
        checkboxs = auto.driver.find_element(
            By.XPATH,
            '//*[@id="form_bdProprietor"]/table/tbody/tr/td/table/tbody/tr[2]/td/table',
        ).find_elements(By.TAG_NAME, "tr")
        for i in checkboxs:
            if data["step_21"]["checked"] in i.find_element(By.TAG_NAME, "label").text:
                i.find_element(By.TAG_NAME, "input").click()

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q04032_FORM_OF_BUS_STATE",
            data,
            "step_21",
            "choose_one",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=21)

        # step 22
        auto.element_is_presence("form_bdOwnership")
        checkboxs = auto.driver.find_element(
            By.XPATH,
            '//*[@id="form_bdOwnership"]/table/tbody/tr/td/table/tbody/tr[2]/td/table',
        ).find_elements(By.TAG_NAME, "tr")
        for i in checkboxs:
            if data["step_22"]["checked"] in i.find_element(By.TAG_NAME, "label").text:
                i.find_element(By.TAG_NAME, "input").click()
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=22)

        # step 23
        auto.element_is_presence("form_bdTitles")
        auto.element_clicked_by_id("proprietorRadio_1")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorFirstName_1_id",
            data,
            "step_23",
            "first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorMiddleName_1_id",
            data,
            "step_23",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorLastName_1_id",
            data,
            "step_23",
            "last_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "proprietorTitle_1_id", data, "step_23", "title"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "proprietorEmail_1_id", data, "step_23", "email"
        )

        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "proprietorTelephone_1_ccode_id",
            data,
            "step_23",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorTelephone_1_acode_id",
            data,
            "step_23",
            "area_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "proprietorTelephone_1_pcode_id",
            data,
            "step_23",
            "phone_number",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=23)

        # step 24
        auto.element_is_presence("form_bdCompAddr")
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q04041_COUNTRY",
            data,
            "step_24",
            "country",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q04048_POSTAL_CODE",
            data,
            "step_24",
            "postal_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q04042_ADDRESS1",
            data,
            "step_24",
            "street_address_or_route_number_line_1",
        )
        # auto.automate_by_value(auto.element_filled_by_id,'Q04043_ADDRESS2',data,'step_24','street_address_or_route_number_line_2')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=24)

        # step 25
        auto.element_is_presence('form_B0041P040181')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=25)

        # step 26
        auto.element_is_presence('form_B0051P050261')
        auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=26)

        # step 27
        auto.element_is_presence('form_B0051P050011')

        if data['step_27']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050011S05001_Q05001_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050011S05001_Q05001_id_N')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=27)

        # step 28
        auto.element_is_presence('form_B0051P050021')

        if data['step_28']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050021S05002_Q05002_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050021S05002_Q05002_id_N')
        auto.element_clicked_by_id("menu_next_text")
        auto.update_auto_progress_with_ss(progress_id=progress_id, step=28)

        # step 29
        auto.element_is_presence('form_B0051P050111')

        if data['step_29']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050111S05011_Q05030_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050111S05011_Q05030_id_N')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=29)

        # step 30
        auto.element_is_presence('form_B0051P050221')

        if data['step_30']['checked']:
            auto.element_clicked_by_id('ansLbl_B0051P050221S05022_Q05013_id_Y')
        else:
            auto.element_clicked_by_id('ansLbl_B0051P050221S05022_Q05013_id_N')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=30)

        # step 31
        auto.element_is_presence('form_B0051P050231')

        auto.element_clicked_by_id('questionCode_B0051P050231S05023_Q05014_id_GF')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=31)

        # step 32
        auto.element_is_presence('form_B0051P050271')

        if data['step_32']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050271S05027_Q05015_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050271S05027_Q05015_id_N')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=32)

        # step 33
        auto.element_is_presence('form_B0051P050311')

        if data['step_33']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050311S05031_Q05019_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050311S05031_Q05019_id_N')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=33)

        # step 34
        auto.element_is_presence('form_B0051P050321')

        if data['step_34']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050321S05032_Q05021_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050321S05032_Q05021_id_N')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=34)

        # step 35
        auto.element_is_presence('form_B0051P050331')

        if data['step_35']['checked']:
            auto.element_clicked_by_id('questionCode_B0051P050331S05033_Q05022_id_Y')
        else:
            auto.element_clicked_by_id('questionCode_B0051P050331S05033_Q05022_id_N')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=35)

        # # step 36
        # auto.element_is_presence("form_B0051P050311")
        # if data["step_36"]["checked"]:
        #     auto.element_clicked_by_id("questionCode_B0051P050311S05031_Q05019_id_Y")
        # else:
        #     auto.element_clicked_by_id("questionCode_B0051P050311S05031_Q05019_id_N")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=36)

        # # step 37
        # auto.element_is_presence("form_B0051P050321")
        # if data["step_37"]["checked"]:
        #     auto.element_clicked_by_id("questionCode_B0051P050321S05032_Q05021_id_Y")
        # else:
        #     auto.element_clicked_by_id("questionCode_B0051P050321S05032_Q05021_id_N")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=37)

        # # step 38
        # auto.element_is_presence("form_B0051P050331")
        # if data["step_38"]["checked"]:
        #     auto.element_clicked_by_id("questionCode_B0051P050331S05033_Q05022_id_Y")
        # else:
        #     auto.element_clicked_by_id("questionCode_B0051P050331S05033_Q05022_id_N")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=38)

        # step 39
        auto.element_is_presence('form_B0051P050391')
        auto.element_clicked_by_id('questionCode_B0051P050391S05039_Q05023_id_1')
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=39)

        # step 40
        auto.element_is_presence("form_B0051P050241")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=40)

        # # step 41
        # auto.element_is_presence("form_B0061P060011")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=41)

        # # step 42
        # auto.element_is_presence("form_B0061P060121")
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060121S06061_Q06117_NON_CMV_PROP_ONLY_id",
        #     data,
        #     "step_42",
        #     "non_cmv_property",
        # )
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=42)

        # # step 43
        # auto.element_is_presence("form_B0061P060021")
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06004_Q06001_STRAIGHT_TRUCK_OWNED_id",
        #     data,
        #     "step_43",
        #     "straight_trucks",
        #     "owned",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06004_Q06002_STRAIGHT_TRUCK_TERMLEASED_id",
        #     data,
        #     "step_43",
        #     "straight_trucks",
        #     "term_leased",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06004_Q06003_STRAIGHT_TRUCK_TRIPLEASED_id",
        #     data,
        #     "step_43",
        #     "straight_trucks",
        #     "trip_leased",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06004_Q06004_STRAIGHT_TRUCK_DRIVEWAY_id",
        #     data,
        #     "step_43",
        #     "straight_trucks",
        #     "tow_driveway",
        # )

        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06042_Q06005_TRUCK_TRACTOR_OWNED_id",
        #     data,
        #     "step_43",
        #     "truck_tractors",
        #     "owned",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06042_Q06006_TRUCK_TRACTOR_TERMLEASED_id",
        #     data,
        #     "step_43",
        #     "truck_tractors",
        #     "term_leased",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06042_Q06007_TRUCK_TRACTOR_TRIPLEASED_id",
        #     data,
        #     "step_43",
        #     "truck_tractors",
        #     "trip_leased",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06042_Q06008_TRUCK_TRACTOR_DRIVEWAY_id",
        #     data,
        #     "step_43",
        #     "truck_tractors",
        #     "tow_driveway",
        # )

        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06043_Q06009_TRAILER_OWNED_id",
        #     data,
        #     "step_43",
        #     "trailers",
        #     "owned",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06043_Q06010_TRAILER_TERMLEASED_id",
        #     data,
        #     "step_43",
        #     "trailers",
        #     "term_leased",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06043_Q06011_TRAILER_TRIPLEASED_id",
        #     data,
        #     "step_43",
        #     "trailers",
        #     "trip_leased",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06043_Q06012_TRAILER_DRIVEWAY_id",
        #     data,
        #     "step_43",
        #     "trailers",
        #     "tow_driveway",
        # )

        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06044_Q06013_IEP_OWNED_id",
        #     data,
        #     "step_43",
        #     "iep_trailer_chassis_only",
        #     "owned",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06044_Q06014_IEP_TERMLEASED_id",
        #     data,
        #     "step_43",
        #     "iep_trailer_chassis_only",
        #     "term_leased",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06044_Q06015_IEP_TRIPLEASED_id",
        #     data,
        #     "step_43",
        #     "iep_trailer_chassis_only",
        #     "trip_leased",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06044_Q06016_IEP_DRIVEWAY_id",
        #     data,
        #     "step_43",
        #     "iep_trailer_chassis_only",
        #     "tow_driveway",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060021S06044_Q06080_IEP_SERVICED_id",
        #     data,
        #     "step_43",
        #     "iep_trailer_chassis_only",
        #     "serviced",
        # )
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=43)

        # # step 44
        # auto.element_is_presence("form_B0061P060071")
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060071S06007_Q06046_id",
        #     data,
        #     "step_44",
        #     "canada",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060071S06007_Q06047_id",
        #     data,
        #     "step_44",
        #     "mexico",
        # )
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=44)

        # # step 45
        # auto.element_is_presence("form_B0061P060081")
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060081S06008_Q06048_id",
        #     data,
        #     "step_45",
        #     "questionCode_B0061P060081S06008_Q06048_id",
        # )
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=45)

        # # step 46
        # auto.element_is_presence("form_B0061P060091")
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0061P060091S06009_Q06049_id",
        #     data,
        #     "step_46",
        #     "questionCode_B0061P060091S06009_Q06049_id",
        # )
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=46)

        # # step 47
        # auto.element_is_presence("form_B0061P060101")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=47)

        # # step 48
        # auto.element_is_presence("form_B0071P070011")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=48)

        # # step 49
        # auto.element_is_presence("form_B0071P070021")
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0071P070021S07002_Q07001_id",
        #     data,
        #     "step_49",
        #     "questionCode_B0071P070021S07002_Q07001_id",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0071P070021S07002_Q07002_id",
        #     data,
        #     "step_49",
        #     "questionCode_B0071P070021S07002_Q07002_id",
        # )
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=49)

        # # step 50
        # auto.element_is_presence("form_B0071P070051")
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0071P070051S07003_Q07003_id",
        #     data,
        #     "step_50",
        #     "questionCode_B0071P070051S07003_Q07003_id",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0071P070051S07003_Q07004_id",
        #     data,
        #     "step_50",
        #     "questionCode_B0071P070051S07003_Q07004_id",
        # )
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=50)

        # # step 51
        # auto.element_is_presence("form_B0071P070061")
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0071P070061S07004_Q07005_id",
        #     data,
        #     "step_51",
        #     "questionCode_B0071P070061S07004_Q07005_id",
        # )
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=51)

        # # step 52
        # auto.element_is_presence("form_B0071P070031")
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0071P070031S07005_Q07006_id",
        #     data,
        #     "step_44",
        #     "canada",
        # )
        # auto.automate_by_value(
        #     auto.element_filled_by_id,
        #     "questionCode_B0071P070031S07005_Q07007_id",
        #     data,
        #     "step_44",
        #     "mexico",
        # )
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=52)

        # # step 53
        # auto.element_is_presence("form_B0071P070041")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=53)

        # # step 54
        # auto.element_is_presence("form_B0131P130011")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=54)

        # # step 55
        # auto.element_is_presence("form_B0131P130061")
        # if data["step_55"]["checked"]:
        #     auto.element_clicked_by_id("questionCode_B0131P130061S13006_Q13007_id_Y")
        # else:
        #     auto.element_clicked_by_id("questionCode_B0131P130061S13006_Q13007_id_N")
        # auto.element_clicked_by_id("menu_next_text")

        # auto.update_auto_progress_with_ss(progress_id=progress_id, step=55)

        # step 56
        auto.element_is_presence("form_B0131P130071")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=56)

        # step 57
        auto.element_is_presence("form_B0141P140011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=57)

        # step 58
        auto.element_is_presence("form_B0141P140021")
        if data["step_58"]["checked"]:
            auto.element_clicked_by_id("questionCode_B0141P140021S14002_Q14002_id_Y")
        else:
            auto.element_clicked_by_id("questionCode_B0141P140021S14002_Q14002_id_N")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=58)

        # step 59
        auto.element_is_presence("form_B0141P140041")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=59)

        # #step 60
        auto.element_is_presence("form_B0151P150011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=60)

        # #step 61
        auto.element_is_presence("form_certificationEsign")
        auto.automate_by_value(
            auto.element_filled_by_id, "Q15002_FNAME", data, "step_61", "first_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q15007_MIDDLE_NAME",
            data,
            "step_61",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q15003_LNAME", data, "step_61", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q15005_ESIGN",
            data,
            "step_61",
            "esignature_application_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q15004_TITLE", data, "step_61", "title"
        )

        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=61)

        # #step 62
        auto.element_is_presence("form_B0161P160011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=62)

        # #step 63
        auto.element_is_presence("form_B0161P160021")
        auto.element_clicked_by_id("questionCode_B0161P160021S16002_Q16002_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=63)

        # #step 64
        auto.element_is_presence("form_B0161P160031")
        auto.element_clicked_by_id("questionCode_B0161P160031S16003_Q16003_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=64)

        # #step 65
        auto.element_is_presence("form_B0161P160041")
        auto.element_clicked_by_id("questionCode_B0161P160041S16004_Q16004_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=65)

        # #step 66
        auto.element_is_presence("form_B0161P160051")
        auto.element_clicked_by_id("questionCode_B0161P160051S16005_Q16005_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=66)

        # #step 67
        auto.element_is_presence("form_B0161P160061")
        auto.element_clicked_by_id("questionCode_B0161P160061S16006_Q16006_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=67)

        # #step 68
        auto.element_is_presence("form_B0161P160081")
        auto.element_clicked_by_id("questionCode_B0161P160081S16008_Q16008_id_Y")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=68)

        # #step 69
        auto.element_is_presence("form_B0161P160101")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0161P160101S16010_Q16010_id",
            data,
            "step_69",
            "electronic_signature_application_password",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=69)

        # #step 70
        auto.element_is_presence("form_B0161P160191")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=70)

        # #step 71
        auto.element_is_presence("form_B0171P170011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=71)

        # #step 72
        auto.element_is_presence("form_applicantsOathEsign")
        auto.automate_by_value(
            auto.element_filled_by_id, "Q17002_FNAME", data, "step_61", "first_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q17007_MIDDLE_NAME",
            data,
            "step_61",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q17003_LNAME", data, "step_61", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q17005_ESIGN",
            data,
            "step_61",
            "esignature_application_password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q17004_TITLE", data, "step_61", "title"
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=72)

        # #step 73
        auto.element_is_presence("form_B0231P230011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=73)

        # #step 74
        auto.element_is_presence("form_B0231P230021")
        if data["step_74"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0231P230021S23002_Q23002_COMP_CONTACT_NME_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0231P230021S23002_Q23002_COMP_CONTACT_NME_id_N"
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=74)

        # #step 75
        auto.element_is_presence("form_B0231P230041")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23012_USERID_id",
            data,
            "step_75",
            "user_id",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23013_PASSWORD_id",
            data,
            "step_75",
            "password",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23014_PASSWORD_VERIFY_id",
            data,
            "step_75",
            "password",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "questionCode_B0231P230041S23004_Q23034_COMP_OFF_PREF_CONT_METHOD_id",
            data,
            "step_75",
            "method_of_contact",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23038_COMP_OFF_EMAIL_id",
            data,
            "step_75",
            "email",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "questionCode_B0231P230041S23004_Q23039_COMP_OFF_EMAIL_CFM_id",
            data,
            "step_75",
            "email",
        )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=75)

        # #step 76
        auto.element_is_presence("form_B0231P230091")
        if data["step_76"]["checked"]:
            auto.element_clicked_by_id(
                "questionCode_B0231P230091S23009_Q23041_SEC_QUES_NEW_SET_id_Y"
            )
        else:
            auto.element_clicked_by_id(
                "questionCode_B0231P230091S23009_Q23041_SEC_QUES_NEW_SET_id_N"
            )
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=76)

        # #step 77
        auto.element_is_presence("form_companyRob")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=77)

        # #step 78
        auto.element_is_presence("form_rob")
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23022_ROB_FNAME", data, "step_78", "first_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q23041_ROB_MNAME",
            data,
            "step_78",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23023_ROB_LNAME", data, "step_78", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23024_ROB_TITLE", data, "step_78", "title"
        )
        auto.element_clicked_by_id("Q23025_ROB_CNFM")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=78)

        # #step 79
        auto.element_is_presence("form_companyRoles")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=79)

        # #step 80
        auto.element_is_presence("form_roleResponsibility")
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q23027_RESP_FNAME",
            data,
            "step_80",
            "first_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q23043_RESP_MNAME",
            data,
            "step_80",
            "middle_name",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23028_RESP_LNAME", data, "step_80", "last_name"
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q23029_RESP_TITLE", data, "step_80", "title"
        )
        auto.element_clicked_by_id("Q23030_RESP_CNFM")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=80)

        # #step 81
        auto.element_is_presence("form_B0181P180011")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=81)

        # step 82
        auto.element_is_presence("form_B0181P180021")
        auto.element_clicked_by_id("menu_next_text")

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=82)

        # #step 83
        auto.element_is_presence("form_paymentInfo")
        if data["step_83"]["card"] == "vi":
            auto.element_clicked_by_id("Q18007_CREDIT_CARD_TYPEVisa")
        elif data["step_83"]["card"] == "mc":
            auto.element_clicked_by_id("Q18007_CREDIT_CARD_TYPEMasterCard")
        elif data["step_83"]["card"] == "ax":
            auto.element_clicked_by_id("Q18007_CREDIT_CARD_TYPEAmex")
        else:
            auto.element_clicked_by_id("Q18007_CREDIT_CARD_TYPEDiscover")

        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q18008_CREDIT_CARD_NUM",
            data,
            "step_83",
            "credit_card_number",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q18009_CREDIT_CARD_EXP_MM",
            data,
            "step_83",
            "choose_exp_month",
        )
        auto.automate_by_value(
            auto.element_filled_enter_by_id,
            "Q18010_CREDIT_CARD_EXP_YY",
            data,
            "step_83",
            "choose_exp_year",
        )
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q18011_CC_SECURITY_CODE",
            data,
            "step_83",
            "security_code",
        )
        auto.automate_by_value(
            auto.element_filled_by_id, "Q18012_CC_FNAME", data, "step_83", "first_name"
        )
        # auto.automate_by_value(auto.element_filled_by_id,'Q18017_CC_MNAME',data,'step_83','middle_name')
        auto.automate_by_value(
            auto.element_filled_by_id, "Q18016_CC_LNAME", data, "step_83", "last_name"
        )
        # auto.automate_by_value(auto.element_filled_by_id,'Q18____CC_SUFFIX',data,'step_83','suffix')
        auto.automate_by_value(
            auto.element_filled_by_id,
            "Q18013_CC_ESIGN",
            data,
            "step_83",
            "electronic_signature_application_password",
        )
        # auto.element_clicked_by_id('menu_next_text')

        auto.update_auto_progress_with_ss(progress_id=progress_id, step=83)
        auto.element_clicked_by_id("dijit_form_Button_4")

        # step 84
        auto.element_is_presence("form_B0181P180041")
        paymentMsg = auto.element_value_by_id("questionDesc_Q18015")
        auto.update_auto_progress_with_ss(progress_id=progress_id, step=84)

        if paymentMsg:
            intList = re.findall(r"\b\d+\b", paymentMsg.text)
            if intList:
                usdot = int(intList[1])
                print(usdot)
                auto.update_company_usdot(usdot)

        auto.complete_auto_progress()
        time.sleep(5)
        auto.driver.quit()
        print("automation complete ---")

    except Exception as e:
        auto.driver.quit()
        print(e)

    finally:
        auto.driver.quit()
        print("driver quit")

    return True


# data = {
#     "step_9": {
#         "create_password": "Password@1234",
#         "confirm_password": "Password@1234",
#         "security_question_1": "What was my high school mascot?",
#         "security_answer_1": "bear",
#         "security_question_2": "What is my least favorite vegetable?",
#         "security_answer_2": "ford",
#         "security_question_3": "What is my pet name?",
#         "security_answer_3": "baby",
#     },
#     "step_11": {
#         "application_contact_type": "Applicant Representative",
#         "application_contact_first_name": "Toderai",
#         "application_contact_last_name": "Tarima",
#         "application_contact_title": "owner",
#         "application_contact_country": "United States",
#         "application_contact_street_address_line_1": "52 elm street APT#2",
#         "application_contact_postal_code": "03766",
#         "application_contact_telephone_number": {
#             "country_code": "United States",
#             "area_code": "603",
#             "phone_number": "266-9040",
#             "extra_phone_number": "",
#         },
#         "application_contact_email_address": "tonderaitarima@gmail.com",
#         "application_contact_confirm_email_address": "tonderaitarima@gmail.com",
#         "application_contact_preferred_contact_method": "US Mail",
#     },
#     "step_13": {"checked": False},
#     "step_14": {"legal_business_name": "Tarima Logistics LLC"},
#     "step_16": {"checked": True},
#     "step_17": {"mailing_address_sameas_principal": True},
#     "step_18": {
#         "country": "United States",
#         "area_code": "603",
#         "phone_number": "266-9040",
#     },
#     "step_19": {"ein": "873540999"},
#     "step_20": {"checked": False},
#     "step_21": {
#         "checked": "Corporation (State of Incorporation)",
#         "choose_one": "NEW HAMPSHIRE",
#     },
#     "step_22": {"checked": "Owned/controlled by citizen of United States"},
#     "step_23": {
#         "company_contact_1_checked": True,
#         "first_name": "Toderai",
#         "last_name": "Tarima",
#         "title": "owner",
#         "email": "tonderaitarima@gmail.com",
#         "country": "United States",
#         "area_code": "603",
#         "phone_number": "266-9040",
#     },
#     "step_24": {
#         "country": "United States",
#         "street_address_or_route_number_line_1": "52 elm street APT#2",
#         "postal_code": "03766",
#         "blank_click": True,
#     },
#     "step_27": {"checked": False},
#     "step_28": {"checked": True},
#     "step_29": {"checked": True},
#     "step_30": {"checked": "Other Non-Hazardous Freight"},
#     "step_31": {"checked": True},
#     "step_32": {"checked": False},
#     "step_33": {"checked": False},
#     "step_34": {"checked": False},
#     "step_35": {"checked": False},
#     "step_36": {"checked": False},
#     "step_37": {"checked": False},
#     "step_38": {"checked": False},
#     "step_39": {"checked": "General Freight"},
#     "step_42": {"non_cmv_property": 0},
#     "step_43": {
#         "straight_trucks": {
#             "owned": 1,
#             "term_leased": 0,
#             "trip_leased": 0,
#             "tow_driveway": 0,
#         },
#         "truck_tractors": {
#             "owned": 0,
#             "term_leased": 0,
#             "trip_leased": 0,
#             "tow_driveway": 0,
#         },
#         "trailers": {"owned": 0, "term_leased": 0, "trip_leased": 0, "tow_driveway": 0},
#         "iep_trailer_chassis_only": {
#             "owned": 0,
#             "term_leased": 0,
#             "trip_leased": 0,
#             "tow_driveway": 0,
#             "serviced": 0,
#         },
#     },
#     "step_44": {"canada": 0, "mexico": 0},
#     "step_45": {"questionCode_B0061P060081S06008_Q06048_id": 1},
#     "step_46": {"questionCode_B0061P060091S06009_Q06049_id": 0},
#     "step_49": {
#         "questionCode_B0071P070021S07002_Q07001_id": 1,
#         "questionCode_B0071P070021S07002_Q07002_id": 0,
#     },
#     "step_50": {
#         "questionCode_B0071P070051S07003_Q07003_id": 0,
#         "questionCode_B0071P070051S07003_Q07004_id": 0,
#     },
#     "step_51": {"questionCode_B0071P070061S07004_Q07005_id": 0},
#     "step_52": {"canada": 0, "mexico": 0},
#     "step_55": {"checked": True},
#     "step_58": {"checked": False},
#     "step_61": {
#         "first_name": "Toderai",
#         "last_name": "Tarima",
#         "esignature_application_password": "Password@1234",
#         "title": "owner",
#     },
#     "step_69": {"electronic_signature_application_password": "Password@1234"},
#     "step_72": {
#         "first_name": "Toderai",
#         "last_name": "Tarima",
#         "esignature_application_password": "Password@1234",
#         "title": "owner",
#     },
#     "step_74": {"checked": True},
#     "step_75": {
#         "user_id": "tonderaitarima@gmail.com",
#         "email": "tonderaitarima@gmail.com",
#         "password": "Password@1234",
#         "method_of_contact": "US Mail",
#     },
#     "step_76": {"checked": True},
#     "step_78": {
#         "first_name": "Toderai",
#         "last_name": "Tarima",
#         "title": "owner",
#         "checked": True,
#     },
#     "step_80": {
#         "first_name": "Toderai",
#         "last_name": "Tarima",
#         "title": "owner",
#         "checked": True,
#     },
#     "step_83": {
#         "card": "vi",
#         "credit_card_number": "4427427069919779",
#         "choose_exp_month": "NOV",
#         "choose_exp_year": "2026",
#         "security_code": "493",
#         "first_name": "Registration",
#         "last_name": "llc",
#         "electronic_signature_application_password": "Password@1234",
#     },
# }
