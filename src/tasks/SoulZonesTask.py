from src.tasks.BaseBattleTask import BaseBattleTask


class SoulZonesTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "魂土"
        self.trigger_count = 1
        self.count = 1

        self.default_config.update({
            "UserStatus": "队长",
            "Friend 1": "",
            "Friend 2": "",
            "Soul Zones": "悲鸣",
            "魂十一": "",
            "魂十二": "",
            "魂十三": "",

        })
        self.config_description.update({
            "UserStatus": "队伍角色：队长创建的队伍，队员加入队伍，单人独自挑战。",
            "Friend 1": "邀请几位就填几位，不邀请请不要填写",
            "魂十一": "预设队伍编号，格式：组,队  例如 1,5 表示第1组第5个队伍（对应悲鸣）",
            "魂十二": "预设队伍编号，格式：组,队  例如 2,3 表示第2组第3个队伍（对应神罚）",
            "魂十三": "预设队伍编号，格式：组,队  例如 3,1 表示第3组第1个队伍（对应虚无）",
        })
        self.config_type.update({
            "UserStatus": {
                "type": "drop_down",
                "options": ["队长", "队员", "单人"],
            },
            "Soul Zones": {
                "type": "drop_down",
                "options": ["拾层","悲鸣", "神罚", "虚无"],
            },
        })

    def run(self):
        if not self.logged_in:
            return False
        self.in_home_and_back()
        if self.config["Preset Enable"]:
            self._switch_preset_by_soul_zone()

        if self.config["UserStatus"] == "队长":
            if not self.SoulZones_page():
                self.log_warning("SoulZones_page 失败")
                return False
            if not self.Leader_page():
                self.log_warning("Leader_page 失败")
                return False
            if not self.Invitation():
                self.log_warning("Invitation 失败")
                return False
            self.log_info("进入battle")
            self.Leader_battle()
            return True

        elif self.config["UserStatus"] == "单人":
            if not self.SoulZones_page():
                self.log_warning("SoulZones_page 失败")
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

    def _switch_preset_by_soul_zone(self):
        """根据 Soul Zones 选择，从对应的魂XX配置中解析 组,队 并切换预设。"""
        zone_map = {
            "悲鸣": "魂十一",
            "神罚": "魂十二",
            "虚无": "魂十三",
        }
        key = zone_map.get(self.config["Soul Zones"])
        if key and self.config.get(key):
            val = self.config[key].strip()
            if val:
                parts = val.split(",")
                if len(parts) == 2:
                    group = int(parts[0].strip())
                    team = int(parts[1].strip())
                    self.log_info(f"({self.config['Soul Zones']}) → {key}: 组{group} 队{team}")
                    self.SwitchSoul_by_num(group, team)
                    return
        # 兜底：使用默认的 Preset Team
        self.log_info("使用默认预设队伍")
        group, team = self._parse_preset()
        self.SwitchSoul_by_num(group, team)

    def SoulZones_page(self):   

        if not self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        self.info_set("步骤", "进入探索页面")
        if self.wait_click_feature('Exploration_Soul', threshold=0.7,
                                        box=self.B('bottom'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("探索 Soul")
            self.info_set("步骤", "进入Soul")
        elif text:=self.ocr_and_click(['御魂','御','魂'],1,box=self.box_of_screen(0.18, 0.86, 0.26, 0.99)):
            print(text)
        else:
            self.log_info('找不到Soul')
            return False

        if text:=self.wait_ocr(['御魂','御','魂'],box=self.box_of_screen(0.11,0,0.17,0.1)):

            self.click_relative(0.2,0.5,after_sleep=1)
            self.log_info('点击八岐大蛇')
        else:
            self.log_info('没点击到御魂')
        self._swipe(0.11,0.69,0.11,0.22,0.5)
        self._swipe(0.11,0.69,0.11,0.22,0.5)
        self.sleep(0.5)
        if text:=self.ocr_and_click(self.config["Soul Zones"],1,box=self.box_of_screen(0.06,0.43,0.16,0.94),time_out=3):
                self.log_info('寻找悲鸣')
                return True
        else:
            self.log_info('找不到悲鸣')
            return False
    def Treasure(self):
        def check_battle_end():
            if self.count == 1:
                if self.find_one('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish')):
                    return 'finish'
                if self.ocr("发现宝藏",
                            box=self.box_of_screen(0.36, 0.18, 0.65, 0.33)):
                    return 'treasure'
            else:
                if self.find_one('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish')):
                    return 'finish'
            return None
        result = self.wait_until(
                lambda: check_battle_end(),
                time_out=self.config["BattleTime"] + 15,
                raise_if_not_found=False,
            )
        return result
        


