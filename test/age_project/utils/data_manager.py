from typing import List, Tuple
import heapq
from dataclasses import dataclass
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

import os
import sys

# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the deploy directory to sys.path
sys.path.extend([current_dir, os.path.dirname(current_dir)])


@dataclass
class CommunityMember:
    name: str
    age: int
    group: str


class CommunityData:
    def __init__(self, members: List[CommunityMember], group_colors: dict):
        self.original_members = members.copy()
        self.members = members
        self.age_threshold = 60
        self.group_colors = group_colors
        self.senior_color = QColor(212, 175, 55)
        self.group_order = {group: idx for idx, group in enumerate(group_colors.keys())}

    def reset_to_original(self):
        self.members = self.original_members.copy()

    def add_member(self, name: str, age: int, group: str):
        """添加新成员"""
        new_member = CommunityMember(name, age, group)
        self.members.append(new_member)
        self.original_members.append(new_member)

    def sort_members(self, method: str):
        if method == "随机":
            import random

            random.shuffle(self.members)
        elif method == "快速排序(年龄升序)":
            self.members.sort(key=lambda x: x.age)
        elif method == "归并排序(年龄降序)":
            self.members.sort(key=lambda x: x.age, reverse=True)
        elif method == "堆排序(年龄升序)":
            heap = []
            for member in self.members:
                heapq.heappush(heap, (member.age, member))
            self.members = [heapq.heappop(heap)[1] for _ in range(len(heap))]
        elif method == "组别排序":
            self.members.sort(key=lambda x: (self.group_order[x.group], x.age))

    @property
    def names(self) -> List[str]:
        return [m.name for m in self.members]

    @property
    def ages(self) -> List[int]:
        return [m.age for m in self.members]

    @property
    def max_age(self) -> int:
        return max(self.ages, default=0)

    @property
    def member_count(self) -> int:
        return len(self.members)

    def get_color(self, member: CommunityMember) -> QColor:
        return self.group_colors.get(member.group, Qt.GlobalColor.gray)

    def get_name_color(self, member: CommunityMember) -> QColor:
        return (
            self.senior_color
            if member.age >= self.age_threshold
            else Qt.GlobalColor.black
        )
