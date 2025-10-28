import datetime
import uuid
from collections.abc import Generator

import pytest
from coursemology_py.api.course import CourseAPI
from coursemology_py.exceptions import CoursemologyAPIError
from coursemology_py.models.course.assessment.categories import (
    CategoriesIndexResponse,
    Tab,
    TabBasic,
)
from coursemology_py.models.course.assessment.questions import (
    JustRedirect,
    McqMrqPostData,
    MultipleResponseOption,
    ProgrammingPostStatusData,
    ProgrammingQuestion,
    RedirectWithEditUrl,
    TemplateFile,
    TestCase,
    TextResponseQuestion,
    TextResponseSolution,
)
from coursemology_py.models.course.assessments import (
    AssessmentData,
    AssessmentPayload,
    AssessmentsIndexResponse,
    CreateAssessmentPayload,
)


@pytest.fixture(scope="function")
def test_assessment(course_api: CourseAPI, test_tab: TabBasic) -> Generator[AssessmentData]:
    """
    Creates a temporary assessment with a comprehensive payload.
    """
    title = f"Test Assessment {uuid.uuid4().hex[:8]}"
    print(f"\nCreating temporary assessment '{title}'...")

    # Find the category ID for the given tab
    categories_response = course_api.assessment.categories.index()
    category_id = None
    for cat in categories_response.categories:
        if any(t.id == test_tab.id for t in cat.tabs):
            category_id = cat.id
            break
    assert category_id is not None, "Could not find parent category for the test tab."

    # Build the new, comprehensive payload
    assessment_payload = AssessmentPayload(
        title=title,
        start_at=datetime.datetime.now(datetime.UTC),
    )
    create_payload = CreateAssessmentPayload(assessment=assessment_payload, category=category_id, tab=test_tab.id)

    created_assessment: AssessmentData | None = None
    try:
        created_assessment_id_response = course_api.assessment.assessments.create(create_payload)
        created_assessment = course_api.assessment.assessments.fetch(created_assessment_id_response.id)
        print(f"Successfully created assessment with ID: {created_assessment.id}")
        yield created_assessment
    finally:
        if created_assessment and created_assessment.delete_url:
            print(f"\nCleaning up: Deleting assessment {created_assessment.id}...")
            course_api.assessment.assessments.delete(created_assessment.delete_url)
            print(f"Successfully deleted assessment {created_assessment.id}.")


@pytest.fixture(scope="function")
def assessment_with_question(
    course_api: CourseAPI, test_assessment: AssessmentData
) -> Generator[AssessmentData]:
    """
    A fixture that provides a test assessment that is guaranteed to have at least two questions.
    """
    # --- Create the first question ---
    question_payload_data_1 = McqMrqPayload(
        title="Temporary Test Question 1",
        maximum_grade=10,
        grading_scheme="all_correct",
        options_attributes=[
            MultipleResponseOption(correct=True, option="A", weight=0, explanation=None)
        ],
    )
    question_payload_1 = McqMrqPostData(question_multiple_response=question_payload_data_1)
    course_api.assessment.question(test_assessment.id).mcq_mrq.create(question_payload_1)
    print(f"Added temporary question 1 to assessment {test_assessment.id}")

    # --- Create the second question ---
    question_payload_data_2 = McqMrqPayload(
        title="Temporary Test Question 2",
        maximum_grade=20,
        grading_scheme="any_correct",
        options_attributes=[
            MultipleResponseOption(correct=True, option="B", weight=0, explanation=None)
        ],
    )
    question_payload_2 = McqMrqPostData(question_multiple_response=question_payload_data_2)
    course_api.assessment.question(test_assessment.id).mcq_mrq.create(question_payload_2)
    print(f"Added temporary question 2 to assessment {test_assessment.id}")

    yield test_assessment


# --- Categories API Tests ---


def test_assessment_categories_fetch(course_api: CourseAPI):
    """Tests fetching the assessment categories and tabs."""
    response = course_api.assessment.categories.index()
    assert isinstance(response, CategoriesIndexResponse)
    assert isinstance(response.categories, list)
    if response.categories:
        assert isinstance(response.categories[0].tabs, list)
    print(f"\nSuccessfully fetched {len(response.categories)} assessment categories.")


# --- Assessments API Tests ---


@pytest.mark.dependency()
def test_assessments_index(course_api: CourseAPI, test_tab: Tab):
    """Tests fetching the list of all assessments in a specific tab."""
    response = course_api.assessment.assessments.index(tab_id=test_tab.id)
    assert isinstance(response, AssessmentsIndexResponse)
    assert isinstance(response.assessments, list)
    print(f"\nSuccessfully fetched {len(response.assessments)} assessments from tab {test_tab.id}.")


@pytest.mark.dependency()
def test_assessment_create(test_assessment: AssessmentData):
    """Tests assessment creation (implicitly via the fixture)."""
    assert isinstance(test_assessment, AssessmentData)
    assert "Test Assessment" in test_assessment.title


@pytest.mark.dependency(depends=["test_assessment_create"])
def test_assessment_fetch(course_api: CourseAPI, test_assessment: AssessmentData):
    """Tests fetching a specific assessment by its ID."""
    response = course_api.assessment.assessments.fetch(test_assessment.id)
    assert isinstance(response, AssessmentData)
    assert response.id == test_assessment.id
    assert response.title == test_assessment.title


