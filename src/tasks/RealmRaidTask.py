import re

from src.tasks.BaseBattleTask import BaseBattleTask
from datetime import datetime, timedelta
class RealmRaidTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "日常-战斗-个人、寮突破"
        self.trigger_count = 1
        self.count = 1
        self.tickets = 0
        self.forward = True
        self.default_config.update({
            "Tickets": 1,
            "RealmRaid":True,
            "RyouToppa":False,
            "RealmRaid_Team":"1,1",
            "RyouToppa_Team": "1,1",
        })
        self.config_description.update({
            "Tickets": "至少有多少张票才去挑战个人突破",
            "AttackNumber":"对于结界突破无需填写",
            "RealmRaid_Team": "个人突破的队伍预设",
            "RyouToppa_Team": "寮突破的队伍预设",
        })
    def run(self):
        self.in_home_and_back()
        if not (self.config["RealmRaid"] or self.config["RyouToppa"]):
            self.log_warning("没有选择任何突破")
            self.Back_Home()
            return True
        print(f"{self.config["RealmRaid"]},{self.config["RyouToppa"]}")

        if self.config["RealmRaid"]:
            if self.config["Preset Enable"]:
                group, team = self._parse_preset(self.config["RealmRaid_Team"])
                self.SwitchSoul_by_num(group, team)
            if not self.RealmRaid_page():
                self.log_warning("找不到结界页面")
                return False
            if not self.realmraid_battle():
                self.log_warning("个人突破失败")
                return False
            self.wait_click_feature("Cancel_Old",time_out=3,
                                    threshold=0.8,
                                    box=self.box_of_screen(0.91, 0.13, 0.97, 0.23),
                                    raise_if_not_found=False)
            self.Back_Home()
            self.sleep(1)

        if self.config["RyouToppa"]:
            if self.config["RealmRaid"]:
                if self.config["RyouToppa_Team"] != self.config["RealmRaid_Team"]:
                    if self.config["Preset Enable"]:
                        group, team = self._parse_preset(self.config["RyouToppa_Team"])
                        self.SwitchSoul_by_num(group, team)
            else:
                if self.config["RealmRaid"]:
                    group, team = self._parse_preset(self.config["RyouToppa_Team"])
                    self.SwitchSoul_by_num(group, team)

            if not self.RealmRaid_page():
                self.log_warning("找不到结界页面")
                return False
            self.log_info("111111111111111111111111111111111111")
            if self.wait_click_ocr(match=re.compile("阴阳"),
                                box=self.box_of_screen(0.93, 0.33, 1.0, 0.7)):
                self.sleep(0.5)
                self.log_info("111111111111111111111111111111111111")
                if not self.ryoutoppa_battle():
                    self.log_warning("寮突破失败")
                    return False
        return True
        
    def RealmRaid_page(self):
        if not self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=6, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        self.info_set("步骤", "进入探索页面")

        if self.wait_click_feature('Exploration_RealmRaid', threshold=0.7,
                                        box=self.B('bottom'),
                                        raise_if_not_found=False, time_out=6, after_sleep=1):
            self.log_info("探索 RealmRaid")
            self.info_set("步骤", "进入RealmRaid")

        if self.wait_ocr(match=re.compile("结界|突破"),
                                   time_out=6,
                                   box=self.box_of_screen(0.43, 0.08, 0.57, 0.18)):
            self.log_info("进入突破页面")
            return True
        else:
            self.log_info('找不到突破')
            return False

    def realmraid_battle(self):
        if text := self.wait_ocr(threshold=0.8,box=self.box_of_screen(0.89,0.02,0.95,0.1),
                                 time_out=6):
            nums = re.findall(r'\d+', text[0].name)
            self.tickets = int(nums[0]) if nums else 0
            self.log_info(f"{self.tickets}")
            if self.tickets > self.config["Tickets"]:
                self.log_info("开打开打")
            else:
                self.log_info("票数不够")
                return False
        self.log_info("进入battle")
        self.count = 1
        group_rows = {
            1: (0.23, 0.27),  # (594, 395)
            2: (0.50, 0.27),  # (1300, 398)
            3: (0.76, 0.27),  # (1951, 398)
            4: (0.23, 0.46),  # (613, 665)
            5: (0.51, 0.46),  # (1315, 662)
            6: (0.77, 0.46),  # (1980, 669)
            7: (0.23, 0.65),  # (609, 939)
            8: (0.50, 0.65),  # (1296, 939)
            9: (0.77, 0.65),  # (1973, 939)
        }
        group_rows_2 = [
            (0.25, 0.50, 0.35, 0.57),  # (x1, y1, x2, y2) 相对
            (0.51, 0.50, 0.61, 0.57),
            (0.78, 0.50, 0.87, 0.57),

            (0.25, 0.69, 0.35, 0.77),
            (0.51, 0.69, 0.61, 0.77),
            (0.78, 0.69, 0.87, 0.77),

            (0.25, 0.87, 0.35, 0.95),
            (0.51, 0.87, 0.61, 0.95),
            (0.78, 0.87, 0.87, 0.95),]
            
    


        res = self.find_feature("Real_Raid_Finish",box=self.box_of_screen(0.11,0.20,0.88,0.73),threshold=0.7)
        lens = len(res)
        print(lens)
        

        # 判断方向：lens=0 默认正着；
        if lens > 0:
            ys = [b.y for b in res]
            print(ys)
            self.forward = sum(ys) / len(ys) < self.frame.shape[0] * 0.43  # 偏上=正着，偏下=倒着
        else:
            self.forward = True

        # 留至少1个，lens 永远 ≥ 1
        if  (lens + self.tickets) % 9 != 0:
            attack_num = self.tickets
        else:
            attack_num = self.tickets - 1
        
        self.log_info(f"方向={'正' if self.forward else '倒'} lens={lens} tickets={self.tickets} 本轮打{attack_num}次")
        self.count = (lens + 1)
        if lock_res := self.Lock_team((0.50,0.70,0.70,0.90)):
                self.log_info("锁上了")
        else:
            self.log_info("没锁")

        while(attack_num):
            target = self.count if self.forward else (10 - self.count)
            x, y = group_rows[target]

            #退四
            if(self.forward and self.count == 9):
                for i in range(4):
                    if self.ocr_and_click(["结界","突破"],box=self.box_of_screen(0.45, 0.09, 0.55, 0.18)):
                        self.click_relative(x, y, after_sleep=1)
                        self.ocr_and_click("进攻",box=self.box_of_screen(*group_rows_2[8]))

                    if  self.wait_click_feature('Battle_Back', threshold=0.7,
                                    box=self.box_of_screen(0,0,0.1,0.1),
                                    raise_if_not_found=False, time_out=5, after_sleep=0.5):
                        if res := self.ocr_and_click('确认',box=self.box_of_screen(0.54,0.55,0.62,0.70)):
                            self.info_set("步骤", "点击 确认")
                            if  self.wait_click_feature('Battle_Failure', threshold=0.7,
                                        box=self.B('Battle_Failure'),
                                        raise_if_not_found=False, time_out=10, after_sleep=1):
                                print(i)
                                self.info_set("步骤", "返回结界突破")
                            else:
                                self.log_warning("找不到 Battle_Failure")
                            
                        else:
                            self.info_set("确认弹窗", "无")
                            self.log_warning("找不到Battle_Finish")
            if self.ocr_and_click(["结界","突破"],box=self.box_of_screen(0.45, 0.09, 0.55, 0.18)):
                self.sleep(0.5)
                self.click_relative(x, y, after_sleep=0.5)
                print(x,y)
                self.log_info("进攻")
            if self.ocr_and_click("进攻",box=self.box_of_screen(*group_rows_2[target-1])):
                self.log_info(f"点击第 {target} 个")
                if self.count == 1:
                    self.log_info("检测是否为自动")
                    self.change_auto()
            else:
                self.log_info("没找到进攻")
                return False
            
            if not lock_res:
                pass

            res = self.Find_finish(self.config["BattleTime"])
            if res == 2:
                self.log_warning("战斗失败！！")
                return False
            elif res == 3:
                self.log_warning("战斗超时！！")
                return False
            if ( self.forward == True and self.count % 3 == 0 ) or (self.forward == False and (self.count) % 3 ==0):
                self.log_info(f"方向={'正' if self.forward else '倒'},第 {self.count} 个挑战 ,出现了勾玉结算)")
                if res := self.wait_feature('Battle_Finish', threshold=0.7,
                                    box=self.box_of_screen(0.39,0.57,0.62,0.88),
                                    raise_if_not_found=False, time_out=5):
                    self.sleep(1)
                    self.click(res,after_sleep=1)
                else:
                    self.log_warning("找不到Battle_Finish 222")
            

            self.log_info(f"第 {self.count} 个挑战 总共{self.tickets} 第 {self.trigger_count} 次战斗")
            if self.count == 9:
                self.forward = (not self.forward)
            self.count = self.count%9 + 1
            self.trigger_count+=1
            attack_num -= 1
        return True

    def ryoutoppa_battle(self):
        self.count = 1
        group_rows = {
            1: (0.47, 0.27),
            2: (0.72, 0.27),
            3: (0.47, 0.45),
            4: (0.73, 0.46),
            5: (0.46, 0.65),
            6: (0.71, 0.66),
            7: (0.48, 0.84),
            8: (0.72, 0.85),
        }
        # now = datetime.now()
        # final_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        # if now < final_time:
        #     if text := self.wait_ocr(threshold=0.8,
        #                         box=self.box_of_screen(0.12, 0.77, 0.29, 0.83),
        #                         time_out = 6):
        #         if nums := re.findall(r'\d+', text[0].name):
        #             self.tickets = int(nums[0])
        #         self.log_info(f"还没到九点，只能打{self.tickets}次")
        #         if self.tickets > 0:
        #             self.log_info("开打开打")
        #             return True
        #         else:
        #             self.log_info("票数不够")
        #             return False
        # else:
        #     self.log_info("打九点了一直打")
        #     self.tickets = 300
        target = 1

        if lock_res := self.Lock_team((0.14, 0.82, 0.2, 0.9)):
                self.log_info("锁上了")
        else:
            self.log_info("没锁")

        while True:
            if self.wait_ocr(match=re.compile("结界|突破"),
                               time_out=6,
                               box=self.box_of_screen(0.43, 0.08, 0.57, 0.18)):
                self.log_info("进入突破页面")
            else:
                self.log_info('找不到突破')
            res = self.find_feature("Real_Raid_Finish",
                                    box=self.box_of_screen(0.32, 0.18, 0.87, 0.92),
                                    threshold=0.7)
            lens = len(res)
            self.log_info(f"当前已经检测到{lens}已经击破")
            if target + lens >=9:
                self.log_info("战斗结束")
                return True
            if target > 4:
                self.log_warning("四个对手全部失败")
                return False

            x, y = group_rows[target]
            self.click_relative(x, y, after_sleep=0.5)
            if self.wait_click_ocr(match=re.compile("进攻"),
                                time_out=6,
                                box=self.box_of_screen(0.32, 0.18, 0.87, 0.92)):
                self.log_info(f"挑战第 {target} 个")
            else:
                self.log_warning("找不到进攻")
                return False

            if self.count == 1:
                self.log_info("检测是否为自动")
                self.change_auto()

            res = self.Find_finish(self.config["BattleTime"])
            if res == 1:
                self.log_info(f"第{target}个 挑战成功，继续")
                self.count += 1
                self.trigger_count += 1
            elif res == 2:
                self.log_warning(f"第{target}个 挑战失败，换下一个")
                target += 1
                self.trigger_count += 1
            elif res == 3:
                self.log_warning(f"第{target}个 挑战超时")
                self.Back_Home()
                return False
                # TODO: 用户自行处理超时逻辑