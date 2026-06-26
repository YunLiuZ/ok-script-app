from src.tasks.BaseBattleTask import BaseBattleTask


class AreaBossTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "地域鬼王"
        self.trigger_count = 1
        self.count = 1

    def run(self):
        # self.SwitchSoul_by_num(int(self.config["Preset Group"]),int(self.config["Preset Team"]))
        self.AreaBoss_page()
        self.Battle()

    def AreaBoss_page(self):
        # self.In_Home()

        if not self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        self.info_set("步骤", "进入探索页面")

        if text:=self.ocr_and_click(['地域','鬼王'],1,box=self.box_of_screen(0.48,0.94,0.55,0.98)):
            print(text)
        

    def Battle(self):
        self.log_info("进入battle")
        self.count = 1
        
        while(self.count <= self.config["AttackNumber"]):
            
            if text:=self.ocr_and_click(['筛','选'],0.5,box=self.B('Areaboss_Filter')):
                print(text)
            if text:=self.ocr_and_click(['收','藏'],0.5,box=self.B('Areaboss_Filter_Page')):
                print(text)
            
            group_rows = {1: 0.36, 2: 0.58}
            self.click_nth('x', 0.86, group_rows,self.trigger_count ,self.count)
            if text:=self.ocr_and_click(['挑战'],0.5,box=self.box_of_screen(0.86,0.73,0.93,0.79)):
                print(text)

            if not self.wait_click_feature('Battle_Success', threshold=0.7,
                                    box=self.B('Battle_Success'),
                                    raise_if_not_found=False, time_out=60, after_sleep=1):
                self.log_warning("找不到Battle_Success")

            self.click_relative(0.6,0.3,after_sleep=0.5)
            if not self.wait_click_feature('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish'),
                                    raise_if_not_found=False, time_out=5, after_sleep=1):
                self.log_warning("找不到Battle_Finish")
            if not self.wait_click_feature('Daily_New_Cancel', threshold=0.7,
                                    box=self.B('Daily_New_Cancel'),
                                    raise_if_not_found=False, time_out=5, after_sleep=1):
                self.log_warning("找不到Daily_New_Cancel")
            self.log_info(f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
            self.count+=1
            self.trigger_count+=1
        self.sleep(1)     
        self.Back_Home()             
    def Battle_process(self):
        pass

        
        
        