import re

from src.tasks.BaseOmjTask import BaseOmjTask


class OrchidsTask(BaseOmjTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "日常-同心之兰"
        self.description = "好友互送礼物30勾玉，使用前请至少保证有30勾玉"

        self.default_config.update({
            "First": True,
            "Friend 1": "",
        })
        self.config_description.update({
            "Friend 1": "在使用之前，请给好友发个消息，保证好友在最近列表，同心之兰队友",
        })

    def run(self):
        self.in_home_and_back()
        if self.config["First"]:
            self.log_info("，开始邀请")
            self.Orchids()
            self.sleep(2)
            self.log_info("等待邀请")
            if self.wait_click_feature('Invitation_Confirm', threshold=0.7,
                                       box=self.B('Invitation_Confirm'),
                                       raise_if_not_found=False, time_out=10, after_sleep=1):
                self.log_info("完成邀请")
                return True
        else:
            if self.wait_click_feature('Invitation_Confirm', threshold=0.7,
                                       box=self.B('Invitation_Confirm'),
                                       raise_if_not_found=False, time_out=10, after_sleep=1):
                if self.Orchids():
                    self.log_info("完成邀请")
                    return True
            else:
                self.log_info("没接收到邀请")
    def Orchids(self):
        if not self.wait_click_feature('Home_Friend', threshold=0.7,
                                       box=self.box_of_screen(0.66, 0.82, 0.76, 0.97),
                                       raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Friend")
        if self.wait_ocr(match=re.compile('提升|羁绊提'),
                         box=self.box_of_screen(0.34, 0.09, 0.64, 0.25),
                         time_out=3):
            self.wait_click_feature('Daily_New_Cancel', threshold=0.7,
                                       box=self.box_of_screen(0.86, 0.07, 0.94, 0.2),
                                       raise_if_not_found=False, time_out=3, after_sleep=1)
            self.log_info("关闭弹窗")
        if not (text := self.ocr_and_click(['最近'], 1,
                                           box=self.box_of_screen(0.20, 0.13, 0.27, 0.19))):
            self.log_info('找不到最近页面')
        if not (text := self.ocr_and_click(self.config["Friend 1"], 1,
                                           box=self.box_of_screen(0.16, 0.22, 0.28, 0.82))):
            self.log_info('找不到好友')
        if not self.wait_click_feature('Orchids', threshold=0.7,
                                       box=self.box_of_screen(0.8383, 0.141, 0.8852, 0.2313),
                                       raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到同心之兰")
        if self.wait_ocr(match=re.compile('福袋'),time_out=3,threshold=0.7,
                         box=self.box_of_screen(0.23, 0.2, 0.36, 0.28)):
            self.click_relative(0.7,0.87)
            self.sleep(1)
            self.click_relative(0.2,0.2)
            self.sleep(1)
        else:
            self.log_warning("没找到福袋")
        if not self.wait_click_feature('Cancel_Old', threshold=0.7,
                                       box=self.box_of_screen(0.85, 0.08, 0.99, 0.25),
                                       raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("没有正确的进入关闭好友的流程")
        if self.In_Home():
            return True
        else:
            return False



