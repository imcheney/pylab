from enum import Enum


class Skill(Enum):
    STRIKE = 1
    HEAL = 2
    SHIELD = 3


if __name__ == '__main__':
    print Skill.HEAL