#region 队长   
    def Leader_page(self):
        if self.ocr_and_click(['组队'],box=self.box_of_screen(0.74,0.82,0.83,0.92)):
            self.log_info('点击组队')
        self.sleep(0.5)
    
        self.click_relative(0.84,0.87,after_sleep=1) #组队  

        if text:=self.ocr_and_click(['不公开','仅邀请',],box=self.box_of_screen(0.61,0.67,0.78,0.74)):
            print(text)
            self.click_relative(0.68,0.80,after_sleep=1)
            return True
        return False
        
    def _invite_one(self, f: str, invite_xy: tuple, confirm_box: tuple) -> bool:
        """邀请单个好友：invite_xy=(x,y) 邀请按钮位置，confirm_box 确认区域。"""
        self.click_relative(*invite_xy, after_sleep=1)
        for tab in ('最近', '好友', '跨区', '寮友'):
            if self.ocr_and_click(tab, box=self.B("Friend_Index")):
                if self.ocr_and_click(f, box=self.B("Friend")):
                    self.click_relative(0.60, 0.79, after_sleep=1)
                    self.log_info('寻找到一位')
                    if self.ocr_and_click(f, time_out=20,
                                           box=self.box_of_screen(*confirm_box)):
                        return True
        return False

    def Invitation(self):
        if text := self.wait_ocr(['协战', '队伍'],
                                  box=self.box_of_screen(0, 0, 0.17, 0.1), time_out=3):
            print(text)

        targets = [self.config["Friend 1"]]
        if self.config["Friend 2"]:
            targets.append(self.config["Friend 2"])

        for i, f in enumerate(targets):
            if i == 0:
                ok = self._invite_one(f, (0.50, 0.34), (0.43, 0.15, 0.53, 0.19))
            else:
                ok = self._invite_one(f, (0.83, 0.34), (0.77, 0.14, 0.88, 0.19))
            if not ok:
                return False
        return True

            

    def Leader_battle(self):
        targets = [self.config["Friend 1"]]
        if self.config["Friend 2"]:
            targets.append(self.config["Friend 2"])
        if lock_res:=self.Lock_team((0.07,0.87,0.12,0.97)):
            self.log_info("锁")
        else:
            self.log_info("没锁")
    
        self.count = 1

        while(self.count <= self.config["AttackNumber"]):
            # if not self.wait_click_feature('Home_Explore', threshold=0.7, #TIAOZHAN
            #                             box=self.box_of_screen(0.91 ,0.81 ,1 , 1),
            #                             raise_if_not_found=False, time_out=25, after_sleep=1):
            #     self.log_warning("找不到tiaozhan")
            # self.info_set("步骤", "进入tiaozhan")
             for i, f in enumerate(targets):
                if i == 0:
                    ok = self.ocr_and_click(f, time_out=30,box=self.box_of_screen (0.43, 0.15, 0.53, 0.19))
                else:
                    ok = self.ocr_and_click(f, time_out=30,box=self.box_of_screen (0.77, 0.14, 0.88, 0.19))
                if ok:
                    self.click_relative(0.95,0.90,after_sleep=0.5)
                    self.log_info("进入battle")
                    
                    if self.count == 1: 
                        if not lock_res:
                            if not self.config["Preset Enable"]: #只是忘记锁了
                                self.ocr_and_click("准备",box=self.box_of_screen(0.87, 0.77, 0.96, 0.85))
                                self.log_warning("请锁定阵容")
                            else:
                                self.Change_team()
                    self.Find_finish(self.config["BattleTime"])

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
                else:
                    self.log_info("队友不在了")
                    self.Back_Home()
                    return False
        if not self.wait_click_feature('Back', threshold=0.7,
                                            box=self.B('Back'),
                                            raise_if_not_found=False, time_out=5, after_sleep=1):
            self.log_warning("找不到Battle_Finish")
        if self.ocr_and_click("确定",box=self.box_of_screen(0.54, 0.57, 0.63, 0.62)):
            self.wait_click_feature("Home_Button",box=self.B("Home_Button"),threshold=0.8,time_out=3,after_sleep=2)
        if self.in_home_and_back():
            return True
        else:
            return False

                           
