from src.tasks.BaseBattleTask import BaseBattleTask


class SoulZonesTask(BaseBattleTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "御魂副本"

    def run(self):
        self.SwitchSoul_by_num(int(self.config["Preset Group"]),int(self.config["Preset Team"]))
