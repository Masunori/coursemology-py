import uuid
from collections.abc import Generator

import pytest
from coursemology_py.api.course import CourseAPI
from coursemology_py.exceptions import CoursemologyAPIError
from coursemology_py.models.common import JobSubmitted
from coursemology_py.models.course.disbursement import (
    DisbursementPayload,
    DisbursementRecordPayload,
)
from coursemology_py.models.course.experience_points import (
    ExperiencePointsRecord,
    ExperiencePointsRecordPayload,
    ExperiencePointsRecordsForUserResponse,
    ExperiencePointsRecordsResponse,
)
from coursemology_py.models.course.users import CourseUser

# --- Fixture for a temporary, managed EXP record ---


@pytest.fixture(scope="function")
def test_exp_record(course_api: CourseAPI, test_user: CourseUser) -> Generator[ExperiencePointsRecord]:
    """
    A function-scoped fixture that creates a single, temporary experience points
    record for a test user and cleans it up afterward.
    """
    reason = f"Automated test EXP record {uuid.uuid4().hex[:8]}"
    points_to_award = 50
    print(f"\nCreating temporary EXP record for user {test_user.id} with reason '{reason}'...")

    # 1. Create the record via the disbursement API
    record_payload = DisbursementRecordPayload(points_awarded=points_to_award, course_user_id=test_user.id)
    disbursement_payload = DisbursementPayload(reason=reason, experience_points_records_attributes=[record_payload])
    course_api.disbursement.create(disbursement_payload)

    # 2. Find the record we just created to get its ID
    created_record: ExperiencePointsRecord | None = None
    try:
        user_exp_records = course_api.experience_points_record.fetch_exp_for_user(test_user.id)
        created_record = next((rec for rec in user_exp_records.records if rec.reason.text == reason), None)
        assert created_record is not None, "Failed to find the newly created EXP record."
        print(f"Successfully created EXP record with ID: {created_record.id}")

        # 3. Yield the record to the test
        yield created_record

    finally:
        # 4. Clean up the record
        if created_record:
            print(f"\nCleaning up: Deleting EXP record {created_record.id}...")
            try:
                course_api.experience_points_record.delete(created_record.id, test_user.id)
                print(f"Successfully deleted EXP record {created_record.id}.")
            except CoursemologyAPIError as e:
                pytest.fail(f"Cleanup failed for EXP record {created_record.id}. Error: {e}")


# --- API Tests ---


def test_fetch_all_exp(course_api: CourseAPI):
    """Tests fetching all experience points records for the course."""
    response = course_api.experience_points_record.fetch_all_exp(page_num=1)
    assert isinstance(response, ExperiencePointsRecordsResponse)
    assert isinstance(response.records, list)
    assert response.filters is not None
    print(f"\nSuccessfully fetched {len(response.records)} EXP records for the course.")


def test_fetch_exp_for_user(course_api: CourseAPI, test_user: CourseUser):
    """Tests fetching all experience points records for a specific user."""
    response = course_api.experience_points_record.fetch_exp_for_user(user_id=test_user.id)
    assert isinstance(response, ExperiencePointsRecordsForUserResponse)
    assert response.student_name == test_user.name
    assert isinstance(response.records, list)
    print(f"\nSuccessfully fetched {len(response.records)} EXP records for user {test_user.id}.")


def test_download_csv(course_api: CourseAPI):
    """Tests that triggering a CSV download returns a job object."""
    response = course_api.experience_points_record.download_csv()
    assert isinstance(response, JobSubmitted)
    assert "jobs" in response.job_url
    print(f"\nSuccessfully triggered CSV download job at: {response.job_url}")


def test_exp_record_update(course_api: CourseAPI, test_exp_record: ExperiencePointsRecord, test_user: CourseUser):
    """Tests updating an existing experience points record."""
    updated_reason = f"Updated reason {uuid.uuid4().hex[:8]}"
    updated_points = 123
    payload = ExperiencePointsRecordPayload(reason=updated_reason, points_awarded=updated_points)

    # Update the record
    response = course_api.experience_points_record.update(test_exp_record.id, test_user.id, payload)

    # Verify the changes
    assert isinstance(response, ExperiencePointsRecord)
    assert response.id == test_exp_record.id
    assert response.reason.text == updated_reason
    assert response.points_awarded == updated_points
    print(f"\nSuccessfully updated EXP record {test_exp_record.id}.")


def test_exp_record_delete(course_api: CourseAPI, test_user: CourseUser):
    """Tests the explicit deletion of an experience points record."""
    reason = f"To Be Deleted {uuid.uuid4().hex[:8]}"
    record_payload = DisbursementRecordPayload(points_awarded=10, course_user_id=test_user.id)
    disbursement_payload = DisbursementPayload(reason=reason, experience_points_records_attributes=[record_payload])

    # 1. Create a record specifically for this test
    course_api.disbursement.create(disbursement_payload)
    user_exp_records = course_api.experience_points_record.fetch_exp_for_user(test_user.id)
    record_to_delete = next((rec for rec in user_exp_records.records if rec.reason.text == reason), None)
    assert record_to_delete is not None, "Failed to create a record for the delete test."
    print(f"\nCreated EXP record {record_to_delete.id} for deletion test.")

    # 2. Delete it
    course_api.experience_points_record.delete(record_to_delete.id, test_user.id)
    print(f"Deleted EXP record {record_to_delete.id}.")

    # 3. Verify it's gone
    records_after_delete = course_api.experience_points_record.fetch_exp_for_user(test_user.id).records
    record_ids = [rec.id for rec in records_after_delete]
    assert record_to_delete.id not in record_ids, "Deleted EXP record ID should not be in the user's list."
    print("Verified that the EXP record was successfully deleted.")
