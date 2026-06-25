from src.tasks.BaseBattleTask import BaseBattleTask

from datetime import datetime

class GameEventsBattleTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "活动"
        self.trigger_count = 0

    def run(self):
        # self.SwitchSoul_by_num(int(self.config["Preset Group"]),int(self.config["Preset Team"]))
        # self.reset()
        self.Battle_page()
        self.Battle(int(self.config["AttackNumber"]))
    def Battle_page(self):
        self.In_Home()
        self.click_relative(0.34,0.25,after_sleep=2)
        if text:=self.ocr_and_click(['鸣','鼓','战斗'],1,box=self.box_of_screen(0.18,0.41,0.25,0.64)):
            print(text)

        # self.ocr_and_click('挑战')


    def Battle(self,num:int):
        if not (self.ocr(['养成','协站','式神录'],box=self.box_of_screen(0.65,0.82,0.84,0.9))):
            return
            
        while(self.trigger_count < num ):
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

            self.trigger_count += 1
            self.log_info(f"第 {self.trigger_count} 次战斗结束 总共{int(self.config["AttackNumber"])}")

