import datetime
import uuid

import pytest
from coursemology_py.api.course import CourseAPI
from coursemology_py.exceptions import CoursemologyAPIError
from coursemology_py.models.course.disbursement import (
    DisbursementCreateResponse,
    DisbursementIndexResponse,
    DisbursementPayload,
    DisbursementRecordPayload,
    ForumDisbursementIndexResponse,
    ForumDisbursementPayload,
)
from coursemology_py.models.course.users import CourseUser

# --- Standard Disbursement Tests ---


def test_disbursement_index(course_api: CourseAPI):
    """Tests fetching the initial data for standard EXP disbursement."""
    try:
        response = course_api.disbursement.index()
        assert isinstance(response, DisbursementIndexResponse)
        assert isinstance(response.course_users, list)
        assert isinstance(response.course_groups, list)
        print(f"\nSuccessfully fetched disbursement index with {len(response.course_users)} users.")
    except CoursemologyAPIError as e:
        pytest.fail(f"API call to disbursement.index() failed: {e}")


def test_standard_disbursement_create_and_cleanup(course_api: CourseAPI, test_user: CourseUser):
    """
    Tests creating a standard disbursement and then cleans up the created
    experience points record.
    """
    reason = f"Automated test disbursement {uuid.uuid4().hex[:8]}"
    points_to_award = 10

    record_payload = DisbursementRecordPayload(
        points_awarded=points_to_award,
        course_user_id=test_user.id,
    )
    disbursement_payload = DisbursementPayload(
        reason=reason,
        experience_points_records_attributes=[record_payload],
    )

    created_record_id: int | None = None
    try:
        # 1. Create the disbursement
        response = course_api.disbursement.create(disbursement_payload)
        assert isinstance(response, DisbursementCreateResponse)
        assert response.count == 1
        print(f"\nSuccessfully created a standard disbursement for user {test_user.id}.")

        # 2. Find the created record for cleanup
        # The create response doesn't return the ID, so we must find it.
        user_exp_records = course_api.experience_points_record.fetch_exp_for_user(test_user.id)
        found_record = next(
            (
                rec
                for rec in user_exp_records.records
                if rec.reason.text == reason and rec.points_awarded == points_to_award
            ),
            None,
        )
        assert found_record is not None, "Could not find the created EXP record for cleanup."
        created_record_id = found_record.id
        print(f"Found created EXP record with ID: {created_record_id}")

    finally:
        # 3. Clean up the created record
        if created_record_id:
            print(f"Cleaning up: Deleting EXP record {created_record_id}...")
            try:
                course_api.experience_points_record.delete(created_record_id, test_user.id)
                print(f"Successfully deleted EXP record {created_record_id}.")
            except CoursemologyAPIError as e:
                pytest.fail(f"Cleanup of EXP record failed: {e}")


# --- Forum Disbursement Tests ---


def test_forum_disbursement_index(course_api: CourseAPI):
    """Tests fetching data for forum EXP disbursement."""
    # Define a time range, e.g., the last 30 days
    end_time = datetime.datetime.now(datetime.UTC)
    start_time = end_time - datetime.timedelta(days=30)
    weekly_cap = 100

    try:
        response = course_api.disbursement.forum_disbursement_index(start_time, end_time, weekly_cap)
        assert isinstance(response, ForumDisbursementIndexResponse)
        assert isinstance(response.forum_users, list)
        assert response.filters.weekly_cap == weekly_cap
        print(f"\nSuccessfully fetched forum disbursement index with {len(response.forum_users)} eligible users.")
    except CoursemologyAPIError as e:
        pytest.fail(f"API call to forum_disbursement_index() failed: {e}")


def test_forum_disbursement_create(course_api: CourseAPI):
    """
    Tests creating a forum disbursement if there are eligible users.
    Note: This test does not perform cleanup due to the complexity of tracking
    multiple created records. It primarily validates the API call.
    """
    end_time = datetime.datetime.now(datetime.UTC)
    start_time = end_time - datetime.timedelta(days=30)
    weekly_cap = 100

    # 1. Fetch eligible users first
    index_response = course_api.disbursement.forum_disbursement_index(start_time, end_time, weekly_cap)
    eligible_users = [user for user in index_response.forum_users if user.points > 0]

    if not eligible_users:
        pytest.skip("No users with forum activity found to test forum disbursement creation.")

    # 2. Prepare payload for eligible users
    record_payloads = [
        DisbursementRecordPayload(points_awarded=user.points, course_user_id=user.id) for user in eligible_users
    ]
    disbursement_payload = ForumDisbursementPayload(
        reason=f"Automated forum disbursement test {uuid.uuid4().hex[:8]}",
        experience_points_records_attributes=record_payloads,
        start_time=start_time,
        end_time=end_time,
        weekly_cap=weekly_cap,
    )

    # 3. Create the disbursement
    try:
        response = course_api.disbursement.forum_disbursement_create(disbursement_payload)
        assert isinstance(response, DisbursementCreateResponse)
        assert response.count == len(eligible_users)
        print(f"\nSuccessfully created a forum disbursement for {len(eligible_users)} users.")
    except CoursemologyAPIError as e:
        pytest.fail(f"API call to forum_disbursement_create() failed: {e}")
