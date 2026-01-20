"""Stream type classes for tap-greenhouse."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from singer_sdk import typing as th

from tap_greenhouse.client import GreenhouseStream

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

# Reusable schema components
UserRefSchema = th.ObjectType(
    th.Property("id", th.IntegerType),
    th.Property("first_name", th.StringType),
    th.Property("last_name", th.StringType),
    th.Property("name", th.StringType),
    th.Property("employee_id", th.StringType),
)

DepartmentRefSchema = th.ObjectType(
    th.Property("id", th.IntegerType),
    th.Property("name", th.StringType),
    th.Property("parent_id", th.IntegerType),
    th.Property("parent_department_external_id", th.StringType),
    th.Property("child_ids", th.ArrayType(th.IntegerType)),
    th.Property("child_department_external_ids", th.ArrayType(th.StringType)),
    th.Property("external_id", th.StringType),
)

OfficeRefSchema = th.ObjectType(
    th.Property("id", th.IntegerType),
    th.Property("name", th.StringType),
    th.Property("location", th.ObjectType(th.Property("name", th.StringType))),
    th.Property("parent_id", th.IntegerType),
    th.Property("child_ids", th.ArrayType(th.IntegerType)),
    th.Property("external_id", th.StringType),
)

CustomFieldsSchema = th.ObjectType(additional_properties=th.CustomType({"type": ["string", "number", "boolean", "null", "array", "object"]}))

KeyedCustomFieldSchema = th.ObjectType(
    additional_properties=th.ObjectType(
        th.Property("name", th.StringType),
        th.Property("type", th.StringType),
        th.Property("value", th.CustomType({"type": ["string", "number", "boolean", "null", "array", "object"]})),
    )
)


class CandidatesStream(GreenhouseStream):
    """Candidates stream."""

    name = "candidates"
    path = "/candidates"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("first_name", th.StringType),
        th.Property("last_name", th.StringType),
        th.Property("company", th.StringType),
        th.Property("title", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("last_activity", th.DateTimeType),
        th.Property("is_private", th.BooleanType),
        th.Property("photo_url", th.StringType),
        th.Property("can_email", th.BooleanType),
        th.Property(
            "phone_numbers",
            th.ArrayType(
                th.ObjectType(
                    th.Property("value", th.StringType),
                    th.Property("type", th.StringType),
                )
            ),
        ),
        th.Property(
            "addresses",
            th.ArrayType(
                th.ObjectType(
                    th.Property("value", th.StringType),
                    th.Property("type", th.StringType),
                )
            ),
        ),
        th.Property(
            "email_addresses",
            th.ArrayType(
                th.ObjectType(
                    th.Property("value", th.StringType),
                    th.Property("type", th.StringType),
                )
            ),
        ),
        th.Property(
            "website_addresses",
            th.ArrayType(
                th.ObjectType(
                    th.Property("value", th.StringType),
                    th.Property("type", th.StringType),
                )
            ),
        ),
        th.Property(
            "social_media_addresses",
            th.ArrayType(
                th.ObjectType(
                    th.Property("value", th.StringType),
                )
            ),
        ),
        th.Property("recruiter", UserRefSchema),
        th.Property("coordinator", UserRefSchema),
        th.Property("tags", th.ArrayType(th.StringType)),
        th.Property("application_ids", th.ArrayType(th.IntegerType)),
        th.Property(
            "applications",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("candidate_id", th.IntegerType),
                    th.Property("prospect", th.BooleanType),
                    th.Property("applied_at", th.DateTimeType),
                    th.Property("rejected_at", th.DateTimeType),
                    th.Property("last_activity_at", th.DateTimeType),
                    th.Property("status", th.StringType),
                    th.Property(
                        "jobs",
                        th.ArrayType(
                            th.ObjectType(
                                th.Property("id", th.IntegerType),
                                th.Property("name", th.StringType),
                            )
                        ),
                    ),
                    th.Property(
                        "current_stage",
                        th.ObjectType(
                            th.Property("id", th.IntegerType),
                            th.Property("name", th.StringType),
                        ),
                    ),
                    th.Property(
                        "source",
                        th.ObjectType(
                            th.Property("id", th.IntegerType),
                            th.Property("public_name", th.StringType),
                        ),
                    ),
                )
            ),
        ),
        th.Property(
            "educations",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("school_name", th.StringType),
                    th.Property("degree", th.StringType),
                    th.Property("discipline", th.StringType),
                    th.Property("start_date", th.StringType),
                    th.Property("end_date", th.StringType),
                )
            ),
        ),
        th.Property(
            "employments",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("company_name", th.StringType),
                    th.Property("title", th.StringType),
                    th.Property("start_date", th.StringType),
                    th.Property("end_date", th.StringType),
                )
            ),
        ),
        th.Property(
            "attachments",
            th.ArrayType(
                th.ObjectType(
                    th.Property("filename", th.StringType),
                    th.Property("url", th.StringType),
                    th.Property("type", th.StringType),
                    th.Property("created_at", th.DateTimeType),
                )
            ),
        ),
        th.Property("linked_user_ids", th.ArrayType(th.IntegerType)),
        th.Property("custom_fields", CustomFieldsSchema),
        th.Property("keyed_custom_fields", KeyedCustomFieldSchema),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params, including updated_at filter for incremental sync."""
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_replication_key_value(context)
        if start_date:
            params["updated_after"] = start_date
        return params


