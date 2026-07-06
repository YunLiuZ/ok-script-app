from src.tasks.BaseOmjTask import BaseOmjTask


class BaseBattleTask(BaseOmjTask):
    """战斗任务基类：统一管理阵容锁定、预设队伍切换等战斗配置。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_config.update({

            "Lock Team Enable": True,
            "Preset Enable": False,
            "Preset Group": "1",
            "Preset Team": "1",
            "Group Name": "",
            "Team Name": "",
            "AttackNumber":10,
            "BattleTime": 30,
        })

        self.config_description.update({
            "Lock Team Enable": "开启后每次战斗前锁定当前阵容，防止误操作切换队伍。",
            "Preset Enable": "开启后战斗前自动切换到指定的预设队伍。",
            "Preset Group": "预设队伍所在的组编号（1-7），用于 SwitchSoul_by_num。",
            "Preset Team": "该组中的预设队伍编号（1-4），用于 SwitchSoul_by_num。",
            "BattleTime": "大致的通过时间 一般情况下不用设置 战斗时间超过一分钟 按大概时间加30秒即可"
        })

        self.config_type.update({
            # 不指定 type，框架根据 value 类型自动选择控件：
            # bool → SwitchButton, str → LineEdit, int → SpinBox
        })


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
        self.in_home_and_back()
        self.ocr_and_click('式神',box=self.B('Home_Shikigami_Chronicles'))

        self.wait_click_ocr(match='预设',
                            box=self.B('Home_Shikigami_Presets'),time_out=3,after_sleep=1)
        self._swipe(0.91,0.22,0.91,0.77,0.5)

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
        self.in_home_and_back()

    def Lock_team(self,confirm_box:tuple):
        if res := self.find_feature("Lock_Team",threshold=0.9,box=self.box_of_screen(*confirm_box)) :
            self.log_info("检查到没上锁")
            if self.config["Lock Team Enable"]:
                self.click(res[0]) #锁上了
                self.log_info("点击上锁")
                return True
            else :
                return False #解锁
        else:
            if self.config["Lock Team Enable"]:
                self.log_info("上锁")
                return True #锁上了
            else:
                self.log_info("点击解锁")
                self.click(res[0]) #解锁了
                return False
    def Change_team(self):
        self.ocr_and_click("预","设",box=(0,0.87,0.15,1))# (0.8781, 0.7701, 0.9625, 0.8535)
        group_rows = {1: 0.36, 2: 0.45, 3: 0.54, 4: 0.63, 5: 0.72, 6: 0.81, 7: 0.90}
        self.click_nth('x', 0.76, group_rows, int(self.config["Preset Group"]), "预设组")

        team_rows = {1: 0.22, 2: 0.44, 3: 0.64, 4: 0.85}
        self.click_nth('x', 0.77, team_rows, int(self.config["Preset Team"]), "预设队伍")

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
