GET_LIST_OF_MEMBERS_IN_ORG = """
  query($org: String!, $after: String) {
      organization(login: $org) {
        membersWithRole(first: 100, after: $after) {
          pageInfo {
            endCursor
            hasNextPage
          }
          edges {
            node {
              login
              organizationVerifiedDomainEmails(login: $org)
            }
          }
        }
      }
    }
"""

QUERIES = {"GET_LIST_OF_MEMBERS_IN_ORG": GET_LIST_OF_MEMBERS_IN_ORG}
