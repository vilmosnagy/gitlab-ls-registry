from datetime import datetime, timedelta

from gitlab import get_paged_api, delete_api

ENABLED_PROJECTS_TO_CLEAR = [

]

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def get_all_artifacts_for_project(project):
    jobs = get_paged_api(f"/api/v4/projects/{project['id']}/jobs")
    if len(jobs) > 0:
        return list(filter(lambda job: "artifacts_file" in job, jobs))
    else:
        return []


def get_all_projects_path_with_namespaces():
    projects_json = get_paged_api("api/v4/projects")
    return list(map(lambda x: {'name': x["path_with_namespace"], 'id': x['id']}, projects_json))


def delete_old_artifacts_if_enabled(project):
    if project['name'] not in ENABLED_PROJECTS_TO_CLEAR:
        print(f'skipping project: {project["name"]}')
        return
    jobs_with_artifacts = get_all_artifacts_for_project(project)
    jobs_to_delete = list(filter(lambda image: datetime.strptime(image['created_at'], DATE_FORMAT).replace(tzinfo=None) < (datetime.now() - timedelta(days=7)),
                                 jobs_with_artifacts))
    for job_to_delete in jobs_to_delete:
        print(f'deleting {job_to_delete["id"]}')
        delete_api(f"/api/v4/projects/{project['id']}/jobs/{job_to_delete['id']}/artifacts")


def main():
    print("Will delete artifacts older than 1 weeks from the following repositories: ")
    for image in ENABLED_PROJECTS_TO_CLEAR:
        print(f" - {image}")
    print()

    projects = get_all_projects_path_with_namespaces()
    for project in projects:
        delete_old_artifacts_if_enabled(project)


if __name__ == "__main__":
    main()
