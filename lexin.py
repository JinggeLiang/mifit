import requests
import json
import time
import random

from hashlib import md5


class LeXin:
    def __init__(self, user, password, steps, sc_key=""):
        self.user = str(user)
        self.password = str(password)
        self.steps = random.randint(int(steps) - 2000, int(steps) + 2000)
        self.sc_key = sc_key

        self.login_url = "https://sports.lifesense.com/sessions_service/login?" \
                         "platform=android&systemType=2&version=4.6.7"
        self.step_url = "https://sports.lifesense.com/sport_service/sport/sport/uploadMobileStepV2?" \
                        "version=4.5&systemType=2"
        self.user_agent = "Dalvik/2.1.0 (Linux; U; Android 9; SM-G9500 Build/PPR1.180610.011)"
        self.band_ids = ["http://we.qq.com/d/AQC7PnaOelOaCg9Ux8c9Ew95yumTVfMcFuGCHMY-",
                         "http://we.qq.com/d/AQC7PnaOi9BLVrfJIiVTU8ENIbv_9Lmlqia1ToGc",
                         "http://we.qq.com/d/AQC7PnaOXQhy3VvzFeP5bZMKmAQrGE6NJWdK3Xnk",
                         "http://we.qq.com/d/AQC7PnaOaEXBdhkdXQvTRE1CO1fIqBuitbSSGt2r",
                         "http://we.qq.com/d/AQC7PnaOdI9h0tfCr0KRlb78ISAE9qcaZ3btHrJE",
                         "http://we.qq.com/d/AQC7PnaOsThRYksmQcvpa0klKFrupqaqKyEPm8nj",
                         "http://we.qq.com/d/AQC7PnaOk8V-FV7R4ix61GToC5fh5I151hvlsNf6",
                         ]
        self.bind_msg = ''

    def get_id_token(self):
        header_login = {'Content-Type': 'application/json; charset=utf-8',
                        'Accept-Encoding': 'gzip',
                        'User-Agent': self.user_agent
                        }
        data_org_login = {"appType": 6, "clientId": md5(self.user.encode(encoding="utf-8")).hexdigest(), "loginName":
                          self.user, "password": md5(self.password.encode(encoding="utf-8")).hexdigest(), "roleType": 0}
        data_login = json.dumps(data_org_login)
        resp_data = json.loads(requests.post(url=self.login_url, data=data_login, headers=header_login).text)
        uid = resp_data['data']['userId']
        token = resp_data['data']['accessToken']
        return uid, token

    def bind_device(self, uid, token):
        bind_url = "https://sports.lifesense.com/device_service/device_user/bind"
        band_id = random.choice(self.band_ids)
        bind_org_data = {
                        "qrcode": band_id,
                        "userId": int(uid)
                        }
        bind_data = json.dumps(bind_org_data)
        bind_header = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Cookie": "accessToken=" + token,
                    "User-Agent": self.user_agent
                    }
        bind_result = requests.post(url=bind_url, data=bind_data, headers=bind_header)
        self.bind_msg = json.loads(bind_result.text)['msg']
        time.sleep(5)

    def update_steps(self):
        uid, token = self.get_id_token()
        header_step = {'Cookie': 'accessToken=' + token,
                       'Content-Type': 'application/json; charset=utf-8'
                       }
        data_org_step = {"list": [{"DataSource": 2,
                                   "active": 1,
                                   "calories": str(int(self.steps // 20)),
                                   "dataSource": 2,
                                   "deviceId": "M_NULL",
                                   "distance": int(self.steps / 3),
                                   "exerciseTime": 0,
                                   "isUpload": 0,
                                   "measurementTime": time.strftime("%Y-%m-%d %H:%M:%S",
                                                                    time.localtime(int(time.time()))),
                                   "priority": 0,
                                   "step": self.steps,
                                   "type": 2,
                                   "updated": float(str(time.time()).split(".")[0])
                                               + float(str(time.time()).split(".")[1][:3]),
                                   "userId": uid}]
                         }
        data_step = json.dumps(data_org_step)
        time.sleep(3)
        result = json.loads(requests.post(url=self.step_url, data=data_step, headers=header_step).text)
        data = list(set(result['data']['pedometerRecordHourlyList'][0]['step'].split(",")))

        for i in range(len(data)):
            data[i] = int(data[i])

        self.steps = max(data) if self.steps < max(data) else self.steps
        msg = f"手机号:{self.user}, 当前步数:{self.steps}, 绑定情况:{self.bind_msg}"
        print(msg)
        if self.sc_key:
            self.push_wx(self.sc_key, msg)

    def push_wx(self, sc_key, desp=""):
        """
        推送消息到微信
        """
        server_url = f"https://sc.ftqq.com/{sc_key}.send"
        params = {
            "text": f'乐心健康 步数修改 {self.user}',
            "desp": desp
        }

        response = requests.get(server_url, params=params)
        json_data = response.json()

        if json_data['errno'] == 0:
            print(f"推送成功。")
        else:
            print(f"推送失败：{json_data['errno']}({json_data['errmsg']})")


if __name__ == '__main__':
    user = input()
    password = input()
    steps = input()
    sc_key = input()
    lx = LeXin(user, password, steps, sc_key)
    # lx.bind_device(*(lx.get_id_token()))  # 未绑定手环需要先绑定
    lx.update_steps()
