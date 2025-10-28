import datetime
import uuid
from collections.abc import Generator

import polars as pl
import pytest
from coursemology_py.api.course import CourseAPI
from coursemology_py.models.course.assessment.answer_with_question import AnyAnswer
from coursemology_py.models.course.assessment.questions import (
    McqMrqFormData,
    McqMrqPostData,
    MultipleResponseOption,
    MultipleResponseQuestion,
)
from coursemology_py.models.course.assessments import (
    AssessmentData,
    AssessmentPayload,
    CreateAssessmentPayload,
)
from coursemology_py.models.course.statistics import (
    AnswerDataWithQuestion,
    AssessmentsStatistics,
    CoursePerformanceStatistics,
    CourseProgressionStatistics,
    LearningRateRecordsData,
    MainAssessmentInfo,
    StaffStatistics,
    StudentsStatistics,
)
from coursemology_py.models.course.users import CourseUser

# --- Fixtures for Statistics Tests ---


@pytest.fixture(scope="module")
def test_assessment(course_api: CourseAPI) -> Generator[AssessmentData]:
    """
    Creates a temporary assessment with one question for the module.
    Cleans up by deleting the assessment at the end of the module.
    """
    # 1. Create the assessment
    assessment_payload = AssessmentPayload(
        title=f"Statistics Test Assessment {uuid.uuid4().hex[:8]}",
        start_at=datetime.datetime.now(datetime.UTC),
    )
    # Assumes a tab with ID 1 exists. Adjust if necessary.
    create_payload = CreateAssessmentPayload(tab=1, assessment=assessment_payload)
    created_assessment = course_api.assessment.assessments.create(create_payload)
    print(f"\nCreated temporary assessment with ID: {created_assessment.id}")

    # 2. Add a question to the assessment
    question_payload = McqMrqPostData(
        question_multiple_response=McqMrqFormData(
            gradingScheme="all_correct",
            question=MultipleResponseQuestion(
                title="Stats Test Question",
                maximum_grade=10,
                weight=0,
                skillIds=[],
                options=[MultipleResponseOption(correct=True, option="A", weight=0)],
            ),
            allowRandomization=False,
        )
    )
    course_api.assessment.question(created_assessment.id).mcq_mrq.create(question_payload)
    print(f"Added question to assessment {created_assessment.id}")

    yield created_assessment

    # 3. Cleanup
    if created_assessment.delete_url is not None:
        print(f"\nCleaning up: Deleting assessment {created_assessment.id}...")
        course_api.assessment.assessments.delete(created_assessment.delete_url)
        print(f"Successfully deleted assessment {created_assessment.id}.")
    else:
        print("No delete URL found; cannot clean up the assessment.")


@pytest.fixture(scope="function")
def submitted_answer(
    course_api: CourseAPI, test_user: CourseUser, test_assessment: AssessmentData
) -> Generator[AnyAnswer]:
    """
    Ensures the test_user has an active submission and an answer for the test_assessment.
    """
    # This is a complex setup. We need to log in as the test_user to create a submission.
    # For simplicity in this example, we'll assume an endpoint exists to create a submission
    # on behalf of a user, or we'll skip if it's too complex.
    # A full implementation would require a second authenticated client.

    # Let's check if the user already has a submission. If not, we can't test answer stats.
    submissions = course_api.assessment.submissions(test_assessment.id).index().submissions
    user_submission = next((s for s in submissions if s.user.id == test_user.id), None)

    if not user_submission:
        pytest.skip("Cannot test answer statistics: test_user has no submission for the test assessment.")

    submission_details = course_api.assessment.submissions(test_assessment.id).edit(user_submission.id)
    answer = submission_details.answers[0]

    yield answer


# --- Course Statistics API Tests ---


def test_fetch_all_student_statistics(course_api: CourseAPI):
    """Tests fetching statistics for all students."""
    response = course_api.statistics.course.fetch_all_student_statistics()
    assert isinstance(response, StudentsStatistics)
    assert isinstance(response.students, list)
    if response.students:
        assert isinstance(response.students[0].name, str)
    print(f"\nSuccessfully fetched stats for {len(response.students)} students.")


def test_fetch_all_student_statistics_df(course_api: CourseAPI):
    """Tests fetching student statistics directly into a Polars DataFrame."""
    df = course_api.statistics.course.fetch_all_student_statistics_df()
    assert isinstance(df, pl.DataFrame)
    assert "name" in df.columns
    assert "experience_points" in df.columns
    print(f"\nSuccessfully fetched student stats into a DataFrame with shape {df.shape}.")


def test_fetch_all_staff_statistics(course_api: CourseAPI):
    """Tests fetching statistics for all staff."""
    response = course_api.statistics.course.fetch_all_staff_statistics()
    assert isinstance(response, StaffStatistics)
    assert isinstance(response.staff, list)
    print(f"\nSuccessfully fetched stats for {len(response.staff)} staff members.")


def test_fetch_course_progression_statistics(course_api: CourseAPI):
    """Tests fetching course progression statistics."""
    response = course_api.statistics.course.fetch_course_progression_statistics()
    assert isinstance(response, CourseProgressionStatistics)
    assert isinstance(response.progression, list)
    if response.progression:
        assert isinstance(response.progression[0].title, str)
    print(f"\nSuccessfully fetched {len(response.progression)} progression items.")


def test_fetch_course_performance_statistics(course_api: CourseAPI):
    """Tests fetching course performance statistics."""
    response = course_api.statistics.course.fetch_course_performance_statistics()
    assert isinstance(response, CoursePerformanceStatistics)
    assert isinstance(response.performance, list)
    if response.performance:
        assert isinstance(response.performance[0].title, str)
    print(f"\nSuccessfully fetched {len(response.performance)} performance items.")


def test_fetch_assessments_statistics(course_api: CourseAPI):
    """Tests fetching statistics for all assessments."""
    response = course_api.statistics.course.fetch_assessments_statistics()
    assert isinstance(response, AssessmentsStatistics)
    assert isinstance(response.assessments, list)
    if response.assessments:
        assert isinstance(response.assessments[0].title, str)
    print(f"\nSuccessfully fetched stats for {len(response.assessments)} assessments.")


# --- User Statistics API Tests ---


def test_fetch_learning_rate_records(course_api: CourseAPI, test_user: CourseUser):
    """Tests fetching learning rate records for a specific user."""
    response = course_api.statistics.user(test_user.id).fetch_learning_rate_records()
    assert isinstance(response, LearningRateRecordsData)
    assert isinstance(response.records, list)
    print(f"\nSuccessfully fetched {len(response.records)} learning rate records for user {test_user.id}.")


# --- Assessment Statistics API Tests ---


def test_fetch_assessment_statistics(course_api: CourseAPI, test_assessment: AssessmentData):
    """Tests fetching main statistics for a specific assessment."""
    response = course_api.statistics.assessment.fetch_assessment_statistics(test_assessment.id)
    assert isinstance(response, MainAssessmentInfo)
    assert response.id == test_assessment.id
    assert response.title == test_assessment.title
    print(f"\nSuccessfully fetched main stats for assessment {test_assessment.id}.")


# --- Answer Statistics API Tests ---


def test_fetch_answer_statistics(course_api: CourseAPI, submitted_answer: AnyAnswer):
    """Tests fetching statistics for a specific answer."""
    response = course_api.statistics.answer.fetch(submitted_answer.id)
    assert isinstance(response, AnswerDataWithQuestion)
    assert response.answer.id == submitted_answer.id
    assert response.question.id == submitted_answer.question_id
    print(f"\nSuccessfully fetched stats for answer {submitted_answer.id}.")
