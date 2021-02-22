from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


def list_policies():

    credentials = GoogleCredentials.get_application_default()

    service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

    # Name of the resource to list `Constraints` for.
    resource = 'projects/skyuk-uk-mikaelmichelier-poc'  # TODO: Update placeholder value.
    constraints = []

    list_available_org_policy_constraints_request_body = {
        # TODO: Add desired entries to the request body.
    }

    while True:
        request = service.projects().listAvailableOrgPolicyConstraints(resource=resource, body=list_available_org_policy_constraints_request_body)
        response = request.execute()

        for constraint in response.get('constraints', []):
            # TODO: Change code below to process each `constraint` resource:
            constraints.append(constraint['name'])

        if 'nextPageToken' not in response:
            break
        list_available_org_policy_constraints_request_body['pageToken'] = response['nextPageToken']

    return constraints
