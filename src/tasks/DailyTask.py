from src.tasks.MyBaseTask import MyBaseTask
from src.tasks.BaseOmjTask import BaseOmjTask


class DailyTask(BaseOmjTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "每日签到"
        self.description = "签到加黑碎"

    def run(self):
        if self.state.is_done_today("daily_sign"):
            self.log_info(f"今日已签到 ({self.state.done_at('daily_sign')})，跳过")
        else:
            self.Sign()

        if self.state.is_done_today("gift_shop"):
            self.log_info(f"礼包屋今日已签到 ({self.state.done_at('gift_shop')})，跳过")
        else:
            self.Gift_Shop_Sign()

    def Sign(self):
        """签到流程

        1. 确认在主页
        2. 点击签到入口 Home_Sign
        3. 点击一键完成 Sign_Button
        4. 分支判断：
           - 分支A: 检测到 Sign_Daily_Skip → 点击跳过 →
                    Daily_New_Cancel → Daily_Sign_Success → Home_Button
           - 分支B: 直接检测到 Daily_Sign_Success → Home_Button
        """
        # 1. 确认在主页，不在主页则跳过
        if not self.In_Home():
            self.log_info("不在主页")
            if self.Back_Home() is not True:
                return
        # 2. 等待签到入口出现并点击
        if not self.wait_click_feature('Home_Sign', threshold=0.7,box=self.box_of_screen(0.55, 0.5, 0.7, 0.7),
                                        raise_if_not_found=False, time_out=3):
            self.log_warning("找不到签到入口 Home_Sign")
            self.click_relative(0.64,0.6)
        self.info_set("步骤", "进入签到页面")
        # 3. 等待一键完成按钮出现并点击
        if not self.wait_click_feature('Sign_Button', threshold=0.7,box=self.box_of_screen(0,0,1,1),
                                        raise_if_not_found=False, time_out=3,):
            self.log_warning("找不到一键完成 Sign_Button")
            return
        self.info_set("步骤", "已点击一键完成")

        # 循环消除各种弹窗，直到 Daily_Sign_Success 出现
        if not self.wait_until(
            lambda: self.find_one('Daily_Sign_Success', threshold=0.7,
                                  box=self.box_of_screen(0, 0, 1, 1)),
            time_out=15,
            post_action=self._dismiss_popups,
            raise_if_not_found=False,
        ):
            self.log_warning("签到超时：未检测到 Daily_Sign_Success")
            return

        # 签到成功 → 点击 → 返回主页
        self.wait_click_feature('Daily_Sign_Success', threshold=0.7,
                                box=self.box_of_screen(0, 0, 1, 1),
                                raise_if_not_found=False, time_out=3)
        self.wait_click_feature('Back', threshold=0.7,
                                box=self.box_of_screen(0, 0, 0.2, 0.2),
                                raise_if_not_found=False, time_out=3)
        if not self.In_Home():
            self.log_info("不在主页")
            if self.Back_Home() is not True:
                return

        # self.state.mark_done("daily_sign")  # 测试期间注释
        self.log_info("签到完成 ✅ (测试模式，未持久化)", notify=True)

    def _click_then_wait_next(self, target, next_target, step_name):
        """点击 target，然后边消弹窗边等 next_target 出现。"""
        full = self.box_of_screen(0, 0, 1, 1)
        if not self.wait_click_feature(target, threshold=0.7, box=full,
                                        raise_if_not_found=False, time_out=5):
            self.log_warning(f"找不到 {target}")
            return False
        self.info_set("步骤", step_name)
        if next_target is None:
            return True  # 最后一步，不需要等下一个
        return self.wait_until(
            lambda: self.find_one(next_target, threshold=0.7, box=full),
            time_out=10,
            post_action=self._dismiss_popups,
            raise_if_not_found=False,
        )

    def _dismiss_popups(self):
        """消除可能出现的各种弹窗。"""
        for name in ('Confirm', 'Sign_Daily_Skip', 'Daily_New_Cancel', 'Cancel_Old'):
            if btn := self.find_one(name, threshold=0.7,
                                    box=self.box_of_screen(0, 0, 1, 1)):
                self.click_box(btn, after_sleep=0.5)
                self.info_set("步骤", f"点击 {name}")

    def Gift_Shop_Sign(self):
        """礼包屋签到流程：Home_Store → Gift_Store → Gift_Daily → Gift_Daily_Finish → Gift_Finish → Home_Button"""
        if not self.In_Home():
            self.log_warning("不在主页，跳过礼包屋签到")
            if self.Back_Home() is not True:
                return

        steps = [
            ('Home_Store',       'Gift_Store',        '进入商店'),
            ('Gift_Store',       'Gift_Daily',        '进入礼包商店'),
            ('Gift_Daily',       'Gift_Daily_Finish', '进入每日礼包'),
            ('Gift_Daily_Finish','Gift_Finish',       '每日礼包完成'),
            ('Gift_Finish',      'Home_Button',       '礼包完成'),
            ('Home_Button',      None,                '返回主页'),
        ]
        for target, next_target, step_name in steps:
            if not self._click_then_wait_next(target, next_target, step_name):
                return

        # self.state.mark_done("gift_shop")  # 测试期间注释
        self.log_info("礼包屋签到完成 ✅ (测试模式，未持久化)", notify=True)

    # ---------- 测试辅助方法 ----------

    def find_home_sign(self):
        """测试用：在当前帧中匹配 Home_Sign 模板"""
        return self.find_one('Home_Sign', threshold=0.6)