class ApplicationsStream(GreenhouseStream):
    """Applications stream."""

    name = "applications"
    path = "/applications"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = "last_activity_at"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("candidate_id", th.IntegerType),
        th.Property("prospect", th.BooleanType),
        th.Property("applied_at", th.DateTimeType),
        th.Property("rejected_at", th.DateTimeType),
        th.Property("last_activity_at", th.DateTimeType),
        th.Property(
            "location",
            th.ObjectType(
                th.Property("address", th.StringType),
            ),
        ),
        th.Property(
            "source",
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("public_name", th.StringType),
            ),
        ),
        th.Property("credited_to", UserRefSchema),
        th.Property("recruiter", UserRefSchema),
        th.Property("coordinator", UserRefSchema),
        th.Property(
            "rejection_reason",
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("name", th.StringType),
                th.Property("type", th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                )),
            ),
        ),
        th.Property("rejection_details", CustomFieldsSchema),
        th.Property(
            "jobs",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                )
            ),
        ),
        th.Property("job_post_id", th.IntegerType),
        th.Property("status", th.StringType),
        th.Property(
            "current_stage",
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("name", th.StringType),
            ),
        ),
        th.Property(
            "answers",
            th.ArrayType(
                th.ObjectType(
                    th.Property("question", th.StringType),
                    th.Property("answer", th.StringType),
                )
            ),
        ),
        th.Property("prospective_office", OfficeRefSchema),
        th.Property("prospective_department", DepartmentRefSchema),
        th.Property(
            "prospect_detail",
            th.ObjectType(
                th.Property("prospect_pool", th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                )),
                th.Property("prospect_stage", th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                )),
                th.Property("prospect_owner", UserRefSchema),
            ),
        ),
        th.Property("custom_fields", CustomFieldsSchema),
        th.Property("keyed_custom_fields", KeyedCustomFieldSchema),
        th.Property(
            "attachments",
            th.ArrayType(
                th.ObjectType(
                    th.Property("filename", th.StringType),
                    th.Property("url", th.StringType),
                    th.Property("type", th.StringType),
                    th.Property("created_at", th.DateTimeType),
                )
            ),
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params, including last_activity_after filter for incremental sync."""
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_replication_key_value(context)
        if start_date:
            params["last_activity_after"] = start_date
        return params


class JobsStream(GreenhouseStream):
    """Jobs stream."""

    name = "jobs"
    path = "/jobs"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("name", th.StringType),
        th.Property("requisition_id", th.StringType),
        th.Property("notes", th.StringType),
        th.Property("confidential", th.BooleanType),
        th.Property("status", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("opened_at", th.DateTimeType),
        th.Property("closed_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("is_template", th.BooleanType),
        th.Property("copied_from_id", th.IntegerType),
        th.Property("departments", th.ArrayType(DepartmentRefSchema)),
        th.Property("offices", th.ArrayType(OfficeRefSchema)),
        th.Property("custom_fields", CustomFieldsSchema),
        th.Property("keyed_custom_fields", KeyedCustomFieldSchema),
        th.Property(
            "hiring_team",
            th.ObjectType(
                th.Property("hiring_managers", th.ArrayType(UserRefSchema)),
                th.Property(
                    "recruiters",
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("id", th.IntegerType),
                            th.Property("first_name", th.StringType),
                            th.Property("last_name", th.StringType),
                            th.Property("name", th.StringType),
                            th.Property("employee_id", th.StringType),
                            th.Property("responsible", th.BooleanType),
                        )
                    ),
                ),
                th.Property(
                    "coordinators",
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("id", th.IntegerType),
                            th.Property("first_name", th.StringType),
                            th.Property("last_name", th.StringType),
                            th.Property("name", th.StringType),
                            th.Property("employee_id", th.StringType),
                            th.Property("responsible", th.BooleanType),
                        )
                    ),
                ),
                th.Property("sourcers", th.ArrayType(UserRefSchema)),
            ),
        ),
        th.Property(
            "openings",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("opening_id", th.StringType),
                    th.Property("status", th.StringType),
                    th.Property("opened_at", th.DateTimeType),
                    th.Property("closed_at", th.DateTimeType),
                    th.Property("application_id", th.IntegerType),
                    th.Property(
                        "close_reason",
                        th.ObjectType(
                            th.Property("id", th.IntegerType),
                            th.Property("name", th.StringType),
                        ),
                    ),
                )
            ),
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params, including updated_at filter for incremental sync."""
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_replication_key_value(context)
        if start_date:
            params["updated_after"] = start_date
        return params


class UsersStream(GreenhouseStream):
    """Users stream."""

    name = "users"
    path = "/users"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("name", th.StringType),
        th.Property("first_name", th.StringType),
        th.Property("last_name", th.StringType),
        th.Property("primary_email_address", th.StringType),
        th.Property("emails", th.ArrayType(th.StringType)),
        th.Property("employee_id", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("disabled", th.BooleanType),
        th.Property("site_admin", th.BooleanType),
        th.Property("linked_candidate_ids", th.ArrayType(th.IntegerType)),
        th.Property("offices", th.ArrayType(OfficeRefSchema)),
        th.Property("departments", th.ArrayType(DepartmentRefSchema)),
        th.Property("custom_fields", CustomFieldsSchema),
        th.Property("keyed_custom_fields", KeyedCustomFieldSchema),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params, including updated_at filter for incremental sync."""
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_replication_key_value(context)
        if start_date:
            params["updated_after"] = start_date
        return params


class DepartmentsStream(GreenhouseStream):
    """Departments stream."""

    name = "departments"
    path = "/departments"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("name", th.StringType),
        th.Property("parent_id", th.IntegerType),
        th.Property("parent_department_external_id", th.StringType),
        th.Property("child_ids", th.ArrayType(th.IntegerType)),
        th.Property("child_department_external_ids", th.ArrayType(th.StringType)),
        th.Property("external_id", th.StringType),
    ).to_dict()


class OfficesStream(GreenhouseStream):
    """Offices stream."""

    name = "offices"
    path = "/offices"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("name", th.StringType),
        th.Property(
            "location",
            th.ObjectType(
                th.Property("name", th.StringType),
            ),
        ),
        th.Property("primary_contact_user_id", th.IntegerType),
        th.Property("parent_id", th.IntegerType),
        th.Property("parent_office_external_id", th.StringType),
        th.Property("child_ids", th.ArrayType(th.IntegerType)),
        th.Property("child_office_external_ids", th.ArrayType(th.StringType)),
        th.Property("external_id", th.StringType),
    ).to_dict()


class OffersStream(GreenhouseStream):
    """Offers stream."""

    name = "offers"
    path = "/offers"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("version", th.IntegerType),
        th.Property("application_id", th.IntegerType),
        th.Property("job_id", th.IntegerType),
        th.Property("candidate_id", th.IntegerType),
        th.Property(
            "opening",
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("opening_id", th.StringType),
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("sent_at", th.StringType),
        th.Property("resolved_at", th.DateTimeType),
        th.Property("starts_at", th.StringType),
        th.Property("status", th.StringType),
        th.Property("custom_fields", CustomFieldsSchema),
        th.Property("keyed_custom_fields", KeyedCustomFieldSchema),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params, including updated_at filter for incremental sync."""
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_replication_key_value(context)
        if start_date:
            params["updated_after"] = start_date
        return params


class ScheduledInterviewsStream(GreenhouseStream):
    """Scheduled Interviews stream."""

    name = "scheduled_interviews"
    path = "/scheduled_interviews"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("application_id", th.IntegerType),
        th.Property("external_event_id", th.StringType),
        th.Property(
            "start",
            th.ObjectType(
                th.Property("date_time", th.DateTimeType),
                th.Property("date", th.StringType),
            ),
        ),
        th.Property(
            "end",
            th.ObjectType(
                th.Property("date_time", th.DateTimeType),
                th.Property("date", th.StringType),
            ),
        ),
        th.Property("location", th.StringType),
        th.Property("video_conferencing_url", th.StringType),
        th.Property("status", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property(
            "interview",
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("name", th.StringType),
            ),
        ),
        th.Property("organizer", UserRefSchema),
        th.Property(
            "interviewers",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("first_name", th.StringType),
                    th.Property("last_name", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("employee_id", th.StringType),
                    th.Property("response_status", th.StringType),
                    th.Property("scorecard_id", th.IntegerType),
                )
            ),
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params, including updated_at filter for incremental sync."""
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_replication_key_value(context)
        if start_date:
            params["updated_after"] = start_date
        return params


class JobStagesStream(GreenhouseStream):
    """Job Stages stream."""

    name = "job_stages"
    path = "/job_stages"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("name", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("job_id", th.IntegerType),
        th.Property("priority", th.IntegerType),
        th.Property(
            "interviews",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("schedulable", th.BooleanType),
                    th.Property("estimated_minutes", th.IntegerType),
                    th.Property("default_interviewer_users", th.ArrayType(UserRefSchema)),
                    th.Property(
                        "interview_kit",
                        th.ObjectType(
                            th.Property("id", th.IntegerType),
                            th.Property("content", th.StringType),
                            th.Property(
                                "questions",
                                th.ArrayType(
                                    th.ObjectType(
                                        th.Property("id", th.IntegerType),
                                        th.Property("question", th.StringType),
                                    )
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params, including updated_at filter for incremental sync."""
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_replication_key_value(context)
        if start_date:
            params["updated_after"] = start_date
        return params


class ScorecardsStream(GreenhouseStream):
    """Scorecards stream."""

    name = "scorecards"
    path = "/scorecards"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("updated_at", th.DateTimeType),
        th.Property("created_at", th.DateTimeType),
        th.Property("interview", th.StringType),
        th.Property("interview_step", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
        )),
        th.Property("candidate_id", th.IntegerType),
        th.Property("application_id", th.IntegerType),
        th.Property("interviewed_at", th.DateTimeType),
        th.Property("submitted_by", UserRefSchema),
        th.Property("interviewer", UserRefSchema),
        th.Property("submitted_at", th.DateTimeType),
        th.Property("overall_recommendation", th.StringType),
        th.Property(
            "attributes",
            th.ArrayType(
                th.ObjectType(
                    th.Property("name", th.StringType),
                    th.Property("type", th.StringType),
                    th.Property("note", th.StringType),
                    th.Property("rating", th.StringType),
                )
            ),
        ),
        th.Property(
            "ratings",
            CustomFieldsSchema,
        ),
        th.Property(
            "questions",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("question", th.StringType),
                    th.Property("answer", th.StringType),
                )
            ),
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params, including updated_at filter for incremental sync."""
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_replication_key_value(context)
        if start_date:
            params["updated_after"] = start_date
        return params


class SourcesStream(GreenhouseStream):
    """Sources stream."""

    name = "sources"
    path = "/sources"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("name", th.StringType),
        th.Property("type", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
        )),
    ).to_dict()


class RejectionReasonsStream(GreenhouseStream):
    """Rejection Reasons stream."""

    name = "rejection_reasons"
    path = "/rejection_reasons"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("name", th.StringType),
        th.Property("type", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
        )),
    ).to_dict()


class JobPostsStream(GreenhouseStream):
    """Job Posts stream."""

    name = "job_posts"
    path = "/job_posts"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("title", th.StringType),
        th.Property("location", th.ObjectType(
            th.Property("id", th.IntegerType),
            th.Property("name", th.StringType),
        )),
        th.Property("internal", th.BooleanType),
        th.Property("external", th.BooleanType),
        th.Property("active", th.BooleanType),
        th.Property("live", th.BooleanType),
        th.Property("first_published_at", th.DateTimeType),
        th.Property("job_id", th.IntegerType),
        th.Property("content", th.StringType),
        th.Property("internal_content", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property(
            "questions",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("label", th.StringType),
                    th.Property("description", th.StringType),
                    th.Property("required", th.BooleanType),
                    th.Property("private", th.BooleanType),
                    th.Property("active", th.BooleanType),
                    th.Property("type", th.StringType),
                    th.Property(
                        "answer_options",
                        th.ArrayType(
                            th.ObjectType(
                                th.Property("id", th.IntegerType),
                                th.Property("label", th.StringType),
                                th.Property("free_form", th.BooleanType),
                            )
                        ),
                    ),
                )
            ),
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params, including updated_at filter for incremental sync."""
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_replication_key_value(context)
        if start_date:
            params["updated_after"] = start_date
        return params


