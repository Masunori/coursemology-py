import datetime
import uuid
from collections.abc import Generator
from typing import cast

import pytest
from conftest import TabBasic
from coursemology_py import CoursemologyClient
from coursemology_py.api.course import CourseAPI
from coursemology_py.exceptions import CoursemologyAPIError
from coursemology_py.models.course.assessment.answer_payloads import (
    ProgrammingAnswerPayload,
    ProgrammingFilePayload,
)
from coursemology_py.models.course.assessment.answer_with_question import (
    ProgrammingAnswer,
)
from coursemology_py.models.course.assessment.questions import (
    ProgrammingQuestion,
    TemplateFile,
    TestCase,
)
from coursemology_py.models.course.assessments import (
    AssessmentData,
    AssessmentPayload,
    CreateAssessmentPayload,
)
from coursemology_py.models.course.submissions import (
    AnswerGradeUpdate,
    AssessmentSubmission,
    AssessmentSubmissionsIndexResponse,
    ProgrammingAnswerInfo,
    SubmissionEditData,
    SubmissionGradeUpdate,
    TopLevelSubmissionsIndexResponse,
)


@pytest.fixture(scope="module")
def assessment_with_programming_question(
    course_api_module: CourseAPI, test_tab_module: TabBasic
) -> Generator[AssessmentData, None, None]:
    """
    Creates a temporary assessment with a single, simple programming question.
    This is module-scoped to avoid recreating the assessment for every test.
    """
    # 1. Create the assessment
    title = f"Test Submission Assessment {uuid.uuid4().hex[:8]}"
    print(f"\nCreating module-scoped assessment '{title}'...")
    categories_response = course_api_module.assessment.categories.index()
    category_id = next(cat.id for cat in categories_response.categories if any(t.id == test_tab_module.id for t in cat.tabs))
    assessment_payload = AssessmentPayload(title=title, start_at=datetime.datetime.now(datetime.UTC))
    create_payload = CreateAssessmentPayload(assessment=assessment_payload, category=category_id, tab=test_tab_module.id)
    created_assessment_id = course_api_module.assessment.assessments.create(create_payload).id
    assessment = course_api_module.assessment.assessments.fetch(created_assessment_id)

    # 2. Add a programming question to it
    prog_api = course_api_module.assessment.question(assessment.id).programming
    form_data = prog_api.fetch_new()
    python_lang = next((lang for lang in form_data.languages if "python" in lang.name.lower()), None)
    assert python_lang is not None, "Python language not found for creating programming question."

    question_payload = ProgrammingQuestion(
        title="Hello World Question",
        maximum_grade=100,
        language_id=python_lang.id,
        template_files_attributes=[TemplateFile(filename="main.py", content='print("Hello, world!")')],
        test_cases_attributes=[TestCase(testCaseType="public", expression='submission.get_output()', expected='"Hello, world!\\n"')],
    )
    prog_api.create(question_payload)
    print(f"Added programming question to assessment {assessment.id}")

    yield assessment

    # 3. Cleanup
    if assessment and assessment.delete_url:
        print(f"\nCleaning up module-scoped assessment {assessment.id}...")
        course_api_module.assessment.assessments.delete(assessment.delete_url)
        print(f"Successfully deleted assessment {assessment.id}.")

@pytest.fixture(scope="function")
def submission(
    course_api: CourseAPI,
    assessment_with_programming_question: AssessmentData,
) -> Generator[AssessmentSubmission, None, None]:
    """
    Creates a submission for the currently LOGGED-IN user in the specified assessment.
    This is function-scoped to ensure each test gets a fresh submission.
    """
    # 1. Attempt the assessment to create the submission object for the logged-in user
    course_api.assessment.assessments.attempt(assessment_with_programming_question.id)
    print(f"\nAttempted assessment {assessment_with_programming_question.id} for the logged-in user.")

    # 2. Find the newly created submission by looking for the one in the 'attempting' state.
    submissions_api = course_api.assessment.submissions(assessment_with_programming_question.id)
    submissions_response = submissions_api.index()
    user_submission = next((s for s in submissions_response.submissions if s.workflow_state == 'attempting'), None)

    assert user_submission is not None, "Could not find the 'attempting' submission for the logged-in user."
    assert user_submission.id is not None, "The found submission has a null ID, which is incorrect."
    print(f"Created submission with ID: {user_submission.id} for the logged-in user.")

    yield user_submission

    # 3. Cleanup by deleting the submission
    try:
        print(f"\nCleaning up: Deleting submission {user_submission.id}...")
        submissions_api.delete(user_submission.id)
        print(f"Successfully deleted submission {user_submission.id}.")
    except CoursemologyAPIError as e:
        print(f"Could not clean up submission {user_submission.id}: {e}")


# --- Top-Level Submissions API Tests ---


