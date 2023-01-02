class UserExistsException(Exception):
    def __int__(self, message="UserExistsException: Discord ID already exists"):
        self.message = message
        super().__init__(self.message)

class CourseExistsException(Exception):
    def __init__(self, message="CourseExistsException: Course ID already exists in user's schedule"):
        self.message = message
        super().__init__(self.message)

class NoCoursesException(Exception):
    def __init__(self, message="NoCoursesException: User has no courses in their schedule"):
        self.message = message
        super().__init__(self.message)

class MaxCoursesReachedException(Exception):
    def __init__(self, message="MaxCoursesReachedException: User has reached the maximum amount of courses allowed. Contact an administrator to change the maximum amount of courses"):
        self.message = message
        super().__init__(self.message)

class InvalidMaxCoursesException(Exception):
    def __init__(self, message="InvalidMaxCoursesException: Value inputted not in valid range"):
        self.message = message
        super().__init__(self.message)

class LackingPermissionsException(Exception):
    def __init__(self, message="LackingPermissionsException: User does not have administrative privileges to use this command"):
        self.message = message
        super().__init__(self.message)