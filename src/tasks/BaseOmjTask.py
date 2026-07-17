import math
import re
import time
from datetime import datetime, timedelta
from typing import List

import numpy as np

from ok import BaseTask, Logger, og, CannotFindException

class BaseOmjTask(BaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = {1: 0.09, 2: 0.18, 3: 0.27, 4: 0.35, 5: 0.42, 6: 0.53, 7: 0.62,8: 0.71, 9: 0.80, 10: 0.88}#0.89
# region global
    @property
    def logged_in(self):
        return og.my_app.logged_in

    @logged_in.setter
    def logged_in(self, value):
        og.my_app.logged_in = value

    @property
    def onetime_failed(self):
        return og.my_app.onetime_failed

    @onetime_failed.setter
    def onetime_failed(self, value):
        og.my_app.onetime_failed = value

    @property
    def schedule_failed(self):
        return og.my_app.schedule_failed

    @schedule_failed.setter
    def schedule_failed(self, value):
        og.my_app.schedule_failed = value

    @property
    def failed_task(self):
        return og.my_app.failed_task

    @failed_task.setter
    def failed_task(self, value):
        og.my_app.failed_task = value

    @property
    def pending_tasks(self):
        return og.my_app.pending_tasks

    @pending_tasks.setter
    def pending_tasks(self, value):
        og.my_app.pending_tasks = value
# endregion
    def run_safe(self):
        """包装 run()：管理 fail_count + onetime_failed + failed_task。"""
        if not self.logged_in:
                if not self.executor.device_manager.device_connected():
                    self.log_info("游戏未启动，尝试启动...")
                    if not self.start_game():
                        self.log_warning("请手动启动游戏")
                    return False
                elif self.wait_until(
                        condition=lambda:self.base_scene(),
                                            time_out=120,pre_action=lambda : self.log_page(),raise_if_not_found=False
                    ):
                        self.logged_in = True
                        self.log_info("游戏启动成功")    
                else:
                    self.log_info("游戏启动失败")
                    return False
        try:
            result = self.run()
            if result is False:
                if self.logged_in:
                    og.my_app.fail_count[self.name] = og.my_app.fail_count.get(self.name, 0) + 1
                self.onetime_failed = True
                self.failed_task = self.name
                self.log_error(f"[{self.name}] 返回 False，fail_count={og.my_app.fail_count.get(self.name, 0)}")
                return False
            og.my_app.fail_count[self.name] = 0  # 成功归零
            return True
        except Exception as e:
            og.my_app.fail_count[self.name] = og.my_app.fail_count.get(self.name, 0) + 1
            self.onetime_failed = True
            self.failed_task = self.name
            self.log_error(f"[{self.name}] 异常: {e}，fail_count={og.my_app.fail_count.get(self.name, 0)}")
            return False



# region Logged
    def wait_home(self):
        if not self.logged_in:
            if self.base_scene():
                self.logged_in = True
                return True
        return False
    def log_page(self):
        if self.base_scene():
            self.logged_in = True
            return True
        if self.ocr_and_click(['进入','游戏'],3,box=self.box_of_screen(0.41, 0.78, 0.58, 0.88)):
            self.log_info("进入游戏")
            if self.base_scene():
                self.logged_in = True
                return True
        if text := self.ocr(match='公告',box=self.box_of_screen(0,0,0.24,0.81)):
            self.log_info("有公告123")
            if btns := self.find_feature('Daily_New_Cancel', box=self.B('Cancel_Box'), threshold=0.7):
                self.click(btns[0], after_sleep=0.2)
                self.log_info('关闭弹窗1')
        if self.ocr(match=re.compile('下载'),
                     box=self.box_of_screen(0.37, 0.87, 0.63, 0.96)):
            self.log_info("检测到正在下载")
            self.sleep(5)
        if self.ocr(match='切换',box=self.box_of_screen(0.38, 0.69, 0.62, 0.77)):
            self.click_relative(0.5,0.83)
            self.sleep(3)
            if self.base_scene():
                self.logged_in = True
        if self.ocr(match=re.compile('公告|扫码|下载|修复|账号'),
                    box=self.box_of_screen(0.92, 0.08, 0.99, 0.91),):
            self.click_relative(0.5, 0.83)
            self.sleep(3)
            if self.base_scene():
                self.logged_in = True
        if btns := self.find_feature('Daily_New_Cancel',
                                     box=self.B('Cancel_Box'), threshold=0.8):
            self.click(btns[0], after_sleep=0.2)
            self.log_info('关闭弹窗2')
        if btns := self.find_feature('Cancel_Old',
                                     box=self.B('Cancel_Box'), threshold=0.8):
            self.click(btns[0], after_sleep=0.2)
            self.log_info('关闭弹窗3')
        if btns := self.find_feature('Back', box=self.B('Back'), threshold=0.8):
            self.click(btns[0], after_sleep=0.5)
            self.log_info('点击 Back')
        if btns := self.find_feature('Home_Button', box=self.B('Home_Button'), threshold=0.8):
            self.click(btns[0], after_sleep=0.3)
            self.log_info('点击 Home_Button')
        if text := self.ocr(
            match=re.compile('正在连接|断开|重新连接|其他设备'),
            box=self.box_of_screen(0.34, 0.36, 0.66, 0.65),
        ):
            msg = ' '.join(t.name for t in text)
            self.log_info(f"检测到意外弹窗: {msg}")

            if re.search('正在连接', msg):
                self.log_info("网络问题，等待10秒后重试...")
                self.sleep(10)
                return self.unexpected_error()

            if re.search('断开|重新连接', msg):
                self.log_info("游戏已断开连接，重启游戏")
                return self.restart_game()

            if re.search('其他设备', msg):
                self.log_info("检测到其他设备登录，重启游戏")
                return self.restart_game()
    def start_game(self):
        pkg = self.executor.config.get('adb', {}).get('packages', [''])[0]
        self.log_info("→ 启动游戏...")
        try:
            self.adb_shell(
                f'monkey -p {pkg} -c android.intent.category.LAUNCHER 1',
                timeout=10,
            )
        except Exception as e:
            self.log_error(f"启动游戏失败: {e}")
            return False
        self.log_info("→ 等待游戏加载...")
        if self.wait_until(
            condition=lambda:self.base_scene(),
                                time_out=120,pre_action=lambda : self.log_page(),raise_if_not_found=False
        ):
            self.logged_in = True
            self.log_info("游戏启动成功")
            return True
        self.log_info("游戏启动失败")
        return False
    def _clear_flags(self):
        self.onetime_failed = False
        self.schedule_failed = False
        self.failed_task = ""
        
    
    def restart_game(self, wait_load=True):
        """通过 ADB 强制停止并重新启动游戏。返回 True 表示重启成功。"""
        pkg = self.executor.config.get('adb', {}).get('packages', [''])[0]
        print("1111111111111111111111111111111111")
        print(pkg)
        self.log_info({pkg})
        print("1111111111111111111111111111111111")
        if not pkg:
            self.log_error("未配置 ADB packages，无法重启游戏")
            return False

        self.log_info(f"正在重启游戏 ({pkg})...")

        # 强制停止
        self.log_info("→ 停止游戏...")
        try:
            self.adb_shell(f'am force-stop {pkg}', timeout=10)
        except Exception as e:
            self.log_warning(f"force-stop 异常（可能已停止）: {e}")

        self.sleep(2)
        self.logged_in = False
        # 重新启动
        self.log_info("→ 启动游戏...")
        try:
            self.adb_shell(
                f'monkey -p {pkg} -c android.intent.category.LAUNCHER 1',
                timeout=10,
            )
        except Exception as e:
            self.log_error(f"启动游戏失败: {e}")
            return False

        if wait_load:
            self.log_info("→ 等待游戏加载 (15s)...")
            self.sleep(15)

        self.log_info("游戏重启完成")
        return True

    def unexpected_error(self):
        """检测意外弹窗并处理。返回 True 表示已处理，False 表示无需处理。"""
        if text := self.ocr(
            match=re.compile('正在连接|断开|重新连接|其他设备'),
            box=self.box_of_screen(0.34, 0.36, 0.66, 0.65),
        ):
            msg = ' '.join(t.name for t in text)
            self.log_info(f"检测到意外弹窗: {msg}")

            if re.search('正在连接', msg):
                self.log_info("网络问题，等待10秒后重试...")
                self.sleep(10)
                return self.unexpected_error()

            if re.search('断开|重新连接', msg):
                self.log_info("游戏已断开连接，重启游戏")
                return self.restart_game()

            if re.search('其他设备', msg):
                self.log_info("检测到其他设备登录，重启游戏")
                return self.restart_game()

        return False

# endregion
#region Home
    def base_scene(self):
        if home := self.find_one(["Home_Store","Home_Shikigami_Chronicles"], threshold=0.8, box=self.B('bottom')):
            self.log_info("home")
            return True
        if town := self.find_feature('Home_Town', threshold=0.8, box=self.B('Home_Town')):
            self.log_info("town")
            return True

        if exploration := self.find_one(["Exploration_Delegation","Exploration_Hero","Exploration_Awake"],
                                        box=self.B('bottom')):
            self.log_info("exploration")
            return True
        else:
            return False
    def in_home_and_back(self):

        if self.In_Home():
            self.log_info("在主页")
        else:
            self.log_info("不在主页")
            self.Back_Home()
        return True
    def In_Home(self):
        self.log_info("寻找町中")
        home = self.find_one(["Home_Store","Home_Shikigami_Chronicles","YinYang_Lodge"], threshold=0.75, box=self.B('bottom'))
        if not (town := self.find_feature('Home_Town', threshold=0.8, box=self.B('Home_Town'))):
            town = self.find_feature('Home_Explore', threshold=0.8, box=self.B('Home_Explore'))
        town1 = self.find_one(["Home_Town", "Home_Explore"], threshold=0.8, box=self.B('Home_Exp'))
        town_ocr = self.ocr(match=re.compile('町中|探索'))

        if town and home:
            self.log_info("主页")
            return True
        elif town and (not home):
            self.log_info("卷轴没有打开")
            self.sleep(0.5)
            self.click_relative(0.94, 0.89,after_sleep=1)
            if  self.find_one(["Home_Store","Home_Shikigami_Chronicles","YinYang_Lodge"], threshold=0.75, box=self.B('bottom')):
                return True
        elif town1 and home:
            if self.reset():
                return True
        elif town1 and (not home):
            self.log_info("卷轴没有打开,而且角色位置不是很对")
            self.sleep(0.5)
            self.click_relative(0.94, 0.89,after_sleep=1)
            if home := self.find_one(["Home_Store","Home_Shikigami_Chronicles","YinYang_Lodge"], threshold=0.75, box=self.B('bottom')):
                if self.reset():
                    return True
        elif home:
            if self.reset():
                return True
        return False
       
    def Back_Home(self):
        """快速路径：Home_Button → Back → Home_Button。"""
        self.log_info('进入backhome')
        if btns := self.find_feature('Home_Button', box=self.B('Home_Button'), threshold=0.8):
            self.click(btns[0], after_sleep=2)
            self.log_info('点击 Home_Button')
            if self.In_Home():
                return True
        self.sleep(0.3)
        if btns := self.find_feature('Back', box=self.B('Back'), threshold=0.8):
            self.click(btns[0], after_sleep=0.5)
            self.log_info('点击 Back')
            if self.In_Home():
                return True
        self.sleep(0.3)
        if btns := self.find_feature('Home_Button', box=self.B('Home_Button'), threshold=0.8):
            self.click(btns[0], after_sleep=2)
            self.log_info('点击 Home_Button')
            if self.In_Home():
                return True
        return self.Back_Home_loop()

    def Back_Home_loop(self):
        """顽固路径：循环消弹窗直到回到主页。"""
        self.log_info('进入backhome循环')

        cancel_box = self.box_of_screen(0.5, 0, 1, 0.5)

        def try_back():
            if btns := self.find_feature('Daily_New_Cancel',
                                          box=cancel_box, threshold=0.8):
                self.click(btns[0], after_sleep=0.2)
                self.log_info('关闭弹窗')
                return
            if btns := self.find_feature( 'Cancel_Old',
                                          box=cancel_box, threshold=0.8):
                self.click(btns[0], after_sleep=0.2)
                self.log_info('关闭弹窗')
                return
            if btns := self.find_feature('Back', box=self.B('Back'), threshold=0.8):
                self.click(btns[0], after_sleep=0.5)
                self.log_info('点击 Back')
                return
            if btns := self.find_feature('Home_Button', box=self.B('Home_Button'), threshold=0.8):
                self.click(btns[0], after_sleep=0.3)
                self.log_info('点击 Home_Button')

        return self.wait_until(
            self.In_Home,
            time_out=5,
            post_action=try_back,
            raise_if_not_found=False,
        )

    def reset(self):
        """从阴阳寮返回主页。"""
        self.log_info("寻从阴阳寮返回主页")
        if not self.wait_click_feature('YinYang_Lodge', threshold=0.7,
                                        box=self.B('YinYang_Lodge'),
                                        raise_if_not_found=False, time_out=3, after_sleep=1):
            self.log_warning("找不到YinYang_Lodge")
            return False
        self.info_set("步骤", "进入YinYang_Lodge")
        self.wait_click_feature('Home_Button', threshold=0.8, box=self.B('Home_Button'),
                                after_sleep=2,time_out=5,raise_if_not_found=False)
        return True

    def in_store(self):
        self.log_info('进入判断')
        if self.find_one(
            ['Gift_Store','Grocery_Store'],
            threshold=0.8,box=self.box_of_screen(0, 0.8, 1, 1)
        ):
            self.log_info('in store')
            self.sleep(1)
            return True
        return False
#endregion     
    
    
    def ocr_and_click(self, match, sleep: float = 0.5,time_out :float =3, box=None, random_click: bool = False,raise_if_not_found=False) -> bool:
        """OCR 指定区域按优先级模糊匹配文字并点击。返回 True/False。
        match: str 或 list[str]，内部自动转正则（包含即匹配）。
        random_click=True 时在识别区域内随机选点点击。
        """
        import re, random
        if isinstance(match, str):
            match = [match]
        for m in match:
            results = self.wait_ocr(match=re.compile(m), box=box, threshold=0.7,time_out=time_out,raise_if_not_found=raise_if_not_found)
            if results:
                r = results[0]
                if random_click:
                    h = self.frame.shape[0] if hasattr(self, 'frame') else 1440
                    w = self.frame.shape[1] if hasattr(self, 'frame') else 2560
                    rx = random.randint(r.x, r.x + r.width)
                    ry = random.randint(r.y, r.y + r.height)
                    self.click_relative(rx / w, ry / h, after_sleep=sleep)
                else:
                    self.click_box(r, after_sleep=sleep)
                self.log_info(f"OCR '{m}' -> '{r.name}' 并点击")
                return True
        return False


    def B(self, name: str):
        """快捷获取特征搜索 Box：self.B('Home_Sign') → Box 对象。"""
        from src.feature_boxes import BOX
        coords = BOX.get(name, BOX["full"])
        return self.box_of_screen(*coords)

    def click_nth(self, axis: str, fixed: float, pos_map: dict, n: int, label: str = ""):
        """点击列表中第 n 项。
        axis='x': X 固定，Y 从 pos_map 查（纵向列表）
        axis='y': Y 固定，X 从 pos_map 查（横向列表）
        """
        coord = pos_map.get(n)
        if coord is None:
            self.log_warning(f"第 {n} 个{label} 不在坐标表中")
            return
        x, y = (fixed, coord) if axis == 'x' else (coord, fixed)
        self.click_relative(x, y, after_sleep=1)
        print(x,y)
        self.log_info(f"选择第 {n} 个{label}")
    def _swipe(self,x:float,y:float,to_x:float,to_y:float,duration:float):
        h, w = self.frame.shape[:2]
        self.swipe(
            int(x * w), int(y * h),  # 起点像素
            int(to_x * w), int(to_y * h),  # 终点像素
            duration=duration,
        )

        self.log_info('滑动完成')

    # ---------- 游戏重启 ----------

