from src.tasks.BaseBattleTask import BaseBattleTask


class AreaBossTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "地域鬼王"
        self.trigger_count = 0

    def run(self):
        self.SwitchSoul_by_num(int(self.config["Preset Group"]),int(self.config["Preset Team"]))
    def AreaBoss(self):
        self.In_Home()

        if not self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        self.info_set("步骤", "进入探索页面")

        if not self.Find_And_Click_Home("鬼王"):
            if not self.wait_click_feature('Areaboss', threshold=0.7,
                                        box=self.B('ocr_bottom'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
                self.log_warning("找不到地域鬼王")
        self.info_set("步骤", "进入地域鬼王")

        if not self.wait_click_feature('Areaboss_Filter', threshold=0.7,
                                        box=self.B('Areaboss_Filter '),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Areaboss_Filter")
        self.info_set("步骤", "进入Areaboss_Filter")

        if not self.ocr_and_click('收藏',self.B("Areaboss_Filter_Page")):
            self.click_relative(0.94,0.89)
            self.sleep(1)
    def Battle(self,num:int):
        while(self.trigger_count < num):
            pass
        
        
        