from selenium.webdriver.remote.webdriver import WebDriver as wd
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wdw
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
import selenium
from bs4 import BeautifulSoup 
import json
from selenium.webdriver.chrome.options import Options
import re
import time

class WebVPN:
    def __init__(self, opt: dict, headless=False):
        self.root_handle = None
        self.driver: wd = None
        self.userid = opt["username"]
        self.passwd = opt["password"]
        self.headless = headless

    def login_webvpn(self):
        """
        Log in to WebVPN with the account specified in `self.userid` and `self.passwd`

        :return:
        """
        d = self.driver
        if d is not None:
            d.close()
        chrome_options = Options()
        chrome_options.page_load_strategy = 'eager'
        d = selenium.webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=chrome_options)
        d.get("https://webvpn.tsinghua.edu.cn/login")
        username = d.find_elements(By.XPATH,
                                   '//div[@class="login-form-item"]//input'
                                   )[0]
        password = d.find_elements(By.XPATH,
                                   '//div[@class="login-form-item password-field" and not(@id="captcha-wrap")]//input'
                                   )[0]
        username.send_keys(str(self.userid))
        password.send_keys(self.passwd)
        d.find_element(By.ID, "login").click()
        self.root_handle = d.current_window_handle
        self.driver = d
        return d

    def access(self, url_input):
        """
        Jump to the target URL in WebVPN

        :param url_input: target URL
        :return:
        """
        d = self.driver
        url = By.ID, "quick-access-input"
        btn = By.ID, "go"
        wdw(d, 5).until(EC.visibility_of_element_located(url))
        actions = AC(d)
        actions.move_to_element(d.find_element(*url))
        actions.click()
        actions.\
            key_down(Keys.CONTROL).\
            send_keys("A").\
            key_up(Keys.CONTROL).\
            send_keys(Keys.DELETE).\
            perform()

        d.find_element(*url)
        d.find_element(*url).send_keys(url_input)
        d.find_element(*btn).click()

    def switch_another(self):
        """
        If there are only 2 windows handles, switch to the other one

        :return:
        """
        d = self.driver
        assert len(d.window_handles) == 2
        wdw(d, 5).until(EC.number_of_windows_to_be(2))
        for window_handle in d.window_handles:
            if window_handle != d.current_window_handle:
                d.switch_to.window(window_handle)
                return

    def to_root(self):
        """
        Switch to the home page of WebVPN

        :return:
        """
        self.driver.switch_to.window(self.root_handle)

    def close_all(self):
        """
        Close all window handles

        :return:
        """
        while True:
            try:
                l = len(self.driver.window_handles)
                if l == 0:
                    break
            except selenium.common.exceptions.InvalidSessionIdException:
                return
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.close()

    def login_info(self):
        """
        TODO: After successfully logged into WebVPN, login to info.tsinghua.edu.cn

        :return:
        """
        d = self.driver
        self.switch_another()
        
        # 等待页面加载，然后输入账号密码，跳转
        username = By.XPATH, '//*[@id="userName"]'
        wdw(d, 5).until(EC.visibility_of_element_located(username))

        username = d.find_element(By.ID,'userName')
        passwd = d.find_element(By.NAME, 'password')
        username.send_keys(self.userid)
        passwd.send_keys(self.passwd)

        login_button = d.find_element(By.XPATH, '/html/body/table[2]/tbody/tr/td[3]/table/tbody/tr/td[6]/input')
        login_button.click()
        # print(self.driver.page_source)
        # 判断登录成功的依据
        if (self.driver.page_source.find('正在登录') == -1):
            print('login failed')
        else:
            temp = By.XPATH, '//*[@id="header"]/div/div/div[1]/div[1]/span'
            wdw(d, 5).until(EC.visibility_of_element_located(temp))
            return 
        # Hint: - Use `access` method to jump to info.tsinghua.edu.cn
        #       - Use `switch_another` method to change the window handle
        #       - Wait until the elements are ready, then preform your actions
        #       - Before return, make sure that you have logged in successfully
        raise NotImplementedError

    def get_grades(self):
        """
        TODO: Get and calculate the GPA for each semester.
        

        Example return / print:
            2020-秋: *.**
            2021-春: *.**
            2021-夏: *.**
            2021-秋: *.**
            2022-春: *.**

        :return:
        """
        d = self.driver
        self.to_root()
        self.access('zhjw.cic.tsinghua.edu.cn/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw')
        d.switch_to.window(d.window_handles[2])
        time.sleep(3)
        # 找到储存成绩表的元素
        content = d.find_element(By.ID, 'table1').get_attribute('innerHTML')
        self.close_all()
        self.parse_grade(content)
        # print(content)


        # with open('source.html','w') as f:
        #     f.write(d.page_source)
        # query_grade = d.find_element(By.XPATH, '//*[@id="menu"]/li[2]/div[6]/div[3]/div/dl/dt[1]/a')
        # print(query_grade.get_property('herf'))

        # pattern = '教学建议</a><div class="clear"></div><a target="_blank" class="left" href="(.*?)">全部成绩'
        # link = re.findall(pattern,d.page_source)[0]
        # print(link)
        # # print(link)
        # d.get(link)
        # query_grade.click()


        return 
        # Hint: - You can directly switch into
        #         `zhjw.cic.tsinghua.edu.cn/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw`
        #         after logged in
        #       - You can use Beautiful Soup to parse the HTML content or use
        #         XPath directly to get the contents
        #       - You can use `element.get_attribute("innerHTML")` to get its
        #         HTML code

        # raise NotImplementedError
    def parse_grade(self, content):
        '''parse html str, then output the GPA of each term
        
        '''
        soup = BeautifulSoup(content,features="html.parser")
        tr_list = soup.find_all('tr')
        sum = 0
        # 计算总学分，总成绩
        grade_sum = {}
        point_sum = {}
        for x in range(1,len(tr_list)): # 初始化
            td_list = tr_list[x].find_all('td')
            seme = td_list[5].string
            pattern = '(2.*?)\n'
            seme = re.findall(pattern, seme)[0]
            grade_sum[seme] = 0
            point_sum[seme] = 0


        for x in range(1,len(tr_list)):
            td_list = tr_list[x].find_all('td')
            if ((td_list[3].string).find('P') != -1): # 处理pf课
                continue

            point = int(td_list[2].string)
            grade = point * float(td_list[4].string)
            seme = td_list[5].string
            pattern = '(2.*?)\n'
            seme = re.findall(pattern, seme)[0]
            grade_sum[seme] += grade
            point_sum[seme] += point
        for x in grade_sum:
            output = x + ':' + str(grade_sum[x] / point_sum[x])
            print(output)

opt = None
try:
    with open('settings.json','r') as f:
        temp = f.read()
        opt = json.loads(temp)
except:
    print('Failed to open config file.')
wb = WebVPN(opt)

wb.login_webvpn()

wb.access('http://info.tsinghua.edu.cn')

wb.login_info()

wb.get_grades()







