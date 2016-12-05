import json


class Settings:
    __all_configs = None

    def __init__(self):
        self.config = Settings.__all_configs
        self.load()

    def load(self):
        if Settings.__all_configs is not None:
            return
        with open("config.json") as conf_file:
            self.config = json.loads(conf_file.read())
            Settings.__all_configs = self.config

    def repositories_folder(self):
        return self.config["repositories_folder"]

    def output_folder(self):
        return self.config["output_folder"]

    def equinox(self):
        return self.config["equinox"]

    def ref_miner(self):
        return self.config["ref_miner"]

    def results_repo_name(self):
        return self.config["results_git_repo_prefix"]