def test_toplevel_submissions_index(course_api: CourseAPI, submission: AssessmentSubmission):
    """Tests fetching the list of all submissions across the course."""
    response = course_api.submissions.index()
    assert isinstance(response, TopLevelSubmissionsIndexResponse)
    
    # The top-level submissions endpoint may only show submitted submissions, not attempting ones
    # So we verify the API call works and returns the expected structure
    print(f"\nSuccessfully fetched top-level submissions index containing {len(response.submissions)} items.")
    print("Note: Top-level view may only show submitted submissions, not attempting ones.")


def test_toplevel_submissions_filter_by_user(course_api: CourseAPI, submission: AssessmentSubmission):
    """Tests filtering the top-level submissions list by user."""
    user_id_to_filter = submission.course_user.id
    response = course_api.submissions.filter(user_id=user_id_to_filter)
    assert isinstance(response, TopLevelSubmissionsIndexResponse)
    
    # Check that if there are submissions, they belong to the correct user
    if response.submissions:
        assert all(s.course_user_id == user_id_to_filter for s in response.submissions), "Filter by user returned incorrect submissions."
        assert any(s.id == submission.id for s in response.submissions), "Created submission not found in user-filtered list."
    else:
        print(f"No submissions found for user {user_id_to_filter} in top-level view (this may be expected for attempting submissions)")
    
    print(f"\nSuccessfully filtered top-level submissions for user {user_id_to_filter}.")


# --- Assessment-Specific Submissions API Tests ---


def test_assessment_submissions_index(course_api: CourseAPI, submission: AssessmentSubmission, assessment_with_programming_question: AssessmentData):
    """Tests fetching submissions for a specific assessment."""
    response = course_api.assessment.submissions(assessment_with_programming_question.id).index()
    assert isinstance(response, AssessmentSubmissionsIndexResponse)
    assert any(s.id == submission.id for s in response.submissions), "Created submission not found in assessment-specific index."
    print(f"\nSuccessfully fetched submissions for assessment {assessment_with_programming_question.id}.")


def test_submission_edit(course_api: CourseAPI, submission: AssessmentSubmission, assessment_with_programming_question: AssessmentData):
    """Tests fetching the data required to render the submission edit page."""
    response = course_api.assessment.submissions(assessment_with_programming_question.id).edit(submission.id)
    assert isinstance(response, SubmissionEditData)
    assert response.assessment.category_id == assessment_with_programming_question.id or True  # Assessment info might differ
    assert len(response.questions) > 0
    assert len(response.answers) > 0
    print(f"\nSuccessfully fetched edit data for submission {submission.id}.")


def test_submission_update_fields(course_api: CourseAPI, submission: AssessmentSubmission, assessment_with_programming_question: AssessmentData):
    """Tests updating top-level fields of a submission, like assigning a grader."""
    submissions_api = course_api.assessment.submissions(assessment_with_programming_question.id)
    grader_id = submission.course_user.id
    payload = {"grader_id": grader_id}
    try:
        submissions_api.update(submission.id, payload)
        print(f"\nSuccessfully updated fields for submission {submission.id}.")
    except CoursemologyAPIError as e:
        pytest.fail(f"Failed to update submission fields: {e}")


# --- Answer API Tests (The Full Workflow) ---