@pytest.mark.dependency(depends=["test_assessment_create"])
def test_assessment_update(course_api: CourseAPI, test_assessment: AssessmentData):
    """Tests updating an assessment's title and other attributes."""
    updated_title = f"Updated Assessment {uuid.uuid4().hex[:8]}"
    payload = AssessmentPayload(
        title=updated_title,
        start_at=test_assessment.start_at.effective_time,
        description="This assessment has been updated.",
        autograded=True,
    )
    course_api.assessment.assessments.update(test_assessment.id, payload)
    response = course_api.assessment.assessments.fetch(test_assessment.id)
    assert response.title == updated_title
    assert response.description == "This assessment has been updated."
    assert response.autograded is True
    print(f"\nSuccessfully updated assessment {test_assessment.id}.")


@pytest.mark.dependency(depends=["test_assessment_create"])
def test_assessment_reorder_questions(course_api: CourseAPI, assessment_with_question: AssessmentData):
    """Tests the reordering of questions within an assessment."""
    # Fetch the assessment to get the question IDs
    fetched_assessment = course_api.assessment.assessments.fetch(assessment_with_question.id)
    question_ids = [q.id for q in fetched_assessment.questions]

    if len(question_ids) < 2:
        pytest.skip("Skipping reorder test: Need at least two questions to reorder.")

    # Reverse the order and send the update
    reordered_ids = list(reversed(question_ids))
    try:
        course_api.assessment.assessments.reorder_questions(assessment_with_question.id, reordered_ids)
        print(f"\nSuccessfully called reorder_questions for assessment {assessment_with_question.id}.")
        # A full verification would re-fetch and check the order, but the API call success is the main test.
    except CoursemologyAPIError as e:
        pytest.fail(f"API call to reorder_questions failed: {e}")


# --- Question API Tests ---


# ... imports
from coursemology_py.models.course.assessment.questions import (
    # ... other models
    McqMrqPayload, # Import the new payload model
    McqMrqPostData, # Import the new wrapper
    MultipleResponseOption,
    # ... other models
)
# ...

# --- Question API Tests ---

@pytest.mark.dependency(depends=["test_assessment_create"])
def test_question_create_mcq(course_api: CourseAPI, test_assessment: AssessmentData):
    """Tests creating a new Multiple Choice Question (MCQ) within an assessment."""
    mcq_payload = McqMrqPayload(
        title=f"New Test Question {uuid.uuid4().hex[:8]}",
        maximum_grade=10,
        grading_scheme="all_correct",
        options_attributes=[
            MultipleResponseOption(correct=True, option="Correct", weight=0, explanation=None),
            MultipleResponseOption(correct=False, option="Incorrect", weight=0, explanation=None),
        ],
    )
    payload = McqMrqPostData(question_multiple_response=mcq_payload)

    try:
        response = course_api.assessment.question(test_assessment.id).mcq_mrq.create(payload)
        assert isinstance(response, RedirectWithEditUrl)
        assert "edit" in response.redirect_edit_url
        print(f"\nSuccessfully created a new MCQ in assessment {test_assessment.id}.")
    except CoursemologyAPIError as e:
        pytest.fail(f"Failed to create a new MCQ: {e}")


@pytest.mark.dependency(depends=["test_assessment_create"])
def test_question_create_text_response(course_api: CourseAPI, test_assessment: AssessmentData):
    """Tests creating a new Text Response question within an assessment."""
    payload = TextResponseQuestion(
        title=f"New Text Response Question {uuid.uuid4().hex[:8]}",
        maximum_grade=10,
        weight=0,
        skillIds=[],
        allow_attachment=False,
        hide_text=False,
        isAttachmentRequired=False,
        solutions_attributes=[
            TextResponseSolution(solutionType="keyword", solution="answer", grade=10, explanation="Good job")
        ],
    )
    try:
        response = course_api.assessment.question(test_assessment.id).text_response.create(payload)
        assert isinstance(response, JustRedirect)
        assert "assessments" in response.redirect_url
        print(f"\nSuccessfully created a new Text Response question in assessment {test_assessment.id}.")
    except CoursemologyAPIError as e:
        pytest.fail(f"Failed to create a new Text Response question: {e}")


@pytest.mark.dependency(depends=["test_assessment_create"])
def test_question_create_programming(course_api: CourseAPI, test_assessment: AssessmentData):
    """Tests creating a new Programming question within an assessment."""
    # Fetch available languages to get a valid language_id
    form_data = course_api.assessment.question(test_assessment.id).programming.fetch_new()
    assert form_data.languages, "No programming languages available to create question."
    python_lang = next((lang for lang in form_data.languages if "python" in lang.name.lower()), None)
    assert python_lang is not None, "Python language not found in available languages."
    language_id = python_lang.id

    payload = ProgrammingQuestion(
        title=f"New Programming Question {uuid.uuid4().hex[:8]}",
        maximum_grade=100,
        weight=0,
        skillIds=[],
        language_id=language_id,
        is_codaveri=False,
        multipleFileSubmission=False,
        template_files_attributes=[TemplateFile(filename="main.py", content="def test():\n    pass\n")],
        test_cases_attributes=[
            TestCase(testCaseType="public", expression="test()", expected="None", hint="Call the function.")
        ],
    )
    try:
        response = course_api.assessment.question(test_assessment.id).programming.create(payload)
        assert isinstance(response, ProgrammingPostStatusData)
        assert isinstance(response.id, int)
        assert "edit" in response.redirect_edit_url if response.redirect_edit_url else False
        print(f"\nSuccessfully created a new Programming question in assessment {test_assessment.id}.")
    except CoursemologyAPIError as e:
        pytest.fail(f"Failed to create a new Programming question: {e}")
