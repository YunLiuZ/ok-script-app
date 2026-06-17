import re

from ok import BaseTask

class MyBaseTask(BaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "基本设置"
        self.description = "切换御魂 判断是否在主页"
    def in_home(self):
        return self.find_one(['Home_Town', 'Home_Store', 'Home_Sign'],
                            threshold=0.6) is not None




