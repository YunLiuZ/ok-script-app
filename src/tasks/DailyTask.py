from src.tasks.BaseOmjTask import BaseOmjTask


class DailyTask(BaseOmjTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "每日签到"
        self.description = "签到加黑碎"

    def run(self):
        # if self.state.is_done_today("daily_sign"):
        #     self.log_info(f"今日已签到 ({self.state.done_at('daily_sign')})，跳过")
        # else:
        #     self.Sign()

        if self.state.is_done_today("gift_shop"):
            self.log_info(f"礼包屋今日已签到 ({self.state.done_at('gift_shop')})，跳过")
        else:
            self.Gift_Shop_Sign()

    def Sign(self):
        """签到流程"""
        # 1. 确认在主页
        self.In_Home()

        # 2. 点击签到入口
        if not self.wait_click_feature('Home_Sign', threshold=0.7,
                                        box=self.B('Home_Sign'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到签到入口 Home_Sign")
            self.click_relative(0.64, 0.6)
        self.info_set("步骤", "进入签到页面")

        self.click_relative(0.92, 0.22, after_sleep=1)

        # 3. 点击一键完成
        if not self.wait_click_feature('Sign_Button', threshold=0.7,
                                        box=self.B('Sign_Button'),
                                        raise_if_not_found=False, time_out=3, after_sleep=2):
            if texts := self.ocr(box=self.B('ocr_sign_button'), match='完成'):
                self.click_box(texts[0], after_sleep=2)
                self.info_set("步骤", "找不到一键完成")
                self.click_relative(0.9, 0.9, after_sleep=1)
            self.log_warning("找不到一键完成 Sign_Button")
        self.info_set("步骤", "已点击一键完成")

        # 结界式神经验满
        if texts := self.ocr(box=self.B('ocr_confirm_dialog'), match='确认'):
            self.click_box(texts[0], after_sleep=2)
            self.info_set("步骤", "点击 确认")
        else:
            self.info_set("确认弹窗", "无")

        # 每日签到的弹窗
        if not self.wait_click_feature('Cancel_Old', threshold=0.7,
                                        box=self.B('Cancel_Old'),
                                        raise_if_not_found=False, time_out=3):
            self.log_warning("找不到一键完成每日签到关闭")

        if not self.wait_click_feature('Sign_Daily_Skip', threshold=0.7,
                                        box=self.B('Sign_Daily_Skip'),
                                        raise_if_not_found=False, time_out=3):
            if texts := self.ocr(box=self.B('ocr_skip_topright'), match='跳过'):
                self.click_box(texts[0], after_sleep=2)
                self.info_set("步骤", "跳过")
                if not self.wait_click_feature('Daily_New_Cancel', threshold=0.7,
                                                box=self.B('Daily_New_Cancel'),
                                                raise_if_not_found=False, time_out=3):
                    self.log_warning("找不到万花关闭")
                    self.click_relative(0.9, 0.09, after_sleep=1)

        if not self.wait_click_feature('Daily_Sign_Success', threshold=0.7,
                                        box=self.B('Daily_Sign_Success'),
                                        raise_if_not_found=False, time_out=3):
            if not (texts := self.ocr(box=self.B('ocr_sign_result'), match='成功')):
                self.click_relative(0.25, 0.1)

        # 签到成功 → 点击 → 返回主页
        self.wait_click_feature('Daily_Sign_Success', threshold=0.7,
                                box=self.B('full'),
                                raise_if_not_found=False, time_out=3)
        self.wait_click_feature('Back', threshold=0.7,
                                box=self.B('Back'),
                                raise_if_not_found=False, time_out=3)
        if not self.In_Home():
            self.log_info("不在主页")
            if self.Back_Home() is not True:
                return

        # self.state.mark_done("daily_sign")  # 测试期间注释
        self.log_info("签到完成", notify=True)

    def Gift_Shop_Sign(self):
        """礼包屋签到流程"""
        if not self.In_Home():
            self.log_warning("不在主页")
            self.Back_Home()
        if not self.wait_click_feature('Home_Store', threshold=0.7,
                                        box=self.B('Home_Store'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("找不到Home_Store")

        # self.Find_And_Click_Home('商店')
        self.click_relative(0.5, 0.5, after_sleep=2)
        self.log_info("点击中间")
        if not self.in_store():
            self.Back_Home()
            # self.Find_And_Click_Home('商店')
            if not self.wait_click_feature('Home_Store', threshold=0.7,
                                        box=self.B('Home_Store'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
                self.log_info("找不到Home_Store")

        self.Find_And_Click_Home('礼包屋')
        if not self.wait_click_feature('Gift_Daily', threshold=0.7,
                                        box=self.B('Gift_Daily'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("找不到Gift_Daily")
        if not self.wait_click_feature('Gift_Daily_Finish', threshold=0.7,
                                        box=self.B('Gift_Daily_Finish'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("找不到Gift_Daily_Finish")
        if not self.wait_click_feature('Gift_Finish', threshold=0.7,
                                        box=self.B('Gift_Finish'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("找不到Gift_Finish")
        if not self.wait_click_feature('Gift_Finish', threshold=0.7,
                                        box=self.B('Gift_Finish'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("找不到Gift_Finish")

        self.wait_click_feature('Home_Button', threshold=0.7,
                                box=self.B('Home_Button'),
                                raise_if_not_found=False, time_out=3)
        # self.state.mark_done("gift_shop")  # 测试期间注释
        self.log_info("礼包屋签到完成", notify=True)

    # ---------- 测试辅助方法 ----------

    def find_home_sign(self):
        """测试用：在当前帧中匹配 Home_Sign 模板"""
        return self.find_one('Home_Sign', threshold=0.6)
