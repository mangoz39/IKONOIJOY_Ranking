class SongRanker:
    def __init__(self, songs):
        self.songs = songs
        self.temp_list = [[song] for song in songs]  # merge sort initialize
        self.merged_list = []
        self.tmp_left = self.temp_list.pop(0)
        self.tmp_right = self.temp_list.pop(0)
        self.current_pairs = []
        self.choice = None

        if self.songs:
            self.prepare_next_comparison()

    def prepare_next_comparison(self):
        print('start make new pairs')
        self.current_pairs = []
        if len(self.temp_list) == 3:
            tmp = self.temp_list.pop(0)
            left = self.temp_list.pop(0)
            right = self.temp_list.pop(0)
            self.temp_list = []
            self.temp_list.append(tmp)
            self.current_pairs.append([left, right])
            return

        while self.temp_list:
            if len(self.temp_list) == 1:  # 讓佇列始終保持雙數
                self.current_pairs.append([self.temp_list.pop(0), []])
                continue

            left = self.temp_list.pop(0)
            right = self.temp_list.pop(0)

            self.current_pairs.append([left, right])
        return

    def get_current_pair(self):
        # pass parameters to views.py
        if self.tmp_left and self.tmp_right:
            return self.tmp_left[0], self.tmp_right[0]
        else:
            return None, None

    def make_new_pair(self):
        new_pair = self.current_pairs.pop(0)
        if len(new_pair) == 1:
            self.tmp_left, self.tmp_right = new_pair, []
            return
        else:
            self.tmp_left, self.tmp_right = new_pair[0], new_pair[1]
            return

    def choose(self, choice):

        print("Before merge:")
        print(f"current_pairs: {self.current_pairs}")
        print(f"tmp_left: {self.tmp_left}")
        print(f"tmp_right: {self.tmp_right}")

        self.merge(choice)

        if not self.tmp_left and not self.tmp_right:
            self.temp_list.append(self.merged_list)
            print(f'push {self.merged_list} to tmp')
            if not self.current_pairs:
                if len(self.merged_list) == len(self.songs):
                    return True
                else:
                    print('empty c pair')
                    self.prepare_next_comparison()
            self.merged_list = []
            self.make_new_pair()

        print("\nAfter merge:")
        print(f"current_pairs: {self.current_pairs}")
        print(f"tmp_left: {self.tmp_left}")
        print(f"tmp_right: {self.tmp_right}")

        if not self.tmp_left or not self.tmp_right:
            if not self.tmp_left:
                self.merged_list.extend(self.tmp_right)
                self.tmp_right = []
            else:
                self.merged_list.extend(self.tmp_left)
                self.tmp_left = []
            self.temp_list.append(self.merged_list)
            self.prepare_next_comparison()
            self.merged_list = []
            self.make_new_pair()

        return False

    def merge(self, preferred):
        # preferred isn't received, stop merging
        if preferred is None:
            return

        # merging and check if any list is empty
        if preferred:
            self.merged_list.append(self.tmp_left.pop(0))  # 如果選擇了左邊，就把它移到合併結果
            if not self.tmp_left:
                self.merged_list.extend(self.tmp_right)
                self.tmp_right = []
        else:
            self.merged_list.append(self.tmp_right.pop(0))  # 否則選擇右邊的
            if not self.tmp_right:
                self.merged_list.extend(self.tmp_left)
                self.tmp_left = []

        print(f'{preferred} win, merged = {self.merged_list}')
        return

    def to_dict(self):
        """轉換為字典，方便存入 session"""
        return {
            "temp_list": self.temp_list,
            "merged_list": self.merged_list,
            "current_pairs": self.current_pairs,
            "tmp_left": self.tmp_left,
            "tmp_right": self.tmp_right,
        }

    @classmethod
    def from_dict(cls, data, songs):
        """從 session 取出的資料還原為 SongRanker 物件"""
        ranker = cls.__new__(cls)
        ranker.songs = songs
        ranker.temp_list = data.get("temp_list", [[song] for song in songs])
        ranker.merged_list = data.get("merged_list", [])
        ranker.current_pairs = data.get("current_pairs", [])
        ranker.tmp_left = data.get("tmp_left", [])
        ranker.tmp_right = data.get("tmp_right", [])
        return ranker
