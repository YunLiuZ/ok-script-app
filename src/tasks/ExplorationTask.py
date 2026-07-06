


from src.tasks.BaseBattleTask import BaseBattleTask


class ExplorationTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "困28"
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
        })
        self.config_type.update({
            "UserStatus": {
                "type": "drop_down",
                "options": ["队长", "队员", "单人"],
            },
        })
    def run(self):
        self.Leader_battle()
        # self.in_home_and_back()
        # if self.config["Preset Enable"]:
        #     self.SwitchSoul_by_num(int(self.config["Preset Group"]),int(self.config["Preset Team"]))
        # if self.config["UserStatus"] in ("队长"):
        #     if self.Exploration_page():
        #         if self.Leader_page():
        #             if self.Invitation():
        #                 self.log_info("进入battle")
        #                 self.Leader_battle()
        #             else:
        #                 self.log_warning("Invitation 失败")
        #         else:
        #             self.log_warning("Leader_page 失败")
        #     else:
        #         self.log_warning("SoulZones_page 失败")

        # elif self.config["UserStatus"] in ("单人"):
        #     self.SoulZones_page()
        #     self.Alone_battle()
        # else:
        #     self.log_info("等待邀请")
        #     if  self.wait_click_feature('Invitation_Confirm', threshold=0.7,
        #                             box=self.B('Invitation_Confirm'),
        #                             raise_if_not_found=False, time_out=120, after_sleep=1):
        #         self.Member_battle()
                
        #     else: 
        #         self.log_info("等待超过六十秒")
    def Exploration_page(self):   
        if not self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        self.info_set("步骤", "进入探索页面")
        if not (text:=self.ocr_and_click(['二十八'],1,box=self.box_of_screen(0.82, 0.62, 0.92, 0.68))):
            print(text)
            self.log_info('找不到二十八')
        if  (text:=self.ocr_and_click(['困难'],1,box=self.box_of_screen(0.01, 0.25, 0.13, 0.51))):
            return True
        else:
            self.log_info('找不到困难')
            
   

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
        if self._invite_one(self.config["Friend 1"], (0.83, 0.34), (0.2832, 0.1187, 0.527, 0.2076)):
            return True
    
    def Leader_battle(self):# 未开始
        self.count = 1
        lock_res=self.Lock_team((0,0.88,0.06,0.95))
        targets = [self.config["Friend 1"]]
        if self.ocr_and_click(self.config["Friend 1"], time_out=20,box=self.box_of_screen (0.77, 0.14, 0.88, 0.19)):
                    self.click_relative(0.95,0.90,after_sleep=0.5)
                    self.log_info("进入battle")

        
       
        while(self.count <= self.config["AttackNumber"]):
            if self.count == 1: 
                if not lock_res:
                    if not self.config["Preset Enable"]: #只是忘记锁了
                        self.ocr_and_click("准备",box=self.box_of_screen(0.87, 0.77, 0.96, 0.85))
                        self.log_warning("请锁定阵容")
                    else:
                        self.Change_team()
                        
            if not self.wait_click_feature('Battle_Success', threshold=0.7,
                                    box=self.B('Battle_Success_Soul'),
                                    raise_if_not_found=False, time_out=self.config["BattleTime"], after_sleep=2):
                self.log_warning("找不到Battle_Success_Soul")


            if not self.wait_click_feature('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish'),
                                    raise_if_not_found=False, time_out=5, after_sleep=1):
                self.log_warning("找不到Battle_Finish")
            if self.count == 1:      
                if self.wait_ocr("发现宝藏",time_out=1,box=self.box_of_screen(0.36,0.18,0.65,0.33)):
                    self.click_relative(0.1,0.1,after_sleep=1)
                if  self.wait_click_feature('Leader_Invitation', threshold=0.7,
                                    box=self.B('Leader_Invitation'),
                                    raise_if_not_found=False, time_out=3, after_sleep=1):
                    if not (self.ocr_and_click('确定',time_out=2,box=self.box_of_screen(0.51,0.53,0.67,0.63))):
                        self.log_warning("找不到确定")
                else:
                    self.log_warning("找不到Leader_Invitation")

            self.log_info(f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
            self.count+=1
            self.trigger_count+=1
        if not self.wait_click_feature('Back', threshold=0.7,
                                            box=self.B('Back'),
                                            raise_if_not_found=False, time_out=5, after_sleep=1):
            self.log_warning("找不到Battle_Finish")
        if self.ocr_and_click("确定",box=self.box_of_screen(0.54, 0.57, 0.63, 0.62)):
            self.wait_click_feature("Home_Button",box=self.B("Home_Button"),threshold=0.8,time_out=3,after_sleep=2)
        self.in_home_and_back()

        