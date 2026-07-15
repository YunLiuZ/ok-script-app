from src.tasks.BaseBattleTask import BaseBattleTask


class AreaBossTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "地域鬼王"
        self.trigger_count = 1
        self.count = 1

    def run(self):
        if not self.logged_in:
            return False
        self.in_home_and_back()
        if self.config["Preset Enable"]:
            group, team = self._parse_preset()
            self.SwitchSoul_by_num(group, team)
        if not self.AreaBoss_page():
            self.log_warning("找不到鬼王页面")
            return False
        if not self.Battle():
            self.log_warning("battle失败")
            return False
        self.sleep(1)
        self.Back_Home()
        return True

    def AreaBoss_page(self):
        # self.In_Home()

        
        if self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        self.info_set("步骤", "进入探索页面")
        if self.wait_click_feature('Exploration_AreaBoss', threshold=0.7,
                                        box=self.B('bottom'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("探索 AreaBoss")
            self.info_set("步骤", "进入探索页面")
            return True
        else:
            if text:=self.ocr_and_click(['地域','鬼王'],1,box=self.box_of_screen(0.48,0.94,0.55,0.98)):
                print(text)
                return True
            else:
                return False
        

    def Battle(self):
        self.log_info("进入battle")
        self.count = 1

        
        while(self.count <= self.config["AttackNumber"]):
            
            if text:=self.ocr_and_click(['筛','选'],0.5,box=self.B('Areaboss_Filter')):
                print(text)
            if text:=self.ocr_and_click(['收','藏'],0.5,box=self.B('Areaboss_Filter_Page')):
                print(text)
            
            group_rows = {1: 0.36, 2: 0.58,3:0.78}
            self.click_nth('x', 0.86, group_rows,self.trigger_count ,self.count)
            if lock_res := self.Lock_team((0.86,0.88,1,1)):
                self.log_info("锁上了")
            else:
                self.log_info("没锁")
             

            if text:=self.ocr_and_click(['挑战'],0.5,box=self.box_of_screen(0.86,0.73,0.93,0.79)):
                print(text)
            if not lock_res:
                pass

            self.Find_finish(self.config["BattleTime"])
            
            if not self.wait_click_feature('Daily_New_Cancel', threshold=0.7,
                                    box=self.B('Daily_New_Cancel'),
                                    raise_if_not_found=False, time_out=5, after_sleep=1):
                self.log_warning("找不到Daily_New_Cancel")
                self.Back_Home()
                return False
            self.log_info(f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
            self.count+=1
            self.trigger_count+=1
        return True

    def Battle_process(self):
        pass

        
        
        