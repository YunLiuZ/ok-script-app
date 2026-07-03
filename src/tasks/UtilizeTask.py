import re
from src.tasks.BaseOmjTask import BaseOmjTask


class UtilizeTask(BaseOmjTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Utilize"

        self.default_config.update({
            "Utilize": True,
            "KekkaiActivation": True,
            "KekkaiUtilize": True,
        })
        self.config_description.update({
        })

        # 保存结界卡到期时间，供定时任务使用
        self.kekkai_expire_time = None  # 格式: "HH:MM:SS"

    def run(self):
        if self.in_home_and_back():
            self.Utilize_page()
            if self.config.get("KekkaiActivation"):
                self.KekkaiActivation()

    def _extract_kekkai_time(self, ocr_results):
        """从 OCR 结果中提取结界卡剩余时间并保存。"""
        for r in ocr_results:
            m = re.search(r'\d{2}:\d{2}:\d{2}', r.name)
            if m:
                self.kekkai_expire_time = m.group()
                self.log_info(f"结界卡剩余时间: {self.kekkai_expire_time}")
                self.info_set("结界卡到期", self.kekkai_expire_time)
                return
        self.log_warning("未能从 OCR 结果中提取到时间")


    def Utilize_page(self):
        if not self.wait_click_feature('YinYang_Lodge', threshold=0.7,
                                        box=self.B('YinYang_Lodge'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到YinYang_Lodge")
        self.info_set("步骤", "进入YinYang_Lodge")

        if text := self.ocr_and_click(['结界'],
                                  box=self.box_of_screen(0.66, 0.84, 1, 1), time_out=3):
            print(text)

        # 这一段 需要识别一个结界卡是否 已经用完了
        

    def KekkaiActivation(self):
        if text := self.ocr_and_click(['界卡'],
                                  box=self.box_of_screen(0.67, 0.36, 0.75, 0.58), time_out=3):
            print(text)

        if text := self.ocr_and_click(['太鼓', '斗鱼'],
                                  box=self.box_of_screen(0.63, 0.36, 0.8, 0.41), time_out=3):
            print(text)
            self.log_info("结界卡还在")
            # 从 OCR 结果中提取时间 (HH:MM:SS)
            self._extract_kekkai_time(text)
        if text := self.ocr_and_click(['升序'],
                                  box=self.box_of_screen(0.13, 0.12, 0.42, 0.22), time_out=3):
            print(text)
        if text := self.ocr_and_click(['全部'],
                                  box=self.box_of_screen(0.13, 0.12, 0.42, 0.22), time_out=3):
            print(text)
            text = self.ocr_and_click(['太鼓'],
                                  box=self.box_of_screen(0.28, 0.21, 0.41, 0.61), time_out=3)
        # 找到合适的星级并寄养 可以选择私有或者公开寄养 激活会变亮

    def KekkaiUtilize(self):
        if text := self.ocr_and_click(['育成'],
                                  box=self.box_of_screen(0.44, 0.36, 0.52, 0.57), time_out=3):
            print(text)
        if text := self.ocr_and_click(['智能','放入'],2,
                                  box=self.box_of_screen(0.89, 0.69, 0.94, 0.78), time_out=3):
            print(text)
        if self.ocr_and_click(['式神','寄养'],
                                  box=self.box_of_screen(0.83, 0.00, 1, 0.1), time_out=3):
            for tab in ('好友', '跨区'):
                if self.ocr_and_click(tab, box=self.box_of_screen(0.17, 0.15, 0.35, 0.22)):
                    pass
"""                    if 识别点击到可寄养的图标 
                    if self.ocr_and_click('进入','结界', box=self.box_of_screen((0.61, 0.74, 0.76, 0.82)):
                        if self.wait_o(['式神','寄养'],
                                  box=self.box_of_screen(0.83, 0.00, 1, 0.1), time_out=3):
                                  c_ve((0.17, 0.8))
                                  self.ocr_and_click('que'ren', box=self.box_of_screen(0.51, 0.7, 0.64, 0.81):
                                  sleep(2)
                                  c_ve(0.04, 0.07) 返回
                                  home_button
                                结界的返回有点特别。

"""
