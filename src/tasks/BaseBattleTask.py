from src.tasks.BaseOmjTask import BaseOmjTask


class BaseBattleTask(BaseOmjTask):
    """战斗任务基类：统一管理阵容锁定、预设队伍切换等战斗配置。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_config.update({

            "Lock Team Enable": False,
            "Preset Enable": False,
            "Preset Group": "1",
            "Preset Team": "1",
            "Group Name": "",
            "Team Name": "",
            "AttackNumber":"10",
        })

        self.config_description.update({
            "Lock Team Enable": "开启后每次战斗前锁定当前阵容，防止误操作切换队伍。",
            "Preset Enable": "开启后战斗前自动切换到指定的预设队伍。",
            "Preset Group": "预设队伍所在的组编号（1-7），用于 SwitchSoul_by_num。",
            "Preset Team": "该组中的预设队伍编号（1-4），用于 SwitchSoul_by_num。",
        })

        self.config_type.update({
            # 不指定 type，框架根据 value 类型自动选择控件：
            # bool → SwitchButton, str → LineEdit, int → SpinBox
        })


    def SwitchSoul_by_name(self):
        self.In_Home()
        self.Find_And_Click_Home('式神录')
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
        """按编号切换预设队伍（从 config 读取 Preset Group / Preset Team）。"""
        self.In_Home()
        self.Find_And_Click_Home('式神录')
        self.wait_click_ocr(match='预设',
                            box=self.get_box_by_name('Home_Shikigami_Presets'))

        group_rows = {1: 0.17, 2: 0.27, 3: 0.35, 4: 0.47, 5: 0.56, 6: 0.67, 7: 0.75}
        self.click_nth('x', 0.91, group_rows, group, "预设组")

        team_rows = {1: 0.22, 2: 0.44, 3: 0.64, 4: 0.85}
        self.click_nth('x', 0.77, team_rows, team, "预设队伍")