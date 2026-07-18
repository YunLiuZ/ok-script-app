from src.tasks.BaseOmjTask import BaseOmjTask


class BaseBattleTask(BaseOmjTask):
    """战斗任务基类：统一管理阵容锁定、预设队伍切换等战斗配置。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_config.update({

            "Lock Team Enable": True,
            "Preset Enable": False,
            "Preset Team": "1,1",
            "AttackNumber":10,
            "BattleTime": 300,
        })

        self.config_description.update({
            "Lock Team Enable": "开启后每次战斗前锁定当前阵容，防止误操作切换队伍。",
            "Preset Enable": "开启后战斗前自动切换到指定的预设队伍。",
            "Preset Team": "预设队伍编号，格式：组,队  例如 1,5 表示第1组第5个队伍。",
            "BattleTime": "通过时间 一般情况下不用修改"
        })

    # ---------- 预设队伍解析 ----------

    def _parse_preset(self):
        """解析 Preset Team 配置（格式 "组,队" 如 "1,5"），返回 (group, team)。"""
        val = self.config.get("Preset Team", "1,1")
        parts = val.split(",")
        if len(parts) == 2:
            return int(parts[0].strip()), int(parts[1].strip())
        return 1, 1

    def SwitchSoul_by_name(self):
        self.In_Home()
        self.ocr_and_click('式神录',box=self.B("Home_Shikigami_Chronicles"))
        self.wait_click_ocr(match='预设',
                            box=self.get_box_by_name('Home_Shikigami_Presets'))
        self.wait_click_ocr(match=self.config["Preset Group"],
                            box=self.get_box_by_name('Home_Shikigami_Group'))
        texts = self.ocr(match=self.config["Preset Team"],
                         box=self.get_box_by_name('Home_Shikigami_Group_Name'))
        if texts:
            h = self.frame.shape[0]
            center_y = texts[0].y + texts[0].height / 2
            rel_y = center_y / h
            self.click_relative(0.77, rel_y)
            self.log_info(f"点击预设队伍 {self.config['Preset Team']} at (0.77, {rel_y:.3f})")
    
    def SwitchSoul_by_num(self,group:int,team:int):
        """按编号切换预设队伍（从 config 读取 Preset Group / Preset Team)。"""

        if self.wait_click_feature('Home_Shikigami_Chronicles', threshold=0.7,
                                        box=self.B('bottom'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("Home_Shikigami_Chronicles")
            self.info_set("步骤", "进入Home_Shikigami_Chronicles")
        elif text:=self.ocr_and_click(['式神'],1,box=self.B('Home_Shikigami_Chronicles')):
            print(text)
        else:
            self.log_info('找不到Home_Shikigami_Chronicles')
            return False
    

        if self.wait_click_ocr(match='预设',
                            box=self.B('Home_Shikigami_Presets'),time_out=3,after_sleep=1):
            self._swipe(0.91,0.22,0.91,0.77,0.5)
            self.sleep(0.5)

            group_rows = {1: 0.17, 2: 0.27, 3: 0.35, 4: 0.47, 5: 0.56, 6: 0.67, 7: 0.75}
            self.click_nth('x', 0.91, group_rows, group, "预设组")

            team_rows = {1: 0.22, 2: 0.44, 3: 0.64, 4: 0.85}
            self.click_nth('x', 0.77, team_rows, team, "预设队伍")

            self.sleep(1)
            if text := self.ocr('确认',box=self.box_of_screen(0.50,0.53,0.66,0.63)):
                self.click(text[0],after_sleep=0.5)
            if text := self.ocr('确认',box=self.box_of_screen(0.50,0.53,0.66,0.63)):
                self.click(text[0],after_sleep=0.5)
            if not self.wait_click_feature('Back', threshold=0.7,
                                            box=self.B('Back'),
                                            raise_if_not_found=False, time_out=3, after_sleep=1):
            
                self.log_info('回家')
            else:
                self.log_info('找不到Home_Shikigami_Chronicles')
        self.in_home_and_back()

    def Lock_team(self,confirm_box:tuple,lock = "Lock",notlock = "Not_Lock"):
        if res := self.find_feature(lock,threshold=0.9,box=self.box_of_screen(*confirm_box)) :
            self.log_info("检查到上锁")
            if self.config["Lock Team Enable"]:
                self.log_info("上锁")
                return True
            else :
                self.click(res[0]) 
                self.log_info("解锁")
                return False 
        elif  res := self.find_feature(notlock,threshold=0.9,box=self.box_of_screen(*confirm_box)) :
            if self.config["Lock Team Enable"]:
                self.click(res[0])
                self.log_info("上锁")
                return True 
            else:
                self.log_info("解锁")
                return False
    def Change_team(self):
        self.ocr_and_click(["预","设"],box=self.box_of_screen(0,0.87,0.15,1))# (0.8781, 0.7701, 0.9625, 0.8535)
        group, team = self._parse_preset()
        group_rows = {1: 0.36, 2: 0.45, 3: 0.54, 4: 0.63, 5: 0.72, 6: 0.81, 7: 0.90}
        self.click_nth('x', 0.76, group_rows, group, "预设组")

        team_rows = {1: 0.22, 2: 0.44, 3: 0.64, 4: 0.85}
        self.click_nth('x', 0.77, team_rows, team, "预设队伍")

        self.ocr_and_click("出战",1,box=self.box_of_screen(0.26, 0.88, 0.40, 0.96))
        if not self.ocr_and_click("确定",time_out=2,box=self.box_of_screen(0.45, 0.57, 0.54, 0.62)):
            if self.ocr_and_click("准备",box=self.box_of_screen(0.87, 0.77, 0.96, 0.85)):
                True
            else:
                False
        else:
            if self.ocr_and_click("准备",box=self.box_of_screen(0.87, 0.77, 0.96, 0.85)):
                return True
            else: return False
    def Find_finish(self, battle_time, success_box='Battle_Success'):
        """
        等待战斗结束并处理结算画面。
        同时检测 Battle_Success 和 Battle_Finish，用各自的 box。
        保留原嵌套重试逻辑：点一次 → sleep → 确认 → 没点上再补刀。

        Returns:
            True  战斗正常结束
            False 超时
        """
        success_clicked = False
        def finish():
            if self.wait_click_feature('Battle_Finish', threshold=0.7,
                                        box=self.B('Battle_Finish'),
                                        raise_if_not_found=False, time_out=3):
                self.sleep(1)
                if res1 := self.find_one('Battle_Finish', threshold=0.7,
                                          box=self.B('Battle_Finish')):
                    self.click(res1)
                    self.log_info("第一次没点到")
                    return True
                else:
                    self.log_info("第一次点到")
                return True
            elif self.wait_click_feature('Battle_Finish_Soul', threshold=0.7,
                                        box=self.B('Battle_Finish_Soul'),
                                        raise_if_not_found=False, time_out=3):
                self.sleep(1)
                if res1 := self.find_one('Battle_Finish_Soul', threshold=0.7,
                                          box=self.B('Battle_Finish_Soul')):
                    self.click(res1)
                    self.log_info("第一次没点到")
                    return True
                else:
                    self.log_info("第一次点到")
                    return True
            return False

        def check():
            if res := self.find_one('Battle_Success', threshold=0.7,
                                        box=self.B('success_box')):
                self.click(res)
                self.sleep(1)
                if res1 := self.find_one('Battle_Success', threshold=0.7,
                                          box=self.B('success_box')):
                    self.click(res1)
                    self.log_info("第一次没点到")
                else:
                    self.log_info("第一次点到")
                if finish():
                    return True
                else:
                    return False
            # 检测 Battle_Finish（原嵌套重试逻辑）
            if res := self.find_one('Battle_Finish', threshold=0.7,
                                        box=self.B('Battle_Finish'),
                                        ):
                self.click(res)
                self.sleep(1)
                if res1 := self.find_one('Battle_Finish', threshold=0.7,
                                          box=self.B('Battle_Finish')):
                    self.click(res1)
                    self.log_info("第一次没点到")
                    self.sleep(1)
                    return True
                else:
                    self.log_info("第一次点到")
                    return True
            if res := self.find_one('Battle_Finish_Soul', threshold=0.7,
                                        box=self.B('Battle_Finish_Soul'),
                                        ):
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
            return False

        if self.wait_until(check, time_out=battle_time, raise_if_not_found=False):
            return True

        self.log_warning("战斗结束超时")
        return False
