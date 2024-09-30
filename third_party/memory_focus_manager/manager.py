import copy
import datetime
import yaml

FOCUS_DEFAULT_PATH = r"setting/focus_memory.yaml"

TIME_FORMAT = "%Y-%m-%d"


class MemoryFocusManager:
    def __init__(
        self, path: str = FOCUS_DEFAULT_PATH, cache_clear_time: int = 7
    ) -> None:
        self.important_memory: list[str] = []
        self.cache_memory: dict[str, list[tuple[str, int]]] = {}
        self.cache_memory_clear_time = cache_clear_time
        self.file_path = ""
        self.load_from_file(path)

    def update_cache_clear(self):
        current_time = datetime.datetime.now()
        cache_memory_copy = copy.deepcopy(self.cache_memory)
        for key, cache_list in self.cache_memory.items():
            list_copy = copy.deepcopy(cache_list)
            for index, (content, del_time) in enumerate(cache_list):
                clear_time = datetime.timedelta(days=del_time)
                cache_time = datetime.datetime.strptime(key, TIME_FORMAT)
                if current_time - cache_time > clear_time:
                    list_copy.pop(index)
            cache_memory_copy[key] = list_copy
            if list_copy == []:
                cache_memory_copy.pop(key)
        self.cache_memory = cache_memory_copy

    def add_new_cache_memory(self, content: str, cache_day: int):
        current_time = datetime.datetime.now()
        time_str = current_time.strftime(TIME_FORMAT)
        if self.cache_memory.get(time_str, None) == None:
            self.cache_memory[time_str] = []
        self.cache_memory[time_str].append((content, cache_day))

    def add_new_important_memory(self, content: str):
        self.important_memory.append(content)

    def set_important_memory(self, memory: list):
        self.important_memory = copy.deepcopy(memory)

    def set_cache_memory(self, memory: dict):
        self.cache_memory = copy.deepcopy(memory)

    def get_important_memory(self) -> list[str]:
        return copy.deepcopy(self.important_memory)

    def get_cache_memory(self) -> dict[str, list[tuple[str, int]]]:
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
