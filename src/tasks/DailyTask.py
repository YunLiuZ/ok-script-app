from src.tasks.BaseOmjTask import BaseOmjTask


class DailyTask(BaseOmjTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "每日签到！"
        self.description = "签到，黑蛋"

        self.default_config.update({
            "Orchids": True,
            "Friend 1": "",
        })
        self.config_description.update({
            "Friend 1": "在使用之前，请给好友发个消息，保证好友在最近列表，同心之兰队友",
        })

    def run(self):
        if not self.logged_in:
            return False
        # if self.config["Orchids"]:
        #     self.Orchids()
        self.in_home_and_back()
        if not self.Sign():
            return False
        if not self.Gift_Shop_Sign():
            return False
        return True



        # if self.state.is_done_today("daily_sign"):
        #     self.log_info(f"今日已签到 ({self.state.done_at('daily_sign')})，跳过")
        # else:
        #     self.Sign()
        #
        # if self.state.is_done_today("gift_shop"):
        #     self.log_info(f"礼包屋今日已签到 ({self.state.done_at('gift_shop')})，跳过")
        # else:
        #     self.Gift_Shop_Sign()

    def Sign(self):
        """签到流程"""
        self.in_home_and_back()

        # 点击签到入口
        if not self.wait_click_feature('Home_Sign', threshold=0.7,
                                        box=self.B('Home_Sign'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到签到入口 Home_Sign")
        self.log_info("进入签到页面")
        self.click_relative(0.92, 0.22, after_sleep=1)

        # 点击一键完成
        if self.wait_click_feature('Sign_Button', threshold=0.7,
                                   box=self.B('Sign_Button'),
                                   raise_if_not_found=False, time_out=5,after_sleep=1):
            self.log_info("已点击一键完成")
        else:
            self.log_info("没有一键完成")

        # 结界式神经验满弹窗
        if texts := self.wait_ocr(match='确认', box=self.B('ocr_confirm_dialog'),
                             threshold=0.8,time_out=1):
            self.click_box(texts[0])
            self.log_info("点击 确认")
        else:
            self.log_info("无")
        self.sleep(2)

        def check():
            if res := self.find_one('Battle_Finish', threshold=0.7,
                                    box=self.box_of_screen(0.3, 0.3, 0.8, 0.8)):
                self.log_info("五日")
                self.click(res)
                if not self.wait_click_feature('Daily_New_Cancel', threshold=0.7,
                                               box=self.box_of_screen(0.64, 0.09, 0.75, 0.21),
                                               raise_if_not_found=False, time_out=5):
                    self.log_info("找不到一键完成每日签到关闭")
                return True
            if res := self.find_one('Daily_New_Cancel', threshold=0.7,
                                    box=self.box_of_screen(0.64, 0.09, 0.75, 0.21)):
                self.click(res, after_sleep=1)
                self.log_info("每日签到关闭")
                return True
            return False

        if not self.wait_until(check, time_out=5, raise_if_not_found=False):
            self.log_warning("没有签到或者签到失败")
        # 跳过
        if not self.wait_click_feature('Sign_Daily_Skip', threshold=0.7,
                                        box=self.B('Sign_Daily_Skip'),
                                        raise_if_not_found=False, time_out=3):
            if texts := self.ocr(box=self.B('ocr_skip_topright'), match='跳过'):
                self.click_box(texts[0], after_sleep=2)
                self.log_info( "跳过")
                if not self.wait_click_feature('Daily_New_Cancel', threshold=0.7,
                                                box=self.B('Daily_New_Cancel'),
                                                raise_if_not_found=False, time_out=3):
                    self.log_warning("找不到万花关闭")
                    self.click_relative(0.9, 0.09, after_sleep=1)

        # 签到成功
        if not self.wait_click_feature('Daily_Sign_Success', threshold=0.7,
                                        box=self.B('Daily_Sign_Success'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.ocr_and_click("成功", box=self.B('Daily_Sign_Success'))

        # 返回主页
        if self.wait_click_feature('Home_Button', threshold=0.7,
                                box=self.B('Home_Button'),
                                raise_if_not_found=False, time_out=3,after_sleep=2):
            self.log_info("签到完成")
            return True

    def Gift_Shop_Sign(self):
        """礼包屋签到流程"""
        self.in_home_and_back()

        if not self.wait_click_feature('Home_Store', threshold=0.7,
                                        box=self.B('Home_Store'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("找不到Home_Store")

        self.click_relative(0.5, 0.5, after_sleep=2)
        self.log_info("点击中间")
        if not self.in_store():
            self.Back_Home()
            if not self.wait_click_feature('Home_Store', threshold=0.7,
                                            box=self.B('Home_Store'),
                                            raise_if_not_found=False, time_out=3, after_sleep=1):
                self.log_info("找不到Home_Store")

        self.ocr_and_click('礼包', box=self.B('Gift_Store'))
        if not self.wait_click_feature('Gift_Daily', threshold=0.7,
                                        box=self.B('Gift_Daily'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_info("找不到Gift_Daily")
        if not self.wait_click_feature('Gift_Daily_Finish', threshold=0.7,
                                        box=self.B('Gift_Daily_Finish'),
                                        raise_if_not_found=False, time_out=3, after_sleep=2):
            self.log_info("找不到Gift_Daily_Finish")

        if self.ocr_and_click(['获得', '奖励'], box=self.box_of_screen(0.35, 0.24, 0.65, 0.37),
                              raise_if_not_found=False):
            self.log_info("找到获得奖励")
            self.sleep(0.5)
            self.click_relative(0.2, 0.2, after_sleep=0.5)
        else:
            self.log_info("找不到奖励")

        if self.wait_click_feature('Home_Button', threshold=0.7,
                                box=self.B('Home_Button'),
                                raise_if_not_found=False, time_out=3,after_sleep=2):
            return True
        # self.state.mark_done("gift_shop")  # 测试期间注释
        self.log_info("礼包屋签到完成", notify=True)

    def Orchids(self):
        self.in_home_and_back()
        self.click_nth('y', 0.89, self.rows, 8, "预设组")

        if not (text := self.ocr_and_click(['最近'], 1,
                                             box=self.box_of_screen(0.20, 0.13, 0.27, 0.19))):
            self.log_info('找不到最近页面')
        if not (text := self.ocr_and_click(['最近'], 1,
                                             box=self.box_of_screen(0.20, 0.13, 0.27, 0.19))):
            self.log_info('找不到最近页面')
        if not (text := self.ocr_and_click(self.config["Friend 1"], 1,
                                             box=self.box_of_screen(0.16, 0.22, 0.28, 0.82))):
            self.log_info('找不到好友')
        if not self.wait_click_feature('Orchids', threshold=0.7,
                                        box=self.box_of_screen(0.8383, 0.141, 0.8852, 0.2313),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到同心之兰")
        if not (text := self.ocr_and_click("30", 1,
                                             box=self.box_of_screen(0.66, 0.85, 0.74, 0.91))):
            self.log_info('找不到赠送')

    # ---------- 测试辅助方法 ----------

    def find_home_sign(self):
        """测试用：在当前帧中匹配 Home_Sign 模板"""
        return self.find_one('Home_Sign', threshold=0.6)
