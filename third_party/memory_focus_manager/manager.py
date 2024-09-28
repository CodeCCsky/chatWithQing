import copy
import datetime
import yaml

FOCUS_DEFAULT_PATH = r"setting/focus_memory.yaml"

TIME_FORMAT = "%Y-%m-%d"


class MemoryFocusManager:  # TODO test
    def __init__(self, path: str = FOCUS_DEFAULT_PATH, cache_clear_time: int = 14) -> None:
        self.important_memory: list[str] = []
        self.cache_memory: dict[str, list[str]] = {}
        self.cache_memory_clear_time = cache_clear_time
        self.file_path = ""
        self.load_from_file(path)

    def update_cache_clear(self):
        current_time = datetime.datetime.now()
        clear_time = datetime.timedelta(days=self.cache_memory_clear_time)
        cache_memory_copy = copy.deepcopy(self.cache_memory)
        for key, _ in self.cache_memory.items():
            cache_time = datetime.datetime.strptime(key, TIME_FORMAT)
            if current_time - cache_time > clear_time:
                cache_memory_copy.pop(key)
        self.cache_memory = copy.deepcopy(cache_memory_copy)

    def add_new_cache_memory(self, content: str):
        current_time = datetime.datetime.now()
        time_str = current_time.strftime(TIME_FORMAT)
        if self.cache_memory.get(time_str, None) == None:
            self.cache_memory[time_str] = []
        self.cache_memory[time_str].append(content)

    def add_new_important_memory(self, content: str):
        self.important_memory.append(content)

    def set_important_memory(self, memory: list):
        self.important_memory = copy.deepcopy(memory)

    def set_cache_memory(self, memory: dict):
        self.cache_memory = copy.deepcopy(memory)

    def get_important_memory(self) -> list[str]:
        return copy.deepcopy(self.important_memory)

    def get_cache_memory(self) -> dict[str, list[str]]:
        return copy.deepcopy(self.cache_memory)

    def load_from_file(self, path: str):
        self.file_path = path
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data: dict = yaml.load(f.read(), Loader=yaml.FullLoader)
                self.important_memory = data.get("important", [])
                self.cache_memory = data.get("cache", {})
        except (IOError, yaml.YAMLError):
            self.save_file()

    def save_file(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            data = {"important": self.important_memory, "cache": self.cache_memory}
            yaml.dump(data=data, stream=f, allow_unicode=True)
