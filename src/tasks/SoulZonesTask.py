from src.tasks.BaseBattleTask import BaseBattleTask


class SoulZonesTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "魂土"
        self.trigger_count = 1
        self.count = 1

        self.default_config.update({
            "UserStatus": "队长",
            "InviteNumber": 0,
            "Friend 1": "",
            "Friend 2": "",

        })
        self.config_description.update({
            "UserStatus": "队伍角色：队长创建的队伍，队员加入队伍，单人独自挑战。",
        })
        self.config_type.update({
            "UserStatus": {
                "type": "drop_down",
                "options": ["队长", "队员", "单人"],
            },
        })

    def run(self):
        self.SwitchSoul_by_num(int(self.config["Preset Group"]),int(self.config["Preset Team"]))
        if self.config["UserStatus"] in ("队长", "单人"):
            self.SoulZones_page()
            self.Invitation()
        else:
            self.log_info("队员模式，等待队长邀请")
        # self.Battle()

    def SoulZones_page(self):   
        self.in_home_and_back()

        if not self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        self.info_set("步骤", "进入探索页面")

        if not (text:=self.ocr_and_click(['御魂','御','魂'],1,box=self.box_of_screen(0.11,0.94,0.17,0.98))):
            self.log_info('找不到御魂页面')

        if text:=self.wait_ocr(['御魂','御','魂'],box=self.box_of_screen(0.11,0,0.17,0.1)):

            self.click_relative(0.2,0.5,after_sleep=1)
            self.log_info('点击八岐大蛇')
        else:
            self.log_info('没点击到御魂')
        
        if self.ocr_and_click(['组队'],box=self.box_of_screen(0.74,0.82,0.83,0.92)):
            self.log_info('点击组队')

        if text:=self.wait_ocr(['组队','组','队'],box=self.box_of_screen(0,0,0.17,0.1),time_out=3):
            self._swipe(0.39,0.66,0.39,0.29,0.5)
            self._swipe(0.39,0.66,0.39,0.29,0.5)
            self.sleep(0.5)
            if text:=self.ocr_and_click(['悲鸣','悲','鸣'],1,box=self.box_of_screen(0.32,0.42,0.48,0.69),time_out=3):
                self.log_info('寻找悲鸣')
            else:self.log_info('找不到悲鸣')

            self.click_relative(0.84,0.87,after_sleep=1)            
        if text:=self.ocr_and_click(['不公开','仅邀请',],box=self.box_of_screen(0.61,0.67,0.78,0.74)):
            print(text)
            self.click_relative(0.68,0.80,after_sleep=1)
    
    def Invitation(self):
        if text := self.wait_ocr(['协战', '队伍'],
                                  box=self.box_of_screen(0, 0, 0.17, 0.1), time_out=3):
            print(text)
            
        # 确定要找的好友列表
        targets = [self.config["Friend 1"]]
        if self.config["Friend 2"]:
            targets.append(self.config["Friend 2"])

        # 先在"最近"里找

        for i, f in enumerate(targets):
            if i == 0:
                self.click_relative(0.50, 0.34, after_sleep=1)
            else:
                self.click_relative(0.83, 0.34, after_sleep=1)

            self.ocr_and_click('最近', box=self.B("Friend_Index"))
            if self.ocr_and_click(f, box=self.B("Friend")):
                self.click_relative(0.60,0.79,after_sleep=1)
                self.log_info('寻找到一位')
            elif self.ocr_and_click('好友', box=self.B("Friend_Index")):
                if self.ocr_and_click(f, box=self.B("Friend")):
                    self.click_relative(0.60,0.79,after_sleep=1)
                    self.log_info('寻找到一位')
            elif self.ocr_and_click('跨区', box=self.B("Friend_Index")):
                if self.ocr_and_click(f, box=self.B("Friend")):
                    self.click_relative(0.60,0.79,after_sleep=1)
                    self.log_info('寻找到一位')
            elif self.ocr_and_click('寮友', box=self.B("Friend_Index")):
                if self.ocr_and_click(f, box=self.B("Friend")):
                    self.click_relative(0.60,0.79,after_sleep=1)
                    self.log_info('寻找到一位')
        
    def Battle(self):
        
        self.count = 1
        while(self.count <= self.config["AttackNumber"]):
            # if not self.wait_click_feature('Home_Explore', threshold=0.7, #TIAOZHAN
            #                             box=self.box_of_screen(0.91 ,0.81 ,1 , 1),
            #                             raise_if_not_found=False, time_out=25, after_sleep=1):
            #     self.log_warning("找不到tiaozhan")
            # self.info_set("步骤", "进入tiaozhan")

            self.click_relative(0.95,0.90,after_sleep=0.5)
            self.log_info("进入battle")
            if not self.wait_click_feature('Battle_Success', threshold=0.7,
                                    box=self.B('Battle_Success_Soul'),
                                    raise_if_not_found=False, time_out=60, after_sleep=1):
                self.log_warning("找不到Battle_Success_Soul")


            if not self.wait_click_feature('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish'),
                                    raise_if_not_found=False, time_out=5, after_sleep=1):
                self.log_warning("找不到Battle_Finish")
            self.log_info(f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
            self.count+=1
            self.trigger_count+=1

        



        


        
