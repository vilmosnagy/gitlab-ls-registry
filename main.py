import csv

from gitlab import get_paged_api, get_api


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
                    "image_path": repository['path'],
                    "image_name": tag['path'],
                    "image_tag": tag_name,
                    "size": tag_size,
                    "created_at": created_at
                }]
        return ret_list
    else:
        return []


def get_all_images_for_each_project(projects):
    ret_list = []
    for project in projects:
        ret_list += get_all_images_for_project(project)
    return ret_list


def write_image_info_to_csv(images_for_projects):
    with open("output.csv", 'w') as resultFile:
        wr = csv.DictWriter(resultFile, images_for_projects[0].keys(), dialect='excel')
        wr.writeheader()
        for image in images_for_projects:
            wr.writerow(image)


def get_all_projects_path_with_namespaces():
    projects_json = get_paged_api("api/v4/projects")
    return list(map(lambda x: {'name': x["path_with_namespace"], 'id': x['id']}, projects_json))


def main():
    projects = get_all_projects_path_with_namespaces()
    images_for_projects = get_all_images_for_each_project(projects)
    write_image_info_to_csv(images_for_projects)


if __name__ == "__main__":
    main()
