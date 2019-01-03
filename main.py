import csv
import requests

GITLAB_URL = "<TODO>"
GITLAB_USERNAME = "<TODO>"
GITLAB_TOKEN = "<TODO>"


def get_all_images_for_project(project):
    response = get_api(f"/{project}/container_registry.json")
    if response.status_code is not 200:
        return []
    all_image_info = response.json()
    if len(all_image_info) > 0:
        ret_list = []
        for image in all_image_info:
            image_name = image["path"]
            image_tags = get_api(image["tags_path"]).json()
            for image_tag in image_tags:
                tag_name = image_tag["name"]
                tag_size = image_tag["total_size"]
                created_at = image_tag["created_at"]
                ret_list += [{
                    "image_name": image_name,
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


def main():
    projects = get_all_projects_path_with_namespaces()
    images_for_projects = get_all_images_for_each_project(projects)
    write_image_info_to_csv(images_for_projects)


def get_all_projects_path_with_namespaces():
    projects_json = get_paged_api("api/v4/projects")
    return list(map(lambda x: x["path_with_namespace"], projects_json))


def get_paged_api(url):
    page = 1
    ret_array = []
    response = get_api(url, page).json()
    ret_array += response
    while len(response) > 0:
        page += 1
        response = get_api(url, page).json()
        ret_array += response
    return ret_array


def get_api(url, page=None):
    url = f"{GITLAB_URL}/{url}"
    if not url.__contains__('?'):
        url = f"{url}?private_token={GITLAB_TOKEN}"
    else:
        url = f"{url}&private_token={GITLAB_TOKEN}"
    if page:
        url = url + f"&page={page}"
    return requests.get(url)


if __name__ == "__main__":
    main()
