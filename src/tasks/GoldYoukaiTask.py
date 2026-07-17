from src.tasks.BaseBattleTask import BaseBattleTask
class GoldYoukaiTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "日常-战斗-金币妖怪"
        self.trigger_count = 1
        self.count = 1

    def GoldYoukai_page(self):
        if self.wait_click_feature('Home_Team', threshold=0.7,
                                        box=self.B('bottom'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Team")
        self.log_info("进入组队页面")
        if self.ocr_and_click(["金币"], threshold=0.7,
                                        box=self.box_of_screen(0.11, 0.18, 0.29, 0.87),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            
            self.log_info("金币妖怪")
        else:
            self._swipe(0.22,0.22,0.22,0.82,0.2)
            self.log_info("滑到顶")
            self._swipe(0.22,0.22,0.22,0.82,0.5)
            if self.ocr_and_click(["金币"], threshold=0.7,
                                        box=self.box_of_screen(0.11, 0.18, 0.29, 0.87),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
              self.log_info("金币妖怪")
            else:self.log_warning("找不到金币妖怪")
        
        if self.ocr_and_click(["创建","队伍"], threshold=0.7,
                                        box=self.box_of_screen(0.74, 0.79, 0.94, 0.94),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            if not self.ocr_and_click(["创建","队伍"], threshold=0.7,
                                        box=self.box_of_screen(0.74, 0.79, 0.94, 0.94),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
                self.log_info("出现弹窗 再次点击")
            if text:=self.ocr_and_click(['不公开','仅邀请',],box=self.box_of_screen(0.3457, 0.5653, 0.5074, 0.6243)):
              print(text)
              self.click_relative(0.51,0.71,after_sleep=1)
            self.log_info("创建队伍")
        if text:=self.wait_ocr(['协战','队伍'],box=self.box_of_screen(0,0,0.2,0.1)):
            
          self.log_info('进入协战队伍')
          return True
        else:
          self.log_info('没有进入队伍')
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
                ok = self._invite_one(f, (0.33, 0.4), (0.22, 0.14, 0.42, 0.28))
            else:
                ok = self._invite_one(f, (0.52, 0.43), (0.42, 0.17, 0.61, 0.32))
            if not ok:
                return False
        return True
    def Leader_battle(self):
        #金币妖怪暂时不做 有点奇怪 这些识别区域是正确的
        targets = [self.config["Friend 1"]]
        if self.config["Friend 2"]:
            targets.append(self.config["Friend 2"])
        self.count = 1
        while(self.count <= self.config["AttackNumber"]):
            for i, f in enumerate(targets):
                if i == 0:
                  ok = self.ocr_and_click(f, time_out=30,box=self.box_of_screen (0.22, 0.14, 0.42, 0.28))
                else:
                  ok = self.ocr_and_click(f, time_out=30,box=self.box_of_screen (0.42, 0.17, 0.61, 0.32))
                if ok:
                    self.click_relative(0.95,0.90,after_sleep=0.5)
                    self.log_info("进入battle")
                    self.Find_finish(self.config["BattleTime"])
                    self.log_info(f"第 {self.count} 次战斗结束 总共{self.config["AttackNumber"]} 第 {self.trigger_count} 次战斗")
                    self.count+=1
                    self.trigger_count+=1
                else:
                    self.log_info("队友不在了")
                    self.Back_Home()
                    return False

        