#endregion

    def Alone_battle(self):
        self.count = 1
        while(self.count <= self.config["AttackNumber"]):
            if self.ocr_and_click(['挑战'],box=self.box_of_screen(0.87,0.79,0.98,0.90)):
                self.log_info('点击挑战')   
            if self.count == 1:
                result = self.Treasure()
                if result == 'treasure':
                    self.click_relative(0.1, 0.1, after_sleep=0.5)
                    self.log_info(f"第 {self.count} 次战斗结束(宝藏) 总共{self.config['AttackNumber']} 第 {self.trigger_count} 次战斗")
                    self.count += 1
                    self.trigger_count += 1
                    continue
                elif result == 'finish':
                    self.wait_click_feature('Battle_Finish', threshold=0.7,
                                                box=self.B('Battle_Finish'),
                                                raise_if_not_found=False, time_out=5,
                                                after_sleep=1)
                    self.log_info(f"第 {self.count} 次战斗结束 总共{self.config['AttackNumber']} 第 {self.trigger_count} 次战斗")
                    self.count += 1
                    self.trigger_count += 1
                    continue
            if res := self.wait_feature('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish'),
                                    raise_if_not_found=False, time_out=5):
                    self.sleep(1)
                    self.click(res,after_sleep=1)
            else:
                self.log_warning("找不到Battle_Finish 222")
            self.log_info(f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
            self.count+=1
            self.trigger_count+=1
        self.wait_click_feature("Home_Button",box=self.B("Home_Button"),threshold=0.8,time_out=3,after_sleep=2)
        self.in_home_and_back()

    def Member_battle(self):
        self.count = 1
        while self.count <= self.config["AttackNumber"] :
            if not self.Find_finish(self.config["BattleTime"]):
                self.Back_Home()
                return False
            if self.count == 1:      
                if self.wait_ocr("发现宝藏",time_out=1,box=self.box_of_screen(0.36,0.18,0.65,0.33)):
                    self.click_relative(0.1,0.1,after_sleep=0.5)
                if not self.wait_click_feature('Member_Confirm', threshold=0.7,
                                        box=self.B('Member_Confirm'),
                                        raise_if_not_found=False, time_out=10, after_sleep=1):
                    self.log_warning("找不到Member_Confirm")
                if  self.wait_click_feature('Leader_Invitation', threshold=0.7,
                                        box=self.B('Leader_Invitation'),
                                        raise_if_not_found=False, time_out=2, after_sleep=1):
                        if not (self.ocr_and_click('确定',time_out=2,box=self.box_of_screen(0.45,0.45,0.70,0.70))):
                            self.log_warning("找不到确认")       
            self.log_info(f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
            self.count += 1
            self.trigger_count+=1
        if self.Back_Home():
            return True
        else:
            return False


