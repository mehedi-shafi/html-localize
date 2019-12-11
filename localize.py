from bs4 import BeautifulSoup as bs
import os
import base64
import requests

class HTMLLocalize:

    TEMP_DIRECTORY = 'temp'

    def __init__(self):
        if not os.path.exists(self.TEMP_DIRECTORY):
            os.mkdir(self.TEMP_DIRECTORY)

    def url_to_base64(self, fileurl):
        try:
            response = requests.get(fileurl)
            # getting file name from url and removing any token if exists at the end
            file_name = fileurl.split('/')[-1].split('?')[0]
            with open(f'{self.TEMP_DIRECTORY}/{file_name}', 'wb') as file:
                file.write(response.content)
            return response.headers['content-type'], self.file_to_base64(f'{self.TEMP_DIRECTORY}/{file_name}')
        except Exception as E:
            print(E)
            return '', ''
    
    def clean_temp(self):
        import shutil
        print('Clearing the mess')
        shutil.rmtree(self.TEMP_DIRECTORY)

    def guess_type(self, filepath):
        try:
            import magic  # python-magic
            return magic.from_file(filepath, mime=True)
        except ImportError:
            import mimetypes
            return mimetypes.guess_type(filepath)[0]

    def file_to_base64(self, filepath):
        print(f'Encoding {filepath}')
        with open(filepath, 'rb') as f:
            encoded_str = base64.b64encode(f.read())
        return encoded_str.decode('utf-8')

    def process_image_path(self, file_path):
        if os.path.exists(file_path):
            return self.guess_type(file_path), self.file_to_base64(file_path)
        else:
            return self.url_to_base64(file_path)

    def make_html_images_inline(self, in_filepath, out_filepath, clear=True):
        basepath = os.path.split(in_filepath.rstrip(os.path.sep))[0]
        soup = bs(open(in_filepath, 'r'), 'html.parser')
        for img in soup.find_all('img'):
            img_path = os.path.join(basepath, img.attrs['src'])
            mimetype, image_data = self.process_image_path(img_path)
            img.attrs['src'] = \
                "data:%s;base64, %s" % (mimetype, image_data)

        with open(out_filepath, 'w') as of:
            of.write(str(soup))

        # clear temp directory
        if clear:
            self.clean_temp()

if __name__ == '__main__':
    import sys
    localizer = HTMLLocalize()
    localizer.make_html_images_inline(sys.argv[1], sys.argv[2])