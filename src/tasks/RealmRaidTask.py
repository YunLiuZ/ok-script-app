from src.tasks.BaseBattleTask import BaseBattleTask


class RealmRaidTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "个人突破"
        self.trigger_count = 1
        self.count = 1
        self.tickets = 0
        self.forward = True
        self.default_config.update({
            "Tickets": 10,
        })
        self.config_description.update({
            "Tickets": "至少有多少张票才去挑战",
            "AttackNumber":"对于结界突破无需填写",
        })
    def run(self):
        self.in_home_and_back()
        if self.config["Preset Enable"]:
            self.SwitchSoul_by_num(int(self.config["Preset Group"]),int(self.config["Preset Team"]))
        if self.RealmRaid_page():
            self.Battle()
            self.sleep(1)     
            self.Back_Home() 
        else:
            self.log_warning("找不到结界页面")
            self.sleep(1)     
            self.Back_Home()

        
    def RealmRaid_page(self):
        if not self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        self.info_set("步骤", "进入探索页面")
        if text:=self.ocr_and_click(['结界','突破'],sleep=2,box=self.B("ocr_explore_box")):
            print(text)
            if text := self.wait_ocr(threshold=0.8,box=self.box_of_screen(0.89,0.02,0.95,0.1),time_out=2):
                import re
                nums = re.findall(r'\d+', text[0].name)
                self.tickets = int(nums[0]) if nums else 0
                print(f"票数: {self.tickets}")
                self.log_info("{self.tickets}")
                if self.tickets > self.config["Tickets"]:
                    self.log_info("1123")
                    return True
                else: 
                    
                    return False
                    
        else:
            print("2")
            return False
    
        
    def Battle(self):
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
            self.forward = sum(ys) / len(ys) < self.frame.shape[0] * 0.5  # 偏上=正着，偏下=倒着
        else:
            self.forward = True

        # 留至少1个，lens 永远 ≥ 1
        if  (lens + self.tickets) % 9 != 0:
            attack_num = self.tickets
        else:
            attack_num = self.tickets - 1
        
        self.log_info(f"方向={'正' if self.forward else '倒'} lens={lens} tickets={self.tickets} 本轮打{attack_num}次")
        self.count = (lens + 1)
        if lock_res := self.Lock_team((0.63,0.79,0.67,0.87)):
                self.log_info("锁上了")
        else:
            self.log_info("没锁")

        while(attack_num):
            
            target = self.count if self.forward else (10 - self.count)
            x, y = group_rows[target]
            
            
            #退四
            if(self.forward and self.count == 9):
                for i in range(4):
                    if self.ocr_and_click(["结界","突破"]):
                        self.click_relative(x, y, after_sleep=1)
                        self.ocr_and_click("进攻",box=self.box_of_screen(*group_rows_2[8]))

                    if  self.wait_click_feature('Battle_Back', threshold=0.7,
                                    box=self.box_of_screen(0,0,0.2,0.2),
                                    raise_if_not_found=False, time_out=5, after_sleep=0.5):
                        if texts := self.wait_ocr(match='确认',box=self.box_of_screen(0.54,0.55,0.62,0.59),threshold=0.8,time_out=1):
                            self.click_box(texts[0], after_sleep=1)
                            self.info_set("步骤", "点击 确认")

                            if  self.wait_click_feature('Battle_Failure', threshold=0.7,
                                        box=self.B('Battle_Failure'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
                                print(i)
                                self.info_set("步骤", "返回结界突破")
                            else:
                                self.log_warning("找不到 Battle_Failure")
                            
                        else:
                            self.info_set("确认弹窗", "无")
                            self.log_warning("找不到Battle_Finish")

            self.click_relative(x, y, after_sleep=0.5)
            self.log_info("进攻")
            if self.ocr_and_click("进攻",box=self.box_of_screen(*group_rows_2[target-1])):
                self.log_info(f"点击第 {target} 个")
            else:
                self.log_info("没找到进攻")
            
            if not lock_res:
                pass

            if not self.wait_click_feature('Battle_Success', threshold=0.7,
                                    box=self.B('Battle_Success'),
                                    raise_if_not_found=False, time_out=self.config["BattleTime"], after_sleep=1.5):
                self.log_warning("找不到Battle_Success")

            if not self.wait_click_feature('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish'),
                                    raise_if_not_found=False, time_out=5, after_sleep=1):
                self.log_warning("找不到Battle_Finish")
            if self.count % 3 == 0:
                if not self.wait_click_feature('Battle_Finish', threshold=0.7,
                                    box=self.box_of_screen(0.39,0.57,0.62,0.88),
                                    raise_if_not_found=False, time_out=5, after_sleep=1):
                    self.log_warning("找不到Battle_Finish 222")
            

            self.log_info(f"第 {self.count} 个挑战 总共{self.tickets} 第 {self.trigger_count} 次战斗")
            self.count = self.count%9 + 1
            self.trigger_count+=1
            attack_num -= 1
                    