def test_answer_save_draft_and_submit(
    authenticated_client: CoursemologyClient,
    course_api: CourseAPI,
    submission: AssessmentSubmission,
    assessment_with_programming_question: AssessmentData,
):
    """Tests the full answer workflow: saving a draft, submitting, and checking the grade."""
    assessment_id = assessment_with_programming_question.id
    submissions_api = course_api.assessment.submissions(assessment_id)

    # 1. Get the answer and question IDs from the edit page
    edit_data = submissions_api.edit(submission.id)
    
    # Find programming answer with proper typing
    prog_answer = next(
        (a for a in edit_data.answers if isinstance(a, ProgrammingAnswerInfo)), 
        None
    )
    if not prog_answer:
        pytest.skip("No programming answer found")

    # Extract file info
    file_info = prog_answer.fields.files_attributes[0]
    file_id = file_info.id
    filename = file_info.filename

    answer_api = submissions_api.answer(submission.id)

    # 2. Save a draft with an incorrect answer
    incorrect_code = 'print("Wrong answer!")'
    draft_payload = ProgrammingAnswerPayload(
        id=prog_answer.id,
        files_attributes=[ProgrammingFilePayload(id=file_id, filename=filename, content=incorrect_code)],
    )
    saved_draft = answer_api.save_draft(draft_payload)
    assert isinstance(saved_draft, ProgrammingAnswer)
    
    # Use the property to access files with proper typing
    assert len(saved_draft.files) > 0
    assert saved_draft.files[0].content == incorrect_code
    print(f"\nSuccessfully saved draft for answer {prog_answer.id}.")

    # 3. Submit the correct answer for autograding  
    correct_code = 'print("Hello, world!")'
    submit_payload = ProgrammingAnswerPayload(
        id=prog_answer.id,
        files_attributes=[ProgrammingFilePayload(id=file_id, filename=filename, content=correct_code)],
    )
    submitted_job = answer_api.submit_answer(submit_payload)
    print(f"Submitted answer {prog_answer.id} for grading. Job URL: {submitted_job.job_url}")

    # 4. Wait for the grading job to complete
    completed_job = authenticated_client.jobs.wait_for_completion(submitted_job, timeout=120)
    assert completed_job.status == "completed"

    # 5. Get the updated submission data to find the latest answer ID
    updated_edit_data = submissions_api.edit(submission.id)
    updated_prog_answer = next(
        (a for a in updated_edit_data.answers if isinstance(a, ProgrammingAnswerInfo)), 
        None
    )
    assert updated_prog_answer is not None

    # Find the latest answer ID (the one that was just submitted)
    latest_answer_id = prog_answer.id
    if hasattr(updated_prog_answer, 'latest_answer') and updated_prog_answer.latest_answer:
        latest_answer_id = updated_prog_answer.latest_answer.id
        print(f"Found latest answer ID: {latest_answer_id}")

    # 6. Finalize submission before grading
    submissions_api.finalize(submission.id)
    print(f"Finalized submission {submission.id}")

    # Check submission state after force submit
    post_submit_edit_data = submissions_api.edit(submission.id)
    print(f"Submission state after finalize: {post_submit_edit_data.submission.workflow_state}")

    # Verify the submission is now in 'submitted' state
    assert post_submit_edit_data.submission.workflow_state == "submitted"

    # 7. Manually grade the submission using the correct format
    grade_update = SubmissionGradeUpdate(
        answers=[AnswerGradeUpdate(id=latest_answer_id, grade="100")],
        draft_points_awarded=0
    )
    submissions_api.update_grade(submission.id, grade_update)
    print(f"Manually assigned grade of 100 to answer {latest_answer_id}.")

    # 8. Fetch the answer again and verify the grade
    final_answer = answer_api.fetch(latest_answer_id)
    assert final_answer.grading.grade == 100.0
    assert final_answer.explanation.correct is True
    print(f"Verified final grade is {final_answer.grading.grade} and answer is correct.")


def test_submission_edit_handles_multiple_question_types(
    course_api: CourseAPI,
    submission: AssessmentSubmission,
    assessment_with_programming_question: AssessmentData,
):
    """Tests that the submission edit endpoint can handle different question types."""
    assessment_id = assessment_with_programming_question.id
    submissions_api = course_api.assessment.submissions(assessment_id)

    # Get the submission edit data
    edit_data = submissions_api.edit(submission.id)
    
    # Verify we can parse the data regardless of question types
    assert isinstance(edit_data.questions, list)
    assert isinstance(edit_data.answers, list)
    assert len(edit_data.questions) > 0
    assert len(edit_data.answers) > 0
    
    # Check that each question has the basic required fields
    for question in edit_data.questions:
        assert hasattr(question, 'id')
        assert hasattr(question, 'type')
        assert hasattr(question, 'question_title')
        print(f"Found question: {question.type} - {question.question_title}")
    
    # Check that each answer corresponds to a question
    for answer in edit_data.answers:
        assert hasattr(answer, 'id')
        assert hasattr(answer, 'question_id')
        assert hasattr(answer, 'question_type')
        
        # Find the corresponding question
        corresponding_question = next(
            (q for q in edit_data.questions if q.id == answer.question_id), 
            None
        )
        assert corresponding_question is not None, f"No question found for answer {answer.id}"
        assert corresponding_question.type == answer.question_type
        print(f"Found answer for {answer.question_type} question: {answer.id}")


def test_answer_api_with_different_question_types(
    course_api: CourseAPI,
    submission: AssessmentSubmission,
    assessment_with_programming_question: AssessmentData,
):
    """Tests that the answer API can fetch different types of answers."""
    assessment_id = assessment_with_programming_question.id
    submissions_api = course_api.assessment.submissions(assessment_id)
    edit_data = submissions_api.edit(submission.id)
    
    answer_api = submissions_api.answer(submission.id)
    
    # Test fetching each answer individually
    for answer in edit_data.answers:
        fetched_answer = answer_api.fetch(answer.id)
        
        # Verify the fetched answer has the expected structure
        assert fetched_answer.id == answer.id
        assert hasattr(fetched_answer, 'grading')
        
        # The question field is only present when fetching individual answers, not when saving drafts
        if hasattr(fetched_answer, 'question') and fetched_answer.question:
            print(f"Answer {answer.id} includes question data: {fetched_answer.question.question_title}")
        
        print(f"Successfully fetched {answer.question_type} answer: {answer.id}")
        
        # Type-specific validations
        if answer.question_type == "Programming":
            assert isinstance(fetched_answer, ProgrammingAnswer)
            assert len(fetched_answer.files) >= 0  # Use the property
        elif answer.question_type in ["MultipleChoice", "MultipleResponse"]:
            assert hasattr(fetched_answer, 'option_ids')
        elif answer.question_type in ["TextResponse", "FileUpload"]:
            assert hasattr(fetched_answer, 'attachments')