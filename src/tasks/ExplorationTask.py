


from src.tasks.BaseBattleTask import BaseBattleTask


class ExplorationTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "战斗-困28"
        self.trigger_count = 1
        self.count = 1
        self.default_config.update({
            "UserStatus": "队长",
            "Friend 1": "",
            "Friend 2": "",          
        })
        self.config_description.update({
            "UserStatus": "队伍角色：队长创建的队伍，队员加入队伍，单人独自挑战。",
            "Friend 1": "邀请几位就填几位，不邀请请不要填写",
            "Lock Team Enable":"困28的锁阵容为自动轮换，在使用之前请务必设置好自动轮换，任务会自动打开"
        })
        self.config_type.update({
            "UserStatus": {
                "type": "drop_down",
                "options": ["队长", "队员", "单人"],
            },
        })
    def run(self):
        self.in_home_and_back()
        if self.config["Preset Enable"]:
            group, team = self._parse_preset()
            self.SwitchSoul_by_num(group, team)

        if self.config["UserStatus"] == "队长":
            if not self.Exploration_page():
                self.log_warning("Exploration_page 失败")
                return False
            if not self.Leader_page():
                self.log_warning("Leader_page 失败")
                return False
            if not self.Invitation():
                self.log_warning("Invitation 失败")
                return False
            self.log_info("进入battle")
            if not self.Leader_battle():
                return False
            return True

        elif self.config["UserStatus"] == "单人":
            if not self.Exploration_page():
                self.log_warning("Exploration_page 失败")
                return False
            self.Alone_battle()
            return True

        else:  # 队员
            self.log_info("等待邀请")
            if self.wait_click_feature('Invitation_Confirm', threshold=0.7,
                                        box=self.B('Invitation_Confirm'),
                                        raise_if_not_found=False, time_out=300, after_sleep=1):
                if self.Member_battle():
                    return True
                else:
                    return False
            else:
                self.log_warning("等待邀请超时")
                return False
    def Exploration_page(self):   
        if not self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        if not (text:=self.ocr_and_click(['二十八'],1,box=self.box_of_screen(0.82, 0.62, 0.92, 0.68))):
            print(text)
            self.log_info('找不到二十八')
        if  (text:=self.ocr_and_click(['困难'],1,box=self.box_of_screen(0.01, 0.25, 0.13, 0.51))):
            return True
        else:

            self.log_info('找不到困难')
            return False
            
   

    def Leader_page(self):
        if not (text:=self.ocr_and_click(['组队'],1,box=self.box_of_screen(0.68, 0.79, 0.93, 0.94))):
            print(text)
            self.log_info('找不到组队')


        if text:=self.ocr_and_click(['不公开','仅邀请',],box=self.box_of_screen(0.3457, 0.5653, 0.5074, 0.6243)):
            print(text)
            self.click_relative(0.68,0.80,after_sleep=1)
        if text:=self.ocr_and_click('创建',box=self.box_of_screen(0.45, 0.68, 0.55, 0.74)):#困28创建
            print(text)
            self.click_relative(0.68,0.80,after_sleep=1)
            return True
        else:
            return False
        
        
    def _invite_one(self, f: str, invite_xy: tuple, confirm_box: tuple) -> bool:
        """邀请单个好友：invite_xy=(x,y) 邀请按钮位置，confirm_box 确认区域。"""
        self.click_relative(*invite_xy, after_sleep=1)
        for tab in ('好友', '跨区', '寮友'):
            if self.ocr_and_click(tab, box=self.B("Exp_Friend_Index")):
                if self.ocr_and_click(f, box=self.B("Friend")):
                    self.click_relative(0.60, 0.79, after_sleep=1)
                    self.log_info('寻找到一位')
                    if self.ocr_and_click(f, time_out=20,
                                           box=self.box_of_screen(*confirm_box)):
                        return True
        return False
    
    def Invitation(self):#完成了 应该从点击挑战开始重新思考
        if text := self.wait_ocr(['协战', '队伍'],
                                  box=self.box_of_screen(0, 0, 0.17, 0.1), time_out=3):
            print(text)
        if self._invite_one(self.config["Friend 1"], (0.83, 0.34), (0.77, 0.14, 0.88, 0.19)):
            self.click_relative(0.95,0.90,after_sleep=0.5)
            self.log_info("进入battle")
            return True
            
           
    def Leader_battle(self):
        self.count = 1
        def battle():
            if (self.wait_click_feature('Exploration_Battle', threshold=0.7,
                                    box=self.box_of_screen(0.16, 0.22, 1.0, 0.88),
                                    raise_if_not_found=False, time_out=3,after_sleep=0.5)):
                self.log_info("进入战斗")
                self.Find_finish(self.config["BattleTime"])

                self.log_info(f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
                self.count+=1
                self.trigger_count+=1
                self.sleep(2)#等等队友 
            else:
                self.click_relative(0.87, 0.74,after_sleep=2)
                self.log_info("移动")
        def final_battle():
            if self.wait_click_feature('Exploration_Final_Battle', threshold=0.7,
                                    box=self.box_of_screen(0.16, 0.22, 1.0, 0.88),
                                    raise_if_not_found=False, time_out=3, after_sleep=2):
                self.Find_finish(self.config["BattleTime"])
                self.log_info(f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
                self.log_info("最后一次战斗结束")
                self.count+=1
                self.trigger_count+=1
                return True
            else:
                return False
        while self.count <= self.config["AttackNumber"]:
            if self.ocr_and_click(self.config["Friend 1"], time_out=20,box=self.box_of_screen (0.77, 0.14, 0.88, 0.19)):
                    self.click_relative(0.95,0.90,after_sleep=0.5)
                    self.log_info("进入battle")
            if  self.wait_ocr(['自动', '轮换'],
                            box=self.box_of_screen(0.09, 0.9, 0.2, 0.97), time_out=10):
                self.sleep(1)
                self.click_relative(0.66, 0.85,after_sleep=1)#走一步
                self.log_info("进入战斗页面")
            if self.count == 1:
                if self.calculate_color_percentage({"b": (200, 255), "g": (200, 255), "r": (200, 255)}, 
                                                box=self.box_of_screen(0.09, 0.92, 0.11, 0.95)) > 0.2:
                    self.log_info("自动轮换已经开启")
                else:
                    self.click_relative(0.1,0.93,after_sleep=0.5)
                    self.log_info("打开自动轮换")
            for _ in range(4):
                battle()
            if not self.wait_until(
            final_battle,
            time_out=600,
            pre_action=battle,
            raise_if_not_found=False,
            ):
                return False

            if not self.wait_click_feature('Back', threshold=0.7,
                                                box=self.B('Back'),
                                                raise_if_not_found=False, time_out=5, after_sleep=1):
                self.log_warning("找不到Back")
            self.ocr_and_click("确认",1,box=self.box_of_screen(0.53, 0.5, 0.68, 0.62))
            if self.count <= self.config["AttackNumber"]:
                if self.ocr_and_click(["邀请","继续"],box=self.box_of_screen(0.34, 0.39, 0.67, 0.66)):
                    self.ocr_and_click("确定",box=self.box_of_screen(0.34, 0.39, 0.67, 0.66))
                else:
                    break
        if self.ocr_and_click("取消",box=self.box_of_screen(0.33, 0.55, 0.48, 0.66)):
            self.Back_Home()
            return True
        else:
            return False

    def Member_battle(self):
        def battle():
            if self.Find_finish(self.config["BattleTime"]):
                self.log_info(
                    f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
                self.count += 1
                self.trigger_count += 1
                return True
            else:
                self.log_warning("没找到战斗结算页面")
                self.Back_Home()
                return False
        def final_battle():
            if self.wait_feature('Exploration_Final_Treasure', threshold=0.7,
                                    box=self.box_of_screen(0.16, 0.22, 1.0, 0.88),time_out=3):
                if not self.wait_click_feature('Back', threshold=0.7,
                                               box=self.B('Back'),
                                               raise_if_not_found=False, time_out=5, after_sleep=1):
                    self.log_warning("找不到Back")
                    return False
                self.ocr_and_click("确认", 1, box=self.box_of_screen(0.53, 0.5, 0.68, 0.62))
                return True
            elif self.In_Home():
                return True
            else:
                return False
        self.count = 1
        while self.count <= self.config["AttackNumber"]:
            self.log_info("等待邀请")
            if self.wait_click_feature('Invitation_Confirm', threshold=0.7,
                                       box=self.B('Invitation_Confirm'),
                                       raise_if_not_found=False, time_out=300, after_sleep=1):
                for _ in range(4):
                    if not battle():
                        return False
                if not self.wait_until(condition=lambda :final_battle,
                                    time_out=600,
                                    pre_action=battle,
                                    raise_if_not_found=False,
                                    ):
                    return False
            else:
                self.log_warning("等待邀请超时")
                return False
        if self.Back_Home():
            return True
        else:
            return False
        