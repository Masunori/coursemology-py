from coursemology_py.api.course.announcements import AnnouncementsAPI
from coursemology_py.api.course.assessments import AssessmentAPI
from coursemology_py.api.course.comments import CommentsAPI
from coursemology_py.api.course.disbursement import DisbursementAPI
from coursemology_py.api.course.experience_points import ExperiencePointsRecordAPI
from coursemology_py.api.course.forums import ForumAPI
from coursemology_py.api.course.groups import GroupsAPI
from coursemology_py.api.course.statistics import StatisticsAPI
from coursemology_py.api.course.submissions import TopLevelSubmissionsAPI
from coursemology_py.api.course.user_invitations import UserInvitationsAPI
from coursemology_py.api.course.users import UsersAPI
from coursemology_py.auth import CoursemologySession


class CourseAPI:
    """
    Provides access to all API endpoints for a specific course.
    """

    def __init__(self, session: CoursemologySession, base_url: str, course_id: int):
        self.announcements = AnnouncementsAPI(session, base_url, course_id)
        self.assessment = AssessmentAPI(session, base_url, course_id)
        self.comments = CommentsAPI(session, base_url, course_id)
        self.disbursement = DisbursementAPI(session, base_url, course_id)
        self.experience_points_record = ExperiencePointsRecordAPI(session, base_url, course_id)
        self.forums = ForumAPI(session, base_url, course_id)
        self.groups = GroupsAPI(session, base_url, course_id)
        self.statistics = StatisticsAPI(session, base_url, course_id)
        self.submissions = TopLevelSubmissionsAPI(session, base_url, course_id)
        self.users = UsersAPI(session, base_url, course_id)
        self.user_invitations = UserInvitationsAPI(session, base_url, course_id)
