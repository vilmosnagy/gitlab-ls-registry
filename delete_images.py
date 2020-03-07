import os
from datetime import datetime, timedelta

from gitlab import get_paged_api, get_api, delete_api

ENABLED_PROJECTS_TO_CLEAR = [project.strip() for project in os.environ['ENABLED_PROJECTS_TO_CLEAR'].split(',')]

def get_all_images_for_project(project):
    project_repositories = get_paged_api(f"/api/v4/projects/{project['id']}/registry/repositories")
    if len(project_repositories) > 0:
        ret_list = []
        for repository in project_repositories:
            repo_tags = get_paged_api(f"/api/v4/projects/{project['id']}/registry/repositories/{repository['id']}/tags")
            for tag in repo_tags:
                tag_details = get_api(f"/api/v4/projects/{project['id']}/registry/repositories/{repository['id']}/tags/{tag['name']}").json()
                tag_name = tag_details["name"]
                tag_size = tag_details["total_size"]
                created_at = tag_details["created_at"]
                ret_list += [{
                    "image_name": tag['path'],
                    "image_tag": tag_name,
                    "size": tag_size,
                    "created_at": created_at,
                    "repository_id": repository['id']
                }]
        return ret_list
    else:
        return []


def get_all_projects_path_with_namespaces():
    projects_json = get_paged_api("api/v4/projects")
    return list(map(lambda x: {'name': x["path_with_namespace"], 'id': x['id']}, projects_json))


def delete_old_images_if_enabled(project):
    if project['name'] not in ENABLED_PROJECTS_TO_CLEAR:
        print(f'skipping project: {project["name"]}')
        return
    images = get_all_images_for_project(project)
    images_to_delete = list(filter(lambda image: datetime.fromisoformat(image['created_at']).replace(tzinfo=None) < (datetime.now() - timedelta(days=14)), images))
    for image_to_delete in images_to_delete:
        print(f'deleting {image_to_delete["image_name"]}')
        delete_api(f"/api/v4/projects/{project['id']}/registry/repositories/{image_to_delete['repository_id']}/tags/{image_to_delete['image_tag']}")


def main():
    print("Will delete images older than 2 weeks from the following repositories: ")
    for image in ENABLED_PROJECTS_TO_CLEAR:
        print(f" - {image}")
    print()

    projects = get_all_projects_path_with_namespaces()
    for project in projects:
        delete_old_images_if_enabled(project)


if __name__ == "__main__":
    main()
