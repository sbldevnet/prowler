from re import search
from unittest import mock

from boto3 import client
from moto import mock_organizations

from prowler.providers.aws.services.organizations.organizations_service import (
    Organizations,
)
from tests.providers.aws.audit_info_utils import (
    AWS_ACCOUNT_ARN,
    AWS_REGION_EU_WEST_1,
    set_mocked_aws_audit_info,
)


class Test_organizations_account_part_of_organizations:
    @mock_organizations
    def test_no_organization(self):
        audit_info = set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1])

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.organizations.organizations_account_part_of_organizations.organizations_account_part_of_organizations.organizations_client",
                new=Organizations(audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.organizations.organizations_account_part_of_organizations.organizations_account_part_of_organizations import (
                    organizations_account_part_of_organizations,
                )

                check = organizations_account_part_of_organizations()
                result = check.execute()

                assert len(result) == 1
                assert result[0].status == "FAIL"
                assert search(
                    "AWS Organizations is not in-use for this AWS Account",
                    result[0].status_extended,
                )
                assert result[0].resource_id == "AWS Organization"
                assert result[0].resource_arn == AWS_ACCOUNT_ARN
                assert result[0].region == AWS_REGION_EU_WEST_1

    @mock_organizations
    def test_organization(self):
        audit_info = set_mocked_aws_audit_info([AWS_REGION_EU_WEST_1])

        # Create Organization
        conn = client("organizations")
        response = conn.create_organization()

        with mock.patch(
            "prowler.providers.aws.lib.audit_info.audit_info.current_audit_info",
            new=audit_info,
        ):
            with mock.patch(
                "prowler.providers.aws.services.organizations.organizations_account_part_of_organizations.organizations_account_part_of_organizations.organizations_client",
                new=Organizations(audit_info),
            ):
                # Test Check
                from prowler.providers.aws.services.organizations.organizations_account_part_of_organizations.organizations_account_part_of_organizations import (
                    organizations_account_part_of_organizations,
                )

                check = organizations_account_part_of_organizations()
                result = check.execute()

                assert len(result) == 1
                assert result[0].status == "PASS"
                assert search(
                    "Account is part of AWS Organization",
                    result[0].status_extended,
                )
                assert result[0].resource_id == response["Organization"]["Id"]
                assert result[0].resource_arn == response["Organization"]["Arn"]
                assert result[0].region == AWS_REGION_EU_WEST_1
