import cv2
import os
import argparse
from tqdm import tqdm
import glob

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="path to the images", default="/home/kadir/Downloads/8k_sample")
args = ap.parse_args()


class CropImage:
    width = 8192
    height = 4096
    new_width = 2048
    new_height = 1024
    output_folder_name = "cropped_images"
    y_crop_percent = 0.30

    def __init__(self, image_path):
        self.image_path = image_path

    def list_dir_path(self):
        list_dir = glob.glob(os.path.join(self.image_path, "*.jpg"))
        list_dir = [os.path.basename(image_name) for image_name in list_dir]
        list_dir.sort()
        return list_dir

    def iter_img(self):
        list_dir = CropImage.list_dir_path(self)
        new_list_dir = [img for index, img in enumerate(list_dir, start=1) if index % 5 == 0]
        return new_list_dir

    def height_pixels(self):
        new_min_y = self.height * self.y_crop_percent
        new_max_y = int(new_min_y) + self.new_height
        return new_max_y, int(new_min_y)

    def width_pixel(self):
        width_list: list = []
        start_w = 0
        for index in range(self.width // self.new_width):
            a = (index + 1) * 1024
            width_list.append([start_w, a])
            start_w = a
        return width_list

    def crop_and_save(self):
        abs_path = os.path.abspath(os.path.join(self.image_path, os.pardir))

        if not os.path.exists(abs_path + "/" + self.output_folder_name):
            os.makedirs(abs_path + "/" + self.output_folder_name)

        out_folder_path = os.path.join(abs_path, self.output_folder_name)

        for image in tqdm(CropImage.iter_img(self)):
            for index, width in enumerate(CropImage.width_pixel(self)):
                img_name_split = image.split(".")
                img_name = img_name_split[0] + "_" + str(index) + "." + img_name_split[1]
                img = cv2.imread(os.path.join(self.image_path, image))
                max_h, min_h = CropImage.height_pixels(self)
                img = img[min_h:max_h, width[0]:width[1]]
                cv2.imwrite(os.path.join(out_folder_path, img_name), img)


CropImage(args.image).crop_and_save()
