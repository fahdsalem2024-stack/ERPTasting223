from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from utils.logger import logger
from config.settings import LOGIN_URL
import time


class LoginPage(BasePage):
    USERNAME_INPUT = (By.ID, "userName")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button.btn-login")

    def load(self):
        self.open(LOGIN_URL)

    def enter_username(self, username: str):
        self.type_text(self.USERNAME_INPUT, username, "اسم المستخدم")
        time.sleep(3)

    def enter_password(self, password: str):
        self.type_text(self.PASSWORD_INPUT, password, "كلمة المرور")
        time.sleep(0.5)

    def click_login(self):
        self.click(self.LOGIN_BUTTON, "زر تسجيل الدخول")

    def login(self, username: str, password: str):
        logger.info("=" * 50)
        logger.info("بدء تسجيل الدخول")
        logger.info("=" * 50)

        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

        logger.info("في انتظار التحويل...")
        try:
            WebDriverWait(self.driver, 45).until(
                lambda d: "/Login" not in d.current_url
            )
            logger.success(f"تم الدخول! URL: {self.driver.current_url}")
            time.sleep(2)
            self.take_screenshot("login_success")
        except TimeoutException:
            self.take_screenshot("ERROR_login_failed")
            logger.error(f"فشل التحويل! URL: {self.driver.current_url}")
            raise

    def is_logged_in(self):
        return "/Login" not in self.driver.current_url
