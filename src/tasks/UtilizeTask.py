import re
from src.tasks.BaseOmjTask import BaseOmjTask


class UtilizeTask(BaseOmjTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "日常-结界"

        self.default_config.update({
            "KekkaiActivation": True,
            "KekkaiUtilize": True,
            "寄养优先": "好友优先",
            "卡片优先级": "Douyu优先",
            "检测对象": "都检测",
        })
        self.config_description.update({
            "寄养优先": "优先搜索好友寄养还是跨区寄养。",
            "卡片优先级": "优先选择哪一种结界卡。",
            "检测对象": "搜索时检测哪些结界卡。",
        })
        self.config_type.update({
            "寄养优先": {
                "type": "drop_down",
                "options": ["好友优先", "跨区优先"],
            },
            "卡片优先级": {
                "type": "drop_down",
                "options": ["Douyu优先", "Shop_Kaiko优先"],
            },
            "检测对象": {
                "type": "drop_down",
                "options": ["都检测", "只检测Douyu", "只检测Shop_Kaiko"],
            },
        })

        # 保存结界卡到期时间，供定时任务使用
        self.kekkai_expire_time = None  # 格式: "HH:MM:SS"

    def run(self):
        if self.in_home_and_back():
            self.Utilize_page()
            if self.config.get("KekkaiActivation"):
                self.KekkaiActivation()

            if self.config.get("KekkaiUtilize"):
                self.KekkaiUtilize()
        self.Back_Home()
            

    def _extract_kekkai_time(self, ocr_results):
        """从 OCR 结果中提取结界卡剩余时间并保存。"""
        for r in ocr_results:
            m = re.search(r'\d{2}:\d{2}:\d{2}', r.name)
            if m:
                self.kekkai_expire_time = m.group()
                self.log_info(f"寄养剩余时间: {self.kekkai_expire_time}")
                return
        self.log_warning("未能从 OCR 结果中提取到时间")


    def Utilize_page(self):
        if not self.wait_click_feature('YinYang_Lodge', threshold=0.7,
                                        box=self.B('YinYang_Lodge'),
                                        raise_if_not_found=False, time_out=6, after_sleep=1):
            self.log_warning("找不到YinYang_Lodge")
        self.info_set("步骤", "进入YinYang_Lodge")

        if not self.wait_click_feature('Utilize_Kekkai', threshold=0.7,
                                        box=self.box_of_screen(0.82, 0.84, 0.9, 0.99),
                                        raise_if_not_found=False, time_out=6, after_sleep=1):
            if not (text := self.ocr_and_click(['结界'],
                                  box=self.box_of_screen(0.66, 0.84, 1, 1), time_out=6)):
                
                self.log_warning("找不到Utilize_Kekkai")
            else:
                print(text)
        self.info_set("步骤", "进入Utilize_Kekkai")

        
        self.sleep(1)

        # 这一段 需要识别一个结界卡是否 已经用完了
        

    def KekkaiActivation(self):
        if text := self.ocr_and_click(['界卡'],
                                  box=self.box_of_screen(0.67, 0.36, 0.75, 0.58), time_out=6):
            print(text)

        if text := self.ocr_and_click(['太鼓', '斗鱼'],
                                  box=self.box_of_screen(0.63, 0.36, 0.8, 0.41), time_out=6):
            print(text)
            self.log_info("结界卡还在")
            # 从 OCR 结果中提取时间 (HH:MM:SS)
            self._extract_kekkai_time(text)
            return True
        if text := self.ocr_and_click(['升序'],
                                  box=self.box_of_screen(0.13, 0.12, 0.42, 0.22), time_out=6):
            print(text)
        if text := self.ocr_and_click(['全部'],
                                  box=self.box_of_screen(0.13, 0.12, 0.42, 0.22), time_out=6):
            print(text)
            text = self.ocr_and_click(['太鼓'],1,
                                  box=self.box_of_screen(0.28, 0.21, 0.41, 0.61), time_out=6)
            self.click_relative(0.26, 0.32,after_sleep=1)
            # rgb(221,199,136) → BGR(136,199,221) ±20
            if res := self.ocr(match="结界寄养", box=self.box_of_screen(0.44, 0.7, 0.54, 0.78)):
                print(res)
                self.log_info(f"找到{res}")
                self.sleep(1)
                self.click_relative(0.84,0.84,after_sleep=1)
                if self.ocr_and_click("确定",box=self.box_of_screen(0.51, 0.53, 0.67, 0.67),time_out=6):
                    self.log_info(f"确定")
                    self.sleep(0.5)
                else:
                    self.log_info("该卡没有上四星")
                if not self.wait_click_feature('Cancel_Old', threshold=0.7,
                                    box=self.box_of_screen(0.89, 0.11, 0.95, 0.21),
                                    raise_if_not_found=False, time_out=6, after_sleep=1):
                    self.log_warning("找不到Cancel_Old")
            else:
                print(res)
                self.log_warning("找不到结界寄养")
        self.info_set("步骤", "回到结界")
        # 找到合适的星级并寄养 可以选择私有或者公开寄养 激活会变亮

    def KekkaiUtilize(self):
        if text := self.ocr_and_click(['育成'],
                                  box=self.box_of_screen(0.44, 0.36, 0.52, 0.57), time_out=6):
            print(text)
        
        
        if text := self.ocr_and_click(['智能','放入'],2,
                                  box=self.box_of_screen(0.89, 0.69, 0.94, 0.78), time_out=6):
            self.sleep(1)
            self.log_info("式神经验已满 切换式神")
            print(text)
        if self.wait_click_feature('Utilize_Select', threshold=0.7,
                                    box=self.box_of_screen(0.87, 0.04, 0.98, 0.24),
                                    raise_if_not_found=False, time_out=6, after_sleep=1):
            self.log_warning("找到Utilize_Select")
        elif self.wait_ocr(match=re.compile(['式神','寄养']),box=self.box_of_screen(0.05, 0.04, 0.19, 0.11)):
            self.log_warning("找到Utilize_Select")
        else:
            # if results := self.ocr(box=self.box_of_screen(0.88, 0.13, 0.97, 0.22)):
            #     self._extract_kekkai_time(results)
            self.log_warning("找不到Utilize_Select")

        tabs = ['好友', '跨区'] if self.config.get("寄养优先", "好友优先") == "好友优先" else ['跨区', '好友']

        for tab in tabs:
                if not self.ocr_and_click(tab, box=self.box_of_screen(0.17, 0.15, 0.35, 0.22)):
                    self.log_warning(tab)
                    continue

                self.log_info(f"切换到 {tab} 标签")

                # 根据用户配置生成检测列表（同卡种内6星优先）
                priority = self.config.get("卡片优先级", "Douyu优先")
                detect = self.config.get("检测对象", "都检测")

                if detect == "只检测Douyu":
                    feature_list = ['Douyu_6', 'Douyu']
                elif detect == "只检测Shop_Kaiko":
                    feature_list = ['Shop_Kaiko_6', 'Shop_Kaiko']
                elif priority == "Douyu优先":
                    feature_list = ['Douyu_6', 'Douyu', 'Shop_Kaiko_6', 'Shop_Kaiko']
                else:  # Shop_Kaiko优先
                    feature_list = ['Shop_Kaiko_6', 'Shop_Kaiko', 'Douyu_6', 'Douyu']

                found_kaiko = False

                for attempt in range(2):  # 最多下拉2次
                    # 一次性查找所有目标特征，按优先级排序
                    self.sleep(1)
                    if res := self.find_feature(feature_list, threshold=0.8,
                                                box=self.B('DKekkaiUtilize_Box')):
                        # 按 feature_list 的优先级排序（索引越小越优先）
                        priority_map = {f: i for i, f in enumerate(feature_list)}
                        res_sorted = sorted(res, key=lambda b: priority_map.get(b.name, 99))
                        best = res_sorted[0]
                        self.click(best, after_sleep=1)
                        self.info_set("步骤", f"找到 {best.name}")
                        found_kaiko = True
                        break
                    else:
                        self.log_warning(f"未找到目标卡片，第{attempt+1}次尝试，下拉刷新")
                        self._swipe(0.45, 0.82, 0.45, 0.24, 1)

                if found_kaiko:
                    if self.ocr_and_click(['进入', '结界'], box=self.box_of_screen(0.61, 0.74, 0.76, 0.82)):
                        if self.wait_ocr(match=re.compile('式神'), box=self.box_of_screen(0,0,0.2,0.2),
                                         time_out=6):
                            self.log_info("进入寄养页面")
                            self.sleep(2)
                            self.click_relative(0.16, 0.8)
                            if self.ocr_and_click('确定', 1, box=self.box_of_screen(0.51, 0.7, 0.64, 0.81)):
                                self.log_info("成功寄养")
                                self.click_relative(0.04, 0.07, after_sleep=0.5)

                                if not self.wait_click_feature('Back', threshold=0.7,
                                    box=self.B('Home_Button'),
                                    raise_if_not_found=False, time_out=6, after_sleep=1):
                                    self.log_warning("找不到Home_Button")
                                self.info_set("步骤", "返回自己的结界")
                        else:
                            self.log_info("没有进入寄养页面")
                    break  # 找到并处理完就退出 tab 循环
                else:
                    self.log_warning(f"{tab} 标签下未找到可寄养的好友")

    
        
                    

                    
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
