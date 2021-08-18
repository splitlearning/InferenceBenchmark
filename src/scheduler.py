from interface import (load_config, load_algo, load_data, load_model, load_utils)


class Scheduler():
    def __init__(self, config_path) -> None:
        self.initialize(config_path)

    def initialize(self, config_path) -> None:
        self.config = load_config(config_path)
        self.utils = load_utils(self.config)
        self.utils.copy_source_code(self.config["results_path"])
        self.utils.init_logger()

        self.algo = load_algo(self.config, self.utils)
        self.dataloader = load_data(self.config)
        self.model = load_model(self.config, self.utils)

        self.utils.logger.set_log_freq(len(self.dataloader.train))

    def run_job(self):
        self.utils.logger.log_console("Starting the job")
        for epoch in range(self.config["total_epochs"]):
            self.train()
            self.test()
            self.epoch_summary()
        self.generate_challenge()

    def train(self) -> None:
        self.algo.train()
        self.model.train()
        for batch_idx, sample in enumerate(self.dataloader.train):
            items = self.utils.get_data(sample)
            z = self.algo.forward(items)
            items["server_grads"] = self.model.processing(z, items["pred_lbls"])
            self.algo.backward(items)

    def test(self) -> None:
        self.algo.eval()
        self.model.eval()
        for batch_idx, sample in enumerate(self.dataloader.test):
            items = self.utils.get_data(sample)
            z = self.algo.forward(items)
            self.model.processing(z, items["pred_lbls"])

    def epoch_summary(self):
        self.utils.logger.flush_epoch()
        self.utils.save_models()

    def generate_challenge(self) -> None:
        self.algo.eval()
        self.model.eval()
        for batch_idx, sample in enumerate(self.dataloader.test):
            items = self.utils.get_data(sample)
            z = self.algo.forward(items)
            self.utils.save_data(z, items["prvt_lbls"])