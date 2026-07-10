from src.tasks.BaseOmjTask import BaseOmjTask


class DelegationTask(BaseOmjTask):

    # 配置项 → 游戏内中文翻译
    DELEGATION_MAP = {
        "Bird Feather": "鸟之羽",
        "Find Earring": "寻找耳环",
        "Cat Boss": "猫老大",
        "Miyoshino": "接送弥助",
        "Strange Trace": "奇怪的痕迹",
        "Miyoshino Painting": "弥助的画",
        "以鱼为礼":"以鱼为礼"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "式神委派"
        self.default_config.update({
            "Bird Feather": True,
            "Find Earring": True,
            "Cat Boss": True,
            "Miyoshino": True,
            "Strange Trace": True,
            "Miyoshino Painting": True,
            "以鱼为礼":True ,
        })
        self.config_description.update({
            "Bird Feather": "bird_feather_help",
            "Find Earring": "find_earring_help",
            "Cat Boss": "Cat Boss_help",
            "Miyoshino": "Miyoshino_help",
            "Miyoshino Painting": "Miyoshino Painting_help",
            "Strange Trace": "Strange Trace_help",
        })

    def run(self):
        if self.in_home_and_back():
            self.Delegation_page()
            self.Finish_delegation()
            self.Delegation_selet()
            self.Back_Home()

    def Delegation_page(self):
        """导航到式神委派页面"""
        self.log_info('导航')

        if not self.wait_click_feature('Home_Explore', threshold=0.7,
                                        box=self.B('Home_Explore'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到探索 Home_Sign")
        self.info_set("步骤", "进入探索页面")
        if (text := self.ocr_and_click(['式神', '委派'], 1,
                                            box=self.box_of_screen(0.3293, 0.8708, 0.407, 0.9833))):
            print(text)
            self.log_info('找到式神委派')
            return True
        else :
            self.log_info('找不到式神委派')
            return False

    def Delegation_selet(self):
        """根据用户配置，在委派列表中识别并点击已启用的委派任务。"""
        self.log_info('进入委派任务')
        self._swipe(0.85, 0.80, 0.85, 0.30, 0.5)

        # 一次 OCR 扫描整页，过滤掉根本不在屏幕上的任务
        visible_texts = set()
        if results := self.ocr(box=self.B("Delegation")):
            for r in results:
                visible_texts.add(r.name)

        # 只循环当前屏幕上存在的已启用任务
        pending = []
        for key, translation in self.DELEGATION_MAP.items():
            if not self.config.get(key, False):
                continue
            if translation in visible_texts:
                pending.append((key, translation))
        self.log_info(f"检测到 {len(pending)} 个可见任务: {[t for _, t in pending]}")

        for key, translation in pending:
            if not self.ocr_and_click(translation, 1, box=self.B("Delegation")):
                self.log_info(f'找不到委派任务: {translation} ({key})')
            else:
                self.info_set("委派", f"已点击 {translation}")
                if self.wait_ocr("召回", box=self.box_of_screen(0.73, 0.35, 0.93, 0.53),
                                 threshold=0.8, time_out=2, raise_if_not_found=False):
                    self.log_info('找到还未完成的任务')
                    if not (text := self.ocr_and_click(['跳过'], 2,
                                                        box=self.box_of_screen(0.72, 0.54, 0.85, 0.69))):
                        print(text)
                        self.log_info('找不到跳过')
                        continue
                else:
                    self.Delegation()
                    self._swipe(0.85, 0.80, 0.85, 0.30, 0.5)

    def Finish_delegation(self):
        self.log_info('检查是否有已完成的委派')
        while (text := self.ocr_and_click(['完成'], 1,
                                        box=self.B("Delegation"), raise_if_not_found=False)):
            print(text)
            self.click_relative(0.89, 0.44, after_sleep=1)
            self.wait_until(condition=lambda: self.ocr_and_click(['完成'], 1, time_out=0.5,
                                            box=self.box_of_screen(0.73, 0.35, 0.93, 0.53)),
                                            time_out=20, pre_action=lambda: self.click_relative(0.47, 0.81, after_sleep=0.5)
                                            , raise_if_not_found=False)

            if not self.ocr_and_click(['顺利', "达成"], 1,
                                        box=self.box_of_screen(0.26, 0.05, 0.8, 0.29), raise_if_not_found=False):
                self.log_warning("找不到Battle_Success_Soul")
        self.log_info('没有待完成')

    def Delegation(self):

        if not (text := self.ocr_and_click(['跳过'], 2,
                                            box=self.box_of_screen(0.49, 0.69, 0.59, 0.79))):
            print(text)
            self.log_info('找不到跳过')
        if not (text := self.ocr_and_click(['委派'], 2,
                                            box=self.box_of_screen(0.73, 0.35, 0.93, 0.53))):
            print(text)
            self.log_info('找不到式神委派')
        if not (text := self.ocr_and_click(['一键'], 2,
                                        box=self.box_of_screen(0.85, 0.59, 0.98, 0.88))):
            print(text)
            self.log_info('找不到一键')
        if not (text := self.ocr_and_click(['出发'], 2,
                                        box=self.box_of_screen(0.85, 0.59, 0.98, 0.88))):
            print(text)
            self.log_info('找不到出发')
            if text := self.wait_ocr(['式神'],
                                    box=self.box_of_screen(0, 0, 0.17, 0.1), time_out=3):
                return True
            else: return False
