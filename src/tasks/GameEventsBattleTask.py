from src.tasks.BaseBattleTask import BaseBattleTask

from datetime import datetime

class GameEventsBattleTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "活动"
        self.generalclimb = 0
        self.apmode = 0

        self.default_config.update({
            "ApMode": True,
            "GeneralClimb": True,
            "GeneralClimbNum": 10,
            
        })
        self.config_description.update({
            "AttackNumber": "挂体力的次数",

        })

    def run(self):
        # self.SwitchSoul_by_num(int(self.config["Preset Group"]),int(self.config["Preset Team"]))
        # self.reset()
        self.Battle_page()
        self.Battle()

    def Battle_page(self):
        self.In_Home()
        self.click_relative(0.34,0.25,after_sleep=2)
        if text:=self.ocr_and_click(['鸣','鼓','战斗'],1,box=self.box_of_screen(0.18,0.41,0.25,0.64)):
            print(text)

        # self.ocr_and_click('挑战')


    def Battle(self):
        if not (self.ocr(['养成','协战','式神录'],box=self.box_of_screen(0.65,0.82,0.84,0.9))):
            self.log_warning('没进战斗页面')
            return
        self.Change_mode()
        while(self.config["GeneralClimb"] and self.generalclimb < self.config["GeneralClimbNum"]):

            self.Battle_process()
            self.generalclimb += 1
            self.log_info(f"第 {self.generalclimb} 次爬塔战斗结束 总共{self.config["GeneralClimbNum"]}")

        while(self.config["ApMode"] and self.apmode < self.config["AttackNumber"]):
            if self.ocr(box=self.box_of_screen(0.929,0.762,0.938,0.788)):
                self.click_relative(0.973,0.776,after_sleep=0.5)
            self.Battle_process()
            self.apmode += 1
            self.log_info(f"第 {self.apmode} 次体力爬塔战斗结束 总共{self.config["AttackNumber"]}")
        self.Back_Home()
           
            
    def Change_mode(self):
        if self.ocr(box=self.box_of_screen(0.929,0.762,0.938,0.788)):
            self.log_warning('现在是刷票')
            return True
        else:           
            self.click_relative(0.973,0.776,after_sleep=0.5)
            self.log_warning('切换')

            
            

    def Battle_process(self):
        if text := self.wait_click_ocr(['挑战'],box=self.box_of_screen(0.88,0.83,0.95,0.91)):
                print(text)
        self.sleep(12)
        self.log_info(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if not self.wait_click_feature('Battle_Finish', threshold=0.7,
                                    box=self.B('Battle_Finish'),
                                    raise_if_not_found=False, time_out=10, after_sleep=1):
            self.log_warning("找不到Battle_Finish")
        self.log_info(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.info_set("步骤", "进入Battle_Finish")


        