class CustomFieldsStream(GreenhouseStream):
    """Custom Fields stream."""

    name = "custom_fields"
    path = "/custom_fields"
    primary_keys: ClassVar[tuple[str, ...]] = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("name", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("field_type", th.StringType),
        th.Property("priority", th.IntegerType),
        th.Property("value_type", th.StringType),
        th.Property("private", th.BooleanType),
        th.Property("required", th.BooleanType),
        th.Property("require_approval", th.BooleanType),
        th.Property("trigger_new_version", th.BooleanType),
        th.Property("name_key", th.StringType),
        th.Property("description", th.StringType),
        th.Property("expose_in_job_board_api", th.BooleanType),
        th.Property("api_only", th.BooleanType),
        th.Property("offices", th.ArrayType(OfficeRefSchema)),
        th.Property("departments", th.ArrayType(DepartmentRefSchema)),
        th.Property("template_token_string", th.StringType),
        th.Property(
            "custom_field_options",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("priority", th.IntegerType),
                    th.Property("external_id", th.StringType),
                )
            ),
        ),
    ).to_dict()


class ActivityFeedStream(GreenhouseStream):
    """Activity Feed stream - requires candidate_id context."""

    name = "activity_feed"
    path = "/candidates/{candidate_id}/activity_feed"
    primary_keys: ClassVar[tuple[str, ...]] = ("id", "candidate_id")
    replication_key = None
    parent_stream_type = CandidatesStream

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("candidate_id", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("subject", th.StringType),
        th.Property("body", th.StringType),
        th.Property("private", th.BooleanType),
        th.Property("visibility", th.StringType),
        th.Property("user", UserRefSchema),
    ).to_dict()

    def get_child_context(
        self,
        record: dict,
        context: Context | None,
    ) -> dict:
        """Return context for child streams."""
        return {"candidate_id": record["id"]}

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Return URL params."""
        params = super().get_url_params(context, next_page_token)
        return params

    def post_process(
        self,
        row: dict,
        context: Context | None = None,
    ) -> dict | None:
        """Add candidate_id to each activity record."""
        if context:
            row["candidate_id"] = context.get("candidate_id")
        return row
