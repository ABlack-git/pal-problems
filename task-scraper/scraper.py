import requests
import pdfkit
import os
import io
import zipfile

from bs4 import BeautifulSoup


class Task:
    def __init__(self, task_url, base_dir, task_type, task_name):
        self._task_type = self._format_name(task_type)
        self._task_name = self._format_name(task_name)
        self.task_location = os.path.join(base_dir, self._task_type, self._task_name)
        self.task_url = task_url
        self._zip_content = None
        self._page_content = None
        self.base_url = "https://cw.felk.cvut.cz/courses/a4m33pal/"

    def save_task(self, save_empty_tasks=False):
        print(f"Task: {self._task_name}, url: {self.task_url}")
        self._get_zip_content()
        if self._zip_content is not None and len(self._zip_content) > 0:
            os.makedirs(os.path.join(self.task_location, "data"))
            self._save_data()
        else:
            print("Zip content was not found")
            if not save_empty_tasks:
                print("Ignoring")
                return
            os.makedirs(self.task_location)
        self._save_page()

    def _save_data(self):
        print("Saving content of zip archive")
        z = zipfile.ZipFile(io.BytesIO(self._zip_content))
        z.extractall(os.path.join(self.task_location, "data"))

    def _save_page(self):
        print("Saving page")
        pdfkit.from_url(self.task_url, os.path.join(self.task_location, self._task_name + ".pdf"),
                        options={'quiet': ''})

    def _get_zip_content(self):
        resp = requests.get(self.task_url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        for link in soup.find_all('a'):
            text = link.getText()
            if "public data" in text.lower():
                self._zip_content = requests.get(self.base_url + link.get('href')).content
                print(f"Found link to data: {link.get('href')}")
                break

    @staticmethod
    def _format_name(name):
        return name.lower().replace("-", "").replace(" ", "-")


def main():
    start_page = "https://cw.fel.cvut.cz/b191/courses/b4m33pal/problems"
    base_dir = "/Users/zakharca/Documents/Study/PAL"
    page = requests.get(start_page)
    soup = BeautifulSoup(page.content, 'html.parser')
    task_groups = soup.find('h2', {'class': 'sectionedit2'}).find_next('div').find_all('p')
    for task_group in task_groups:
        title = task_group.find('strong')
        if title is None:
            continue
        else:
            title = title.getText()
        print(f"Task group: {title}")
        tasks_a = task_group.find_all('a')
        for task_a in tasks_a:
            url = task_a.get('href')
            name = task_a.getText().strip()
            if url.endswith(".pdf"):
                print(f"Task is pdf. Ignoring. Name: {name}, url: {url}")
                continue
            task = Task(url, base_dir, title, name)
            task.save_task()


if __name__ == '__main__':
    main()
