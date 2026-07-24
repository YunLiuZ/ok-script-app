import re

from src.tasks.BaseBattleTask import BaseBattleTask

from datetime import datetime

class GameEventsBattleTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "战斗-活动"
        self.count = 0

        self.isap = True

        self.ap_tickets = 0
        self.general_tickets = 0

        self.default_config.update({
            "ApMode": True,
            "GeneralClimb": True,
        })
        self.config_description.update({
            "AttackNumber": "挂体力的次数",

        })

    def run(self):
        # self.SwitchSoul_by_num(int(self.config["Preset Group"]),int(self.config["Preset Team"]))
        # self.reset()
        self.in_home_and_back()
        self.Battle_page()
        self.Battle()

    def Battle_page(self):
        self.click_relative(0.34,0.25,after_sleep=2)
        if text:=self.ocr_and_click(['砂影','迷城','战斗'],1,
                                    box=self.box_of_screen(0.78, 0.17, 0.87, 0.53)):
            print(text)


    def Battle(self):
        self.ocr_and_click("式神",box=self.box_of_screen(0.65,0.82,0.84,0.9))
        if self.wait_ocr(match=re.compile("养成|协战|式神"),
                         time_out=3,
                         box=self.box_of_screen(0.65,0.82,0.84,0.9)):
            self.sleep(0.5)
            if text:=self.ocr(match=re.compile("必定|双倍|掉落"),
                             box=self.box_of_screen(0.01, 0.75, 0.32, 0.88)):
                print(text)
                self.log_info("现在是体力模式")
                self.isap = True
            else:
                print(text)
                self.log_info("现在是爬塔模式")
                self.isap = False
        else:
            self.log_warning("没有进入战斗页面")
            return False

        if text := self.ocr(threshold=0.8,box=self.box_of_screen(0.47, 0.02, 0.52, 0.07)):
            nums = re.findall(r'\d+', text[0].name)
            self.general_tickets = int(nums[0]) if nums else 0
            self.log_info(f"爬塔票数：{self.general_tickets}")

        if text := self.ocr(threshold=0.8,box=self.box_of_screen(0.61, 0.02, 0.67, 0.07)):
            nums = re.findall(r'\d+', text[0].name)
            self.ap_tickets = int(nums[0]) if nums else 0
            self.log_info(f"体力的票数{self.ap_tickets}")
        if self.Lock_team((0.61, 0.89, 0.66, 0.97)):
                self.log_info("锁上了")
        else:
            self.log_info("没锁")

        if self.config["GeneralClimb"]:
            self.count = 1
            if self.isap:
                self.click_relative(0.98,0.77)
                self.log_info("切换为爬塔")
                self.isap = False
                self.sleep(0.5)
            else:
                self.log_info("爬塔")
            while self.count < self.general_tickets:
                self.Battle_process()
                self.count += 1
                self.log_info(f"第 {self.count} 次爬塔战斗结束 总共{self.general_tickets}")

        if self.config["ApMode"]:
            self.count=1
            if not self.isap:
                self.click_relative(0.98, 0.77)
                self.log_info("切换为刷体力")
                self.isap = True
                self.sleep(0.5)
            else:
                self.log_info("体力")
            num = self.config["AttackNumber"] if (self.config["AttackNumber"] < self.ap_tickets) else self.ap_tickets
            while self.count < num:
                self.Battle_process()
                self.count += 1
                self.log_info(f"第 {self.count} 次体力爬塔战斗结束 总共{num}")
        self.Back_Home()


    def Battle_process(self):
        def check():
            if res := self.find_one('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish')):
                self.click(res)
                self.sleep(2)
                if res1 := self.find_one('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish')):
                    self.click(res1)
                    self.sleep(0.5)
                    self.log_info("第一次没点到")
                    return True
                else:
                    self.log_info("第一次点到")
                    return True
            if res := self.find_one('Battle_Finish_Soul', threshold=0.7,
                                        box=self.B('Battle_Finish_Soul')):
                self.click(res)
                self.sleep(1)
                if res1 := self.find_one('Battle_Finish_Soul', threshold=0.7,
                                        box=self.B('Battle_Finish_Soul')):
                    self.click(res1)
                    self.log_info("第一次没点到")
                    self.sleep(1)
                    return True
                else:
                    self.log_info("第一次点到")
                    return True

        if text := self.wait_click_ocr(match=re.compile("挑战"),box=self.box_of_screen(0.88,0.83,0.95,0.91)):
                print(text)
        if self.count == 1:
            self.change_auto()

        if self.wait_until(check, time_out=self.config["BattleTime"], raise_if_not_found=False):
            return True

        
