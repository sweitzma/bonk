from enum import IntFlag


class Marks(IntFlag):
    ANY = 1
    READ = 2
    FAVORITE = 4
    ARCHIVE = 8
